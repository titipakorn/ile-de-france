import numpy as np
import pandas as pd
import itertools

"""
This stage has the census data as input and samples households according to the
household weights given by INSEE. The resulting sample size can be controlled
through the 'sampling_rate' configuration option.
"""

def configure(context):
    # context.stage("data.census.filtered")
    context.stage("data.synthesis_pop.raw")
    context.config("random_seed")
    context.config("sampling_rate")

def execute(context):
    random = np.random.RandomState(context.config("random_seed"))
    sampling_rate=context.config("sampling_rate")
    
    syn_pop = context.stage("data.synthesis_pop.raw")
    df_hh=syn_pop["hh"].copy()
    df_hh["hhid"]=df_hh.reset_index().index+1
    df_hh=df_hh.sort_values(by="hhid")
    
    df_dd = syn_pop["dd"].copy()
    df_dd["dwelling_id"] = df_dd.reset_index().index+1
    df_dd=df_dd[["zone","dwelling_id"]]
    df_dd = df_dd.rename(columns={"zone":"departement_id"})

    selector = random.random_sample(syn_pop["hh"].shape[0]) < sampling_rate
    df_hh = df_hh[selector].rename(columns={"dwelling":"dwelling_id"})
    df_hh = pd.merge(df_hh,df_dd)

    df_pp = syn_pop["pp"]
    df_pp["person_id"] = df_pp.reset_index().index+1
    df_pp.loc[df_pp["gender"] == 1, "sex"] = "male"
    df_pp.loc[df_pp["gender"] == 2, "sex"] = "female"
    df_pp["sex"] = df_pp["sex"].astype("category")
    df_pp["couple"] = df_pp["relationShip"] == "married"
    df_pp["employed"] = df_pp["occupation"] == 1
    df_pp["studies"] = df_pp["occupation"] == 3

    df_target = pd.merge(df_hh, df_pp)
    df_target = df_target.rename(columns={"hhid":"household_id","hhSize":"household_size","autos":"number_of_vehicles","driversLicense":"has_license"})
    
    return df_target
