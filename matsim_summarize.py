#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

# Create a dfFrame from the given df
bau_case="scenarios/bau_capacity/simulation_output_02/eqasim_trips.csv"

df = pd.read_csv(bau_case, sep=';')

#%%
#focusing on working trip
# df = df[(df['preceding_purpose']=="home") & (df['following_purpose']=="work")]
# #focusing on school trip
# df = df[(df['preceding_purpose']=="home") & (df['following_purpose']=="education")]

# Calculate the trip duration in minutes
df['trip_duration'] = df['travel_time'] / 60

# Define the bin edges for the histogram
bin_edges = np.arange(0, 360, 30)
axes = df.hist(column='trip_duration', bins=bin_edges,density=True, grid=False, figsize=(12, 8), color='#86bf91', rwidth=0.9)
ax = axes[0, 0]
total = len(df)
# ax.set_xticks(bin_edges_x)
# ax.grid(True, axis='y', ls=':', alpha=0.4)
# ax.set_axisbelow(True)
# for dir in ['left', 'right', 'top']:
#     ax.spines[dir].set_visible(False)
# ax.tick_params(axis="y", length=0)  # Switch off y ticks
# ax.margins(x=0.02) # tighter x margins
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.xlabel('Trip Duration (30-min)')
plt.ylabel('Frequency (%)')
plt.title('Trip Duration Distribution')
plt.show()

#%%
# df=df[(df["preceding_purpose"]=="work") | (df["following_purpose"]=="work")]

df=df[(df["preceding_purpose"]=="education") | (df["following_purpose"]=="education")]

# %%

# 2. Trip Distance and Duration
df['travel_time_minute']=df['travel_time']/60
df['vehicle_distance_km']=df['vehicle_distance']/1000
df['routed_distance_km']=df['routed_distance']/1000
# Plotting trip distance and duration
plt.figure(figsize=(12, 6))

# Plot trip distance
plt.subplot(1, 2, 1)
plt.hist(df['routed_distance_km'], bins=range(0, 100,5),density=True, edgecolor='black')
plt.title('Trip Distance Distribution')
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.xlabel('Distance 5-km')
plt.ylabel('Frequency (%)')

# Plot trip duration
plt.subplot(1, 2, 2)
plt.hist(df['travel_time_minute'], bins=range(0,120,5),density=True, edgecolor='black')
plt.title('Trip Duration Distribution')
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.xlabel('Duration 5-min')
plt.ylabel('Frequency (%)')

plt.tight_layout()
plt.show()

# Plot trip distance
plt.hist(df[df['vehicle_distance_km']>0]['vehicle_distance_km'], bins=range(0, 100,5),density=True, edgecolor='black')
plt.title('Car Distance Distribution')
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.xlabel('Distance 5-km')
plt.ylabel('Frequency (%)')
plt.show()
# %%
