"""
しのうたタイム - メインページ

VTuber「幽音しの」さんの配信で歌唱された楽曲を検索・閲覧できる
非公式ファンサイトのメインページです。

主な機能:
- 楽曲データの読み込みと表示
- キーワード検索（曲名、アーティスト、配信タイトル）
- YouTubeタイムスタンプ付きリンク生成
- 段階的表示（25件ずつ）
- 曲目番号の自動生成

データソース:
- data/M_YT_LIVE.TSV: 配信情報
- data/M_YT_LIVE_TIMESTAMP.TSV: 楽曲タイムスタンプ情報
"""

import streamlit as st
import pandas as pd
from PIL import Image
from footer import display_footer  # ★ここを追加★
from src.config import setup_logging

# ロギングの初期化（アプリケーション起動時に一度だけ実行）
if "logging_initialized" not in st.session_state:
    setup_logging()
    st.session_state.logging_initialized = True

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

st.info("左のサイドバーから「Song List beta」を選択して、楽曲リストをご覧ください。")

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
    """
    タイムスタンプ文字列を秒数に変換する
    
    YouTubeのタイムスタンプ付きURL生成のために、
    HH:MM:SS形式またはMM:SS形式の時間文字列を秒数に変換します。
    
    Args:
        timestamp_str (str): タイムスタンプ文字列
            - HH:MM:SS形式（例: "1:23:45"）
            - MM:SS形式（例: "12:34"）
    
    Returns:
        int: 変換された秒数。変換に失敗した場合はNone
            - HH:MM:SS形式の場合: 時間*3600 + 分*60 + 秒
            - MM:SS形式の場合: 分*60 + 秒
    
    Examples:
        >>> convert_timestamp_to_seconds("1:23:45")
        5025
        >>> convert_timestamp_to_seconds("12:34")
        754
        >>> convert_timestamp_to_seconds(None)
        None
    
    Notes:
        - 入力がNoneまたは文字列でない場合はNoneを返す
        - コロン区切りが3つでも2つでもない場合はNoneを返す
    """
    if pd.isna(timestamp_str) or not isinstance(timestamp_str, str):
        return None

    parts = list(map(int, timestamp_str.split(":")))

    if len(parts) == 3:
        # HH:MM:SS形式
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        # MM:SS形式
        return parts[0] * 60 + parts[1]
    else:
        return None


# --- データの読み込み ---
# TSVファイルから配信情報と楽曲情報を読み込む
# エラーハンドリングにより、ファイルが存在しない場合や読み込みに失敗した場合に
# ユーザーに適切なエラーメッセージを表示する
df_lives = None
df_songs = None

# 配信情報（M_YT_LIVE.TSV）の読み込み
# カラム: ID, 配信日, タイトル, URL
try:
    df_lives = pd.read_csv(lives_file_path, delimiter="\t")
except FileNotFoundError:
    st.error(f'エラー: 配信情報ファイル "{lives_file_path}" が見つかりません。')
    st.info(f"`{lives_file_path}` がアプリと同じディレクトリにあるか確認してください。")
except Exception as e:
    st.error(
        f'配信情報ファイル "{lives_file_path}" の読み込み中にエラーが発生しました: {e}'
    )

