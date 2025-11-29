"""
ユーティリティ関数モジュール

汎用的なデータ変換・処理関数を提供します。
各関数は純粋関数として実装され、副作用を持ちません。
"""

import logging
from typing import Optional
from datetime import datetime
import pandas as pd

# ロガーの設定
logger = logging.getLogger(__name__)


def convert_timestamp_to_seconds(timestamp_str: str) -> Optional[int]:
    """
    タイムスタンプ文字列を秒数に変換する
    
    YouTubeのタイムスタンプ付きURL生成のために、
    HH:MM:SS形式またはMM:SS形式の時間文字列を秒数に変換します。
    
    Args:
        timestamp_str: タイムスタンプ文字列
            - HH:MM:SS形式（例: "1:23:45"）
            - MM:SS形式（例: "12:34"）
    
    Returns:
        変換された秒数。変換に失敗した場合はNone
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

    try:
        parts = list(map(int, timestamp_str.split(":")))

        if len(parts) == 3:
            # HH:MM:SS形式
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            # MM:SS形式
            return parts[0] * 60 + parts[1]
        else:
            return None
    except (ValueError, AttributeError):
        # 数値変換エラーまたは属性エラーの場合はNoneを返す
        return None


def generate_youtube_url(base_url: str, timestamp_seconds: int) -> str:
    """
    YouTubeタイムスタンプ付きURLを生成する
    
    配信URLにタイムスタンプパラメータ（&t=秒数s）を付加することで、
    リンクをクリックすると該当の歌唱箇所から再生が開始されるURLを生成します。
    
    Args:
        base_url: 基本URL（YouTube配信のURL）
        timestamp_seconds: タイムスタンプ（秒）
    
    Returns:
        タイムスタンプ付きURL
        - base_urlまたはtimestamp_secondsがNoneの場合は空文字列を返す
        - それ以外の場合は「base_url&t=秒数s」形式のURLを返す
    
    Examples:
        >>> generate_youtube_url("https://www.youtube.com/watch?v=abc123", 754)
        'https://www.youtube.com/watch?v=abc123&t=754s'
        >>> generate_youtube_url(None, 100)
        ''
        >>> generate_youtube_url("https://www.youtube.com/watch?v=abc123", None)
        ''
    
    Notes:
        - base_urlにすでにタイムスタンプパラメータが含まれている場合でも、
          新しいタイムスタンプパラメータを追加します
    """
    if pd.isna(base_url):
        return ""
    if pd.notna(timestamp_seconds):
        return f"{base_url}&t={int(timestamp_seconds)}s"
    return base_url


def generate_song_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """
    曲目番号を生成する
    
    各配信内での楽曲の歌唱順序を示す曲目番号を生成します。
    同一日に複数配信がある場合は「配信番号-曲順」形式、
    単一配信の場合は「曲順」形式で表示します。
    
    Args:
        df: 楽曲データのDataFrame
            必須カラム:
            - LIVE_ID: 配信ID
            - ライブ配信日_sortable: ソート用の配信日（datetime型）
    
    Returns:
        曲目番号が追加されたDataFrame
            追加されるカラム:
            - 曲順: 各配信内での曲順（1から始まる連番）
            - ライブ番号: 同一日内の配信番号（1から始まる連番）
            - 曲目: 表示用の曲目番号（例: "1-3曲目" または "3曲目"）
    
    Examples:
        同一日に複数配信がある場合:
        - 1番目の配信の3曲目 → "1-3曲目"
        - 2番目の配信の1曲目 → "2-1曲目"
        
        同一日に単一配信の場合:
        - 3曲目 → "3曲目"
    
    Notes:
        - 入力DataFrameは変更されず、コピーが返されます
        - LIVE_IDとライブ配信日_sortableカラムが必須です
    """
    df_result = df.copy()
    
    # ステップ1: 各配信内での曲順を計算
    # groupby("LIVE_ID").cumcount()により、各配信内で0から始まる連番を生成し、+1で1始まりにする
    df_result["曲順"] = df_result.groupby("LIVE_ID").cumcount() + 1

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
        df_result[["ライブ配信日_sortable", "LIVE_ID"]].drop_duplicates().copy()
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
    df_result = pd.merge(
        df_result,
        temp_live_numbers[["LIVE_ID", "ライブ番号"]],
        on=["LIVE_ID"],
        how="left",
        suffixes=("", "_new"),
    )

    # マージで重複した列がある場合は新しい方を使用
    if "ライブ番号_new" in df_result.columns:
        df_result["ライブ番号"] = df_result["ライブ番号_new"]
        df_result = df_result.drop(columns=["ライブ番号_new"])

    # ステップ4: 各日付の配信数をカウント
    # 同一日に複数配信があるかどうかを判定するため
    live_counts_per_date = df_result.groupby("ライブ配信日_sortable")[
        "LIVE_ID"
    ].transform("nunique")

    # ステップ5: 曲目番号の表示形式を決定
    # 同一日に複数配信がある場合: "1-3曲目"（1番目の配信の3曲目）
    # 同一日に単一配信の場合: "3曲目"
    df_result["曲目"] = df_result.apply(
        lambda row: (
            f"{row['ライブ番号']}-{row['曲順']}曲目"
            if live_counts_per_date.loc[row.name] > 1
            else f"{row['曲順']}曲目"
        ),
        axis=1,
    )
    
    return df_result


def convert_date_string(date_str: str) -> Optional[datetime]:
    """
    日付文字列をdatetime型に変換する
    
    UNIXミリ秒形式またはYYYY/MM/DD形式の日付文字列を
    datetime型に変換します。
    
    Args:
        date_str: 日付文字列
            - UNIXミリ秒形式（例: "1609459200000"）
            - YYYY/MM/DD形式（例: "2021/01/01"）
            - その他のpandasが認識できる日付形式
    
    Returns:
        datetime型のオブジェクト。変換に失敗した場合はNone
    
    Examples:
        >>> convert_date_string("1609459200000")
        datetime.datetime(2021, 1, 1, 0, 0)
        >>> convert_date_string("2021/01/01")
        datetime.datetime(2021, 1, 1, 0, 0)
        >>> convert_date_string(None)
        None
        >>> convert_date_string("invalid")
        None
    
    Notes:
        - 入力がNoneまたは文字列でない場合はNoneを返す
        - まずUNIXミリ秒として変換を試み、失敗した場合は
          pandasのto_datetimeで一般的な日付形式として変換を試みる
    """
    if pd.isna(date_str):
        return None
    
    try:
        # まずUNIXミリ秒として変換を試みる（数値型に変換してから）
        try:
            numeric_value = float(date_str)
            result = pd.to_datetime(numeric_value, unit="ms", errors="coerce")
            if pd.notna(result):
                return result.to_pydatetime()
        except (ValueError, TypeError):
            # 数値変換に失敗した場合は次の方法を試す
            pass
        
        # UNIXミリ秒で変換できなかった場合、一般的な日付形式として変換
        result = pd.to_datetime(date_str, errors="coerce")
        if pd.notna(result):
            return result.to_pydatetime()
        
        return None
    except (ValueError, TypeError, AttributeError):
        return None
