# Description: This script downloads the Ecobici dataset from the specified URL and saves it to a local file.
import pandas as pd # type: ignore
import sys
import requests
import io
from datetime import datetime
import holidays # type: ignore

rawDataAll = pd.DataFrame()

def download_data(url):
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
        rawData.rename(columns={'Fecha_arribo': 'Fecha Arribo'}, inplace=True)
    rawData['Ciclo_Estacion_Retiro'] = rawData['Ciclo_Estacion_Retiro'].astype('uint16',errors='ignore')
    rawData['Ciclo_Estacion_Arribo']  = rawData['Ciclo_Estacion_Arribo'].astype('uint16',errors='ignore')
    return rawData

# Set to true to download the data, or false to read from a local file
download = True

if download:
    urls = ['https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-01.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-02.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-03.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-04.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-05.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-06.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/05/2022-07.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/10/2022-08.csv',\
        'https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/08/202209.csv']
    # URL to download the Ecobici dataset
    for url in urls:
        rawData = download_data(url)
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,rawData], axis=0)

if download:
    # URL to download the Ecobici dataset
    for txt in ['10','11','12']:
        # Download the dataset for month i+1
        url = "https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/10/ecobici_2022_{}.csv".format(txt)
        rawData = download_data(url)
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,rawData], axis=0)

if download:
    # URL to download the Ecobici dataset
    for txt in ['01','02','03','04','05','06','07','08','09']:
        # Download the dataset for month i+1
        url = "https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/10/ecobici_2023_{}.csv".format(txt)
        rawData = download_data(url)
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,rawData], axis=0)

if download:
    urls = ['https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/11/datosabiertos_2023_octubre.csv','https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/12/datosabiertos_2023_noviembre.csv','https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/01/datos_abiertos_2023_diciembre.csv']
    # URL to download the Ecobici dataset
    for url in urls:
        rawData = download_data(url)
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
df                 = pd.read_csv('data/cdmx_data_trips.csv',dtype=dtype_dict)
df['Fecha_Retiro'] = pd.to_datetime(df['Fecha_Retiro'], format='%d/%m/%Y').dt.date
df['Fecha Arribo'] = pd.to_datetime(df['Fecha Arribo'], format='%d/%m/%Y').dt.date
df['Hora_Retiro']  = pd.to_datetime(df['Hora_Retiro'], format='%H:%M:%S').dt.hour
df['Hora_Arribo']  = pd.to_datetime(df['Hora_Arribo'], format='%H:%M:%S').dt.hour

# Group by the station, the date and the hour of withdrawal
grouped_retiro = df.groupby(['Ciclo_Estacion_Retiro', 'Fecha_Retiro', 'Hora_Retiro'],observed=False).agg(
    n_trips_out=('Ciclo_Estacion_Retiro', 'size')
).reset_index().rename(columns={'Ciclo_Estacion_Retiro': 'estacion', 'Fecha_Retiro': 'date', 'Hora_Retiro': 'hour'})

# Group by the station, the date and the hour of arrival
grouped_arribo = df.groupby(['Ciclo_Estacion_Arribo', 'Fecha Arribo', 'Hora_Arribo'],observed=False).agg(
    n_trips_in=('Ciclo_Estacion_Arribo', 'size')
).reset_index().rename(columns={'Ciclo_Estacion_Arribo': 'estacion', 'Fecha Arribo': 'date', 'Hora_Arribo': 'hour'})

print(grouped_arribo.head())
print(grouped_retiro.head())
print(grouped_arribo['estacion'].unique())
sys.exit(0)

# Merge the two dataframes based on the columns estacion, date, hour
merged = grouped_arribo.merge(grouped_retiro, on=['estacion', 'date', 'hour'], how='outer').reset_index()
merged.drop(columns=['index'], inplace=True)


# Because there can be NaN, we will replace them by zero
merged.fillna(0, inplace=True)
merged['n_trips_in']  = merged['n_trips_in'].astype('int16')
merged['n_trips_out'] = merged['n_trips_out'].astype('int16')
merged['flow']        = merged['n_trips_in'] - merged['n_trips_out']
merged['weekday']     = merged['date'].apply(lambda x:  x.weekday())

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

# Print 100 random records
print(merged.sample(100))
merged.to_csv('data/cdmx_data_flow.csv')