# 楽曲タイムスタンプ情報（M_YT_LIVE_TIMESTAMP.TSV）の読み込み
# カラム: ID, LIVE_ID, 曲名, アーティスト, タイムスタンプ
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
    # ===== データ結合処理 =====
    # 配信情報（df_lives）と楽曲情報（df_songs）をLIVE_IDをキーとして結合
    # 左結合（left join）により、楽曲データを基準として配信情報を紐付ける
    # これにより、各楽曲がどの配信で歌われたかを特定できる
    df_merged = pd.merge(
        df_songs,
        df_lives[["ID", "配信日", "タイトル", "URL"]],
        left_on="LIVE_ID",  # 楽曲データのLIVE_IDカラム
        right_on="ID",      # 配信データのIDカラム
        how="left",         # 左結合: 楽曲データを基準とする
        suffixes=("_song", "_live"),  # 重複する列名に接尾辞を付与
    )

    # 結合に使用したが不要となった配信側のID列（ID_live）を削除
    df_merged = df_merged.drop(columns=["ID_live"])

    # 列名を分かりやすい日本語名に変更
    df_merged = df_merged.rename(
        columns={
            "ID_song": "楽曲ID",
            "配信日": "ライブ配信日_original",  # 元の配信日データ（UNIXミリ秒またはYYYY/MM/DD形式）
            "タイトル": "ライブタイトル",
            "URL": "元ライブURL",
        }
    )
    
    # 表示用の「ライブ配信日」列を作成（元データをそのまま使用）
    df_merged["ライブ配信日"] = df_merged["ライブ配信日_original"]

    # ===== タイムスタンプ変換処理 =====
    # タイムスタンプ文字列（HH:MM:SSまたはMM:SS形式）を秒数に変換
    # YouTubeのタイムスタンプ付きURL生成に使用
    df_merged["タイムスタンプ_秒"] = df_merged["タイムスタンプ"].apply(
        convert_timestamp_to_seconds
    )

    # ===== 日付変換とソート処理 =====
    # ソート用に配信日を日付型（datetime）に変換
    # まずUNIXミリ秒として変換を試みる
    df_merged["ライブ配信日_sortable"] = pd.to_datetime(
        df_merged["ライブ配信日_original"], unit="ms", errors="coerce"
    )

    # UNIXミリ秒で変換できなかった行（NaT）に対して、YYYY/MM/DD形式として再変換
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

    # データをソート: 配信日降順（新しい順）→ LIVE_ID昇順 → タイムスタンプ昇順
    # これにより、最新の配信が上に表示され、同一配信内では歌唱順に並ぶ
    df_merged = df_merged.sort_values(
        by=["ライブ配信日_sortable", "LIVE_ID", "タイムスタンプ_秒"],
        ascending=[False, True, True],
    ).reset_index(drop=True)

    # ===== YouTubeタイムスタンプ付きURL生成 =====
    # 配信URLにタイムスタンプパラメータ（&t=秒数s）を付加
    # これにより、リンクをクリックすると該当の歌唱箇所から再生が開始される
    df_merged["YouTubeタイムスタンプ付きURL"] = df_merged.apply(
        lambda row: (
            f"{row['元ライブURL']}&t={int(row['タイムスタンプ_秒'])}s"
            if pd.notna(row["元ライブURL"]) and pd.notna(row["タイムスタンプ_秒"])
            else ""
        ),
        axis=1,
    )

    # ===== 曲目番号生成ロジック =====
    # 各配信内での楽曲の歌唱順序を示す曲目番号を生成する
    # 同一日に複数配信がある場合は「配信番号-曲順」形式、単一配信の場合は「曲順」形式で表示
    
    # ステップ1: 各配信内での曲順を計算
    # groupby("LIVE_ID").cumcount()により、各配信内で0から始まる連番を生成し、+1で1始まりにする
    df_merged["曲順"] = df_merged.groupby("LIVE_ID").cumcount() + 1

    # ステップ2: 同一日内の配信に番号を振る（ライブ番号）
    def assign_live_number_per_date(group_df):
        """
        同一日付内の各配信に連番（ライブ番号）を振る
        
        Args:
            group_df: 同一日付でグループ化されたDataFrame
        
        Returns:
            DataFrame: LIVE_IDとライブ番号を含むDataFrame
        """
        # factorizeにより、LIVE_IDの出現順に0から始まる番号を振り、+1で1始まりにする
        factor_codes, _ = pd.factorize(group_df["LIVE_ID"])
        group_df["ライブ番号"] = factor_codes + 1
        return group_df[["LIVE_ID", "ライブ番号"]]

    # ライブ番号の計算: 日付とLIVE_IDのユニークな組み合わせを抽出
    temp_live_numbers = (
        df_merged[["ライブ配信日_sortable", "LIVE_ID"]].drop_duplicates().copy()
    )

    # ソートして、factorizeの順序を安定させる（LIVE_IDの昇順）
    temp_live_numbers = temp_live_numbers.sort_values(
        by=["ライブ配信日_sortable", "LIVE_ID"]
    )

    # 日付ごとにグループ化し、各配信にライブ番号を振る
    temp_live_numbers = temp_live_numbers.groupby(
        "ライブ配信日_sortable", group_keys=False
    ).apply(assign_live_number_per_date, include_groups=False)

    # ステップ3: 元のDataFrameにライブ番号をマージ
    df_merged = pd.merge(
        df_merged,
        temp_live_numbers[["LIVE_ID", "ライブ番号"]],
        on=["LIVE_ID"],
        how="left",
        suffixes=("", "_new"),
    )

    # マージで重複した列がある場合は新しい方を使用
    if "ライブ番号_new" in df_merged.columns:
        df_merged["ライブ番号"] = df_merged["ライブ番号_new"]
        df_merged = df_merged.drop(columns=["ライブ番号_new"])

    # ステップ4: 各日付の配信数をカウント
    # 同一日に複数配信があるかどうかを判定するため
    live_counts_per_date = df_merged.groupby("ライブ配信日_sortable")[
        "LIVE_ID"
    ].transform("nunique")

    # ステップ5: 曲目番号の表示形式を決定
    # 同一日に複数配信がある場合: "1-3曲目"（1番目の配信の3曲目）
    # 同一日に単一配信の場合: "3曲目"
    df_merged["曲目"] = df_merged.apply(
        lambda row: (
            f"{row['ライブ番号']}-{row['曲順']}曲目"
            if live_counts_per_date.loc[row.name] > 1
            else f"{row['曲順']}曲目"
        ),
        axis=1,
    )

    st.session_state.df_full = df_merged.copy()

    # ===== 検索機能の実装 =====
    # キーワード検索により、曲名・アーティスト・配信タイトルから楽曲を絞り込む
    # セッション状態を使用して、検索条件と結果を保持する
    
    # セッション状態の初期化
    # Streamlitはページ再読み込み時に変数がリセットされるため、
    # session_stateを使用して状態を永続化する
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""  # 検索キーワード
    if "filtered_df" not in st.session_state:
        st.session_state.filtered_df = st.session_state.df_full.copy()  # フィルタリング後のデータ
    if "include_live_title" not in st.session_state:
        st.session_state.include_live_title = True  # 配信タイトル検索フラグ
    if "display_limit" not in st.session_state:
        st.session_state.display_limit = 25  # 初期表示件数（段階的表示用）
    if "search_query_prev" not in st.session_state:
        st.session_state.search_query_prev = st.session_state.search_query
    if "include_live_title_prev" not in st.session_state:
        st.session_state.include_live_title_prev = st.session_state.include_live_title

    # 検索UI要素の配置
    # テキスト入力ボックス: キーワード入力用
    current_input = st.text_input(
        "キーワード検索（曲名、アーティスト）",
        key="search_input_box",
        placeholder="ここにキーワードを入力",
    )

    # チェックボックス: 配信タイトルを検索対象に含めるかどうか
    current_checkbox_value = st.checkbox(
        "検索対象にライブ配信タイトルを含める",
        key="include_live_title_checkbox",
    )

    # 検索ボタン
    search_button = st.button("検索")

    # ===== 検索処理の実行 =====
    # 検索ボタンがクリックされた場合にフィルタリングを実行
    if search_button:
        # 現在の入力値をセッション状態に保存
        st.session_state.search_query = current_input
        st.session_state.include_live_title = current_checkbox_value
        st.session_state.display_limit = 25  # 検索条件が変わったら表示件数をリセット

        if st.session_state.search_query:
            # フィルタ条件の構築: 曲名またはアーティストに検索キーワードが含まれる
            # str.contains()で部分一致検索、case=Falseで大文字小文字を区別しない
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

            # チェックボックスがオンの場合、配信タイトルも検索対象に追加
            if st.session_state.include_live_title:
                filter_condition = filter_condition | st.session_state.df_full[
                    "ライブタイトル"
                ].astype(str).str.contains(
                    st.session_state.search_query, case=False, na=False
                )

            # フィルタ条件を適用してデータを絞り込む
            st.session_state.filtered_df = st.session_state.df_full[
                filter_condition
            ].copy()
            st.write(
                f"「{st.session_state.search_query}」で検索した結果: {len(st.session_state.filtered_df)}件"
            )
        else:
            # 検索キーワードが空の場合は全件表示
            st.session_state.filtered_df = st.session_state.df_full.copy()
            st.write("検索キーワードが入力されていません。全件表示します。")
    
    # 検索ボタンが押されていない場合の処理
    # 以前の検索結果を維持して表示
    elif st.session_state.search_query:
        # 検索キーワードが存在する場合は、以前のフィルタリング結果を表示
        st.write(
            f"「{st.session_state.search_query}」で検索した結果: {len(st.session_state.filtered_df)}件"
        )
    else:
        # 検索キーワードが空の場合は全件表示
        st.session_state.filtered_df = st.session_state.df_full.copy()
        st.write("検索キーワードが入力されていません。全件表示します。")

    # 現在の入力値を保存（次回の変更検知用）
    st.session_state.search_query_prev = current_input
    st.session_state.include_live_title_prev = current_checkbox_value

    # ===== 段階的表示処理 =====
    # 検索結果を25件ずつ段階的に表示することで、
    # 大量データでも初期表示速度を維持し、ユーザー体験を向上させる
    df_to_show = st.session_state.filtered_df.copy()

    # YouTubeリンクをHTML形式に変換
    # target="_blank"により、新しいタブで動画を開く
    df_to_show["YouTubeリンク"] = df_to_show.apply(
        lambda row: f'<a href="{row["YouTubeタイムスタンプ付きURL"]}" target="_blank">YouTubeへ👻</a>',
        axis=1,
    )

    # 表示に不要な内部処理用の列を削除
    # これにより、ユーザーに見せる情報を整理する
    df_to_show = df_to_show.drop(
        columns=[
            "YouTubeタイムスタンプ付きURL",  # HTMLリンク生成後は不要
            "ライブ配信日_original",          # 元の配信日データ（内部処理用）
            "ライブ配信日_sortable",          # ソート用の日付データ
            "タイムスタンプ_秒",              # 秒数変換後のデータ（URL生成に使用済み）
            "LIVE_ID",                       # 内部ID
            "楽曲ID",                        # 内部ID
            "タイムスタンプ",                # 元のタイムスタンプ文字列
            "ライブタイトル",                # 検索には使用したが表示は不要
            "元ライブURL",                   # タイムスタンプ付きURL生成に使用済み
        ],
        errors="ignore",  # 列が存在しない場合もエラーを出さない
    )

    # アーティスト列にカスタムCSSクラスを適用
    # style.cssの.artist-cellクラスにより、アーティスト名のみ改行を許可
    # 長いアーティスト名でもテーブルレイアウトが崩れないようにする
    df_to_show["アーティスト"] = (
        df_to_show["アーティスト"]
        .astype(str)
        .apply(lambda x: f'<div class="artist-cell">{x}</div>')
    )

    # 表示する列の順序を定義
    final_display_columns = [
        "ライブ配信日",
        "曲目",
        "曲名",
        "アーティスト",
        "YouTubeリンク",
    ]
    # DataFrameに実際に存在する列のみを選択（安全性のため）
    final_display_columns = [
        col for col in final_display_columns if col in df_to_show.columns
    ]

    # 表示件数を制限（段階的表示）
    # display_limitはセッション状態で管理され、「さらに表示」ボタンで増加する
    df_limited_display = df_to_show[final_display_columns].head(
        st.session_state.display_limit
    )

    # DataFrameをHTMLテーブルに変換
    # escape=False: HTMLタグをそのまま表示（リンクとCSSクラスを有効化）
    # index=False: 行番号を非表示
    html_table = df_limited_display.to_html(
        escape=False, index=False, justify="left", classes="dataframe"
    )

    # テーブルヘッダーを短縮形に置き換え
    # より見やすく、コンパクトな表示にする
    custom_headers = {
        "ライブ配信日": "配信日",
        "曲目": "No.",
        "曲名": "曲名",
        "アーティスト": "アーティスト",
        "YouTubeリンク": "リンク",
    }
    for original, custom in custom_headers.items():
        html_table = html_table.replace(f"<th>{original}</th>", f"<th>{custom}</th>")

    # テーブルをスクロール可能なdivで囲む
    # 横幅が広い場合でも横スクロールで対応し、レイアウトが崩れないようにする
    scrollable_html = f"""
    <div style="overflow-x: auto; max-width: 100%;">
        {html_table}
    </div>
    """
    # 生成したHTMLをStreamlitで表示
    st.write(scrollable_html, unsafe_allow_html=True)

    # ===== 「さらに表示」ボタン =====
    # 表示件数が検索結果の総件数より少ない場合にボタンを表示
    if st.session_state.display_limit < len(st.session_state.filtered_df):
        if st.button(
            f"さらに25件表示（現在の表示: {min(st.session_state.display_limit, len(st.session_state.filtered_df))}/{len(st.session_state.filtered_df)}件）"
        ):
            # ボタンがクリックされたら表示件数を25件増やす
            st.session_state.display_limit += 25
            st.rerun()  # ページを再読み込みして更新を反映
    else:
        # 全件表示済みの場合はメッセージを表示
        st.info(f"全ての{len(st.session_state.filtered_df)}件が表示されています。")

else:
    st.warning(
        "必要なTSVファイルがすべて読み込めなかったため、結合データは表示できません。"
    )

# フッターの表示
display_footer()  # ★ここを呼び出す★
