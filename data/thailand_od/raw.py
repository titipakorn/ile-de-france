import pandas as pd
import os
import zipfile

"""
Loads raw OD data from French census data.
"""

def configure(context):
    context.config("data_path")
    context.config("od_pro_path", "BMR_OD_PCU.csv")

def execute(context):
    # First, load work
    with context.progress(label = "Reading OD flows ...") as progress:
        csv = pd.read_csv("%s/%s" % (context.config("data_path"), context.config("od_pro_path")))
    # Convert columns to float except the first one
    for column in csv.columns[1:]:
        if(csv[column].dtypes)==object:
            csv[column] = csv[column].str.replace(',', '').astype(float)
    csv = csv.set_index('Zone')
    return csv


def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("od_pro_path"))):
        raise RuntimeError("Thailand OD data is not available")

    return [
        os.path.getsize("%s/%s" % (context.config("data_path"), context.config("od_pro_path"))),
    ]
