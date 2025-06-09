import streamlit as st
import pandas as pd
from PIL import Image

# ブラウザのタブ名を「しのうたタイム」に設定し、レイアウトを広めに設定
st.set_page_config(
    page_title="しのうたタイム",
    page_icon="👻",
    layout="wide",
)

# --- カスタムCSSの適用 ---
try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.error("エラー: style.css が見つかりません。")
    st.info("`style.css` がアプリと同じディレクトリにあるか確認してください。")
except Exception as e:
    st.error(f"エラー: style.css の読み込み中に問題が発生しました: {e}")
# --- カスタムCSSの適用ここまで ---

st.title("しのうたタイム👻🫧")

# --- 概要欄の追加 ---
st.markdown(
    """
    こちらはVTuber「[幽音しの](https://www.774.ai/talent/shino-kasukane)」さんの配信で歌われた楽曲をまとめた非公式データベースです。
    曲名、アーティスト、ライブ配信タイトルで検索できます。YouTubeリンクから該当の歌唱箇所に直接飛べます。
    """
)
st.markdown("---")
# --- 概要欄の追加ここまで ---

# --- TSVファイルのパス ---
lives_file_path = "data/M_YT_LIVE.TSV"
songs_file_path = "data/M_YT_LIVE_TIMESTAMP.TSV"


# --- 時間文字列を秒数に変換するヘルパー関数 ---
def convert_timestamp_to_seconds(timestamp_str):
    if pd.isna(timestamp_str) or not isinstance(timestamp_str, str):
        return None

    parts = list(map(int, timestamp_str.split(":")))

    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    else:
        return None


# --- データの読み込み ---
df_lives = None
df_songs = None

try:
    df_lives = pd.read_csv(lives_file_path, delimiter="\t")
except FileNotFoundError:
    st.error(f'エラー: 配信情報ファイル "{lives_file_path}" が見つかりません。')
    st.info(f"`{lives_file_path}` がアプリと同じディレクトリにあるか確認してください。")
except Exception as e:
    st.error(
        f'配信情報ファイル "{lives_file_path}" の読み込み中にエラーが発生しました: {e}'
    )

try:
    df_songs = pd.read_csv(songs_file_path, delimiter="\t")
except FileNotFoundError:
    st.error(f'エラー: 楽曲情報ファイル "{songs_file_path}" が見つかりません。')
    st.info(f"`{songs_file_path}` がアプリと同じディレクトリにあるか確認してください。")
except Exception as e:
    st.error(
        f'楽曲情報ファイル "{songs_file_path}" の読み込み中にエラーが発生しました: {e}'
    )


