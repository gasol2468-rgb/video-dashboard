import os
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# =========================
# 基本設定
# =========================
load_dotenv()

st.set_page_config(
    page_title="茶葉創作者總控台",
    page_icon="🎬",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CACHE_PATH = DATA_DIR / "youtube_cache.json"
OVERRIDE_PATH = DATA_DIR / "content_override.json"
NOTES_PATH = DATA_DIR / "creator_notes.json"

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
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
        radial-gradient(circle at top left, rgba(59,130,246,0.10), transparent 22%),
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
    background: linear-gradient(135deg, rgba(59,130,246,0.3) 0%, rgba(16,185,129,0.2) 100%) !important;
    border: 1px solid rgba(96,165,250,0.4) !important;
    color: #f8fafc !important;
    transition: all 0.3s ease !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, rgba(59,130,246,0.5) 0%, rgba(16,185,129,0.3) 100%) !important;
    border: 1px solid rgba(96,165,250,0.6) !important;
    box-shadow: 0 8px 20px rgba(59,130,246,0.3) !important;
    transform: translateY(-2px) !important;
}
div[data-testid="stExpander"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.04) 100%) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
}
div[data-testid="stExpanderContent"] {
    background: rgba(15,23,42,0.4) !important;
}
div[data-testid="stDownloadButton"] > button {
    border-radius: 12px !important;
    background: linear-gradient(135deg, rgba(59,130,246,0.3) 0%, rgba(16,185,129,0.2) 100%) !important;
    border: 1px solid rgba(96,165,250,0.3) !important;
    color: #f8fafc !important;
    font-weight: 600 !important;
    height: 40px !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg, rgba(59,130,246,0.5) 0%, rgba(16,185,129,0.3) 100%) !important;
    border: 1px solid rgba(96,165,250,0.6) !important;
    box-shadow: 0 6px 16px rgba(59,130,246,0.25) !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
div[data-testid="stSelectbox"] svg {
    fill: rgba(96,165,250,0.8) !important;
}
div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
div[data-testid="stDataFrame"] td,
div[data-testid="stDataFrame"] th {
    background: transparent !important;
    color: #f8fafc !important;
}
div[data-testid="stDataFrame"] thead {
    background: rgba(255,255,255,0.08) !important;
}
div[data-testid="stSlider"] {
    color: #f8fafc !important;
}
div[data-testid="stSlider"] > div > div > div {
    background: rgba(255,255,255,0.1) !important;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.metric-card, .hero, .panel, .dark-panel, .reco-box {
    animation: fadeIn 0.5s ease-out !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 工具
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

def load_notes():
    data = load_json(NOTES_PATH, [])
    return data if isinstance(data, list) else []

def save_note(note_text: str):
    notes = load_notes()
    notes.insert(0, {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": note_text.strip()
    })
    save_json(NOTES_PATH, notes)

def export_to_csv(df: pd.DataFrame) -> bytes:
    """匯出為 CSV"""
    csv_buffer = df.to_csv(index=False, encoding="utf-8-sig")
    return csv_buffer.encode("utf-8-sig")

def export_to_excel(df: pd.DataFrame) -> bytes:
    """匯出為 Excel"""
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='影片數據', index=False)
        worksheet = writer.sheets['影片數據']
        for idx, col in enumerate(df.columns):
            max_length = max(df[col].astype(str).str.len().max(), len(str(col)))
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
    output.seek(0)
    return output.getvalue()

def create_content_calendar(df: pd.DataFrame) -> pd.DataFrame:
    """生成內容日曆"""
    calendar_df = df[["title", "type", "published_at", "views", "engagement_rate"]].copy()
    calendar_df["published_at"] = calendar_df["published_at"].dt.strftime("%Y-%m-%d %H:%M")
    calendar_df = calendar_df.sort_values("published_at", ascending=False)
    return calendar_df

@st.cache_data
def extract_comments_insights(df: pd.DataFrame) -> dict:
    """簡單的評論洞察分析"""
    total_comments = int(df["comments"].sum())
    avg_comments = round(df["comments"].mean(), 1)
    max_comments_video = df.loc[df["comments"].idxmax()] if len(df) > 0 else None

    return {
        "total": total_comments,
        "average": avg_comments,
        "top_video": max_comments_video["title"] if max_comments_video is not None else "",
        "top_count": int(max_comments_video["comments"]) if max_comments_video is not None else 0
    }

def create_pdf_report(df: pd.DataFrame, summary_dict: dict, title: str = "Tea Creator Report") -> bytes:
    """生成簡單 PDF 報告"""
    from io import BytesIO
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()

    # 標題
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)

    # 摘要資訊（使用英文 key）
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Summary", ln=True)
    pdf.set_font("Arial", "", 10)

    # 翻譯 key 為英文
    key_mapping = {
        "總觀看": "Total Views",
        "平均互動率": "Avg Engagement Rate",
        "影片數": "Video Count"
    }

    for key, value in summary_dict.items():
        if isinstance(value, (int, float)):
            display_key = key_mapping.get(key, key)
            display_value = f"{value:,.0f}" if isinstance(value, (int, float)) else str(value)
            try:
                pdf.cell(0, 6, f"{display_key}: {display_value}", ln=True)
            except:
                pass

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Total Records: {len(df)}", ln=True)

    buffer = BytesIO()
    pdf_data = pdf.output()
    buffer.write(pdf_data)
    buffer.seek(0)

    return buffer.getvalue()

