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
from src.repositories.live_repository import LiveRepository
from src.repositories.timestamp_repository import TimestampRepository
from src.repositories.song_list_repository import SongListRepository
from src.exceptions.errors import DataLoadError
from tests.fixtures.sample_data import (
    SAMPLE_LIVES_DATA,
    SAMPLE_SONGS_DATA,
    SAMPLE_SONG_LIST_DATA,
    create_sample_tsv_file,
    create_sample_dataframe
)


class TestDataServiceDataLoading:
    """データ読み込み機能のテスト"""
    
    def test_load_lives_data_success(self):
        """配信データの正常な読み込みをテスト"""
        # サンプルデータ
        df = pd.DataFrame(SAMPLE_LIVES_DATA)
        
        # モックの作成
        config = Mock(spec=Config)
        live_repo = Mock(spec=LiveRepository)
        live_repo.load_as_dataframe.return_value = df
        timestamp_repo = Mock(spec=TimestampRepository)
        song_list_repo = Mock(spec=SongListRepository)
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config, live_repo, timestamp_repo, song_list_repo)
        result = service.load_lives_data()
        
        # 検証
        assert result is not None
        assert len(result) == 3
        assert list(result.columns) == ["ID", "配信日", "タイトル", "URL"]
        live_repo.load_as_dataframe.assert_called_once()
    
    def test_load_lives_data_error(self):
        """配信データの読み込みエラーをテスト"""
        # モックの作成
        config = Mock(spec=Config)
        live_repo = Mock(spec=LiveRepository)
        live_repo.load_as_dataframe.side_effect = DataLoadError("M_YT_LIVE.TSV", "ファイルが見つかりません")
        timestamp_repo = Mock(spec=TimestampRepository)
        song_list_repo = Mock(spec=SongListRepository)
        
        # DataServiceを初期化
        service = DataService(config, live_repo, timestamp_repo, song_list_repo)
        
        # 検証
        with pytest.raises(DataLoadError) as excinfo:
            service.load_lives_data()
        assert "ファイルが見つかりません" in str(excinfo.value)
    
    def test_load_songs_data_success(self):
        """楽曲データの正常な読み込みをテスト"""
        # サンプルデータ
        df = pd.DataFrame(SAMPLE_SONGS_DATA)
        
        # モックの作成
        config = Mock(spec=Config)
        live_repo = Mock(spec=LiveRepository)
        timestamp_repo = Mock(spec=TimestampRepository)
        timestamp_repo.load_as_dataframe.return_value = df
        song_list_repo = Mock(spec=SongListRepository)
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config, live_repo, timestamp_repo, song_list_repo)
        result = service.load_songs_data()
        
        # 検証
        assert result is not None
        assert len(result) == 5
        assert "曲名" in result.columns
        assert "タイムスタンプ" in result.columns
        timestamp_repo.load_as_dataframe.assert_called_once()
    
    def test_load_songs_data_error(self):
        """楽曲データの読み込みエラーをテスト"""
        # モックの作成
        config = Mock(spec=Config)
        live_repo = Mock(spec=LiveRepository)
        timestamp_repo = Mock(spec=TimestampRepository)
        timestamp_repo.load_as_dataframe.side_effect = DataLoadError("songs.tsv", "読み込みエラー")
        song_list_repo = Mock(spec=SongListRepository)
        
        # DataServiceを初期化
        service = DataService(config, live_repo, timestamp_repo, song_list_repo)
        
        # 検証
        with pytest.raises(DataLoadError) as excinfo:
            service.load_songs_data()
        assert "読み込みエラー" in str(excinfo.value)
    
    def test_load_song_list_data_success(self):
        """楽曲リストデータの正常な読み込みをテスト"""
        # サンプルデータ
        df = pd.DataFrame(SAMPLE_SONG_LIST_DATA)
        
        # モックの作成
        config = Mock(spec=Config)
        live_repo = Mock(spec=LiveRepository)
        timestamp_repo = Mock(spec=TimestampRepository)
        song_list_repo = Mock(spec=SongListRepository)
        song_list_repo.load_as_dataframe.return_value = df
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config, live_repo, timestamp_repo, song_list_repo)
        result = service.load_song_list_data()
        
        # 検証
        assert result is not None
        assert len(result) == 5
        assert "曲名" in result.columns
        assert "アーティスト" in result.columns
        song_list_repo.load_as_dataframe.assert_called_once()
    
    def test_load_song_list_data_error(self):
        """楽曲リストデータの読み込みエラーをテスト"""
        # モックの作成
        config = Mock(spec=Config)
        live_repo = Mock(spec=LiveRepository)
        timestamp_repo = Mock(spec=TimestampRepository)
        song_list_repo = Mock(spec=SongListRepository)
        song_list_repo.load_as_dataframe.side_effect = DataLoadError("song_list.tsv", "エラー")
        
        # DataServiceを初期化
        service = DataService(config, live_repo, timestamp_repo, song_list_repo)
        
        # 検証
        with pytest.raises(DataLoadError) as excinfo:
            service.load_song_list_data()
        assert "エラー" in str(excinfo.value)
    


class TestDataServiceDataMerging:
    """データ結合機能のテスト"""
    
    def test_merge_data_success(self):
        """正常なデータ結合をテスト"""
        # サンプルデータを作成
        lives_df = create_sample_dataframe(SAMPLE_LIVES_DATA)
        songs_df = create_sample_dataframe(SAMPLE_SONGS_DATA)
        
        # モックの作成
        config = Mock(spec=Config)
        live_repo = Mock(spec=LiveRepository)
        timestamp_repo = Mock(spec=TimestampRepository)
        song_list_repo = Mock(spec=SongListRepository)
        
        # DataServiceを初期化してデータを結合
        service = DataService(config, live_repo, timestamp_repo, song_list_repo)
        result = service.merge_data(lives_df, songs_df)
        
        # 検証
        assert result is not None
        assert len(result) == 5  # 楽曲データの件数と一致
        assert "楽曲ID" in result.columns
        assert "ライブタイトル" in result.columns
        assert "元ライブURL" in result.columns
        assert "ID_live" not in result.columns  # 削除されているはず
    
    def test_merge_data_column_renaming(self):
        """列名の変更が正しく行われることをテスト"""
        # サンプルデータを作成
        lives_df = create_sample_dataframe(SAMPLE_LIVES_DATA)
        songs_df = create_sample_dataframe(SAMPLE_SONGS_DATA)
        
        # モックの作成
        config = Mock(spec=Config)
        live_repo = Mock(spec=LiveRepository)
        timestamp_repo = Mock(spec=TimestampRepository)
        song_list_repo = Mock(spec=SongListRepository)
        
        # DataServiceを初期化してデータを結合
        service = DataService(config, live_repo, timestamp_repo, song_list_repo)
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
        
        # モック
        config = Mock(spec=Config)
        live_repo = Mock(spec=LiveRepository)
        timestamp_repo = Mock(spec=TimestampRepository)
        song_list_repo = Mock(spec=SongListRepository)
        
        # DataServiceを初期化してデータを結合
        service = DataService(config, live_repo, timestamp_repo, song_list_repo)
        result = service.merge_data(lives_df, songs_df)
        
        # 検証：ID_liveが削除されている
        assert "ID_live" not in result.columns


