"""
リトライロジックモジュール

ネットワークエラーやAPI呼び出し失敗時のリトライ機能を提供します。
"""

import time
import logging
from functools import wraps
from typing import Callable, Optional, Tuple, Type, Union


logger = logging.getLogger(__name__)


class RetryStrategy:
    """
    リトライ戦略クラス
    
    指数バックオフアルゴリズムを使用してリトライ遅延時間を計算します。
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        """
        リトライ戦略を初期化
        
        Args:
            max_retries: 最大リトライ回数
            base_delay: 基本遅延時間（秒）
            max_delay: 最大遅延時間（秒）
            exponential_base: 指数バックオフの基数
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def calculate_delay(self, attempt: int) -> float:
        """
        リトライ遅延時間を計算（指数バックオフ）
        
        Args:
            attempt: 試行回数（0から開始）
            
        Returns:
            遅延時間（秒）
        """
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    logger_instance: Optional[logging.Logger] = None
) -> Callable:
    """
    リトライデコレーター
    
    指定された例外が発生した場合に、関数の実行を自動的にリトライします。
    指数バックオフアルゴリズムを使用して遅延時間を計算します。
    
    Args:
        max_retries: 最大リトライ回数
        base_delay: 基本遅延時間（秒）
        max_delay: 最大遅延時間（秒）
        exponential_base: 指数バックオフの基数
        exceptions: リトライ対象の例外クラス（単一またはタプル）
        logger_instance: ロガーインスタンス（Noneの場合はモジュールロガーを使用）
    
    Returns:
        デコレートされた関数
    
    Example:
        @retry(max_retries=3, base_delay=1.0, exceptions=(NetworkError, APITimeoutError))
        def fetch_data():
            # ネットワークリクエストなど
            pass
    """
    strategy = RetryStrategy(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base
    )
    
    log = logger_instance or logger
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = strategy.calculate_delay(attempt)
                        log.warning(
                            f"関数 {func.__name__} の実行に失敗しました "
                            f"(試行 {attempt + 1}/{max_retries + 1}): {str(e)}. "
                            f"{delay}秒後にリトライします..."
                        )
                        time.sleep(delay)
                    else:
                        log.error(
                            f"関数 {func.__name__} の実行に失敗しました "
                            f"(最大リトライ回数 {max_retries + 1} に到達): {str(e)}"
                        )
            
            # 最大リトライ回数に到達した場合、最後の例外を再送出
            raise last_exception
        
        return wrapper
    
    return decorator
