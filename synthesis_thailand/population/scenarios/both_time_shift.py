from tqdm import tqdm
import itertools
import numpy as np
import pandas as pd

"""
This stage duplicates trips and attaches them to the synthetic population.
"""

def configure(context):
    context.stage("synthesis_thailand.population.scenarios.school_time_shift")
    context.config("work_shift_minutes",30)
    
def execute(context):
    # Load data
    df_trips = context.stage("synthesis_thailand.population.scenarios.school_time_shift")
    work_shift_minutes = context.config("work_shift_minutes")*60
    # find people who goes to work, and starting from home
    hbw_people=df_trips[(df_trips['T_PURPOSE']==1) & (df_trips['T_Type']=='HBW')]['P_CODE'].unique()
    df_trips.loc[df_trips['P_CODE'].isin(hbw_people),'departure_time']+=work_shift_minutes
    df_trips.loc[df_trips['P_CODE'].isin(hbw_people),'arrival_time']+=work_shift_minutes
    return df_trips