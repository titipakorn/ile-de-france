#%%
import synpp
import os
import hashlib
import pandas as pd
import numpy as np
import itertools


data_path = "/home/users/v-surapoom/Workspaces/ile-de-france/experiments/data"
cache_path = "cache"
output_path = "test_output"
config = dict(random_seed=12345,sampling_rate=0.01,
    data_path = data_path, output_path = output_path,
    output_prefix = "test_003", hts = "entd",java_memory="50G",
    processes=32)
    # %%


stages = [
    dict(descriptor = "synthesis_thailand.locations.work"),
]

test_stage=synpp.run(stages, config, working_directory = cache_path)
# %%


stages = [
    dict(descriptor = "synthesis_thailand.locations.work"),
    # dict(descriptor = "synthesis.population.activities"),
]

test_stage=synpp.run(stages, config, working_directory = cache_path)
# %%

stages_2 = [
    dict(descriptor = "synthesis_thailand.output"),
    dict(descriptor = "matsim_thailand.output"),
    # dict(descriptor = "synthesis_thailand.population.spatial.locations"),
    #  dict(descriptor = "synthesis_thailand.population.activities"),
        # dict(descriptor = "synthesis_thailand.population.enriched"),
    #  dict(descriptor = "matsim_thailand.scenario.population"),
    # dict(descriptor = "synthesis_thailand.population.spatial.secondary.distance_distributions"),
    # dict(descriptor = "synthesis_thailand.population.spatial.primary.locations"),
    # dict(descriptor = "synthesis_thailand.population.spatial.home.locations"),

]

test_stage_2=synpp.run(stages_2, config, working_directory = cache_path)
#%%
df_households, df_persons, df_trips=test_stage_2[0]
#%%
activity_type='work'
distance_slot = "routed_distance"
distance_factor = 1.0 # / 1.3

# Add commuting distances
df_commute_distance = df_trips[
    ((df_trips["preceding_purpose"] == "home") & (df_trips["following_purpose"] == activity_type)) |
    ((df_trips["preceding_purpose"] == activity_type) & (df_trips["following_purpose"] == "home"))
].drop_duplicates("person_id", keep = "first")[["person_id", distance_slot]].rename(columns = { distance_slot: "commute_distance" })
# %%

stages = [
     dict(descriptor = "data.od.raw"),
    #  dict(descriptor = "data.spatial.secondary"),
    # dict(descriptor = "synthesis_thailand.locations.education"),
    # dict(descriptor = "synthesis_thailand.locations.secondary")
]

test_stage_3=synpp.run(stages, config, working_directory = cache_path)

# %%
stages_4 = [
          dict(descriptor = "synthesis.population.spatial.home.locations"),
     dict(descriptor = "synthesis.population.spatial.primary.locations"),
    dict(descriptor = "synthesis.population.spatial.secondary.locations")
]

test_stage_4=synpp.run(stages_4, config, working_directory = cache_path)

# %%
