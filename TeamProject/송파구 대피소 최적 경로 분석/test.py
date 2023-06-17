from folium.plugins import HeatMap
import pandas as pd
import folium

points_df = pd.read_csv('points.csv')
facility_df = pd.read_csv('서울특별시 송파구_민방위대피시설_20210914.csv',encoding='UTF-8')

songpa_map = folium.Map(location=[37.514322572335935, 127.05748125608533], zoom_start=12)

for index, row in facility_df.iterrows():
    facility_name = row['민방위대피시설명']
    latitude = row['위도']
    longitude = row['경도']
    
    # Add marker to the map
    folium.Marker([latitude, longitude], popup=facility_name).add_to(songpa_map)



# Create a list of coordinates
heat_data = points_df[['Latitude', 'Longitude']].values.tolist()

# Create a HeatMap
HeatMap(heat_data).add_to(songpa_map)
import geopandas as gpd
import folium

# GeoJSON 파일 읽기
gdf = gpd.read_file('HangJeongDong_ver20230401.geojson')

# 송파구에 해당하는 데이터만 필터링
gdf_songpa = gdf[gdf['sggnm'] == '송파구']


folium.GeoJson(gdf_songpa).add_to(songpa_map)  # 송파구 데이터를 지도에 추가

# Save the map
songpa_map.save('songpa_heatmap.html')
