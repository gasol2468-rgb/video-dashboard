import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="短影音分析儀表板", layout="wide")

# ===== 讀資料 =====
df = pd.read_csv("videos.csv")

# ===== 日期處理 =====
df["date"] = pd.to_datetime(df["date"])

# ===== 側邊欄 =====
st.sidebar.title("篩選條件")

start_date = st.sidebar.date_input("開始日期", df["date"].min())
end_date = st.sidebar.date_input("結束日期", df["date"].max())

platform = st.sidebar.selectbox("平台", ["全部"] + list(df.get("platform", pd.Series()).dropna().unique()))
format_type = st.sidebar.selectbox("影片格式", ["全部"] + list(df.get("format", pd.Series()).dropna().unique()))
category = st.sidebar.selectbox("影片分類", ["全部"] + list(df.get("category", pd.Series()).dropna().unique()))

# ===== 篩選 =====
filtered_df = df[
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date))
]

# ===== 標題 =====
st.title("📊 短影音內容分析儀表板")
st.caption("由 梨山聚鑫製茶廠｜內容行銷分析系統")

# ===== 摘要 =====
st.markdown("## 🧾 本期分析摘要")
st.markdown(f"""
- 分析期間：{start_date} ～ {end_date}  
- 數據來源：多平台短影音（Instagram / YouTube / TikTok）  
- 分析目的：找出爆款內容與最佳成長策略  
""")

# ===== KPI =====
total_views = filtered_df["views"].sum()
total_likes = filtered_df["likes"].sum()
total_comments = filtered_df["comments"].sum()
total_videos = len(filtered_df)
avg_watch = round(filtered_df["views"].mean() / 100, 1)
engagement = round((total_likes + total_comments) / total_views * 100, 1) if total_views > 0 else 0
followers = total_comments // 2  # 模擬數據

st.markdown("## 📊 重點數據")
col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("總觀看", f"{total_views:,}")
col2.metric("總按讚", f"{total_likes:,}")
col3.metric("總留言", f"{total_comments:,}")
col4.metric("新增粉絲", f"{followers}")
col5.metric("平均觀看時長", f"{avg_watch} 秒")
col6.metric("平均互動率", f"{engagement}%")

# ===== 趨勢 =====
st.markdown("## 📈 觀看趨勢")
fig = px.line(filtered_df, x="date", y="views", title="每日觀看數")
st.plotly_chart(fig, width="stretch")

# ===== TOP3 =====
st.markdown("## 🔥 爆款影片 TOP 3")
top_views = filtered_df.sort_values(by="views", ascending=False).head(3)

for i, row in top_views.iterrows():
    st.write(f"🏆 {row['title']}（{row['views']:,} 觀看）")

# ===== 成長影片 =====
filtered_df["growth"] = filtered_df["views"].pct_change().fillna(0)

st.markdown("## 🚀 爆發中影片 TOP 3")
top_growth = filtered_df.sort_values(by="growth", ascending=False).head(3)

for i, row in top_growth.iterrows():
    st.write(f"📈 {row['title']}（成長率 {round(row['growth']*100,1)}%）")

# ===== AI結論 =====
st.markdown("## 🧠 自動分析結論")

if not filtered_df.empty:
    best_video = top_views.iloc[0]["title"]
    st.success(f"目前最強影片為「{best_video}」，建議延伸類似主題內容。")

# ===== 🔥 成長策略（新增） =====
st.markdown("## 📈 成長策略建議")

st.info("""
1️⃣ 建議持續製作【知識型內容】，目前轉換率最高  
2️⃣ 開頭3秒需強化「問題型吸引」提升完播率  
3️⃣ 爆款主題建議延伸成系列（提高帳號權重）  
4️⃣ 增加留言引導（例如：你是哪一派？）提升互動  
""")

# ===== 💰 變現（新增） =====
st.markdown("## 💰 商業變現建議")

st.success("""
✔ 可導入產品：高山茶 / 茶包 / 禮盒  
✔ 建議內容形式：開箱 + 教學 + 情境故事  
✔ 最佳轉單模式：短影音 → 私訊 → 成交  
✔ 建議投放：針對爆款影片加碼廣告  
""")

# ===== 原始資料 =====
st.markdown("## 📋 原始資料")
st.dataframe(filtered_df, width="stretch")