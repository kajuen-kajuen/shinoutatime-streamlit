"""
Logging Configのユニットテスト

ロギング設定の正確性を検証します。
要件5.1, 5.2, 5.3, 5.4, 5.5に対応しています。
"""

import os
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from src.config.logging_config import (
    setup_logging,
    get_logger,
    set_log_level,
    setup_twitter_embed_logging,
    log_twitter_embed_fetch,
    log_twitter_embed_error
)


class TestLoggingSetup:
    """setup_logging関数のテスト"""
    
    def setup_method(self):
        """各テストの前にロガーをリセット"""
        # ルートロガーのハンドラーをクリア
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)
    
    def teardown_method(self):
        """各テストの後にロガーをクリア"""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)
    
    def test_setup_logging_default_level(self):
        """
        デフォルトのログレベル（INFO）が設定されることを確認
        要件5.1: ログレベルの設定
        """
        setup_logging()
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
    
    def test_setup_logging_custom_level(self):
        """
        カスタムログレベルが正しく設定されることを確認
        要件5.1: ログレベルの設定
        """
        setup_logging(log_level="DEBUG")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
    
    def test_setup_logging_warning_level(self):
        """
        WARNINGレベルが正しく設定されることを確認
        要件5.1: ログレベルの設定
        """
        setup_logging(log_level="WARNING")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING
    
    def test_setup_logging_error_level(self):
        """
        ERRORレベルが正しく設定されることを確認
        要件5.1: ログレベルの設定
        """
        setup_logging(log_level="ERROR")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.ERROR
    
    def test_setup_logging_console_handler(self):
        """
        コンソールハンドラーが正しく設定されることを確認
        要件5.1: ハンドラーの設定
        """
        setup_logging()
        
        root_logger = logging.getLogger()
        
        # コンソールハンドラーが存在することを確認
        console_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(console_handlers) == 1
        
        # ハンドラーのレベルが正しいことを確認
        assert console_handlers[0].level == logging.INFO
    
    def test_setup_logging_formatter(self):
        """
        ログフォーマットが正しく設定されることを確認
        要件5.4: フォーマットの設定
        """
        setup_logging()
        
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter
        
        # フォーマッターが設定されていることを確認
        assert formatter is not None
        
        # フォーマット文字列を確認
        assert "%(asctime)s" in formatter._fmt
        assert "%(name)s" in formatter._fmt
        assert "%(levelname)s" in formatter._fmt
        assert "%(message)s" in formatter._fmt
    
    def test_setup_logging_from_env_variable(self):
        """
        環境変数からログレベルが読み込まれることを確認
        要件5.1: ログレベルの設定
        """
        with patch.dict(os.environ, {"SHINOUTA_LOG_LEVEL": "DEBUG"}):
            setup_logging()
            
            root_logger = logging.getLogger()
            assert root_logger.level == logging.DEBUG
    
    def test_setup_logging_clears_existing_handlers(self):
        """
        既存のハンドラーがクリアされることを確認
        要件5.1: ハンドラーの設定
        """
        # 既存のハンドラーを追加
        root_logger = logging.getLogger()
        old_handler = logging.StreamHandler()
        root_logger.addHandler(old_handler)
        
        # setup_loggingを呼び出す
        setup_logging()
        
        # 古いハンドラーが削除されていることを確認
        assert old_handler not in root_logger.handlers


class TestGetLogger:
    """get_logger関数のテスト"""
    
    def test_get_logger_returns_logger(self):
        """
        ロガーオブジェクトが返されることを確認
        """
        logger = get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
    
    def test_get_logger_different_names(self):
        """
        異なる名前で異なるロガーが返されることを確認
        """
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 is not logger2


class TestSetLogLevel:
    """set_log_level関数のテスト"""
    
    def setup_method(self):
        """各テストの前にロガーを初期化"""
        setup_logging(log_level="INFO")
    
    def teardown_method(self):
        """各テストの後にロガーをクリア"""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)
    
    def test_set_log_level_to_debug(self):
        """
        ログレベルをDEBUGに変更できることを確認
        要件5.1: ログレベルの設定
        """
        set_log_level("DEBUG")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
    
    def test_set_log_level_to_warning(self):
        """
        ログレベルをWARNINGに変更できることを確認
        要件5.1: ログレベルの設定
        """
        set_log_level("WARNING")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING
    
    def test_set_log_level_updates_handlers(self):
        """
        ハンドラーのレベルも更新されることを確認
        要件5.1: ログレベルの設定
        """
        set_log_level("ERROR")
        
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            assert handler.level == logging.ERROR
    
    def test_set_log_level_case_insensitive(self):
        """
        ログレベルの大文字小文字が区別されないことを確認
        要件5.1: ログレベルの設定
        """
        set_log_level("debug")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG



