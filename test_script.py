# %%
import synpp
import os
import hashlib
import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt

data_path = "/home/users/v-surapoom/Workspaces/ile-de-france/experiments/data"
cache_path = "cache"
output_path = "scenarios/test03/bau"
config = dict(
    random_seed=12345,
    sampling_rate=0.01,
    data_path=data_path,
    output_path=output_path,
    output_prefix="v01",
    hts="entd",
    java_memory="50G",
    processes=32,
)

# Adjust display option to show all columns
pd.set_option("display.max_columns", None)
# %%

stages = [
    dict(descriptor="data.hts.thailand.cleaned"),
    dict(descriptor="synthesis_thailand.population.activities"),
    dict(descriptor="synthesis_thailand.population.trips"),
    dict(descriptor="synthesis_thailand.population.enriched"),
    #   dict(descriptor = "synthesis_thailand.population.scenarios.no_education_escort_trip"),
    # dict(descriptor = "synthesis_thailand.population.scenarios.work_time_shift"),
]

test_stage = synpp.run(stages, config, working_directory=cache_path)
# df_trips=test_stage[0][2]

# %%
hts_persons = test_stage[3]
hts_trips = test_stage[2]
students = hts_trips[(hts_trips["preceding_purpose"] == "home") & (hts_trips["following_purpose"] == "education")]
students = pd.merge(students, hts_persons, on="person_id")
students = students[(students["employed"] == False) & (students["studies"] == True)]

# %%
# student trips from HTS
hts_trips = test_stage[0][2]
hts_persons = test_stage[0][1]
# %%
# Student Trip Modes

students = hts_trips[(hts_trips["T_PURPOSE"] == 2)]
students = pd.merge(students, hts_persons, on="P_CODE")
students = students[(students["employed"] == False) & (students["studies"] == True)]
# %%
plt.figure(figsize=(6, 6))
trip_modes = students["mode"].value_counts()
# Plotting trip modes
# Plotting trip distance and duration
case_name = ""
colors = ["#0079B9", "#FF7500", "#00A200", "#E90017"]
labels = ["car", "pt", "car_passenger", "walk"]
trip_modes.plot(
    kind="pie", autopct=lambda x: f"""{x:1.1f}%\n({x * (trip_modes.sum()) / 100:.0f})""", colors=colors, labels=labels
)
# Set the aspect ratio to be equal so that pie is drawn as a circle
plt.axis("equal")
plt.title(f"{case_name} Student Trip Modes")
plt.ylabel("")
plt.show()
# %%
students = hts_trips[(hts_trips["T_PURPOSE"] == 2)]
students = pd.merge(students, hts_persons, on="P_CODE")
students = students[(students["employed"] == True) & (students["studies"] == False)]
# %%
# Student's Parent Trip Modes
students = hts_trips[(hts_trips["following_purpose"] == "education")]
students = pd.merge(students, hts_persons, on="person_id")
students = students[(students["employed"] == True) & (students["studies"] == False)]
# %%
trip_modes = students["mode"].value_counts()
# Plotting trip modes
# Plotting trip distance and duration
plt.figure(figsize=(6, 6))
case_name = ""
colors = ["#0079B9", "#FF7500", "#00A200", "#E90017"]
labels = ["car", "pt", "car_passenger", "walk"]
trip_modes.plot(
    kind="pie", autopct=lambda x: f"""{x:1.1f}%\n({x * (trip_modes.sum()) / 100:.0f})""", colors=colors, labels=labels
)
# Set the aspect ratio to be equal so that pie is drawn as a circle
plt.axis("equal")
plt.title(f"""{case_name} Student's Parent Trip Modes""")
plt.ylabel("")
plt.show()


# %%
drive_students = hts_trips[(hts_trips["T_PURPOSE"] == 2) & (hts_trips["mode"] == "car")]
drive_students = pd.merge(drive_students, hts_persons, on="P_CODE")

