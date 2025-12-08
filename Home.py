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
import pandas as pd
from typing import Optional
from src.ui.components.footer import display_footer
from src.config import setup_logging
from src.config.settings import Config
from src.services.data_service import DataService
from src.core.data_pipeline import DataPipeline
from src.services.search_service import SearchService
from src.ui.components import (
    render_search_form,
    render_results_table,
    render_pagination,
)

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

# カスタムCSSの適用
try:
    with open(config.css_file_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.error(f"エラー: {config.css_file_path} が見つかりません。")
except Exception as e:
    st.error(f"エラー: {config.css_file_path} の読み込み中に問題が発生しました: {e}")

# タイトルと説明
st.title("しのうたタイム👻🫧")
st.info("左のサイドバーから「Song List beta」を選択して、楽曲リストをご覧ください。")
st.markdown(
    """
    こちらはVTuber「[幽音しの](https://www.774.ai/talent/shino-kasukane)」さんの配信で歌われた楽曲をまとめた非公式データベースです。
    曲名、アーティスト、ライブ配信タイトルで検索できます。YouTubeリンクから該当の歌唱箇所に直接飛べます。
    """
)
st.markdown("---")


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
    data_service = DataService(config)
    pipeline = DataPipeline(data_service, config)
    return pipeline.execute()


# データパイプラインの実行
df_full = load_and_process_data(
    config.lives_file_path,
    config.songs_file_path,
    config.enable_cache
)

# SearchServiceのインスタンス化
search_service = SearchService()

if df_full is not None:
    # セッション状態の初期化
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "filtered_df" not in st.session_state:
        st.session_state.filtered_df = df_full.copy()
    if "include_live_title" not in st.session_state:
        st.session_state.include_live_title = True
    if "display_limit" not in st.session_state:
        st.session_state.display_limit = config.initial_display_limit
    
    # 検索フォームの表示
    current_input, current_checkbox_value, search_button = render_search_form(
        default_query=st.session_state.search_query,
        include_live_title=st.session_state.include_live_title
    )
    
    # 検索ボタンが押された場合の処理
    if search_button:
        st.session_state.search_query = current_input
        st.session_state.include_live_title = current_checkbox_value
        st.session_state.display_limit = config.initial_display_limit
        
        if st.session_state.search_query:
            # 検索対象フィールドの設定
            search_fields = ["曲名", "アーティスト"]
            if st.session_state.include_live_title:
                search_fields.append("ライブタイトル")
            
            # 検索実行
            st.session_state.filtered_df = search_service.search(
                df_full,
                st.session_state.search_query,
                search_fields,
                case_sensitive=False
            )
            st.write(
                f"「{st.session_state.search_query}」で検索した結果: "
                f"{len(st.session_state.filtered_df)}件"
            )
        else:
            st.session_state.filtered_df = df_full.copy()
            st.write("検索キーワードが入力されていません。全件表示します。")
    
    elif st.session_state.search_query:
        st.write(
            f"「{st.session_state.search_query}」で検索した結果: "
            f"{len(st.session_state.filtered_df)}件"
        )
    else:
        st.session_state.filtered_df = df_full.copy()
        st.write("検索キーワードが入力されていません。全件表示します。")
    
    # 表示用データの準備
    df_to_show = st.session_state.filtered_df.copy()
    
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
        total_count=len(st.session_state.filtered_df),
        current_limit=st.session_state.display_limit,
        increment=config.display_increment
    )
    
    if new_limit:
        st.session_state.display_limit = new_limit
        st.rerun()

else:
    st.warning(
        "必要なTSVファイルがすべて読み込めなかったため、結合データは表示できません。"
    )
    # エラー情報を表示するためにDataServiceのインスタンスを作成
    data_service = DataService(config)
    if data_service.get_last_error():
        st.error(data_service.get_last_error())

# フッターの表示
display_footer()
