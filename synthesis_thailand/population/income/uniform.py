import pandas as pd
import numpy as np

def configure(context):
    context.stage("synthesis_thailand.population.sampled")
    context.stage("data.income.region")

def execute(context):
    df_persons = context.stage("synthesis_thailand.population.sampled")
    df_income = context.stage("data.income.region")

    df_households = df_persons[["household_id", "region"]].drop_duplicates()
    df_households = df_households.set_index("household_id")

    np.random.seed(context.config("random_seed", 0))

    incomes = []
    for region, group in df_households.groupby("region"):
        regional_income = df_income[df_income["region"] == region]
        
        if regional_income.empty:
            # Fallback to national average if regional data is missing
            regional_income = df_income[df_income["region"] == "National"]

        if not regional_income.empty:
            probabilities = regional_income["households"] / regional_income["households"].sum()
            income_distribution = np.random.choice(regional_income.index, size=len(group), p=probabilities)
            
            min_incomes = regional_income.loc[income_distribution, "min_income"].values
            max_incomes = regional_income.loc[income_distribution, "max_income"].values
            
            household_incomes = np.random.uniform(min_incomes, max_incomes)
            
            incomes.append(pd.DataFrame({
                "household_id": group.index,
                "household_income": household_incomes
            }))

    df_final_incomes = pd.concat(incomes).set_index("household_id")
    df_households = df_households.join(df_final_incomes)
    
    return df_households[["household_income"]]