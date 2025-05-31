# Open the cdmx flow file and print the first 10 lines
import sys
import os
import pandas as pd # type: ignore
import holidays # type: ignore
import geopandas as gpd # type: ignore

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
#.map(lambda x: geo_lyon_stations[x].nom if x in geo_lyon_stations.index else 'Unknown')

# 
tmp = rawDataAll.groupby(['station_id', 'date', 'hour']).agg({'available_bikes': 'mean', 'stands': 'mean', 'capacity': 'mean'})
print(tmp.head(20))
print(len(tmp))
print(len(lyon_zones_geo))