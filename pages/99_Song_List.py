import streamlit as st
import pandas as pd
import io # TSVデータを読み込むために追加

# --- ページの基本設定 ---
st.set_page_config(
    page_title="V_SONG_LIST",
    page_icon="🎼",
    layout="wide",
)

st.title("V_SONG_LIST 🎼")
st.markdown("---")

# # --- TSVデータのサンプル ---
# # 実際にファイルから読み込む場合は、この部分をコメントアウトしてください
# tsv_data = """
# アーティスト	曲名	最近の歌唱
# (K)NoW_NAME	Harvest	https://www.youtube.com/live/wY3z5W9B8N0?si=FVqBjyoCdmcOKFxz&t=31800s
# 164P feat.GUMI	天ノ弱	https://www.youtube.com/live/0d6TiZm7xWc?si=rSfrknMqNQFcz5xw&t=3567s
# 25時、ナイトコードで。x KAITO	化けの花(1chorus)	https://www.youtube.com/live/OEtLBen9pLM?si=M4WDMSGkkHfWLvDr&t=4372s
# 40mP feat.初音ミク	からくりピエロ	https://www.youtube.com/live/rjOy6A4c68o?si=Q07K-470tlYbzNHk&t=7030s
# Ado	心という名の不可解	https://www.youtube.com/live/lrLQ6akH23w?si=aC5HLJK6UZYwu-Yn&t=4912s
# aiko	milk	https://www.youtube.com/live/6wh0qjbo6K4?si=vntI9mYE52ZplV6U&t=2583s
# aiko	カブトムシ	https://www.youtube.com/live/N0Tp3auhZ54?si=TUAMJQ8TqFkAVZ1r&t=2589s
# Aimer	I beg you	https://www.youtube.com/live/GvGh24EJfGg?si=QLYBryRLPz4v_Qdl&t=4053s
# YOASOBI	夜に駆ける	https://www.youtube.com/live/E8l1nOoKLLI?si=9GMtlAOzsgHxbniX&t=3220s
# 結束バンド	星座になれたら	https://www.youtube.com/live/BTi31luRntI?si=HKZA9dD6UF6pnPvq&t=4357s
# """

# --- データの読み込みとキャッシュ化 ---
@st.cache_data
def load_data(data):
    try:
        # 文字列データから直接DataFrameを作成
        df = pd.read_csv(io.StringIO(data), delimiter='\t')
        return df
    except Exception as e:
        st.error(f'データの読み込み中にエラーが発生しました: {e}')
        return pd.DataFrame()

# データをキャッシュから読み込み
# 実際のファイルパスを使う場合は load_data(file_path) のように変更してください
df_original = load_data(tsv_data)


# --- メイン画面の表示 ---
if not df_original.empty:
    
    # --- サイドバーにフィルターを配置 ---
    st.sidebar.header("絞り込みオプション")

    # 1. アーティストによる絞り込み
    # 'アーティスト'列のユニークなリストを取得し、ソートする
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
    # 表示用のDataFrameをコピーして作成
    df_display = df_original.copy()

    # アーティストでフィルタリング
    if selected_artists:
        df_display = df_display[df_display['アーティスト'].isin(selected_artists)]

    # 検索キーワードでフィルタリング
    if search_keyword:
        df_display = df_display[
            df_display['曲名'].str.contains(search_keyword, case=False, na=False)
        ]

    # --- 結果の表示 ---
    st.markdown(f"### 楽曲リスト ({len(df_display)}件)")
    
    # データを表形式で表示
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            # "最近の歌唱"列のデータを元にリンクを自動生成
            "最近の歌唱": st.column_config.LinkColumn(
                "YouTubeリンク", # 列ヘッダーに表示されるテキスト
                help="クリックするとYouTubeで開きます",
                display_text="再生する", # 各セルに表示されるテキスト
            )
        },
        # テーブルの高さを設定
        height=600 
    )

else:
    st.warning("楽曲データが読み込めませんでした。")