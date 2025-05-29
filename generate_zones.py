import pandas as pd
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import sys



##################################################################################################
# Read the Cdmx stations json
cdmx_stations = pd.read_json('data/cdmx_stations.json')
cdmx_stations = pd.DataFrame.from_records(cdmx_stations['data'].stations)
cdmx_stations = cdmx_stations.drop(columns=['name','rental_methods','short_name','eightd_has_key_dispenser','is_charging','has_kiosk','electric_bike_surcharge_waiver','external_id'])

# Create a DataFrame with a geometry containing the Points
geo_cdmx_stations = gpd.GeoDataFrame(
    cdmx_stations, crs="EPSG:4326", geometry=gpd.points_from_xy(cdmx_stations["lon"], cdmx_stations["lat"])
)
geo_cdmx_stations = geo_cdmx_stations.to_crs(epsg=3857)

# Read the GeoJSON file for Mexico City colonias
cdmx_colonias = gpd.read_file('data/cdmx_colonias.geojson')
cdmx_colonias = cdmx_colonias.to_crs(epsg=3857)
cdmx_colonias['n_bike_stations'] = cdmx_colonias.apply(lambda x: geo_cdmx_stations.within(x.geometry).sum(), axis=1)
cdmx_colonias = cdmx_colonias[cdmx_colonias['n_bike_stations']>0]
to_merges = [[762,1802,1225],[38,911,39,910,757],[478,1605,1800,1458,1799],[759,1527,1187],[1006,1609,1417,1464],[302,579,1804,488,1107,231],[89,637,481,1710,1222],[1224,1321,1322,1323],[47,1227,236],[477,1320,1530,1047,1459,1318],[244,1256,1011,823,1488,1490,1764],[1,241,1067,820,1015,3,119],[87,342,1319,1529,813],[758,1457,1707,1100],[343,432,1528,1801,1662],[40,1045,1412,1373],[344,1219,296,1661],[76,1028,139,731,942],[46,95,352,349],[580,581,1712],[347,1669,1415],[90,484,1105],[761,1416],[230,298,815,482],[477,1663],[88,1666,575],[1003,1607,1052,1106],[45,486,1050,913,1803,1670],[161,345,297,573],[402,1384,1750,1751,875,1346,1495],[578,1193,1463],[684,1220,1191,1226]]
for to_merge in to_merges:
    for i in range(1,len(to_merge)):  
        # Merge two colonias
        cdmx_colonias.loc[to_merge[0],'geometry'] = cdmx_colonias.loc[to_merge[0],'geometry'].union(cdmx_colonias.loc[to_merge[i],'geometry'])
        # Drop the second colonia
        cdmx_colonias = cdmx_colonias.drop(index=to_merge[i])
cdmx_colonias['n_bike_stations'] = cdmx_colonias.apply(lambda x: geo_cdmx_stations.within(x.geometry).sum(), axis=1)
cdmx_colonias.to_csv('data/cdmx_zones.csv', index=False)

##################################################################################################
# Read the Lyon stations CSV
lyon_stations = pd.read_csv('data/lyon_stations.csv', index_col=0)
lyon_stations = lyon_stations.drop(columns=['adresse1','adresse2','code_insee','numdansarrondissement','stationbonus','achevement','validite','pole']) 
lyon_stations['commune'] = lyon_stations['commune'].astype('category')
# Create a DataFrame with a geometry containing the Points
geo_lyon_stations = gpd.GeoDataFrame(
    lyon_stations, crs="EPSG:4326", geometry=gpd.points_from_xy(lyon_stations["lon"], lyon_stations["lat"])
)
geo_lyon_stations = geo_lyon_stations.to_crs(epsg=3857)
# Read the GeoJSON file for Lyon communes
lyon_communes = gpd.read_file('data/lyon_communes.geojson')
lyon_communes = lyon_communes.to_crs(epsg=3857)
lyon_communes['n_bike_stations'] = lyon_communes.apply(lambda x: geo_lyon_stations.within(x.geometry).sum(), axis=1)
lyon_communes = lyon_communes[lyon_communes['n_bike_stations']>0]
to_merges = [[84,273],[152,275],[176,201,198],[62,259],[49,252,185,220],[15,278],[37,158,153]]
for to_merge in to_merges:
    for i in range(1,len(to_merge)):  
        # Merge two colonias
        lyon_communes.loc[to_merge[0],'geometry'] = lyon_communes.loc[to_merge[0],'geometry'].union(lyon_communes.loc[to_merge[i],'geometry'])
        # Drop the second colonia
        lyon_communes = lyon_communes.drop(index=to_merge[i])
