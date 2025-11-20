"""
Data Serviceのユニットテスト

DataServiceクラスの各メソッドが正しく動作することを検証します。
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd

from src.services.data_service import DataService
from src.config.settings import Config
from tests.fixtures.sample_data import (
    SAMPLE_LIVES_DATA,
    SAMPLE_SONGS_DATA,
    SAMPLE_SONG_LIST_DATA,
    create_sample_tsv_file,
    create_sample_dataframe
)


class TestDataServiceDataLoading:
    """データ読み込み機能のテスト"""
    
    def test_load_lives_data_success(self, tmp_path):
        """配信データの正常な読み込みをテスト"""
        # 一時TSVファイルを作成
        lives_file = tmp_path / "M_YT_LIVE.TSV"
        df = pd.DataFrame(SAMPLE_LIVES_DATA)
        df.to_csv(lives_file, sep='\t', index=False, encoding='utf-8')
        
        # Configをモック
        config = Mock(spec=Config)
        config.lives_file_path = str(lives_file)
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config)
        result = service.load_lives_data()
        
        # 検証
        assert result is not None
        assert len(result) == 3
        assert list(result.columns) == ["ID", "配信日", "タイトル", "URL"]
        assert service.get_last_error() is None
    
    def test_load_lives_data_file_not_found(self):
        """存在しないファイルの読み込みをテスト"""
        # Configをモック（存在しないファイルパス）
        config = Mock(spec=Config)
        config.lives_file_path = "/nonexistent/path/M_YT_LIVE.TSV"
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config)
        result = service.load_lives_data()
        
        # 検証
        assert result is None
        assert service.get_last_error() is not None
        assert "見つかりません" in service.get_last_error()
    
    def test_load_songs_data_success(self, tmp_path):
        """楽曲データの正常な読み込みをテスト"""
        # 一時TSVファイルを作成
        songs_file = tmp_path / "M_YT_LIVE_TIMESTAMP.TSV"
        df = pd.DataFrame(SAMPLE_SONGS_DATA)
        df.to_csv(songs_file, sep='\t', index=False, encoding='utf-8')
        
        # Configをモック
        config = Mock(spec=Config)
        config.songs_file_path = str(songs_file)
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config)
        result = service.load_songs_data()
        
        # 検証
        assert result is not None
        assert len(result) == 5
        assert "曲名" in result.columns
        assert "タイムスタンプ" in result.columns
        assert service.get_last_error() is None
    
    def test_load_songs_data_file_not_found(self):
        """存在しない楽曲ファイルの読み込みをテスト"""
        # Configをモック（存在しないファイルパス）
        config = Mock(spec=Config)
        config.songs_file_path = "/nonexistent/path/M_YT_LIVE_TIMESTAMP.TSV"
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config)
        result = service.load_songs_data()
        
        # 検証
        assert result is None
        assert service.get_last_error() is not None
        assert "見つかりません" in service.get_last_error()
    
    def test_load_song_list_data_success(self, tmp_path):
        """楽曲リストデータの正常な読み込みをテスト"""
        # 一時TSVファイルを作成
        song_list_file = tmp_path / "V_SONG_LIST.TSV"
        df = pd.DataFrame(SAMPLE_SONG_LIST_DATA)
        df.to_csv(song_list_file, sep='\t', index=False, encoding='utf-8')
        
        # Configをモック
        config = Mock(spec=Config)
        config.song_list_file_path = str(song_list_file)
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config)
        result = service.load_song_list_data()
        
        # 検証
        assert result is not None
        assert len(result) == 5
        assert "曲名" in result.columns
        assert "アーティスト" in result.columns
        assert service.get_last_error() is None
    
    def test_load_song_list_data_file_not_found(self):
        """存在しない楽曲リストファイルの読み込みをテスト"""
        # Configをモック（存在しないファイルパス）
        config = Mock(spec=Config)
        config.song_list_file_path = "/nonexistent/path/V_SONG_LIST.TSV"
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config)
        result = service.load_song_list_data()
        
        # 検証
        assert result is None
        assert service.get_last_error() is not None
        assert "見つかりません" in service.get_last_error()
    
    def test_load_lives_data_general_exception(self, tmp_path):
        """load_lives_dataで一般的な例外が発生した場合の処理をテスト"""
        # 一時TSVファイルを作成（不正なフォーマット）
        lives_file = tmp_path / "M_YT_LIVE.TSV"
        lives_file.write_text("Invalid\tTSV\tFormat\nWith\tInconsistent\tColumns\nAnd\tMore", encoding='utf-8')
        
        # Configをモック
        config = Mock(spec=Config)
        config.lives_file_path = str(lives_file)
        
        # pd.read_csvがParserErrorを発生させるようにモック
        with patch('pandas.read_csv') as mock_read_csv:
            mock_read_csv.side_effect = ValueError("Invalid data format")
            
            # DataServiceを初期化してデータを読み込む
            service = DataService(config)
            result = service.load_lives_data()
            
            # 検証
            assert result is None
            assert service.get_last_error() is not None
            assert "読み込み中にエラーが発生しました" in service.get_last_error()
            assert "Invalid data format" in service.get_last_error()
    
    def test_load_songs_data_general_exception(self, tmp_path):
        """load_songs_dataで一般的な例外が発生した場合の処理をテスト"""
        # 一時TSVファイルを作成
        songs_file = tmp_path / "M_YT_LIVE_TIMESTAMP.TSV"
        songs_file.write_text("Invalid\tData", encoding='utf-8')
        
        # Configをモック
        config = Mock(spec=Config)
        config.songs_file_path = str(songs_file)
        
        # pd.read_csvがValueErrorを発生させるようにモック
        with patch('pandas.read_csv') as mock_read_csv:
            mock_read_csv.side_effect = ValueError("Parsing error")
            
            # DataServiceを初期化してデータを読み込む
            service = DataService(config)
            result = service.load_songs_data()
            
            # 検証
            assert result is None
            assert service.get_last_error() is not None
            assert "読み込み中にエラーが発生しました" in service.get_last_error()
            assert "Parsing error" in service.get_last_error()
    
    def test_load_song_list_data_general_exception(self, tmp_path):
        """load_song_list_dataで一般的な例外が発生した場合の処理をテスト"""
        # 一時TSVファイルを作成
        song_list_file = tmp_path / "V_SONG_LIST.TSV"
        song_list_file.write_text("Bad\tFormat", encoding='utf-8')
        
        # Configをモック
        config = Mock(spec=Config)
        config.song_list_file_path = str(song_list_file)
        
        # pd.read_csvがRuntimeErrorを発生させるようにモック
        with patch('pandas.read_csv') as mock_read_csv:
            mock_read_csv.side_effect = RuntimeError("Unexpected error")
            
            # DataServiceを初期化してデータを読み込む
            service = DataService(config)
            result = service.load_song_list_data()
            
            # 検証
            assert result is None
            assert service.get_last_error() is not None
            assert "読み込み中にエラーが発生しました" in service.get_last_error()
            assert "Unexpected error" in service.get_last_error()


class TestDataServiceDataMerging:
    """データ結合機能のテスト"""
    
    def test_merge_data_success(self):
        """正常なデータ結合をテスト"""
        # サンプルデータを作成
        lives_df = create_sample_dataframe(SAMPLE_LIVES_DATA)
        songs_df = create_sample_dataframe(SAMPLE_SONGS_DATA)
        
        # Configをモック
        config = Mock(spec=Config)
        
        # DataServiceを初期化してデータを結合
        service = DataService(config)
        result = service.merge_data(lives_df, songs_df)
        
        # 検証
        assert result is not None
        assert len(result) == 5  # 楽曲データの件数と一致
        assert "楽曲ID" in result.columns
        assert "ライブタイトル" in result.columns
        assert "元ライブURL" in result.columns
        assert "ID_live" not in result.columns  # 削除されているはず
        assert service.get_last_error() is None
    
    def test_merge_data_column_renaming(self):
        """列名の変更が正しく行われることをテスト"""
        # サンプルデータを作成
        lives_df = create_sample_dataframe(SAMPLE_LIVES_DATA)
        songs_df = create_sample_dataframe(SAMPLE_SONGS_DATA)
        
        # Configをモック
        config = Mock(spec=Config)
        
        # DataServiceを初期化してデータを結合
        service = DataService(config)
        result = service.merge_data(lives_df, songs_df)
        
        # 検証：列名が正しく変更されている
        assert "楽曲ID" in result.columns
        assert "ライブ配信日_original" in result.columns
        assert "ライブタイトル" in result.columns
        assert "元ライブURL" in result.columns
    
    def test_merge_data_removes_unnecessary_columns(self):
        """不要な列が削除されることをテスト"""
        # サンプルデータを作成
        lives_df = create_sample_dataframe(SAMPLE_LIVES_DATA)
        songs_df = create_sample_dataframe(SAMPLE_SONGS_DATA)
        
        # Configをモック
        config = Mock(spec=Config)
        
        # DataServiceを初期化してデータを結合
        service = DataService(config)
        result = service.merge_data(lives_df, songs_df)
        
        # 検証：ID_liveが削除されている
        assert "ID_live" not in result.columns


class TestDataServiceErrorHandling:
    """エラーハンドリング機能のテスト"""
    
    def test_get_last_error_after_success(self, tmp_path):
        """成功後のエラーメッセージがNoneであることをテスト"""
        # 一時TSVファイルを作成
        lives_file = tmp_path / "M_YT_LIVE.TSV"
        df = pd.DataFrame(SAMPLE_LIVES_DATA)
        df.to_csv(lives_file, sep='\t', index=False, encoding='utf-8')
        
        # Configをモック
        config = Mock(spec=Config)
        config.lives_file_path = str(lives_file)
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config)
        service.load_lives_data()
        
        # 検証
        assert service.get_last_error() is None
    
    def test_get_last_error_after_failure(self):
        """失敗後のエラーメッセージが設定されることをテスト"""
        # Configをモック（存在しないファイルパス）
        config = Mock(spec=Config)
        config.lives_file_path = "/nonexistent/path/M_YT_LIVE.TSV"
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config)
        service.load_lives_data()
        
        # 検証
        error_message = service.get_last_error()
        assert error_message is not None
        assert isinstance(error_message, str)
        assert len(error_message) > 0
    
    def test_error_message_cleared_on_success(self):
        """成功時にエラーメッセージがクリアされることをテスト"""
        # Configをモック
        config = Mock(spec=Config)
        config.lives_file_path = "/nonexistent/path/M_YT_LIVE.TSV"
        
        # DataServiceを初期化
        service = DataService(config)
        
        # 最初は失敗させる
        service.load_lives_data()
        assert service.get_last_error() is not None
        
        # 次は成功させる（一時ファイルを作成）
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False, encoding='utf-8') as f:
            df = pd.DataFrame(SAMPLE_LIVES_DATA)
            df.to_csv(f.name, sep='\t', index=False)
            config.lives_file_path = f.name
            
            service.load_lives_data()
            
            # 検証：エラーメッセージがクリアされている
            assert service.get_last_error() is None
            
            # クリーンアップ
            os.unlink(f.name)
