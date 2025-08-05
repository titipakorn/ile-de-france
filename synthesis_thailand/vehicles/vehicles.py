import pandas as pd

def configure(context):
    # This will call the different vehicle assignment scripts
    context.stage("synthesis_thailand.vehicles.cars.default")
    # In the future, we could add motorcycle assignment here:
    # context.stage("synthesis_thailand.vehicles.motorcycles.default")

    context.stage("data.vehicles.types")

def execute(context):
    df_assigned_cars = context.stage("synthesis_thailand.vehicles.cars.default")
    df_vehicle_types = context.stage("data.vehicles.types")

    df_assigned_motorcycles = context.stage("synthesis_thailand.vehicles.motorcycles.default")
    df_all_vehicles = pd.concat([df_assigned_cars, df_assigned_motorcycles])

    if df_all_vehicles.empty:
        return pd.DataFrame(columns=["vehicle_id", "household_id", "vehicle_type"])

    # Assign a unique ID to each vehicle
    df_all_vehicles = df_all_vehicles.reset_index().rename(columns={"index": "vehicle_id"})
    df_all_vehicles["vehicle_id"] = "veh_" + df_all_vehicles["vehicle_id"].astype(str)

    # The final output should be two dataframes: one with the vehicle list, one with the types
    return df_vehicle_types, df_all_vehicles[["vehicle_id", "household_id", "vehicle_type"]]