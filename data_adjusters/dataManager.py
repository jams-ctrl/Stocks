# with one command, designed to run once per day to update .csv files of each company with new stock prices
from dataModifier import modify_data
from stockDownloader import download_data
import os
import sys
import pandas as pd
from datetime import datetime, timezone, timedelta
# go up one parent folder
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
# since went up one parent folder all function calls are made from the invisible "parent-folder" - must change in prediction.py to use the right filepath
from company_name_manager import get_top_50
# go down 1 parent folder
sys.path.remove(parent_dir)

# get date of last upload
df = pd.read_csv('dates.csv', header=None)
past_date = df[0].tolist()[1]
# get present day 
present = datetime.now().strftime('%Y-%m-%d') 

ticker = "ADBE"
# for ticker in tickers:
# download all the stocks past date of last upload
dataFrame = download_data(past_date,present, ticker)
# append new data to csv file
script_dir = os.path.dirname(os.path.abspath(__file__))
# CHANGE csv path if path to csv files changes
csv_path = os.path.join(script_dir, "..", "stock_data", f"{ticker}_5yr_data.csv")
with open(csv_path, "rb+") as f:
    f.seek(0, 2)  # go to end of file
    if f.tell() > 0:
        f.seek(-1, 2)
        if f.read(1) != b"\n":
            f.write(b"\n")
# CHANGE IF ADDING NEW COMPANIES
dataFrame.to_csv(csv_path, mode='a', index=False, header=None)

# modifiy all the stocks for said company and append features 
modified_data_frame = modify_data(csv_path)
# drop all placeholder dates from before and append full csv 
# modified_data_frame = modified_data_frame[modified_data_frame["date"] <= past_date]
# replaces entire csv file with new one
modified_data_frame.to_csv(csv_path, mode='w', index=False, float_format="%.4f")

    