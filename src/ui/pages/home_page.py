"""
ホーム画面ページ

アプリケーションのメインページ（ホーム画面）の表示ロジックを担当します。
データはデータモデル v2(data/v2/)の歌唱の一覧(views.build_performance_view)を読みます。
"""

import html
import logging
from typing import Optional

import streamlit as st
import pandas as pd

from src.config.settings import Config
from src.core.text import normalize_for_match
from src.ui.components.footer import display_footer
from src.ui.components import (
    render_search_form,
    render_results_table,
    render_pagination,
)
from src.ui.v2_data import load_performance_view

# ロガーの設定
logger = logging.getLogger(__name__)

# 表の列(表示の見出し)
TABLE_COLUMNS = ["配信日", "No.", "曲名", "アーティスト", "種類", "リンク"]

# 読み込みに失敗したときの案内(Song List と同じ)
LOAD_ERROR_HINT = "時間をおいて、ページを開き直してください。"

# Markdown で書式として効く記号
_MARKDOWN_SPECIALS = set("\\`*_{}[]()#+-.!|<>~")


def escape_markdown(text: str) -> str:
    """Markdown の記号の前にバックスラッシュを付け、入力した文字のまま表示されるようにする"""
    return "".join(f"\\{ch}" if ch in _MARKDOWN_SPECIALS else ch for ch in text)


def filter_view(view: pd.DataFrame, query: str, include_title: bool) -> pd.DataFrame:
    """
    検索語で歌唱の一覧を絞る

    曲名・アーティスト(読みを含む)、include_title のときは配信のタイトルも対象にする。
    検索語も一覧の検索用の列と同じく normalize_for_match してから部分一致で照合する。
    空(空白だけを含む)の検索語なら全件を返す。
    """
    needle = normalize_for_match(query)
    if not needle:
        return view
    column = "search" if include_title else "search_song"
    return view[view[column].str.contains(needle, regex=False)]


def data_as_of(view: pd.DataFrame) -> str:
    """
    データの時点の表示(「データは YYYY/MM/DD の配信まで(歌唱 N 件)」)

    日付は一覧の配信日の最大値、件数は一覧(画面に出す歌唱)の件数。一覧が空なら空文字。
    """
    if view.empty:
        return ""
    latest = view["date"].max().replace("-", "/")
    return f"データは {latest} の配信まで(歌唱 {len(view):,} 件)"


def build_table(view: pd.DataFrame) -> pd.DataFrame:
    """
    表に出す形にする(列は TABLE_COLUMNS)

    アーティストとリンクは HTML に組み立てる(データ由来の文字列はエスケープする)。
    ほかの列は render_results_table がエスケープする。
    """
    return pd.DataFrame({
        "配信日": view["date"].str.replace("-", "/"),
        "No.": view["no"],
        "曲名": view["display_title"],
        "アーティスト": view["artist"].map(lambda a: f'<div class="artist-cell">{html.escape(a)}</div>'),
        "種類": view["type_label"],
        "リンク": [
            f'<a href="{html.escape(u, quote=True)}" target="_blank" rel="noopener">{html.escape(label)}</a>'
            if u else ""
            for u, label in zip(view["link"], view["link_label"])
        ],
    })


class HomePage:
    """
    ホーム画面クラス

    ホーム画面の描画とインタラクションを管理します。
    """

    def __init__(self, config: Optional[Config] = None):
        """
        初期化

        Args:
            config: 設定(Home.py の setup_page() が読んだもの)。渡されなければ環境変数から読む
        """
        self.config = config or Config.from_env()
        logger.info("HomePage initialized")

    def run(self):
        """
        ホーム画面を実行・表示する

        ページ設定・共通の CSS・サイト名の見出しは、Home.py が先に setup_page() で出している。
        """
        self._render_header()

        # データ読み込み
        try:
            view = load_performance_view()
        except Exception as e:  # DataLoadError のほか、集計中の想定外の失敗も画面に出して止める
            logger.error(f"データの読み込み中にエラーが発生しました: {e}", exc_info=True)
            self._handle_error()
        else:
            self._handle_search_and_display(view)

        display_footer()

    def _render_header(self):
        """ヘッダー領域の描画(サイト名の見出しの下のお知らせと説明)"""
        st.info("左のサイドバーから「Song List beta」を選択して、楽曲リストをご覧ください。")
        st.markdown(
            """
            こちらはVTuber「[幽音しの](https://www.774.ai/talent/shino-kasukane)」さんの配信で歌われた楽曲をまとめた非公式データベースです。
            曲名、アーティスト、ライブ配信タイトルで検索できます。YouTubeリンクから該当の歌唱箇所に直接飛べます。
            """
        )
        st.markdown("---")

    def _handle_search_and_display(self, view: pd.DataFrame):
        """
        検索処理と結果表示の制御

        session_state には検索語・チェックボックス・表示件数だけを持ち、結果は毎回 view から絞る。

        Args:
            view: 歌唱の一覧(全件)
        """
        # セッション状態の初期化
        if "search_query" not in st.session_state:
            st.session_state.search_query = ""
        if "include_live_title" not in st.session_state:
            st.session_state.include_live_title = True
        if "display_limit" not in st.session_state:
            st.session_state.display_limit = self.config.initial_display_limit

        # データの時点(いつの配信までのデータか)
        as_of = data_as_of(view)
        if as_of:
            st.caption(as_of)

        # 検索フォームの表示
        current_input, current_checkbox_value, search_button = render_search_form(
            default_query=st.session_state.search_query,
            include_live_title=st.session_state.include_live_title
        )

        # 検索ボタンが押されたら、検索条件を保存して表示件数を戻す
        if search_button:
            st.session_state.search_query = current_input
            st.session_state.include_live_title = current_checkbox_value
            st.session_state.display_limit = self.config.initial_display_limit

        query = st.session_state.search_query
        filtered = filter_view(view, query, st.session_state.include_live_title)
        if normalize_for_match(query):
            st.write(f"「{escape_markdown(query)}」で検索した結果: {len(filtered)}件")
        else:
            st.write("検索キーワードが入力されていません。全件表示します。")

        # 結果テーブル表示
        self._render_results(filtered)

    def _render_results(self, view: pd.DataFrame):
        """結果テーブルとページネーションの表示"""
        shown = view.head(st.session_state.display_limit)
        render_results_table(
            build_table(shown),
            TABLE_COLUMNS,
            {c: c for c in TABLE_COLUMNS},
            html_columns={"アーティスト", "リンク"},
        )

        # ページネーションの表示(ボタンの on_click で display_limit を増やす。st.rerun は要らない)
        render_pagination(
            total_count=len(view),
            state_key="display_limit",
            increment=self.config.display_increment,
        )

    def _handle_error(self):
        """
        エラー時の表示

        公開の画面なので、例外のメッセージ(サーバー上のパスを含む)は出さず、短い案内だけにする。
        詳しいことはログに出ている(run の logger.error)。
        """
        st.error("データの読み込みまたは処理中にエラーが発生しました。")
        st.info(LOAD_ERROR_HINT)
