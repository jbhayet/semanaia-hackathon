import requests
import json
import pandas as pd
import sys,io
import ast
import numpy as np
import matplotlib.pyplot as plt
from meteostat import Point, Daily
from datetime import datetime
import holidays

def string_to_dict(dict_string):
    # Convert to proper json format
    dicts = ast.literal_eval(ast.literal_eval(dict_string))
    return dicts

nrequests = 350
#nrequests = 2
# Number of features to download per request
record_features= 300000
# total: 116 408 137
record_offset  = 1
# Read the Lyon stations CSV
lyon_stations = pd.read_csv('lyon_stations.csv', index_col=0)
lyon_stations = lyon_stations.drop(columns=['adresse1','adresse2','code_insee','numdansarrondissement','nbbornettes','stationbonus','achevement','validite','pole']) 
lyon_stations['commune'] = lyon_stations['commune'].astype('category')


rawDataAll = pd.DataFrame()
for i in range(0,nrequests):
    # Start id of the first feature to download (to cover the whole dataset)
    start_id    =  record_offset +i*record_features
    access_url  = f'https://data.grandlyon.com/fr/datapusher/ws/timeseries/jcd_jcdecaux.historiquevelov/all.csv?maxfeatures={record_features}&start={start_id}&filename=stations-velo-v-de-la-metropole-de-lyon---disponibilites-temps-reel&ds=.&separator=,'
    print('--- Request: {} de {} at {}'.format(i+1, nrequests, access_url))
    # Download the data
    answer  = requests.get(access_url)
    # Check if the request was successful
    if answer.status_code != 200:
        print('Error: ',answer.status_code)
        break
    
    # Convert the response content to a pandas DataFrame
    # The data is in CSV format, so we can use pd.read_csv
    rawData = pd.read_csv(io.StringIO(answer.text), parse_dates=["horodate"])
    # Remove the columns that are not needed
    rawData = rawData.drop(columns=['main_stands', 'overflow_stands'])

    # In the column 'total_stands', convert the string representation of a dictionary to an actual dictionary
    # and extract the 'availabilities' and 'capacity' values
    stands = rawData['total_stands'].apply(string_to_dict)
    rawData['available_bikes'] = stands.apply(lambda x: x['availabilities']['bikes']).astype('uint16')
    rawData['stands']  = stands.apply(lambda x: x['availabilities']['stands']).astype('uint16')
    rawData['capacity']= stands.apply(lambda x: x['capacity']).astype('uint16')
    rawData['number']  = rawData.number.astype('uint16')
    rawData['status']  = rawData.status.astype('category')
    rawData            = rawData.drop(columns=['total_stands'])
    # Set time date as a datetime object
    rawData['horodate'] = pd.to_datetime(rawData['horodate'], format='%Y-%m-%d %H:%M:%S')
    rawData['date']    = rawData['horodate'].apply(lambda x: datetime(x.year,x.month,x.day))
    rawData['weekday'] = rawData['date'].dt.dayofweek
    rawData['year']    = rawData['date'].dt.year
    rawData['year']    = rawData['year'].astype('uint16')
    rawData['month']   = rawData['date'].dt.month
    rawData['month']   = rawData['month'].astype('uint8')
    rawData['day']     = rawData['date'].dt.day
    rawData['day']     = rawData['day'].astype('uint8')
    rawData['hour']    = rawData['horodate'].dt.hour
    rawData['hour']    = rawData['hour'].astype('uint8')
    rawData['minute']  = rawData['horodate'].dt.minute
    rawData['minute']  = rawData['minute'].astype('uint8')
    rawData['commune'] = rawData['number'].apply(lambda x:  lyon_stations.loc[x,'commune'] if x in lyon_stations.index else 'Unknown').astype('category')

    start              = datetime(rawData['date'].min().year, rawData['date'].min().month,rawData['date'].min().day)
    end                = datetime(rawData['date'].max().year, rawData['date'].max().month,rawData['date'].max().day)
    print(f'--- Data from {start} to {end}')
    # Get daily weather data in the covered period
    weather_data   = Daily(Point(lyon_stations.iloc[0].lat, lyon_stations.iloc[0].lon,100), start, end)
    weather_data   = weather_data.fetch()
    rawData['tmin']= rawData['date'].apply(lambda x: weather_data.loc[x,'tmin'] if x in weather_data.index else np.nan)   
    rawData['tmax']= rawData['date'].apply(lambda x: weather_data.loc[x,'tmax'] if x in weather_data.index else np.nan)   
    rawData['prcp']= rawData['date'].apply(lambda x: weather_data.loc[x,'prcp'] if x in weather_data.index else np.nan)   
    rawData['wspd']= rawData['date'].apply(lambda x: weather_data.loc[x,'wspd'] if x in weather_data.index else np.nan)   
    # Are there holidays in the dataset?
    rawData['holiday'] = rawData['horodate'].apply(lambda x: 1 if datetime(x.year,x.month,x.day) in holidays.FR() else 0)
    rawData['holiday'] = rawData['holiday'].astype('uint8')
    # Add the result of the request to the main DataFrame
    rawDataAll = pd.concat([rawDataAll,rawData], axis=0)

