from tqdm import tqdm
import pandas as pd
import numpy as np
import data.hts.hts as hts

"""
This stage cleans the national HTS.
"""

def configure(context):
    context.stage("data.hts.thailand.raw")

PURPOSE_MAP = [
    ("1", "work"),
    ("2", "education"),
    ("3", "other"),
    ("4", "other"),
    # ("5", "escort"),
    ("6", "home"),
]

MODES_MAP = [
    ("0", "stay"),
    ("1", "car"),
    ("2", "car"), # passenger
    ("3", "bike"), # bike
    ("4", "car_passenger"), # motorcycle passenger
    ("5", "pt"),
    ("6", "pt"),
    ("7", "pt"),
    ("8", "pt"), # van
    ("9", "pt"), # taxi
    ("10", "pt"), #bike taxi
    ("11", "walk"), # walk/bikecycle
    ("12", "pt"), # Boat
    ("13", "pt"), # Boat
    ("14", "pt"), # Boat
    ("15", "pt"), # other
]

def fix_time(x):
    if len(x) == 10:
        return "00:00:00.000"
    elif len(x) == 12:
        return x
    else:
        return x[11:]

def fix_escort(x):
    if(x['T_PURPOSE']==5):
        if x['T_Type'].endswith("W"):
            return 1
        elif x['T_Type'].endswith("E"):
            return 2
        else:
            return 3
    else:
        return x['T_PURPOSE']
    
def convert_time(x):
    return np.dot(np.array(x.split(":"), dtype = float), [3600.0, 60.0, 1.0])

