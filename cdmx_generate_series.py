# Open the cdmx flow file and print the first 10 lines
import sys
import os
import pandas as pd # type: ignore
import holidays # type: ignore

cdmx_flow_file = 'data/cdmx_data_flow.csv'
if not os.path.exists(cdmx_flow_file):
    print(f"File {cdmx_flow_file} does not exist.")
    sys.exit(1)
# Read the file and print the first 10 lines
rawDataAll = pd.read_csv(cdmx_flow_file)
print(f"--- Total number of records: {len(rawDataAll)}")
print(rawDataAll.head(60))

# A date at 1st of january 2022
start_date = pd.to_datetime('2022-01-01')
# Test if the start date is a holiday
if start_date in holidays.Mexico():
    print(f"{start_date.date()} is a holiday in Mexico.")