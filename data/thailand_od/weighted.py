from tqdm import tqdm
import pandas as pd
import numpy as np

"""
Transforms absolute OD flows from French census into a weighted destination
matrix given a certain origin commune for work and education.

Potential TODO: Do this by mode of transport!
"""

def configure(context):
    context.stage("data.thailand_od.raw")

def execute(context):
    # Load data
    df_od = context.stage("data.thailand_od.raw")

    # Compute totals
    df_od_total = df_od.sum(axis=1)
    
    df_weighted_od=df_od.copy()
    # Compute weight
    df_weighted_od=df_weighted_od.div(df_od_total, axis=0)
    
    converted_matrix = df_weighted_od.stack().reset_index()
    converted_matrix.columns = ['origin_id', 'destination_id', 'weight']
    converted_matrix['destination_id']=converted_matrix['destination_id'].astype(int)
    converted_matrix['origin_id']=converted_matrix['origin_id'].astype(int)
    return converted_matrix
