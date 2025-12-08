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

import streamlit as st
import pandas as pd
from src.ui.components.footer import display_footer
from src.config.settings import Config
from src.services.data_service import DataService

# --- 設定の初期化 ---
config = Config()

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

/* タイトルの中央寄せ */
# h1 {
#     text-align: center;
#     margin-bottom: 1.5rem;
# }

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

# --- データサービスの初期化 ---
data_service = DataService(config)

# --- データの読み込み ---
@st.cache_data
def load_song_list():
    """
    楽曲リストデータを読み込む
    
    DataServiceを使用してV_SONG_LIST.TSVファイルから楽曲リストデータを読み込みます。
    Streamlitのキャッシュ機能により、再読み込みを防ぎます。
    
    Returns:
        pandas.DataFrame: 読み込まれた楽曲データのDataFrame。
                         以下の列を含む:
                         - アーティスト: アーティスト名（表示用）
                         - アーティスト(ソート用): アーティスト名（ソート用）
                         - 曲名: 楽曲名
                         - 最近の歌唱: 最近の歌唱へのYouTube URL
        None: ファイルが見つからない場合、または読み込みエラーが発生した場合
    
    要件: 8.1, 8.2
    """
    df = data_service.load_song_list_data()
    if df is None:
        # エラーメッセージを表示
        error_msg = data_service.get_last_error()
        if error_msg:
            st.error(f"エラー: {error_msg}")
            st.info(f"`{config.song_list_file_path}` が正しく配置されているか確認してください。")
    return df

df_original = load_song_list()

# --- メインコンテンツの表示 ---
if df_original is not None:
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

    # 表示用にデータをコピー
    df_to_show = df_sorted.copy()

    # YouTubeリンクの生成
    # 「最近の歌唱」列のURLをクリック可能なHTMLリンクに変換
    # 新しいタブで開くように target="_blank" を指定
    # 要件: 8.4
    df_to_show["リンク"] = df_to_show["最近の歌唱"].apply(
        lambda url: f'<a href="{url}" target="_blank">YouTubeへ👻</a>' if pd.notna(url) else ""
    )
    
    # アーティスト列のスタイリング
    # 「アーティスト」列の各セルをdivタグで囲み、CSSクラス "artist-cell" を適用
    # これにより、アーティスト名が長い場合に改行が許可される
    # 要件: 8.4
    df_to_show["アーティスト"] = df_to_show["アーティスト"].apply(
        lambda x: f'<div class="artist-cell">{x}</div>'
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
    # 表示列の選択（ソート用の列は内部処理のみで使用）
    display_columns = ["アーティスト", "曲名", "リンク"]
    
    # HTMLテーブルの生成と表示
    # このページは特殊なHTMLカスタマイズが必要なため、直接HTMLを生成
    html_table = df_to_show[display_columns].to_html(
        escape=False, index=False, justify="left", classes="dataframe"
    )
    st.write(html_table, unsafe_allow_html=True)

else:
    st.warning("楽曲データが読み込めませんでした。")

# --- フッターを表示 ---
display_footer()
