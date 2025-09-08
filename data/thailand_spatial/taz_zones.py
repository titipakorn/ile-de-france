import numpy as np
import pandas as pd
import geopandas as gpd
import os

"""
Provides the complete TAZ (Traffic Analysis Zone) system for Thailand.
This module loads the main zone boundaries that define the geographic areas.
"""

def configure(context):
    context.config("data_path")

def execute(context):
    filename = "{}/{}".format(context.config("data_path"), "thailand_location/taz_zones.geojson")

    if not os.path.exists(filename):
        # Fallback to shapefile if geojson not available
        filename_shp = "{}/{}".format(context.config("data_path"), "thailand_location/taz_zones.shp")
        if os.path.exists(filename_shp):
            df = gpd.read_file(filename_shp)
        else:
            raise RuntimeError(f"TAZ zone file not found. Please provide either:\n"
                             f"- {filename} (GeoJSON format), or\n"
                             f"- {filename_shp} (Shapefile format)")
    else:
        df = gpd.read_file(filename)

    # Standardize column names - adjust these based on your actual TAZ data structure
    # Common TAZ field names: ZONE_ID, TAZ_ID, ZONE_CODE, ID, etc.
    zone_id_columns = ["ZONE_ID", "TAZ_ID", "ZONE_CODE", "ZONE", "ID", "FID", "OBJECTID"]
    zone_column = None

    for col in zone_id_columns:
        if col in df.columns:
            zone_column = col
            break

    if zone_column is None:
        # If no standard zone ID found, use the first non-geometry column
        non_geom_cols = [col for col in df.columns if col != 'geometry']
        if non_geom_cols:
            zone_column = non_geom_cols[0]
            print(f"Warning: Using '{zone_column}' as zone ID column. Please verify this is correct.")
        else:
            raise RuntimeError("Could not identify zone ID column in TAZ data")

    # Rename to standard format
    df = df.rename(columns={zone_column: "zone_id"})

    # Ensure we have the required columns and clean data
    df = df[["zone_id", "geometry"]].copy()
    df = df.dropna(subset=["zone_id", "geometry"])

    # Ensure zone_id is string type for consistency
    df["zone_id"] = df["zone_id"].astype(str)

    # Handle CRS - ensure proper projection for Thailand
    if df.crs is None:
        print("Warning: No CRS found in TAZ data. Assuming WGS84 (EPSG:4326)")
        df = df.set_crs(epsg=4326)

    # Convert to Thailand-appropriate projected CRS for accurate distance calculations
    # UTM Zone 47N (EPSG:32647) covers most of Thailand including Bangkok
    target_crs = "EPSG:32647"  # UTM Zone 47N - best for central Thailand

    print(f"Original CRS: {df.crs}")
    if df.crs.to_string() != target_crs:
        print(f"Converting to {target_crs} for accurate distance calculations")
        df = df.to_crs(target_crs)

    # Calculate zone centroids for distance calculations (now in meters)
    df["centroid"] = df["geometry"].centroid
    df["centroid_x"] = df["centroid"].x
    df["centroid_y"] = df["centroid"].y

    # Calculate zone area in square meters
    df["area"] = df["geometry"].area

    print(f"Loaded {len(df)} TAZ zones in {df.crs}")
    print(f"Zone ID range: {df['zone_id'].min()} to {df['zone_id'].max()}")
    print(f"Zone areas range: {df['area'].min():.0f} to {df['area'].max():.0f} square meters")

    return df

def validate(context):
    # Check for TAZ zone files
    geojson_path = "{}/{}".format(context.config("data_path"), "thailand_location/taz_zones.geojson")
    shapefile_path = "{}/{}".format(context.config("data_path"), "thailand_location/taz_zones.shp")

    if os.path.exists(geojson_path):
        return os.path.getsize(geojson_path)
    elif os.path.exists(shapefile_path):
        return os.path.getsize(shapefile_path)
    else:
        raise RuntimeError("TAZ zone file is required but not found. Please provide either:\n"
                         f"- {geojson_path} (GeoJSON format), or\n" 
                         f"- {shapefile_path} (Shapefile format)")