# %%
# Define the bin size and range
unemployed_students = drive_students[drive_students["employed"] == False]
unemployed_students["age"] = unemployed_students["age"].astype(int)
bin_size = 5
min_age = unemployed_students["age"].min()
max_age = unemployed_students["age"].max()
bins = range(min_age, max_age + bin_size, bin_size)

# Create the bin chart
plt.hist(unemployed_students["age"], bins=bins, edgecolor="black", alpha=0.7)
plt.xticks(bins)
plt.xlabel("Age")
plt.ylabel("Count")
plt.title("Age Distribution")
plt.grid(True)
plt.show()

# %%
pt_students = hts_trips[(hts_trips["T_PURPOSE"] == 2) & (hts_trips["mode"] == "pt")]
pt_students = pd.merge(pt_students, hts_persons, on="P_CODE")
# Define the bin size and range
unemployed_students = pt_students[pt_students["employed"] == False]
unemployed_students["age"] = unemployed_students["age"].astype(int)
bin_size = 5
min_age = unemployed_students["age"].min()
max_age = unemployed_students["age"].max()
bins = range(min_age, max_age + bin_size, bin_size)

# Create the bin chart
plt.hist(unemployed_students["age"], bins=bins, edgecolor="black", alpha=0.7)
plt.xticks(bins)
plt.xlabel("Age")
plt.ylabel("Count")
plt.title("Age Distribution")
plt.grid(True)
plt.show()

# %%
students["age"] = students["age"].astype(int)
bin_size = 5
min_age = students["age"].min()
max_age = students["age"].max()
bins = range(min_age, max_age + bin_size, bin_size)

# Create the bin chart
plt.hist(students["age"], bins=bins, edgecolor="black", alpha=0.7)
plt.xticks(bins)
plt.xlabel("Age")
plt.ylabel("Count")
plt.title("Age Distribution")
plt.grid(True)
plt.show()
# %%
students["person_weight"] = students["person_weight"].astype(int)
bin_size = 200
min_age = 0
max_age = 1000
bins = range(min_age, max_age + bin_size, bin_size)

# Create the bin chart
plt.hist(students[students["age"] < 18]["person_weight"], bins=bins, edgecolor="black", alpha=0.7)
plt.xticks(bins)
plt.xlabel("Person_weight")
plt.ylabel("Count")
plt.title("Person Weight Distribution")
plt.grid(True)
plt.show()
# %%
student_hts_trips = hts_trips[(hts_trips["T_PURPOSE"] == 2) & (hts_trips["mode"] == "car")]

# %%
# df_persons=test_stage[3]
trips = test_stage[2]
students = trips[(trips["following_purpose"] == "education") & (trips["activity_duration"] >= 20000)][
    "person_id"
].unique()
student_parents = trips[(trips["following_purpose"] == "education") & (trips["activity_duration"] < 20000)][
    "person_id"
].unique()
print("Number Of Students:", len(students))
print("Number Of Parents who went to school:", len(student_parents))
print(f"Parent/Student Ratio {len(student_parents)/len(students)*100:.2f} %")
# df_students=df_persons[df_persons["person_id"].isin(students)]

# %%
# Student Trip Modes
plt.figure(figsize=(6, 6))
trip_modes = trips[trips["person_id"].isin(students)]["mode"].value_counts()
# Plotting trip modes
# Plotting trip distance and duration
case_name = "Parent x50"
colors = ["#0079B9", "#FF7500", "#00A200", "#E90017"]
labels = ["car", "pt", "car_passenger", "walk"]
trip_modes.plot(
    kind="pie", autopct=lambda x: f"""{x:1.1f}%\n({x * (trip_modes.sum()) / 100:.0f})""", colors=colors, labels=labels
)
# Set the aspect ratio to be equal so that pie is drawn as a circle
plt.axis("equal")
plt.title(f"{case_name} Student Trip Modes")
plt.ylabel("")
plt.show()

