import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="短影音內容成效分析報告", layout="wide")

# =========================
# 基本設定
# =========================
CLIENT_NAME = "梨山聚鑫製茶廠"
REPORT_TITLE = "短影音內容成效分析報告"
AUTHOR_NAME = "ZiYi Media Lab"
SERVICE_TYPE = "內容分析顧問版"

CONTACT_NAME = "梓逸"
CONTACT_LINE = "@your_line_id"
CONTACT_INSTAGRAM = "@your_instagram"
CONTACT_EMAIL = "your_email@example.com"

# =========================
# 讀取資料
# =========================
df = pd.read_csv("videos.csv")
df["date"] = pd.to_datetime(df["date"])

# 如果缺欄位就自動補
defaults = {
    "platform": "Instagram",
    "format": "Reels",
    "category": "知識",
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "saves": 0,
    "watch_time_seconds": 20,
    "followers_gained": 0,
}
for col, default_value in defaults.items():
    if col not in df.columns:
        df[col] = default_value

# =========================
# 側邊欄篩選
# =========================
st.sidebar.title("篩選條件")

start_date = st.sidebar.date_input("開始日期", df["date"].min().date())
end_date = st.sidebar.date_input("結束日期", df["date"].max().date())

platform_options = ["全部"] + sorted(df["platform"].dropna().unique().tolist())
format_options = ["全部"] + sorted(df["format"].dropna().unique().tolist())
category_options = ["全部"] + sorted(df["category"].dropna().unique().tolist())

selected_platform = st.sidebar.selectbox("平台", platform_options)
selected_format = st.sidebar.selectbox("影片格式", format_options)
selected_category = st.sidebar.selectbox("影片分類", category_options)

# =========================
# 篩選資料
# =========================
filtered_df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
].copy()

if selected_platform != "全部":
    filtered_df = filtered_df[filtered_df["platform"] == selected_platform]

if selected_format != "全部":
    filtered_df = filtered_df[filtered_df["format"] == selected_format]

if selected_category != "全部":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

if filtered_df.empty:
    st.title(f"📊 {CLIENT_NAME}｜{REPORT_TITLE}")
    st.warning("目前篩選條件下沒有資料，請調整左側條件。")
    st.stop()

# =========================
# 計算欄位
# =========================
if "prev_views" not in filtered_df.columns:
    filtered_df["prev_views"] = filtered_df["views"].shift(1).fillna(filtered_df["views"])

filtered_df["engagement_count"] = (
    filtered_df["likes"] + filtered_df["comments"] + filtered_df["shares"] + filtered_df["saves"]
)

filtered_df["engagement_rate"] = (
    filtered_df["engagement_count"] / filtered_df["views"] * 100
).round(1)

filtered_df["growth_value"] = filtered_df["views"] - filtered_df["prev_views"]
filtered_df["growth_percent"] = (
    (filtered_df["growth_value"] / filtered_df["prev_views"].replace(0, 1)) * 100
).round(1)

# =========================
# KPI
# =========================
total_views = int(filtered_df["views"].sum())
total_likes = int(filtered_df["likes"].sum())
total_comments = int(filtered_df["comments"].sum())
total_followers = int(filtered_df["followers_gained"].sum())
avg_watch_time = round(filtered_df["watch_time_seconds"].mean(), 1)
avg_engagement_rate = round(filtered_df["engagement_rate"].mean(), 1)

today = datetime.today().strftime("%Y-%m-%d")

# =========================
# 報告抬頭
# =========================
st.title(f"📊 {CLIENT_NAME}｜{REPORT_TITLE}")
st.caption(f"製作單位：{AUTHOR_NAME}｜方案類型：{SERVICE_TYPE}")

st.markdown("## 🧾 客戶報告資訊")
info_col1, info_col2, info_col3 = st.columns(3)
info_col1.write(f"**客戶名稱：** {CLIENT_NAME}")
info_col2.write(f"**報告日期：** {today}")
info_col3.write(f"**分析區間：** {start_date} ～ {end_date}")

st.markdown("""
## 📌 本期分析目的
- 盤點短影音整體表現
- 找出高觀看與高成長內容
- 提出下一階段內容優化方向
- 作為品牌內容策略與轉單規劃依據
""")

st.divider()

# =========================
# KPI 區
# =========================
st.markdown("## 📊 重點數據總覽")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("總觀看", f"{total_views:,}")
k2.metric("總按讚", f"{total_likes:,}")
k3.metric("總留言", f"{total_comments:,}")
k4.metric("新增粉絲", f"{total_followers:,}")
k5.metric("平均觀看時長", f"{avg_watch_time} 秒")
k6.metric("平均互動率", f"{avg_engagement_rate}%")

st.divider()

# =========================
# 自動分析結論
# =========================
best_platform = filtered_df.groupby("platform")["views"].sum().idxmax()
best_category = filtered_df.groupby("category")["views"].sum().idxmax()

top_views = filtered_df.sort_values(by="views", ascending=False).head(3)
top_growth = filtered_df.sort_values(by="growth_percent", ascending=False).head(3)

best_video = top_views.iloc[0]["title"]
best_video_views = int(top_views.iloc[0]["views"])

best_growth_video = top_growth.iloc[0]["title"]
best_growth_rate = float(top_growth.iloc[0]["growth_percent"])

