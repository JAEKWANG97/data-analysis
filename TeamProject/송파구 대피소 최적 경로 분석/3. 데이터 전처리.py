import pandas as pd

facility_count_df = pd.read_csv('facility_count.csv')
facility_df = pd.read_csv('서울특별시 송파구_민방위대피시설_20210914.csv', encoding='UTF-8')

# 대피소명 기준으로 facility_count_df와 facility_df를 병합합니다.
facility_df = pd.merge(facility_df, facility_count_df, left_on='민방위대피시설명', right_on='대피소명', how='left')

# 누락된 카운트를 0으로 채웁니다.
facility_df['카운트'] = facility_df['카운트'].fillna(0)

# 불필요한 열들을 삭제합니다.
facility_df = facility_df.drop('소재지지번주소',axis=1)
facility_df = facility_df.drop('개방여부',axis=1)
facility_df = facility_df.drop('관리기관명',axis=1)
facility_df = facility_df.drop('데이터기준일자',axis=1)
facility_df = facility_df.drop('민방위대피시설구분',axis=1)
facility_df = facility_df.drop('소재지도로명주소',axis=1)
facility_df = facility_df.drop('대피소명',axis=1)

# 업데이트된 facility_df를 CSV 파일로 저장합니다.
facility_df.to_csv('updated_facility.csv', index=False)
print(facility_df)
