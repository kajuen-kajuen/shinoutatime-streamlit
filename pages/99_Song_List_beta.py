"""
楽曲リスト表示ページ（β版）

このモジュールは、VTuber「幽音しの」さんの配信で歌唱された全楽曲のリストを
アーティスト順に表示する機能を提供します。

主な機能:
- V_SONG_LIST.TSVファイルからの楽曲データ読み込み
- アーティスト名によるソート（大文字小文字を区別しない）
- 最近の歌唱へのYouTubeリンク表示
- β版の制約に関する情報表示

データソース:
- data/V_SONG_LIST.TSV: 楽曲リストデータ（アーティスト、曲名、最近の歌唱URL）

注意事項:
- β版のため、漢字のソート順が完全ではない可能性があります
- 一部楽曲が重複表示される場合があります
- 機能は予告なく変更される可能性があります

要件: 8.1-8.5
"""

import html
import logging

import streamlit as st
import pandas as pd
from src.ui.components.footer import display_footer
from src.config.settings import Config
from src.exceptions.errors import DataLoadError
from src.services.data_service import DataService
from src.repositories.live_repository import LiveRepository
from src.repositories.timestamp_repository import TimestampRepository
from src.repositories.song_list_repository import SongListRepository

logger = logging.getLogger(__name__)

# --- 設定の初期化 ---
config = Config.from_env()

# --- ページの基本設定 ---
st.set_page_config(
    page_title="歌唱楽曲リスト(β版) - しのうたタイム",
    page_icon=config.page_icon,
    layout=config.layout,
)

# --- ★★★ 新しいCSSをPythonコード内に直接実装 ★★★ ---
CUSTOM_CSS = """
/* ================================================= */
/* アプリケーション全体のレイアウト調整 */
/* ================================================= */
/* Streamlitのメインコンテンツエリアの幅を制御し、中央寄せにする */
.block-container {
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* ================================================= */
/* 特定のStreamlit要素のスタイリング */
/* ================================================= */

/* タイトルの中央寄せ(使っていない)
h1 {
    text-align: center;
    margin-bottom: 1.5rem;
}
*/

/* 検索結果件数表示のメッセージを左寄せに戻す */
div[data-testid="stMarkdown"] p {
    text-align: left;
    margin-bottom: 1rem;
}

/* ================================================= */
/* HTMLテーブルのスタイリング（既存+微調整） */
/* ================================================= */

/* テーブル内のヘッダーとデータセルに white-space: nowrap; を適用して改行を防ぐ */
table.dataframe th,
table.dataframe td {
    white-space: nowrap;
    /* デフォルトで改行しない */
    padding: 8px 12px;
    text-align: left;
}

/* アーティスト列のセル内コンテンツにのみ改行を許可 */
.artist-cell {
    white-space: normal;
    /* 通常の改行を許可 */
    word-break: break-word;
    /* 長い単語でも強制的に改行 */
}

table.dataframe {
    min-width: fit-content;
    width: 100%;
    border-collapse: collapse;
}

table.dataframe th,
table.dataframe td {
    border: 1px solid #ddd;
}

table.dataframe thead th {
    background-color: #f2f2f2;
    font-weight: bold;
}
"""
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)
# --- ★★★ CSSの実装ここまで ★★★ ---


# --- ヘッダー ---
st.title("しのうたタイム👻🫧")
st.subheader("歌唱楽曲リスト(β版)")
st.markdown(
    """
    こちらはVTuber「[幽音しの](https://www.774.ai/talent/shino-kasukane)」さんの配信で歌われた楽曲をまとめた非公式データベースです。
    """
)

# --- β版の制約について ---
# 
# β版の制約事項:
# 1. アーティスト・楽曲の並び順
#    - 現在、アルファベットの大文字小文字を区別しないソートを実装
#    - 漢字の五十音順ソートには未対応のため、並び順が不完全
#    - 将来的には日本語対応のソートライブラリの導入を検討
#
# 2. 一部楽曲の重複
#    - データソース（V_SONG_LIST.TSV）に重複エントリが存在する可能性
#    - 重複排除機能は未実装
#
# 3. 機能の変更
#    - β版のため、予告なくレイアウトや機能が変更・削除される可能性
#    - 正式版リリース時に大幅な変更が行われる可能性
#
# 要件: 8.1-8.5に関連する制約事項
with st.expander("β版の制約について"):
    st.info(
        """
        - **アーティスト・楽曲の並び順:** 現在、漢字の並び順を調整中です。
        - **一部楽曲の重複:** 一部の楽曲が重複して表示される場合があります。
        - **機能の変更:** 今後、予告なくレイアウトや機能が変更・削除されることがあります。
        """
    )
st.markdown("---")

# --- リポジトリの初期化 ---
live_repo = LiveRepository(config.lives_file_path)
timestamp_repo = TimestampRepository(config.songs_file_path)
song_list_repo = SongListRepository(config.song_list_file_path)

