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
    df=df.rename(columns={"ZONE":"zone"})
    return df

def validate(context):
    if not os.path.exists("{}/{}".format(context.config("data_path"), "thailand_location/work_locations.geojson")):
        raise RuntimeError("thailand work location is not available")

    return os.path.getsize("{}/{}".format(context.config("data_path"), "thailand_location/work_locations.geojson"))
