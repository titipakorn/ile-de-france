import os
import pandas as pd

"""
This stage provides spatial codes for Thailand.
It creates a mapping between TAZ zones and administrative regions.
"""

def configure(context):
    context.config("data_path")
    context.stage("data.thailand_spatial.taz_zones")

def execute(context):
    # Load TAZ zones to get the spatial hierarchy
    df_taz = context.stage("data.thailand_spatial.taz_zones")

    # Create a spatial codes dataframe for Thailand
    # Using TAZ zone_id as the primary spatial identifier
    df_codes = pd.DataFrame({
        'iris_id': df_taz['zone_id'],  # Use zone_id as iris equivalent
        'commune_id': df_taz['zone_id'],  # For Thailand, zone is the base unit
        'departement_id': df_taz['zone_id'],  # Map to zone_id
        'region_id': 1  # Single region for Thailand (can be modified if needed)
    })

    # Convert to appropriate data types
    df_codes["iris_id"] = df_codes["iris_id"].astype("category")
    df_codes["commune_id"] = df_codes["commune_id"].astype("category")
    df_codes["departement_id"] = df_codes["departement_id"].astype("category")
    df_codes["region_id"] = df_codes["region_id"].astype(int)

    print(f"Created Thailand spatial codes for {len(df_codes)} zones")

    return df_codes

def validate(context):
    # Thailand spatial codes are generated from TAZ zones, so always valid if TAZ zones exist
    return True
