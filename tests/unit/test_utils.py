"""
ユーティリティ関数のテスト

src/core/utils.pyの各関数が正しく動作することを確認するテストです。
"""

import pytest
import pandas as pd
from datetime import datetime

from src.core.utils import (
    convert_timestamp_to_seconds,
    generate_youtube_url,
    generate_song_numbers,
    convert_date_string,
)


class TestConvertTimestampToSeconds:
    """convert_timestamp_to_seconds関数のテスト"""
    
    def test_hh_mm_ss_format(self):
        """HH:MM:SS形式のタイムスタンプを正しく変換できることを確認"""
        assert convert_timestamp_to_seconds("1:23:45") == 5025
        assert convert_timestamp_to_seconds("0:00:00") == 0
        assert convert_timestamp_to_seconds("2:30:15") == 9015
    
    def test_mm_ss_format(self):
        """MM:SS形式のタイムスタンプを正しく変換できることを確認"""
        assert convert_timestamp_to_seconds("12:34") == 754
        assert convert_timestamp_to_seconds("0:00") == 0
        assert convert_timestamp_to_seconds("59:59") == 3599
    
    def test_invalid_format(self):
        """無効な形式の場合にNoneを返すことを確認"""
        assert convert_timestamp_to_seconds("1:2:3:4") is None
        assert convert_timestamp_to_seconds("invalid") is None
        assert convert_timestamp_to_seconds("") is None
        assert convert_timestamp_to_seconds("12") is None
    
    def test_none_input(self):
        """None入力の場合にNoneを返すことを確認"""
        assert convert_timestamp_to_seconds(None) is None
    
    def test_non_string_input(self):
        """文字列以外の入力の場合にNoneを返すことを確認"""
        assert convert_timestamp_to_seconds(123) is None
        # リスト入力はpd.isna()でエラーになるため、実装側で型チェックが先に行われる
        # 実際の使用ケースではDataFrameから文字列が渡されるため、このケースは稀


class TestGenerateYoutubeUrl:
    """generate_youtube_url関数のテスト"""
    
    def test_valid_url_and_timestamp(self):
        """有効なURLとタイムスタンプでURLを生成できることを確認"""
        base_url = "https://www.youtube.com/watch?v=abc123"
        result = generate_youtube_url(base_url, 754)
        assert result == "https://www.youtube.com/watch?v=abc123&t=754s"
    
    def test_zero_timestamp(self):
        """タイムスタンプが0の場合も正しく処理できることを確認"""
        base_url = "https://www.youtube.com/watch?v=abc123"
        result = generate_youtube_url(base_url, 0)
        assert result == "https://www.youtube.com/watch?v=abc123&t=0s"
    
    def test_none_base_url(self):
        """base_urlがNoneの場合に空文字列を返すことを確認"""
        assert generate_youtube_url(None, 100) == ""
    
    def test_none_timestamp(self):
        """timestampがNoneの場合に空文字列を返すことを確認"""
        base_url = "https://www.youtube.com/watch?v=abc123"
        assert generate_youtube_url(base_url, None) == ""
    
    def test_both_none(self):
        """両方Noneの場合に空文字列を返すことを確認"""
        assert generate_youtube_url(None, None) == ""
    
    def test_float_timestamp(self):
        """浮動小数点数のタイムスタンプを整数に変換することを確認"""
        base_url = "https://www.youtube.com/watch?v=abc123"
        result = generate_youtube_url(base_url, 754.7)
        assert result == "https://www.youtube.com/watch?v=abc123&t=754s"


