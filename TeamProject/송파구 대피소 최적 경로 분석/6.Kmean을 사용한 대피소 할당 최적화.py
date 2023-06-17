import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import os
os.environ['OMP_NUM_THREADS'] = '4'


# 먼저, 대피소와 인원 데이터를 로드합니다.
# 해당 알고리즘에서는 거리가 가장 먼 인원들을 재배치 했었음
shelters = pd.read_csv('updated_facility.csv')
shelters['카운트'] = 0
shelters = shelters.drop('카운트',axis=1)

people = pd.read_csv('points.csv').sample(1000)
my_location = pd.DataFrame({'Latitude': [37.49687939935719], 'Longitude': [127.13548474247413]})
people = pd.concat([people, my_location], ignore_index=True)



# 클러스터링을 위한 데이터 준비
X = people[['Latitude', 'Longitude']].values
init = shelters[['위도', '경도']].values

# 클러스터링 수행
kmeans = KMeans(n_clusters=init.shape[0], init=init, n_init=1)
people['cluster'] = kmeans.fit_predict(X)

# 각 대피소에 할당된 인원 수 계산
counts = people['cluster'].value_counts()
print(shelters)

# 대피소가 수용인원을 초과한 경우, 가장 멀리 있는 인원을 가장 가까운 대피소로 재할당
# 대피소의 수용인원을 고려하여 인원을 재할당
for index, row in shelters.iterrows():
    count = counts.get(index, 0)
    while count > row['대피가능인원수']:
        # 대피소로부터 가장 멀리 떨어진 인원 찾기
        people_in_cluster = people[people['cluster'] == index].copy()
        people_in_cluster['distance'] = np.sqrt((people_in_cluster['Latitude'] - row['위도'])**2 + (people_in_cluster['Longitude'] - row['경도'])**2)
        farthest_person_index = people_in_cluster['distance'].idxmax()

        # 대피소 중에서 수용인원을 초과하지 않는 가장 가까운 대피소 찾기
        feasible_shelters = shelters[shelters['대피가능인원수'] >= count]
        feasible_shelters['distance'] = np.sqrt((feasible_shelters['위도'] - people_in_cluster.loc[farthest_person_index, 'Latitude'])**2 + 
                                                (feasible_shelters['경도'] - people_in_cluster.loc[farthest_person_index, 'Longitude'])**2)
        nearest_shelter_index = feasible_shelters['distance'].idxmin()

        # 인원을 가장 가까운 대피소로 재할당
        people.loc[farthest_person_index, 'cluster'] = nearest_shelter_index

        # 인원 수 업데이트
        count -= 1
        counts[nearest_shelter_index] += 1
        counts[index] -= 1

# 나의 좌표가 어떤 클러스터에 할당되었는지 확인
my_cluster = people.loc[people['Latitude'] == 37.49687939935719]['cluster'].values[0]
my_shelter = shelters.loc[my_cluster]
print(my_shelter)
print(f"가장 가까운 대피소는 위도 {my_shelter['위도']}, 경도 {my_shelter['경도']}에 위치하고 있습니다.")

import matplotlib.pyplot as plt

# 각 클러스터에 대해 다른 색을 사용하여 사람들의 위치를 플롯합니다.
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'orange', 'purple', 'brown']
fig, ax = plt.subplots(figsize=(10, 10))
for i in range(len(shelters)):
    cluster_points = people[people['cluster'] == i]
    ax.scatter(cluster_points['Longitude'], cluster_points['Latitude'], s=5, c=colors[i % len(colors)])

# 대피소의 위치를 플롯합니다.
ax.scatter(shelters['경도'], shelters['위도'], s=100, c='black', marker='X')

plt.show()


import folium

# 내 위치와 가장 가까운 대피소의 위치
my_location_coords = [my_location['Latitude'].values[0], my_location['Longitude'].values[0]]
my_shelter_coords = [my_shelter['위도'], my_shelter['경도']]

# 지도 생성
m = folium.Map(location=my_location_coords, zoom_start=14)

# 내 위치 표시
folium.Marker(
    location=my_location_coords,
    popup='My Location',
    icon=folium.Icon(icon="cloud"),
).add_to(m)

# 가장 가까운 대피소 위치 표시
folium.Marker(
    location=my_shelter_coords,
    popup='Nearest Shelter',
    icon=folium.Icon(color="red"),
).add_to(m)

# 지도를 HTML 파일로 저장
m.save('my_location_map.html')



# import folium
# from folium.plugins import MarkerCluster

# # 지도 생성
# m = folium.Map(location=[37.537230684313975, 127.12177042377495], zoom_start=12)

# # MarkerCluster 객체 생성
# marker_cluster = MarkerCluster().add_to(m)

# folium.Marker(
#     location=[shelters.loc[2, '위도'], shelters.loc[2, '경도']],
#     icon=folium.Icon(color='black'),
#     popup="대피소 2",
# ).add_to(m)

# for index, row in people[people['cluster'] == 2].iterrows():
#     folium.Marker(location=[row['Latitude'], row['Longitude']]).add_to(marker_cluster)

# # 지도를 HTML 파일로 저장
# m.save('marker_cluster_map.html')