# --- データの結合と表示 ---
if df_lives is not None and df_songs is not None:
    # 'ID' (M_YT_LIVE.TSV) と 'LIVE_ID' (M_YT_LIVE_TIMESTAMP.TSV) をキーとして結合
    df_merged = pd.merge(
        df_songs,
        df_lives[["ID", "配信日", "タイトル", "URL"]],
        left_on="LIVE_ID",
        right_on="ID",
        how="left",
        suffixes=("_song", "_live"),
    )

    # 結合に使ったが、重複するM_YT_LIVE.TSV側のID列（`ID_live`）を削除
    df_merged = df_merged.drop(columns=["ID_live"])

    # 列名を分かりやすく変更
    df_merged = df_merged.rename(
        columns={
            "ID_song": "楽曲ID",
            "配信日": "ライブ配信日_original",
            "タイトル": "ライブタイトル",
            "URL": "元ライブURL",
        }
    )
    # 表示用の「ライブ配信日」は、元の「ライブ配信日_original」をそのまま使う
    df_merged["ライブ配信日"] = df_merged["ライブ配信日_original"]

    # タイムスタンプを秒数に変換する新しい列を追加
    df_merged["タイムスタンプ_秒"] = df_merged["タイムスタンプ"].apply(
        convert_timestamp_to_seconds
    )

    # --- 新しい曲目生成ロジックの開始 ---
    # ソート用に日付型に変換したカラムを作成
    df_merged["ライブ配信日_sortable"] = pd.to_datetime(
        df_merged["ライブ配信日_original"], unit="ms", errors="coerce"
    )

    # UNIXミリ秒で変換できなかった（NaTの）行に対して、YYYY/MM/DD形式として再変換を試みる
    mask_nat_sortable = df_merged["ライブ配信日_sortable"].isna()
    if mask_nat_sortable.any():
        try:
            df_merged.loc[mask_nat_sortable, "ライブ配信日_sortable"] = pd.to_datetime(
                df_merged.loc[mask_nat_sortable, "ライブ配信日_original"],
                errors="coerce",
            )
        except Exception as e:
            st.warning(f"ソート用の「ライブ配信日」変換中にエラーが発生しました: {e}")
            st.warning(
                "日付の形式が複雑な可能性があります。TSVファイル内の「配信日」カラムのデータを直接確認してください。"
            )

    # ライブ配信日の降順 (新しい日付が上)、かつその中で LIVE_ID の昇順、さらにタイムスタンプの昇順でソート
    df_merged = df_merged.sort_values(
        by=["ライブ配信日_sortable", "LIVE_ID", "タイムスタンプ_秒"],
        ascending=[False, True, True],
    ).reset_index(drop=True)

    # YouTubeタイムスタンプ付きURLを正しく作成
    df_merged["YouTubeタイムスタンプ付きURL"] = df_merged.apply(
        lambda row: (
            f"{row['元ライブURL']}&t={int(row['タイムスタンプ_秒'])}s"
            if pd.notna(row["元ライブURL"]) and pd.notna(row["タイムスタンプ_秒"])
            else ""
        ),
        axis=1,
    )

    # 同じ日付のライブに配信番号を振る
    df_merged["日付_LIVE_ID_tuple"] = list(
        zip(df_merged["ライブ配信日_sortable"], df_merged["LIVE_ID"])
    )
    unique_tuples, live_nums = pd.factorize(df_merged["日付_LIVE_ID_tuple"])
    df_merged["ライブ番号"] = unique_tuples + 1
    df_merged = df_merged.drop(columns=["日付_LIVE_ID_tuple"])

    # 各ライブ配信内で楽曲に連番を振る
    df_merged["曲順"] = df_merged.groupby("LIVE_ID").cumcount() + 1

    # 新しい曲目形式を生成
    live_counts_per_date = df_merged.groupby("ライブ配信日_sortable")[
        "LIVE_ID"
    ].transform("nunique")

    df_merged["曲目"] = df_merged.apply(
        lambda row: (
            f"{row['ライブ番号']}-{row['曲順']}曲目"
            if live_counts_per_date.loc[row.name] > 1
            else f"{row['曲順']}曲目"
        ),
        axis=1,
    )
    # --- 新しい曲目生成ロジックの終了 ---

    st.session_state.df_full = df_merged.copy()

    # --- 検索ボックスとボタン、チェックボックスの追加 ---
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "filtered_df" not in st.session_state:
        st.session_state.filtered_df = st.session_state.df_full.copy()
    if "include_live_title" not in st.session_state:
        st.session_state.include_live_title = True
    if "display_limit" not in st.session_state:
        st.session_state.display_limit = 25  # 初期表示件数

    current_input = st.text_input(
        "キーワード検索（曲名、アーティスト）",
        value=st.session_state.search_query,
        key="search_input_box",
        placeholder="ここにキーワードを入力",
    )

    current_checkbox_value = st.checkbox(
        "検索対象にライブ配信タイトルを含める",
        value=st.session_state.include_live_title,
        key="include_live_title_checkbox",
    )

    search_button = st.button("検索")

    if search_button:
        st.session_state.search_query = current_input
        st.session_state.include_live_title = current_checkbox_value
        st.session_state.display_limit = 25

        if st.session_state.search_query:
            filter_condition = st.session_state.df_full["曲名"].astype(
                str
            ).str.contains(
                st.session_state.search_query, case=False, na=False
            ) | st.session_state.df_full[
                "アーティスト"
            ].astype(
                str
            ).str.contains(
                st.session_state.search_query, case=False, na=False
            )

            if st.session_state.include_live_title:
                filter_condition = filter_condition | st.session_state.df_full[
                    "ライブタイトル"
                ].astype(str).str.contains(
                    st.session_state.search_query, case=False, na=False
                )

            st.session_state.filtered_df = st.session_state.df_full[
                filter_condition
            ].copy()
            st.write(
                f"「{st.session_state.search_query}」で検索した結果: {len(st.session_state.filtered_df)}件"
            )
        else:
            st.session_state.filtered_df = st.session_state.df_full.copy()
            st.write("検索キーワードが入力されていません。全件表示します。")
    elif not st.session_state.search_query and not search_button:
        st.session_state.filtered_df = st.session_state.df_full.copy()
        st.write("検索キーワードが入力されていません。全件表示します。")

    # ここから段階的表示の処理
    df_to_show = st.session_state.filtered_df.copy()

    # YouTubeリンクをHTML形式で直接埋め込むために変換
    df_to_show["YouTubeリンク"] = df_to_show.apply(
        lambda row: f'<a href="{row["YouTubeタイムスタンプ付きURL"]}" target="_blank">YouTubeへ👻</a>',
        axis=1,
    )

    # --- 不要な列を削除 ---
    df_to_show = df_to_show.drop(
        columns=[
            "YouTubeタイムスタンプ付きURL",  # HTMLリンク生成後に削除
            "ライブ配信日_original",
            "ライブ配信日_sortable",
            "タイムスタンプ_秒",
            "LIVE_ID",
            "楽曲ID",
            "タイムスタンプ",
            "ライブ番号",
            "曲順",
            "ライブタイトル",  # ★削除対象
            "元ライブURL",  # ★削除対象
        ],
        errors="ignore",
    )

    # アーティスト列にカスタムクラスを適用 (style.cssに .artist-cell が定義されていれば機能します)
    df_to_show["アーティスト"] = (
        df_to_show["アーティスト"]
        .astype(str)
        .apply(lambda x: f'<div class="artist-cell">{x}</div>')
    )

    # 表示する列の順序を再調整
    final_display_columns = [
        "ライブ配信日",
        "曲目",
        "曲名",
        "アーティスト",
        "YouTubeリンク",
        # "ライブタイトル", # ★削除対象
        # "元ライブURL",    # ★削除対象
    ]
    # 実際にDataFrameに存在する列のみを選択して表示
    final_display_columns = [
        col for col in final_display_columns if col in df_to_show.columns
    ]

    # 表示件数を制限
    df_limited_display = df_to_show[final_display_columns].head(
        st.session_state.display_limit
    )

    # DataFrameをHTMLとして生成
    html_table = df_limited_display.to_html(
        escape=False, index=False, justify="left", classes="dataframe"
    )

    # ヘッダーの置き換え辞書
    custom_headers = {
        "ライブ配信日": "配信日",
        "曲目": "No.",
        "曲名": "曲名",
        "アーティスト": "アーティスト",
        "YouTubeリンク": "リンク",
        # "ライブタイトル": "ライブタイトル", # ★削除対象
        # "元ライブURL": "元ライブURL",    # ★削除対象
    }

    # HTML文字列内で各ヘッダーを置き換える
    for original, custom in custom_headers.items():
        html_table = html_table.replace(f"<th>{original}</th>", f"<th>{custom}</th>")

    # テーブルをスクロール可能なdivで囲む
    scrollable_html = f"""
    <div style="overflow-x: auto; max-width: 100%;">
        {html_table}
    </div>
    """
    # 生成したHTMLをStreamlitで表示
    st.write(scrollable_html, unsafe_allow_html=True)

    # 「もっと見る」ボタン
    if st.session_state.display_limit < len(st.session_state.filtered_df):
        if st.button(
            f"さらに25件表示（現在の表示: {min(st.session_state.display_limit, len(st.session_state.filtered_df))}/{len(st.session_state.filtered_df)}件）"
        ):
            st.session_state.display_limit += 25
            st.rerun()
    else:
        st.info(f"全ての{len(st.session_state.filtered_df)}件が表示されています。")

else:
    st.warning(
        "必要なTSVファイルがすべて読み込めなかったため、結合データは表示できません。"
    )

st.markdown("---")
st.caption("Streamlit アプリケーション by Gemini")
st.caption(
    "本サイトに関する質問・バグの報告などは[@kajuen_kajuen](https://x.com/kajuen_kajuen)までお願いします。"
)
