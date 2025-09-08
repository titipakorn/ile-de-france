import numpy as np
import pandas as pd
import itertools

"""
This stage scales up the Thailand HTS sample to represent the full population
using survey weights and sampling rates.
"""

def configure(context):
    context.stage("data.hts.thailand.cleaned")  # Use original cleaned.py instead of cleaned_simple.py
    context.config("random_seed")
    context.config("sampling_rate", 1.0)
    context.config("target_population", None)  # Optional: target total population
    context.config("scaling_method", "weight_based")  # "simple", "weight_based", or "stochastic"

def execute(context):
    df_households, df_persons, df_trips = context.stage("data.hts.thailand.cleaned")  # Use original cleaned.py

    sampling_rate = context.config("sampling_rate")
    random = np.random.RandomState(context.config("random_seed"))
    scaling_method = context.config("scaling_method")
    target_population = context.config("target_population")

    print(f"Population Scaling Configuration:")
    print(f"- Original sample: {len(df_households)} households, {len(df_persons)} persons")
    print(f"- Sampling rate: {sampling_rate}")
    print(f"- Scaling method: {scaling_method}")
    print(f"- Target population: {target_population}")

    if scaling_method == "simple":
        # Simple scaling by sampling rate
        return scale_simple(df_households, df_persons, df_trips, sampling_rate, random)

    elif scaling_method == "weight_based":
        # Use survey weights for scaling
        return scale_by_weights(df_households, df_persons, df_trips, sampling_rate, random, target_population)

    elif scaling_method == "stochastic":
        # Advanced stochastic rounding (like French pipeline)
        return scale_stochastic(df_households, df_persons, df_trips, sampling_rate, random)

    else:
        raise ValueError(f"Unknown scaling method: {scaling_method}")

def scale_simple(df_households, df_persons, df_trips, sampling_rate, random):
    """Simple scaling: replicate households based on sampling rate"""

    if sampling_rate >= 1.0:
        print("No scaling needed (sampling_rate >= 1.0)")
        return df_households, df_persons, df_trips

    # Calculate how many times to replicate each household
    scale_factor = 1.0 / sampling_rate
    n_replications = int(np.floor(scale_factor))

    print(f"Simple scaling: replicating each household {n_replications} times")

    # Replicate households
    household_list = []
    person_list = []
    trip_list = []

    household_id_counter = 0
    person_id_counter = 0
    trip_id_counter = 0

    for rep in range(n_replications):
        # Copy households
        df_hh_copy = df_households.copy()
        df_hh_copy["original_household_id"] = df_hh_copy["household_id"]
        df_hh_copy["household_id"] = np.arange(household_id_counter, household_id_counter + len(df_hh_copy))
        household_id_counter += len(df_hh_copy)
        household_list.append(df_hh_copy)

        # Copy persons and update household references
        df_p_copy = df_persons.copy()
        df_p_copy["original_person_id"] = df_p_copy["person_id"]
        df_p_copy["original_household_id"] = df_p_copy["household_id"]

        # Create mapping from old to new household IDs
        hh_mapping = dict(zip(df_households["household_id"], df_hh_copy["household_id"]))
        df_p_copy["household_id"] = df_p_copy["household_id"].map(hh_mapping)
        df_p_copy["person_id"] = np.arange(person_id_counter, person_id_counter + len(df_p_copy))
        person_id_counter += len(df_p_copy)
        person_list.append(df_p_copy)

        # Copy trips and update person references
        df_t_copy = df_trips.copy()
        df_t_copy["original_trip_id"] = df_t_copy["trip_id"]
        df_t_copy["original_person_id"] = df_t_copy["person_id"]

        # Create mapping from old to new person IDs
        p_mapping = dict(zip(df_persons["person_id"], df_p_copy["person_id"]))
        df_t_copy["person_id"] = df_t_copy["person_id"].map(p_mapping)
        df_t_copy["trip_id"] = np.arange(trip_id_counter, trip_id_counter + len(df_t_copy))
        trip_id_counter += len(df_t_copy)
        trip_list.append(df_t_copy)

    # Combine all replications
    df_households_scaled = pd.concat(household_list, ignore_index=True)
    df_persons_scaled = pd.concat(person_list, ignore_index=True)
    df_trips_scaled = pd.concat(trip_list, ignore_index=True)

    print(f"Scaled population: {len(df_households_scaled)} households, {len(df_persons_scaled)} persons, {len(df_trips_scaled)} trips")

    return df_households_scaled, df_persons_scaled, df_trips_scaled