best_engagement_video = filtered_df.sort_values(by="engagement_rate", ascending=False).iloc[0]["title"]
best_engagement_rate = float(
    filtered_df.sort_values(by="engagement_rate", ascending=False).iloc[0]["engagement_rate"]
)

st.markdown("## 🧠 自動分析結論")
st.success(f"目前最佳平台為【{best_platform}】，最值得持續投入的內容類型為【{best_category}】。")
st.info(f"本期最高觀看影片為【{best_video}】，累積觀看 {best_video_views:,}。")
st.warning(f"成長最快影片為【{best_growth_video}】，成長率達 {best_growth_rate}% 。")
st.write(f"互動率最高影片為 **{best_engagement_video}**，互動率為 **{best_engagement_rate}%**。")

st.divider()

# =========================
# 成長策略建議
# =========================
st.markdown("## 📈 成長策略建議")
st.info(f"""
1️⃣ 建議持續加碼【{best_category}】類型內容，因為目前整體表現最佳。  
2️⃣ 建議優先經營【{best_platform}】平台，作為主要流量來源。  
3️⃣ 建議延伸【{best_video}】與【{best_growth_video}】的相似主題，建立系列化內容。  
4️⃣ 建議優化影片前 3 秒，增加問題式開頭與互動引導，提高停留與留言。  
""")

# =========================
# 商業變現建議
# =========================
st.markdown("## 💰 商業變現建議")
st.success("""
✔ 建議可導入產品：高山茶、茶包、禮盒、節慶組合  
✔ 建議內容形式：開箱、教學、比較、情境故事  
✔ 建議轉單流程：短影音吸引 → 私訊詢問 → 導購成交  
✔ 建議對爆款影片進行小額廣告測試，放大自然流量成果  
""")

# =========================
# 顧問服務方案
# =========================
st.markdown("## 💼 顧問服務方案")

plan1, plan2, plan3 = st.columns(3)

with plan1:
    st.markdown("### 📄 單次分析報告")
    st.write("適合想先了解帳號狀況的品牌")
    st.write("- 數據盤點")
    st.write("- 爆款分析")
    st.write("- 成長建議")
    st.write("**NT$ 3,000 / 次**")

with plan2:
    st.markdown("### 📅 每月內容顧問")
    st.write("適合穩定經營短影音的品牌")
    st.write("- 每月分析報告")
    st.write("- 題材建議")
    st.write("- 成長策略")
    st.write("**NT$ 8,000 / 月**")

with plan3:
    st.markdown("### 🎬 短影音代操")
    st.write("適合想直接放大流量與轉單的品牌")
    st.write("- 腳本規劃")
    st.write("- 內容策略")
    st.write("- 代操優化")
    st.write("**NT$ 20,000 起 / 月**")

st.divider()

# =========================
# 成交 CTA 區
# =========================
st.markdown("## 🚀 下一步合作方式")
st.warning("""
如果你希望把短影音變成穩定流量與訂單，現在就可以開始合作。
我們可以依照你的品牌需求，提供：
- 單次分析
- 每月顧問
- 長期代操
""")

contact_col1, contact_col2 = st.columns(2)

with contact_col1:
    st.markdown("### 📩 聯絡方式")
    st.write(f"**聯絡人：** {CONTACT_NAME}")
    st.write(f"**LINE：** {CONTACT_LINE}")
    st.write(f"**Instagram：** {CONTACT_INSTAGRAM}")
    st.write(f"**Email：** {CONTACT_EMAIL}")

with contact_col2:
    st.markdown("### ✅ 適合合作對象")
    st.write("- 想提升短影音流量的品牌")
    st.write("- 想把內容變成成交工具的商家")
    st.write("- 想建立自媒體帶貨系統的團隊")
    st.write("- 想做數據化內容經營的公司")

st.success("👉 看完這份報告後，若你想要我幫你做專屬版本，歡迎直接聯絡。")

st.divider()

# =========================
# 排行榜
# =========================
left_col, right_col = st.columns(2)

with left_col:
    st.markdown("## 🔥 爆款影片 TOP 3")
    medals = ["🥇", "🥈", "🥉"]
    for idx, row in enumerate(top_views.itertuples(), start=0):
        st.write(f"{medals[idx]} {row.title}")
        st.write(f"觀看數：{int(row.views):,}")
        st.write("---")

with right_col:
    st.markdown("## 🚀 爆發中影片 TOP 3")
    for idx, row in enumerate(top_growth.itertuples(), start=1):
        st.write(f"{idx}. {row.title}")
        st.write(f"成長率：{row.growth_percent}%")
        st.write("---")

st.divider()

# =========================
# 圖表
# =========================
st.markdown("## 📈 數據圖表分析")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig_views = px.line(
        filtered_df,
        x="date",
        y="views",
        color="platform",
        markers=True,
        title="每日觀看趨勢"
    )
    st.plotly_chart(fig_views, width="stretch")

with chart_col2:
    category_summary = filtered_df.groupby("category", as_index=False)["views"].sum()
    fig_category = px.bar(
        category_summary,
        x="category",
        y="views",
        title="各分類觀看表現"
    )
    st.plotly_chart(fig_category, width="stretch")

st.divider()

# =========================
# 原始資料
# =========================
st.markdown("## 📋 原始資料明細")
st.dataframe(filtered_df, width="stretch")