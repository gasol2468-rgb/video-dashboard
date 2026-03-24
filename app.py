import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

st.set_page_config(
    page_title="Philip Analytics Studio",
    layout="wide"
)

# =========================
# 品牌設定
# =========================
BRAND_NAME = "Philip Analytics Studio"
BRAND_SUBTITLE = "短影音內容分析顧問系統"
LINE_ID = "@135rt"
IG_ID = "@philip42"
BASE_URL = "https://video-dashboard-57vqejueptdmg9phqjztbo.streamlit.app"

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCKOspk1Ev6WEzdSGWWxNgDtfywFnayuER5OBUs5a20BmbiYVyUAiKcyFNCMM6VgKDAacVKRPu6pww/pub?output=csv"

# =========================
# 讀資料
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
# 客戶
# =========================
clients = df["client"].unique()
selected_client = st.sidebar.selectbox("選擇客戶", clients)
df = df[df["client"] == selected_client]

# =========================
# 計算
# =========================
total_views = int(df["views"].sum())
total_likes = int(df["likes"].sum())
total_comments = int(df["comments"].sum())
total_followers = int(df["followers_gained"].sum())

top3 = df.sort_values(by="views", ascending=False).head(3)
best_video = top3.iloc[0]["title"]
best_views = int(top3.iloc[0]["views"])

best_platform = df.groupby("platform")["views"].sum().idxmax()
best_category = df.groupby("category")["views"].sum().idxmax()

avg_engagement = round(
    ((df["likes"].sum() + df["comments"].sum()) / max(df["views"].sum(), 1)) * 100, 1
)

report_date = datetime.today().strftime("%Y-%m-%d")
full_url = f"{BASE_URL}/?client={selected_client}"

# =========================
# AI
# =========================
ai_summary = f"""
本期最佳影片為【{best_video}】，觀看數 {best_views:,}。
表現最佳平台為【{best_platform}】，
建議持續優化【{best_category}】內容。
"""

ai_actions = f"""
1. 延伸熱門影片主題  
2. 主攻 {best_platform}  
3. 強化前3秒吸引力  
4. 增加互動引導  
"""

# =========================
# PDF
# =========================
def create_pdf():
    buffer = io.BytesIO()

    pdfmetrics.registerFont(TTFont("NotoSansTC", "NotoSansTC-VariableFont_wght.ttf"))

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    styles["Title"].fontName = "NotoSansTC"
    styles["Normal"].fontName = "NotoSansTC"

    content = []
    content.append(Paragraph(f"{selected_client} 分析報告", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"觀看：{total_views:,}", styles["Normal"]))
    content.append(Paragraph(f"按讚：{total_likes:,}", styles["Normal"]))
    content.append(Paragraph(f"留言：{total_comments:,}", styles["Normal"]))
    content.append(Paragraph(f"粉絲：{total_followers:,}", styles["Normal"]))

    doc.build(content)
    buffer.seek(0)
    return buffer

pdf_file = create_pdf()

# =========================
# HERO
# =========================
st.title(f"{selected_client}｜短影音分析報告")
st.caption(f"{BRAND_SUBTITLE}｜{report_date}")

# =========================
# 成交區（🔥重點）
# =========================
st.markdown("""
### 為什麼你需要這份分析？

很多人不是沒拍影片，而是：

- 拍很多沒流量  
- 有流量沒轉單  
- 不知道哪支有效  

👉 我們幫你找出「可複製爆款」

---
""")

st.markdown("""
### 立即優化你的短影音

✔ 穩定流量  
✔ 提升轉單  
✔ 找到爆款  

📩 聯絡我：

LINE：@135rt  
IG：@philip42  

---
""")

# =========================
# KPI
# =========================
col1, col2, col3, col4 = st.columns(4)
col1.metric("觀看", total_views)
col2.metric("按讚", total_likes)
col3.metric("留言", total_comments)
col4.metric("粉絲", total_followers)

# =========================
# AI分析
# =========================
st.subheader("AI 分析")
st.write(ai_summary)

st.subheader("建議")
st.write(ai_actions)

# =========================
# 圖表
# =========================
fig = px.line(df, x="date", y="views")
st.plotly_chart(fig, width="stretch")

# =========================
# TOP3
# =========================
st.subheader("TOP 影片")
st.dataframe(top3)

# =========================
# PDF
# =========================
st.download_button(
    "下載報告",
    data=pdf_file,
    file_name="report.pdf"
)

# =========================
# 專屬連結
# =========================
st.code(full_url)