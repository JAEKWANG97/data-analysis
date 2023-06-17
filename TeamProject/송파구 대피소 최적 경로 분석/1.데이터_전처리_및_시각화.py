import requests
import json
import pandas as pd
import folium
import numpy as np
import random
from shapely.geometry import Point


facility_df = pd.read_csv('서울특별시 송파구_민방위대피시설_20210914.csv',encoding='UTF-8')
songpa_df = pd.read_csv('송파구 동별 인구 수.csv',encoding='UTF-8')

points_df = pd.read_csv('points.csv')


print(facility_df.head())
print(songpa_df.head())

print(facility_df.describe())
print(songpa_df.describe())

facility_total_pop = facility_df['대피가능인원수'].sum()
songpa_total_pop = songpa_df['계'].sum()



#전체 수용인원수가 송파구 인구의 약 2.5배임
#하지만 이는 1인당 대피면적을 0.825미터 제곱으로 계산을 한 것.
#이는 170cm 성인 남성이 누우면 차리하는 면적과 거의 일치

#우선 대피소 위치의 효율성을 먼저 분석해보겠음
# Create a map centered around Songpa-gu, Seoul
# folium 지도 생성
songpa_map = folium.Map(location=[37.514322572335935, 127.05748125608533], zoom_start=12)
# Iterate over the facility dataframe and add markers to the map
for index, row in facility_df.iterrows():
    facility_name = row['민방위대피시설명']
    latitude = row['위도']
    longitude = row['경도']
    
    # Add marker to the map
    folium.Marker([latitude, longitude], popup=facility_name).add_to(songpa_map)



# 서울 행정구역 json raw파일(githubcontent)
# Load Seoul municipal boundaries JSON data
# r = requests.get('https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json')
# seoul_geo = r.json()

# songpa_geo = None
# for feature in seoul_geo['features']:
#     if feature['properties']['name'] == '송파구':
#         songpa_geo = feature
#         break

# Add Seoul municipal boundaries to the map
# folium.GeoJson(songpa_geo, name='지역구').add_to(songpa_map)

# import geopandas as gpd
# import folium

# # GeoJSON 파일 읽기
# gdf = gpd.read_file('HangJeongDong_ver20230401.geojson')

# # 송파구에 해당하는 데이터만 필터링
# gdf_songpa = gdf[gdf['sggnm'] == '송파구']



# # 송파구 데이터를 지도에 추가
# folium.GeoJson(gdf_songpa).add_to(songpa_map)

# # 지도 출력



songpa_df = songpa_df.drop('남', axis=1) 
songpa_df = songpa_df.drop('여', axis=1) 
facility_df = facility_df.drop('소재지지번주소',axis=1)
facility_df = facility_df.drop('개방여부',axis=1)
facility_df = facility_df.drop('관리기관명',axis=1)
facility_df = facility_df.drop('데이터기준일자',axis=1)
print(songpa_df)

facility_df = facility_df.drop('민방위대피시설구분',axis=1)
# 각 동별 인구수를 확률 분포로 변환
songpa_df['인구분포'] = songpa_df['계'] / songpa_df['계'].sum()


# 각 동별 인구 수와 대피소 수용 인원 비율 계산
songpa_df['대피소수용인원비율'] = songpa_df['계'] / facility_total_pop

# 대피소 수용 인원과 각 동별 인구 수의 상관관계 분석
correlation = songpa_df['대피소수용인원비율'].corr(songpa_df['계'])




#세분화된 동 통합 => 가락 1동 가락 2동 가락 본동 ==> 가락
songpa_df['동별_통합'] = songpa_df['동별'].str.slice(stop=2)
songpa_merged_df = songpa_df.groupby('동별_통합').agg({'계': 'sum', '인구분포': 'sum', '대피소수용인원비율': 'sum'}).reset_index()


print(songpa_merged_df)

