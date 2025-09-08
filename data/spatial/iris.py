import pandas as pd
import geopandas as gpd
import os
import py7zr
import glob

"""
Loads the IRIS zoning system.
For Thailand synthesis, this uses TAZ zones instead of French IRIS data.
"""

def configure(context):
    context.config("data_path")

    # Check if we're running Thailand synthesis
    hts = context.config("hts", "france")

    if hts == "thailand":
        # For Thailand, use TAZ zones as IRIS equivalent
        context.stage("data.thailand_spatial.taz_zones")
    else:
        # For France and other regions, use standard IRIS data
        context.config("iris_path", "iris_2023")
        context.stage("data.spatial.codes")

def execute(context):
    # Check if we're running Thailand synthesis
    hts = context.config("hts", "france")

    if hts == "thailand":
        # For Thailand, use TAZ zones as IRIS equivalent
        df_taz = context.stage("data.thailand_spatial.taz_zones")

        # Create IRIS-compatible dataframe using TAZ zones
        df_iris = df_taz.copy()
        df_iris = df_iris.rename(columns={"zone_id": "iris_id"})

        # Set iris_id as index for compatibility with existing code
        if "iris_id" in df_iris.columns:
            df_iris = df_iris.set_index("iris_id")

        print(f"Using Thailand TAZ zones as IRIS equivalent: {len(df_iris)} zones")
        return df_iris

    else:
        # Original France IRIS logic
        df_codes = context.stage("data.spatial.codes")

        source_path = find_iris("{}/{}".format(context.config("data_path"), context.config("iris_path")))

        with py7zr.SevenZipFile(source_path) as archive:
            contour_paths = [
                path for path in archive.getnames()
                if "LAMB93" in path
            ]

            archive.extract(context.path(), contour_paths)

        shp_path = [path for path in contour_paths if path.endswith(".shp")]

        if len(shp_path) != 1:
            raise RuntimeError("Ambiguous SHP file: %s" % shp_path)

        df_iris = gpd.read_file("%s/%s" % (context.path(), shp_path[0]))

        df_iris["iris_id"] = df_iris["CODE_IRIS"]
        df_iris = df_iris[["iris_id", "geometry"]].set_index("iris_id")

        # Filter data
        requested_iris = set(df_codes["iris_id"].cat.categories)
        merged_iris = set(df_iris.index.unique())

        if requested_iris != merged_iris:
            raise RuntimeError("Some IRIS are missing: %s" % (requested_iris - merged_iris,))

        return df_iris

def find_iris(path):
    candidates = sorted(list(glob.glob("{}/*.7z".format(path))))

    if len(candidates) == 0:
        raise RuntimeError("IRIS data is not available in {}".format(path))
    
    if len(candidates) > 1:
        raise RuntimeError("Multiple candidates for IRIS are available in {}".format(path))
    
    return candidates[0]


def validate(context):
    # Check if we're running Thailand synthesis
    hts = context.config("hts", "france")

    if hts == "thailand":
        # For Thailand, validation is handled by TAZ zones module
        return True
    else:
        # Original France validation logic
        path = find_iris("{}/{}".format(context.config("data_path"), context.config("iris_path")))
        return os.path.getsize(path)
