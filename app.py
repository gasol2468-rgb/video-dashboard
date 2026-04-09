import os
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    -webkit-font-smoothing: antialiased;
}
.stApp {
    background:
        radial-gradient(ellipse 100% 55% at 50% -5%, rgba(99,102,241,0.32), transparent),
        radial-gradient(ellipse 60% 40% at 0% 100%, rgba(6,182,212,0.1), transparent),
        radial-gradient(ellipse 50% 35% at 100% 80%, rgba(99,102,241,0.1), transparent),
        linear-gradient(180deg, #070e1f 0%, #0b1428 30%, #0d1830 60%, #0f1c38 100%);
    color: #f8fafc;
}
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: radial-gradient(circle, rgba(99,102,241,0.12) 1px, transparent 1px);
    background-size: 36px 36px;
    pointer-events: none;
    z-index: 0;
    mask-image: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.4) 20%, rgba(0,0,0,0.4) 80%, transparent 100%);
    -webkit-mask-image: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.4) 20%, rgba(0,0,0,0.4) 80%, transparent 100%);
}
/* ── Sidebar 全域覆蓋 ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1528 0%, #0a1020 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #cbd5e1 !important;
}
section[data-testid="stSidebar"] input {
    color: #f1f5f9 !important;
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(99,102,241,0.3) !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #fff !important;
    border: none !important;
}
.block-container {
    max-width: 1320px;
    padding-top: 2rem;
    padding-bottom: 4rem;
    position: relative;
    z-index: 1;
}
.hero {
    background: linear-gradient(145deg, rgba(255,255,255,0.075) 0%, rgba(255,255,255,0.025) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-top: 1px solid rgba(255,255,255,0.18);
    border-radius: 32px;
    padding: 44px 48px;
    color: white;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    box-shadow: 0 40px 80px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
}
.hero-kicker {
    font-size: 10.5px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-weight: 700;
    color: rgba(129,140,248,0.9);
    margin-bottom: 14px;
}
.hero-title {
    font-size: 52px;
    font-weight: 800;
    line-height: 0.95;
    margin-bottom: 18px;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #ffffff 30%, rgba(255,255,255,0.65));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    color: rgba(226,232,240,0.75);
    font-size: 15px;
    font-weight: 400;
    line-height: 1.75;
}
.section-title {
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(148,163,184,0.65);
    margin: 40px 0 16px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(255,255,255,0.07), transparent);
}
.metric-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.04) 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-top: 1px solid rgba(255,255,255,0.22);
    border-radius: 24px;
    padding: 24px 28px;
    min-height: 160px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.12);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 15%; right: 15%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.22), transparent);
    pointer-events: none;
}
.metric-card:hover {
    background: linear-gradient(145deg, rgba(255,255,255,0.095) 0%, rgba(255,255,255,0.04) 100%);
    border-color: rgba(99,102,241,0.28);
    box-shadow: 0 24px 48px rgba(0,0,0,0.38), 0 0 0 1px rgba(99,102,241,0.12), inset 0 1px 0 rgba(255,255,255,0.12);
    transform: translateY(-2px);
}
.metric-label {
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-weight: 700;
    color: rgba(148,163,184,0.8);
    margin-bottom: 12px;
}
.metric-number {
    font-size: 40px;
    font-weight: 800;
    color: #c7d2fe;
    line-height: 1.0;
    letter-spacing: -0.03em;
    margin-bottom: 8px;
    font-feature-settings: "tnum";
    text-shadow: 0 0 24px rgba(99,102,241,0.45);
}
.metric-note {
    font-size: 13px;
    font-weight: 400;
    color: rgba(203,213,225,0.8);
    margin-top: 10px;
    line-height: 1.65;
}
.panel {
    background: linear-gradient(145deg, rgba(255,255,255,0.09) 0%, rgba(255,255,255,0.04) 100%);
    color: #f8fafc;
    border: 1px solid rgba(255,255,255,0.1);
    border-top: 1px solid rgba(255,255,255,0.2);
    border-radius: 24px;
    padding: 24px 28px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
    margin-bottom: 20px;
    position: relative;
}
.dark-panel {
    background: linear-gradient(145deg, rgba(255,255,255,0.09) 0%, rgba(255,255,255,0.04) 100%);
    color: #f8fafc;
    border: 1px solid rgba(255,255,255,0.1);
    border-top: 1px solid rgba(255,255,255,0.2);
    border-radius: 24px;
    padding: 24px 28px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
    margin-bottom: 20px;
    position: relative;
}
.list-item {
    padding: 13px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 14px;
    font-weight: 400;
    line-height: 1.75;
    color: rgba(241,245,249,0.88);
}
.list-item:last-child { border-bottom: none; }
.list-item b { color: #ffffff; font-weight: 600; }
.badge-green, .badge-yellow, .badge-red, .badge-blue {
    display: inline-flex;
    align-items: center;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.badge-green  { background: rgba(52,211,153,0.1);  color: #6ee7b7; border: 1px solid rgba(52,211,153,0.22);  }
.badge-yellow { background: rgba(251,191,36,0.1);  color: #fde68a; border: 1px solid rgba(251,191,36,0.22);  }
.badge-red    { background: rgba(248,113,113,0.1); color: #fca5a5; border: 1px solid rgba(248,113,113,0.22); }
.badge-blue   { background: rgba(99,102,241,0.12); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.25);  }
.reco-box {
    background: linear-gradient(145deg, rgba(99,102,241,0.1) 0%, rgba(8,12,24,0.85) 60%);
    border: 1px solid rgba(99,102,241,0.18);
    border-top: 1px solid rgba(99,102,241,0.35);
    border-radius: 24px;
    padding: 28px 32px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 24px 48px rgba(0,0,0,0.35), inset 0 1px 0 rgba(99,102,241,0.18);
    color: white;
}
.reco-title {
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-weight: 700;
    color: rgba(129,140,248,0.85);
    margin-bottom: 14px;
}
.reco-main {
    font-size: 26px;
    font-weight: 800;
    line-height: 1.3;
    margin-bottom: 14px;
    color: #ffffff;
    letter-spacing: -0.015em;
}
.reco-sub {
    font-size: 14px;
    font-weight: 400;
    color: rgba(226,232,240,0.85);
    line-height: 1.85;
}
.note-chip {
    display: inline-block;
    background: rgba(99,102,241,0.12);
    color: rgba(129,140,248,0.9);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 10.5px;
    font-weight: 600;
    margin-bottom: 8px;
    letter-spacing: 0.03em;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: 12px !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #f8fafc !important;
}
div.stButton > button {
    border-radius: 10px !important;
    height: 42px !important;
    background: rgba(99,102,241,0.18) !important;
    border: 1px solid rgba(99,102,241,0.28) !important;
    color: rgba(248,250,252,0.95) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div.stButton > button:hover {
    background: rgba(99,102,241,0.3) !important;
    border: 1px solid rgba(99,102,241,0.48) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.22) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stExpander"] {
    background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-top: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
}
div[data-testid="stExpanderContent"] {
    background: rgba(8,12,24,0.4) !important;
    border-top: 1px solid rgba(255,255,255,0.05) !important;
}
div[data-testid="stDownloadButton"] > button {
    border-radius: 10px !important;
    background: rgba(99,102,241,0.13) !important;
    border: 1px solid rgba(99,102,241,0.22) !important;
    color: rgba(248,250,252,0.9) !important;
    font-weight: 600 !important;
    height: 42px !important;
    font-size: 13.5px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: rgba(99,102,241,0.26) !important;
    border: 1px solid rgba(99,102,241,0.42) !important;
    box-shadow: 0 8px 20px rgba(99,102,241,0.18) !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
div[data-testid="stSelectbox"] svg { fill: rgba(129,140,248,0.85) !important; }
div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.02) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    overflow: hidden !important;
}
div[data-testid="stDataFrame"] td,
div[data-testid="stDataFrame"] th {
    background: transparent !important;
    color: rgba(241,245,249,0.88) !important;
    font-weight: 500 !important;
    border: none !important;
    font-size: 13px !important;
}
div[data-testid="stDataFrame"] thead {
    background: rgba(255,255,255,0.055) !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}
div[data-testid="stDataFrame"] tbody tr:hover {
    background: rgba(99,102,241,0.07) !important;
}
div[data-testid="stSlider"] { color: #f8fafc !important; }
div[data-testid="stSlider"] > div > div > div { background: rgba(255,255,255,0.1) !important; }
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes floatY {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-6px); }
}
@keyframes recoPulse {
    0%, 100% { box-shadow: 0 24px 48px rgba(0,0,0,0.35), inset 0 1px 0 rgba(99,102,241,0.18); }
    50%       { box-shadow: 0 24px 48px rgba(0,0,0,0.35), inset 0 1px 0 rgba(99,102,241,0.25), 0 0 55px rgba(99,102,241,0.13); }
}
@keyframes glowGreen {
    0%, 100% { box-shadow: 0 0 0 0 rgba(52,211,153,0); }
    50%       { box-shadow: 0 0 12px 3px rgba(52,211,153,0.2); }
}
@keyframes glowYellow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(251,191,36,0); }
    50%       { box-shadow: 0 0 12px 3px rgba(251,191,36,0.2); }
}
@keyframes glowRed {
    0%, 100% { box-shadow: 0 0 0 0 rgba(248,113,113,0); }
    50%       { box-shadow: 0 0 12px 3px rgba(248,113,113,0.2); }
}
@keyframes shimmerLine {
    0%   { background-position: -300% center; }
    100% { background-position: 300% center; }
}
@keyframes borderGlow {
    0%, 100% { border-color: rgba(99,102,241,0.18); }
    50%       { border-color: rgba(99,102,241,0.38); }
}
@keyframes sectionReveal {
    from { opacity: 0; transform: translateX(-8px); }
    to   { opacity: 1; transform: translateX(0); }
}
.hero {
    animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) both,
               floatY 7s ease-in-out 1.2s infinite !important;
}
.hero::before {
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.35) 50%, transparent 100%);
    background-size: 300% 100%;
    animation: shimmerLine 5s linear 1.5s infinite !important;
}
.reco-box {
    animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) both,
               recoPulse 4.5s ease-in-out 1s infinite,
               borderGlow 4.5s ease-in-out 1s infinite !important;
}
.badge-green  { animation: glowGreen  3.5s ease-in-out infinite !important; }
.badge-yellow { animation: glowYellow 3.5s ease-in-out infinite !important; }
.badge-red    { animation: glowRed    3.5s ease-in-out infinite !important; }
.section-title {
    animation: sectionReveal 0.4s cubic-bezier(0.22,1,0.36,1) both !important;
}
.section-title::after {
    background: linear-gradient(90deg, rgba(99,102,241,0.3) 0%, rgba(255,255,255,0.04) 60%, transparent 100%);
    background-size: 200% 100%;
    animation: shimmerLine 6s linear infinite !important;
}
/* scroll-reveal classes (applied by JS) */
.sr-hidden {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s cubic-bezier(0.22,1,0.36,1), transform 0.6s cubic-bezier(0.22,1,0.36,1);
}
.sr-visible {
    opacity: 1 !important;
    transform: translateY(0) !important;
}
/* ── Selectbox 深色強制修正 ── */
div[data-testid="stSelectbox"] [data-baseweb="select"],
div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
    background-color: rgba(8,12,24,0.85) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] span,
