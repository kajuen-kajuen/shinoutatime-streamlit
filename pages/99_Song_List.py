import streamlit as st
import pandas as pd
# import io # ioはファイル読み込みでは不要なので削除してもOK

# --- ページの基本設定 ---
st.set_page_config(
    page_title="V_SONG_LIST",
    page_icon="🎼",
    layout="wide",
)

st.title("V_SONG_LIST 🎼")
st.markdown("---")

# --- TSVファイルのパスを指定 ---
file_path = "data/V_SONG_LIST.TSV" 

# --- データの読み込みとキャッシュ化 ---
# ファイルパスを引数に取るように修正
@st.cache_data
def load_data(path):
    try:
        # ファイルパスから直接DataFrameを作成
        df = pd.read_csv(path, delimiter='\t')
        return df
    except FileNotFoundError:
        st.error(f'エラー: 指定されたファイル "{path}" が見つかりません。')
        st.info("ファイルが `data/V_SONG_LIST.TSV` に正しく配置されているか確認してください。")
        return pd.DataFrame() # 空のDataFrameを返す
    except Exception as e:
        st.error(f'データの読み込み中にエラーが発生しました: {e}')
        return pd.DataFrame()

# データをキャッシュから読み込み
# ★★★ ここでファイルパスを渡します ★★★
df_original = load_data(file_path)


# --- メイン画面の表示 ---
if not df_original.empty:
    
    # --- サイドバーにフィルターを配置 ---
    st.sidebar.header("絞り込みオプション")

    # 1. アーティストによる絞り込み
    artists = sorted(df_original['アーティスト'].dropna().unique())
    selected_artists = st.sidebar.multiselect(
        "アーティストで絞り込む:",
        options=artists,
        placeholder="アーティストを選択"
    )

    # 2. 曲名での検索
    search_keyword = st.sidebar.text_input(
        "曲名で検索:",
        placeholder="キーワードを入力..."
    )

    # --- フィルター処理 ---
    df_display = df_original.copy()

    if selected_artists:
        df_display = df_display[df_display['アーティスト'].isin(selected_artists)]

    if search_keyword:
        df_display = df_display[
            df_display['曲名'].str.contains(search_keyword, case=False, na=False)
        ]

    # --- 結果の表示 ---
    st.markdown(f"### 楽曲リスト ({len(df_display)}件)")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "最近の歌唱": st.column_config.LinkColumn(
                "YouTubeリンク",
                help="クリックするとYouTubeで開きます",
                display_text="再生する",
            )
        },
        height=600 
    )

else:
    st.warning("楽曲データが読み込めませんでした。")