import os
import json
import re
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from openai import OpenAI

# =========================
# 基本設定
# =========================
st.set_page_config(
    page_title="茶葉創作者總控台",
    page_icon="🎬",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

OVERRIDE_PATH = DATA_DIR / "content_override.json"
NOTES_PATH = DATA_DIR / "creator_notes.json"

# 你可以直接改這裡，或用 export 設環境變數 YOUTUBE_API_KEY = 
""import os

YOUTUBE_API_KEY = os.getenv("AIzaSyDGsiqVfahPsplQ2QAlVx-LNMSDUwCWnbc", "")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "UCU6zSdI-U_WKMrAUt5JuePA")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# =========================
# 樣式
# =========================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(59,130,246,0.12), transparent 22%),
        radial-gradient(circle at top right, rgba(16,185,129,0.08), transparent 18%),
        linear-gradient(180deg, #04070c 0%, #0b1220 45%, #0f172a 100%);
    color: #f8fafc;
}

.block-container {
    max-width: 1280px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 30px;
    padding: 34px;
    color: white;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 24px 48px rgba(0,0,0,0.30);
    margin-bottom: 22px;
}

.hero-kicker {
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #bfdbfe;
    margin-bottom: 10px;
}

.hero-title {
    font-size: 40px;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 12px;
}

.hero-sub {
    color: #dbeafe;
    font-size: 15px;
    line-height: 1.95;
}

.section-title {
    font-size: 24px;
    font-weight: 800;
    color: #f8fafc;
    margin: 10px 0 14px 0;
}

.metric-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 20px;
    min-height: 152px;
    box-shadow: 0 14px 28px rgba(0,0,0,0.22);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.metric-label {
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 8px;
}

.metric-number {
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.1;
}

.metric-note {
    font-size: 14px;
    color: #cbd5e1;
    margin-top: 10px;
    line-height: 1.8;
}

.panel {
    background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(248,250,252,0.92) 100%);
    color: #0f172a;
    border-radius: 24px;
    padding: 22px;
    box-shadow: 0 16px 34px rgba(0,0,0,0.18);
    margin-bottom: 18px;
}

.dark-panel {
    background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.04) 100%);
    color: #f8fafc;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 22px;
    box-shadow: 0 16px 34px rgba(0,0,0,0.22);
    margin-bottom: 18px;
}

.list-item {
    padding: 12px 0;
    border-bottom: 1px solid rgba(15,23,42,0.08);
    font-size: 15px;
    line-height: 1.9;
}
.list-item:last-child {
    border-bottom: none;
}

.dark-list-item {
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    font-size: 15px;
    line-height: 1.9;
}
.dark-list-item:last-child {
    border-bottom: none;
}

.badge-green, .badge-yellow, .badge-red, .badge-blue {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
}
.badge-green { background: rgba(52,211,153,0.16); color: #86efac; }
.badge-yellow { background: rgba(251,191,36,0.16); color: #fde68a; }
.badge-red { background: rgba(248,113,113,0.16); color: #fecaca; }
.badge-blue { background: rgba(96,165,250,0.16); color: #bfdbfe; }

.reco-box {
    background: linear-gradient(135deg, #111827 0%, #1e293b 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 26px;
    padding: 24px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.28);
    color: white;
}

.reco-title {
    font-size: 12px;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: #93c5fd;
    margin-bottom: 10px;
}

.reco-main {
    font-size: 26px;
    font-weight: 800;
    line-height: 1.55;
    margin-bottom: 12px;
}

.reco-sub {
    font-size: 15px;
    color: #e5e7eb;
    line-height: 1.95;
}

.script-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(248,250,252,0.92) 100%);
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 16px 28px rgba(0,0,0,0.16);
    height: 100%;
    color: #0f172a;
}

.script-version {
    display: inline-block;
    background: #dbeafe;
    color: #1d4ed8;
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 10px;
}

.script-body {
    white-space: pre-wrap;
    line-height: 1.9;
    font-size: 14px;
}

.note-chip {
    display: inline-block;
    background: #e2e8f0;
    color: #334155;
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 12px;
    margin-bottom: 10px;
}

div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.96);
    border-radius: 18px;
    padding: 6px;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    border-radius: 14px !important;
}

