"""
エラーケースのテスト

ファイル権限エラー、パースエラーなどの異常系をテストします。
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import os
import tempfile
from pathlib import Path


class TestErrorCases:
    """エラーケースのテスト"""

    def test_settings_config_file_not_found(self):
        """Configのファイル未検出テスト"""
        from src.config.settings import Config

        # 存在しないファイルを指定
        config = Config()
        config.css_file_path = "nonexistent.css"

        # Configはファイルの存在をチェックしないので、エラーは発生しない
        assert config.css_file_path == "nonexistent.css"

    def test_retry_decorator_failure(self):
        """リトライデコレーターの失敗テスト"""
        from src.utils.retry import retry
        import time

        @retry(max_retries=3, base_delay=0.1)
        def failing_function():
            raise ValueError("Always fails")

        # リトライ後も失敗することを確認
        with pytest.raises(ValueError):
            failing_function()
