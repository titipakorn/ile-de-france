
import pandas as pd
import numpy as np

def configure(context):
    context.stage("synthesis_thailand.population.enriched")
    context.stage("data.vehicles.raw")
    context.stage("data.vehicles.types")

def execute(context):
    df_households = context.stage("synthesis_thailand.population.enriched")[["household_id", "motorcycle_availability"]].drop_duplicates()
    df_raw_vehicles = context.stage("data.vehicles.raw")
    df_vehicle_types = context.stage("data.vehicles.types")

    # Filter for motorcycle types
    motorcycle_types = df_vehicle_types[df_vehicle_types["mode"] == "motorcycle"]["type_id"].unique()
    df_raw_motorcycles = df_raw_vehicles[df_raw_vehicles["vehicle_type"].isin(motorcycle_types)]

    # Simple assignment: for households that have motorcycles, assign a random model from the raw data
    households_with_motorcycles = df_households[df_households["motorcycle_availability"].isin(["1", "2+"])]
    
    if households_with_motorcycles.empty or df_raw_motorcycles.empty:
        return pd.DataFrame(columns=["household_id", "vehicle_type"])

    # Create a pool of available motorcycles to sample from
    motorcycle_pool = df_raw_motorcycles["vehicle_type"].values

    assigned_motorcycles = []
    for _, household in households_with_motorcycles.iterrows():
        num_motorcycles = 1 if household["motorcycle_availability"] == "1" else np.random.randint(2, 4)
        for _ in range(num_motorcycles):
            chosen_motorcycle_type = np.random.choice(motorcycle_pool)
            assigned_motorcycles.append({
                "household_id": household["household_id"],
                "vehicle_type": chosen_motorcycle_type
            })

    df_assigned_motorcycles = pd.DataFrame(assigned_motorcycles)
    return df_assigned_motorcycles
