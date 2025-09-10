import streamlit as st
import pandas as pd

# ブラウザのタブ名を「V_SONG_LIST」に設定
st.set_page_config(
    page_title="V_SONG_LIST",
    page_icon="🎼",
    layout="wide",
)

st.title("V_SONG_LIST🎼")
st.markdown("---")

# --- TSVファイルのパス ---
file_path = "data/V_SONG_LIST.TSV"

# --- データの読み込みとキャッシュ化 ---
# アプリの再実行時に毎回ファイルを読み込まないようにキャッシュします
@st.cache_data
def load_data(file_path):
    try:
        # タブ区切りでファイルを読み込み
        df = pd.read_csv(file_path, delimiter='\t')
        return df
    except FileNotFoundError:
        st.error(f'エラー: 指定されたファイル "{file_path}" が見つかりません。')
        st.info("ファイルが `data/V_SONG_LIST.TSV` に正しく配置されているか確認してください。")
        return pd.DataFrame()  # ファイルが見つからない場合は空のDataFrameを返す
    except Exception as e:
        st.error(f'ファイルの読み込み中にエラーが発生しました: {e}')
        return pd.DataFrame()

# データをキャッシュから読み込み
df = load_data(file_path)

if not df.empty:
    st.markdown("## 楽曲リスト")
    
    # YouTubeリンクをMarkdown形式に変換
    df['最近の歌唱'] = df['最近の歌唱'].apply(
        lambda url: f'[YouTubeへ]({url})' if isinstance(url, str) and 'youtube.com' in url else url
    )
    
    # データを表形式で表示
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "最近の歌唱": st.column_config.LinkColumn(
                "リンク",
                help="YouTubeへのリンク",
                display_text="YouTubeへ"
            )
        }
    )
else:
    st.warning("必要なTSVファイルが読み込めなかったため、データは表示できません。")