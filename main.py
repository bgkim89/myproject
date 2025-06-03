import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px

# 데이터 불러오기
df = pd.read_csv('지진_데이터.csv')

st.title("한국과 주변 지역의 지진 데이터 시각화")
st.markdown("""
중학생을 위한 재해재난(지진) 데이터 시각화 앱입니다.  
아래에서 지도와 그래프로 우리나라와 주변 지역에서 발생한 지진을 살펴볼 수 있습니다.
""")

# 지도 시각화
st.header("1. 지진 발생 위치 지도 (Folium)")

m = folium.Map(location=[36.5, 127.8], zoom_start=6)  # 한반도 중심 좌표

marker_cluster = MarkerCluster().add_to(m)
for idx, row in df.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=f"날짜: {row['시간']}<br>규모: {row['규모']}<br>위치: {row['위치']}",
        tooltip=f"규모 {row['규모']}"
    ).add_to(marker_cluster)

st_data = st_folium(m, width=700, height=500)

# 연도별/규모별 그래프
st.header("2. 지진 통계 그래프 (Plotly)")
df['연도'] = pd.to_datetime(df['시간']).dt.year
df['규모'] = df['규모'].astype(float)

tab1, tab2 = st.tabs(['연도별 지진 발생 수', '지진 규모 분포'])

with tab1:
    year_count = df['연도'].value_counts().sort_index()
    fig = px.bar(x=year_count.index, y=year_count.values, labels={'x': '연도', 'y': '지진 수'}, title="연도별 지진 발생 수")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = px.histogram(df, x='규모', nbins=20, title="지진 규모 분포 (히스토그램)")
    st.plotly_chart(fig2, use_container_width=True)

st.info("지도를 확대/이동하거나, 막대그래프와 히스토그램에서 각종 패턴을 살펴보세요!")
