import numpy as np

def configure(context):
    context.stage("data.thailand_spatial.secondary")

def execute(context):
    df_locations = context.stage("data.thailand_spatial.secondary")
    df_locations["destination_id"] = np.arange(len(df_locations))

    # Attach attributes for activity types
    df_locations["offers_leisure"] = df_locations["category_c"].isin((10,70,80))
    df_locations["offers_shop"] = df_locations["category_c"] == 40
    df_locations["offers_other"] = ~(df_locations["offers_leisure"] | df_locations["offers_shop"])

    # Define new IDs
    df_locations["location_id"] = np.arange(len(df_locations))
    df_locations["location_id"] = "sec_" + df_locations["location_id"].astype(str)

    return df_locations
