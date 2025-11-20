"""
Retry Utilityのユニットテスト

リトライ機能の基本動作、指数バックオフ、例外フィルタリングをテストします。
"""

import pytest
import time
from unittest.mock import Mock, patch
from src.utils.retry import retry, RetryStrategy


class TestRetryStrategy:
    """RetryStrategyクラスのテスト"""
    
    def test_calculate_delay_first_attempt(self):
        """最初の試行での遅延時間計算をテスト"""
        strategy = RetryStrategy(base_delay=1.0, exponential_base=2.0)
        delay = strategy.calculate_delay(0)
        assert delay == 1.0
    
    def test_calculate_delay_exponential_growth(self):
        """指数的な遅延時間の増加をテスト"""
        strategy = RetryStrategy(base_delay=1.0, exponential_base=2.0)
        assert strategy.calculate_delay(0) == 1.0
        assert strategy.calculate_delay(1) == 2.0
        assert strategy.calculate_delay(2) == 4.0
        assert strategy.calculate_delay(3) == 8.0
    
    def test_calculate_delay_max_limit(self):
        """最大遅延時間の制限をテスト"""
        strategy = RetryStrategy(base_delay=1.0, max_delay=5.0, exponential_base=2.0)
        # 4回目の試行では8秒になるはずだが、max_delayで5秒に制限される
        delay = strategy.calculate_delay(3)
        assert delay == 5.0


class TestRetryDecorator:
    """retryデコレーターのテスト"""
    
    def test_successful_execution_no_retry(self):
        """成功した実行ではリトライしないことをテスト（要件6.2）"""
        mock_func = Mock(return_value="success")
        decorated = retry(max_retries=3)(mock_func)
        
        result = decorated()
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_on_failure_then_success(self):
        """失敗後にリトライして成功することをテスト（要件6.2）"""
        mock_func = Mock(side_effect=[Exception("error1"), Exception("error2"), "success"])
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):  # sleepをモックして高速化
            decorated = retry(max_retries=3, base_delay=0.1)(mock_func)
            result = decorated()
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_count_verification(self):
        """リトライ回数の検証をテスト（要件6.1）"""
        mock_func = Mock(side_effect=Exception("error"))
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):
            decorated = retry(max_retries=3, base_delay=0.1)(mock_func)
            
            with pytest.raises(Exception, match="error"):
                decorated()
        
        # max_retries=3の場合、初回 + 3回リトライ = 合計4回呼び出される
        assert mock_func.call_count == 4
    
    def test_all_retries_fail(self):
        """すべてのリトライが失敗した場合のテスト（要件6.3）"""
        mock_func = Mock(side_effect=Exception("persistent error"))
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):
            decorated = retry(max_retries=2, base_delay=0.1)(mock_func)
            
            with pytest.raises(Exception, match="persistent error"):
                decorated()
        
        # 初回 + 2回リトライ = 合計3回
        assert mock_func.call_count == 3
    
    def test_last_exception_raised(self):
        """最後の例外が再送出されることをテスト（要件6.3）"""
        mock_func = Mock(side_effect=[
            Exception("error1"),
            Exception("error2"),
            Exception("final error")
        ])
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):
            decorated = retry(max_retries=2, base_delay=0.1)(mock_func)
            
            with pytest.raises(Exception, match="final error"):
                decorated()
    
    def test_retry_with_arguments(self):
        """引数を持つ関数のリトライをテスト"""
        mock_func = Mock(side_effect=[Exception("error"), "success"])
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):
            decorated = retry(max_retries=2, base_delay=0.1)(mock_func)
            result = decorated("arg1", kwarg1="value1")
        
        assert result == "success"
        # 引数が正しく渡されていることを確認
        mock_func.assert_called_with("arg1", kwarg1="value1")
    
    def test_zero_retries(self):
        """リトライ回数が0の場合のテスト"""
        mock_func = Mock(side_effect=Exception("error"))
        mock_func.__name__ = "test_function"
        
        decorated = retry(max_retries=0, base_delay=0.1)(mock_func)
        
        with pytest.raises(Exception, match="error"):
            decorated()
        
        # リトライなしで1回だけ実行
        assert mock_func.call_count == 1