# =========================
# 快取
# =========================
def save_cache(df: pd.DataFrame):
    df_to_save = df.copy()

    for col in df_to_save.columns:
        if pd.api.types.is_datetime64_any_dtype(df_to_save[col]):
            df_to_save[col] = df_to_save[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rows": df_to_save.to_dict(orient="records")
    }
    save_json(CACHE_PATH, payload)

def load_cache():
    payload = load_json(CACHE_PATH, {})
    rows = payload.get("rows", [])
    saved_at = payload.get("saved_at", "")
    if not rows:
        return None, saved_at
    df = pd.DataFrame(rows)
    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    return df, saved_at

# =========================
# YouTube
# =========================
def fetch_youtube_videos(api_key: str, channel_id: str, max_results: int = 12) -> pd.DataFrame:
    if not api_key:
        raise RuntimeError("請先設定 YOUTUBE_API_KEY（目前沒有讀到）")

    search_url = "https://www.googleapis.com/youtube/v3/search"
    res = requests.get(
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
    data = res.json()

    if "error" in data:
        raise RuntimeError(json.dumps(data, ensure_ascii=False, indent=2))

    items = data.get("items", [])
    if not items:
        return pd.DataFrame(columns=["video_id", "title", "published_at", "views", "likes", "comments", "url"])

    videos = []
    video_ids = []

    for item in items:
        vid = item["id"]["videoId"]
        snippet = item["snippet"]
        videos.append({
            "video_id": vid,
            "title": snippet.get("title", ""),
            "published_at": snippet.get("publishedAt", ""),
            "url": f"https://www.youtube.com/watch?v={vid}",
        })
        video_ids.append(vid)

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
        s = stats_map.get(v["video_id"], {})
        v["views"] = int(s.get("viewCount", 0))
        v["likes"] = int(s.get("likeCount", 0))
        v["comments"] = int(s.get("commentCount", 0))

    df = pd.DataFrame(videos)
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    df["engagement"] = df["likes"] + df["comments"]
    df["engagement_rate"] = ((df["engagement"] / df["views"].replace(0, 1)) * 100).round(2)
    return df

# =========================
# 類型
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
# 分析
# =========================
def analyze_latest_video(df: pd.DataFrame) -> dict:
    latest = df.sort_values("published_at", ascending=False).iloc[0]
    rate = float(latest["engagement_rate"])
    views = int(latest["views"])
    content_type = latest["type"]

    if rate >= 2:
        verdict = "互動不錯，值得延伸"
        reason = "這支影片的互動率不低，代表題材或切角有打中觀眾。"
    elif views >= df["views"].median():
        verdict = "觀看有潛力，但互動還能再補"
        reason = "有基本觀看，但留言與按讚偏少，代表可以優化開頭或結尾互動。"
    else:
        verdict = "需要再調整"
        reason = "目前這支的觀看與互動都偏普通，建議換更有話題的切角。"

    if content_type == "教學型":
        action = "下一支可以拍更短更直接的教學版，前3秒先講答案。"
    elif content_type == "故事型":
        action = "下一支建議延伸人物、茶園、品牌故事，用情緒感撐住。"
    elif content_type == "推廣型":
        action = "下一支不要只講產品，改成為什麼值得買的生活情境。"
    elif content_type == "開箱型":
        action = "下一支可以拍比較型內容，讓觀眾更容易留言。"
    else:
        action = "下一支建議用更明確的主題包裝，不要太散。"

    return {
        "title": latest["title"],
        "views": int(latest["views"]),
        "likes": int(latest["likes"]),
        "comments": int(latest["comments"]),
        "rate": rate,
        "type": content_type,
        "verdict": verdict,
        "reason": reason,
        "action": action
    }

# =========================
# AI
# =========================
def generate_next_idea_ai(df: pd.DataFrame, latest_info: dict):
    best = df.sort_values(["engagement_rate", "views"], ascending=False).iloc[0]
    fallback = f"""【下一支主題】
延伸「{best['title']}」這類型內容

【開頭一句】
很多人以為這很普通，但真的懂的人一看就知道差很多。

【拍法建議】
{latest_info['action']}
"""
    if not client:
        return fallback

    prompt = f"""
你是台灣短影音內容企劃，擅長茶葉、生活感、帶一點銷售但不硬廣的內容。

最新影片：
標題：{latest_info['title']}
觀看：{latest_info['views']}
按讚：{latest_info['likes']}
留言：{latest_info['comments']}
互動率：{latest_info['rate']}%
類型：{latest_info['type']}
判斷：{latest_info['verdict']}
觀察：{latest_info['reason']}

目前表現最好的影片：
標題：{best['title']}
觀看：{int(best['views'])}
互動率：{best['engagement_rate']}%
類型：{best['type']}

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
        res = client.responses.create(model="gpt-4o-mini", input=prompt)
        return res.output_text
    except Exception:
        return fallback

def generate_auto_script_ai(next_idea_text: str):
    fallback = """【版本一｜生活感】
【開頭】
有時候不是想喝什麼厲害的，只是想讓自己慢下來。

【腳本】
先從生活情境切進去，
不要急著講產品，先讓觀眾有感。

【結尾】
你喝茶最在意的是味道，還是那個感覺？

【版本二｜故事感】
【開頭】
你現在看到的不只是一杯茶，後面其實有很多故事。

【腳本】
從產地、人物、季節或一個細節開始講，
先吸住情緒，再帶出重點。

【結尾】
如果是你，你會想更認識這杯茶嗎？

【版本三｜自然帶貨】
【開頭】
很多人都以為茶差不多，但真的喝到好的，你會回不去。

【腳本】
從生活需求切入，再講這杯茶為什麼不一樣。

【結尾】
你會想自己喝，還是拿來送人？
"""
    if not client:
        return fallback

    prompt = f"""
你是台灣短影音腳本高手，擅長茶葉內容。

根據下面的影片建議，幫我寫 3 個版本：
1. 生活感
2. 故事感
3. 自然帶貨

影片建議：
{next_idea_text}

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
        res = client.responses.create(model="gpt-4o-mini", input=prompt)
        return res.output_text
    except Exception:
        return fallback

# =========================
# 同步控制
# =========================
st.markdown("""
<div class="hero">
    <div class="hero-kicker">Tea Creator Control Center</div>
    <div class="hero-title">🎬 茶葉創作者總控台</div>
    <div class="hero-sub">
        這版已改成省 quota 模式：<br>
        平常先看快取資料，只有按同步才會打 YouTube API。
    </div>
</div>
""", unsafe_allow_html=True)

top_left, top_right = st.columns([1, 3])

with top_left:
    sync_now = st.button("同步最新 YouTube 資料", width="stretch")

cache_df, cache_saved_at = load_cache()

if sync_now:
    with st.spinner("正在同步 YouTube 資料..."):
        try:
            fresh_df = fetch_youtube_videos(YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID, max_results=12)
            save_cache(fresh_df)
            cache_df = fresh_df
            cache_saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("同步完成，已更新快取資料")
        except Exception as e:
            st.error("同步失敗，已改用快取資料")
            st.code(str(e))

with top_right:
    if cache_saved_at:
        st.info(f"目前顯示的是快取資料。最近同步時間：{cache_saved_at}")
    else:
        st.warning("目前還沒有快取資料，請先按一次同步。")

with st.expander("檢查環境變數"):
    st.write("YOUTUBE_API_KEY 是否有讀到：", bool(YOUTUBE_API_KEY))
    st.write("YOUTUBE_CHANNEL_ID：", YOUTUBE_CHANNEL_ID)
    st.write("OPENAI_API_KEY 是否有讀到：", bool(OPENAI_API_KEY))

if cache_df is None or cache_df.empty:
    st.warning("目前沒有可顯示的資料，請先按「同步最新 YouTube 資料」。")
    st.stop()

# =========================
# 載入資料
# =========================
override = load_json(OVERRIDE_PATH, {})
df = apply_manual_type(cache_df, override)

df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0)
df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0)
df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0)
df["engagement"] = df["likes"] + df["comments"]
df["engagement_rate"] = ((df["engagement"] / df["views"].replace(0, 1)) * 100).round(2)

