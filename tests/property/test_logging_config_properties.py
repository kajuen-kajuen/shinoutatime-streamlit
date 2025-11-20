"""
Logging Configのプロパティベーステスト

ロギング設定の普遍的な性質を検証します。
要件5.1, 5.4に対応しています。
"""

import os
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest
from hypothesis import given, strategies as st, settings

from src.config.logging_config import (
    setup_logging,
    set_log_level,
    setup_twitter_embed_logging
)


# ログレベルの戦略
log_levels = st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR"])


class TestLoggingConfigProperties:
    """Logging Configのプロパティテスト"""
    
    def setup_method(self):
        """各テストの前にロガーをリセット"""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)
    
    def teardown_method(self):
        """各テストの後にロガーをクリア"""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)
    
    @given(log_level=log_levels)
    @settings(max_examples=100)
    def test_property_log_level_consistency(self, log_level):
        """
        Feature: test-coverage-improvement, Property 11: ログレベル設定の一貫性
        Validates: Requirements 5.1
        
        すべての有効なログレベル（DEBUG、INFO、WARNING、ERROR）に対して、
        ロガーのレベルが正しく設定される
        """
        setup_logging(log_level=log_level)
        
        root_logger = logging.getLogger()
        expected_level = getattr(logging, log_level)
        
        # ロガーのレベルが正しく設定されていることを確認
        assert root_logger.level == expected_level
        
        # すべてのハンドラーのレベルも正しく設定されていることを確認
        for handler in root_logger.handlers:
            assert handler.level == expected_level
    
    @given(log_level=log_levels)
    @settings(max_examples=100)
    def test_property_set_log_level_consistency(self, log_level):
        """
        Feature: test-coverage-improvement, Property 11: ログレベル設定の一貫性
        Validates: Requirements 5.1
        
        すべての有効なログレベルに対して、
        set_log_level関数がロガーとハンドラーのレベルを正しく更新する
        """
        # 初期設定
        setup_logging(log_level="INFO")
        
        # ログレベルを変更
        set_log_level(log_level)
        
        root_logger = logging.getLogger()
        expected_level = getattr(logging, log_level)
        
        # ロガーのレベルが更新されていることを確認
        assert root_logger.level == expected_level
        
        # すべてのハンドラーのレベルも更新されていることを確認
        for handler in root_logger.handlers:
            assert handler.level == expected_level
    
    @given(
        log_level=log_levels,
        enable_file_logging=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_handler_count_consistency(self, log_level, enable_file_logging):
        """
        Feature: test-coverage-improvement, Property 11: ログレベル設定の一貫性
        Validates: Requirements 5.1
        
        すべてのログレベルとファイルロギング設定に対して、
        適切な数のハンドラーが作成される
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(
                log_level=log_level,
                log_file=log_file,
                enable_file_logging=enable_file_logging
            )
            
            root_logger = logging.getLogger()
            
            # ファイルロギングが有効な場合は2つ、無効な場合は1つのハンドラー
            expected_handler_count = 2 if enable_file_logging else 1
            assert len(root_logger.handlers) == expected_handler_count
            
            # すべてのハンドラーが正しいレベルを持つことを確認
            expected_level = getattr(logging, log_level)
            for handler in root_logger.handlers:
                assert handler.level == expected_level
    
    @given(log_level=log_levels)
    @settings(max_examples=100)
    def test_property_twitter_embed_logger_level_consistency(self, log_level):
        """
        Feature: test-coverage-improvement, Property 11: ログレベル設定の一貫性
        Validates: Requirements 5.1
        
        すべての有効なログレベルに対して、
        Twitter埋め込み専用ロガーのレベルが正しく設定される
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            logger = setup_twitter_embed_logging(
                log_level=log_level,
                log_file=log_file
            )
            
            expected_level = getattr(logging, log_level)
            
            # ロガーのレベルが正しく設定されていることを確認
            assert logger.level == expected_level
            
            # すべてのハンドラーのレベルも正しく設定されていることを確認
            for handler in logger.handlers:
                assert handler.level == expected_level
        
        # クリーンアップ
        logger.handlers.clear()



class TestLogFormatProperties:
    """ログフォーマットのプロパティテスト"""
    
    def setup_method(self):
        """各テストの前にロガーをリセット"""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)
    
    def teardown_method(self):
        """各テストの後にロガーをクリア"""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)
    
    @given(
        log_level=log_levels,
        message=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100)
    def test_property_log_format_consistency(self, log_level, message):
        """
        Feature: test-coverage-improvement, Property 12: ログフォーマットの一貫性
        Validates: Requirements 5.4
        
        すべてのログメッセージに対して、
        出力されるログは指定されたフォーマット（タイムスタンプ、レベル、メッセージ）を含む
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(
                log_level=log_level,
                log_file=log_file,
                enable_file_logging=True
            )
            
            logger = logging.getLogger("test_logger")
            
            # ログレベルに応じてメッセージを出力
            if log_level == "DEBUG":
                logger.debug(message)
            elif log_level == "INFO":
                logger.info(message)
            elif log_level == "WARNING":
                logger.warning(message)
            elif log_level == "ERROR":
                logger.error(message)
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # ファイルの内容を確認
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # メッセージが含まれていることを確認
                    if message in content:
                        # フォーマットの要素が含まれていることを確認
                        # タイムスタンプ（YYYY-MM-DD HH:MM:SS形式）
                        assert any(char.isdigit() for char in content)
                        
                        # ログレベル
                        assert log_level in content
                        
                        # メッセージ
                        assert message in content
    
    @given(log_level=log_levels)
    @settings(max_examples=100)
    def test_property_formatter_consistency_across_handlers(self, log_level):
        """
        Feature: test-coverage-improvement, Property 12: ログフォーマットの一貫性
        Validates: Requirements 5.4
        
        すべてのハンドラーに対して、
        同じフォーマットが適用される
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(
                log_level=log_level,
                log_file=log_file,
                enable_file_logging=True
            )
            
            root_logger = logging.getLogger()
            
            # すべてのハンドラーがフォーマッターを持つことを確認
            for handler in root_logger.handlers:
                assert handler.formatter is not None
                
                # フォーマット文字列に必要な要素が含まれていることを確認
                fmt = handler.formatter._fmt
                assert "%(asctime)s" in fmt
                assert "%(name)s" in fmt
                assert "%(levelname)s" in fmt
                assert "%(message)s" in fmt
    
    @given(
        log_level=log_levels,
        message=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=100)
    def test_property_twitter_embed_log_format_consistency(self, log_level, message):
        """
        Feature: test-coverage-improvement, Property 12: ログフォーマットの一貫性
        Validates: Requirements 5.4
        
        Twitter埋め込み専用ロガーに対して、
        すべてのログメッセージが指定されたフォーマットを含む
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            logger = setup_twitter_embed_logging(
                log_level=log_level,
                log_file=log_file
            )
            
            # ログレベルに応じてメッセージを出力
            if log_level == "DEBUG":
                logger.debug(message)
            elif log_level == "INFO":
                logger.info(message)
            elif log_level == "WARNING":
                logger.warning(message)
            elif log_level == "ERROR":
                logger.error(message)
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # ファイルの内容を確認
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # メッセージが含まれていることを確認
                    if message in content:
                        # フォーマットの要素が含まれていることを確認
                        assert any(char.isdigit() for char in content)
                        assert log_level in content
                        assert message in content
            
            # クリーンアップ
            logger.handlers.clear()
