# Open the cdmx flow file and print the first 10 lines
import sys
import os
import pandas as pd # type: ignore
import holidays # type: ignore
import geopandas as gpd # type: ignore
import numpy as np
lyon_data_file = 'data/lyon_data.csv'
if not os.path.exists(lyon_data_file):
    print(f"xxx File {lyon_data_file} does not exist.")
    sys.exit(1)
# Read the file and print the first 10 lines
rawDataAll = pd.read_csv(lyon_data_file)
rawDataAll.rename(columns={'number': 'station_id'}, inplace=True)
# Remove all records with 'Unknown' commune
rawDataAll = rawDataAll[rawDataAll['commune'] != 'Unknown']
print(f"--- Total number of hourly records: {len(rawDataAll)}")

# Read the lyon zones
lyon_zones_file = 'data/lyon_zones.csv'
if not os.path.exists(lyon_zones_file):
    print(f"File {lyon_zones_file} does not exist.")
    sys.exit(1)
# Read the file and print the first 10 lines
lyon_zones_data = pd.read_csv(lyon_zones_file)
lyon_zones_geo = gpd.GeoDataFrame(
    geometry=gpd.GeoSeries.from_wkt(lyon_zones_data['geometry'], crs=4326), data=lyon_zones_data
)

# Read the Lyon stations json
lyon_stations = pd.read_csv('data/lyon_stations.csv')
print(f"--- Total number of stations: {len(lyon_stations)}")
# Create a DataFrame with a geometry containing the Points
geo_lyon_stations = gpd.GeoDataFrame(
    lyon_stations, crs="EPSG:4326", geometry=gpd.points_from_xy(lyon_stations["lon"], lyon_stations["lat"])
)
geo_lyon_stations.to_crs(epsg=3857, inplace=True)
geo_lyon_stations['zone_name'] = geo_lyon_stations.apply(lambda x: lyon_zones_geo[lyon_zones_geo.contains(x.geometry)].iloc[0].nom if not lyon_zones_geo[lyon_zones_geo.contains(x.geometry)].empty else 'Unknown', axis=1)
geo_lyon_stations['zone_id'] = geo_lyon_stations.apply(lambda x: lyon_zones_geo.index[lyon_zones_geo.contains(x.geometry)].to_list()[0] if not lyon_zones_geo[lyon_zones_geo.contains(x.geometry)].empty else 'Unknown', axis=1)

# Identify the station name for each record in rawDataAll
geo_lyon_stations          = geo_lyon_stations.to_crs(epsg=3857).set_index('idstation')
rawDataAll['station_name'] = pd.Series(geo_lyon_stations.loc[rawDataAll['station_id']].nom.values,index=rawDataAll.index)
rawDataAll['zone_id']      = pd.Series(geo_lyon_stations.loc[rawDataAll['station_id']].zone_id.values,index=rawDataAll.index)
rawDataAll['zone_name']    = pd.Series(geo_lyon_stations.loc[rawDataAll['station_id']].zone_name.values,index=rawDataAll.index)


grouped = rawDataAll.groupby(['station_id', 'date', 'hour']).agg({'available_bikes': 'mean', 'stands': 'mean', 'capacity': 'mean'}).reset_index()
# A dataframe with the available bikes each day at 4:00AM
available_4am = grouped[grouped['hour'] == 4]
# Set the index to 'station_id' and 'date'
available_4am.set_index(['station_id', 'date'], inplace=True)
# For each entry, find the number of available bikes in this station at 4:00AM in the same day
tmp = rawDataAll[['station_id','date']].apply(tuple, axis=1).values

rawDataAll['available_bikes_4am'] = rawDataAll.apply(lambda x: available_4am.loc[(x['station_id'], x['date']), 'available_bikes'] if (x['station_id'], x['date']) in available_4am.index else np.nan, axis=1) 
# Count the number of nan
n_available_bikes_4am = rawDataAll['available_bikes_4am'].isna().sum()
print(f"--- Number of records with no available bikes at 4:00AM: {n_available_bikes_4am} out of {len(rawDataAll)} ({n_available_bikes_4am/len(rawDataAll)*100:.2f}%)")
# Remove the records with no available bikes at 4:00AM
rawDataAll = rawDataAll[~rawDataAll['available_bikes_4am'].isna()]

# Generate the normalized occupation rate: Each day, the occupation rate is the number of available bikes at the current hour minus the number of available bikes at 4:00AM, divided by the capacity of the station.
rawDataAll['occupation']= (rawDataAll['available_bikes']-rawDataAll['available_bikes_4am']) / rawDataAll['capacity']
rawDataAll['occupation'] = rawDataAll['occupation'].round(3)
grouped = rawDataAll.groupby(['station_id', 'date']).agg({'occupation':lambda x: list(x),'zone_id': lambda x: x.iloc[0],'tmin': lambda x: x.iloc[0],'tmax': lambda x: x.iloc[0],'prcp': lambda x: x.iloc[0],'wspd': lambda x: x.iloc[0],'weekday': lambda x: x.iloc[0],'holiday': lambda x: x.iloc[0]}).reset_index()

# Determine the size of the list in each row
grouped['n_occupations'] = grouped['occupation'].apply(lambda x: len(x))
# Check which rows have less than 24 occupations
grouped = grouped[grouped['n_occupations'] == 24]
# Remove the 'date' and 'n_occupations' columns
grouped = grouped.drop(columns=['n_occupations','date'])

print(grouped.sample(100))