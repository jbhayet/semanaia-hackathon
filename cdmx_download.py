# Description: This script downloads the Ecobici dataset from the specified URL and saves it to a local file.
import pandas as pd # type: ignore
import sys
import requests
import io
from datetime import datetime
import holidays # type: ignore
from meteostat import Point, Daily  # type: ignore
import numpy as np

def download_data_cdmx(url):
    """Download data from the specified URL and return it as a pandas DataFrame."""
    print(f"--- Downloading data from {url}")    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"xxx Error: Unable to download data, status code {response.status_code}")
        sys.exit(1)
    rawData = pd.read_csv(io.StringIO(response.text))
    if 'Genero_usuario' in rawData.columns:
        rawData = rawData.drop(columns=['Genero_usuario'])  # Remove the index column if it exists
    if 'Genero_Usuario' in rawData.columns:
        rawData = rawData.drop(columns=['Genero_Usuario'])  # Remove the index column if it exists
    if 'Edad_usuario' in rawData.columns:
        rawData = rawData.drop(columns=['Edad_usuario'])  # Remove the index column if it exists
    if 'Edad_Usuario' in rawData.columns:
        rawData = rawData.drop(columns=['Edad_Usuario'])  # Remove the index column if it exists
    if 'Bici' in rawData.columns:
        rawData = rawData.drop(columns=['Bici'])  # Remove the index column if it exists

    # Some cleaning: names of the stations. For some of them, the name is repeated twice, so we will keep only the first one
    rawData.replace('445-446', '445', inplace=True)
    rawData.replace('390-391', '390', inplace=True)
    rawData.replace('107-108', '107', inplace=True)
    rawData.replace('158-159', '158', inplace=True)
    rawData.replace('192-193', '192', inplace=True)
    rawData.replace('264-275', '264', inplace=True)
    rawData.replace('273-274', '273', inplace=True)
    rawData.replace('271-272', '271', inplace=True)
    rawData.replace('268-269', '268', inplace=True)

    # More cleaning: rename columns to have a consistent format
    if 'Hora_retiro' in rawData.columns:
        rawData.rename(columns={'Hora_retiro': 'Hora_Retiro'}, inplace=True)
    if 'Hora_arribo' in rawData.columns:
        rawData.rename(columns={'Hora_arribo': 'Hora_Arribo'}, inplace=True)
    if 'Hora_arribo' in rawData.columns:
        rawData.rename(columns={'Hora_arribo': 'Hora_Arribo'}, inplace=True)
    if 'CE_arribo' in rawData.columns:
        rawData.rename(columns={'CE_arribo': 'Ciclo_Estacion_Arribo'}, inplace=True)
    if 'Ciclo_EstacionArribo' in rawData.columns:
        rawData.rename(columns={'Ciclo_EstacionArribo': 'Ciclo_Estacion_Arribo'}, inplace=True)
    if 'CE_retiro' in rawData.columns:
        rawData.rename(columns={'CE_retiro': 'Ciclo_Estacion_Retiro'}, inplace=True)
    if 'Fecha_retiro' in rawData.columns:
        rawData.rename(columns={'Fecha_retiro': 'Fecha_Retiro'}, inplace=True)
    if 'Fecha_arribo' in rawData.columns:
        rawData.rename(columns={'Fecha_arribo': 'Fecha_Arribo'}, inplace=True)
    if 'Fecha Arribo' in rawData.columns:
        rawData.rename(columns={'Fecha Arribo': 'Fecha_Arribo'}, inplace=True)
    # Check the date format 
    try:
        # If we can parse the dates with the format '%d/%m/%Y', we will use it
        rawData['Fecha_Retiro'] = pd.to_datetime(rawData['Fecha_Retiro'], format='%d/%m/%Y', errors='raise')
        rawData['Fecha_Arribo'] = pd.to_datetime(rawData['Fecha_Arribo'], format='%d/%m/%Y', errors='raise')
    except ValueError as e:
        try:
            # Otherwise, we will try to parse the dates with the format '%d/%m/%y'
            rawData['Fecha_Retiro'] = rawData['Fecha_Retiro'].map(lambda x: str(x).replace("/2022", "/22"))
            rawData['Fecha_Arribo'] = rawData['Fecha_Arribo'].map(lambda x: str(x).replace("/2022", "/22"))
            rawData['Fecha_Retiro'] = rawData['Fecha_Retiro'].map(lambda x: str(x).replace("/2023", "/23"))
            rawData['Fecha_Arribo'] = rawData['Fecha_Arribo'].map(lambda x: str(x).replace("/2023", "/23"))
            rawData['Fecha_Retiro'] = pd.to_datetime(rawData['Fecha_Retiro'], format='%d/%m/%y', errors='raise')
            rawData['Fecha_Arribo'] = pd.to_datetime(rawData['Fecha_Arribo'], format='%d/%m/%y', errors='raise')
        except ValueError as e:
            print(f"xxx Error: {e}")
            # If the date format is not correct, we will exit the program
            sys.exit(1)

    # Ensure that the columns 'Ciclo_Estacion_Retiro' and 'Ciclo_Estacion_Arribo' are numeric
    rawData['Ciclo_Estacion_Retiro'] = pd.to_numeric(rawData['Ciclo_Estacion_Retiro'], errors='coerce',downcast='integer')
    rawData['Ciclo_Estacion_Arribo'] = pd.to_numeric(rawData['Ciclo_Estacion_Arribo'], errors='coerce',downcast='integer')
    rawData.dropna(subset=['Ciclo_Estacion_Retiro', 'Ciclo_Estacion_Arribo'], inplace=True)
    rawData['Ciclo_Estacion_Retiro'] = pd.to_numeric(rawData['Ciclo_Estacion_Retiro'], errors='coerce',downcast='integer')
    rawData['Ciclo_Estacion_Arribo'] = pd.to_numeric(rawData['Ciclo_Estacion_Arribo'], errors='coerce',downcast='integer')
    return rawData

