import pandas as pd
import folium
import geopandas as gpd
from shapely.geometry import Point
from sklearn.neighbors import NearestNeighbors
from geopy.distance import geodesic

# 데이터 파일들을 불러옵니다.
facility_df = pd.read_csv('서울특별시 송파구_민방위대피시설_20210914.csv', encoding='UTF-8')
songpa_df = pd.read_csv('송파구 동별 인구 수.csv', encoding='UTF-8')
points_df = pd.read_csv('points.csv')

# 송파구를 중심으로 하는 지도를 생성합니다.
songpa_map = folium.Map(location=[37.514322572335935, 127.05748125608533], zoom_start=12)

# 민방위 대피시설의 위치에 마커를 추가합니다.
for index, row in facility_df.iterrows():
    facility_name = row['민방위대피시설명']
    latitude = row['위도']
    longitude = row['경도']
    folium.Marker([latitude, longitude], popup=facility_name).add_to(songpa_map)

# 서울의 행정구역 경계 GeoJSON 데이터를 불러옵니다.
gdf = gpd.read_file('HangJeongDong_ver20230401.geojson')
gdf_songpa = gdf[gdf['sggnm'] == '송파구']
folium.GeoJson(gdf_songpa).add_to(songpa_map)

# 랜덤한 점들을 생성합니다.
points = [Point(row['Longitude'], row['Latitude']) for _, row in points_df.iterrows()]

# 점들로부터 GeoDataFrame을 생성합니다.
gdf_points = gpd.GeoDataFrame(geometry=points)

# KNN을 이용해 각 점에 대한 가장 가까운 시설을 찾습니다.
facility_coordinates = facility_df[['위도', '경도']].values
knn = NearestNeighbors(n_neighbors=1)
knn.fit(facility_coordinates)

closest_facilities = []
distances = []

for point in points:
    _, nearest_index = knn.kneighbors([[point.y, point.x]])
    closest_facility = facility_df.loc[nearest_index[0][0], '민방위대피시설명']
    closest_facilities.append(closest_facility)
    
    # 점과 시설 사이의 거리를 계산합니다.
    facility_latitude = facility_df.loc[nearest_index[0][0], '위도']
    facility_longitude = facility_df.loc[nearest_index[0][0], '경도']
    distance = geodesic((point.y, point.x), (facility_latitude, facility_longitude)).meters
    distances.append(distance)

# GeoDataFrame에 가장 가까운 시설과 거리 열을 추가합니다.
gdf_points['가장가까운대피시설명'] = closest_facilities
gdf_points['거리'] = distances

# 각 가장 가까운 시설에 대한 점의 수를 계산합니다.
facility_count = gdf_points['가장가까운대피시설명'].value_counts().reset_index()
facility_count.columns = ['대피소명', '카운트']

# 시설 카운트를 CSV 파일로 저장합니다.
facility_count.to_csv('facility_count.csv', index=False)
gdf_points.to_csv('gdf_points.csv', index=False)

print(facility_count)
