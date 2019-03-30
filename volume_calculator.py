
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

def find_data_time(minutes,date,df):
    df = df[pd.to_datetime(df['time_recorded_dateTime']).dt.date == date]
    curDate = df["time_recorded_dateTime"].min()
    nextDate = curDate + timedelta(minutes = minutes)
    end_date =  df["time_recorded_dateTime"].max()
    dic_times  = pd.DataFrame(columns=('start_interval', 'end_interval', 'uniqueBus'))
    while nextDate < end_date:
        current_data = df[df['time_recorded_dateTime'].between(curDate,nextDate)]
        #groupby segment
        #redundent duplicates by trip id or busid
        #count
        #write to csv
        curDate = nextDate
        nextDate = curDate + timedelta(minutes = minutes)

    current_data = df[df['time_recorded_dateTime'].between(curDate, end_date)]

def sql_connection():
    conn = sqlite3.connect(f'segments.gpkg')
    c = conn.cursor()

    name_list = []
    for table_name in c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        name_list.append(table_name[0])
    # name_list = [name for name in name_list if '_' not in name ]
    print(name_list)

    coordinates_dic = {name: list(c.execute(f"SELECT y,x FROM {name} ORDER BY fid")) for name in name_list}
    coordinates =[list(c.execute(f"SELECT y,x FROM {name} ORDER BY fid")) for name in name_list]
    df_segments = pd.DataFrame.from_dict({'name': name_list, 'coordinates': coordinates})
    df_segments.to_csv('datasets/segments.csv')
    dic2 = {}
    for name, coordinates in coordinates_dic.items():
        dic2.update({coordinate: name for coordinate in coordinates})
    lats = [key[0] for key in dic2.keys()]
    lons = [key[1] for key in dic2.keys()]
    names = list(dic2.values())
    df_segments2 = pd.DataFrame.from_dict({'lat': lats, 'lon': lons, 'name': names})
    df_segments2.to_csv('datasets/segments2.csv')

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

find_segment()
# sql_connection()
# df = pd.read_csv(r'datasets\shaul_hamelech_routes_2019-03-17_2019-03-23.csv', encoding = "utf-8" )
# # df['time_recorded_dateTime'] = df.apply(lambda row: row['timestamp'].split('T')[0] + " "+ row["time_recorded"],axis=1)
# df['time_recorded_dateTime'] = pd.to_datetime(df['time_recorded_dateTime'])
# print(df)
# uq_dates = df.time_recorded_dataTime.dt.date.unique()
#
# for date in uq_dates:
#     find_data_time(15,date,df)