# This is the main DataFrame that will hold all the data
rawDataAll = pd.DataFrame()

# Set to true to download the data, or false to read from a local file
download = False

if download:
    urls = [\
    'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-01.csv',\
    'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-02.csv',\
    'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-03.csv',\
    'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-04.csv',\
    'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-05.csv',\
    'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-06.csv',\
    'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-07.csv',\
    'https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/10/2022-08.csv',\
    'https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/08/202209.csv'\
    ]
    # URL to download the Ecobici dataset
    for url in urls:
        rawData = download_data_cdmx(url)
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,rawData], axis=0)

if download:
    # URL to download the Ecobici dataset
    for txt in ['10','11','12']:
        # Download the dataset for month i+1
        url = "https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/10/ecobici_2022_{}.csv".format(txt)
        rawData = download_data_cdmx(url)
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,rawData], axis=0)

if download:
    # URL to download the Ecobici dataset
    for txt in ['01','02','03','04','05','06','07','08','09']:
        # Download the dataset for month i+1
        url = "https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/10/ecobici_2023_{}.csv".format(txt)
        rawData = download_data_cdmx(url)
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,rawData], axis=0)

if download:
    urls = ['https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/11/datosabiertos_2023_octubre.csv','https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/12/datosabiertos_2023_noviembre.csv','https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/01/datos_abiertos_2023_diciembre.csv']
    # URL to download the Ecobici dataset
    for url in urls:
        rawData = download_data_cdmx(url)
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,rawData], axis=0)

if download:  # Set to True to download the data for 2024
    urls = [\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/02/ecobici_2024_enero.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/03/2024-02.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/04/datos_abiertos_2024_03-1-1.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/datos_abiertos_2024_04.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/06/2024-05-1.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/07/2024-06.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/08/datos_abiertos_2024_07.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/09/2024-08.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/10/2024-09.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/11/2024-10.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/12/2024-11.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2025/01/2024-12.csv'\
        ]
    # URL to download the Ecobici dataset
    for url in urls:
        rawData = download_data_cdmx(url)
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,rawData], axis=0)

# Save the data to a CSV file
if not rawDataAll.empty:
    print(f'--- Total number of records: {len(rawDataAll)}')    
    # Save the data to a CSV file
    rawDataAll.to_csv('data/cdmx_data_trips.csv', index=False)

# Read the saved data
dtype_dict = {
    'Ciclo_Estacion_Retiro': 'uint16',
    'Ciclo_Estacion_Arribo': 'uint16',
    'Fecha_Retiro': 'string',
    'Fecha Arribo': 'string',
    'Hora_Retiro': 'string',
    'Hora_Arribo': 'string'
}

# Read the CSV file into a DataFrame with the specified dtypes
df                 = pd.read_csv('data/cdmx_data_trips.csv',dtype=dtype_dict)
df['Fecha_Retiro'] = pd.to_datetime(df['Fecha_Retiro'], format='%Y-%m-%d').dt.date
df['Fecha_Arribo'] = pd.to_datetime(df['Fecha_Arribo'], format='%Y-%m-%d').dt.date