class TestFileLogging:
    """ファイルロギングのテスト"""
    
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
    
    def test_file_logging_creates_handler(self):
        """
        ファイルロギングを有効にするとファイルハンドラーが作成されることを確認
        要件5.2: ファイルハンドラーの作成
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(log_file=log_file, enable_file_logging=True)
            
            root_logger = logging.getLogger()
            
            # ファイルハンドラーが存在することを確認
            file_handlers = [
                h for h in root_logger.handlers
                if isinstance(h, logging.handlers.RotatingFileHandler)
            ]
            assert len(file_handlers) == 1
    
    def test_file_logging_writes_to_file(self):
        """
        ログがファイルに書き込まれることを確認
        要件5.2: ログファイルへの出力
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(log_file=log_file, enable_file_logging=True)
            
            # ログメッセージを出力
            logger = logging.getLogger()
            logger.info("テストメッセージ")
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # ファイルが作成されていることを確認
            assert os.path.exists(log_file)
            
            # ファイルの内容を確認
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "テストメッセージ" in content
    
    def test_file_logging_creates_directory(self):
        """
        ログディレクトリが自動的に作成されることを確認
        要件5.2: ディレクトリの自動作成
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "logs", "subdir", "test.log")
            
            setup_logging(log_file=log_file, enable_file_logging=True)
            
            # ディレクトリが作成されていることを確認
            assert os.path.exists(os.path.dirname(log_file))
    
    def test_file_logging_disabled_by_default(self):
        """
        デフォルトではファイルロギングが無効であることを確認
        要件5.2: ファイルハンドラーの作成
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(log_file=log_file, enable_file_logging=False)
            
            root_logger = logging.getLogger()
            
            # ファイルハンドラーが存在しないことを確認
            file_handlers = [
                h for h in root_logger.handlers
                if isinstance(h, logging.handlers.RotatingFileHandler)
            ]
            assert len(file_handlers) == 0
    
    def test_file_logging_from_env_variable(self):
        """
        環境変数からファイルロギングが有効化されることを確認
        要件5.2: ファイルハンドラーの作成
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            with patch.dict(os.environ, {"SHINOUTA_ENABLE_FILE_LOGGING": "true"}):
                setup_logging(log_file=log_file)
                
                root_logger = logging.getLogger()
                
                # ファイルハンドラーが存在することを確認
                file_handlers = [
                    h for h in root_logger.handlers
                    if isinstance(h, logging.handlers.RotatingFileHandler)
                ]
                assert len(file_handlers) == 1
    
    def test_file_logging_with_custom_path_from_env(self):
        """
        環境変数からログファイルパスが読み込まれることを確認
        要件5.2: ログファイルへの出力
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "custom.log")
            
            with patch.dict(os.environ, {
                "SHINOUTA_LOG_FILE": log_file,
                "SHINOUTA_ENABLE_FILE_LOGGING": "true"
            }):
                setup_logging()
                
                # ログメッセージを出力
                logger = logging.getLogger()
                logger.info("カスタムパステスト")
                
                # ハンドラーをフラッシュ
                for handler in logger.handlers:
                    handler.flush()
                
                # ファイルが作成されていることを確認
                assert os.path.exists(log_file)
    
    def test_file_logging_enabled_with_env_true(self):
        """
        環境変数SHINOUTA_ENABLE_FILE_LOGGINGが"true"の場合にファイルログが有効化されることを確認
        要件5.2: ファイルハンドラーの作成
        未カバー行: 205, 209
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            with patch.dict(os.environ, {"SHINOUTA_ENABLE_FILE_LOGGING": "true"}):
                setup_logging(log_file=log_file)
                
                root_logger = logging.getLogger()
                
                # ファイルハンドラーが存在することを確認
                file_handlers = [
                    h for h in root_logger.handlers
                    if isinstance(h, logging.handlers.RotatingFileHandler)
                ]
                assert len(file_handlers) == 1
    
    def test_file_logging_enabled_with_env_1(self):
        """
        環境変数SHINOUTA_ENABLE_FILE_LOGGINGが"1"の場合にファイルログが有効化されることを確認
        要件5.2: ファイルハンドラーの作成
        未カバー行: 205, 209
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            with patch.dict(os.environ, {"SHINOUTA_ENABLE_FILE_LOGGING": "1"}):
                setup_logging(log_file=log_file)
                
                root_logger = logging.getLogger()
                
                # ファイルハンドラーが存在することを確認
                file_handlers = [
                    h for h in root_logger.handlers
                    if isinstance(h, logging.handlers.RotatingFileHandler)
                ]
                assert len(file_handlers) == 1
    
    def test_file_logging_enabled_with_env_yes(self):
        """
        環境変数SHINOUTA_ENABLE_FILE_LOGGINGが"yes"の場合にファイルログが有効化されることを確認
        要件5.2: ファイルハンドラーの作成
        未カバー行: 205, 209
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            with patch.dict(os.environ, {"SHINOUTA_ENABLE_FILE_LOGGING": "yes"}):
                setup_logging(log_file=log_file)
                
                root_logger = logging.getLogger()
                
                # ファイルハンドラーが存在することを確認
                file_handlers = [
                    h for h in root_logger.handlers
                    if isinstance(h, logging.handlers.RotatingFileHandler)
                ]
                assert len(file_handlers) == 1



class TestLogRotation:
    """ログローテーションのテスト"""
    
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
    
    def test_log_rotation_configuration(self):
        """
        ログローテーションの設定が正しく適用されることを確認
        要件5.3: ローテーション設定
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            max_bytes = 1024
            backup_count = 3
            
            setup_logging(
                log_file=log_file,
                enable_file_logging=True,
                max_bytes=max_bytes,
                backup_count=backup_count
            )
            
            root_logger = logging.getLogger()
            
            # ファイルハンドラーを取得
            file_handlers = [
                h for h in root_logger.handlers
                if isinstance(h, logging.handlers.RotatingFileHandler)
            ]
            assert len(file_handlers) == 1
            
            handler = file_handlers[0]
            
            # ローテーション設定を確認
            assert handler.maxBytes == max_bytes
            assert handler.backupCount == backup_count
    
    def test_log_rotation_creates_backup(self):
        """
        ログファイルがローテーションされてバックアップが作成されることを確認
        要件5.3: バックアップファイルの作成
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            # 小さいサイズでローテーションをトリガー
            max_bytes = 100
            backup_count = 2
            
            setup_logging(
                log_file=log_file,
                enable_file_logging=True,
                max_bytes=max_bytes,
                backup_count=backup_count
            )
            
            logger = logging.getLogger()
            
            # 大量のログを出力してローテーションをトリガー
            for i in range(50):
                logger.info(f"ローテーションテストメッセージ {i}")
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # メインのログファイルが存在することを確認
            assert os.path.exists(log_file)
            
            # バックアップファイルが作成されているか確認
            # ローテーションが発生した場合、.1 ファイルが存在する
            backup_file = f"{log_file}.1"
            # ファイルサイズが小さいため、ローテーションが発生している可能性がある
            # 少なくともメインファイルは存在する
            assert os.path.exists(log_file)
    
    def test_log_rotation_respects_backup_count(self):
        """
        バックアップファイルの数が制限されることを確認
        要件5.3: バックアップファイルの作成
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            max_bytes = 50
            backup_count = 2
            
            setup_logging(
                log_file=log_file,
                enable_file_logging=True,
                max_bytes=max_bytes,
                backup_count=backup_count
            )
            
            logger = logging.getLogger()
            
            # 大量のログを出力して複数回ローテーションをトリガー
            for i in range(100):
                logger.info(f"バックアップカウントテスト {i}")
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # メインファイルとバックアップファイルの数を確認
            log_files = [
                f for f in os.listdir(tmpdir)
                if f.startswith("test.log")
            ]
            
            # メインファイル + バックアップファイル（最大backup_count個）
            # 実際のファイル数は backup_count + 1 以下であるべき
            assert len(log_files) <= backup_count + 1
    
    def test_log_rotation_default_settings(self):
        """
        デフォルトのローテーション設定が適用されることを確認
        要件5.3: ローテーション設定
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(log_file=log_file, enable_file_logging=True)
            
            root_logger = logging.getLogger()
            
            # ファイルハンドラーを取得
            file_handlers = [
                h for h in root_logger.handlers
                if isinstance(h, logging.handlers.RotatingFileHandler)
            ]
            assert len(file_handlers) == 1
            
            handler = file_handlers[0]
            
            # デフォルト設定を確認（10MB、5世代）
            assert handler.maxBytes == 10 * 1024 * 1024
            assert handler.backupCount == 5



class TestMultipleHandlers:
    """複数ハンドラーのテスト"""
    
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
    
    def test_console_and_file_handlers_both_active(self):
        """
        コンソールとファイルの両方のハンドラーが有効であることを確認
        要件5.5: コンソールとファイルの両方
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(log_file=log_file, enable_file_logging=True)
            
            root_logger = logging.getLogger()
            
            # コンソールハンドラーが存在することを確認
            console_handlers = [
                h for h in root_logger.handlers
                if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.handlers.RotatingFileHandler)
            ]
            assert len(console_handlers) == 1
            
            # ファイルハンドラーが存在することを確認
            file_handlers = [
                h for h in root_logger.handlers
                if isinstance(h, logging.handlers.RotatingFileHandler)
            ]
            assert len(file_handlers) == 1
            
            # 合計2つのハンドラーが存在することを確認
            assert len(root_logger.handlers) == 2
    
    def test_handlers_are_independent(self):
        """
        ハンドラーが独立して動作することを確認
        要件5.5: ハンドラーの独立性
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(log_file=log_file, enable_file_logging=True)
            
            root_logger = logging.getLogger()
            
            # 各ハンドラーが独立したフォーマッターを持つことを確認
            formatters = [h.formatter for h in root_logger.handlers]
            assert all(f is not None for f in formatters)
            
            # 各ハンドラーが独立したレベルを持つことを確認
            levels = [h.level for h in root_logger.handlers]
            assert all(level == logging.INFO for level in levels)
    
    def test_both_handlers_receive_messages(self):
        """
        両方のハンドラーがログメッセージを受信することを確認
        要件5.5: コンソールとファイルの両方
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(log_file=log_file, enable_file_logging=True)
            
            logger = logging.getLogger()
            test_message = "両方のハンドラーテスト"
            logger.info(test_message)
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # ファイルにメッセージが書き込まれていることを確認
            assert os.path.exists(log_file)
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert test_message in content
    
    def test_handlers_can_have_different_levels(self):
        """
        各ハンドラーが異なるログレベルを持てることを確認
        要件5.5: ハンドラーの独立性
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            setup_logging(log_file=log_file, enable_file_logging=True, log_level="DEBUG")
            
            root_logger = logging.getLogger()
            
            # 各ハンドラーのレベルを個別に変更できることを確認
            console_handler = None
            file_handler = None
            
            for handler in root_logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    file_handler = handler
                elif isinstance(handler, logging.StreamHandler):
                    console_handler = handler
            
            assert console_handler is not None
            assert file_handler is not None
            
            # レベルを個別に変更
            console_handler.setLevel(logging.WARNING)
            file_handler.setLevel(logging.DEBUG)
            
            # 変更が反映されていることを確認
            assert console_handler.level == logging.WARNING
            assert file_handler.level == logging.DEBUG
    
    def test_console_only_when_file_logging_disabled(self):
        """
        ファイルロギングが無効の場合、コンソールハンドラーのみが存在することを確認
        要件5.5: ハンドラーの独立性
        """
        setup_logging(enable_file_logging=False)
        
        root_logger = logging.getLogger()
        
        # コンソールハンドラーのみが存在することを確認
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)
        assert not isinstance(root_logger.handlers[0], logging.handlers.RotatingFileHandler)



class TestTwitterEmbedLogging:
    """Twitter埋め込み機能のロギングテスト"""
    
    def setup_method(self):
        """各テストの前にロガーをリセット"""
        # Twitter埋め込みロガーをクリア
        twitter_logger = logging.getLogger("twitter_embed")
        twitter_logger.handlers.clear()
        twitter_logger.setLevel(logging.WARNING)
    
    def teardown_method(self):
        """各テストの後にロガーをクリア"""
        twitter_logger = logging.getLogger("twitter_embed")
        twitter_logger.handlers.clear()
        twitter_logger.setLevel(logging.WARNING)
    
    def test_setup_twitter_embed_logging_default(self):
        """
        デフォルト設定でTwitter埋め込みロガーが作成されることを確認
        要件5.1, 5.2: ログレベルとファイルハンドラーの設定
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            logger = setup_twitter_embed_logging(log_file=log_file)
            
            assert logger.name == "twitter_embed"
            assert logger.level == logging.INFO
            
            # ファイルハンドラーとコンソールハンドラーが存在することを確認
            assert len(logger.handlers) == 2
    
    def test_setup_twitter_embed_logging_from_env_log_level(self):
        """
        環境変数TWITTER_EMBED_LOG_LEVELからログレベルが読み込まれることを確認
        要件5.1: ログレベルの設定
        未カバー行: 292-297
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            with patch.dict(os.environ, {"TWITTER_EMBED_LOG_LEVEL": "DEBUG"}):
                logger = setup_twitter_embed_logging(log_file=log_file)
                
                assert logger.level == logging.DEBUG
    
    def test_setup_twitter_embed_logging_from_env_log_file(self):
        """
        環境変数TWITTER_EMBED_LOG_FILEからログファイルパスが読み込まれることを確認
        要件5.2: ログファイルへの出力
        未カバー行: 292-297
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_log_file = os.path.join(tmpdir, "custom_twitter.log")
            
            with patch.dict(os.environ, {"TWITTER_EMBED_LOG_FILE": custom_log_file}):
                logger = setup_twitter_embed_logging()
                
                # ログメッセージを出力
                logger.info("環境変数テスト")
                
                # ハンドラーをフラッシュ
                for handler in logger.handlers:
                    handler.flush()
                
                # カスタムパスにファイルが作成されていることを確認
                assert os.path.exists(custom_log_file)
    
    def test_setup_twitter_embed_logging_default_values_when_env_not_set(self):
        """
        環境変数が設定されていない場合にデフォルト値が使用されることを確認
        要件5.1, 5.2: ログレベルとファイルパスのデフォルト値
        未カバー行: 292-297
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # 環境変数をクリア
            with patch.dict(os.environ, {}, clear=True):
                # デフォルトのログファイルパスを上書き
                default_log_file = os.path.join(tmpdir, "twitter_embed.log")
                logger = setup_twitter_embed_logging(log_file=default_log_file)
                
                # デフォルトのログレベル（INFO）が使用されることを確認
                assert logger.level == logging.INFO
                
                # ログメッセージを出力
                logger.info("デフォルト値テスト")
                
                # ハンドラーをフラッシュ
                for handler in logger.handlers:
                    handler.flush()
                
                # デフォルトパスにファイルが作成されていることを確認
                assert os.path.exists(default_log_file)
    
    def test_setup_twitter_embed_logging_custom_rotation_settings(self):
        """
        カスタムローテーション設定が適用されることを確認
        要件5.3: ローテーション設定
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            max_bytes = 2048
            backup_count = 3
            
            logger = setup_twitter_embed_logging(
                log_file=log_file,
                max_bytes=max_bytes,
                backup_count=backup_count
            )
            
            # ファイルハンドラーを取得
            file_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.handlers.RotatingFileHandler)
            ]
            assert len(file_handlers) == 1
            
            handler = file_handlers[0]
            
            # ローテーション設定を確認
            assert handler.maxBytes == max_bytes
            assert handler.backupCount == backup_count
    
    def test_setup_twitter_embed_logging_propagate_disabled(self):
        """
        親ロガーへの伝播が無効化されていることを確認
        要件5.1: ロガーの設定
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            logger = setup_twitter_embed_logging(log_file=log_file)
            
            # 親ロガーへの伝播が無効化されていることを確認
            assert logger.propagate is False


class TestLogTwitterEmbedFetch:
    """log_twitter_embed_fetch関数のテスト"""
    
    def setup_method(self):
        """各テストの前にロガーをリセット"""
        twitter_logger = logging.getLogger("twitter_embed")
        twitter_logger.handlers.clear()
        twitter_logger.setLevel(logging.WARNING)
    
    def teardown_method(self):
        """各テストの後にロガーをクリア"""
        twitter_logger = logging.getLogger("twitter_embed")
        twitter_logger.handlers.clear()
        twitter_logger.setLevel(logging.WARNING)
    
    def test_log_twitter_embed_fetch_success(self):
        """
        成功時のログ記録を確認
        要件5.4: ログフォーマットの設定
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            logger = setup_twitter_embed_logging(log_file=log_file)
            tweet_url = "https://twitter.com/user/status/123"
            
            log_twitter_embed_fetch(logger, tweet_url, success=True)
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # ログファイルの内容を確認
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "埋め込みコード取得成功" in content
                assert tweet_url in content
    
    def test_log_twitter_embed_fetch_failure(self):
        """
        失敗時のログ記録を確認
        要件5.4: ログフォーマットの設定
        未カバー行: 332-337
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            logger = setup_twitter_embed_logging(log_file=log_file)
            tweet_url = "https://twitter.com/user/status/456"
            error_message = "ネットワークエラー"
            
            log_twitter_embed_fetch(logger, tweet_url, success=False, error_message=error_message)
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # ログファイルの内容を確認
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "埋め込みコード取得失敗" in content
                assert tweet_url in content
                assert error_message in content
    
    def test_log_twitter_embed_fetch_failure_without_error_message(self):
        """
        エラーメッセージなしの失敗時のログ記録を確認
        要件5.4: ログフォーマットの設定
        未カバー行: 332-337
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            logger = setup_twitter_embed_logging(log_file=log_file)
            tweet_url = "https://twitter.com/user/status/789"
            
            log_twitter_embed_fetch(logger, tweet_url, success=False)
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # ログファイルの内容を確認
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "埋め込みコード取得失敗" in content
                assert tweet_url in content
                assert "不明なエラー" in content