# =========================
# 篩選
# =========================
type_options = ["全部"] + sorted(df["type"].dropna().unique().tolist())
f1, f2 = st.columns([1, 3])

with f1:
    selected_type = st.selectbox("內容類型", type_options)

with f2:
    min_views = st.slider("最低觀看門檻", 0, int(df["views"].max()) if len(df) > 0 else 0, 0)

filtered_df = df.copy()
if selected_type != "全部":
    filtered_df = filtered_df[filtered_df["type"] == selected_type]
filtered_df = filtered_df[filtered_df["views"] >= min_views]

if filtered_df.empty:
    st.warning("目前沒有符合條件的資料")
    st.stop()

top_video = filtered_df.sort_values(["engagement_rate", "views"], ascending=False).iloc[0]
latest_info = analyze_latest_video(filtered_df)
next_idea = generate_next_idea_ai(filtered_df, latest_info)

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
# 最新影片分析 + 下一支建議
# =========================
left, right = st.columns([1.02, 0.98])

with left:
    st.markdown('<div class="section-title">最新影片分析</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="panel">
        <div class="list-item"><b>最新影片：</b>{latest_info['title']}</div>
        <div class="list-item"><b>類型：</b>{latest_info['type']}</div>
        <div class="list-item"><b>觀看 / 按讚 / 留言：</b>{latest_info['views']:,} / {latest_info['likes']} / {latest_info['comments']}</div>
        <div class="list-item"><b>互動率：</b>{latest_info['rate']}%</div>
        <div class="list-item"><b>判斷：</b>{latest_info['verdict']}</div>
        <div class="list-item"><b>原因：</b>{latest_info['reason']}</div>
        <div class="list-item"><b>建議動作：</b>{latest_info['action']}</div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">下一支主題建議</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="reco-box"><div class="reco-title">AI recommendation</div><div class="reco-main">下一支最值得拍</div><div class="reco-sub">{next_idea.replace(chr(10), "<br>")}</div></div>',
        unsafe_allow_html=True
    )

