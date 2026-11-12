"""
ページの準備(全ページで共通)

どのページも最初にこれを呼び、ページ設定・CSS・見出しの形をそろえる。
見出しは、サイト名を大きく出し、Home 以外はその下に絵文字付きのページ名を出す
(2026-10-21 決定。裏ラジアーカイブスの set_site_config() と同じ考え方)。
"""

import logging
import threading
from typing import Optional

import streamlit as st

from src.config.logging_config import setup_logging
from src.config.settings import Config

logger = logging.getLogger(__name__)

# 全ページの一番上に出すサイト名
SITE_HEADING = "しのうたタイム👻🫧"

# CSS を読めなかったときに画面に出す案内(公開の画面なので、パスや例外の文は出さない)
CSS_ERROR_MESSAGE = "スタイルを読み込めませんでした。表示が崩れることがあります。"

# ログの初期化を済ませたか。Streamlit はページを開くたびにスクリプトを流し直すが、
# このモジュールは読み込んだまま残るので、プロセスに1回だけになる
_logging_ready = False
_logging_lock = threading.Lock()


def ensure_logging() -> None:
    """
    ログの初期化(src/config/logging_config.py の setup_logging)を、プロセスに1回だけ行う

    どのページを最初に開いても(Song List や Information を直接開いても)初期化される。
    訪問のたびにハンドラを付け直さない。
    """
    global _logging_ready
    if _logging_ready:
        return
    with _logging_lock:
        if not _logging_ready:
            setup_logging()
            _logging_ready = True


def page_tab_title(config: Config, page_name: Optional[str]) -> str:
    """ブラウザのタブの名前(Home はサイト名だけ、ほかは「ページ名 - サイト名」)"""
    return f"{page_name} - {config.page_title}" if page_name else config.page_title


def load_css(css_file_path: str) -> None:
    """
    共通の CSS(src/ui/styles/style.css)を読み込む。読めなければ短い案内を出して続ける

    公開の画面なので、ファイルのパスや例外の文は画面に出さない(Home・Song List の読み込みの失敗と同じ)。
    詳しいことはログに出す。
    """
    try:
        with open(css_file_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"CSS の読み込みに失敗しました: {css_file_path}: {e}", exc_info=True)
        st.error(CSS_ERROR_MESSAGE)


def setup_page(page_name: Optional[str] = None, icon: str = "") -> Config:
    """
    ページの準備: ログの初期化(プロセスに1回)・ページ設定・共通の CSS・見出し

    st.set_page_config は最初の Streamlit の命令である必要があるので、各ページの最初に呼ぶ。

    Args:
        page_name: ページ名(Home は None)。タブの名前と、サイト名の下の見出しに使う
        icon: ページ名の前に付ける絵文字

    Returns:
        設定(Config.from_env() の結果。ページの中ではこれを使う)
    """
    ensure_logging()
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
