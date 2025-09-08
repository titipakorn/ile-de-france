import pandas as pd
import numpy as np
import os

"""
This stage outputs the scaled Thailand population synthesis data.
"""

def configure(context):
    context.stage("data.hts.thailand.scaled")
    context.config("output_path")
    context.config("output_prefix", "thailand_")
    context.config("output_formats", ["csv", "parquet"])

def execute(context):
    # Load scaled Thailand population data
    df_households, df_persons, df_trips = context.stage("data.hts.thailand.scaled")

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

    # Generate summary statistics
    print(f"\n=== THAILAND POPULATION SYNTHESIS SUMMARY ===")
    print(f"Final scaled population:")
    print(f"- Households: {len(df_households):,}")
    print(f"- Persons: {len(df_persons):,}")
    print(f"- Trips: {len(df_trips):,}")

    # Calculate key statistics
    avg_hh_size = df_persons.groupby("household_id").size().mean()
    avg_trips_per_person = len(df_trips) / len(df_persons) if len(df_persons) > 0 else 0

    print(f"\nKey statistics:")
    print(f"- Average household size: {avg_hh_size:.2f}")
    print(f"- Average trips per person: {avg_trips_per_person:.2f}")

    if "person_weight" in df_persons.columns:
        total_weighted_pop = df_persons["person_weight"].sum()
        print(f"- Total weighted population: {total_weighted_pop:,.0f}")

    # Output breakdown by mode
    if "mode" in df_trips.columns and len(df_trips) > 0:
        print(f"\nTrip mode distribution:")
        mode_dist = df_trips["mode"].value_counts()
        for mode, count in mode_dist.items():
            pct = 100 * count / len(df_trips)
            print(f"- {mode}: {count:,} trips ({pct:.1f}%)")

    # Output breakdown by purpose
    if "following_purpose" in df_trips.columns and len(df_trips) > 0:
        print(f"\nTrip purpose distribution:")
        purpose_dist = df_trips["following_purpose"].value_counts()
        for purpose, count in purpose_dist.items():
            pct = 100 * count / len(df_trips)
            print(f"- {purpose}: {count:,} trips ({pct:.1f}%)")

    # Output files
    for name, df in output_data.items():
        print(f"\nOutputting {name}: {len(df):,} records")

        for fmt in formats:
            if fmt == "csv":
                output_file = f"{output_path}/{prefix}{name}_scaled.csv"
                df.to_csv(output_file, index=False)
                print(f"  -> {output_file}")
            elif fmt == "parquet":
                output_file = f"{output_path}/{prefix}{name}_scaled.parquet"
                df.to_parquet(output_file, index=False)
                print(f"  -> {output_file}")

    print(f"\n=== POPULATION SYNTHESIS COMPLETE ===")

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
