import pandas as pd

facility = pd.read_csv('서울특별시 송파구_민방위대피시설_20210914.csv')
updated_facility = pd.read_csv('updated_facility.csv')

# 대피가능 인원수를 초과하는 시설을 찾아냅니다.
exceed_capacity_df = updated_facility[updated_facility['카운트'] > updated_facility['대피가능인원수']]
# 카운트와 대피 가능 인원수의 비율을 계산합니다.
exceed_capacity_df['비율'] = exceed_capacity_df['카운트'] / exceed_capacity_df['대피가능인원수']

print(exceed_capacity_df)

songpa_df = pd.read_csv('송파구 동별 인구 수.csv',encoding='UTF-8')
points_df = pd.read_csv('points.csv')

# 송파구 전체 인구수를 계산합니다.
songpa_total_pop = songpa_df['계'].sum()

# 모든 열을 보여주도록 설정합니다.
pd.set_option('display.max_columns', None)

# '민방위대피시설면적' 열을 삭제합니다.
exceed_capacity_df = exceed_capacity_df.drop('민방위대피시설면적',axis=1)

# exceed_capacity_df를 출력합니다. (열이 정렬되어 출력됩니다.)
print(exceed_capacity_df.to_string(index=False))

# 각종 통계를 계산하고 출력합니다.
Total_capacity = facility['대피가능인원수'].sum()
facility_capacity = updated_facility['대피가능인원수'].sum()
updated_facility_capacity = updated_facility['카운트'].sum()
exceed_facility_capacity = exceed_capacity_df['카운트'].sum()

print(Total_capacity)
print(songpa_total_pop)
print(facility_capacity)
print(updated_facility_capacity)
print(int(exceed_facility_capacity))

print(exceed_capacity_df)
#가장 가까운 대피소로 이동한다고 가정하면 수용인원 초과되는 대피소가 66행이 나옴

# 비율이 가장 큰 행을 찾아 출력합니다.
max_ratio_index = exceed_capacity_df['비율'].idxmax()
max_ratio_row = exceed_capacity_df.loc[max_ratio_index]

print(max_ratio_row)
