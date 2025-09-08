import pandas as pd
import numpy as np
import os

"""
This stage outputs the simplified Thailand HTS data in the required formats.
"""

def configure(context):
    context.stage("data.hts.thailand.cleaned_simple")
    context.config("output_path")
    context.config("output_prefix", "thailand_")
    context.config("output_formats", ["csv"])

def execute(context):
    # Load simplified Thailand HTS data
    df_households, df_persons, df_trips = context.stage("data.hts.thailand.cleaned_simple")

    # Prepare output directory
    output_path = context.config("output_path")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    prefix = context.config("output_prefix")
    formats = context.config("output_formats")

    # Output datasets
    output_data = {
        "households": df_households,
        "persons": df_persons,
        "trips": df_trips
    }

    for name, df in output_data.items():
        print(f"Outputting {name}: {len(df)} records")

        for fmt in formats:
            if fmt == "csv":
                output_file = f"{output_path}/{prefix}{name}.csv"
                df.to_csv(output_file, index=False)
                print(f"  -> {output_file}")
            elif fmt == "parquet":
                output_file = f"{output_path}/{prefix}{name}.parquet"
                df.to_parquet(output_file, index=False)
                print(f"  -> {output_file}")

    return {
        "households": df_households,
        "persons": df_persons,
        "trips": df_trips
    }

def validate(context):
    # Check if output directory exists or can be created
    output_path = context.config("output_path")

    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path)
        except:
            raise RuntimeError(f"Cannot create output directory: {output_path}")

    return True