# --- データサービスの初期化 ---
data_service = DataService(config, live_repo, timestamp_repo, song_list_repo)

# --- データの読み込み ---
@st.cache_data(ttl=3600)
def load_song_list():
    """
    楽曲リストデータを読み込む

    DataServiceを使用してV_SONG_LIST.TSVファイルから楽曲リストデータを読み込みます。
    Streamlitのキャッシュ機能により、再読み込みを防ぎます。
    キャッシュの中では何も表示しない(失敗は例外のまま呼び出し側へ渡し、ページ側で表示する)。

    Returns:
        pandas.DataFrame: 読み込まれた楽曲データのDataFrame。
                         以下の列を含む:
                         - アーティスト: アーティスト名（表示用）
                         - アーティスト(ソート用): アーティスト名（ソート用）
                         - 曲名: 楽曲名
                         - 最近の歌唱: 最近の歌唱へのYouTube URL
                         ファイルが無いときは空のDataFrame。

    Raises:
        DataLoadError: ファイルの形が壊れているなど、読み込みに失敗した場合

    要件: 8.1, 8.2
    """
    return data_service.load_song_list_data()


def _cell(value) -> str:
    """表のセルの文字列(データ由来なのでエスケープする。欠損は空)"""
    return html.escape(str(value)) if pd.notna(value) else ""


def build_table_html(df: pd.DataFrame) -> str:
    """
    アーティスト・曲名・リンクの表の HTML を組み立てる

    データ由来の文字列はすべてエスケープする(曲名の < や & で表が壊れないように)。
    クラス名と見出しの左寄せは、以前の DataFrame.to_html(justify="left", classes="dataframe") と同じ。
    """
    rows = []
    for artist, title, url in zip(df["アーティスト"], df["曲名"], df["最近の歌唱"]):
        link = (
            f'<a href="{html.escape(str(url), quote=True)}" target="_blank" rel="noopener">YouTubeへ👻</a>'
            if pd.notna(url) else ""
        )
        rows.append(
            f'<tr><td><div class="artist-cell">{_cell(artist)}</div></td><td>{_cell(title)}</td><td>{link}</td></tr>'
        )
    header = '<tr style="text-align: left;"><th>アーティスト</th><th>曲名</th><th>リンク</th></tr>'
    return (
        '<table border="1" class="dataframe">'
        f"<thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"
    )


try:
    df_original = load_song_list()
except DataLoadError as e:
    logger.error(f"楽曲リストの読み込みに失敗しました: {e}", exc_info=True)
    st.error("楽曲リストを読み込めませんでした。")
    st.info(f"`{config.song_list_file_path}` が正しく配置されているか確認してください。")
    df_original = None

# --- メインコンテンツの表示 ---
if df_original is not None and not df_original.empty:
    # フィルタリング処理: アーティスト名が「-」の楽曲を除外
    # 
    # フィルタリング仕様:
    # - "アーティスト" 列が「-」（ハイフン）の行を除外
    # - Pandasのベクトル化された操作を使用して効率的に処理
    # - 元のデータファイルは変更せず、メモリ上のDataFrameのみを操作
    # 
    # 要件: 1.1, 1.2, 1.5, 2.1
    df_filtered = df_original[df_original["アーティスト"] != "-"].copy()
    
    # ソート処理: アーティスト名でデータを並び替え
    # 
    # ソート仕様:
    # - "アーティスト(ソート用)" 列を使用してソート
    # - 大文字小文字を区別しない（key=lambda col: col.str.lower()）
    # - 欠損値（NaN）は最後に配置（na_position='last'）
    # - 安定ソート（mergesort）を使用し、同一アーティスト内の曲順を維持
    #
    # β版の制約:
    # - 漢字のソート順は完全ではない可能性があります
    # - 日本語の五十音順ソートには対応していません
    #
    # 要件: 8.2, 8.3
    df_sorted = df_filtered.sort_values(
        by="アーティスト(ソート用)", 
        na_position='last',
        key=lambda col: col.str.lower(),
        kind='mergesort' # 安定ソートを指定し、同じアーティスト内の曲順を維持
    )

    # 全件数の表示
    # 
    # フィルタリング後の正確な件数を表示します。
    # アーティスト名が「-」の楽曲は除外されているため、
    # df_filtered（フィルタリング済みDataFrame）の行数を使用します。
    # 
    # 要件: 1.4（フィルタリング後の正確な件数を表示）, 8.5
    st.markdown(f"**全 {len(df_filtered)} 件表示**")

    # テーブルの表示
    # アーティスト(長い名前は改行を許す artist-cell)・曲名・最近の歌唱へのリンク(新しいタブで開く)
    # 要件: 8.4
    st.write(build_table_html(df_sorted), unsafe_allow_html=True)

else:
    st.warning("楽曲データが読み込めませんでした。")

# --- フッターを表示 ---
display_footer()
