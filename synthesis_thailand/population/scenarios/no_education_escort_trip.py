from tqdm import tqdm
import itertools
import numpy as np
import pandas as pd

"""
This stage duplicates trips and attaches them to the synthetic population.
"""

def configure(context):
    hts = context.config("hts")
    context.stage("data.hts.thailand.cleaned", alias = "hts")

def execute(context):
    # Load data
    df_trips = context.stage("hts")[2]
    #filter out school escort people
    df_trips = df_trips[~df_trips['P_CODE'].isin(df_trips[(df_trips['mode']=='car') & (df_trips['BACKUP_PURPOSE']==5) & (df_trips['T_PURPOSE']==2)]['P_CODE'].unique())]
    #change student mode to pt
    df_trips.loc[(df_trips['mode']=='car_passenger') & ((df_trips['preceding_purpose']=='education') | (df_trips['following_purpose']=='education')),'mode']='pt'
    return df_trips