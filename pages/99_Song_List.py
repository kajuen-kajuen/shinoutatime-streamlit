import streamlit as st
import pandas as pd
import re

# Streamlitのページ設定
st.set_page_config(
    page_title="V_SONG_LIST",
    page_icon="🎼",
    layout="wide"
)

# --- データの読み込みとキャッシュ化 ---
# アプリの再実行時に毎回ファイルを読み込まないようにキャッシュします
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, delimiter='\t', engine='python', on_bad_lines='skip')
        return df
    except FileNotFoundError:
        st.error(f'エラー: 指定されたファイル "{file_path}" が見つかりません。')
        st.info("ファイルが `data/V_SONG_LIST.TSV` に正しく配置されているか確認してください。")
        return pd.DataFrame() # 空のDataFrameを返す
    except Exception as e:
        st.error(f'ファイルの読み込み中にエラーが発生しました: {e}')
        return pd.DataFrame()

# YouTube埋め込みURLを生成する関数
def create_embed_url(url):
    if not isinstance(url, str):
        return None
    
    # 正規表現で動画IDとタイムスタンプを抽出
    match = re.search(r'youtube\.com/(?:live/|watch\?v=)([a-zA-Z0-9_-]+)(?:.*?&t=(\d+)s)?', url)
    if match:
        video_id = match.group(1)
        start_time = match.group(2) if match.group(2) else "0"
        return f"https://www.youtube.com/embed/{video_id}?start={start_time}"
    return None

# --- アプリケーションのメイン部分 ---
st.title("V_SONG_LIST🎼")
st.markdown("---")

# データをキャッシュから読み込み
file_path = "data/V_SONG_LIST.TSV"
df = load_data(file_path)

if not df.empty:
    # DataFrameに埋め込み用URLの列を追加
    df['埋め込みURL'] = df['最近の歌唱'].apply(create_embed_url)

    # 検索ボックスの作成
    search_query = st.text_input("キーワード検索 (曲名またはアーティスト)", placeholder="例: ヨルシカ")

    # 検索条件に基づいてDataFrameをフィルタリング
    if search_query:
        filtered_df = df[
            df['曲名'].str.contains(search_query, case=False, na=False) |
            df['アーティスト'].str.contains(search_query, case=False, na=False)
        ].copy()
        st.subheader(f"検索結果: {len(filtered_df)}件")
    else:
        filtered_df = df.copy()
        st.subheader(f"全楽曲リスト: {len(filtered_df)}件")

    # 埋め込みURLが有効なものだけを表示
    valid_entries = filtered_df.dropna(subset=['埋め込みURL'])

    # 各曲を2列のレイアウトで表示
    for index, row in valid_entries.iterrows():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"**アーティスト**: {row['アーティスト']}")
            st.markdown(f"**曲名**: {row['曲名']}")
            st.markdown(f"[元のYouTubeリンク]({row['最近の歌唱']})")

        with col2:
            st.video(row['埋め込みURL'])
        
        st.markdown("---")