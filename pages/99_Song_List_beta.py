"""
楽曲リスト表示ページ（β版）

このモジュールは、VTuber「幽音しの」さんの配信で歌唱された全楽曲のリストを
アーティスト順に表示する機能を提供します。

主な機能:
- データモデル v2(data/v2/)の曲ごとの集計(views.build_song_stats)を表示する
- 並びはアーティストの読み → 曲名の読み
- 最新の歌唱へのリンク(切り抜きは除く)
- Home と同じ「さらに25件表示」

データソース:
- data/v2/ の5つの TSV(src/ui/v2_data.py で読み、キャッシュする)
"""

import html
import logging

import streamlit as st
import pandas as pd
from src.ui.components import render_pagination
from src.ui.components.footer import display_footer
from src.config.settings import Config
from src.ui.v2_data import load_song_stats

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
# 並び順(読みの順)と重複(曲ごとに1行)は v2 で解消したので、機能の変更の注意だけ残す
with st.expander("β版の制約について"):
    st.info(
        """
        - **機能の変更:** 今後、予告なくレイアウトや機能が変更・削除されることがあります。
        """
    )
st.markdown("---")


def _cell(value) -> str:
    """表のセルの文字列(データ由来なのでエスケープする。欠損は空)"""
    return html.escape(str(value)) if pd.notna(value) else ""


def build_table_html(stats: pd.DataFrame) -> str:
    """
    アーティスト・曲名・リンクの表の HTML を組み立てる

    データ由来の文字列はすべてエスケープする(曲名の < や & で表が壊れないように)。
    リンクは最新の歌唱(views.build_song_stats の latest_link)。
    クラス名と見出しの左寄せは、以前の DataFrame.to_html(justify="left", classes="dataframe") と同じ。
    表は Home(src/ui/components の render_results_table)と同じ横スクロールの div で包む
    (列が改行しないので、スマホの幅では表が画面からはみ出すため)。
    """
    rows = []
    for artist, title, url, label in zip(
        stats["artist"], stats["title"], stats["latest_link"], stats["latest_link_label"]
    ):
        link = (
            f'<a href="{html.escape(str(url), quote=True)}" target="_blank" rel="noopener">{_cell(label)}</a>'
            if pd.notna(url) and url else ""
        )
        rows.append(
            f'<tr><td><div class="artist-cell">{_cell(artist)}</div></td><td>{_cell(title)}</td><td>{link}</td></tr>'
        )
    header = '<tr style="text-align: left;"><th>アーティスト</th><th>曲名</th><th>リンク</th></tr>'
    return (
        '<div style="overflow-x: auto; max-width: 100%;">'
        '<table border="1" class="dataframe">'
        f"<thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"
        "</div>"
    )


try:
    stats = load_song_stats()
except Exception as e:  # DataLoadError のほか、集計中の想定外の失敗も画面に出して止める
    logger.error(f"楽曲リストの読み込みに失敗しました: {e}", exc_info=True)
    st.error("楽曲リストを読み込めませんでした。")
    st.info(f"`{config.v2_data_dir}` のデータが正しく配置されているか確認してください。")
    stats = None

# --- メインコンテンツの表示 ---
if stats is not None and not stats.empty:
    if "song_list_limit" not in st.session_state:
        st.session_state.song_list_limit = config.initial_display_limit

    st.markdown(f"**全 {len(stats)} 件**")

    # テーブルの表示(並びは views の読みの順: アーティスト → 曲名)
    # アーティスト(長い名前は改行を許す artist-cell)・曲名・最新の歌唱へのリンク(新しいタブで開く)
    st.write(build_table_html(stats.head(st.session_state.song_list_limit)), unsafe_allow_html=True)

    new_limit = render_pagination(
        total_count=len(stats),
        current_limit=st.session_state.song_list_limit,
        increment=config.display_increment,
    )
    if new_limit:
        st.session_state.song_list_limit = new_limit
        st.rerun()

else:
    st.warning("楽曲データが読み込めませんでした。")

# --- フッターを表示 ---
display_footer()