df['Hora_Retiro']  = pd.to_datetime(df['Hora_Retiro'], format='%H:%M:%S').dt.hour
df['Hora_Arribo']  = pd.to_datetime(df['Hora_Arribo'], format='%H:%M:%S').dt.hour

# Group by the station, the date and the hour of withdrawal
grouped_retiro = df.groupby(['Ciclo_Estacion_Retiro', 'Fecha_Retiro', 'Hora_Retiro'],observed=False).agg(
    trips_out=('Ciclo_Estacion_Retiro', 'size')
).reset_index().rename(columns={'Ciclo_Estacion_Retiro': 'station', 'Fecha_Retiro': 'date', 'Hora_Retiro': 'hour'})

# Group by the station, the date and the hour of arrival
grouped_arribo = df.groupby(['Ciclo_Estacion_Arribo', 'Fecha_Arribo', 'Hora_Arribo'],observed=False).agg(
    trips_in=('Ciclo_Estacion_Arribo', 'size')
).reset_index().rename(columns={'Ciclo_Estacion_Arribo': 'station', 'Fecha_Arribo': 'date', 'Hora_Arribo': 'hour'})
print("--- Grouped data for trips in:")
print(grouped_arribo.sample(20))
print("--- Grouped data for trips out:")
print(grouped_retiro.sample(20))
# Merge the two dataframes based on the columns station, date, hour
merged = grouped_arribo.merge(grouped_retiro, on=['station', 'date', 'hour'], how='outer').reset_index()
merged.drop(columns=['index'], inplace=True)

# Because there can be NaN, we will replace them by zero
merged.fillna(0, inplace=True)
merged['trips_in']  = merged['trips_in'].astype('int16')
merged['trips_out'] = merged['trips_out'].astype('int16')
merged['flow']      = merged['trips_in'] - merged['trips_out']
merged['weekday']   = merged['date'].apply(lambda x:  x.weekday())

# Min and max date
min_date = merged['date'].min()
max_date = merged['date'].max()
# Cycle through the dates
date_range = pd.date_range(start=min_date, end=max_date, freq='D')
# For each date in the date range, remember if it is a holiday  
holidays_dict = {}
for date in date_range:
    holidays_dict[date] = 1 if date in holidays.Mexico() else 0
merged['holiday'] = merged['date'].apply(lambda x: holidays_dict.get(pd.to_datetime(x), 0))
merged['holiday'] = merged['holiday'].astype('uint8')

# Get weather data for the period
print(f'--- Fetching weather data from {min_date} to {max_date}')
cdmx_stations = pd.read_json('data/cdmx_stations.json')
cdmx_stations = pd.DataFrame.from_records(cdmx_stations['data'].stations)
start         = datetime(merged['date'].min().year, merged['date'].min().month,merged['date'].min().day)
end           = datetime(merged['date'].max().year, merged['date'].max().month,merged['date'].max().day)
weather_data  = Daily(Point(cdmx_stations.iloc[0].lat, cdmx_stations.iloc[0].lon,2000), start, end)
weather_data  = weather_data.fetch()
tmp           = pd.to_datetime(merged['date'])
merged['tmin']= tmp.apply(lambda x: weather_data.loc[x,'tmin'] if x in weather_data.index else np.nan)   
merged['tmax']= tmp.apply(lambda x: weather_data.loc[x,'tmax'] if x in weather_data.index else np.nan)   
merged['prcp']= tmp.apply(lambda x: weather_data.loc[x,'prcp'] if x in weather_data.index else np.nan)   
merged['wspd']= tmp.apply(lambda x: weather_data.loc[x,'wspd'] if x in weather_data.index else np.nan)   
merged.rename(columns={'station':'station_id'}, inplace=True)
print('--- Columns in the merged DataFrame:')
print(merged.columns)
# Count how many holidays are in the dataset
n_holidays = merged['holiday'].sum()
print(f'--- Total number of holidays in the dataset: {n_holidays}')

# Print 100 random records
print(f'--- Total number of records: {len(merged)}')
print('--- Sample of 100 random records:')
print(merged.sample(100))
print('--- First 10 records for station 85:')
print(merged[merged['station_id'] == 85].head(10))
# Save the merged data to a CSV file
merged.to_csv('data/cdmx_data_flow.csv',index=False)
