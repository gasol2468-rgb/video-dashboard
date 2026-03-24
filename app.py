import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="短影音分析系統", layout="wide")

GOOGLE_SHEET_CSV_URL = "你的CSV網址"

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# =========================
# 🔥 客戶選擇
# =========================
st.sidebar.title("客戶選擇")

clients = df["client"].dropna().unique().tolist()
selected_client = st.sidebar.selectbox("選擇客戶", clients)

df = df[df["client"] == selected_client]

# =========================
# 日期篩選
# =========================
start_date = st.sidebar.date_input("開始日期", df["date"].min().date())
end_date = st.sidebar.date_input("結束日期", df["date"].max().date())

df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
]

# =========================
# KPI
# =========================
st.title(f"📊 {selected_client}｜短影音分析報告")

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
# TOP影片
# =========================
st.subheader("🔥 爆款影片")

top3 = df.sort_values(by="views", ascending=False).head(3)

for i, row in enumerate(top3.itertuples(), 1):
    st.write(f"{i}. {row.title}（{int(row.views):,}觀看）")

st.divider()

# =========================
# AI簡單分析
# =========================
best_video = top3.iloc[0]["title"]
best_views = int(top3.iloc[0]["views"])

st.subheader("🤖 分析結論")

st.info(f"""
本期表現最佳影片為【{best_video}】，觀看數達 {best_views:,}。
建議優先複製該內容形式，延伸相關主題製作系列影片，
並加強開頭吸引力與留言互動設計。
""")

# =========================
# CTA
# =========================
st.subheader("🚀 合作方案")

st.success("""
📌 月顧問  
📌 代操服務  
👉 歡迎合作
""")

st.dataframe(df, use_container_width=True)