import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="短影音分析報告", layout="wide")

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
# Google Sheet CSV 連結
# =========================
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCKOspk1Ev6WEzdSGWWxNgDtfywFnayuER5OBUs5a20BmbiYVyUAiKcyFNCMM6VgKDAacVKRPu6pww/pub?output=csv"

# =========================
# 讀取資料
# =========================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    df["date"] = pd.to_datetime(df["date"])

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

    return df

df = load_data()

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

if st.sidebar.button("🔄 重新抓取 Google Sheet"):
    load_data.clear()
    st.rerun()

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
# 分析用資料
# =========================
best_platform = filtered_df.groupby("platform")["views"].sum().idxmax()
best_category = filtered_df.groupby("category")["views"].sum().idxmax()

top_views = filtered_df.sort_values(by="views", ascending=False).head(3)
top_growth = filtered_df.sort_values(by="growth_percent", ascending=False).head(3)

best_video = top_views.iloc[0]["title"]
best_video_views = int(top_views.iloc[0]["views"])

best_growth_video = top_growth.iloc[0]["title"]
best_growth_rate = float(top_growth.iloc[0]["growth_percent"])

best_engagement_row = filtered_df.sort_values(by="engagement_rate", ascending=False).iloc[0]
best_engagement_video = best_engagement_row["title"]
best_engagement_rate = float(best_engagement_row["engagement_rate"])

# =========================
# AI 分析文字
# =========================
ai_summary = f"""
本期整體來看，表現最好的平台是【{best_platform}】，目前最值得持續加碼的內容分類為【{best_category}】。
在所有影片中，【{best_video}】是本期觀看最高的影片，累積觀看達 {best_video_views:,}，
代表這類主題對受眾有明顯吸引力。

另一方面，【{best_growth_video}】的成長率達到 {best_growth_rate}% ，說明這支影片雖然不一定總觀看最高，
但近期擴散速度很快，適合優先延伸相似題材。

若從互動角度來看，【{best_engagement_video}】的互動率最高，達 {best_engagement_rate}%。
這表示它不只是被看到，還成功引發觀眾反應，適合作為未來內容腳本與開場設計的參考。
"""

ai_actions = f"""
1. 下週優先延伸【{best_video}】與【{best_growth_video}】相關題材，做成系列化內容。  
2. 發布重心建議放在【{best_platform}】，因為目前此平台帶來的流量最穩定。  
3. 內容方向建議持續聚焦【{best_category}】，並加入更多問題式開場與留言引導。  
4. 針對【{best_engagement_video}】拆解它的標題、開頭與內容節奏，複製成功要素。  
5. 若要放大成交，建議把高互動影片導入產品介紹、私訊引導與優惠 CTA。  
"""

# =========================
# 頁首
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
# AI 分析區
# =========================
st.markdown("## 🤖 AI 自動分析摘要")
st.info(ai_summary)

st.markdown("## 🎯 AI 下週行動建議")
st.success(ai_actions)

st.divider()

# =========================
# 顧問結論區
# =========================
st.markdown("## 🧠 自動分析結論")
st.success(f"目前最佳平台為【{best_platform}】，最值得持續投入的內容類型為【{best_category}】。")
st.info(f"本期最高觀看影片為【{best_video}】，累積觀看 {best_video_views:,}。")
st.warning(f"成長最快影片為【{best_growth_video}】，成長率達 {best_growth_rate}% 。")
st.write(f"互動率最高影片為 **{best_engagement_video}**，互動率為 **{best_engagement_rate}%**。")

st.divider()

# =========================
# 商業建議
# =========================
st.markdown("## 💰 商業變現建議")
st.success("""
✔ 建議可導入產品：高山茶、茶包、禮盒、節慶組合  
✔ 建議內容形式：開箱、教學、比較、情境故事  
✔ 建議轉單流程：短影音吸引 → 私訊詢問 → 導購成交  
✔ 建議對爆款影片進行小額廣告測試，放大自然流量成果  
""")

# =========================
# 服務方案
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
# 成交 CTA
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
    st.plotly_chart(fig_views, use_container_width=True)

with chart_col2:
    category_summary = filtered_df.groupby("category", as_index=False)["views"].sum()
    fig_category = px.bar(
        category_summary,
        x="category",
        y="views",
        title="各分類觀看表現"
    )
    st.plotly_chart(fig_category, use_container_width=True)

st.divider()

# =========================
# 原始資料
# =========================
st.markdown("## 📋 原始資料明細")
st.dataframe(filtered_df, use_container_width=True)