def execute(context):
    df_household, df_person, df_trip = context.stage("data.hts.thailand.raw")

    # Make copies
    df_trips = pd.DataFrame(df_trip, copy = True)
    df_persons = pd.DataFrame(df_person, copy = True)
    df_households = pd.DataFrame(df_household, copy = True)
    
    sum_df = df_trips.groupby(['P_CODE','T_NUMBER'])['T_DISTANCE','T_TIME','T_TOLL','T_FARE'].sum()
    sum_df = sum_df.reset_index()
    selected_columns=['P_CODE','T_Type','T_NUMBER','T_PURPOSE','T_DEPARTURE','T_ARRIVAL','T_MODE','T_ORIGIN_LOCATIONCODE','T_DESTINATION_LOCATIONCODE','T_DESTINATION_ZONECODE','T_ORIGIN_ZONECODE']
    df_trips = sum_df.merge(df_trips[selected_columns], on=['P_CODE','T_NUMBER'], how='left')
    df_trips = df_trips.drop_duplicates(subset=['P_CODE','T_NUMBER'], keep='first')
    #fix trip_purpose
    df_trips["T_PURPOSE"]=df_trips.apply(fix_escort,axis=1)
    
    df_trips['PRE_T_PURPOSE'] = df_trips.groupby(['P_CODE'])['T_PURPOSE'].shift(1).fillna(6).astype(int)
    df_trips['PRO_T_PURPOSE'] = df_trips['T_PURPOSE']

    df_persons["person_id"] = np.arange(len(df_persons))
    
    #rename columns
    # ['person_id', 'household_id', 'person_weight', 'age', 'sex', 'employed',
    #        'studies', 'has_license', 'has_pt_subscription', 'number_of_trips',
    #        'departement_id', 'trip_weight', 'is_passenger',
    #        'socioprofessional_class']
    df_persons = df_persons.rename(columns={"HH_NUMBER":"household_id","P_AGE": "age",
                                            "Person Weight":"person_weight"})
    df_persons.loc[df_persons["P_GENDER"] == 1, "sex"] = "male"
    df_persons.loc[df_persons["P_GENDER"] == 2, "sex"] = "female"
    df_persons["sex"] = df_persons["sex"].astype("category")
    # ['person_id', 'trip_id', 'trip_weight', 'departure_time', 'arrival_time',
    #    'trip_duration', 'activity_duration', 'following_purpose',
    #    'preceding_purpose', 'is_last_trip', 'is_first_trip', 'mode',
    #    'origin_departement_id', 'destination_departement_id',
    #    'routed_distance', 'euclidean_distance']
    df_trips = pd.merge(df_trips,df_persons[["P_CODE","person_id"]])
    # df_trips = df_trips.rename(columns={"P_CODE":"person_id"})
    df_trips["trip_id"] = np.arange(len(df_trips))

    # ['household_id', 'household_weight', 'household_size',
    #    'number_of_vehicles', 'number_of_bikes', 'departement_id',
    #    'consumption_units', 'income_class']
    df_households["number_of_vehicles"]=df_households["HH_PC"]+df_households["HH_BIZCAR"]+df_households["HH_BIZTRUCK"]
    df_households["number_of_bikes"]=df_households["HH_MC"]
    df_households = df_households.rename(columns={"HH_NUMBER":"household_id",
                                                  "Weight_3D": "household_weight",
                                                  "HH_TOTALMEMBER":"household_size",
                                                  "HH_INCOME":"income_class",
                                                  "870_Zone":"departement_id"})
    # occupation
    # 1) student 2) worker 3) home worker 4) jobless
    
    # Clean employment
    df_persons["employed"] = df_persons["P_OCCUPATION"].isin([2])

    # Studies
    # Many < 14 year old have NaN
    df_persons["studies"] = df_persons["P_OCCUPATION"].fillna(0) == 1
    df_persons.loc[df_persons["age"] < 5, "studies"] = False
    
    # Trip purpose
    df_trips["following_purpose"] = "other"
    df_trips["preceding_purpose"] = "other"

    # df_trips["following_purpose"] = df_trips["following_purpose"].astype("category")
    # df_trips["preceding_purpose"] = df_trips["preceding_purpose"].astype("category")

    # # Mark previous and next values for each person
    # df_trips['PRE_T_PURPOSE'] = df_trips.groupby('T_CODE')['T_PURPOSE'].shift(1)
    # df_trips['PRO_T_PURPOSE'] = df_trips.groupby('T_CODE')['T_PURPOSE'].shift(-1)
    
    
    for prefix, activity_type in PURPOSE_MAP:
        df_trips.loc[
            df_trips["PRO_T_PURPOSE"].astype(str).str.startswith(prefix), "following_purpose"
        ] = activity_type

        df_trips.loc[
            df_trips["PRE_T_PURPOSE"].astype(str).str.startswith(prefix), "preceding_purpose"
        ] = activity_type
        
    # Trip mode
    df_trips["mode"] = "pt"

    for prefix, mode in MODES_MAP:
        df_trips.loc[
            df_trips["T_MODE"].astype(str).str.startswith(prefix), "mode"
        ] = mode
    #filter stay mode
    df_trips =df_trips[df_trips["mode"]!="stay"]
    df_trips["mode"] = df_trips["mode"].astype("category")

    # Further trip attributes
    df_trips["routed_distance"] = df_trips["T_DISTANCE"] * 1000.0
    df_trips["routed_distance"] = df_trips["routed_distance"].fillna(0.0) # This should be just one within Île-de-France


    # Trip flags
    df_trips = hts.compute_first_last(df_trips)

    # Trip times
    df_trips["T_DEPARTURE"] = df_trips["T_DEPARTURE"].apply(fix_time)
    df_trips["T_ARRIVAL"] = df_trips["T_ARRIVAL"].apply(fix_time)
    df_trips["departure_time"] = df_trips["T_DEPARTURE"].apply(convert_time).astype(float)
    df_trips["arrival_time"] = df_trips["T_ARRIVAL"].apply(convert_time).astype(float)
    df_trips = hts.fix_trip_times(df_trips)

    # Durations
    df_trips["trip_duration"] = df_trips["arrival_time"] - df_trips["departure_time"]
    hts.compute_activity_duration(df_trips)

    # # Add weight to trips
    # df_trips["trip_weight"] = df_trips["PONDKI"]

    # Chain length
    df_persons = pd.merge(
        df_persons, df_trips.groupby('person_id')['T_NUMBER'].max().reset_index().rename(columns = { "T_NUMBER": "number_of_trips" }),
        on = "person_id", how = "left"
    )
    df_persons["number_of_trips"] = df_persons["number_of_trips"].fillna(-1).astype(int)
    # df_persons.loc[(df_persons["number_of_trips"] == -1) & df_persons["is_kish"], "number_of_trips"] = 0

    # # Passenger attribute
    #TODO mathing with trips in a household
    df_persons["is_passenger"] = df_persons["person_id"].isin(
        df_trips[df_trips["mode"] == "car_passenger"]["person_id"].unique()
    )

    # Calculate consumption units
    hts.check_household_size(df_households, df_persons)
    df_households = pd.merge(df_households, hts.calculate_consumption_units(df_persons), on = "household_id")

    # Socioprofessional class
    # df_persons["socioprofessional_class"] = df_persons["CS24"].fillna(80).astype(int) // 10

    return df_households, df_persons, df_trips

def calculate_income_class(df):
    assert "household_income" in df
    assert "consumption_units" in df

    return np.digitize(df["household_income"], INCOME_CLASS_BOUNDS, right = True)
