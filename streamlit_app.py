import streamlit as st
import pandas as pd

# ブラウザのタブ名を「しのうた時計」に設定し、レイアウトを広めに設定
st.set_page_config(page_title="しのうた時計", layout="wide")

st.title("しのうた時計")

# --- TSVファイルのパス ---
lives_file_path = "data/M_YT_LIVE.TSV"
songs_file_path = "data/M_YT_LIVE_TIMESTAMP.TSV"


# --- 時間文字列を秒数に変換するヘルパー関数 ---
def convert_timestamp_to_seconds(timestamp_str):
    if pd.isna(timestamp_str) or not isinstance(timestamp_str, str):
        return None

    parts = list(map(int, timestamp_str.split(":")))

    # 時:分:秒 の場合
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    # 分:秒 の場合 (0:01:47 のように時が0で省略されている場合も対応)
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    else:
        return None  # 不明な形式の場合はNoneを返す


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
        df_songs,  # 楽曲情報をベースにする
        df_lives[["ID", "配信日", "タイトル", "URL"]],  # 配信情報から必要な列のみ選択
        left_on="LIVE_ID",  # 楽曲情報側の結合キー
        right_on="ID",  # 配信情報側の結合キー
        how="left",  # 左外部結合 (全ての楽曲情報に配信情報を紐付ける)
        suffixes=("_song", "_live"),  # 列名が重複した場合の接尾辞
    )

    # 結合に使ったが、重複するM_YT_LIVE.TSV側のID列（`ID_live`）を削除
    df_merged = df_merged.drop(columns=["ID_live"])

    # 列名を分かりやすく変更 (必要に応じて)
    df_merged = df_merged.rename(
        columns={
            "ID_song": "楽曲ID",  # M_YT_LIVE_TIMESTAMP.TSVのID列は楽曲ID
            "配信日": "ライブ配信日_original",  # 元の「配信日」は「ライブ配信日_original」として保持
            "タイトル": "ライブタイトル",
            "URL": "元ライブURL",  # 元のURLも残す場合はこの名前に
        }
    )
    # 表示用の「ライブ配信日」は、元の「ライブ配信日_original」をそのまま使う
    df_merged["ライブ配信日"] = df_merged["ライブ配信日_original"]

    # タイムスタンプを秒数に変換する新しい列を追加
    df_merged["タイムスタンプ_秒"] = df_merged["タイムスタンプ"].apply(
        convert_timestamp_to_seconds
    )

    # 各ライブ配信内で楽曲に連番を振る
    # ライブIDとタイムスタンプでソートし、その順序で連番を振る
    df_merged = df_merged.sort_values(by=["LIVE_ID", "タイムスタンプ_秒"]).reset_index(
        drop=True
    )
    df_merged["曲目"] = (
        df_merged.groupby("LIVE_ID").cumcount() + 1
    )  # 「#」ではなく「曲目」という列名に
    # 「曲目」に「曲目」という単位を追加
    df_merged["曲目"] = df_merged["曲目"].astype(str) + "曲目"

    # YouTubeタイムスタンプ付きURLを正しく作成
    df_merged["YouTubeタイムスタンプ付きURL"] = df_merged.apply(
        lambda row: (
            f"{row['元ライブURL']}&t={int(row['タイムスタンプ_秒'])}s"
            if pd.notna(row["元ライブURL"]) and pd.notna(row["タイムスタンプ_秒"])
            else ""
        ),
        axis=1,
    )

    # --- ここからソート用日付の変換とソート順序の変更 ---
    # ソート用に日付型に変換したカラムを作成
    df_merged["ライブ配信日_sortable"] = pd.to_datetime(
        df_merged["ライブ配信日_original"], unit="ms", errors="coerce"
    )

    # UNIXミリ秒で変換できなかった（NaTの）行に対して、YYYY/MM/DD形式として再変換を試みる
    mask_nat_sortable = df_merged["ライブ配信日_sortable"].isna()

    if mask_nat_sortable.any():  # NaTの行が存在する場合のみ処理
        try:
            df_merged.loc[mask_nat_sortable, "ライブ配信日_sortable"] = pd.to_datetime(
                df_merged.loc[
                    mask_nat_sortable, "ライブ配信日_original"
                ],  # 元の文字列を使用
                infer_datetime_format=True,  # 形式を自動推測させる
                errors="coerce",  # 変換できないものはNaTにする
            )
        except Exception as e:
            st.warning(f"ソート用の「ライブ配信日」変換中にエラーが発生しました: {e}")
            st.warning(
                "日付の形式が複雑な可能性があります。TSVファイル内の「配信日」カラムのデータを直接確認してください。"
            )
            # エラー発生時は、変換できなかった日付はNaTのままになります

    # ライブ配信日の降順 (新しい日付が上)、かつその中で曲目 (タイムスタンプ_秒) の昇順でソート
    # NaT（不正な日付）はソート時に自動的に末尾に配置されます
    df_merged = df_merged.sort_values(
        by=["ライブ配信日_sortable", "タイムスタンプ_秒"], ascending=[False, True]
    ).reset_index(drop=True)
    # --- ソート順序の変更ここまで ---

    # 表示する列の順序を調整 (オプション)
    # 「ライブ配信日_sortable」はソート用なので、表示列からは除外
    display_columns = [
        "ライブ配信日",  # 元の文字列形式の「ライブ配信日」を表示
        "曲目",
        "曲名",
        "アーティスト",
        "YouTubeタイムスタンプ付きURL",
        "ライブタイトル",
    ]

    # 実際にDataFrameに存在する列のみを選択して表示
    actual_display_columns = [
        col for col in display_columns if col in df_merged.columns
    ]
    df_display = df_merged[actual_display_columns].copy()

    # --- 検索ボックスの追加 ---
    # `st.session_state` を使って検索クエリの状態を管理
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "filtered_df" not in st.session_state:
        st.session_state.filtered_df = df_display  # 初期表示は全件

    # 検索入力
    search_input = st.text_input(
        "キーワード検索（ライブタイトル、曲名、アーティスト）",
        st.session_state.search_query,
        key="search_input_box",
        placeholder="ここに入力",  # ★追加したプレースホルダー
    )

    # 検索入力が変更された場合にデータをフィルタリング
    if search_input != st.session_state.search_query:
        st.session_state.search_query = search_input  # 現在の検索入力を状態に保存
        if st.session_state.search_query:
            # 検索クエリに基づいてデータをフィルタリング
            df_display_filtered = df_display[
                df_display["ライブタイトル"]
                .astype(str)
                .str.contains(st.session_state.search_query, case=False, na=False)
                | df_display["曲名"]
                .astype(str)
                .str.contains(st.session_state.search_query, case=False, na=False)
                | df_display["アーティスト"]
                .astype(str)
                .str.contains(st.session_state.search_query, case=False, na=False)
            ]
            st.session_state.filtered_df = df_display_filtered
            st.write(
                f"「{st.session_state.search_query}」で検索した結果: {len(df_display_filtered)}件"
            )
        else:  # キーワードが空になった場合
            st.session_state.filtered_df = df_display  # 全件表示に戻す
            st.write("検索キーワードが入力されていません。全件表示します。")

    # 初回ロード時は常に全件表示
    if not st.session_state.search_query:  # 検索クエリが空の場合
        st.session_state.filtered_df = df_display  # 初期表示は全件

    # st.column_config を使って、各カラムのインタラクティブ機能を無効化
    column_configuration = {}
    for col_name in actual_display_columns:
        if col_name == "YouTubeタイムスタンプ付きURL":
            column_configuration[col_name] = st.column_config.LinkColumn(
                "YouTubeリンク",
                help="クリックするとYouTubeの該当箇所へ遷移します",
                max_chars=None,
                display_text="YouTubeへ 👻",
                width="medium",
                disabled=True,
            )
        else:
            column_configuration[col_name] = st.column_config.TextColumn(
                col_name,
                disabled=True,
            )

    # st.data_editor を使用して、ダウンロードボタンやその他の操作を無効化
    st.data_editor(
        st.session_state.filtered_df,
        use_container_width=True,
        column_config=column_configuration,
        hide_index=True,
        disabled=True,
    )


else:
    st.warning(
        "必要なTSVファイルがすべて読み込めなかったため、結合データは表示できません。"
    )

st.markdown("---")
st.caption("Streamlit アプリケーション by Gemini")