class TestExponentialBackoff:
    """指数バックオフのテスト（要件6.4）"""
    
    def test_exponential_backoff_timing(self):
        """指数バックオフの待機時間をテスト"""
        mock_func = Mock(side_effect=Exception("error"))
        mock_func.__name__ = "test_function"
        
        sleep_times = []
        
        def mock_sleep(duration):
            sleep_times.append(duration)
        
        with patch('time.sleep', side_effect=mock_sleep):
            decorated = retry(max_retries=3, base_delay=1.0, exponential_base=2.0)(mock_func)
            
            with pytest.raises(Exception):
                decorated()
        
        # 指数バックオフの検証: 1.0, 2.0, 4.0
        assert len(sleep_times) == 3
        assert sleep_times[0] == 1.0
        assert sleep_times[1] == 2.0
        assert sleep_times[2] == 4.0
    
    def test_exponential_backoff_with_max_delay(self):
        """最大遅延時間の制限をテスト（要件6.4）"""
        mock_func = Mock(side_effect=Exception("error"))
        mock_func.__name__ = "test_function"
        
        sleep_times = []
        
        def mock_sleep(duration):
            sleep_times.append(duration)
        
        with patch('time.sleep', side_effect=mock_sleep):
            decorated = retry(
                max_retries=4,
                base_delay=1.0,
                max_delay=5.0,
                exponential_base=2.0
            )(mock_func)
            
            with pytest.raises(Exception):
                decorated()
        
        # 指数バックオフ: 1.0, 2.0, 4.0, 8.0 -> max_delayで制限: 1.0, 2.0, 4.0, 5.0
        assert len(sleep_times) == 4
        assert sleep_times[0] == 1.0
        assert sleep_times[1] == 2.0
        assert sleep_times[2] == 4.0
        assert sleep_times[3] == 5.0  # max_delayで制限される
    
    def test_custom_exponential_base(self):
        """カスタム指数基数のテスト"""
        mock_func = Mock(side_effect=Exception("error"))
        mock_func.__name__ = "test_function"
        
        sleep_times = []
        
        def mock_sleep(duration):
            sleep_times.append(duration)
        
        with patch('time.sleep', side_effect=mock_sleep):
            decorated = retry(
                max_retries=3,
                base_delay=1.0,
                exponential_base=3.0
            )(mock_func)
            
            with pytest.raises(Exception):
                decorated()
        
        # 指数基数3.0の場合: 1.0, 3.0, 9.0
        assert len(sleep_times) == 3
        assert sleep_times[0] == 1.0
        assert sleep_times[1] == 3.0
        assert sleep_times[2] == 9.0


class TestExceptionFiltering:
    """例外フィルタリングのテスト（要件6.5）"""
    
    def test_retry_specific_exception_only(self):
        """特定の例外のみリトライすることをテスト（要件6.5）"""
        # ValueError のみリトライ対象
        mock_func = Mock(side_effect=[ValueError("error1"), ValueError("error2"), "success"])
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):
            decorated = retry(max_retries=3, base_delay=0.1, exceptions=ValueError)(mock_func)
            result = decorated()
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_non_retryable_exception_raised_immediately(self):
        """リトライ対象外の例外は即座に再送出されることをテスト（要件6.5）"""
        # ValueError のみリトライ対象だが、TypeErrorが発生
        mock_func = Mock(side_effect=TypeError("type error"))
        mock_func.__name__ = "test_function"
        
        decorated = retry(max_retries=3, base_delay=0.1, exceptions=ValueError)(mock_func)
        
        with pytest.raises(TypeError, match="type error"):
            decorated()
        
        # リトライせずに1回だけ実行
        assert mock_func.call_count == 1
    
    def test_multiple_exception_types(self):
        """複数の例外タイプをリトライ対象にするテスト"""
        # ValueError と TypeError の両方をリトライ対象
        mock_func = Mock(side_effect=[
            ValueError("error1"),
            TypeError("error2"),
            "success"
        ])
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):
            decorated = retry(
                max_retries=3,
                base_delay=0.1,
                exceptions=(ValueError, TypeError)
            )(mock_func)
            result = decorated()
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_exception_not_in_filter_fails_immediately(self):
        """フィルタに含まれない例外は即座に失敗することをテスト（要件6.5）"""
        # ValueError と TypeError のみリトライ対象だが、RuntimeErrorが発生
        mock_func = Mock(side_effect=RuntimeError("runtime error"))
        mock_func.__name__ = "test_function"
        
        decorated = retry(
            max_retries=3,
            base_delay=0.1,
            exceptions=(ValueError, TypeError)
        )(mock_func)
        
        with pytest.raises(RuntimeError, match="runtime error"):
            decorated()
        
        # リトライせずに1回だけ実行
        assert mock_func.call_count == 1
    
    def test_default_exception_catches_all(self):
        """デフォルトではすべての例外をキャッチすることをテスト"""
        # 様々な例外タイプ
        mock_func = Mock(side_effect=[
            ValueError("error1"),
            TypeError("error2"),
            RuntimeError("error3"),
            "success"
        ])
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):
            # exceptionsパラメータを指定しない（デフォルトはException）
            decorated = retry(max_retries=4, base_delay=0.1)(mock_func)
            result = decorated()
        
        assert result == "success"
        assert mock_func.call_count == 4
