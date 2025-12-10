"""
ホーム画面ページ

アプリケーションのメインページ（ホーム画面）の表示ロジックを担当します。
"""

import logging
import streamlit as st
import pandas as pd
from typing import Optional

from src.config.settings import Config
from src.services.data_service import DataService
from src.core.data_pipeline import DataPipeline
from src.services.search_service import SearchService
from src.ui.components.footer import display_footer
from src.ui.components import (
    render_search_form,
    render_results_table,
    render_pagination,
)

# ロガーの設定
logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600, show_spinner="データを読み込み中...")
def load_and_process_data(
    lives_path: str,
    songs_path: str,
    enable_cache: bool
) -> Optional[pd.DataFrame]:
    """
    データを読み込み、処理する
    
    DataPipelineを使用してデータの読み込み、結合、変換、ソートを実行します。
    Streamlitのキャッシュ機能により、同じパラメータでの再実行を防ぎます。
    
    Args:
        lives_path: 配信データファイルのパス
        songs_path: 楽曲データファイルのパス
        enable_cache: キャッシュを有効にするかどうか
    
    Returns:
        処理済みDataFrame。エラー時はNone
        
    Note:
        - TTL（Time To Live）は3600秒（1時間）
        - データファイルのパスが変更された場合、自動的に再読み込みされる
        - キャッシュにより初期表示時間を3秒以内に保つ
        
    要件: 12.1, 12.2, 12.6
    """
    # キャッシュされた関数内でConfigを再作成するのは避けたいため、
    # パスなどのプリミティブな引数を受け取る設計を維持する
    # しかし、内部でDataService/Pipelineを初期化するためにConfigが必要
    # ここでは都度Configを作成するか、引数で必要な情報だけ渡すが、
    # Config.from_env()は軽量なので許容する
    config = Config.from_env()
    
    data_service = DataService(config)
    pipeline = DataPipeline(data_service, config)
    return pipeline.execute()


class HomePage:
    """
    ホーム画面クラス
    
    ホーム画面の描画とインタラクションを管理します。
    """
    
    def __init__(self):
        """初期化"""
        self.config = Config.from_env()
        self.search_service = SearchService()
        logger.info("HomePage initialized")

    def run(self):
        """
        ホーム画面を実行・表示する
        """
        self._load_css()
        self._render_header()
        
        # データ読み込み
        df_full = load_and_process_data(
            self.config.lives_file_path,
            self.config.songs_file_path,
            self.config.enable_cache
        )
        
        if df_full is not None:
            self._handle_search_and_display(df_full)
        else:
            self._handle_error()
            
        display_footer()

    def _load_css(self):
        """カスタムCSSの適用"""
        try:
            with open(self.config.css_file_path, encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            st.error(f"エラー: {self.config.css_file_path} が見つかりません。")
        except Exception as e:
            st.error(f"エラー: {self.config.css_file_path} の読み込み中に問題が発生しました: {e}")

    def _render_header(self):
        """ヘッダー領域の描画"""
        st.title("しのうたタイム👻🫧")
        st.info("左のサイドバーから「Song List beta」を選択して、楽曲リストをご覧ください。")
        st.markdown(
            """
            こちらはVTuber「[幽音しの](https://www.774.ai/talent/shino-kasukane)」さんの配信で歌われた楽曲をまとめた非公式データベースです。
            曲名、アーティスト、ライブ配信タイトルで検索できます。YouTubeリンクから該当の歌唱箇所に直接飛べます。
            """
        )
        st.markdown("---")

    def _handle_search_and_display(self, df_full: pd.DataFrame):
        """
        検索処理と結果表示の制御
        
        Args:
            df_full: 全データ
        """
        # セッション状態の初期化
        if "search_query" not in st.session_state:
            st.session_state.search_query = ""
        if "filtered_df" not in st.session_state:
            st.session_state.filtered_df = df_full.copy()
        if "include_live_title" not in st.session_state:
            st.session_state.include_live_title = True
        if "display_limit" not in st.session_state:
            st.session_state.display_limit = self.config.initial_display_limit
        
        # 検索フォームの表示
        current_input, current_checkbox_value, search_button = render_search_form(
            default_query=st.session_state.search_query,
            include_live_title=st.session_state.include_live_title
        )
        
        # 検索ロジック
        if search_button:
            self._perform_search(df_full, current_input, current_checkbox_value)
        elif st.session_state.search_query:
            # 既に検索済みの状態の表示更新（リロード時など）
            st.write(
                f"「{st.session_state.search_query}」で検索した結果: "
                f"{len(st.session_state.filtered_df)}件"
            )
        else:
            # 未検索（全件）
            st.session_state.filtered_df = df_full.copy()
            st.write("検索キーワードが入力されていません。全件表示します。")
        
        # 結果テーブル表示
        self._render_results(st.session_state.filtered_df)

    def _perform_search(self, df_full: pd.DataFrame, query: str, include_title: bool):
        """
        検索を実行し、セッション状態を更新する
        """
        st.session_state.search_query = query
        st.session_state.include_live_title = include_title
        st.session_state.display_limit = self.config.initial_display_limit
        
        if query:
            search_fields = ["曲名", "アーティスト"]
            if include_title:
                search_fields.append("ライブタイトル")
            
            st.session_state.filtered_df = self.search_service.search(
                df_full,
                query,
                search_fields,
                case_sensitive=False
            )
            st.write(
                f"「{query}」で検索した結果: "
                f"{len(st.session_state.filtered_df)}件"
            )
        else:
            st.session_state.filtered_df = df_full.copy()
            st.write("検索キーワードが入力されていません。全件表示します。")

    def _render_results(self, df: pd.DataFrame):
        """結果テーブルとページネーションの表示"""
        # 表示用データの準備
        df_to_show = df.copy()
        
        # YouTubeリンクをHTML形式に変換
        df_to_show["YouTubeリンク"] = df_to_show.apply(
            lambda row: f'<a href="{row["YouTubeタイムスタンプ付きURL"]}" target="_blank">YouTubeへ👻</a>',
            axis=1,
        )
        
        # アーティスト列にカスタムCSSクラスを適用
        df_to_show["アーティスト"] = (
            df_to_show["アーティスト"]
            .astype(str)
            .apply(lambda x: f'<div class="artist-cell">{x}</div>')
        )
        
        # 表示件数を制限
        df_limited_display = df_to_show.head(st.session_state.display_limit)
        
        # 表示する列とヘッダーの定義
        display_columns = [
            "ライブ配信日",
            "曲目",
            "曲名",
            "アーティスト",
            "YouTubeリンク",
        ]
        column_headers = {
            "ライブ配信日": "配信日",
            "曲目": "No.",
            "曲名": "曲名",
            "アーティスト": "アーティスト",
            "YouTubeリンク": "リンク",
        }
        
        # 結果テーブルの表示
        render_results_table(df_limited_display, display_columns, column_headers)
        
        # ページネーションの表示
        new_limit = render_pagination(
            total_count=len(df),
            current_limit=st.session_state.display_limit,
            increment=self.config.display_increment
        )
        
        if new_limit:
            st.session_state.display_limit = new_limit
            st.rerun()

    def _handle_error(self):
        """エラー時の表示"""
        st.warning(
            "必要なTSVファイルがすべて読み込めなかったため、結合データは表示できません。"
        )
        # エラー情報を表示するためにDataServiceのインスタンスを作成
        data_service = DataService(self.config)
        if data_service.get_last_error():
            st.error(data_service.get_last_error())
