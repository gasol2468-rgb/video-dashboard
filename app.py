import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

st.set_page_config(page_title="Philip 短影音分析系統", layout="wide")

# =========================
# 🔥 你的設定（已幫你填好）
# =========================
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCKOspk1Ev6WEzdSGWWxNgDtfywFnayuER5OBUs5a20BmbiYVyUAiKcyFNCMM6VgKDAacVKRPu6pww/pub?output=csv"
BASE_URL = "https://video-dashboard-xxx.streamlit.app"
LINE_ID = "@135rt"
IG_ID = "@philip42"

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
# URL 客戶
# =========================
query_params = st.query_params
url_client = query_params.get("client", None)

clients = df["client"].dropna().unique().tolist()

if url_client and url_client in clients:
    selected_client = url_client
else:
    selected_client = clients[0]

# =========================
# Sidebar
# =========================
st.sidebar.title("客戶選擇")

selected_client = st.sidebar.selectbox(
    "選擇客戶",
    clients,
    index=clients.index(selected_client)
)

st.query_params["client"] = selected_client

df = df[df["client"] == selected_client].copy()

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
# 圖表
# =========================
st.subheader("📈 觀看趨勢")
fig = px.line(df, x="date", y="views", color="platform")
st.plotly_chart(fig, width="stretch")

st.divider()

# =========================
# TOP影片
# =========================
st.subheader("🔥 爆款影片 TOP 3")

top3 = df.sort_values(by="views", ascending=False).head(3)

for i, row in enumerate(top3.itertuples(), 1):
    st.write(f"{i}. {row.title}（{int(row.views):,}觀看）")

st.divider()

# =========================
# AI 分析
# =========================
best_video = top3.iloc[0]["title"]
best_views = int(top3.iloc[0]["views"])
best_platform = df.groupby("platform")["views"].sum().idxmax()
best_category = df.groupby("category")["views"].sum().idxmax()

ai_summary = f"""
最佳影片：{best_video}（{best_views:,}觀看）  
最佳平台：{best_platform}  
最佳類型：{best_category}
"""

st.subheader("🤖 AI 分析結論")
st.info(ai_summary)

st.subheader("🎯 下週建議")
st.success("""
1. 延伸爆款影片做系列  
2. 強化開頭3秒  
3. 增加CTA引導  
4. 放大高表現內容  
""")

st.divider()

# =========================
# 💰 成交區
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
# 📄 PDF報告
# =========================
def create_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph(f"{selected_client} 短影音分析報告", styles["Title"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"日期：{datetime.today().strftime('%Y-%m-%d')}", styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("【數據摘要】", styles["Heading2"]))
    content.append(Paragraph(f"總觀看：{total_views:,}", styles["Normal"]))
    content.append(Paragraph(f"總按讚：{total_likes:,}", styles["Normal"]))
    content.append(Paragraph(f"總留言：{total_comments:,}", styles["Normal"]))
    content.append(Paragraph(f"新增粉絲：{total_followers:,}", styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("【AI分析】", styles["Heading2"]))
    content.append(Paragraph(ai_summary, styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("【聯絡方式】", styles["Heading2"]))
    content.append(Paragraph(f"LINE：{LINE_ID}", styles["Normal"]))
    content.append(Paragraph(f"IG：{IG_ID}", styles["Normal"]))

    doc.build(content)
    buffer.seek(0)
    return buffer

pdf_file = create_pdf()

st.download_button(
    label="📄 下載PDF報告",
    data=pdf_file,
    file_name=f"{selected_client}_分析報告.pdf",
    mime="application/pdf"
)

st.divider()

# =========================
# 🔗 專屬連結
# =========================
full_url = f"{BASE_URL}/?client={selected_client}"

st.subheader("🔗 客戶專屬報表")
st.code(full_url)

st.divider()

# =========================
# 📩 聯絡
# =========================
st.subheader("📩 聯絡我")

st.warning(f"""
LINE：{LINE_ID}  
IG：{IG_ID}  
👉 想讓短影音變現，直接聯絡
""")

st.divider()

# =========================
# 原始資料
# =========================
st.subheader("📋 原始資料")
st.dataframe(df, width="stretch")