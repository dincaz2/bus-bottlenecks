import pandas as pd
import geopy.distance
import numpy as np
from datetime import datetime, timedelta

# df = pd.read_csv('datasets/shaul_hamelech_routes_2019-03-17_2019-03-23.csv')
# df['time_recorded_datetime'] = pd.to_datetime(df['time_recorded_datetime'])

df_route = pd.read_csv('datasets/Trip 36893372_060319 route 2293 220319 060000.csv', encoding='latin-1').sort_values('SHAPE_PT_SEQUENCE  ')
route_dots_list = [(row['SHAPE_PT_LAT  '], row['SHAPE_PT_LON  ']) for index, row in df_route.iterrows()]
route_dots_dic = {row : index for index, row in enumerate(route_dots_list)}
print(route_dots_list)

def subroute_distance(route_dots_dic, route_dots_list, origin, dest):
    route = route_dots_list[route_dots_dic[origin] : route_dots_dic[dest] + 1]
    route_length = 0
    for i in range(len(route)-1):
        route_length += abs(geopy.distance.geodesic(route[i], route[i+1]).m)
    return route_length

def route_distance(route):
    route_length = 0
    for i in range(len(route)-1):
        route_length += abs(geopy.distance.geodesic(route[i], route[i+1]).m)
    return route_length

def find_nearest_dot(route_dots_list, dot, epsilon=30):
    diffs = [abs(geopy.distance.geodesic(dot, dot2).m) for dot2 in route_dots_list]
    index = np.argmin(diffs)
    if diffs[index] < epsilon:
        return route_dots_list[index]

def find_nearest_dot(route_dots_list, lat, lon, epsilon=30):
    diffs = [abs(geopy.distance.geodesic((lat,lon), dot2).m) for dot2 in route_dots_list]
    index = np.argmin(diffs)
    if diffs[index] < epsilon:
        return route_dots_list[index]

def calc_speed_in_interval(df, segments_df):
    trips = df.groupby('trip_id_to_date', 'segment')
    for _, g in trips:
        g = g['time_recorded_datetime'].sort_values()
        time = g[-1] - g[0]
        segment = segments_df[segments_df.name == ''] #TODO
        dist = route_distance(segment)
        return dist / time



def find_data_time(minutes, date, df, segments):
    df = df[pd.to_datetime(df['time_recorded_dataTime']).dt.date == date]
    curDate = df["time_recorded_datetime"].min()
    nextDate = curDate + timedelta(minutes = minutes)
    end_date =  df["time_recorded_datetime"].max()
    dic_times  = pd.DataFrame(columns=('start_interval', 'end_interval', 'uniqueBus'))
    while nextDate < end_date:
        current_data = df[df['time_recorded_datetime'].between(curDate,nextDate)]
        calc_speed_in_interval(current_data, segments)
        curDate = nextDate
        nextDate = curDate + timedelta(minutes = minutes)
    current_data = df[df['time_recorded_datetime'].between(curDate, end_date)]
    calc_speed_in_interval(current_data, segments)

origin = route_dots_list[0]
dest = route_dots_list[-1]
print(route_distance(route_dots_list))

dot = (32.098752, 34.7794)
print(find_nearest_dot(route_dots_list, dot))