# =========================
# 摘要
# =========================
st.markdown('<div class="section-title">最近表現摘要</div>', unsafe_allow_html=True)

sum_left, sum_right = st.columns(2)

with sum_left:
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
    st.subheader("🔥 爆款候選 TOP 5")
    st.dataframe(hot_show, width="stretch", hide_index=True)

with sum_right:
    top_show = filtered_df.sort_values("views", ascending=False).head(10)[["title", "views", "likes", "comments", "type"]].rename(
        columns={
            "title": "影片標題",
            "views": "觀看數",
            "likes": "按讚數",
            "comments": "留言數",
            "type": "類型"
        }
    )
    st.subheader("🏆 觀看數排行榜 TOP 10")
    st.dataframe(top_show, width="stretch", hide_index=True)

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
    with col_b:
        st.subheader("📊 各內容類型平均互動率")
        st.bar_chart(type_summary.set_index("type")["平均互動率"])

# =========================
# 自動腳本
# =========================
st.markdown('<div class="section-title">自動腳本推薦</div>', unsafe_allow_html=True)

if st.button("生成下一支自動腳本", width="stretch"):
    auto_script = generate_auto_script_ai(next_idea)
    st.markdown(f'<div class="panel" style="white-space:pre-wrap;line-height:1.9;">{auto_script}</div>', unsafe_allow_html=True)

