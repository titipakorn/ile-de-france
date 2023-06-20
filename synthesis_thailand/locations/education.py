import shapely.geometry as geo
import numpy as np
import pandas as pd
import geopandas as gpd

def configure(context):
    context.stage("data.synthesis_pop.raw")

def execute(context):
    df = context.stage("data.synthesis_pop.raw")
    df_dd = df["ss"]
    df_locations = gpd.GeoDataFrame(df_dd, geometry=gpd.points_from_xy(df_dd["coordX"], df_dd["coordY"]), crs=32647)
    
    df_locations = df_locations[["zone", "geometry"]].copy()
    df_locations["fake"] = False

    # Define identifiers
    df_locations["location_id"] = np.arange(len(df_locations))
    df_locations["location_id"] = "edu_" + df_locations["location_id"].astype(str)

    return df_locations[["location_id", "zone", "fake", "geometry"]]
