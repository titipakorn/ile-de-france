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
    context.config("school_shift_minutes",60)
    
def execute(context):
    # Load data
    df_trips = context.stage("hts")[2]
    work_shift_minutes = context.config("school_shift_minutes")*60
    # find people who goes to school, and starting from home
    hbw_people=df_trips[(df_trips['T_PURPOSE']==2) & (df_trips['T_Type']=='HBE')]['P_CODE'].unique()
    df_trips.loc[df_trips['P_CODE'].isin(hbw_people),'departure_time']+=work_shift_minutes
    df_trips.loc[df_trips['P_CODE'].isin(hbw_people),'arrival_time']+=work_shift_minutes
    return df_trips