import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

# 데이터 불러오기
df = pd.read_csv('지진_데이터.csv')

# 숫자형 변환
df['규모'] = df['규모'].astype(float)
df['위도'] = df['위도'].astype(float)
df['경도'] = df['경도'].astype(float)
df['연도'] = pd.to_datetime(df['시간']).dt.year

st.title("한국과 주변 지역의 지진 데이터 시각화 + 이상치 탐지")

# 지역명 검색 UI
region = st.text_input("찾고 싶은 지역명을 입력하세요 (예: 경북, 평안북도, 홍성 등)", "")
if region:
    df_filtered = df[df['위치'].str.contains(region, case=False, na=False)]
    st.write(f"**'{region}'이(가) 포함된 지진 데이터: {len(df_filtered)}건**")
    if df_filtered.empty:
        st.warning("해당 지역의 지진 데이터가 없습니다. 다른 키워드로 입력해 보세요.")
else:
    df_filtered = df

# === [1] 규모 기준 이상치 탐지 ===
mean_mag = df_filtered['규모'].mean()
std_mag = df_filtered['규모'].std()
threshold = mean_mag + 1.5 * std_mag
df_filtered['is_outlier'] = df_filtered['규모'] > threshold

st.header("1. 지진 발생 위치 지도 (Folium) - 이상치(큰 지진) 강조")

m = folium.Map(location=[36.5, 127.8], zoom_start=6)
marker_cluster = MarkerCluster().add_to(m)
for idx, row in df_filtered.iterrows():
    color = 'red' if row['is_outlier'] else 'blue'
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=f"날짜: {row['시간']}<br>규모: {row['규모']}<br>위치: {row['위치']}" + ("<br><b>※이상치(큰 지진)</b>" if row['is_outlier'] else ""),
        tooltip=f"규모 {row['규모']}" + (" (이상치)" if row['is_outlier'] else ""),
        icon=folium.Icon(color=color)
    ).add_to(marker_cluster)
st_folium(m, width=700, height=500)

# === [2] 연도별 발생 빈도 이상치 탐지 ===
st.header("2. 연도별 지진 발생 수 - 빈도 이상치 강조")
year_count = df_filtered['연도'].value_counts().sort_index()
mean_count = year_count.mean()
std_count = year_count.std()
count_threshold = mean_count + 1.5 * std_count
is_count_outlier = year_count > count_threshold

fig = px.bar(
    x=year_count.index, y=year_count.values, 
    labels={'x': '연도', 'y': '지진 수'}, title="연도별 지진 발생 수",
    color=is_count_outlier, color_discrete_map={True: "red", False: "blue"}
)
fig.update_traces(marker_line_width=1.5, marker_line_color='black')
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# === [3] 지진 규모 분포 (이상치 강조) ===
st.header("3. 지진 규모 분포 (이상치 강조)")
fig2 = px.histogram(
    df_filtered, x='규모', nbins=20, title="지진 규모 분포 (히스토그램)",
    color='is_outlier', color_discrete_map={True: "red", False: "blue"},
    labels={"is_outlier": "이상치 여부"}
)
st.plotly_chart(fig2, use_container_width=True)

st.info("지도와 그래프에서 붉은색은 평균보다 큰 이상치(특이한 지진)를, 파란색은 일반 지진을 나타냅니다.")
