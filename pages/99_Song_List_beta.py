import streamlit as st
import pandas as pd
from footer import display_footer

# --- ページの基本設定 ---
st.set_page_config(
    page_title="歌唱楽曲リスト(β版) - しのうたタイム",
    page_icon="👻",
    layout="wide",
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
with st.expander("β版の制約について"):
    st.info(
        """
        - **アーティスト・楽曲の並び順:** 現在、漢字の並び順を調整中です。
        - **一部楽曲の重複:** 一部の楽曲が重複して表示される場合があります。
        - **機能の変更:** 今後、予告なくレイアウトや機能が変更・削除されることがあります。
        """
    )
st.markdown("---")

# --- TSVファイルのパス ---
file_path = "data/V_SONG_LIST.TSV"

# --- データの読み込み ---
@st.cache_data
def load_data(path):
    try:
        # TSVファイルをタブ区切りで読み込む
        df = pd.read_csv(path, delimiter="\t")
        return df
    except FileNotFoundError:
        st.error(f'エラー: 楽曲情報ファイル "{path}" が見つかりません。')
        st.info(f"`{path}` が正しく配置されているか確認してください。")
        return None
    except Exception as e:
        st.error(f'楽曲情報ファイル "{path}" の読み込み中にエラー: {e}')
        return None

df_original = load_data(file_path)

# --- メインコンテンツの表示 ---
if df_original is not None:
    # ★ "アーティスト(ソート用)" 列を基準にDataFrameを並び替える
    #    na_position='last' は、ソート用データがない行を末尾に集めるための設定です
    df_sorted = df_original.sort_values(by="アーティスト(ソート用)", na_position='last')

    # 表示用にデータをコピー
    df_to_show = df_sorted.copy()

    # 「最近の歌唱」列のURLをHTMLのリンクタグに変換する
    df_to_show["リンク"] = df_to_show["最近の歌唱"].apply(
        lambda url: f'<a href="{url}" target="_blank">YouTubeへ👻</a>' if pd.notna(url) else ""
    )
    
    # 「アーティスト」列の各セルをdivタグで囲み、CSSクラスを適用
    df_to_show["アーティスト"] = df_to_show["アーティスト"].apply(
        lambda x: f'<div class="artist-cell">{x}</div>'
    )

    # ★ 表示する列を選択し、ソート用の列は含めない
    final_display_columns = ["アーティスト", "曲名", "リンク"]
    df_display_ready = df_to_show[final_display_columns]

    st.markdown(f"**全 {len(df_original)} 件表示**")

    # DataFrameをHTMLテーブルに変換
    html_table = df_display_ready.to_html(
        escape=False, index=False, justify="left", classes="dataframe"
    )

    # HTMLテーブルのヘッダーを日本語に置換
    custom_headers = {
        "アーティスト": "アーティスト",
        "曲名": "曲名",
        "リンク": "リンク",
    }
    for original, custom in custom_headers.items():
        html_table = html_table.replace(f"<th>{original}</th>", f"<th>{custom}</th>")

    # 生成したHTMLをStreamlitで表示
    st.write(html_table, unsafe_allow_html=True)

else:
    st.warning("楽曲データが読み込めませんでした。")


# --- フッターを表示 ---
display_footer()


