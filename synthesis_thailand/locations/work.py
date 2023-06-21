import pandas as pd
import tqdm
import numpy as np
import geopandas as gpd

"""
This stage provides a list of work places that serve as potential locations for
work activities. It is derived from the SIRENE enterprise database.

Municipalities which do not have any registered enterprise receive a fake work
place at their centroid to be in line with INSEE OD data.
"""

def configure(context):
    # context.stage("data.synthesis_pop.raw")
    context.stage("data.thailand_spatial.work")
def execute(context):
    # df = context.stage("data.synthesis_pop.raw")
    # df_dd = df["jj"]
    # df_workplaces = gpd.GeoDataFrame(df_dd, geometry=gpd.points_from_xy(df_dd["coordX"], df_dd["coordY"]), crs=32647)
    df_workplaces=context.stage("data.thailand_spatial.work")
    df_workplaces["employees"]=1.0
    df_workplaces["fake"] = False
    # Add work identifier
    df_workplaces["location_id"] = np.arange(len(df_workplaces))
    df_workplaces["location_id"] = "work_" + df_workplaces["location_id"].astype(str)

    return df_workplaces[["location_id", "zone", "employees", "fake", "geometry"]]
