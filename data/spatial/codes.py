import os
import pandas as pd
import zipfile

"""
This stages loads a file containing all spatial codes in France and how
they can be translated into each other. These are mainly IRIS, commune,
departement and région.
"""

def configure(context):
    context.config("data_path")

    # Check if we're running Thailand synthesis
    hts = context.config("hts", "france")  # Default to france if not specified

    if hts == "thailand":
        # For Thailand, use TAZ zones as spatial reference
        context.stage("data.thailand_spatial.taz_zones")
    else:
        # For France and other regions, use the standard spatial codes
        context.config("regions", [11])
        context.config("departments", [])
        context.config("codes_path", "codes_2023/reference_IRIS_geo2023.zip")
        context.config("codes_xlsx", "reference_IRIS_geo2023.xlsx")

def execute(context):
    # Check if we're running Thailand synthesis
    hts = context.config("hts", "france")

    if hts == "thailand":
        # For Thailand, create spatial codes from TAZ zones
        df_taz = context.stage("data.thailand_spatial.taz_zones")

        # Create a spatial codes dataframe for Thailand using TAZ zones
        df_codes = pd.DataFrame({
            'iris_id': df_taz['zone_id'],  # Use zone_id as iris equivalent
            'commune_id': df_taz['zone_id'],  # For Thailand, zone is the base unit
            'departement_id': df_taz['zone_id'],  # Map to zone_id
            'region_id': 1  # Single region for Thailand
        })

        # Convert to appropriate data types
        df_codes["iris_id"] = df_codes["iris_id"].astype("category")
        df_codes["commune_id"] = df_codes["commune_id"].astype("category")
        df_codes["departement_id"] = df_codes["departement_id"].astype("category")
        df_codes["region_id"] = df_codes["region_id"].astype(int)

        print(f"Created Thailand spatial codes for {len(df_codes)} zones")
        return df_codes

    else:
        # Original France logic
        # Load IRIS registry
        with zipfile.ZipFile(
            "{}/{}".format(context.config("data_path"), context.config("codes_path"))) as archive:
            with archive.open(context.config("codes_xlsx")) as f:
                df_codes = pd.read_excel(f,
                    skiprows = 5, sheet_name = "Emboitements_IRIS"
                )[["CODE_IRIS", "DEPCOM", "DEP", "REG"]].rename(columns = {
                    "CODE_IRIS": "iris_id",
                    "DEPCOM": "commune_id",
                    "DEP": "departement_id",
                    "REG": "region_id"
                })

        df_codes["iris_id"] = df_codes["iris_id"].astype("category")
        df_codes["commune_id"] = df_codes["commune_id"].astype("category")
        df_codes["departement_id"] = df_codes["departement_id"].astype("category")
        df_codes["region_id"] = df_codes["region_id"].astype(int)

        # Filter zones
        requested_regions = list(map(int, context.config("regions")))
        requested_departments = list(map(str, context.config("departments")))

        if len(requested_regions) > 0:
            df_codes = df_codes[df_codes["region_id"].isin(requested_regions)]

        if len(requested_departments) > 0:
            df_codes = df_codes[df_codes["departement_id"].isin(requested_departments)]

        df_codes["iris_id"] = df_codes["iris_id"].cat.remove_unused_categories()
        df_codes["commune_id"] = df_codes["commune_id"].cat.remove_unused_categories()
        df_codes["departement_id"] = df_codes["departement_id"].cat.remove_unused_categories()

        return df_codes

def validate(context):
    # Check if we're running Thailand synthesis
    hts = context.config("hts", "france")

    if hts == "thailand":
        # For Thailand, validation is handled by TAZ zones module
        return True
    else:
        # Original France validation logic
        if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("codes_path"))):
            raise RuntimeError("Spatial reference codes are not available")
        return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("codes_path")))
