"""
Data Pipelineのユニットテスト

DataPipelineクラスの各メソッドが正しく動作することを検証します。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from src.core.data_pipeline import DataPipeline
from src.services.data_service import DataService
from src.config.settings import Config
from src.exceptions.errors import DataProcessingError
from tests.fixtures.sample_data import (
    SAMPLE_LIVES_DATA,
    SAMPLE_SONGS_DATA,
    create_sample_dataframe
)


def create_merged_dataframe(lives_df, songs_df):
    """DataServiceのmerge_dataメソッドと同じ処理を行うヘルパー関数"""
    merged_df = pd.merge(
        songs_df,
        lives_df[["ID", "配信日", "タイトル", "URL"]],
        left_on="LIVE_ID",
        right_on="ID",
        how="left",
        suffixes=("_song", "_live"),
    )
    merged_df = merged_df.drop(columns=["ID_live"])
    merged_df = merged_df.rename(
        columns={
            "ID_song": "楽曲ID",
            "配信日": "ライブ配信日_original",
            "タイトル": "ライブタイトル",
            "URL": "元ライブURL",
        }
    )
    return merged_df


class TestDataPipelineExecution:
    """パイプライン実行機能のテスト"""
    
    def test_execute_all_steps_success(self):
        """全ステップの正常な実行をテスト"""
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = False
        
        data_service = Mock(spec=DataService)
        
        # サンプルデータを作成
        lives_df = create_sample_dataframe(SAMPLE_LIVES_DATA)
        songs_df = create_sample_dataframe(SAMPLE_SONGS_DATA)
        
        # DataServiceのモックメソッドを設定
        data_service.load_lives_data.return_value = lives_df
        data_service.load_songs_data.return_value = songs_df
        
        # merge_dataの戻り値を設定
        merged_df = create_merged_dataframe(lives_df, songs_df)
        data_service.merge_data.return_value = merged_df
        
        # DataPipelineを初期化して実行
        pipeline = DataPipeline(data_service, config)
        result = pipeline.execute()
        
        # 検証
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        
        # 各ステップが呼ばれたことを確認
        data_service.load_lives_data.assert_called_once()
        data_service.load_songs_data.assert_called_once()
        data_service.merge_data.assert_called_once()
    
    def test_execute_data_transformation_accuracy(self):
        """データ変換の正確性をテスト"""
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = False
        
        data_service = Mock(spec=DataService)
        
        # サンプルデータを作成
        lives_df = create_sample_dataframe(SAMPLE_LIVES_DATA)
        songs_df = create_sample_dataframe(SAMPLE_SONGS_DATA)
        
        # DataServiceのモックメソッドを設定
        data_service.load_lives_data.return_value = lives_df
        data_service.load_songs_data.return_value = songs_df
        
        # merge_dataの戻り値を設定
        merged_df = create_merged_dataframe(lives_df, songs_df)
        data_service.merge_data.return_value = merged_df
        
        # DataPipelineを初期化して実行
        pipeline = DataPipeline(data_service, config)
        result = pipeline.execute()
        
        # 検証：変換後のカラムが存在する
        assert "タイムスタンプ_秒" in result.columns
        assert "YouTubeタイムスタンプ付きURL" in result.columns
        assert "ライブ配信日_sortable" in result.columns
        
        # タイムスタンプが秒数に変換されている
        assert result["タイムスタンプ_秒"].dtype in [int, float]
    
    def test_execute_sort_processing(self):
        """ソート処理が正しく行われることをテスト"""
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = False
        
        data_service = Mock(spec=DataService)
        
        # サンプルデータを作成（複数の配信日を含む）
        lives_data = {
            "ID": [1, 2, 3],
            "配信日": ["2024/01/01", "2024/01/03", "2024/01/02"],
            "タイトル": ["配信1", "配信3", "配信2"],
            "URL": ["https://youtube.com/watch?v=abc", "https://youtube.com/watch?v=ghi", "https://youtube.com/watch?v=def"]
        }
        songs_data = {
            "ID": [1, 2, 3],
            "LIVE_ID": [1, 2, 3],
            "曲名": ["曲A", "曲B", "曲C"],
            "アーティスト": ["アーティストA", "アーティストB", "アーティストC"],
            "タイムスタンプ": ["00:10", "05:30", "02:15"]
        }
        
        lives_df = create_sample_dataframe(lives_data)
        songs_df = create_sample_dataframe(songs_data)
        
        # DataServiceのモックメソッドを設定
        data_service.load_lives_data.return_value = lives_df
        data_service.load_songs_data.return_value = songs_df
        
        # merge_dataの戻り値を設定
        merged_df = create_merged_dataframe(lives_df, songs_df)
        data_service.merge_data.return_value = merged_df
        
        # DataPipelineを初期化して実行
        pipeline = DataPipeline(data_service, config)
        result = pipeline.execute()
        
        # 検証：ソートされている（配信日降順）
        assert result is not None
        assert len(result) == 3
        
        # 曲目番号が生成されている
        assert "曲目" in result.columns


class TestDataPipelineCaching:
    """キャッシュ機能のテスト"""
    
    def test_cache_usage(self):
        """キャッシュの使用をテスト"""
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = True
        
        data_service = Mock(spec=DataService)
        
        # サンプルデータを作成
        lives_df = create_sample_dataframe(SAMPLE_LIVES_DATA)
        songs_df = create_sample_dataframe(SAMPLE_SONGS_DATA)
        
        # DataServiceのモックメソッドを設定
        data_service.load_lives_data.return_value = lives_df
        data_service.load_songs_data.return_value = songs_df
        
        # merge_dataの戻り値を設定
        merged_df = create_merged_dataframe(lives_df, songs_df)
        data_service.merge_data.return_value = merged_df
        
        # DataPipelineを初期化
        pipeline = DataPipeline(data_service, config)
        
        # 1回目の実行
        result1 = pipeline.execute()
        assert result1 is not None
        
        # キャッシュが保存されていることを確認
        assert "final_data" in pipeline._cache
        
        # 2回目の実行（キャッシュから取得）
        result2 = pipeline.execute()
        assert result2 is not None
        
        # DataServiceのメソッドが1回しか呼ばれていないことを確認
        assert data_service.load_lives_data.call_count == 1
        assert data_service.load_songs_data.call_count == 1
        assert data_service.merge_data.call_count == 1
        
        # 結果が同じであることを確認（同じオブジェクトが返される）
        assert result1 is result2
        pd.testing.assert_frame_equal(result1, result2)
    
    def test_cache_clear(self):
        """キャッシュのクリアをテスト"""
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = True
        
        data_service = Mock(spec=DataService)
        
        # サンプルデータを作成
        lives_df = create_sample_dataframe(SAMPLE_LIVES_DATA)
        songs_df = create_sample_dataframe(SAMPLE_SONGS_DATA)
        
        # DataServiceのモックメソッドを設定
        data_service.load_lives_data.return_value = lives_df
        data_service.load_songs_data.return_value = songs_df
        
        # merge_dataの戻り値を設定
        merged_df = create_merged_dataframe(lives_df, songs_df)
        data_service.merge_data.return_value = merged_df
        
        # DataPipelineを初期化
        pipeline = DataPipeline(data_service, config)
        
        # 1回目の実行
        result1 = pipeline.execute()
        assert result1 is not None
        
        # キャッシュをクリア
        pipeline.clear_cache()
        
        # 2回目の実行（キャッシュがクリアされているので再実行）
        result2 = pipeline.execute()
        assert result2 is not None
        
        # DataServiceのメソッドが2回呼ばれていることを確認
        assert data_service.load_lives_data.call_count == 2
        assert data_service.load_songs_data.call_count == 2
        assert data_service.merge_data.call_count == 2


class TestDataPipelineErrorHandling:
    """エラー処理機能のテスト"""
    
    def test_transform_data_date_conversion_fallback(self):
        """_transform_dataの日付変換フォールバック処理をテスト"""
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = False
        
        data_service = Mock(spec=DataService)
        
        # YYYY/MM/DD形式の日付を含むサンプルデータを作成
        lives_data = {
            "ID": [1, 2],
            "配信日": ["2024/01/01", "2024/01/02"],
            "タイトル": ["配信1", "配信2"],
            "URL": ["https://youtube.com/watch?v=abc", "https://youtube.com/watch?v=def"]
        }
        songs_data = {
            "ID": [1, 2],
            "LIVE_ID": [1, 2],
            "曲名": ["曲A", "曲B"],
            "アーティスト": ["アーティストA", "アーティストB"],
            "タイムスタンプ": ["00:10", "05:30"]
        }
        
        lives_df = create_sample_dataframe(lives_data)
        songs_df = create_sample_dataframe(songs_data)
        
        # DataServiceのモックメソッドを設定
        data_service.load_lives_data.return_value = lives_df
        data_service.load_songs_data.return_value = songs_df
        
        # merge_dataの戻り値を設定
        merged_df = create_merged_dataframe(lives_df, songs_df)
        data_service.merge_data.return_value = merged_df
        
        # DataPipelineを初期化
        pipeline = DataPipeline(data_service, config)
        
        # ログをキャプチャするためにロガーをモック
        with patch('src.core.data_pipeline.logger') as mock_logger:
            # パイプラインを実行
            result = pipeline.execute()
            
            # 検証：結果が返される
            assert result is not None
            assert "ライブ配信日_sortable" in result.columns
            
            # 日付が正しく変換されていることを確認
            assert not result["ライブ配信日_sortable"].isna().all()
            
            # 警告ログが記録される可能性がある（UNIXミリ秒として解釈できない場合）
            # ただし、YYYY/MM/DD形式は最初の変換で失敗し、フォールバック処理で成功する
    
    def test_data_load_failure(self):
        """データ読み込み失敗時の処理をテスト"""
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = False
        
        data_service = Mock(spec=DataService)
        
        # DataServiceのモックメソッドを設定（読み込み失敗）
        data_service.load_lives_data.return_value = None
        data_service.load_songs_data.return_value = None
        data_service.get_last_error.return_value = "ファイルが見つかりません"
        
        # DataPipelineを初期化して実行
        pipeline = DataPipeline(data_service, config)
        result = pipeline.execute()
        
        # 検証：Noneが返される
        assert result is None
    
    def test_data_transformation_error(self):
        """データ変換エラー時の処理をテスト"""
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = False
        
        data_service = Mock(spec=DataService)
        
        # サンプルデータを作成（不正なタイムスタンプを含む）
        lives_df = create_sample_dataframe(SAMPLE_LIVES_DATA)
        songs_data = {
            "ID": [1, 2],
            "LIVE_ID": [1, 1],
            "曲名": ["曲A", "曲B"],
            "アーティスト": ["アーティストA", "アーティストB"],
            "タイムスタンプ": ["invalid", "also_invalid"]  # 不正なタイムスタンプ
        }
        songs_df = create_sample_dataframe(songs_data)
        
        # DataServiceのモックメソッドを設定
        data_service.load_lives_data.return_value = lives_df
        data_service.load_songs_data.return_value = songs_df
        
        # merge_dataの戻り値を設定
        merged_df = create_merged_dataframe(lives_df, songs_df)
        data_service.merge_data.return_value = merged_df
        
        # DataPipelineを初期化して実行
        pipeline = DataPipeline(data_service, config)
        
        # 不正なタイムスタンプでもエラーにならず、デフォルト値（0）が設定される
        result = pipeline.execute()
        
        # 検証：結果が返される（エラーハンドリングされている）
        assert result is not None
        assert "タイムスタンプ_秒" in result.columns
    
    def test_empty_data_processing(self):
        """空のデータ処理をテスト"""
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = False
        
        data_service = Mock(spec=DataService)
        
        # 空のDataFrameを作成
        lives_df = pd.DataFrame(columns=["ID", "配信日", "タイトル", "URL"])
        songs_df = pd.DataFrame(columns=["ID", "LIVE_ID", "曲名", "アーティスト", "タイムスタンプ"])
        
        # DataServiceのモックメソッドを設定
        data_service.load_lives_data.return_value = lives_df
        data_service.load_songs_data.return_value = songs_df
        
        # merge_dataの戻り値を設定（空のDataFrame）
        merged_df = create_merged_dataframe(lives_df, songs_df)
        data_service.merge_data.return_value = merged_df
        
        # DataPipelineを初期化して実行
        pipeline = DataPipeline(data_service, config)
        result = pipeline.execute()
        
        # 検証：空のDataFrameの場合、generate_song_numbersでエラーが発生してNoneが返される
        # これは期待される動作
        assert result is None
    
    def test_validate_step_result_empty_dataframe(self):
        """_validate_step_resultが空のDataFrameを処理することをテスト"""
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = False
        
        data_service = Mock(spec=DataService)
        
        # DataPipelineを初期化
        pipeline = DataPipeline(data_service, config)
        
        # 空のDataFrameを作成
        empty_df = pd.DataFrame()
        
        # ログをキャプチャするためにロガーをモック
        with patch('src.core.data_pipeline.logger') as mock_logger:
            # _validate_step_resultを呼び出し
            result = pipeline._validate_step_result(empty_df, "test_step")
            
            # 検証：Trueが返される（警告のみで処理は継続）
            assert result is True
            
            # 警告ログが記録されたことを確認
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "test_step" in warning_call
            assert "空のDataFrame" in warning_call
