"""
ページの準備(全ページで共通)

どのページも最初にこれを呼び、ページ設定・CSS・見出しの形をそろえる。
見出しは、サイト名を大きく出し、Home 以外はその下に絵文字付きのページ名を出す
(2026-10-21 決定。裏ラジアーカイブスの set_site_config() と同じ考え方)。
"""

import logging
from typing import Optional

import streamlit as st

from src.config.settings import Config

logger = logging.getLogger(__name__)

# 全ページの一番上に出すサイト名
SITE_HEADING = "しのうたタイム👻🫧"


def page_tab_title(config: Config, page_name: Optional[str]) -> str:
    """ブラウザのタブの名前(Home はサイト名だけ、ほかは「ページ名 - サイト名」)"""
    return f"{page_name} - {config.page_title}" if page_name else config.page_title


def load_css(css_file_path: str) -> None:
    """共通の CSS(src/ui/styles/style.css)を読み込む。読めなければエラーを出して続ける"""
    try:
        with open(css_file_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"エラー: {css_file_path} が見つかりません。")
    except Exception as e:
        logger.error(f"CSS の読み込みに失敗しました: {e}", exc_info=True)
        st.error(f"エラー: {css_file_path} の読み込み中に問題が発生しました: {e}")


def setup_page(page_name: Optional[str] = None, icon: str = "") -> Config:
    """
    ページの準備: ページ設定・共通の CSS・見出し

    st.set_page_config は最初の Streamlit の命令である必要があるので、各ページの最初に呼ぶ。

    Args:
        page_name: ページ名(Home は None)。タブの名前と、サイト名の下の見出しに使う
        icon: ページ名の前に付ける絵文字

    Returns:
        設定(Config.from_env() の結果。ページの中ではこれを使う)
    """
    config = Config.from_env()
    st.set_page_config(
        page_title=page_tab_title(config, page_name),
        page_icon=config.page_icon,
        layout=config.layout,
    )
    load_css(config.css_file_path)
    st.title(SITE_HEADING)
    if page_name:
        st.header(f"{icon} {page_name}".strip())
    return config
