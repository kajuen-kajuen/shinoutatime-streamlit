"""
カスタム例外モジュール

アプリケーション固有の例外クラスを定義します。
"""

import logging
from typing import Any, Dict, Optional


class ShinoutaTimeError(Exception):
    """基底例外クラス
    
    しのうたタイムアプリケーションの全ての例外の基底クラスです。
    """
    pass


class DataLoadError(ShinoutaTimeError):
    """データ読み込みエラー
    
    TSVファイルなどのデータ読み込み時に発生するエラーです。
    """
    
    def __init__(self, file_path: str, message: str):
        """
        Args:
            file_path: エラーが発生したファイルのパス
            message: エラーメッセージ
        """
        self.file_path = file_path
        self.message = message
        super().__init__(f"データ読み込みエラー ({file_path}): {message}")


class DataProcessingError(ShinoutaTimeError):
    """データ処理エラー
    
    データの変換や処理時に発生するエラーです。
    """
    
    def __init__(self, step: str, message: str):
        """
        Args:
            step: エラーが発生した処理ステップ
            message: エラーメッセージ
        """
        self.step = step
        self.message = message
        super().__init__(f"データ処理エラー ({step}): {message}")


class ConfigurationError(ShinoutaTimeError):
    """設定エラー
    
    アプリケーション設定に関するエラーです。
    """
    
    def __init__(self, setting: str, message: str):
        """
        Args:
            setting: エラーが発生した設定項目
            message: エラーメッセージ
        """
        self.setting = setting
        self.message = message
        super().__init__(f"設定エラー ({setting}): {message}")


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """エラーをログに記録する
    
    例外オブジェクトと追加のコンテキスト情報をログに記録します。
    
    Args:
        error: 例外オブジェクト
        context: 追加のコンテキスト情報（オプション）
    """
    logger = logging.getLogger(__name__)
    
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error)
    }
    
    if context:
        error_info.update(context)
    
    logger.error(
        f"エラーが発生しました: {error_info['error_type']} - {error_info['error_message']}",
        extra=error_info,
        exc_info=True
    )