div[data-testid="stSelectbox"] [data-baseweb="select"] div {
    color: #f1f5f9 !important;
    background-color: transparent !important;
}
/* 下拉選單彈出層 */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div {
    background: rgba(10,14,28,0.98) !important;
}
div[data-baseweb="popover"] [data-baseweb="menu"],
div[data-baseweb="popover"] ul {
    background: rgba(10,14,28,0.98) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
    box-shadow: 0 16px 48px rgba(0,0,0,0.6) !important;
    backdrop-filter: blur(20px) !important;
}
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] [role="option"] {
    background: transparent !important;
    color: rgba(241,245,249,0.88) !important;
}
div[data-baseweb="popover"] li:hover,
div[data-baseweb="popover"] [role="option"]:hover,
div[data-baseweb="popover"] [aria-selected="true"] {
    background: rgba(99,102,241,0.15) !important;
}
/* ── TextInput 深色修正 ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input:focus {
    background: rgba(8,12,24,0.7) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    outline: none !important;
    box-shadow: none !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(99,102,241,0.55) !important;
}
/* ── TextArea 深色修正（含 focus 紅框覆蓋）── */
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextArea"] textarea:focus {
    background: rgba(8,12,24,0.7) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    outline: none !important;
    box-shadow: none !important;
    resize: vertical !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(99,102,241,0.55) !important;
}
div[data-testid="stTextArea"] textarea::placeholder,
div[data-testid="stTextInput"] input::placeholder {
    color: rgba(148,163,184,0.4) !important;
}
/* ── Alert / Info 修正 ── */
div[data-testid="stAlert"] {
    background: rgba(99,102,241,0.07) !important;
    border: 1px solid rgba(99,102,241,0.18) !important;
    border-radius: 12px !important;
    color: rgba(165,180,252,0.9) !important;
    backdrop-filter: blur(10px) !important;
}
div[data-testid="stAlert"] p, div[data-testid="stAlert"] span {
    color: rgba(165,180,252,0.9) !important;
}
/* ── Slider 修正 ── */
div[data-testid="stSlider"] label {
    color: rgba(148,163,184,0.75) !important;
    font-size: 11px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}
