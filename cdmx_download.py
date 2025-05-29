# Description: This script downloads the Ecobici dataset from the specified URL and saves it to a local file.
import pandas as pd # type: ignore
import sys
import requests
import io
from datetime import datetime

rawDataAll = pd.DataFrame()

def download_data(url):
    """Download data from the specified URL and return it as a pandas DataFrame."""
    response = requests.get(url)
    if response.status_code != 200:
        print(f"xxx Error: Unable to download data, status code {response.status_code}")
        sys.exit(1)
    return pd.read_csv(io.StringIO(response.text))

# Set to true to download the data, or false to read from a local file
download = False

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
        print(f"--- Downloading data from {url}")
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,download_data(url)], axis=0)

    # URL to download the Ecobici dataset
    for txt in ['10','11','12']:
        # Download the dataset for month i+1
        url = "https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/10/ecobici_2022_{}.csv".format(txt)
        print(f"--- Downloading data for month {txt} from {url}")
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,download_data(url)], axis=0)

    # URL to download the Ecobici dataset
    for txt in ['01','02','03','04','05','06','07','08','09']:
        # Download the dataset for month i+1
        url = "https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/10/ecobici_2023_{}.csv".format(txt)
        print(f"--- Downloading data for month {txt} from {url}")
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,download_data(url)], axis=0)

    urls = ['https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/11/datosabiertos_2023_octubre.csv','https://ecobici.cdmx.gob.mx/wp-content/uploads/2023/12/datosabiertos_2023_noviembre.csv','https://ecobici.cdmx.gob.mx/wp-content/uploads/2024/01/datos_abiertos_2023_diciembre.csv']
    # URL to download the Ecobici dataset
    for url in urls:
        print(f"--- Downloading data from {url}")
        # Add the result of the request to the main DataFrame
        rawDataAll = pd.concat([rawDataAll,download_data(url)], axis=0)

# Save the data to a CSV file
if not rawDataAll.empty:
    print(f'--- Total number of records: {len(rawDataAll)}')    
    # Save the data to a CSV file
    rawDataAll.to_csv('data/cdmx_data_trips.csv', index=False)

# Read the saved data
df                 = pd.read_csv('data/cdmx_data_trips.csv')
df                 = df.drop(columns=['Genero_Usuario','Edad_Usuario','Bici'])
df['Fecha_Retiro'] = pd.to_datetime(df['Fecha_Retiro'], format='%d/%m/%Y').dt.date
df['Fecha Arribo'] = pd.to_datetime(df['Fecha Arribo'], format='%d/%m/%Y').dt.date
df['Hora_Retiro']  = pd.to_datetime(df['Hora_Retiro'], format='%H:%M:%S').dt.hour
df['Hora_Arribo']  = pd.to_datetime(df['Hora_Arribo'], format='%H:%M:%S').dt.hour
df['Ciclo_Estacion_Retiro'] = df['Ciclo_Estacion_Retiro'].astype('category')
df['Ciclo_EstacionArribo']  = df['Ciclo_EstacionArribo'].astype('category')


# Group by the station, the date and the hour of withdrawal
grouped_retiro = df.groupby(['Ciclo_Estacion_Retiro', 'Fecha_Retiro', 'Hora_Retiro'],observed=False).agg(
    n_trips_out=('Ciclo_Estacion_Retiro', 'size')
).reset_index().rename(columns={'Ciclo_Estacion_Retiro': 'estacion', 'Fecha_Retiro': 'date', 'Hora_Retiro': 'hour'})

# Group by the station, the date and the hour of arrival
grouped_arribo = df.groupby(['Ciclo_EstacionArribo', 'Fecha Arribo', 'Hora_Arribo'],observed=False).agg(
    n_trips_in=('Ciclo_EstacionArribo', 'size')
).reset_index().rename(columns={'Ciclo_EstacionArribo': 'estacion', 'Fecha Arribo': 'date', 'Hora_Arribo': 'hour'})



# Merge the two dataframes based on the columns estacion, date, hour
merged = grouped_arribo.merge(grouped_retiro, on=['estacion', 'date', 'hour'], how='outer').reset_index()
merged.drop(columns=['index'], inplace=True)
# Because there can be NaN, we will replace them by zero
merged.fillna(0, inplace=True)
merged['n_trips_in']  = merged['n_trips_in'].astype('int16')
merged['n_trips_out'] = merged['n_trips_out'].astype('int16')
merged['flow']        = merged['n_trips_in'] - merged['n_trips_out']
merged.to_csv('data/cdmx_data_flow.csv')

print(merged.head())
