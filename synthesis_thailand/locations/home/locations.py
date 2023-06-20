import pandas as pd
import numpy as np
import geopandas as gpd

"""
This stage provides a list of home places that serve as potential locations for
home activities.
"""

def configure(context):
    context.stage("data.synthesis_pop.raw")

def execute(context):
    # Find required IRIS
    df = context.stage("data.synthesis_pop.raw")
    df_dd = df["dd"]
    df_addresses = gpd.GeoDataFrame(df_dd, geometry=gpd.points_from_xy(df_dd["coordX"], df_dd["coordY"]), crs=32647)
    df_addresses['building_id'] = df_addresses.reset_index().index
    df_addresses['weight']=1.0
    # Add home identifier
    df_addresses["location_id"] = np.arange(len(df_addresses))
    df_addresses["location_id"] = "home_" + df_addresses["location_id"].astype(str)
    df_addresses = df_addresses.rename(columns={"hhID":"household_id"})
    
    return df_addresses[['zone', 'household_id', 'building_id', 'weight',
       'location_id','geometry']]