div[data-testid="stSlider"] [data-testid="stThumbValue"] {
    color: rgba(165,180,252,0.9) !important;
    font-weight: 700 !important;
}
/* ── Control bar (同步區域) ── */
.control-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-top: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 0 20px;
    height: 56px;
    margin-bottom: 12px;
    backdrop-filter: blur(12px);
}
/* ── Filter bar ── */
.filter-bar {
    background: linear-gradient(145deg, rgba(255,255,255,0.045) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 16px 20px 8px;
    margin-bottom: 20px;
    backdrop-filter: blur(12px);
}
/* ── Chart label ── */
.chart-label {
    font-size: 12.5px;
    font-weight: 600;
    color: rgba(241,245,249,0.88);
    letter-spacing: 0.01em;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.chart-label-badge {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: rgba(129,140,248,0.9);
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.22);
    border-radius: 999px;
    padding: 2px 8px;
}
/* ── Chart panel (wraps Plotly) ── */
.chart-panel {
    background: linear-gradient(145deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.022) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-top: 1px solid rgba(255,255,255,0.13);
    border-radius: 24px;
    padding: 20px 20px 8px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.07);
    margin-bottom: 0;
}
/* ── Featured metric card ── */
.metric-card-featured {
    background: linear-gradient(145deg, rgba(99,102,241,0.1) 0%, rgba(255,255,255,0.025) 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-top: 1px solid rgba(99,102,241,0.38);
    border-radius: 24px;
    padding: 24px 28px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.3), inset 0 1px 0 rgba(99,102,241,0.15);
    position: relative;
    overflow: hidden;
    animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) both !important;
}
.metric-card-featured::before {
    content: '';
    position: absolute;
    top: 0; left: 15%; right: 15%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.5), transparent);
}
.featured-title {
    font-size: 18px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.5;
    margin-top: 10px;
}
.featured-sub {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(129,140,248,0.85);
    margin-bottom: 8px;
}
/* ── HTML custom table ── */
.html-table-wrap {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.02);
    width: 100%;
}
.html-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.hth {
    background: rgba(255,255,255,0.05);
    color: rgba(148,163,184,0.75);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    white-space: nowrap;
}
.htr { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
.htr:last-child { border-bottom: none; }
.htr:hover { background: rgba(99,102,241,0.07); }
.htd {
    padding: 10px 14px;
    color: rgba(241,245,249,0.85);
    font-weight: 400;
    vertical-align: middle;
    font-feature-settings: "tnum";
}
.htd-title {
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: rgba(255,255,255,0.92);
    font-weight: 500;
}
/* ── Export panel ── */
.export-panel {
    background: linear-gradient(145deg, rgba(255,255,255,0.055) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-top: 1px solid rgba(255,255,255,0.13);
    border-radius: 24px;
    padding: 24px 28px 20px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 16px 32px rgba(0,0,0,0.25);
}
.export-desc {
    font-size: 12px;
    color: rgba(148,163,184,0.65);
    margin-bottom: 16px;
    letter-spacing: 0.02em;
}
/* ── Section spacing ── */
.section-gap { margin-top: 48px; }
/* ── Streamlit 原生元件深色修復 ── */
div[data-testid="stSpinner"] > div {
    border-top-color: rgba(99,102,241,0.85) !important;
}
div[data-testid="stStatusWidget"] { color: rgba(165,180,252,0.9) !important; }
div[data-testid="stAlert"][kind="success"],
div[data-testid="stAlert"][data-baseweb="notification"][kind="positive"] {
    background: rgba(52,211,153,0.08) !important;
    border: 1px solid rgba(52,211,153,0.22) !important;
    color: rgba(110,231,183,0.9) !important;
}
div[data-testid="stAlert"][kind="error"],
div[data-testid="stAlert"][data-baseweb="notification"][kind="negative"] {
    background: rgba(248,113,113,0.08) !important;
    border: 1px solid rgba(248,113,113,0.22) !important;
    color: rgba(252,165,165,0.9) !important;
}
div[data-testid="stAlert"][kind="warning"] {
    background: rgba(251,191,36,0.08) !important;
    border: 1px solid rgba(251,191,36,0.22) !important;
    color: rgba(253,230,138,0.9) !important;
}
div[data-testid="stAlert"] * { color: inherit !important; }
div[data-testid="stNumberInput"] input {
    background: rgba(8,12,24,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}
div[data-testid="stNumberInput"] button {
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.25) !important;
    color: #f1f5f9 !important;
}
/* ── 健康分數 ── */
.health-panel {
    background: linear-gradient(145deg, rgba(99,102,241,0.1) 0%, rgba(255,255,255,0.03) 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-top: 1px solid rgba(99,102,241,0.35);
    border-radius: 24px;
    padding: 24px 28px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.28);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 32px;
}
.health-score-ring {
    flex-shrink: 0;
    width: 80px;
    height: 80px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}
.health-score-num {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.03em;
    font-feature-settings: "tnum";
}
.health-items {
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px 24px;
}
.health-item-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(148,163,184,0.7);
    margin-bottom: 4px;
}
.health-item-bar {
    height: 4px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    overflow: hidden;
    margin-top: 4px;
}
.health-item-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.8s cubic-bezier(0.22,1,0.36,1);
}
/* ── 目標追蹤 ── */
.goal-bar-wrap {
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    height: 6px;
    overflow: hidden;
    margin: 6px 0 4px;
}
.goal-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, rgba(99,102,241,0.9), rgba(52,211,153,0.85));
    transition: width 0.8s cubic-bezier(0.22,1,0.36,1);
}
/* ── 手機響應式 ── */
@media (max-width: 768px) {
    .block-container { padding-left: 12px !important; padding-right: 12px !important; }
    .hero { padding: 28px 24px !important; border-radius: 20px !important; }
    .hero-title { font-size: 32px !important; }
    .health-panel { flex-direction: column; gap: 16px; }
    .health-items { grid-template-columns: 1fr; }
}
/* ── Filter status bar ── */
.filter-status {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 10px 0 4px;
    flex-wrap: wrap;
}
.filter-status-label {
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(148,163,184,0.5);
    margin-right: 4px;
}
.filter-chip {
    font-size: 11.5px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    color: rgba(203,213,225,0.7);
}
.filter-chip--active {
    background: rgba(99,102,241,0.15);
    border-color: rgba(99,102,241,0.3);
    color: rgba(165,180,252,0.9);
}
.filter-status-count {
    margin-left: auto;
    font-size: 11px;
    font-weight: 600;
    color: rgba(148,163,184,0.5);
}
/* ── Sync chip ── */
.sync-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    height: 42px;
    padding: 0 18px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    color: rgba(148,163,184,0.85);
    letter-spacing: 0.01em;
    white-space: nowrap;
}
.sync-chip--warn {
    background: rgba(251,191,36,0.06);
    border-color: rgba(251,191,36,0.2);
    color: rgba(253,230,138,0.85);
}
.sync-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: rgba(52,211,153,0.9);
    box-shadow: 0 0 6px rgba(52,211,153,0.6);
    flex-shrink: 0;
    animation: dotPulse 2.5s ease-in-out infinite;
}
.sync-dot--warn {
    background: rgba(251,191,36,0.9);
    box-shadow: 0 0 6px rgba(251,191,36,0.6);
}
@keyframes dotPulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.35; }
}
/* ── TextArea 深色 ── */
div[data-testid="stTextArea"] textarea {
    background: rgba(8,12,24,0.7) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #f1f5f9 !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<script>
(function() {
  function init() {
    // 1. 數字計數動畫
    function animateCounters() {
      document.querySelectorAll('.metric-number').forEach(function(el) {
        var raw = el.textContent.trim();
        var isPercent = raw.includes('%');
        var num = parseFloat(raw.replace(/[,%\\s]/g, ''));
        if (isNaN(num) || num === 0) return;
        var decimals = isPercent ? 2 : 0;
        var duration = 1100;
        var start = null;
        el.textContent = isPercent ? '0.00%' : '0';
        function step(ts) {
          if (!start) start = ts;
          var p = Math.min((ts - start) / duration, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          var cur = num * eased;
          if (isPercent) {
            el.textContent = cur.toFixed(decimals) + '%';
          } else {
            el.textContent = Math.round(cur).toLocaleString();
          }
          if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      });
    }

    // 2. 捲動進場 (Intersection Observer)
    function setupScrollReveal() {
      var cards = document.querySelectorAll('.metric-card, .panel, .dark-panel');
      if (!cards.length) return;
      cards.forEach(function(el, i) {
        el.classList.add('sr-hidden');
        el.style.transitionDelay = (i * 60) + 'ms';
      });
      var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('sr-visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.08 });
      cards.forEach(function(el) { observer.observe(el); });
    }

    // 3. 卡片 hover 光暈跟隨滑鼠
    function setupCardGlow() {
      document.querySelectorAll('.metric-card').forEach(function(card) {
        card.addEventListener('mousemove', function(e) {
          var rect = card.getBoundingClientRect();
          var x = ((e.clientX - rect.left) / rect.width * 100).toFixed(1);
          var y = ((e.clientY - rect.top)  / rect.height * 100).toFixed(1);
          card.style.background =
            'radial-gradient(circle at ' + x + '% ' + y + '%, rgba(99,102,241,0.12) 0%, rgba(255,255,255,0.065) 40%, rgba(255,255,255,0.025) 100%)';
        });
        card.addEventListener('mouseleave', function() {
          card.style.background = '';
        });
      });
    }

    animateCounters();
    setupScrollReveal();
    setupCardGlow();
  }

  // Streamlit 會動態注入 DOM，稍延後執行
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { setTimeout(init, 600); });
  } else {
    setTimeout(init, 600);
  }
})();
</script>
""", unsafe_allow_html=True)

# =========================
# 工具
# =========================
def render_html_table(df: pd.DataFrame) -> str:
    headers = "".join(f'<th class="hth">{c}</th>' for c in df.columns)
    rows = ""
    for _, row in df.iterrows():
        cells = ""
        for i, val in enumerate(row):
            cls = "htd htd-title" if i == 0 else "htd"
            cells += f'<td class="{cls}">{val}</td>'
        rows += f'<tr class="htr">{cells}</tr>'
    return f'<div class="html-table-wrap"><table class="html-table"><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>'

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
    df = df.copy()
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)
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
        thumbnails = snippet.get("thumbnails", {})
        thumb = thumbnails.get("medium", thumbnails.get("default", {})).get("url", "")
        videos.append({
            "video_id": vid,
            "title": snippet.get("title", ""),
            "published_at": snippet.get("publishedAt", ""),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "thumbnail": thumb,
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
  <div style="display:flex;justify-content:space-between;align-items:center;gap:32px;">
    <div style="flex:1;min-width:0;">
      <div class="hero-kicker">Tea Creator Control Center</div>
      <div class="hero-title">茶葉創作者總控台</div>
      <div class="hero-sub">追蹤表現 &nbsp;·&nbsp; 洞察趨勢 &nbsp;·&nbsp; 規劃下一支</div>
    </div>
    <div style="display:flex;align-items:flex-end;gap:8px;padding-bottom:4px;flex-shrink:0;">
      <div style="width:3px;height:52px;background:linear-gradient(to top,rgba(99,102,241,0.9),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:34px;background:linear-gradient(to top,rgba(129,140,248,0.65),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:72px;background:linear-gradient(to top,rgba(99,102,241,0.85),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:44px;background:linear-gradient(to top,rgba(165,180,252,0.55),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:60px;background:linear-gradient(to top,rgba(99,102,241,0.75),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:28px;background:linear-gradient(to top,rgba(129,140,248,0.45),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:80px;background:linear-gradient(to top,rgba(99,102,241,1.0),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:38px;background:linear-gradient(to top,rgba(165,180,252,0.6),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:58px;background:linear-gradient(to top,rgba(99,102,241,0.7),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:22px;background:linear-gradient(to top,rgba(129,140,248,0.4),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:66px;background:linear-gradient(to top,rgba(99,102,241,0.8),transparent);border-radius:3px;"></div>
      <div style="width:3px;height:42px;background:linear-gradient(to top,rgba(165,180,252,0.5),transparent);border-radius:3px;"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 側邊欄
# =========================
with st.sidebar:
    st.markdown("""
    <div style="font-size:10px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;
         color:rgba(129,140,248,0.8);margin-bottom:16px;padding-bottom:8px;
         border-bottom:1px solid rgba(255,255,255,0.07);">導航</div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;flex-direction:column;gap:4px;">
      <a href="#section-metrics" style="color:#e2e8f0;font-size:13px;font-weight:500;text-decoration:none;padding:6px 10px;border-radius:8px;transition:background 0.2s;" onmouseover="this.style.background='rgba(99,102,241,0.2)';this.style.color='#a5b4fc'" onmouseout="this.style.background='transparent';this.style.color='#e2e8f0'">📊 數據總覽</a>
      <a href="#section-analysis" style="color:#e2e8f0;font-size:13px;font-weight:500;text-decoration:none;padding:6px 10px;border-radius:8px;transition:background 0.2s;" onmouseover="this.style.background='rgba(99,102,241,0.2)';this.style.color='#a5b4fc'" onmouseout="this.style.background='transparent';this.style.color='#e2e8f0'">🎬 影片分析</a>
      <a href="#section-charts" style="color:#e2e8f0;font-size:13px;font-weight:500;text-decoration:none;padding:6px 10px;border-radius:8px;transition:background 0.2s;" onmouseover="this.style.background='rgba(99,102,241,0.2)';this.style.color='#a5b4fc'" onmouseout="this.style.background='transparent';this.style.color='#e2e8f0'">📈 趨勢圖表</a>
      <a href="#section-tools" style="color:#e2e8f0;font-size:13px;font-weight:500;text-decoration:none;padding:6px 10px;border-radius:8px;transition:background 0.2s;" onmouseover="this.style.background='rgba(99,102,241,0.2)';this.style.color='#a5b4fc'" onmouseout="this.style.background='transparent';this.style.color='#e2e8f0'">🔧 創作工具</a>
      <a href="#section-export" style="color:#e2e8f0;font-size:13px;font-weight:500;text-decoration:none;padding:6px 10px;border-radius:8px;transition:background 0.2s;" onmouseover="this.style.background='rgba(99,102,241,0.2)';this.style.color='#a5b4fc'" onmouseout="this.style.background='transparent';this.style.color='#e2e8f0'">📥 數據導出</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:10px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;
         color:rgba(129,140,248,0.8);margin:24px 0 12px;padding-bottom:8px;
         border-bottom:1px solid rgba(255,255,255,0.07);">同步設定</div>
    """, unsafe_allow_html=True)
    max_results = st.number_input("抓取影片數量", min_value=5, max_value=50, value=12, step=5)

    st.markdown("""
    <div style="font-size:10px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;
         color:rgba(129,140,248,0.8);margin:24px 0 12px;padding-bottom:8px;
         border-bottom:1px solid rgba(255,255,255,0.07);">月度目標</div>
    """, unsafe_allow_html=True)
    goal_views = st.number_input("觀看數目標", min_value=0, value=st.session_state.get("goal_views", 10000), step=1000)
    goal_rate  = st.number_input("互動率目標 (%)", min_value=0.0, value=st.session_state.get("goal_rate", 2.0), step=0.1, format="%.1f")
    if st.button("儲存目標", width="stretch"):
        st.session_state["goal_views"] = goal_views
        st.session_state["goal_rate"]  = goal_rate
        st.success("已儲存")

cache_df, cache_saved_at = load_cache()

sync_col, status_col = st.columns([1, 3])

with sync_col:
    sync_now = st.button("同步最新資料", width="stretch")

if sync_now:
    with st.spinner("正在同步 YouTube 資料..."):
        try:
            fresh_df = fetch_youtube_videos(YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID, max_results=max_results)
            save_cache(fresh_df)
            cache_df = fresh_df
            cache_saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("同步完成")
        except Exception as e:
            st.error("同步失敗，已改用快取資料")
            st.code(str(e))

with status_col:
    if cache_saved_at:
        st.markdown(f"""
        <div class="sync-chip">
            <span class="sync-dot"></span>
            上次同步：{cache_saved_at}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sync-chip sync-chip--warn">
            <span class="sync-dot sync-dot--warn"></span>
            尚無快取資料，請先同步
        </div>
        """, unsafe_allow_html=True)

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
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
f1, f2 = st.columns([1, 3])

with f1:
    selected_type = st.selectbox("內容類型", type_options)

with f2:
    min_views = st.slider("最低觀看門檻", 0, int(df["views"].max()) if len(df) > 0 else 0, 0)
st.markdown('</div>', unsafe_allow_html=True)

filtered_df = df.copy()
if selected_type != "全部":
    filtered_df = filtered_df[filtered_df["type"] == selected_type]
filtered_df = filtered_df[filtered_df["views"] >= min_views]

# 篩選狀態列
_filter_chips = []
if selected_type != "全部":
    _filter_chips.append(f'<span class="filter-chip filter-chip--active">{selected_type}</span>')
if min_views > 0:
    _filter_chips.append(f'<span class="filter-chip filter-chip--active">觀看 ≥ {min_views:,}</span>')
_chip_html = "".join(_filter_chips) if _filter_chips else '<span class="filter-chip">全部影片</span>'
st.markdown(f"""
<div class="filter-status">
    <span class="filter-status-label">目前篩選</span>
    {_chip_html}
    <span class="filter-status-count">{len(filtered_df)} 支影片</span>
</div>
""", unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("目前沒有符合條件的資料")
    st.stop()

top_video = filtered_df.sort_values(["engagement_rate", "views"], ascending=False).iloc[0]
latest_info = analyze_latest_video(filtered_df)

# AI cache：只有 latest video 或篩選條件改變時才重新呼叫
_ai_cache_key = f"{latest_info['title']}_{selected_type}_{min_views}"
if st.session_state.get("_ai_cache_key") != _ai_cache_key:
    st.session_state["_ai_cache_key"] = _ai_cache_key
    st.session_state["next_idea"] = generate_next_idea_ai(filtered_df, latest_info)
next_idea = st.session_state.get("next_idea", "")

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
# 健康分數
# =========================
st.markdown('<div id="section-metrics"></div>', unsafe_allow_html=True)

def _calc_health(df, avg_r):
    # 互動率分（0-30）
    s_rate = min(avg_r / 3.0 * 30, 30)
    # 影片數分（0-20）：12支以上滿分
    s_count = min(len(df) / 12 * 20, 20)
    # 觀看中位數分（0-25）：中位數 ≥ 1000 滿分
    med = df["views"].median()
    s_views = min(med / 1000 * 25, 25)
    # 類型多樣性分（0-15）：3種以上滿分
    diversity = df["type"].nunique()
    s_div = min(diversity / 3 * 15, 15)
    # 近期活躍分（0-10）：最近一支距今 ≤ 14 天
    if df["published_at"].notna().any():
        _pub = df["published_at"].dropna()
        _pub = _pub.dt.tz_convert("UTC") if _pub.dt.tz is not None else _pub.dt.tz_localize("UTC")
        days_since = (pd.Timestamp.now(tz="UTC") - _pub.max()).days
        s_active = max(0, 10 - days_since * 0.7)
    else:
        s_active = 0
    total = int(s_rate + s_count + s_views + s_div + s_active)
    return total, {"互動率": (s_rate, 30), "影片量": (s_count, 20), "觀看表現": (s_views, 25), "內容多樣": (s_div, 15), "發片活躍": (s_active, 10)}

_health_score, _health_breakdown = _calc_health(filtered_df, avg_rate)
_h_color = "#6ee7b7" if _health_score >= 70 else "#fde68a" if _health_score >= 45 else "#fca5a5"
_h_label = "健康" if _health_score >= 70 else "尚可" if _health_score >= 45 else "需關注"

_breakdown_html = ""
for name, (val, max_val) in _health_breakdown.items():
    pct = int(val / max_val * 100)
    _breakdown_html += f"""
    <div>
        <div class="health-item-label">{name} <span style="float:right;color:rgba(255,255,255,0.5);">{int(val)}/{max_val}</span></div>
        <div class="health-item-bar"><div class="health-item-fill" style="width:{pct}%;background:linear-gradient(90deg,rgba(99,102,241,0.8),{_h_color});"></div></div>
    </div>"""

# 目標進度
_gv = st.session_state.get("goal_views", goal_views)
_gr = st.session_state.get("goal_rate", goal_rate)
_gv_pct = min(int(total_views / _gv * 100), 100) if _gv > 0 else 0
_gr_pct = min(int(avg_rate / _gr * 100), 100) if _gr > 0 else 0

st.markdown(f"""
<div class="health-panel">
    <div style="flex-shrink:0;text-align:center;">
        <div style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(148,163,184,0.65);margin-bottom:6px;">頻道健康</div>
        <div class="health-score-num" style="color:{_h_color};text-shadow:0 0 20px {_h_color}44;">{_health_score}</div>
        <div style="font-size:10px;font-weight:700;color:{_h_color};opacity:0.8;margin-top:2px;">{_h_label}</div>
    </div>
    <div style="width:1px;height:60px;background:rgba(255,255,255,0.07);flex-shrink:0;"></div>
    <div class="health-items">{_breakdown_html}</div>
    <div style="width:1px;height:60px;background:rgba(255,255,255,0.07);flex-shrink:0;"></div>
    <div style="flex-shrink:0;min-width:140px;">
        <div style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(148,163,184,0.65);margin-bottom:10px;">月度目標</div>
        <div style="font-size:11px;color:rgba(203,213,225,0.7);margin-bottom:3px;">觀看 {total_views:,} / {_gv:,}</div>
        <div class="goal-bar-wrap"><div class="goal-bar-fill" style="width:{_gv_pct}%;"></div></div>
        <div style="font-size:10px;color:rgba(148,163,184,0.5);margin-bottom:10px;">{_gv_pct}%</div>
        <div style="font-size:11px;color:rgba(203,213,225,0.7);margin-bottom:3px;">互動率 {avg_rate}% / {_gr}%</div>
        <div class="goal-bar-wrap"><div class="goal-bar-fill" style="width:{_gr_pct}%;"></div></div>
        <div style="font-size:10px;color:rgba(148,163,184,0.5);">{_gr_pct}%</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 指標卡
# =========================
c1, c2, c3, c4 = st.columns([1, 1, 1, 1.45])

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">頻道狀態</div>
        <div class="{status_badge}" style="margin-bottom:12px;">{status_text}</div>
        <div class="metric-note">{status_note}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">總觀看數</div>
        <div class="metric-number">{total_views:,}</div>
        <div class="metric-note">篩選條件下合計</div>
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
    <div class="metric-card-featured">
        <div class="featured-sub">最佳表現影片</div>
        <div class="featured-title">{top_video['title']}</div>
        <div class="metric-note" style="margin-top:12px;">
            觀看 {int(top_video['views']):,} &nbsp;·&nbsp;
            互動率 {top_video['engagement_rate']}%
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 最新影片分析 + 下一支建議
# =========================
st.markdown('<div id="section-analysis"></div>', unsafe_allow_html=True)
left, right = st.columns([1.02, 0.98])

with left:
    st.markdown('<div class="section-title">最新影片分析</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dark-panel">
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
    hot_show = hot_df[["title", "views", "likes", "engagement_rate"]].copy()
    hot_show["views"] = hot_show["views"].apply(lambda x: f"{int(x):,}")
    hot_show["engagement_rate"] = hot_show["engagement_rate"].apply(lambda x: f"{x}%")
    hot_show.columns = ["影片標題", "觀看", "按讚", "互動率"]
    st.markdown(
        '<div class="chart-label">爆款候選 &nbsp;<span class="chart-label-badge">TOP 5</span></div>'
        + render_html_table(hot_show),
        unsafe_allow_html=True
    )

with sum_right:
    top_show = filtered_df.sort_values("views", ascending=False).head(10)[["title", "views", "likes", "type"]].copy()
    top_show["views"] = top_show["views"].apply(lambda x: f"{int(x):,}")
    top_show.columns = ["影片標題", "觀看", "按讚", "類型"]
    st.markdown(
        '<div class="chart-label">觀看數排行 &nbsp;<span class="chart-label-badge">TOP 10</span></div>'
        + render_html_table(top_show),
        unsafe_allow_html=True
    )

# =========================
# 圖表
# =========================
st.markdown('<div id="section-charts"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">趨勢分析</div>', unsafe_allow_html=True)

chart_left, chart_right = st.columns(2)

_chart_layout = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='rgba(148,163,184,0.8)', size=12),
    xaxis=dict(
        gridcolor='rgba(255,255,255,0.05)',
        linecolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='rgba(148,163,184,0.65)', size=11),
        tickangle=-30,
    ),
    yaxis=dict(
        gridcolor='rgba(255,255,255,0.05)',
        linecolor='rgba(255,255,255,0.0)',
        tickfont=dict(color='rgba(148,163,184,0.65)', size=11),
    ),
    margin=dict(l=0, r=0, t=12, b=0),
    hoverlabel=dict(
        bgcolor='rgba(10,14,28,0.95)',
        bordercolor='rgba(99,102,241,0.3)',
        font=dict(color='#f1f5f9', size=12),
    ),
)

