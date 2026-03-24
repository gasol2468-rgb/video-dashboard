import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="短影音分析系統", layout="wide")

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCKOspk1Ev6WEzdSGWWxNgDtfywFnayuER5OBUs5a20BmbiYVyUAiKcyFNCMM6VgKDAacVKRPu6pww/pub?output=csv"

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    df["date"] = pd.to_datetime(df["date"])

    if "client" not in df.columns:
        df["client"] = "預設客戶"

    for col in ["likes", "comments", "shares", "saves", "followers_gained"]:
        if col not in df.columns:
            df[col] = 0

    if "platform" not in df.columns:
        df["platform"] = "Instagram"

    if "category" not in df.columns:
        df["category"] = "其他"

    return df

df = load_data()

# =========================
# 專屬網址參數
# 用法：
# ?client=聚鑫茶
# =========================
query_params = st.query_params
url_client = query_params.get("client", None)

clients = df["client"].dropna().unique().tolist()

# 如果網址有 client 參數，就優先用網址
if url_client and url_client in clients:
    selected_client = url_client
else:
    selected_client = clients[0] if clients else "預設客戶"

# 側邊欄
st.sidebar.title("客戶選擇")
selected_client = st.sidebar.selectbox(
    "選擇客戶",
    clients,
    index=clients.index(selected_client) if selected_client in clients else 0
)

# 同步網址參數
st.query_params["client"] = selected_client

df = df[df["client"] == selected_client].copy()

# 日期篩選
start_date = st.sidebar.date_input("開始日期", df["date"].min().date())
end_date = st.sidebar.date_input("結束日期", df["date"].max().date())

df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
]

if st.sidebar.button("🔄 重新抓取資料"):
    load_data.clear()
    st.rerun()

if df.empty:
    st.warning("目前沒有資料")
    st.stop()

# KPI
st.title(f"📊 {selected_client}｜短影音分析報告")

total_views = int(df["views"].sum())
total_likes = int(df["likes"].sum())
total_comments = int(df["comments"].sum())
total_followers = int(df["followers_gained"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("總觀看", f"{total_views:,}")
col2.metric("總按讚", f"{total_likes:,}")
col3.metric("總留言", f"{total_comments:,}")
col4.metric("新增粉絲", f"{total_followers:,}")

st.divider()

# 圖表
st.subheader("📈 觀看趨勢")
fig = px.line(df, x="date", y="views", color="platform", markers=True)
st.plotly_chart(fig, width="stretch")

st.divider()

# TOP影片
st.subheader("🔥 爆款影片 TOP 3")
top3 = df.sort_values(by="views", ascending=False).head(3)

for i, row in enumerate(top3.itertuples(), 1):
    st.write(f"{i}. {row.title}（{int(row.views):,}觀看）")

st.divider()

# AI 分析
best_video = top3.iloc[0]["title"]
best_views = int(top3.iloc[0]["views"])
best_platform = df.groupby("platform")["views"].sum().idxmax()
best_category = df.groupby("category")["views"].sum().idxmax()

st.subheader("🤖 AI 分析結論")
st.info(f"""
本期表現最佳影片為【{best_video}】，觀看數達 {best_views:,}。
目前表現最好的平台為【{best_platform}】。
內容分類中【{best_category}】表現最佳，建議持續延伸。
""")

st.subheader("🎯 下週建議")
st.success(f"""
1. 延伸【{best_video}】做系列內容  
2. 主力經營【{best_platform}】  
3. 持續強化【{best_category}】主題  
4. 加強開頭 3 秒與 CTA 設計
""")

st.divider()

# CTA
st.subheader("🚀 合作方案")
st.success("""
📌 單次分析  
📌 月顧問  
📌 長期代操  
👉 歡迎合作
""")

# 專屬網址提示
st.subheader("🔗 客戶專屬網址")
st.code(f"?client={selected_client}")

st.subheader("📋 原始資料")
st.dataframe(df, width="stretch")