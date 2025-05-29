# Open the cdmx flow file and print the first 10 lines
import sys
import os
import pandas as pd


cdmx_flow_file = 'data/cdmx_data_flow.csv'
if not os.path.exists(cdmx_flow_file):
    print(f"File {cdmx_flow_file} does not exist.")
    sys.exit(1)
# Read the file and print the first 10 lines
rawDataAll = pd.read_csv(cdmx_flow_file)
print(f"--- Total number of records: {len(rawDataAll)}")