# Save the data to a CSV file
if not rawDataAll.empty:
    print(f'--- Total number of records: {len(rawDataAll)}')    
    # Remove the 'horodate' column as it is not needed anymore
    rawDataAll = rawDataAll.drop(columns=['horodate'])
    # Select only the status 'OPEN'
    rawDataAll = rawDataAll[rawDataAll['status'] == 'OPEN']
    # Remove the 'status' column as it is not needed anymore
    rawDataAll = rawDataAll.drop(columns=['status'])
    # Take the mean of available_bikes, stands, capacity, tmin, tmax, prcp, wspd for each hour
    rawDataAll = rawDataAll.groupby(['number','year', 'month', 'day', 'hour']).agg({'date': lambda x: x.iloc[0], 'available_bikes': 'mean', 'stands': 'mean', 'capacity': 'mean', 'commune': lambda x: x.iloc[0],'tmin': lambda x: x.iloc[0],'tmax': lambda x: x.iloc[0],'prcp': lambda x: x.iloc[0],'wspd': lambda x: x.iloc[0],'holiday': lambda x: x.iloc[0],'weekday': lambda x: x.iloc[0]}).round(1).reset_index()
    # Search for the weather data 
    rawDataAll.to_csv('lyon_data.csv', index=False) 


sys.exit(0)

# Load the CSV file into a DataFrame
dtype_dic= {'capacity':'uint16', 'available_bikes':'uint16', 'stands':'uint16', 'number':'uint16', 'sta'
'tus':'category', 'year':'uint16', 'month':'uint8', 'day':'uint8', 'hour':'uint8', 'minute':'uint8'}
df = pd.read_csv('lyon_data_small.csv', dtype=dtype_dic)

stations_ids = df['number'].unique()
n_stations   = len(stations_ids)
print(f'There are {n_stations} stations in the dataset.')
# Select one random station
import random
station_id = random.choice(stations_ids)
print(f'Selected station: {station_id}')
# Filter the DataFrame for the selected station
station_data = df[df['number'] == station_id]
print(station_data.head())
commune = station_data['commune'].iloc[0]
print(f'The station is located in {commune}.')
idx          = station_data[df['hour'] == 19].index
idx_id       = random.choice(idx)
station_data = station_data.loc[idx_id:idx_id+47]
print(station_data.head())
print(station_data.tail())


l = len(station_data['available_bikes'].values)
t = np.arange(19,19+l)
tt= np.arange(19,19+l)%24 
station_data.to_csv('test.csv', index=False) 

print('The data covers the following week days:{}'.format(station_data['weekday'].unique()))
print('The weather for this day is:')
print('Tmin: {:.1f} C, Tmax: {:.1f} C, Precipitation: {:.1f} mm, Wind Speed: {:.1f} m/s'.format(
    station_data['tmin'].iloc[0], station_data['tmax'].iloc[0], station_data['prcp'].iloc[0], station_data['wspd'].iloc[0]))
# Plot the data for the selected station
plt.figure(figsize=(12, 6))
plt.plot(t,station_data['available_bikes'].values, marker='o', label='Available Bikes')
plt.xticks(t[::2], tt[::2])
plt.xlabel('Hour of the Day')
plt.ylabel('Number of Available Bikes')
plt.title(f'Available Bikes at Station {station_id} ({commune}) Over 48 Hours')
plt.show()

