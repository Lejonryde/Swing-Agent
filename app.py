import os
import json
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="SWINGKINGS // ARGON v2.0", page_icon="👑", layout="wide")

CSS_STYLE = """
<style>
html, body, [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #05070b, #0a0e17, #0f172a) !important; color: #e2e8f0 !important; background-attachment: fixed; }
[data-testid="stSidebar"] { background-color: #090d14 !important; border-right: 1px solid #1e293b !important; }
.logo-header-box { background: rgba(15, 23, 42, 0.95); border: 2px solid #38bdf8; box-shadow: 0 0 35px rgba(56, 189, 248, 0.25); border-radius: 16px; padding: 24px; margin-bottom: 25px; text-align: center; }
.logo-title { font-size: 2.8rem; font-weight: 900; letter-spacing: 3px; background: linear-gradient(90deg, #38bdf8, #a855f7, #f43f5e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
.logo-sub { color: #94a3b8; font-size: 0.88rem; letter-spacing: 2px; margin-top: 8px; text-transform: uppercase; }
.stock-card { background: rgba(17, 24, 39, 0.92); border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
.argon-badge { background: linear-gradient(90deg, #0284c7, #2563eb); color: #ffffff; padding: 3px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; float: right; }
.bear-badge { background: linear-gradient(90deg, #dc2626, #991b1b
