import pandas as pd
import geopy.distance
import numpy as np

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

def found_nearest_dot(route_dots_list, dot):
    index = np.argmin([abs(geopy.distance.geodesic(dot, dot2).m) for dot2 in route_dots_list])
    return route_dots_list[index]

def calc_speed(df, segment, start_time, end_time):
    start_point, end_point = segment[0], segment[-1]
    dist = route_distance(segment)
    # df = 1 # time interval
    trips = df.groupby('trip_id_to_date')
    for _, g in trips:
        df_group = df[df['time_recorded_datetime'].between(start_time, end_time)]


origin = route_dots_list[0]
dest = route_dots_list[-1]
print(route_distance(route_dots_list))

dot = (32.098752, 34.7794)
print(found_nearest_dot(route_dots_list, dot))