import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import os
os.environ['OMP_NUM_THREADS'] = '4'

#해당 파일에서는 가장 멀리 있는 인원을 재할당하는게 아닌 가장 가까운 인원을 재할당 함으로써 전체적으로 평등한 대피소 경로를 추출하고자함
# 먼저, 대피소와 인원 데이터를 로드합니다.
shelters = pd.read_csv('updated_facility.csv')
shelters['카운트'] = 0
people = pd.read_csv('points.csv').sample(200)

# Prepare data for clustering
X = people[['Latitude', 'Longitude']].values
init = shelters[['위도', '경도']].values

# Perform clustering
kmeans = KMeans(n_clusters=init.shape[0], init=init, n_init=1)
people['cluster'] = kmeans.fit_predict(X)

# Count the number of people assigned to each shelter
counts = people['cluster'].value_counts()

# If a shelter is over capacity, reassign the nearest person to the nearest shelter
for index, row in shelters.iterrows():
    count = counts.get(index, 0)
    while count > row['대피가능인원수']:
        # 대피소에 가장 가까운 인원을 찾습니다.
        nearest_person_index = people[people['cluster'] == index]['distance'].idxmin()

        # 가장 가까운 인원에 대해 가장 가까운 대피소를 찾습니다.
        shelters['distance'] = np.sqrt((shelters['위도'] - people.loc[nearest_person_index, 'Latitude'])**2 + (shelters['경도'] - people.loc[nearest_person_index, 'Longitude'])**2)
        nearest_shelter_index = shelters['distance'].idxmin()

        # 인원을 가장 가까운 대피소로 재할당합니다.
        people.loc[nearest_person_index, 'cluster'] = nearest_shelter_index

        # 인원 수를 업데이트합니다.
        counts[nearest_shelter_index] += 1
        counts[index] -= 1

# import matplotlib.pyplot as plt

# # 각 클러스터에 대해 다른 색을 사용하여 사람들의 위치를 플롯합니다.
# colors = ['b', 'g', 'r', 'c', 'm', 'y', 'orange', 'purple', 'brown']
# fig, ax = plt.subplots(figsize=(10, 10))
# for i in range(len(shelters)):
#     cluster_points = people[people['cluster'] == i]
#     ax.scatter(cluster_points['Longitude'], cluster_points['Latitude'], s=5, c=colors[i % len(colors)])

# # 대피소의 위치를 플롯합니다.
# ax.scatter(shelters['경도'], shelters['위도'], s=100, c='black', marker='X')

# plt.show()

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

# # 지도를 HTML 파일
