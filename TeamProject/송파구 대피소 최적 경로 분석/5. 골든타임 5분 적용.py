#좌표간 가장 가까운 이동거리를 구했음
#이제 사람의 평균 보행 속도 또는 달리기 속도 로 몇 분 걸리는 지 알아보려고함
import pandas as pd

def parse_point(point_str):
    # "POINT (x y)" 문자열을 받아서 [y, x] 형태의 좌표 리스트를 반환합니다.
    _, coord_str = point_str.split("(")
    x_str, y_str = coord_str[:-1].split()
    return [float(y_str), float(x_str)]

# 먼저 데이터프레임을 로드합니다
gdf_points = pd.read_csv('gdf_points.csv')
gdf_points['geometry'] = gdf_points['geometry'].apply(parse_point)

# 평균 보행 속도(m/s)와 평균 달리기 속도(m/s)를 설정합니다
average_walking_speed = 1.4  # 평균 보행 속도: 1.4 m/s
average_running_speed = 2.5  # 평균 달리기 속도: 2.5 m/s

# 보행 시 걸리는 시간 컬럼 추가 (시간 = 거리 / 속도)
gdf_points['보행시간(초)'] = gdf_points['거리'] / average_walking_speed

# 달리기 시 걸리는 시간 컬럼 추가 (시간 = 거리 / 속도)
gdf_points['달리기시간(초)'] = gdf_points['거리'] / average_running_speed

# 5분을 넘기는 행 추출
exceed_5_minutes = gdf_points[gdf_points['보행시간(초)'] > 300]
exceed_5_minutes_reset = exceed_5_minutes.reset_index(drop=True)

# 추출된 행 출력
print(exceed_5_minutes)


import folium
from folium.plugins import HeatMap


songpa_map = folium.Map(location=[37.514322572335935, 127.05748125608533], zoom_start=12)

# 좌표 리스트를 HeatMap 데이터로 변환
heat_data = [[point[0], point[1], time] for point, time in zip(gdf_points['geometry'], gdf_points['보행시간(초)'])]
HeatMap(heat_data).add_to(songpa_map)

songpa_map.save('exceed_5_minutes_heatmap.html')
