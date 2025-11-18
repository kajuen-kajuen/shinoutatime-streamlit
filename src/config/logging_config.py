"""
ロギング設定モジュール

アプリケーション全体のロギング設定を一元管理します。
ログレベル、フォーマット、ローテーション設定を提供します。
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_file_logging: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    アプリケーション全体のロギングを設定する
    
    ログレベル、フォーマット、ローテーション設定を行います。
    環境変数からの設定読み込みにも対応しています。
    
    Args:
        log_level: ログレベル（DEBUG、INFO、WARNING、ERROR）
                  Noneの場合は環境変数SHINOUTA_LOG_LEVELから読み込む
                  環境変数も未設定の場合はINFOを使用
        log_file: ログファイルのパス
                 Noneの場合は環境変数SHINOUTA_LOG_FILEから読み込む
                 環境変数も未設定の場合は'logs/shinouta.log'を使用
        enable_file_logging: ファイルへのログ出力を有効にするか
                            環境変数SHINOUTA_ENABLE_FILE_LOGGINGでも制御可能
        max_bytes: ログファイルの最大サイズ（バイト）
                  この サイズを超えるとローテーションが発生
        backup_count: 保持するバックアップファイルの数
    
    Examples:
        >>> # デフォルト設定でロギングを初期化
        >>> setup_logging()
        
        >>> # DEBUGレベルでファイルログを有効化
        >>> setup_logging(log_level="DEBUG", enable_file_logging=True)
        
        >>> # 本番環境用の設定（環境変数から読み込み）
        >>> # SHINOUTA_LOG_LEVEL=INFO
        >>> # SHINOUTA_ENABLE_FILE_LOGGING=true
        >>> setup_logging()
    
    Notes:
        - 本番環境ではINFOレベル以上のログのみを出力することを推奨
        - ログファイルはサイズベースでローテーションされます
        - ログディレクトリが存在しない場合は自動的に作成されます
    """
    # 環境変数からログレベルを取得
    if log_level is None:
        log_level = os.getenv("SHINOUTA_LOG_LEVEL", "INFO").upper()
    
    # 環境変数からファイルログ有効化フラグを取得
    env_file_logging = os.getenv("SHINOUTA_ENABLE_FILE_LOGGING", "false").lower()
    if env_file_logging in ("true", "1", "yes"):
        enable_file_logging = True
    
    # 環境変数からログファイルパスを取得
    if log_file is None:
        log_file = os.getenv("SHINOUTA_LOG_FILE", "logs/shinouta.log")
    
    # ログレベルの変換
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 既存のハンドラーをクリア
    root_logger.handlers.clear()
    
    # ログフォーマットの設定
    # 本番環境用: タイムスタンプ、ログレベル、モジュール名、メッセージ
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # ファイルハンドラーの設定（有効な場合）
    if enable_file_logging:
        # ログディレクトリの作成
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ローテーティングファイルハンドラーの設定
        # ファイルサイズが max_bytes を超えると自動的にローテーション
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        root_logger.info(
            f"ファイルログを有効化しました: {log_file} "
            f"(最大サイズ: {max_bytes / 1024 / 1024:.1f}MB, "
            f"バックアップ数: {backup_count})"
        )
    
    root_logger.info(f"ロギングを初期化しました: レベル={log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    指定された名前のロガーを取得する
    
    モジュールごとにロガーを取得する際に使用します。
    
    Args:
        name: ロガー名（通常は__name__を指定）
    
    Returns:
        logging.Logger: ロガーオブジェクト
    
    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("情報メッセージ")
        >>> logger.error("エラーメッセージ")
    """
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """
    実行時にログレベルを変更する
    
    Args:
        level: ログレベル（DEBUG、INFO、WARNING、ERROR）
    
    Examples:
        >>> set_log_level("DEBUG")
        >>> set_log_level("INFO")
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 全てのハンドラーのレベルも更新
    for handler in root_logger.handlers:
        handler.setLevel(numeric_level)
    
    root_logger.info(f"ログレベルを変更しました: {level}")