with chart_left:
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.markdown('<div class="chart-label">觀看數分佈 &nbsp;<span class="chart-label-badge">TOP 10</span></div>', unsafe_allow_html=True)
    chart_df = filtered_df.sort_values("views", ascending=False).head(10).copy()
    chart_df["short_title"] = chart_df["title"].str[:12] + "…"
    fig_bar = go.Figure(go.Bar(
        x=chart_df["short_title"],
        y=chart_df["views"],
        marker=dict(
            color=chart_df["views"],
            colorscale=[[0, "rgba(99,102,241,0.45)"], [1, "rgba(129,140,248,0.9)"]],
            line=dict(width=0),
            cornerradius=6,
        ),
        hovertemplate="<b>%{customdata}</b><br>觀看數：%{y:,}<extra></extra>",
        customdata=chart_df["title"],
    ))
    fig_bar.update_layout(**_chart_layout, height=280)
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with chart_right:
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.markdown('<div class="chart-label">觀看趨勢</div>', unsafe_allow_html=True)
    time_df = filtered_df.dropna(subset=["published_at"]).copy()
    if len(time_df) > 0:
        time_df["date"] = time_df["published_at"].dt.date
        trend_df = time_df.groupby("date")["views"].sum().reset_index()
        trend_df.columns = ["date", "views"]
        fig_line = go.Figure(go.Scatter(
            x=trend_df["date"],
            y=trend_df["views"],
            mode="lines+markers",
            line=dict(color="rgba(129,140,248,0.85)", width=2.5),
            marker=dict(size=5, color="rgba(165,180,252,0.9)", line=dict(width=0)),
            fill="tozeroy",
            fillcolor="rgba(99,102,241,0.08)",
            hovertemplate="%{x}<br>觀看：%{y:,}<extra></extra>",
        ))
        fig_line.update_layout(**_chart_layout, height=280)
        st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown('<div class="metric-note" style="padding:40px 0;text-align:center;">沒有時間資料</div>', unsafe_allow_html=True)
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
        ts_show = type_summary.copy()
        ts_show["平均觀看數"] = ts_show["平均觀看數"].apply(lambda x: f"{x:,}")
        ts_show["平均互動率"] = ts_show["平均互動率"].apply(lambda x: f"{x}%")
        ts_show = ts_show.rename(columns={"type": "類型"})[["類型", "平均觀看數", "平均互動率", "影片數"]]
        st.markdown(
            '<div class="chart-label">各類型數據摘要</div>' + render_html_table(ts_show),
            unsafe_allow_html=True
        )
    with col_b:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        st.markdown('<div class="chart-label">平均互動率比較</div>', unsafe_allow_html=True)
        fig_type = go.Figure(go.Bar(
            x=type_summary["type"],
            y=type_summary["平均互動率"],
            marker=dict(
                color=type_summary["平均互動率"],
                colorscale=[[0, "rgba(99,102,241,0.45)"], [1, "rgba(52,211,153,0.8)"]],
                line=dict(width=0),
                cornerradius=6,
            ),
            hovertemplate="<b>%{x}</b><br>互動率：%{y:.2f}%<extra></extra>",
        ))
        fig_type.update_layout(**_chart_layout, height=240)
        st.plotly_chart(fig_type, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 自動腳本
# =========================
st.markdown('<div id="section-tools"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">自動腳本推薦</div>', unsafe_allow_html=True)

if st.button("生成下一支自動腳本", width="stretch"):
    auto_script = generate_auto_script_ai(next_idea)
    st.markdown(f'<div class="panel" style="white-space:pre-wrap;line-height:1.9;">{auto_script}</div>', unsafe_allow_html=True)

# =========================
# 數據導出
# =========================
st.markdown('<div id="section-export"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">數據導出</div>', unsafe_allow_html=True)
st.markdown('<div class="export-panel">', unsafe_allow_html=True)
st.markdown('<div class="export-desc">將目前篩選條件下的影片數據匯出為不同格式</div>', unsafe_allow_html=True)

exp_col1, exp_col2, exp_col3 = st.columns([1, 1, 1])

with exp_col1:
    csv_data = export_to_csv(filtered_df[["title", "type", "views", "likes", "comments", "engagement_rate", "published_at"]])
    st.download_button(
        label="下載 CSV",
        data=csv_data,
        file_name=f"video_data_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        width="stretch"
    )

with exp_col2:
    excel_data = export_to_excel(filtered_df[["title", "type", "views", "likes", "comments", "engagement_rate", "published_at"]])
    st.download_button(
        label="下載 Excel",
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
        label="下載 PDF",
        data=pdf_data,
        file_name=f"report_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        width="stretch"
    )

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 內容日曆
# =========================
st.markdown('<div class="section-title">內容發布日曆</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-title">評論分析</div>', unsafe_allow_html=True)

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
# 關鍵字覆蓋追蹤
# =========================
# =========================
# 影片並排比較
# =========================
st.markdown('<div class="section-title">影片並排比較</div>', unsafe_allow_html=True)

_video_titles = filtered_df["title"].tolist()
_cmp_a_col, _cmp_b_col = st.columns(2)
with _cmp_a_col:
    _cmp_a = st.selectbox("影片 A", _video_titles, key="cmp_a")
with _cmp_b_col:
    _cmp_b = st.selectbox("影片 B", _video_titles, index=min(1, len(_video_titles)-1), key="cmp_b")

_ra = filtered_df[filtered_df["title"] == _cmp_a].iloc[0]
_rb = filtered_df[filtered_df["title"] == _cmp_b].iloc[0]

def _cmp_row(label, va, vb, higher_is_better=True):
    try:
        _fa, _fb = float(str(va).replace(",","")), float(str(vb).replace(",",""))
        a_win = (_fa > _fb) == higher_is_better
        b_win = (_fb > _fa) == higher_is_better
    except Exception:
        a_win = b_win = False
    a_style = "color:#6ee7b7;font-weight:700;" if a_win else "color:rgba(241,245,249,0.85);"
    b_style = "color:#6ee7b7;font-weight:700;" if b_win else "color:rgba(241,245,249,0.85);"
    return f"""
    <tr class="htr">
        <td class="htd" style="color:rgba(148,163,184,0.65);font-size:11px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;">{label}</td>
        <td class="htd" style="{a_style}text-align:center;">{va}</td>
        <td class="htd" style="{b_style}text-align:center;">{vb}</td>
    </tr>"""

_pub_a = _ra["published_at"].strftime("%Y-%m-%d") if pd.notna(_ra["published_at"]) else "—"
_pub_b = _rb["published_at"].strftime("%Y-%m-%d") if pd.notna(_rb["published_at"]) else "—"
_cmp_rows = (
    _cmp_row("觀看數", f"{int(_ra['views']):,}", f"{int(_rb['views']):,}") +
    _cmp_row("按讚數", int(_ra["likes"]), int(_rb["likes"])) +
    _cmp_row("留言數", int(_ra["comments"]), int(_rb["comments"])) +
    _cmp_row("互動率", f"{_ra['engagement_rate']}%", f"{_rb['engagement_rate']}%") +
    _cmp_row("發布日期", _pub_a, _pub_b, higher_is_better=False) +
    _cmp_row("類型", _ra["type"], _rb["type"])
)

_thumb_a = f'<img src="{_ra["thumbnail"]}" style="width:100%;border-radius:8px;" />' if "thumbnail" in _ra and _ra.get("thumbnail") else ""
_thumb_b = f'<img src="{_rb["thumbnail"]}" style="width:100%;border-radius:8px;" />' if "thumbnail" in _rb and _rb.get("thumbnail") else ""

st.markdown(f"""
<div class="html-table-wrap">
<table class="html-table">
  <thead><tr>
    <th class="hth" style="width:20%;"></th>
    <th class="hth" style="text-align:center;width:40%;">
      {_thumb_a}
      <div style="margin-top:6px;white-space:normal;line-height:1.4;">{_ra['title'][:30]}{"…" if len(_ra['title'])>30 else ""}</div>
    </th>
    <th class="hth" style="text-align:center;width:40%;">
      {_thumb_b}
      <div style="margin-top:6px;white-space:normal;line-height:1.4;">{_rb['title'][:30]}{"…" if len(_rb['title'])>30 else ""}</div>
    </th>
  </tr></thead>
  <tbody>{_cmp_rows}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">關鍵字覆蓋追蹤</div>', unsafe_allow_html=True)

kw_left, kw_right = st.columns([1, 1.6])

with kw_left:
    st.markdown('<div class="dark-panel">', unsafe_allow_html=True)
    st.markdown('<div class="chart-label">輸入想追蹤的關鍵字</div>', unsafe_allow_html=True)
    kw_input = st.text_area(
        label="關鍵字（每行一個）",
        placeholder="高山茶\n冬片\n台灣茶\n梨山\n手沖",
        height=160,
        label_visibility="collapsed"
    )
    run_kw = st.button("分析覆蓋率", width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)

with kw_right:
    if run_kw and kw_input.strip():
        keywords = [k.strip() for k in kw_input.strip().splitlines() if k.strip()]
        rows_html = ""
        covered_count = 0
        for kw in keywords:
            matched = filtered_df[filtered_df["title"].str.contains(kw, case=False, na=False)]
            count = len(matched)
            if count > 0:
                covered_count += 1
                status_html = f'<span class="badge-green">已涵蓋 {count} 支</span>'
                examples = "、".join(matched["title"].head(2).tolist())
                detail = f'<span style="color:rgba(148,163,184,0.7);font-size:12px;">{examples[:40]}{"…" if len(examples)>40 else ""}</span>'
            else:
                status_html = '<span class="badge-red">未涵蓋</span>'
                detail = '<span style="color:rgba(248,113,113,0.6);font-size:12px;">尚無相關影片，可考慮製作</span>'
            rows_html += f"""
            <div class="list-item" style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
                <div>
                    <span style="font-weight:600;color:#fff;">#{kw}</span>
                    <br>{detail}
                </div>
                <div style="flex-shrink:0;">{status_html}</div>
            </div>"""

        total = len(keywords)
        pct = round(covered_count / total * 100) if total > 0 else 0
        st.markdown(f"""
        <div class="dark-panel">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <div class="chart-label" style="margin:0;">覆蓋分析結果</div>
                <div style="font-size:22px;font-weight:800;color:#c7d2fe;text-shadow:0 0 20px rgba(99,102,241,0.5);">
                    {pct}% <span style="font-size:12px;font-weight:500;color:rgba(148,163,184,0.7);">覆蓋率</span>
                </div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border-radius:999px;height:4px;margin-bottom:16px;">
                <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,rgba(99,102,241,0.9),rgba(52,211,153,0.8));border-radius:999px;transition:width 0.6s ease;"></div>
            </div>
            {rows_html}
        </div>
        """, unsafe_allow_html=True)
    elif run_kw:
        st.warning("請輸入至少一個關鍵字")
    else:
        st.markdown("""
        <div class="dark-panel" style="display:flex;align-items:center;justify-content:center;min-height:180px;">
            <div style="text-align:center;color:rgba(148,163,184,0.5);">
                <div style="font-size:32px;margin-bottom:8px;">🔍</div>
                <div style="font-size:13px;">輸入關鍵字後點擊分析</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================
# 影片表現預測
# =========================
st.markdown('<div class="section-title">影片表現預測</div>', unsafe_allow_html=True)

pred_left, pred_right = st.columns([1, 1.6])

with pred_left:
    st.markdown('<div class="dark-panel">', unsafe_allow_html=True)
    st.markdown('<div class="chart-label">輸入想拍的影片資訊</div>', unsafe_allow_html=True)
    pred_title = st.text_input(
        "影片標題",
        placeholder="例：梨山高冷茶為什麼這麼貴？",
        label_visibility="collapsed"
    )
    pred_type = st.selectbox(
        "影片類型",
        ["教學型", "故事型", "推廣型", "開箱型", "其他"],
        label_visibility="collapsed"
    )
    run_pred = st.button("預測表現", width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)

with pred_right:
    if run_pred and pred_title.strip():
        avg_by_type = filtered_df.groupby("type").agg(
            avg_views=("views", "mean"),
            avg_rate=("engagement_rate", "mean"),
            count=("video_id", "count")
        ).reset_index()
        type_stats = avg_by_type[avg_by_type["type"] == pred_type]
        overall_avg_views = int(filtered_df["views"].mean())
        overall_avg_rate = round(filtered_df["engagement_rate"].mean(), 2)
        if len(type_stats) > 0:
            type_avg_views = int(type_stats["avg_views"].iloc[0])
            type_avg_rate = round(type_stats["avg_rate"].iloc[0], 2)
        else:
            type_avg_views = overall_avg_views
            type_avg_rate = overall_avg_rate

        top5_titles = "\n".join(
            filtered_df.sort_values("engagement_rate", ascending=False)
            .head(5)["title"].tolist()
        )

        if client:
            with st.spinner("AI 預測中…"):
                pred_prompt = f"""你是台灣 YouTube 數據分析師，專門分析茶葉頻道。

頻道歷史數據（目前篩選條件下）：
- 平均觀看數：{overall_avg_views:,}
- 平均互動率：{overall_avg_rate}%
- {pred_type} 類型平均觀看：{type_avg_views:,}，平均互動率：{type_avg_rate}%

表現最好的 5 支影片標題：
{top5_titles}

我想拍這支影片：
標題：{pred_title}
類型：{pred_type}

請根據數據，用繁體中文給我：
1. 預測觀看數範圍（樂觀/合理/保守）
2. 預測互動率範圍
3. 這個標題的優勢（1-2點）
4. 可能的弱點或風險（1-2點）
5. 一個具體的標題優化建議

格式簡潔，每點一行，不要廢話。"""
                try:
                    res = client.responses.create(model="gpt-4o-mini", input=pred_prompt)
                    pred_result = res.output_text
                except Exception:
                    pred_result = None
        else:
            pred_result = None

        views_lo = int(type_avg_views * 0.6)
        views_mid = int(type_avg_views * 1.0)
        views_hi = int(type_avg_views * 1.6)
        rate_lo = round(type_avg_rate * 0.7, 2)
        rate_hi = round(type_avg_rate * 1.4, 2)

        st.markdown(f"""
        <div class="dark-panel">
            <div class="chart-label" style="margin-bottom:16px;">「{pred_title[:20]}{"…" if len(pred_title)>20 else ""}」預測結果</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
                <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);border-radius:14px;padding:14px 16px;">
                    <div style="font-size:10px;font-weight:700;letter-spacing:0.12em;color:rgba(129,140,248,0.8);text-transform:uppercase;margin-bottom:6px;">預測觀看數</div>
                    <div style="font-size:20px;font-weight:800;color:#c7d2fe;text-shadow:0 0 16px rgba(99,102,241,0.4);">{views_lo:,} – {views_hi:,}</div>
                    <div style="font-size:11px;color:rgba(148,163,184,0.6);margin-top:4px;">合理中位：{views_mid:,}</div>
                </div>
                <div style="background:rgba(52,211,153,0.06);border:1px solid rgba(52,211,153,0.18);border-radius:14px;padding:14px 16px;">
                    <div style="font-size:10px;font-weight:700;letter-spacing:0.12em;color:rgba(52,211,153,0.8);text-transform:uppercase;margin-bottom:6px;">預測互動率</div>
                    <div style="font-size:20px;font-weight:800;color:#6ee7b7;text-shadow:0 0 16px rgba(52,211,153,0.3);">{rate_lo}% – {rate_hi}%</div>
                    <div style="font-size:11px;color:rgba(148,163,184,0.6);margin-top:4px;">同類型平均：{type_avg_rate}%</div>
                </div>
            </div>
            {"<div style='white-space:pre-wrap;font-size:13.5px;line-height:1.85;color:rgba(226,232,240,0.88);'>" + pred_result + "</div>" if pred_result else "<div style='color:rgba(148,163,184,0.5);font-size:13px;'>（未設定 OpenAI API，僅顯示統計預測）</div>"}
        </div>
        """, unsafe_allow_html=True)
    elif run_pred:
        st.warning("請輸入影片標題")
    else:
        st.markdown("""
        <div class="dark-panel" style="display:flex;align-items:center;justify-content:center;min-height:180px;">
            <div style="text-align:center;color:rgba(148,163,184,0.5);">
                <div style="font-size:32px;margin-bottom:8px;">📊</div>
                <div style="font-size:13px;">輸入標題與類型後點擊預測</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
# 最佳發片時段
# =========================
st.markdown('<div class="section-title">最佳發片時段</div>', unsafe_allow_html=True)

_time_df = filtered_df.dropna(subset=["published_at"]).copy()
if len(_time_df) >= 3:
    _time_df["hour"] = _time_df["published_at"].dt.hour
    _time_df["weekday"] = _time_df["published_at"].dt.weekday
    _weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    _time_df["weekday_name"] = _time_df["weekday"].map(lambda x: _weekday_names[x])
    _pivot = _time_df.pivot_table(values="engagement_rate", index="weekday_name", columns="hour", aggfunc="mean")
    _pivot = _pivot.reindex([d for d in _weekday_names if d in _pivot.index])
    _heat_left, _heat_right = st.columns([2, 1])
    with _heat_left:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        st.markdown('<div class="chart-label">星期 × 時段 互動率熱力圖</div>', unsafe_allow_html=True)
        fig_heat = go.Figure(go.Heatmap(
            z=_pivot.values,
            x=[f"{h}:00" for h in _pivot.columns],
            y=list(_pivot.index),
            colorscale=[[0,"rgba(8,12,24,0.9)"],[0.5,"rgba(99,102,241,0.6)"],[1,"rgba(52,211,153,0.9)"]],
            hovertemplate="<b>%{y} %{x}</b><br>平均互動率：%{z:.2f}%<extra></extra>",
            showscale=True,
            colorbar=dict(
                thickness=10, len=0.8,
                tickfont=dict(color="rgba(148,163,184,0.7)", size=10),
                outlinewidth=0,
            ),
        ))
        fig_heat.update_layout(**_chart_layout, height=240)
        st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with _heat_right:
        _best_row = _time_df.loc[_time_df["engagement_rate"].idxmax()]
        _best_day = _weekday_names[int(_best_row["weekday"])]
        _best_hour = int(_best_row["hour"])
        _avg_by_day = _time_df.groupby("weekday_name")["engagement_rate"].mean().sort_values(ascending=False)
        _top_day = _avg_by_day.index[0] if len(_avg_by_day) > 0 else "—"
        st.markdown(f"""
        <div class="dark-panel" style="height:100%;">
            <div class="featured-sub">推薦發片時段</div>
            <div style="font-size:28px;font-weight:800;color:#c7d2fe;text-shadow:0 0 20px rgba(99,102,241,0.4);margin:8px 0;">
                {_best_day} {_best_hour}:00
            </div>
            <div class="metric-note">歷史互動率最高的時段</div>
            <div style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06);">
                <div class="metric-label">互動最佳星期</div>
                <div style="font-size:18px;font-weight:700;color:#6ee7b7;">{_top_day}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown('<div class="dark-panel" style="color:rgba(148,163,184,0.5);text-align:center;padding:32px;">資料不足，需至少 3 支有時間戳記的影片</div>', unsafe_allow_html=True)

# =========================
# 影片衰退警示
# =========================
st.markdown('<div class="section-title">影片狀態警示</div>', unsafe_allow_html=True)

_now = pd.Timestamp.now(tz="UTC")
_alert_df = filtered_df.copy()
_pub = _alert_df["published_at"].dt.tz_convert("UTC") if _alert_df["published_at"].dt.tz is not None else _alert_df["published_at"].dt.tz_localize("UTC")
_alert_df["days_ago"] = (_now - _pub).dt.days

_long_tail = _alert_df[(_alert_df["days_ago"] > 30) & (_alert_df["views"] > _alert_df["views"].quantile(0.7))].sort_values("views", ascending=False).head(3)
_underperform = _alert_df[(_alert_df["days_ago"] <= 14) & (_alert_df["engagement_rate"] < _alert_df["engagement_rate"].median())].sort_values("engagement_rate").head(3)

_al, _ar = st.columns(2)
with _al:
    st.markdown('<div class="chart-label">長尾潛力影片 <span class="chart-label-badge">仍在成長</span></div>', unsafe_allow_html=True)
    if len(_long_tail) > 0:
        _tail_rows = ""
        for _, r in _long_tail.iterrows():
            _tail_rows += f"""
            <div class="list-item" style="display:flex;justify-content:space-between;align-items:center;">
                <div style="flex:1;min-width:0;">
                    <div style="font-weight:600;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{r['title'][:28]}{"…" if len(r['title'])>28 else ""}</div>
                    <div style="font-size:11px;color:rgba(148,163,184,0.6);margin-top:2px;">{int(r['days_ago'])} 天前發布</div>
                </div>
                <div style="text-align:right;flex-shrink:0;margin-left:12px;">
                    <div style="font-size:15px;font-weight:700;color:#6ee7b7;">{int(r['views']):,}</div>
                    <div style="font-size:10px;color:rgba(110,231,183,0.6);">觀看</div>
                </div>
            </div>"""
        st.markdown(f'<div class="dark-panel">{_tail_rows}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="dark-panel" style="color:rgba(148,163,184,0.4);padding:24px;text-align:center;">暫無符合條件的長尾影片</div>', unsafe_allow_html=True)

with _ar:
    st.markdown('<div class="chart-label">近期待優化影片 <span class="chart-label-badge" style="background:rgba(248,113,113,0.12);color:rgba(252,165,165,0.9);border-color:rgba(248,113,113,0.25);">互動偏低</span></div>', unsafe_allow_html=True)
    if len(_underperform) > 0:
        _under_rows = ""
        for _, r in _underperform.iterrows():
            _under_rows += f"""
            <div class="list-item" style="display:flex;justify-content:space-between;align-items:center;">
                <div style="flex:1;min-width:0;">
                    <div style="font-weight:600;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{r['title'][:28]}{"…" if len(r['title'])>28 else ""}</div>
                    <div style="font-size:11px;color:rgba(148,163,184,0.6);margin-top:2px;">{int(r['days_ago'])} 天前發布</div>
                </div>
                <div style="text-align:right;flex-shrink:0;margin-left:12px;">
                    <div style="font-size:15px;font-weight:700;color:#fca5a5;">{r['engagement_rate']}%</div>
                    <div style="font-size:10px;color:rgba(252,165,165,0.6);">互動率</div>
                </div>
            </div>"""
        st.markdown(f'<div class="dark-panel">{_under_rows}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="dark-panel" style="color:rgba(148,163,184,0.4);padding:24px;text-align:center;">近期影片表現都不錯</div>', unsafe_allow_html=True)

# =========================
# 原始資料表
# =========================
st.markdown('<div class="section-title">影片資料表</div>', unsafe_allow_html=True)

show_df = filtered_df.sort_values("published_at", ascending=False).copy()
has_thumb = "thumbnail" in show_df.columns
rows_html = ""
for _, row in show_df.iterrows():
    thumb_html = f'<img src="{row["thumbnail"]}" style="width:88px;height:50px;object-fit:cover;border-radius:6px;display:block;" />' if has_thumb and row.get("thumbnail") else '<div style="width:88px;height:50px;background:rgba(255,255,255,0.06);border-radius:6px;"></div>'
    pub = row["published_at"].strftime("%Y-%m-%d") if pd.notna(row["published_at"]) else "—"
    rows_html += f"""
    <tr class="htr">
        <td class="htd" style="padding:8px 12px;">{thumb_html}</td>
        <td class="htd htd-title" style="max-width:220px;">
            <a href="{row['url']}" target="_blank" style="color:rgba(255,255,255,0.9);text-decoration:none;">{row['title']}</a>
        </td>
        <td class="htd"><span class="badge-blue" style="font-size:10px;padding:3px 8px;">{row['type']}</span></td>
        <td class="htd">{int(row['views']):,}</td>
        <td class="htd">{int(row['likes'])}</td>
        <td class="htd">{row['engagement_rate']}%</td>
        <td class="htd" style="color:rgba(148,163,184,0.6);">{pub}</td>
    </tr>"""
st.markdown(f"""
<div class="html-table-wrap">
<table class="html-table">
  <thead><tr>
    <th class="hth">縮圖</th>
    <th class="hth">影片標題</th>
    <th class="hth">類型</th>
    <th class="hth">觀看</th>
    <th class="hth">按讚</th>
    <th class="hth">互動率</th>
    <th class="hth">發布日期</th>
  </tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ 環境變數檢查"):
    st.write("YOUTUBE_API_KEY 是否有讀到：", bool(YOUTUBE_API_KEY))
    st.write("YOUTUBE_CHANNEL_ID：", YOUTUBE_CHANNEL_ID)
    st.write("OPENAI_API_KEY 是否有讀到：", bool(OPENAI_API_KEY))
