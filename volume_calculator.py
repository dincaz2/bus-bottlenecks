
import pandas as pd
import time, datetime
from datetime import datetime, timedelta


def find_data_time(minutes,date,df):
    df = df[pd.to_datetime(df['time_recorded_dataTime']).dt.date == date]
    curDate = df["time_recorded_dataTime"].min()
    nextDate = curDate + timedelta(minutes = minutes)
    end_date =  df["time_recorded_dataTime"].max()
    dic_times  = pd.DataFrame(columns=('start_interval', 'end_interval', 'uniqueBus'))
    while nextDate < end_date:
        current_data = df[df['time_recorded_dataTime'].between(curDate,nextDate)]
        curDate = nextDate
        nextDate = curDate + timedelta(minutes = minutes)

    current_data = df[df['time_recorded_dataTime'].between(curDate, end_date)]



df = pd.read_csv(r'datasets\shaul_hamelech_routes_2019-03-17_2019-03-23.csv', encoding = "utf-8" )
df['time_recorded_dataTime'] = df.apply(lambda row: row['timestamp'].split('T')[0] + " "+ row["time_recorded"],axis=1)
df['time_recorded_dataTime'] = pd.to_datetime(df['time_recorded_dataTime'])
print(df)
uq_dates = df.time_recorded_dataTime.dt.date.unique()

for date in uq_dates:
    find_data_time(15,date,df)




