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

    # 常に全件表示する
    df_to_show = df_original
    st.markdown(f"**全 {len(df_to_show)} 件表示中**")

    # --- データフレームの表示 ---
    st.dataframe(
        df_to_show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "最近の歌唱": st.column_config.LinkColumn(
                "YouTubeリンク", # 列ヘッダーに表示されるテキスト
                help="クリックするとYouTubeで開きます",
                display_text="再生する", # 各セルに表示されるテキスト
            )
        },
        height=800 # 表示高さを少し広めに設定
    )

else:
    st.warning("楽曲データが読み込めませんでした。")


# --- フッターを表示 ---
display_footer()

