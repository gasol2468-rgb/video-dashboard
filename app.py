import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="短影音分析系統", layout="wide")

# 真正的 Google Sheet CSV 網址
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCKOspk1Ev6WEzdSGWWxNgDtfywFnayuER5OBUs5a20BmbiYVyUAiKcyFNCMM6VgKDAacVKRPu6pww/pub?output=csv"

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    df["date"] = pd.to_datetime(df["date"])

    # 沒有 client 欄位時，自動補一個預設客戶，避免整個網站壞掉
    if "client" not in df.columns:
        df["client"] = "預設客戶"

    # 沒有 platform 時補預設值
    if "platform" not in df.columns:
        df["platform"] = "Instagram"

    # 沒有 likes/comments 時補 0
    if "likes" not in df.columns:
        df["likes"] = 0
    if "comments" not in df.columns:
        df["comments"] = 0

    return df

df = load_data()

# =========================
# 側邊欄：客戶與日期
# =========================
st.sidebar.title("篩選條件")

clients = df["client"].dropna().unique().tolist()
selected_client = st.sidebar.selectbox("選擇客戶", clients)

df = df[df["client"] == selected_client].copy()

start_date = st.sidebar.date_input("開始日期", df["date"].min().date())
end_date = st.sidebar.date_input("結束日期", df["date"].max().date())

df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
].copy()

if st.sidebar.button("🔄 重新抓取 Google Sheet"):
    load_data.clear()
    st.rerun()

if df.empty:
    st.title(f"📊 {selected_client}｜短影音分析報告")
    st.warning("目前篩選條件下沒有資料。")
    st.stop()

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
st.plotly_chart(fig, width="stretch")

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
# AI 簡易分析
# =========================
best_video = top3.iloc[0]["title"]
best_views = int(top3.iloc[0]["views"])

st.subheader("🤖 分析結論")
st.info(
    f"本期表現最佳影片為【{best_video}】，觀看數達 {best_views:,}。"
    f"建議優先複製這支影片的主題與形式，延伸成系列內容。"
)

st.divider()

# =========================
# 原始資料
# =========================
st.subheader("📋 原始資料")
st.dataframe(df, width="stretch")