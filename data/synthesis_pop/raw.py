import pandas as pd
import os
import zipfile

"""
This stage loads the synthesis population data from the SILO
"""

def configure(context):
    context.config("data_path")
    context.config("file_path", "thailand_microdata_2015.zip")
    context.config("pp_csv", "pp_2015.csv")
    context.config("dd_csv", "dd_2015.csv")
    context.config("jj_csv", "jj_2015.csv")
    context.config("hh_csv", "hh_2015.csv")
    context.config("ss_csv", "ss_2015.csv")

dtype_obj=dict(
PP_COLUMNS_DTYPES = {
    "hhid": "int32",
    "age": "int8",
    "gender": "int8",
    "relationShip": "str",
    "occupation": "int8",
    "driversLicense": "bool",
    "workplace":"int32",
    "income": "int32",
    "schoolId": "int16",
    "schoolDistance": "float32",
    "schoolType": "int8"
    
},DD_COLUMNS_DTYPES = {
   "zone": "int32",
   "type": "str",
   "hhID": "int32",
   "bedrooms": "int8",
   "quality": "int8",
   "monthlyCost": "int8",
   "yearBuilt": "int8",
   "coordX": "float32",
   "coordY": "float32"
},
JJ_COLUMNS_DTYPES = {
   "zone": "int32",
   "personId": "int32",
   "type": "str",
   "coordX": "float32",
   "coordY": "float32",
   "startTime": "int32",
   "duration": "int32"
},
HH_COLUMNS_DTYPES = {
   "dwelling": "int32",
   "hhSize": "int8",
   "autos": "int8"
},
SS_COLUMNS_DTYPES = {
   "zone": "int32",
   "type": "int8",
   "capacity": "int32",
   "occupancy": "int32",
   "coordX": "float32",
   "coordY": "float32",
   "startTime": "int32",
   "duration": "int32"
})

def execute(context):
    
    data_list=["pp","dd","jj","hh","ss"]
    data_obj=dict()
    with zipfile.ZipFile(
                "{}/{}".format(context.config("data_path"), context.config("file_path"))) as archive:
        for d in data_list:
            df_records = []
            with context.progress(label = f"Reading {d} ...") as progress:
                    with archive.open(context.config(f"{d}_csv")) as f:
                        csv = pd.read_csv(f, 
                                usecols = dtype_obj[f"{d.upper()}_COLUMNS_DTYPES"].keys(),
                                dtype = dtype_obj[f"{d.upper()}_COLUMNS_DTYPES"],
                                chunksize = 10240)
            
                        for df_chunk in csv:
                            progress.update(len(df_chunk))
                            if len(df_chunk) > 0:
                                df_records.append(df_chunk)
            data_obj[d]=pd.concat(df_records)

    return data_obj


def validate(context):
    if not os.path.exists("{}/{}".format(context.config("data_path"), context.config("file_path"))):
        raise RuntimeError("thailand micro data 2015 is not available")

    return os.path.getsize("{}/{}".format(context.config("data_path"), context.config("file_path")))