def scale_by_weights(df_households, df_persons, df_trips, sampling_rate, random, target_population=None):
    """Scale using survey weights (more accurate)"""

    print("Weight-based scaling using survey weights...")

    # Use household weights for scaling
    if "household_weight" not in df_households.columns:
        print("Warning: No household_weight found, using person weights")
        # Calculate household weights from person weights
        hh_weights = df_persons.groupby("household_id")["person_weight"].mean().reset_index()
        hh_weights.rename(columns={"person_weight": "household_weight"}, inplace=True)
        df_households = pd.merge(df_households, hh_weights, on="household_id")

    # Calculate effective population based on weights
    total_weighted_households = df_households["household_weight"].sum()
    total_weighted_persons = df_persons["person_weight"].sum()

    print(f"Total weighted households: {total_weighted_households:.0f}")
    print(f"Total weighted persons: {total_weighted_persons:.0f}")

    # If target population is specified, adjust weights
    if target_population:
        weight_adjustment = target_population / total_weighted_persons
        df_households["household_weight"] *= weight_adjustment
        df_persons["person_weight"] *= weight_adjustment
        print(f"Adjusted weights for target population of {target_population}")

    # Perform stochastic rounding based on weights
    df_households["n_copies"] = np.floor(df_households["household_weight"] * sampling_rate).astype(int)
    df_households["prob_extra"] = (df_households["household_weight"] * sampling_rate) - df_households["n_copies"]
    df_households["extra_copy"] = random.random(len(df_households)) < df_households["prob_extra"]
    df_households["total_copies"] = df_households["n_copies"] + df_households["extra_copy"].astype(int)

    # Generate scaled population
    household_list = []
    person_list = []
    trip_list = []

    household_id_counter = 0
    person_id_counter = 0
    trip_id_counter = 0

    for _, hh_row in df_households.iterrows():
        n_copies = hh_row["total_copies"]
        if n_copies == 0:
            continue

        original_hh_id = hh_row["household_id"]

        for copy_idx in range(n_copies):
            # Copy household
            new_hh_id = household_id_counter
            household_id_counter += 1

            hh_copy = hh_row.copy()
            hh_copy["household_id"] = new_hh_id
            hh_copy["original_hh_id"] = original_hh_id
            household_list.append(hh_copy)

            # Copy persons in this household
            hh_persons = df_persons[df_persons["household_id"] == original_hh_id].copy()
            for _, p_row in hh_persons.iterrows():
                new_person_id = person_id_counter
                person_id_counter += 1

                p_copy = p_row.copy()
                p_copy["person_id"] = new_person_id
                p_copy["household_id"] = new_hh_id
                p_copy["original_person_id"] = p_row["person_id"]
                person_list.append(p_copy)

                # Copy trips for this person
                person_trips = df_trips[df_trips["person_id"] == p_row["person_id"]].copy()
                for _, t_row in person_trips.iterrows():
                    new_trip_id = trip_id_counter
                    trip_id_counter += 1

                    t_copy = t_row.copy()
                    t_copy["trip_id"] = new_trip_id
                    t_copy["person_id"] = new_person_id
                    t_copy["original_trip_id"] = t_row["trip_id"]
                    trip_list.append(t_copy)

    # Convert lists to DataFrames
    df_households_scaled = pd.DataFrame(household_list)
    df_persons_scaled = pd.DataFrame(person_list)
    df_trips_scaled = pd.DataFrame(trip_list)

    print(f"Scaled population: {len(df_households_scaled)} households, {len(df_persons_scaled)} persons, {len(df_trips_scaled)} trips")

    return df_households_scaled, df_persons_scaled, df_trips_scaled

def scale_stochastic(df_households, df_persons, df_trips, sampling_rate, random):
    """Advanced stochastic scaling (similar to French pipeline)"""

    print("Stochastic scaling with advanced replication...")

    # This is a simplified version of the French approach
    # For full implementation, you'd need census data for calibration

    # Use household weights if available
    if "household_weight" not in df_households.columns:
        df_households["household_weight"] = 1.0

    # Perform stochastic rounding
    df_households = df_households.sort_values("household_id").copy()
    df_households["multiplicator"] = np.floor(df_households["household_weight"])
    df_households["multiplicator"] += random.random_sample(len(df_households)) <= (df_households["household_weight"] - df_households["multiplicator"])
    df_households["multiplicator"] = df_households["multiplicator"].astype(int)

    # Replicate households based on multiplicator
    household_multiplicators = df_households["multiplicator"].values
    household_sizes = df_households["household_size"].values

    # Create expandor for replication
    person_indices = []
    current_idx = 0

    for hh_idx, (mult, size) in enumerate(zip(household_multiplicators, household_sizes)):
        hh_person_indices = list(range(current_idx, current_idx + size))
        for _ in range(mult):
            person_indices.extend(hh_person_indices)
        current_idx += size

    # Replicate persons
    df_persons_expanded = df_persons.iloc[person_indices].copy()

    # Create new IDs
    df_persons_expanded["census_person_id"] = df_persons_expanded["person_id"]
    df_persons_expanded["person_id"] = np.arange(len(df_persons_expanded))

    # Create new household IDs
    household_count = np.sum(household_multiplicators)
    new_household_sizes = np.repeat(household_sizes, household_multiplicators)
    df_persons_expanded["household_id"] = np.repeat(np.arange(household_count), new_household_sizes)

    # Sample based on sampling rate
    if sampling_rate < 1.0:
        household_selector = random.random_sample(household_count) < sampling_rate
        person_selector = np.repeat(household_selector, new_household_sizes)
        df_persons_scaled = df_persons_expanded[person_selector].copy()

        # Update household data
        selected_households = df_persons_scaled["household_id"].unique()
        df_households_scaled = df_households.iloc[:len(selected_households)].copy()
        df_households_scaled["household_id"] = selected_households
    else:
        df_persons_scaled = df_persons_expanded
        df_households_scaled = df_households.iloc[:household_count].copy()
        df_households_scaled["household_id"] = np.arange(household_count)

    # Replicate trips
    # Create mapping from old to new person IDs
    old_to_new_person = dict(zip(df_persons_scaled["census_person_id"], df_persons_scaled["person_id"]))

    trip_list = []
    trip_id_counter = 0

    for old_person_id, new_person_id in old_to_new_person.items():
        person_trips = df_trips[df_trips["person_id"] == old_person_id].copy()
        person_trips["person_id"] = new_person_id
        person_trips["original_trip_id"] = person_trips["trip_id"]
        person_trips["trip_id"] = np.arange(trip_id_counter, trip_id_counter + len(person_trips))
        trip_id_counter += len(person_trips)
        trip_list.append(person_trips)

    df_trips_scaled = pd.concat(trip_list, ignore_index=True) if trip_list else pd.DataFrame()

    print(f"Scaled population: {len(df_households_scaled)} households, {len(df_persons_scaled)} persons, {len(df_trips_scaled)} trips")

    return df_households_scaled, df_persons_scaled, df_trips_scaled