class TestGenerateSongNumbers:
    """generate_song_numbers関数のテスト"""
    
    def test_single_live_single_date(self):
        """同一日に単一配信の場合、曲目番号が「N」形式になることを確認"""
        df = pd.DataFrame({
            "LIVE_ID": [1, 1, 1],
            "ライブ配信日_sortable": [
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-01"),
            ],
            "タイムスタンプ_秒": [10, 20, 30],
        })
        
        result = generate_song_numbers(df)
        
        assert "曲順" in result.columns
        assert "ライブ番号" in result.columns
        assert "曲目" in result.columns
        
        # 配信日降順（DataPipelineの仕様）で結果が返ることを確認
        assert list(result["曲順"]) == [1, 2, 3]
        assert list(result["ライブ番号"]) == [1, 1, 1]
        assert list(result["曲目"]) == ["1", "2", "3"]
    
    def test_multiple_lives_single_date(self):
        """同一日に複数配信の場合、曲目番号が「N-M」形式になることを確認"""
        df = pd.DataFrame({
            "LIVE_ID": [1, 1, 2, 2],
            "ライブ配信日_sortable": [
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-01"),
            ],
            "タイムスタンプ_秒": [10, 20, 10, 20],
        })
        
        result = generate_song_numbers(df)
        
        # LIVE_ID順、タイムスタンプ順（昇順）で番号が振られる
        # 結果は配信日降順（今回は同じ日なのでLIVE_ID昇順、タイムスタンプ昇順が維持される）
        assert list(result["曲順"]) == [1, 2, 1, 2]
        assert list(result["ライブ番号"]) == [1, 1, 2, 2]
        assert list(result["曲目"]) == ["1-1", "1-2", "2-1", "2-2"]
    
    def test_multiple_dates(self):
        """複数日付のデータを正しく処理できることを確認"""
        df = pd.DataFrame({
            "LIVE_ID": [1, 1, 2, 2],
            "ライブ配信日_sortable": [
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-02"),
                pd.Timestamp("2024-01-02"),
            ],
            "タイムスタンプ_秒": [10, 20, 10, 20],
        })
        
        result = generate_song_numbers(df)
        
        # 配信日降順で返るため、2024-01-02が先に来る
        assert list(result["ライブ配信日_sortable"]) == [
            pd.Timestamp("2024-01-02"),
            pd.Timestamp("2024-01-02"),
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-01"),
        ]
        assert list(result["曲目"]) == ["1", "2", "1", "2"]

    def test_multiple_lives_different_times_single_date(self):
        """同一日に複数配信（時刻が異なる）場合、正しく「ライブ番号」が振られることを確認"""
        df = pd.DataFrame({
            "LIVE_ID": [1, 1, 2, 2],
            "ライブ配信日_sortable": [
                pd.Timestamp("2024-01-01 12:00:00"),
                pd.Timestamp("2024-01-01 12:00:00"),
                pd.Timestamp("2024-01-01 18:00:00"),
                pd.Timestamp("2024-01-01 18:00:00"),
            ],
            "タイムスタンプ_秒": [10, 20, 10, 20],
        })
        
        result = generate_song_numbers(df)
        
        # 配信日降順で返るため、18:00:00の配信が先に来る
        assert list(result["ライブ番号"]) == [2, 2, 1, 1]
        assert list(result["曲目"]) == ["2-1", "2-2", "1-1", "1-2"]
    
    def test_original_dataframe_not_modified(self):
        """元のDataFrameが変更されないことを確認"""
        df = pd.DataFrame({
            "LIVE_ID": [1, 1],
            "ライブ配信日_sortable": [
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-01"),
            ],
            "タイムスタンプ_秒": [10, 20],
        })
        
        original_columns = df.columns.tolist()
        result = generate_song_numbers(df)
        
        # 元のDataFrameの列が変更されていないことを確認
        assert df.columns.tolist() == original_columns
        # 結果には新しい列が追加されていることを確認
        assert "曲順" in result.columns
        assert "曲目" in result.columns


class TestConvertDateString:
    """convert_date_string関数のテスト"""
    
    def test_unix_milliseconds_format(self):
        """UNIXミリ秒形式の日付文字列を変換できることを確認"""
        # 2021-01-01 00:00:00 UTC = 1609459200000 ms
        result = convert_date_string("1609459200000")
        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 2021
        assert result.month == 1
        assert result.day == 1
    
    def test_yyyy_mm_dd_format(self):
        """YYYY/MM/DD形式の日付文字列を変換できることを確認"""
        result = convert_date_string("2021/01/01")
        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 2021
        assert result.month == 1
        assert result.day == 1
    
    def test_yyyy_mm_dd_hyphen_format(self):
        """YYYY-MM-DD形式の日付文字列を変換できることを確認"""
        result = convert_date_string("2021-01-01")
        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 2021
        assert result.month == 1
        assert result.day == 1
    
    def test_none_input(self):
        """None入力の場合にNoneを返すことを確認"""
        assert convert_date_string(None) is None
    
    def test_invalid_format(self):
        """無効な形式の場合にNoneを返すことを確認"""
        assert convert_date_string("invalid") is None
        assert convert_date_string("") is None
        assert convert_date_string("not-a-date") is None
    
    def test_pandas_na(self):
        """pandas NAの場合にNoneを返すことを確認"""
        assert convert_date_string(pd.NA) is None