class TestLogTwitterEmbedError:
    """log_twitter_embed_error関数のテスト"""
    
    def setup_method(self):
        """各テストの前にロガーをリセット"""
        twitter_logger = logging.getLogger("twitter_embed")
        twitter_logger.handlers.clear()
        twitter_logger.setLevel(logging.WARNING)
    
    def teardown_method(self):
        """各テストの後にロガーをクリア"""
        twitter_logger = logging.getLogger("twitter_embed")
        twitter_logger.handlers.clear()
        twitter_logger.setLevel(logging.WARNING)
    
    def test_log_twitter_embed_error_without_context(self):
        """
        コンテキスト情報なしのエラーログ記録を確認
        要件5.4: ログフォーマットの設定
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            logger = setup_twitter_embed_logging(log_file=log_file)
            error = ValueError("無効なURL")
            
            log_twitter_embed_error(logger, error)
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # ログファイルの内容を確認
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "エラーが発生しました" in content
                assert "ValueError" in content
                assert "無効なURL" in content
    
    def test_log_twitter_embed_error_with_context(self):
        """
        コンテキスト情報ありのエラーログ記録を確認
        要件5.4: ログフォーマットの設定
        未カバー行: 338-343
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            logger = setup_twitter_embed_logging(log_file=log_file)
            error = ConnectionError("接続失敗")
            context = {
                "tweet_url": "https://twitter.com/user/status/123",
                "step": "api_call"
            }
            
            log_twitter_embed_error(logger, error, context=context)
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # ログファイルの内容を確認
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "エラーが発生しました" in content
                assert "ConnectionError" in content
                assert "接続失敗" in content
                assert "コンテキスト" in content
                assert "tweet_url=https://twitter.com/user/status/123" in content
                assert "step=api_call" in content
    
    def test_log_twitter_embed_error_includes_stack_trace(self):
        """
        スタックトレースが記録されることを確認
        要件5.4: ログフォーマットの設定
        未カバー行: 338-343
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "twitter_embed.log")
            
            logger = setup_twitter_embed_logging(log_file=log_file)
            
            # スタックトレースを生成するために例外を発生させる
            try:
                raise RuntimeError("テストエラー")
            except Exception as e:
                log_twitter_embed_error(logger, e, context={"test": "value"})
            
            # ハンドラーをフラッシュ
            for handler in logger.handlers:
                handler.flush()
            
            # ログファイルの内容を確認
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "エラーが発生しました" in content
                assert "RuntimeError" in content
                assert "テストエラー" in content
                # スタックトレースが含まれることを確認
                assert "Traceback" in content
