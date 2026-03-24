import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="短影音分析報告", layout="wide")

# =========================
# 🔥 把你的 CSV 網址貼這裡
# =========================
GOOGLE_SHEET_CSV_URL = "<iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSCKOspk1Ev6WEzdSGWWxNgDtfywFnayuER5OBUs5a20BmbiYVyUAiKcyFNCMM6VgKDAacVKRPu6pww/pubhtml?gid=0&amp;single=true&amp;widget=true&amp;headers=false"></iframe>"

# =========================
# 讀取資料
# =========================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# =========================
# 標題
# =========================
st.title("📊 短影音數據分析報告")

# =========================
# KPI
# =========================
total_views = int(df["views"].sum())
total_likes = int(df["likes"].sum())
total_comments = int(df["comments"].sum())

col1, col2, col3 = st.columns(3)
col1.metric("總觀看", f"{total_views:,}")
col2.metric("總按讚", f"{total_likes:,}")
col3.metric("總留言", f"{total_comments:,}")

st.divider()

# =========================
# 圖表
# =========================
st.subheader("📈 觀看趨勢")

fig = px.line(
    df,
    x="date",
    y="views",
    color="platform",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# =========================
# TOP 影片
# =========================
st.subheader("🔥 爆款影片 TOP 3")

top3 = df.sort_values(by="views", ascending=False).head(3)

for i, row in enumerate(top3.itertuples(), 1):
    st.write(f"{i}. {row.title}（{int(row.views):,}觀看）")

st.divider()

# =========================
# 原始資料
# =========================
st.subheader("📋 原始資料")
st.dataframe(df, use_container_width=True)

# =========================
# 手動刷新按鈕
# =========================
if st.button("🔄 重新抓取 Google Sheet"):
    load_data.clear()
    st.rerun()