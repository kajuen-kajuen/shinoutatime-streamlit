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
    return ""


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
            - 曲目: 表示用の曲目番号（例: "1-3" または "3"）
    
    Examples:
        同一日に複数配信がある場合:
        - 1番目の配信の3曲目 → "1-3"
        - 2番目の配信の1曲目 → "2-1"
        
        同一日に単一配信の場合:
        - 3曲目 → "3"
    
    Notes:
        - 入力DataFrameは変更されず、コピーが返されます
        - LIVE_IDとライブ配信日_sortableカラムが必須です
    """
    df_result = df.copy()
    
    # 必須カラムの確認
    required_cols = ["LIVE_ID", "ライブ配信日_sortable", "タイムスタンプ_秒"]
    for col in required_cols:
        if col not in df_result.columns:
            # タイムスタンプ_秒がない場合は、ソート順が不安定になる可能性があるが、処理は継続可能
            logger.warning(f"Required column '{col}' not found in DataFrame for generate_song_numbers")
    
    # ソート用に日付のみを抽出した列を作成
    df_result["_temp_date"] = df_result["ライブ配信日_sortable"].dt.date
    
    # 全体を正しい順序（古い順）にソート
    sort_cols = ["ライブ配信日_sortable", "LIVE_ID"]
    if "タイムスタンプ_秒" in df_result.columns:
        sort_cols.append("タイムスタンプ_秒")
        
    df_result = df_result.sort_values(by=sort_cols).reset_index(drop=True)
    
    # ステップ1: 各配信内での曲順を計算
    # groupby("LIVE_ID").cumcount()により、各配信内で0から始まる連番を生成し、+1で1始まりにする
    df_result["曲順"] = df_result.groupby("LIVE_ID").cumcount() + 1

    # ステップ2: 同一日内の配信に番号を振る（ライブ番号）
    # 日付とLIVE_IDの組み合わせを抽出し、その日の何番目の配信かを取得
    df_live_order = df_result[["_temp_date", "LIVE_ID", "ライブ配信日_sortable"]].drop_duplicates()
    df_live_order = df_live_order.sort_values(["_temp_date", "ライブ配信日_sortable", "LIVE_ID"])
    df_live_order["ライブ番号"] = df_live_order.groupby("_temp_date").cumcount() + 1
    
    # 元のDFにマージ（ライブ番号を付与）
    df_result = pd.merge(
        df_result, 
        df_live_order[["_temp_date", "LIVE_ID", "ライブ番号"]], 
        on=["_temp_date", "LIVE_ID"], 
        how="left"
    )

    # ステップ3: 各日付の配信数をカウント
    # 同一日に複数配信があるかどうかを判定するため
    live_counts_per_date = df_result.groupby("_temp_date")["LIVE_ID"].transform("nunique")

    # ステップ4: 曲目番号の表示形式を決定
    # 同一日に複数配信がある場合: "1-3"（1番目の配信の3曲目）
    # 同一日に単一配信の場合: "3"
    df_result["曲目"] = df_result.apply(
        lambda row: (
            f"{row['ライブ番号']}-{row['曲順']}"
            if live_counts_per_date.loc[row.name] > 1
            else str(row['曲順'])
        ),
        axis=1,
    )
    
    # 不要な一時列を削除
    df_result = df_result.drop(columns=["_temp_date"])
    
    # 元の順序（DataPipelineでのソート順：配信日降順）に戻す
    df_result = df_result.sort_values(
        by=["ライブ配信日_sortable", "LIVE_ID"] + (["タイムスタンプ_秒"] if "タイムスタンプ_秒" in df_result.columns else []),
        ascending=[False, True] + ([True] if "タイムスタンプ_秒" in df_result.columns else [])
    ).reset_index(drop=True)
    
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
