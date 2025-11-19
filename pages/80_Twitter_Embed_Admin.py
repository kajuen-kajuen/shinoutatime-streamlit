"""
Twitter埋め込みコード管理ページ

このページは、Twitter埋め込みコードを管理するための管理画面を提供します。
管理者認証が必要です。

要件: 4.1, 4.2, 4.3, 4.4, 4.5
"""

import streamlit as st
from footer import display_footer
from src.ui.twitter_embed_admin import render_twitter_embed_admin
from src.config import setup_logging

# ロギングの初期化
if "logging_initialized" not in st.session_state:
    setup_logging()
    st.session_state.logging_initialized = True

# ページ設定
st.set_page_config(
    page_title="Twitter埋め込みコード管理 - しのうたタイム",
    page_icon="🐦",
    layout="wide",
)

# カスタムCSSの適用
try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass
except Exception:
    pass

# 管理画面を表示
render_twitter_embed_admin()

# フッターの表示
st.markdown("---")
display_footer()
