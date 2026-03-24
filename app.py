import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="影片分析儀表板", layout="wide")

st.title("📊 短影音內容分析儀表板")

st.caption("由 梨山聚鑫製茶廠｜內容行銷分析系統")

st.markdown("""
### 🧾 本期分析摘要
- 分析期間：依目前篩選條件
- 數據來源：多平台短影音（Instagram / YouTube / TikTok）
- 分析目的：找出爆款內容與最佳成長策略
""")

# 讀取資料
df = pd.read_csv("videos.csv")
df["date"] = pd.to_datetime(df["date"])
df["publish_date"] = pd.to_datetime(df["publish_date"])

# 計算欄位
df["growth"] = df["views"] - df["prev_views"]
df["growth_rate"] = (df["growth"] / df["prev_views"] * 100).round(1)
df["engagement"] = df["likes"] + df["comments"] + df["shares"] + df["saves"]
df["engagement_rate"] = (df["engagement"] / df["views"] * 100).round(1)

# 側邊欄
st.sidebar.header("篩選條件")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date = st.sidebar.date_input("開始日期", min_date)
end_date = st.sidebar.date_input("結束日期", max_date)

platform_list = ["全部"] + sorted(df["platform"].unique().tolist())
selected_platform = st.sidebar.selectbox("平台", platform_list)

format_list = ["全部"] + sorted(df["format"].unique().tolist())
selected_format = st.sidebar.selectbox("影片格式", format_list)

category_list = ["全部"] + sorted(df["category"].unique().tolist())
selected_category = st.sidebar.selectbox("影片分類", category_list)

# 篩選
filtered_df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
]

if selected_platform != "全部":
    filtered_df = filtered_df[filtered_df["platform"] == selected_platform]

if selected_format != "全部":
    filtered_df = filtered_df[filtered_df["format"] == selected_format]

if selected_category != "全部":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

# KPI
total_views = int(filtered_df["views"].sum()) if len(filtered_df) > 0 else 0
total_likes = int(filtered_df["likes"].sum()) if len(filtered_df) > 0 else 0
total_comments = int(filtered_df["comments"].sum()) if len(filtered_df) > 0 else 0
total_followers = int(filtered_df["followers_gained"].sum()) if len(filtered_df) > 0 else 0
avg_watch_time = round(filtered_df["watch_time_seconds"].mean(), 1) if len(filtered_df) > 0 else 0
avg_engagement_rate = round(filtered_df["engagement_rate"].mean(), 1) if len(filtered_df) > 0 else 0

st.subheader("重點數據")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("總觀看", f"{total_views:,}")
k2.metric("總按讚", f"{total_likes:,}")
k3.metric("總留言", f"{total_comments:,}")
k4.metric("新增粉絲", f"{total_followers:,}")
k5.metric("平均觀看時長", f"{avg_watch_time} 秒")
k6.metric("平均互動率", f"{avg_engagement_rate}%")

st.divider()

# 🧠 自動分析結論
st.subheader("🧠 自動分析結論")

if len(filtered_df) > 0:
    best_platform = filtered_df.groupby("platform")["views"].sum().idxmax()
    best_category = filtered_df.groupby("category")["views"].sum().idxmax()

    best_growth_video = filtered_df.sort_values(by="growth_rate", ascending=False).iloc[0]
    best_engagement_video = filtered_df.sort_values(by="engagement_rate", ascending=False).iloc[0]
    best_followers_video = filtered_df.sort_values(by="followers_gained", ascending=False).iloc[0]

    st.success(f"目前最佳平台為【{best_platform}】，建議持續投入【{best_category}】類型內容。")

    st.info(f"成長最快影片：【{best_growth_video['title']}】（{best_growth_video['growth_rate']}%）")

    st.warning(f"互動率最高影片：【{best_engagement_video['title']}】（{best_engagement_video['engagement_rate']}%）")

    st.write(f"最能帶粉影片：**{best_followers_video['title']}**（+{best_followers_video['followers_gained']} 粉絲）")

    st.markdown("## 📊 綜合策略建議")
    st.write("1. 持續複製爆款內容形式")
    st.write("2. 加強影片前3秒吸引力")
    st.write("3. 提升留言與收藏設計")
    st.write("4. 針對高成長主題做系列內容")

else:
    st.error("沒有資料")

st.divider()

# 爆款 & 爆發
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("🔥 爆款影片 TOP 3")
    top3 = filtered_df.sort_values(by="views", ascending=False).head(3)

    for i, row in enumerate(top3.itertuples(), start=1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        st.markdown(f"{medal} **{row.title}**")
        st.write(f"觀看數：{row.views:,}")
        st.write("---")

with right_col:
    st.subheader("🚀 爆發中影片 TOP 3")
    growth_top3 = filtered_df.sort_values(by="growth_rate", ascending=False).head(3)

    for i, row in enumerate(growth_top3.itertuples(), start=1):
        st.markdown(f"{i}. {row.title}")
        st.write(f"成長率：{row.growth_rate}%")
        st.write("---")

st.divider()

# 圖表
col1, col2 = st.columns(2)

with col1:
    fig = px.line(filtered_df, x="date", y="views", color="platform", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    cat = filtered_df.groupby("category", as_index=False)["views"].sum()
    fig2 = px.bar(cat, x="category", y="views")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("原始資料")
st.dataframe(filtered_df, use_container_width=True)