facility_df['동별'] = facility_df['소재지도로명주소'].str.extract(r'\(([^()]+)\)')
facility_df['동별'] = facility_df['동별'].apply(lambda x: x.split('동')[0])


# print(facility_df)

unique_dongs = facility_df['동별'].unique()
print(unique_dongs)
# print( gdf_songpa[gdf_songpa['temp']].unique())

# nan_rows = facility_df[facility_df['동별'].isna()]
# print(nan_rows)

# print(facility_df)

# grouped_facility = facility_df.groupby('동별').agg({'민방위대피시설명': 'count', '민방위대피시설면적': 'sum', '대피가능인원수': 'sum'})


# print(grouped_facility)

# 'temp' 컬럼에서 '송파구 ' 부분을 제거하고 앞뒤 공백을 제거
gdf_songpa['temp'] = gdf_songpa['temp'].str.replace('송파구 ', '').str.strip()

# '동별' 컬럼에서 앞뒤 공백을 제거
songpa_df['동별'] = songpa_df['동별'].str.strip()
points = []

print(songpa_df['동별'])
print(gdf_songpa['temp'].str.strip().reset_index(drop=True))

for idx, row in songpa_df.iterrows():
    gdf_songpa.loc[gdf_songpa['temp'].str.strip() == row['동별'], '인구수'] = row['계']

print(gdf_songpa.head())

# 포인트를 생성 후 csv 파일로 저장함
# # 인구수만큼 포인트 생성
# for row in gdf_songpa.iterrows():
#     poly = row[1]['geometry']
#     population = row[1]['인구수']
#     for _ in range(int(population)):  # 100은 임의의 값으로, 이 값에 따라 생성되는 포인트의 수가 달라집니다.
#         while True:
#             point = Point(random.uniform(poly.bounds[0], poly.bounds[2]), random.uniform(poly.bounds[1], poly.bounds[3]))
#             if poly.contains(point):
#                 points.append(point)
#                 break

# # Convert the points to a DataFrame
# points_df = pd.DataFrame({'Latitude': [point.y for point in points], 'Longitude': [point.x for point in points]})

# # Save the points DataFrame to a CSV file
# points_df.to_csv('points.csv', index=False)

# 포인트를 GeoDataFrame으로 변환
gdf_points = gpd.GeoDataFrame(geometry=points)

# # 포인트를 지도에 표시
# for point in points:
#     folium.Marker([point.y, point.x] ,      icon=folium.Icon(color="red"),).add_to(songpa_map)


# 해당 시각화 자료를 html파일로 저장
songpa_map.save('songpa_map.html')

from folium.plugins import HeatMap

# Create a list of coordinates
heat_data = [[point.y, point.x] for point in points]

# Create a HeatMap
HeatMap(heat_data).add_to(songpa_map)

# Save the map
songpa_map.save('songpa_heatmap.html')

# 저장된 points 로 가장 가까운 대피소를 알아보는데 이걸 카운트까지 할거임
from geopy.distance import geodesic
closest_facilities = []

for _, point_row in points_df.iterrows():
    point = (point_row['Latitude'], point_row['Longitude'])
    closest_facility = None
    min_distance = float('inf')
    
    for _, facility_row in facility_df.iterrows():
        facility_name = facility_row['민방위대피시설명']
        facility_latitude = facility_row['위도']
        facility_longitude = facility_row['경도']
        
        # Calculate the distance between the point and the facility
        distance = geodesic(point, (facility_latitude, facility_longitude)).meters
        
        # Update the closest facility if a closer one is found
        if distance < min_distance:
            min_distance = distance
            closest_facility = facility_name
    
    closest_facilities.append(closest_facility)

# Add the closest facility information to the points DataFrame
points_df['Closest Facility'] = closest_facilities

# Count the occurrences of each closest facility
facility_count = points_df['Closest Facility'].value_counts().reset_index()
facility_count.columns = ['Facility', 'Count']

print(facility_count)
