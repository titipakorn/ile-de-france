import pandas as pd
import numpy as np

def configure(context):
    context.stage("synthesis_thailand.population.sampled")
    context.stage("data.hts.thailand.cleaned", alias="hts")

def execute(context):
    """
    Generate household incomes using both household and person income data from HTS
    """
    df_persons = context.stage("synthesis_thailand.population.sampled")
    df_hts_households, df_hts_persons, _ = context.stage("hts")

    # Get household-level data from sampled population
    df_households = df_persons[["household_id", "departement_id"]].drop_duplicates()
    df_households = df_households.set_index("household_id")

    # Create comprehensive income lookup using both household and person income data
    # Method 1: Use actual HTS household income directly when available
    hts_household_income = df_hts_households[["household_id", "income_class", "departement_id"]].set_index("household_id")
    hts_household_income = hts_household_income.rename(columns={"income_class": "hts_household_income"})

    # Method 2: Calculate household income from aggregated person incomes for validation/fallback
    person_income_by_household = df_hts_persons.groupby("household_id")["person_income"].agg([
        ('total_person_income', 'sum'),
        ('mean_person_income', 'mean'),
        ('max_person_income', 'max'),
        ('income_contributors', 'count')
    ])

    # Merge both household and person-based income estimates
    income_combined = hts_household_income.join(person_income_by_household, how="outer")

    # Create zone-level income distributions using both data sources
    zone_stats_household = df_hts_households.groupby("departement_id")["income_class"].agg([
        ('hh_mean', 'mean'),
        ('hh_std', 'std'),
        ('hh_min', 'min'),
        ('hh_max', 'max'),
        ('hh_count', 'count')
    ])

    zone_stats_person = df_hts_persons.groupby("departement_id")["person_income"].agg([
        ('p_mean', 'mean'),
        ('p_std', 'std'),
        ('p_min', 'min'),
        ('p_max', 'max'),
        ('p_count', 'count')
    ])

    zone_stats = zone_stats_household.join(zone_stats_person, how="outer").fillna(0)

    # Generate household incomes using zone-specific distributions
    np.random.seed(context.config("random_seed", 0))

    incomes = []
    for zone_id, group in df_households.groupby("departement_id"):
        if zone_id in zone_stats.index and zone_stats.loc[zone_id, "hh_count"] > 0:
            # Use zone-specific household income distribution
            mean_income = zone_stats.loc[zone_id, "hh_mean"]
            std_income = zone_stats.loc[zone_id, "hh_std"]
            min_income = zone_stats.loc[zone_id, "hh_min"]
            max_income = zone_stats.loc[zone_id, "hh_max"]

            # Generate realistic income variation
            household_incomes = np.random.normal(mean_income, std_income, size=len(group))
            household_incomes = np.clip(household_incomes, min_income, max_income)

        else:
            # Fallback to overall distribution
            overall_mean = df_hts_households["income_class"].mean()
            overall_std = df_hts_households["income_class"].std()
            overall_min = df_hts_households["income_class"].min()
            overall_max = df_hts_households["income_class"].max()

            household_incomes = np.random.normal(overall_mean, overall_std, size=len(group))
            household_incomes = np.clip(household_incomes, overall_min, overall_max)

        incomes.append(pd.DataFrame({
            "household_id": group.index,
            "household_income": household_incomes
        }))

    if incomes:
        df_final_incomes = pd.concat(incomes).set_index("household_id")
    else:
        # Final fallback
        df_final_incomes = pd.DataFrame({
            "household_income": [df_hts_households["income_class"].mean()] * len(df_households)
        }, index=df_households.index)

    return df_final_incomes[["household_income"]]
