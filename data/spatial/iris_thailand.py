import os
import pandas as pd
import geopandas as gpd

"""
Thailand-specific IRIS equivalent module.
This provides the same interface as the French IRIS module but uses Thai TAZ zones.
"""

def configure(context):
    context.config("data_path")
    context.stage("data.thailand_spatial.taz_zones")

def execute(context):
    # Load TAZ zones as IRIS equivalent for Thailand
    df_taz = context.stage("data.thailand_spatial.taz_zones")

    # Create IRIS-compatible dataframe using TAZ zones
    df_iris = df_taz.copy()
    df_iris = df_iris.rename(columns={"zone_id": "iris_id"})

    # Ensure we have the same structure as French IRIS data
    if "iris_id" not in df_iris.columns:
        raise RuntimeError("TAZ zones must have zone_id column")

    # Set iris_id as index for compatibility
    df_iris = df_iris.set_index("iris_id")

    print(f"Created IRIS-equivalent data for Thailand with {len(df_iris)} zones")

    return df_iris

def validate(context):
    # Thailand IRIS data is generated from TAZ zones, so always valid if TAZ zones exist
    return True