# df_students=df_students[df_students["employed"]==False]


# %%

# data=test_stage[0][2]

data = test_stage[2]

# %%

# data=data[(data["preceding_purpose"]=="work") | (data["following_purpose"]=="work")]

data = data[(data["preceding_purpose"] == "education") | (data["following_purpose"] == "education")]


# %%
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# %%
# 4. Trip Purposes
data["trip_leg"] = data["preceding_purpose"] + "_" + data["following_purpose"]

# %%
trip_purposes = data["trip_leg"].value_counts()
# trip_purposes=data[["trip_leg","T_DISTANCE"]].groupby("trip_leg").sum()
# trip_purposes = trip_purposes / trip_purposes.sum() * 100
# trip_purposes = trip_purposes[trip_purposes>1]
# Plotting trip purposes
plt.figure(figsize=(12, 6))
trip_purposes.plot(kind="bar")
# xlocs, xlabs = plt.xticks()
# for i, v in enumerate(trip_purposes):
#     plt.text(xlocs[i] - 0.15, v + 0.2, '{:.2f}%'.format(v))
# plt.gca().yaxis.set_major_formatter(PercentFormatter(100))
plt.title("Trip Purpose Distribution")
plt.xlabel("Purpose")
plt.ylabel("Frequency")
plt.xticks(rotation=45)
plt.show()

# %%
import matplotlib.dates as mdates

# Convert departure_time to datetime format
data["departure_time"] = pd.to_datetime(data["departure_time"], unit="s")

# Group departure time into 15-minute intervals
data["departure_time_grouped"] = data["departure_time"].dt.floor("60min")
# data['departure_time_grouped']=pd.to_datetime(data['departure_time_grouped'],format).apply(lambda x: x.hour())
data["departure_time_grouped"] = pd.to_datetime(data["departure_time_grouped"]).dt.strftime("%H")
# Calculate the count for each time interval
departure_time_distribution = data["departure_time_grouped"].value_counts().sort_index()
# Calculate the percentage for each time interval
departure_time_distribution = departure_time_distribution / departure_time_distribution.sum() * 100
# Plotting trip departure time distribution
# %%
trip_duration_purposes = (
    data.groupby(
        [
            "departure_time_grouped",
            "following_purpose",
        ]
    )
    .size()
    .unstack()
    .fillna(0)
)
trip_duration_purposes_percentage = trip_duration_purposes.div(trip_duration_purposes.sum(axis=1), axis=0) * 100

# Plotting trip duration with stacked trip purpose proportions
plt.figure(figsize=(12, 6))

# Create a stacked bar chart for trip duration and trip purpose proportions
trip_duration_purposes_percentage.plot(kind="bar", stacked=True, edgecolor="black")

plt.title("Trip Duration and Trip Purpose Proportions")
plt.xlabel("Duration")
plt.ylabel("Percentage")
plt.legend(title="Trip Purpose")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()
# %%
plt.figure(figsize=(12, 6))
ax = departure_time_distribution.plot(kind="bar", width=0.7)
# # Create the stacked bar chart
# plt.bar(x, values1, label='Value 1')
# plt.bar(x, values2, bottom=values1, label='Value 2')
# plt.bar(x, values3, bottom=np.add(values1, values2), label='Value 3')

plt.gca().yaxis.set_major_formatter(PercentFormatter(100))
plt.title("Trip Departure Time Distribution")
plt.xlabel("Departure Time")
plt.ylabel("Frequency (%)")
plt.xticks(rotation=45)
plt.show()
# %%
# 2. Trip Distance and Duration
trip_distance_summary = data["T_DISTANCE"].describe()
data["trip_duration_minute"] = data["trip_duration"] / 60
trip_duration_summary = data["trip_duration_minute"].describe()


# Plotting trip distance and duration
plt.figure(figsize=(12, 6))