# =========================
# 數據導出
# =========================
st.markdown('<div style="margin: 32px 0;"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">📥 數據導出</div>', unsafe_allow_html=True)

exp_col1, exp_col2, exp_col3 = st.columns([1, 1, 1])

with exp_col1:
    csv_data = export_to_csv(filtered_df[["title", "type", "views", "likes", "comments", "engagement_rate", "published_at"]])
    st.download_button(
        label="📊 下載 CSV",
        data=csv_data,
        file_name=f"video_data_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        width="stretch"
    )

with exp_col2:
    excel_data = export_to_excel(filtered_df[["title", "type", "views", "likes", "comments", "engagement_rate", "published_at"]])
    st.download_button(
        label="📋 下載 Excel",
        data=excel_data,
        file_name=f"video_data_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch"
    )

with exp_col3:
    summary = {
        "總觀看": int(filtered_df["views"].sum()),
        "平均互動率": round(filtered_df["engagement_rate"].mean(), 2),
        "影片數": len(filtered_df)
    }
    pdf_data = create_pdf_report(filtered_df, summary)
    st.download_button(
        label="📄 下載 PDF",
        data=pdf_data,
        file_name=f"report_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        width="stretch"
    )

# =========================
# 內容日曆
# =========================
st.markdown('<div class="section-title">📅 內容發布日曆</div>', unsafe_allow_html=True)

with st.expander("查看內容日曆", expanded=False):
    calendar_df = create_content_calendar(filtered_df)
    if len(calendar_df) > 0:
        cal_display = calendar_df[["published_at", "title", "type", "views", "engagement_rate"]].rename(
            columns={
                "published_at": "發布時間",
                "title": "影片標題",
                "type": "類型",
                "views": "觀看數",
                "engagement_rate": "互動率(%)"
            }
        )
        st.dataframe(cal_display, width="stretch", hide_index=True)
    else:
        st.info("沒有內容日曆數據")

# =========================
# 評論分析
# =========================
st.markdown('<div class="section-title">💬 評論分析</div>', unsafe_allow_html=True)

comment_insights = extract_comments_insights(filtered_df)

col_comment1, col_comment2, col_comment3 = st.columns(3)

with col_comment1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">總留言數</div>
        <div class="metric-number">{comment_insights['total']:,}</div>
        <div class="metric-note">所有影片的留言總計</div>
    </div>
    """, unsafe_allow_html=True)

with col_comment2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">平均留言</div>
        <div class="metric-number">{comment_insights['average']}</div>
        <div class="metric-note">每支影片平均留言數</div>
    </div>
    """, unsafe_allow_html=True)

with col_comment3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">留言最多</div>
        <div class="metric-note" style="font-size:13px;line-height:1.4;">{comment_insights['top_video'][:25]}...</div>
        <div class="metric-note" style="font-size:12px;color:#8b5cf6;margin-top:8px;">{comment_insights['top_count']} 則留言</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 手動分類
# =========================
st.markdown('<div class="section-title">手動分類修正</div>', unsafe_allow_html=True)

override = load_json(OVERRIDE_PATH, {})
type_choices = ["教學型", "故事型", "推廣型", "開箱型", "其他"]
edited_override = dict(override)

for _, row in filtered_df.head(10).iterrows():
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
