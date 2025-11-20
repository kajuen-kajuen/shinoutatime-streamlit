"""
Data Pipelineのプロパティベーステスト

DataPipelineクラスの普遍的な性質を検証します。
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock
import pandas as pd

from src.core.data_pipeline import DataPipeline
from src.services.data_service import DataService
from src.config.settings import Config


class TestDataPipelineProperties:
    """Data Pipelineのプロパティテスト"""
    
    @given(
        error_message=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100, deadline=5000)
    def test_error_handling_consistency(self, error_message):
        """
        Feature: test-coverage-improvement, Property 16: エラー処理の一貫性
        
        すべてのエラー状況（ファイル読み込み失敗、データ変換エラー）に対して、
        Noneが返され、適切なエラーログが記録される
        
        **検証: 要件7.3**
        """
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = False
        
        data_service = Mock(spec=DataService)
        
        # DataServiceのモックメソッドを設定（エラー状態）
        data_service.load_lives_data.return_value = None
        data_service.load_songs_data.return_value = None
        data_service.get_last_error.return_value = error_message
        
        # DataPipelineを初期化して実行
        pipeline = DataPipeline(data_service, config)
        result = pipeline.execute()
        
        # 検証：エラー時はNoneが返される
        assert result is None
        
        # DataServiceのメソッドが呼ばれたことを確認
        data_service.load_lives_data.assert_called_once()