# Plot trip distance
plt.subplot(1, 2, 1)
plt.hist(data["T_DISTANCE"], bins=range(0, 100, 5), density=True, edgecolor="black")
plt.title("Trip Distance Distribution")
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.xlabel("Distance 5-km")
plt.ylabel("Frequency (%)")

# Plot trip duration
plt.subplot(1, 2, 2)
plt.hist(data["trip_duration_minute"], bins=range(0, 120, 5), density=True, edgecolor="black")
plt.title("Trip Duration Distribution")
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.xlabel("Duration 5-min")
plt.ylabel("Frequency (%)")

plt.tight_layout()
plt.show()

# %%
# 3. Trip Modes
trip_modes = data["mode"].value_counts()

# Plotting trip modes
plt.figure(figsize=(8, 6))
trip_modes.plot(kind="pie", autopct="%1.1f%%")
plt.title("Trip Modes")
plt.ylabel("")
plt.show()
# %%


stages = [
    dict(descriptor="synthesis_thailand.locations.work"),
    # dict(descriptor = "synthesis.population.activities"),
]

test_stage = synpp.run(stages, config, working_directory=cache_path)
# %%

stages_2 = [
    dict(descriptor="synthesis_thailand.output"),
    dict(descriptor="matsim_thailand.output"),
    # dict(descriptor = "synthesis_thailand.population.spatial.locations"),
    #  dict(descriptor = "synthesis_thailand.population.activities"),
    # dict(descriptor = "synthesis_thailand.population.enriched"),
    #  dict(descriptor = "matsim_thailand.scenario.population"),
    # dict(descriptor = "synthesis_thailand.population.spatial.secondary.distance_distributions"),
    # dict(descriptor = "synthesis_thailand.population.spatial.primary.locations"),
    # dict(descriptor = "synthesis_thailand.population.spatial.home.locations"),
]

test_stage_2 = synpp.run(stages_2, config, working_directory=cache_path)
# %%
df_households, df_persons, df_trips = test_stage[0]
# %%
activity_type = "work"
distance_slot = "routed_distance"
distance_factor = 1.0  # / 1.3

# Add commuting distances
df_commute_distance = (
    df_trips[
        ((df_trips["preceding_purpose"] == "home") & (df_trips["following_purpose"] == activity_type))
        | ((df_trips["preceding_purpose"] == activity_type) & (df_trips["following_purpose"] == "home"))
    ]
    .drop_duplicates("person_id", keep="first")[["person_id", distance_slot]]
    .rename(columns={distance_slot: "commute_distance"})
)
# %%

stages = [
    dict(descriptor="data.synthesis_pop.raw"),
    #  dict(descriptor = "data.spatial.secondary"),
    # dict(descriptor = "synthesis_thailand.locations.education"),
    # dict(descriptor = "synthesis_thailand.locations.secondary")
]

test_stage_3 = synpp.run(stages, config, working_directory=cache_path)

# %%
stages_4 = [
    dict(descriptor="synthesis.population.spatial.home.locations"),
    dict(descriptor="synthesis.population.spatial.primary.locations"),
    dict(descriptor="synthesis.population.spatial.secondary.locations"),
]

test_stage_4 = synpp.run(stages_4, config, working_directory=cache_path)

# %%

# Data for the stacked bar chart
categories = ["Category A", "Category B", "Category C"]
values1 = [30, 50, 20]
values2 = [15, 25, 35]
values3 = [10, 30, 15]

# Create an array to store the positions of the bars
x = np.arange(len(categories))

# Create the stacked bar chart
plt.bar(x, values1, label="Value 1")
plt.bar(x, values2, bottom=values1, label="Value 2")
plt.bar(x, values3, bottom=np.add(values1, values2), label="Value 3")

# Add labels, title, and legend
plt.xlabel("Categories")
plt.ylabel("Values")
plt.title("Stacked Bar Chart")
plt.legend()

# Set the x-axis tick labels
plt.xticks(x, categories)

# Display the chart
plt.show()

# %%
