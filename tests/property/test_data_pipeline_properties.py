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
from src.exceptions.errors import DataLoadError


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
        読み込みの例外(DataLoadError)が包み直されずにそのまま送出される

        **検証: 要件7.3**
        """
        # モックの設定
        config = Mock(spec=Config)
        config.enable_cache = False

        data_service = Mock(spec=DataService)

        # DataServiceのモックメソッドを設定（エラー状態。読み込みの失敗は例外で伝わる）
        data_service.load_lives_data.side_effect = DataLoadError("lives.tsv", error_message)

        # DataPipelineを初期化して実行
        pipeline = DataPipeline(data_service, config)

        # 検証：エラー時は DataLoadError がそのまま送出され、メッセージが残る
        with pytest.raises(DataLoadError) as excinfo:
            pipeline.execute()
        assert error_message in str(excinfo.value)

        # DataServiceのメソッドが呼ばれたことを確認
        data_service.load_lives_data.assert_called_once()
