from tqdm import tqdm
import pandas as pd
import os

"""
This stage loads the raw data of the Bangkok HTS.
"""

def configure(context):
    context.config("data_path")

def execute(context):
    df_trip = pd.read_csv(
        "%s/thailand_hts/Trip.csv" % context.config("data_path"),
        sep = ";", encoding = "utf-8"
    )
    
    df_person = pd.read_csv(
        "%s/thailand_hts/Person.csv" % context.config("data_path"),
        sep = ";", encoding = "utf-8"
    )
    
    df_household = pd.read_csv(
        "%s/thailand_hts/Household.csv" % context.config("data_path"),
        sep = ";", encoding = "utf-8"
    )

    return df_household, df_person, df_trip

def validate(context):
    for name in ("thailand_hts/Trip.csv","thailand_hts/Hosehold.csv","thailand_hts/Person.csv"):
        if not os.path.exists("%s/%s" % (context.config("data_path"), name)):
            raise RuntimeError("File missing from HTS: %s" % name)

    return [
        os.path.getsize("%s/thailand_hts/Trip.csv" % context.config("data_path")),
        os.path.getsize("%s/thailand_hts/Hosehold.csv" % context.config("data_path")),
        os.path.getsize("%s/thailand_hts/Person.csv" % context.config("data_path")),
    ]