# Villeurbanne is very large, so we will split it into two parts
# Determine the average point of the geometry
centroid = lyon_communes.loc[208,'geometry'].centroid
# Create a GeoDataframe with the sub-polygon above the line
from shapely.geometry import Polygon
polygon = lyon_communes.loc[208, 'geometry']
# Split the polygon by the infinite horizontal line passing through centroid
far = 1000000
up = polygon.intersection(Polygon([
        (polygon.bounds[0]-far, centroid.y),
        (centroid.x+far, centroid.y),
        (centroid.x+far, polygon.bounds[3]+far),
        (polygon.bounds[0]-far, polygon.bounds[3]+far)
    ]))
down = polygon.intersection(Polygon([
        (polygon.bounds[0]-far, centroid.y),
        (centroid.x+far, centroid.y),
        (centroid.x+far, polygon.bounds[1]-far),
        (polygon.bounds[0]-far, polygon.bounds[1]-far)
    ]))
# Replace the original geometry with the left part, and add the right part as a new row
lyon_communes.loc[208, 'geometry'] = up
# Change the commune name to Villeurbanne nord
lyon_communes.loc[209] = lyon_communes.loc[208]
lyon_communes.loc[209, 'geometry'] = down
lyon_communes.loc[208, 'nom'] = 'Villeurbanne nord'
lyon_communes.loc[209, 'nom'] = 'Villeurbanne sud'
lyon_communes['n_bike_stations'] = lyon_communes.apply(lambda x: geo_lyon_stations.within(x.geometry).sum(), axis=1)
# Save the data to CSV files
lyon_communes.to_csv('data/lyon_zones.csv', index=False)


##################################################################################################
# Plotting the data
# Create a figure with two subplots
fig, ax = plt.subplots(1,2,figsize=(8, 6))

# Plotting the Lyon data
ax[0].set_title('Lyon Bike Stations')
# Plot the stations in Lyon
geo_lyon_stations.plot("nbbornettes", cmap="OrRd", ax=ax[0])
# Plot the Lyon communes
lyon_communes.boundary.plot(ax=ax[0], color='black')
# Plot the communes ids too
lyon_communes.index.to_series().apply(lambda x: ax[0].text(lyon_communes.loc[x,'geometry'].centroid.x, lyon_communes.loc[x,'geometry'].centroid.y, x, fontsize=8, ha='center', va='center', color='black'))
ax[0].set_axis_off()
ax[0].add_artist(ScaleBar(1))
ctx.add_basemap(ax[0])

# Plotting the Mexico City data
ax[1].set_title('Mexico City Bike Stations')
# Plot the colonias in Mexico City
cdmx_colonias.boundary.plot(ax=ax[1],color='black')
geo_cdmx_stations.plot("capacity", cmap="OrRd", ax=ax[1])
# Plot the colonias ids too
cdmx_colonias.index.to_series().apply(lambda x: ax[1].text(cdmx_colonias.loc[x,'geometry'].centroid.x, cdmx_colonias.loc[x,'geometry'].centroid.y, x, fontsize=8, ha='center', va='center', color='black'))
ax[1].set_axis_off()
ax[1].add_artist(ScaleBar(1))
ctx.add_basemap(ax[1])
plt.show()



