import numpy as np
import pandas as pd

"""
This stage samples home zones for all synthesized households. From the census
data we have several special cases that we need to cover:
- For people that live in municipalities without IRIS, only their departement is known
- For people that live in IRIS with less than 200 inhabitants, only their municipality is known

Based on these criteria, we can attach a random commune from the departement (which is not
covered by IRIS) to the first case, and we can attach a random IRIS within a commune that
has less than 200 inhabitants to the second case.
"""

def configure(context):
    context.stage("data.synthesis_pop.raw")


def execute(context):
    df = context.stage("data.synthesis_pop.raw")
    df_households = df['dd']
    df_households["location_id"] = np.arange(1,len(df_households)+1)
    df_households = df_households.rename(columns={"hhID":"household_id"})
    df_households['household_id'] = df_households['household_id'].astype(int)
    df_households=df_households[df_households['household_id']>0]

    return df_households[["household_id","location_id", "zone"]]
