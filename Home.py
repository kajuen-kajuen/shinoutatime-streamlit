"""
しのうたタイム - メインページ

VTuber「幽音しの」さんの配信で歌唱された楽曲を検索・閲覧できる
非公式ファンサイトのメインページです。

主な機能:
- 楽曲データの読み込みと表示
- キーワード検索（曲名、アーティスト、配信タイトル）
- YouTubeタイムスタンプ付きリンク生成
- 段階的表示（25件ずつ）
- 曲目番号の自動生成

データソース:
- data/M_YT_LIVE.TSV: 配信情報
- data/M_YT_LIVE_TIMESTAMP.TSV: 楽曲タイムスタンプ情報
"""

import streamlit as st
from src.config import setup_logging
from src.config.settings import Config
from src.ui.pages.home_page import HomePage

# ロギングの初期化（アプリケーション起動時に一度だけ実行）
if "logging_initialized" not in st.session_state:
    setup_logging()
    st.session_state.logging_initialized = True

# 設定の読み込み
config = Config.from_env()

# ページ設定
st.set_page_config(
    page_title=config.page_title,
    page_icon=config.page_icon,
    layout=config.layout,
)

if __name__ == "__main__":
    home_page = HomePage()
    home_page.run()
