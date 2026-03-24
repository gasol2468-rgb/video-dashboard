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
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# 品牌設定
# =========================
BRAND_NAME = "Philip Analytics Studio"
BRAND_SUBTITLE = "短影音內容分析顧問系統"
LINE_ID = "@135rt"
IG_ID = "@philip42"
BASE_URL = "https://video-dashboard-xxx.streamlit.app"

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCKOspk1Ev6WEzdSGWWxNgDtfywFnayuER5OBUs5a20BmbiYVyUAiKcyFNCMM6VgKDAacVKRPu6pww/pub?output=csv"

# =========================
# 樣式
# =========================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero-box {
    padding: 1.4rem 1.6rem;
    border: 1px solid rgba(120,120,120,0.2);
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(240,244,248,0.9), rgba(255,255,255,0.95));
    margin-bottom: 1rem;
}
.section-box {
    padding: 1rem 1.2rem;
    border: 1px solid rgba(120,120,120,0.18);
    border-radius: 16px;
    background: rgba(255,255,255,0.88);
    margin-bottom: 1rem;
}
.small-muted {
    color: #666;
    font-size: 0.92rem;
}
.big-number {
    font-size: 1.8rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

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
# 客戶網址參數
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
st.sidebar.markdown(f"## {BRAND_NAME}")
st.sidebar.caption(BRAND_SUBTITLE)

selected_client = st.sidebar.selectbox(
    "選擇客戶",
    clients,
    index=clients.index(selected_client)
)

st.query_params["client"] = selected_client

df = df[df["client"] == selected_client].copy()

start_date = st.sidebar.date_input("開始日期", df["date"].min().date())
end_date = st.sidebar.date_input("結束日期", df["date"].max().date())

df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
].copy()

if st.sidebar.button("重新抓取最新資料"):
    load_data.clear()
    st.rerun()

if df.empty:
    st.warning("目前沒有資料")
    st.stop()

# =========================
# 核心計算
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

ai_summary = f"""
本期最高表現影片為【{best_video}】，累積觀看 {best_views:,}。
整體流量表現最好的平台是【{best_platform}】，
而最值得持續投入的內容主題為【{best_category}】。
建議以高表現主題為核心，延伸系列內容，並優先在最佳平台持續加碼。
"""

ai_actions = f"""
1. 延伸【{best_video}】做系列內容  
2. 持續加碼【{best_platform}】平台  
3. 聚焦【{best_category}】內容方向  
4. 強化影片前 3 秒吸引力  
5. 增加留言與私訊 CTA 設計  
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
    styles["Heading2"].fontName = "NotoSansTC"

    content = []
    content.append(Paragraph(f"{selected_client} 短影音分析報告", styles["Title"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"報告日期：{report_date}", styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("【重點數據】", styles["Heading2"]))
    content.append(Paragraph(f"總觀看：{total_views:,}", styles["Normal"]))
    content.append(Paragraph(f"總按讚：{total_likes:,}", styles["Normal"]))
    content.append(Paragraph(f"總留言：{total_comments:,}", styles["Normal"]))
    content.append(Paragraph(f"新增粉絲：{total_followers:,}", styles["Normal"]))
    content.append(Paragraph(f"整體互動率：{avg_engagement}%", styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("【AI 分析摘要】", styles["Heading2"]))
    content.append(Paragraph(ai_summary.replace("\n", "<br/>"), styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("【下階段建議】", styles["Heading2"]))
    content.append(Paragraph(ai_actions.replace("\n", "<br/>"), styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("【聯絡方式】", styles["Heading2"]))
    content.append(Paragraph(f"LINE：{LINE_ID}", styles["Normal"]))
    content.append(Paragraph(f"IG：{IG_ID}", styles["Normal"]))

    doc.build(content)
    buffer.seek(0)
    return buffer

pdf_file = create_pdf()

# =========================
# Hero 區
# =========================
st.markdown(f"""
<div class="hero-box">
    <div class="small-muted">{BRAND_NAME}</div>
    <h1 style="margin-bottom:0.3rem;">{selected_client}｜短影音內容分析報告</h1>
    <div class="small-muted">
        {BRAND_SUBTITLE}<br>
        報告日期：{report_date}　｜　分析區間：{start_date} ～ {end_date}
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# KPI 區
# =========================
st.markdown("### 核心指標")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("總觀看", f"{total_views:,}")
k2.metric("總按讚", f"{total_likes:,}")
k3.metric("總留言", f"{total_comments:,}")
k4.metric("新增粉絲", f"{total_followers:,}")
k5.metric("互動率", f"{avg_engagement}%")

st.divider()

# =========================
# AI + 建議
# =========================
c1, c2 = st.columns([1.2, 1])

with c1:
    st.markdown("### AI 分析摘要")
    st.markdown(f"""
    <div class="section-box">
    {ai_summary.replace(chr(10), "<br>")}
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("### 下階段建議")
    st.markdown(f"""
    <div class="section-box">
    {ai_actions.replace(chr(10), "<br>")}
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================
# 圖表區
# =========================
g1, g2 = st.columns(2)

with g1:
    st.markdown("### 觀看趨勢")
    fig = px.line(df, x="date", y="views", color="platform", markers=True)
    st.plotly_chart(fig, width="stretch")

with g2:
    st.markdown("### 爆款影片 TOP 3")
    for i, row in enumerate(top3.itertuples(), 1):
        st.markdown(f"""
        <div class="section-box">
            <div class="big-number">#{i}</div>
            <div><strong>{row.title}</strong></div>
            <div class="small-muted">觀看數：{int(row.views):,}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# =========================
# 服務方案
# =========================
st.markdown("### 合作方案")

p1, p2, p3 = st.columns(3)

with p1:
    st.markdown("""
    <div class="section-box">
        <h4>單次分析</h4>
        <div class="small-muted">適合先了解帳號狀況</div>
        <p>NT$ 3,000</p>
    </div>
    """, unsafe_allow_html=True)

with p2:
    st.markdown("""
    <div class="section-box">
        <h4>月顧問</h4>
        <div class="small-muted">適合穩定優化內容</div>
        <p>NT$ 8,000</p>
    </div>
    """, unsafe_allow_html=True)

with p3:
    st.markdown("""
    <div class="section-box">
        <h4>代操服務</h4>
        <div class="small-muted">適合想直接放大流量與成交</div>
        <p>NT$ 20,000 起</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================
# 專屬連結 / PDF / 聯絡
# =========================
a1, a2 = st.columns(2)

with a1:
    st.markdown("### 客戶專屬連結")
    st.code(full_url)

    st.download_button(
        label="下載 PDF 報告",
        data=pdf_file,
        file_name=f"{selected_client}_分析報告.pdf",
        mime="application/pdf"
    )

with a2:
    st.markdown("### 聯絡方式")
    st.markdown(f"""
    <div class="section-box">
        LINE：{LINE_ID}<br>
        IG：{IG_ID}<br><br>
        想把短影音變成穩定流量與訂單，歡迎直接聯絡。
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================
# 原始資料
# =========================
st.markdown("### 原始資料")
st.dataframe(df, width="stretch")