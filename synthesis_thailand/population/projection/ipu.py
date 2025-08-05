
import pandas as pd
import numpy as np

def configure(context):
    context.stage("synthesis_thailand.population.enriched")
    context.stage("data.census.projection")
    context.config("max_iterations", 100)
    context.config("tolerance", 0.01)

def execute(context):
    df_persons = context.stage("synthesis_thailand.population.enriched")
    df_targets = context.stage("data.census.projection")

    # Initialize weights
    df_persons["weight"] = 1.0

    # Get marginal categories from the targets file
    categories = df_targets["category"].unique()

    for i in range(context.config("max_iterations")):
        max_error = 0.0
        for category in categories:
            # Calculate current weighted totals for the category
            current_totals = df_persons.groupby(category)["weight"].sum()
            
            # Get target totals for the category
            target_totals = df_targets[df_targets["category"] == category].set_index("value")["target"]

            # Calculate adjustment factors
            adjustment_factors = target_totals / current_totals
            adjustment_factors = adjustment_factors.fillna(1.0) # Handle cases with no one in a category

            # Update weights
            df_persons["weight"] *= df_persons[category].map(adjustment_factors).fillna(1.0)

            # Check error
            error = np.abs(1.0 - adjustment_factors).max()
            if error > max_error:
                max_error = error
        
        if max_error < context.config("tolerance"):
            print(f"IPU converged after {i+1} iterations.")
            break
    else:
        print(f"IPU did not converge after {context.config('max_iterations')} iterations. Max error: {max_error}")

    # Return the person dataframe with the new weights
    return df_persons[["person_id", "weight"]]
