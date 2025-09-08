import numpy as np
import pandas as pd
import geopandas as gpd
import os

"""
Provides the municipality zoning system.
"""

def configure(context):
    context.config("data_path")

def execute(context):
    filename="{}/{}".format(context.config("data_path"), "thailand_location/work_locations.geojson")
    file=open(filename)
    df=gpd.read_file(file)
    df=df[["objectid","category_c","ZONE","geometry"]]

    # Ensure consistent CRS - convert to UTM Zone 47N to match TAZ zones
    if df.crs is None:
        print("Warning: No CRS found in work locations data. Assuming WGS84 (EPSG:4326)")
        df = df.set_crs(epsg=4326)

    # Convert to Thailand-appropriate projected CRS (UTM Zone 47N)
    target_crs = "EPSG:32647"  # UTM Zone 47N - matches TAZ zones
    if df.crs.to_string() != target_crs:
        print(f"Converting work locations from {df.crs} to {target_crs}")
        df = df.to_crs(target_crs)

    df=df.rename(columns={"ZONE":"zone"})
    return df

def validate(context):
    if not os.path.exists("{}/{}".format(context.config("data_path"), "thailand_location/work_locations.geojson")):
        raise RuntimeError("thailand work location is not available")

    return os.path.getsize("{}/{}".format(context.config("data_path"), "thailand_location/work_locations.geojson"))
