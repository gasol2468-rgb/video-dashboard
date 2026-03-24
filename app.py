import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="短影音分析系統", layout="wide")

# =========================
# 🔥 Google Sheet CSV
# =========================
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCKOspk1Ev6WEzdSGWWxNgDtfywFnayuER5OBUs5a20BmbiYVyUAiKcyFNCMM6VgKDAacVKRPu6pww/pub?output=csv"

# 👉 改成你的部署網址（很重要）
BASE_URL = "https://video-dashboard-xxx.streamlit.app"

# =========================
# 🔥 讀資料
# =========================
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
# 🔥 URL 客戶參數
# =========================
query_params = st.query_params
url_client = query_params.get("client", None)

clients = df["client"].dropna().unique().tolist()

if url_client and url_client in clients:
    selected_client = url_client
else:
    selected_client = clients[0] if clients else "預設客戶"

# =========================
# Sidebar
# =========================
st.sidebar.title("客戶選擇")

selected_client = st.sidebar.selectbox(
    "選擇客戶",
    clients,
    index=clients.index(selected_client) if selected_client in clients else 0
)

# 同步網址
st.query_params["client"] = selected_client

df = df[df["client"] == selected_client].copy()

# =========================
# 日期篩選
# =========================
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

# =========================
# KPI
# =========================
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

# =========================
# 📈 圖表
# =========================
st.subheader("📈 觀看趨勢")
fig = px.line(df, x="date", y="views", color="platform", markers=True)
st.plotly_chart(fig, width="stretch")

st.divider()

# =========================
# 🔥 TOP 影片
# =========================
st.subheader("🔥 爆款影片 TOP 3")

top3 = df.sort_values(by="views", ascending=False).head(3)

for i, row in enumerate(top3.itertuples(), 1):
    st.write(f"{i}. {row.title}（{int(row.views):,}觀看）")

st.divider()

# =========================
# 🤖 AI 分析
# =========================
best_video = top3.iloc[0]["title"]
best_views = int(top3.iloc[0]["views"])
best_platform = df.groupby("platform")["views"].sum().idxmax()
best_category = df.groupby("category")["views"].sum().idxmax()

st.subheader("🤖 AI 分析結論")

st.info(f"""
本期表現最佳影片為【{best_video}】，觀看數達 {best_views:,}  
最佳平台為【{best_platform}】  
最佳內容類型為【{best_category}】
""")

st.subheader("🎯 下週建議")

st.success(f"""
1. 延伸【{best_video}】做系列內容  
2. 主力經營【{best_platform}】  
3. 強化【{best_category}】主題  
4. 開頭3秒優化  
5. 增加CTA引導留言
""")

st.divider()

# =========================
# 💰 商業建議
# =========================
st.subheader("💰 商業變現建議")

st.success("""
✔ 導入商品（茶葉 / 禮盒 / 茶包）  
✔ 做開箱 / 教學 / 比較內容  
✔ 建立私訊成交流程  
✔ 放大爆款影片（投廣告）
""")

st.divider()

# =========================
# 🚀 成交區
# =========================
st.subheader("🚀 合作方案")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📄 單次分析")
    st.write("NT$ 3,000")

with col2:
    st.markdown("### 📅 月顧問")
    st.write("NT$ 8,000")

with col3:
    st.markdown("### 🎬 代操")
    st.write("NT$ 20,000 起")

st.divider()

# =========================
# 🔗 專屬連結（升級版）
# =========================
st.subheader("🔗 客戶專屬報表")

full_url = f"{BASE_URL}/?client={selected_client}"

st.success("此連結為客戶專屬報表，可直接分享")

st.code(full_url)

st.divider()

# =========================
# 📩 CTA
# =========================
st.subheader("📩 聯絡我")

st.warning("""
LINE：@135rt  
IG：@_philip42_  
👉 想讓短影音變現，直接聯絡
""")

st.divider()

# =========================
# 📋 原始資料
# =========================
st.subheader("📋 原始資料")
st.dataframe(df, width="stretch")