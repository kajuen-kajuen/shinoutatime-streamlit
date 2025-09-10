import streamlit as st
import pandas as pd
from footer import display_footer

# --- ページの基本設定 ---
st.set_page_config(
    page_title="V SONG LIST",
    page_icon="🎼",
    layout="wide",
)

# --- カスタムCSSの適用 ---
try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("style.css が見つかりません。")
except Exception as e:
    st.error(f"style.css の読み込み中にエラーが発生しました: {e}")

# --- ヘッダー ---
st.title("V SONG LIST 🎼")
st.markdown("こちらはVTuberさんの歌唱楽曲をまとめた非公式データベースです。")
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
    df_to_show = df_original.copy()

    # YouTubeリンクをHTMLの a タグ形式に変換する
    df_to_show["リンク"] = df_to_show["最近の歌唱"].apply(
        lambda url: f'<a href="{url}" target="_blank">再生する</a>' if pd.notna(url) else ""
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

