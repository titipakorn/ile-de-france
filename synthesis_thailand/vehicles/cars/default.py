
import pandas as pd
import numpy as np

def configure(context):
    context.stage("synthesis_thailand.population.enriched")
    context.stage("data.vehicles.raw")
    context.stage("data.vehicles.types")

def execute(context):
    df_households = context.stage("synthesis_thailand.population.enriched")[["household_id", "car_availability"]].drop_duplicates()
    df_raw_vehicles = context.stage("data.vehicles.raw")
    df_vehicle_types = context.stage("data.vehicles.types")

    # Filter for car types
    car_types = df_vehicle_types[df_vehicle_types["mode"] == "car"]["type_id"].unique()
    df_raw_cars = df_raw_vehicles[df_raw_vehicles["vehicle_type"].isin(car_types)]

    # Simple assignment: for households that have cars, assign a random car model from the raw data
    households_with_cars = df_households[df_households["car_availability"].isin(["1", "2+"])]
    
    if households_with_cars.empty or df_raw_cars.empty:
        return pd.DataFrame(columns=["household_id", "vehicle_type"])

    # Create a pool of available cars to sample from
    car_pool = df_raw_cars["vehicle_type"].values

    assigned_cars = []
    for _, household in households_with_cars.iterrows():
        num_cars = 1 if household["car_availability"] == "1" else np.random.randint(2, 4) # For "2+", assign 2 or 3 cars
        for _ in range(num_cars):
            chosen_car_type = np.random.choice(car_pool)
            assigned_cars.append({
                "household_id": household["household_id"],
                "vehicle_type": chosen_car_type
            })

    df_assigned_cars = pd.DataFrame(assigned_cars)
    return df_assigned_cars
