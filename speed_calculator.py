import pandas as pd
from datetime import datetime

df = pd.read_csv('datasets/shaul_hamelech_routes_2019-03-17_2019-03-23.csv')
df['time_recorded_datetime'] = df.apply(lambda row: row['timestamp'].split('T')[0] + " "+ row["time_recorded"],axis=1)
df['time_recorded_datetime'] = pd.to_datetime(df['time_recorded_datetime'])
df.to_csv('datasets/shaul_hamelech_routes_2019-03-17_2019-03-23_update.csv')