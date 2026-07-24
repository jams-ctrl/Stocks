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
df_date = pd.read_csv('dates.csv', header=None)
past_date = df_date[0].tolist()[len(df_date)-1]
print(past_date)
# get present day 
present = datetime.now().strftime('%Y-%m-%d') 
present_df = pd.DataFrame([[present]])
# comment date line out for debugging
#present_df.to_csv('dates.csv', mode='a', index=False)

ticker = "AAPL"
# for ticker in tickers:
# download all the stocks past date of last upload
df_base = download_data(past_date,present, ticker)
# append new data to csv file
script_dir = os.path.dirname(os.path.abspath(__file__))
# CHANGE csv path if path to csv files changes
csv_path = os.path.join(script_dir, "..", "stock_data", f"{ticker}_5yr_data.csv")

# takes the last 50 rows of the current csv and adds it to a dataframe - ERROR: IF CSV IS EMPTY WILL PRODUCE BUG
df_cut = pd.read_csv(csv_path).tail(50).reset_index(drop=True)
# adds "new" rows to dataframe
df_cut = pd.concat([df_cut,df_base], ignore_index=True)
# modifiy all the stocks for said company and append features 
modified_data_frame = modify_data(df_cut)
# drop last 50 dataFrame - keep only appended df_base rows - +1 because ghost date
modified_data_frame = modified_data_frame.iloc[-len(df_base)+1:].reset_index(drop=True)
print(modified_data_frame)
# guarentee the append starts on a new line
with open(csv_path, "rb+") as f:
    f.seek(0, 2)  # go to end of file
    if f.tell() > 0:
        f.seek(-1, 2)
        if f.read(1) != b"\n":
            f.write(b"\n")
# appends modified rows to csv
if os.path.getsize(csv_path) == 0:
    # if completely new company with blank csv file
    modified_data_frame.to_csv(csv_path, mode='a', index=False, float_format="%.4f")
#else:
    # if data already in csv
    # comment append line out for debugging
   #modified_data_frame.to_csv(csv_path, mode='a', index=False, header=None)

    