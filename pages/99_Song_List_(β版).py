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
/* アーティスト列のセル内コンテンツにのみ改行を許可 */
.artist-cell {
    white-space: normal;   /* 通常の改行を許可 */
    word-break: break-word;/* 長い単語でも強制的に改行 */
}
"""
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)
# --- ★★★ CSSの実装ここまで ★★★ ---


# --- ヘッダー ---
st.title("歌唱楽曲リスト(β版)")
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
        - **一部楽曲の重複:** 一部の楽曲が重複して表示されています。
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
    # アーティスト名、曲名でソートする
    df_sorted = df_original.sort_values(by=["アーティスト", "曲名"]).reset_index(drop=True)
    
    df_to_show = df_sorted.copy()

    # YouTubeリンクをHTMLの a タグ形式に変換する
    df_to_show["リンク"] = df_to_show["最近の歌唱"].apply(
        lambda url: f'<a href="{url}" target="_blank">再生する</a>' if pd.notna(url) else ""
    )
    
    # ★追加: アーティスト列の各セルをdivタグで囲み、CSSクラスを適用
    df_to_show["アーティスト"] = df_to_show["アーティスト"].apply(
        lambda x: f'<div class="artist-cell">{x}</div>'
    )

    # 表示する列を選択し、順序を整える
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
        "リンク": "YouTubeリンク",
    }
    for original, custom in custom_headers.items():
        html_table = html_table.replace(f"<th>{original}</th>", f"<th>{custom}</th>")

    # 生成したHTMLをStreamlitで表示
    st.write(html_table, unsafe_allow_html=True)

else:
    st.warning("楽曲データが読み込めませんでした。")


# --- フッターを表示 ---
display_footer()