div.stButton > button {
    border-radius: 14px !important;
    height: 46px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# =========================
# JSON 工具
# =========================
def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return default
        return json.loads(content)
    except Exception:
        return default

def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# =========================
# YouTube 抓資料
# =========================
def fetch_youtube_videos(api_key: str, channel_id: str, max_results: int = 20) -> pd.DataFrame:
    if not api_key or api_key == "你的_YOUTUBE_API_KEY":
        raise RuntimeError("請先設定 YOUTUBE_API_KEY")

    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_res = requests.get(
        search_url,
        params={
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "maxResults": max_results,
            "type": "video"
        },
        timeout=30
    )
    data = search_res.json()

    if "error" in data:
        raise RuntimeError(json.dumps(data, ensure_ascii=False, indent=2))

    items = data.get("items", [])
    if not items:
        return pd.DataFrame(columns=["video_id", "title", "published_at", "views", "likes", "comments", "url"])

    video_ids = []
    videos = []

    for item in items:
        vid = item["id"]["videoId"]
        snippet = item["snippet"]
        video_ids.append(vid)
        videos.append({
            "video_id": vid,
            "title": snippet.get("title", ""),
            "published_at": snippet.get("publishedAt", ""),
            "url": f"https://www.youtube.com/watch?v={vid}",
        })

    stats_url = "https://www.googleapis.com/youtube/v3/videos"
    stats_res = requests.get(
        stats_url,
        params={
            "key": api_key,
            "id": ",".join(video_ids),
            "part": "statistics"
        },
        timeout=30
    )
    stats_data = stats_res.json()

    if "error" in stats_data:
        raise RuntimeError(json.dumps(stats_data, ensure_ascii=False, indent=2))

    stats_map = {item["id"]: item.get("statistics", {}) for item in stats_data.get("items", [])}

    for v in videos:
        stats = stats_map.get(v["video_id"], {})
        v["views"] = int(stats.get("viewCount", 0))
        v["likes"] = int(stats.get("likeCount", 0))
        v["comments"] = int(stats.get("commentCount", 0))

    df = pd.DataFrame(videos)
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    df["engagement"] = df["likes"] + df["comments"]
    df["engagement_rate"] = ((df["engagement"] / df["views"].replace(0, 1)) * 100).round(2)
    return df

# =========================
# 分類
# =========================
def infer_type(title: str) -> str:
    t = str(title).lower()
    if any(k in t for k in ["教學", "怎麼", "如何", "技巧", "保存", "必備"]):
        return "教學型"
    if any(k in t for k in ["故事", "歷史", "身世", "人生", "情", "茶金"]):
        return "故事型"
    if any(k in t for k in ["預購", "推薦", "來了", "正式", "便宜", "優惠"]):
        return "推廣型"
    if any(k in t for k in ["開箱", "比較", "實測", "差在哪", "真假"]):
        return "開箱型"
    return "其他"

def apply_manual_type(df: pd.DataFrame, override: dict) -> pd.DataFrame:
    df = df.copy()
    df["type"] = df["title"].apply(infer_type)
    df["type"] = df.apply(lambda r: override.get(r["video_id"], r["type"]), axis=1)
    return df

# =========================
# AI
# =========================
def generate_next_idea_ai(df: pd.DataFrame):
    if df.empty:
        return "【下一支主題】\n目前沒有資料\n\n【開頭一句】\n目前沒有資料\n\n【拍法建議】\n先同步資料"

    best = df.sort_values(["engagement_rate", "views"], ascending=False).iloc[0]

    fallback = f"""【下一支主題】
延伸「{best['title']}」這類型內容

【開頭一句】
很多人以為這很普通，但真的懂的人一看就知道差很多。

【拍法建議】
延續這支影片的主題方向，用更生活感的切角拍，前3秒直接破題，中段補一個重點知識，結尾留一句讓人想留言的話。
"""

    if not client:
        return fallback

    prompt = f"""
你是台灣短影音內容企劃，擅長茶葉、生活感、帶一點銷售但不硬廣的內容。

目前表現最好的影片：
標題：{best['title']}
觀看：{int(best['views'])}
按讚：{int(best['likes'])}
留言：{int(best['comments'])}
互動率：{best['engagement_rate']}%
內容類型：{best['type']}

請幫我提供：
1. 下一支最值得拍的主題
2. 適合的開頭一句
3. 影片大概怎麼拍會比較自然
4. 保持台灣口語、生活感，不要太像廣告
5. 請簡單、清楚、真的能拍

請用這個格式輸出：

【下一支主題】
【開頭一句】
【拍法建議】
"""

    try:
        res = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        return res.output_text
    except Exception:
        return fallback

def generate_scripts_ai(topic: str):
    fallback = f"""【版本一｜生活感】
【開頭】
下班回到家，有時候不是想喝什麼厲害的，只是想讓自己慢下來。

【腳本】
今天這支想跟你分享 {topic}。
很多人一開始會覺得，好像都差不多，
但真的接觸之後，你會發現差別其實很明顯。
不是講得多專業，而是喝下去那個感覺真的不一樣。
這種內容最適合用生活感去拍，
乾淨畫面、簡單旁白、讓人看得舒服。

【結尾】
你平常喝茶，是為了解渴，還是讓自己放鬆一下？

【版本二｜故事感】
【開頭】
你現在看到的不只是一杯茶，後面其實有很多故事。

【腳本】
{topic} 不是只有表面上那個味道而已。
很多人喝茶只喝到第一層，
但真的懂的人，會去看它從哪裡來、怎麼做、為什麼有這個味道。
如果這支片你想拍得更有感，
就不要急著介紹產品，
先讓觀眾感受到這杯茶背後的情緒。

【結尾】
如果是你，你會想認識這杯茶背後的故事嗎？

【版本三｜自然帶貨】
【開頭】
很多人都以為茶差不多，但真的喝到好的，你會回不去。

【腳本】
今天想很簡單跟你聊 {topic}。
不是要硬賣你什麼，
而是很多人真的喝過之後，才知道差別在哪。
從入口、香氣，到後面那個回甘，
其實都不是普通茶能做到的。
如果你最近剛好在找一款更適合自己喝、也適合送人的茶，
這個方向真的可以看一下。

【結尾】
你喜歡自己喝的，還是送禮也拿得出手的那種？
"""
    if not client:
        return fallback

    prompt = f"""
你是台灣短影音腳本高手，擅長茶葉內容。

幫我寫 3 個版本：
1. 生活感
2. 故事感
3. 自然帶貨

主題：{topic}

要求：
- 台灣口語
- 不要太像廣告
- 要有情緒
- 真的能拍
- 簡單清楚

格式：
【版本一｜生活感】
【開頭】
【腳本】
【結尾】

【版本二｜故事感】
【開頭】
【腳本】
【結尾】

【版本三｜自然帶貨】
【開頭】
【腳本】
【結尾】
"""
    try:
        res = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        return res.output_text
    except Exception:
        return fallback

# =========================
# 筆記
# =========================
def load_notes():
    data = load_json(NOTES_PATH, [])
    if isinstance(data, list):
        return data
    return []

def save_note(note_text: str):
    notes = load_notes()
    notes.insert(0, {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": note_text.strip()
    })
    save_json(NOTES_PATH, notes)

# =========================
# 載入資料
# =========================
override = load_json(OVERRIDE_PATH, {})

try:
    raw_df = fetch_youtube_videos(YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID, max_results=20)
except Exception as e:
    st.error("YouTube API 讀取失敗")
    st.code(str(e))
    st.stop()

if raw_df.empty:
    st.warning("目前抓不到影片資料")
    st.stop()

df = apply_manual_type(raw_df, override)

# =========================
# 篩選
# =========================
type_options = ["全部"] + sorted(df["type"].dropna().unique().tolist())
top_bar_left, top_bar_right = st.columns([1, 3])

with top_bar_left:
    selected_type = st.selectbox("內容類型", type_options)

with top_bar_right:
    min_views = st.slider("最低觀看門檻", 0, int(df["views"].max()), 0)

filtered_df = df.copy()
if selected_type != "全部":
    filtered_df = filtered_df[filtered_df["type"] == selected_type]
filtered_df = filtered_df[filtered_df["views"] >= min_views]

if filtered_df.empty:
    st.warning("目前沒有符合條件的資料")
    st.stop()

top_video = filtered_df.sort_values(["engagement_rate", "views"], ascending=False).iloc[0]
total_views = int(filtered_df["views"].sum())
avg_rate = round(filtered_df["engagement_rate"].mean(), 2)

if avg_rate >= 2:
    status_badge = "badge-green"
    status_text = "爆發中"
    status_note = "這批內容有明顯打中觀眾，值得延伸。"
elif avg_rate >= 1:
    status_badge = "badge-yellow"
    status_text = "穩定成長"
    status_note = "方向是對的，可以再優化開頭。"
else:
    status_badge = "badge-red"
    status_text = "需要調整"
    status_note = "建議先優化主題切角與前 3 秒。"

# =========================
# Hero
# =========================
st.markdown("""
<div class="hero">
    <div class="hero-kicker">Tea Creator Control Center</div>
    <div class="hero-title">🎬 茶葉創作者總控台</div>
    <div class="hero-sub">
        這不是只有數字的 dashboard，<br>
        而是幫你判斷：哪支值得延伸、哪類型比較會爆、下一支要拍什麼、腳本怎麼寫。
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 指標卡
# =========================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">目前狀態</div>
        <div class="{status_badge}">{status_text}</div>
        <div class="metric-note">{status_note}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">總觀看</div>
        <div class="metric-number">{total_views:,}</div>
        <div class="metric-note">目前篩選條件下的總觀看</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">平均互動率</div>
        <div class="metric-number">{avg_rate}%</div>
        <div class="metric-note">按讚＋留言 / 觀看</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">最佳影片</div>
        <div class="metric-note" style="font-size:22px;font-weight:800;color:#fff;line-height:1.5;">{top_video['title']}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 摘要 + 推薦
# =========================
left, right = st.columns([1.05, 0.95])

with left:
    st.markdown('<div class="section-title">最近表現摘要</div>', unsafe_allow_html=True)
    rank_df = filtered_df.sort_values("views", ascending=False).head(10)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    for _, row in rank_df.head(4).iterrows():
        st.markdown(
            f'<div class="list-item"><b>{row["title"]}</b><br>觀看 {int(row["views"]):,} ｜ 互動率 {row["engagement_rate"]}% ｜ 類型 {row["type"]}</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">爆款候選 TOP 5</div>', unsafe_allow_html=True)
    hot_df = filtered_df.sort_values(["engagement_rate", "views"], ascending=False).head(5).copy()
    hot_show = hot_df[["title", "views", "likes", "comments", "engagement_rate", "type"]].rename(
        columns={
            "title": "影片標題",
            "views": "觀看數",
            "likes": "按讚數",
            "comments": "留言數",
            "engagement_rate": "互動率",
            "type": "類型"
        }
    )
    st.dataframe(hot_show, width="stretch", hide_index=True)

with right:
    st.markdown('<div class="section-title">AI 下一支建議</div>', unsafe_allow_html=True)
    next_idea = generate_next_idea_ai(filtered_df)
    st.markdown(
        f'<div class="reco-box"><div class="reco-title">AI recommendation</div><div class="reco-main">下一支最值得拍</div><div class="reco-sub">{next_idea.replace(chr(10), "<br>")}</div></div>',
        unsafe_allow_html=True
    )

# =========================
# 圖表
# =========================
st.markdown('<div class="section-title">趨勢分析</div>', unsafe_allow_html=True)

chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown('<div class="dark-panel">', unsafe_allow_html=True)
    st.subheader("📈 觀看數 TOP 10")
    chart_df = filtered_df.sort_values("views", ascending=False).head(10).set_index("title")
    st.bar_chart(chart_df["views"])
    st.markdown('</div>', unsafe_allow_html=True)

with chart_right:
    st.markdown('<div class="dark-panel">', unsafe_allow_html=True)
    st.subheader("📅 觀看趨勢")
    time_df = filtered_df.dropna(subset=["published_at"]).copy()
    if len(time_df) > 0:
        time_df["date"] = time_df["published_at"].dt.date
        trend_df = time_df.groupby("date")["views"].sum()
        st.line_chart(trend_df)
    else:
        st.info("沒有時間資料")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 類型分析
# =========================
st.markdown('<div class="section-title">類型分析</div>', unsafe_allow_html=True)

type_summary = (
    filtered_df.groupby("type")
    .agg(
        平均觀看數=("views", "mean"),
        平均按讚數=("likes", "mean"),
        平均留言數=("comments", "mean"),
        平均互動率=("engagement_rate", "mean"),
        影片數=("video_id", "count"),
    )
    .reset_index()
)

if len(type_summary) > 0:
    type_summary["平均觀看數"] = type_summary["平均觀看數"].round(0).astype(int)
    type_summary["平均按讚數"] = type_summary["平均按讚數"].round(0).astype(int)
    type_summary["平均留言數"] = type_summary["平均留言數"].round(0).astype(int)
    type_summary["平均互動率"] = type_summary["平均互動率"].round(2)

    col_a, col_b = st.columns(2)

    with col_a:
        st.dataframe(type_summary.rename(columns={"type": "內容類型"}), width="stretch", hide_index=True)
        st.subheader("📊 各內容類型平均觀看數")
        st.bar_chart(type_summary.set_index("type")["平均觀看數"])

    with col_b:
        st.subheader("📊 各內容類型平均互動率")
        st.bar_chart(type_summary.set_index("type")["平均互動率"])
else:
    st.info("目前沒有可分析的內容類型資料")

# =========================
# AI 腳本
# =========================
st.markdown('<div class="section-title">AI 腳本</div>', unsafe_allow_html=True)

topic = st.text_input("主題", value=top_video["title"])

if st.button("生成腳本", width="stretch"):
    result = generate_scripts_ai(topic)
    st.markdown("### 🎬 腳本結果")
    st.markdown(f'<div class="panel" style="white-space:pre-wrap;line-height:1.9;">{result}</div>', unsafe_allow_html=True)

# =========================
# 手動分類修正
# =========================
st.markdown('<div class="section-title">手動分類修正</div>', unsafe_allow_html=True)

type_choices = ["教學型", "故事型", "推廣型", "開箱型", "其他"]
edited_override = dict(override)

edit_df = filtered_df.head(10).copy()
for _, row in edit_df.iterrows():
    current_type = edited_override.get(row["video_id"], row["type"])
    idx = type_choices.index(current_type) if current_type in type_choices else 4
    new_type = st.selectbox(
        row["title"][:30],
        type_choices,
        index=idx,
        key=f"type_{row['video_id']}"
    )
    if new_type != current_type:
        edited_override[row["video_id"]] = new_type
    elif row["video_id"] in edited_override and new_type == infer_type(row["title"]):
        edited_override.pop(row["video_id"], None)

if st.button("💾 儲存分類", width="stretch"):
    save_json(OVERRIDE_PATH, edited_override)
    st.success("分類已儲存")
    st.rerun()

# =========================
# 筆記
# =========================
st.markdown('<div class="section-title">創作者筆記</div>', unsafe_allow_html=True)

note_left, note_right = st.columns([1, 1])

with note_left:
    note = st.text_area(
        "把靈感、留言觀察、下一支想法記在這裡：",
        height=180,
        placeholder="例如：\n- 想拍：冬片茶為什麼比較甜\n- 客人常問：高山茶差在哪\n- 下支片方向：30 秒快節奏版本"
    )
    if st.button("記錄靈感", width="stretch"):
        if note.strip():
            save_note(note)
            st.success("已記下靈感")
            st.rerun()
        else:
            st.warning("你還沒輸入內容。")

with note_right:
    notes = load_notes()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### 最近筆記")
    if not notes:
        st.write("目前還沒有筆記。")
    else:
        for item in notes[:8]:
            st.markdown(
                f'<div class="list-item"><span class="note-chip">{item["created_at"]}</span><br>{item["text"]}</div>',
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 原始資料表
# =========================
st.markdown('<div class="section-title">影片資料表</div>', unsafe_allow_html=True)

show_df = filtered_df.copy()
show_df["published_at"] = show_df["published_at"].dt.strftime("%Y-%m-%d")
show_df = show_df[["title", "type", "views", "likes", "comments", "engagement_rate", "published_at", "url"]]
show_df.columns = ["影片標題", "類型", "觀看數", "按讚數", "留言數", "互動率(%)", "發布日期", "連結"]

st.dataframe(show_df, width="stretch", height=360, hide_index=True)
