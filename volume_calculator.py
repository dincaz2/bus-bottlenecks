
import pandas as pd
import time, datetime
from datetime import datetime, timedelta
import sqlite3
import codecs
import geopy.distance
import numpy as np
from shapely.ops import nearest_points
import geopandas as gpd
from shapely.geometry import Point
from scipy.spatial import cKDTree
# unary union of the gpd2 geomtries
from speed_calculator import route_distance

def find_data_time(minutes,date,df, segments_df):
    df = df[pd.to_datetime(df['time_recorded_dateTime']).dt.date == date]
    curDate = df["time_recorded_dateTime"].min()
    nextDate = curDate + timedelta(minutes = minutes)
    end_date =  df["time_recorded_dateTime"].max()
    dic_times  = pd.DataFrame(columns=('start_interval', 'end_interval', 'uniqueBus'))
    entries = []
    while nextDate < end_date:
        current_data = df[df['time_recorded_dateTime'].between(curDate,nextDate)]
        entries += add_bus_counts(current_data, curDate, nextDate, segments_df)
        curDate = nextDate
        nextDate = curDate + timedelta(minutes = minutes)

    current_data = df[df['time_recorded_dateTime'].between(curDate, end_date)]
    entries += add_bus_counts(current_data, curDate, end_date, segments_df)
    return entries

def add_bus_counts(data, curDate, nextDate, segments_df):
    trips = data.groupby(['trip_id_to_date', 'segment'])
    speeds = {}
    for (_,segment_name), g in trips:
        times = list(g['time_recorded_dateTime'].sort_values())
        if len(g) == 1:
            continue
        time = (times[-1] - times[0]).seconds
        if time == 0:
            continue
        segment = segments_df[segments_df.name == segment_name]
        dist = list(segment['length'])[0]
        val = speeds.get(segment_name, list())
        val.append((dist / time) * 3.6)
        speeds[segment_name] = val

    data = data[['trip_id_to_date', 'segment']].drop_duplicates()
    segments = data.groupby('segment')
    day = curDate.day
    from_hour = str(curDate.time())
    to_hour = str(nextDate.time())
    ans = []
    for segment, group in segments:
        avg_speed = (sum(speeds[segment]) / len(speeds[segment])) if segment in speeds else 0
        ans.append([segment, day, from_hour, to_hour, avg_speed, segments.get_group(segment)['trip_id_to_date'].count()])
    return ans
    # groupby segment
    # redundent duplicates by trip id or busid
    # count
    # write to csv


def sql_connection():
    conn = sqlite3.connect(f'segments.gpkg')
    c = conn.cursor()

    name_list = []
    for table_name in c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        name_list.append(table_name[0])
    name_list = [name for name in name_list if '_' not in name ]
    print(name_list)

    # coordinates_dic = {name: list(c.execute(f"SELECT y,x FROM {name} ORDER BY fid")) for name in name_list}
    coordinates =[list(c.execute(f"SELECT y,x FROM {name} ORDER BY fid")) for name in name_list]
    lengths = [route_distance(coordinate) for coordinate in coordinates]

    df_segments = pd.DataFrame.from_dict({'name': name_list, 'coordinates': coordinates, 'length': lengths})
    df_segments.to_csv('datasets/segments.csv')
    # dic2 = {}
    # for name, coordinates in coordinates_dic.items():
    #     dic2.update({coordinate: name for coordinate in coordinates})
    # lats = [key[0] for key in dic2.keys()]
    # lons = [key[1] for key in dic2.keys()]
    # names = list(dic2.values())
    # df_segments2 = pd.DataFrame.from_dict({'lat': lats, 'lon': lons, 'name': names})
    # df_segments2.to_csv('datasets/segments2.csv')

def find_nearest_dot(route_dots_list, lat, lon, epsilon=30):
    diffs = [abs(geopy.distance.geodesic((lat,lon), dot2).m) for dot2 in route_dots_list]
    index = np.argmin(diffs)
    if diffs[index] < epsilon:
        return route_dots_list[index]


def is_in_range(point1 , point2,epsilon=30):
    return (abs(geopy.distance.geodesic(point1, point2).m)<epsilon)


def ckdnearest(gdA, gdB):
    nA = (gdA)
    nB = (gdB)
    btree = cKDTree(nB)
    dist, idx = btree.query(nA,k=1)
    filtered = [gdB[j] if is_in_range(gdB[j],gdA[i]) else None for i,j in enumerate(idx) ]
    distances = dist.astype(int)
    #df = pd.DataFrame.from_dict({'distance': dist.astype(int),
     #                        'bcol': gdB[idx].values})
    return filtered

def find_segment():
    list_names = []
    data = pd.read_csv(r'datasets\shaul_hamelech_routes_2019-03-17_2019-03-23.csv', encoding = "utf-8")
    data['lat'] = data.lat.astype(float)
    data['lon'] = data.lon.astype(float)
    all_segments = pd.read_csv(r'datasets\segments2.csv', encoding = "utf-8")
    all_segments = all_segments[all_segments['name'].apply(lambda name: 'Shaul' in name)]
    all_segments['lat'] = all_segments.lat.astype(float)
    all_segments['lon'] = all_segments.lon.astype(float)

    bus_points = [coor for _,coor in data[['lat','lon']].iterrows()]
    route_dots_list = [coor for _,coor in all_segments[['lat','lon']].iterrows()]

    cordi = ckdnearest(bus_points, route_dots_list)

    for cord in cordi:
        # cordi = ckdnearest(bus_points,route_dots_list)
        if cord is not None:
            my_row = all_segments[(all_segments['lat'] == cord[0]) & (all_segments['lon'] == cord[1])]
            list_names.append(my_row["name"])
        else:
            list_names.append('')

    data["segment"] = list_names
    data.to_csv('datasets/shaul_hamelech_routes_with_segments.csv')

# def choose_only_name():
#     df = pd.read_csv(r'datasets\shaul_hamelech_routes_with_segments.csv', encoding="utf-8")
#     df['segment'] = df['segment'].apply(lambda x: cleanx(x))
#     df.to_csv('datasets/shaul_hamelech_routes_with_segments_names.csv')

# import re

# def cleanx(x):
#     # print(str(x))
#     x = str(x)
#     if x == 'nan':
#         return ''
#     a =re.match(r'\d* *(.*?)\r', x).group(1)
#     return a






# find_segment()
# sql_connection()
df = pd.read_csv(r'datasets\shaul_hamelech_routes_with_segments_names.csv', encoding = "utf-8" )
segments_df = pd.read_csv(r'datasets\segments.csv', encoding = "utf-8" )
# df = pd.read_csv(r'datasets\shaul_tests.csv', encoding = "utf-8" )
# df['time_recorded_dateTime'] = df.apply(lambda row: row['timestamp'].split('T')[0] + " "+ row["time_recorded"],axis=1)
df = df.dropna(subset=['segment'])
df['time_recorded_dateTime'] = pd.to_datetime(df['time_recorded_datetime'])
# print(df)
# df = df[df['segment'].apply(lambda x: str(x) != 'nan')]
uq_dates = df.time_recorded_dateTime.dt.date.unique()

entries_all = []
for date in uq_dates:
    entries_all+= find_data_time(15,date,df, segments_df)

all_df = pd.DataFrame(np.array(entries_all),columns=["Segment", "Day", 'From', 'To', 'AvgSpeed', 'BusCount'])

all_df.to_csv(r'datasets\S_final.csv',index = 0)




