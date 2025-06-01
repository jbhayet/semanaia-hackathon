import os
import pandas as pd  # type: ignore
import holidays  # type: ignore
import geopandas as gpd  # type: ignore
import numpy as np

# Read data/lyon_data01.csv
lyon_data_file01 = 'data/lyon_data01.csv'
if not os.path.exists(lyon_data_file01):
    print(f"xxx File {lyon_data_file01} does not exist.")
    exit(1)
# Read the file 
rawData01 = pd.read_csv(lyon_data_file01)
# Read data/lyon_data02.csv
lyon_data_file02 = 'data/lyon_data02.csv'
if not os.path.exists(lyon_data_file02):
    print(f"xxx File {lyon_data_file02} does not exist.")
    exit(1)
# Read the file
rawData02 = pd.read_csv(lyon_data_file02)
# Concatenate the two dataframes
rawDataAll = pd.concat([rawData01, rawData02], ignore_index=True)
# Save into data/lyon_data.csv
lyon_data_file = 'data/lyon_data.csv'
rawDataAll.to_csv(lyon_data_file, index=False)