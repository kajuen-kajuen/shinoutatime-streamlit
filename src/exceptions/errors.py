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


class DataSaveError(ShinoutaTimeError):
    """データ保存エラー
    
    ファイルへのデータ保存時に発生するエラーです。
    """
    
    def __init__(self, file_path: str, message: str):
        """
        Args:
            file_path: エラーが発生したファイルのパス
            message: エラーメッセージ
        """
        self.file_path = file_path
        self.message = message
        super().__init__(f"データ保存エラー ({file_path}): {message}")


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


# Twitter埋め込み機能用の例外クラス

class TwitterEmbedError(ShinoutaTimeError):
    """Twitter埋め込み機能の基底例外クラス
    
    Twitter埋め込みコード取得機能に関連する全ての例外の基底クラスです。
    """
    pass


class InvalidURLError(TwitterEmbedError):
    """無効なURL形式エラー
    
    ツイートURLの形式が無効な場合に発生するエラーです。
    """
    
    def __init__(self, url: str, message: str = "無効なツイートURL形式です"):
        """
        Args:
            url: 無効なURL
            message: エラーメッセージ
        """
        self.url = url
        self.message = message
        super().__init__(f"{message}: {url}")


class NetworkError(TwitterEmbedError):
    """ネットワーク接続エラー
    
    Twitter APIへの接続時にネットワークエラーが発生した場合のエラーです。
    """
    
    def __init__(self, message: str = "ネットワーク接続エラーが発生しました", original_error: Optional[Exception] = None):
        """
        Args:
            message: エラーメッセージ
            original_error: 元の例外オブジェクト（オプション）
        """
        self.message = message
        self.original_error = original_error
        error_detail = f" ({str(original_error)})" if original_error else ""
        super().__init__(f"{message}{error_detail}")


class APITimeoutError(TwitterEmbedError):
    """APIタイムアウトエラー
    
    Twitter APIへのリクエストがタイムアウトした場合のエラーです。
    """
    
    def __init__(self, timeout_seconds: float, message: str = "APIリクエストがタイムアウトしました"):
        """
        Args:
            timeout_seconds: タイムアウト時間（秒）
            message: エラーメッセージ
        """
        self.timeout_seconds = timeout_seconds
        self.message = message
        super().__init__(f"{message} (タイムアウト: {timeout_seconds}秒)")


class RateLimitError(TwitterEmbedError):
    """レート制限エラー
    
    Twitter APIのレート制限に達した場合のエラーです。
    """
    
    def __init__(self, reset_time: Optional[str] = None, message: str = "APIレート制限に達しました"):
        """
        Args:
            reset_time: レート制限がリセットされる時刻（オプション）
            message: エラーメッセージ
        """
        self.reset_time = reset_time
        self.message = message
        reset_info = f" (リセット時刻: {reset_time})" if reset_time else ""
        super().__init__(f"{message}{reset_info}")


class FileWriteError(TwitterEmbedError):
    """ファイル書き込みエラー
    
    埋め込みコードファイルへの書き込み時に発生するエラーです。
    """
    
    def __init__(self, file_path: str, message: str = "ファイルへの書き込みに失敗しました", original_error: Optional[Exception] = None):
        """
        Args:
            file_path: エラーが発生したファイルのパス
            message: エラーメッセージ
            original_error: 元の例外オブジェクト（オプション）
        """
        self.file_path = file_path
        self.message = message
        self.original_error = original_error
        error_detail = f" ({str(original_error)})" if original_error else ""
        super().__init__(f"{message}: {file_path}{error_detail}")


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
