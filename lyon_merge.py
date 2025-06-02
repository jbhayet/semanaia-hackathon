import os
import pandas as pd  # type: ignore

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
# Read data/lyon_data03.csv
lyon_data_file03 = 'data/lyon_data03.csv'
if not os.path.exists(lyon_data_file03):
    print(f"xxx File {lyon_data_file03} does not exist.")
    exit(1)
# Read the file
rawData03 = pd.read_csv(lyon_data_file03)
# Read data/lyon_data04.csv
lyon_data_file04 = 'data/lyon_data04.csv'
if not os.path.exists(lyon_data_file04):
    print(f"xxx File {lyon_data_file04} does not exist.")
    exit(1)
# Read the file
rawData04 = pd.read_csv(lyon_data_file04)

# Concatenate the two dataframes
rawDataAll = pd.concat([rawData01, rawData02, rawData03, rawData04], ignore_index=True)
# Save into data/lyon_data.csv
lyon_data_file = 'data/lyon_data.csv'
rawDataAll.to_csv(lyon_data_file, index=False)