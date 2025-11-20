"""
Retry Utilityのプロパティベーステスト

リトライ機能の普遍的な性質を検証します。
"""

import pytest
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, settings
from src.utils.retry import retry, RetryStrategy


class TestRetryProperties:
    """Retry Utilityのプロパティテスト"""
    
    @given(
        max_retries=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=100)
    def test_property_retry_count_consistency(self, max_retries):
        """
        Feature: test-coverage-improvement, Property 13: リトライ回数の一貫性
        
        すべてのリトライ回数設定に対して、失敗した処理は指定された回数だけリトライされる
        **検証: 要件6.1**
        """
        # 常に失敗する関数を作成
        mock_func = Mock(side_effect=Exception("error"))
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):  # sleepをモックして高速化
            decorated = retry(max_retries=max_retries, base_delay=0.01)(mock_func)
            
            with pytest.raises(Exception):
                decorated()
        
        # 初回実行 + max_retries回のリトライ = max_retries + 1回の呼び出し
        expected_calls = max_retries + 1
        assert mock_func.call_count == expected_calls, \
            f"max_retries={max_retries}の場合、{expected_calls}回呼び出されるべきですが、{mock_func.call_count}回でした"
    
    @given(
        max_retries=st.integers(min_value=1, max_value=10),
        success_on_attempt=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_retry_until_success(self, max_retries, success_on_attempt):
        """
        リトライ中に成功した場合、それ以上リトライしないことを検証
        
        すべてのリトライ回数設定に対して、途中で成功した場合は
        それ以上リトライせずに成功結果を返す
        """
        # success_on_attemptがmax_retriesより大きい場合はスキップ
        if success_on_attempt > max_retries + 1:
            return
        
        # success_on_attempt回目で成功する関数を作成
        side_effects = [Exception("error")] * (success_on_attempt - 1) + ["success"]
        mock_func = Mock(side_effect=side_effects)
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):
            decorated = retry(max_retries=max_retries, base_delay=0.01)(mock_func)
            result = decorated()
        
        assert result == "success"
        assert mock_func.call_count == success_on_attempt, \
            f"{success_on_attempt}回目で成功するはずが、{mock_func.call_count}回呼び出されました"
    
    @given(
        base_delay=st.floats(min_value=0.01, max_value=2.0),
        exponential_base=st.floats(min_value=1.5, max_value=3.0),
        max_delay=st.floats(min_value=5.0, max_value=100.0),
        attempt=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_exponential_backoff_consistency(
        self, base_delay, exponential_base, max_delay, attempt
    ):
        """
        Feature: test-coverage-improvement, Property 14: 指数バックオフの一貫性
        
        すべてのリトライ試行に対して、待機時間は指数的に増加する
        （base_delay * exponential_base^attempt）
        **検証: 要件6.4**
        """
        strategy = RetryStrategy(
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=exponential_base
        )
        
        delay = strategy.calculate_delay(attempt)
        
        # 期待される遅延時間を計算
        expected_delay = base_delay * (exponential_base ** attempt)
        expected_delay = min(expected_delay, max_delay)
        
        # 浮動小数点の比較のため、許容誤差を設定
        assert abs(delay - expected_delay) < 0.0001, \
            f"attempt={attempt}, base_delay={base_delay}, exponential_base={exponential_base}, " \
            f"max_delay={max_delay}の場合、遅延時間は{expected_delay}であるべきですが、{delay}でした"
        
        # 遅延時間がmax_delayを超えないことを確認
        assert delay <= max_delay, \
            f"遅延時間{delay}がmax_delay={max_delay}を超えています"
        
        # 遅延時間が0以上であることを確認
        assert delay >= 0, f"遅延時間{delay}が負の値です"
    
    @given(
        max_retries=st.integers(min_value=1, max_value=5),
        exception_choice=st.sampled_from([
            (ValueError, ValueError("value error")),
            (TypeError, TypeError("type error")),
            (RuntimeError, RuntimeError("runtime error")),
        ])
    )
    @settings(max_examples=100)
    def test_property_exception_filtering_consistency(self, max_retries, exception_choice):
        """
        Feature: test-coverage-improvement, Property 15: 例外フィルタリングの一貫性
        
        すべての例外タイプに対して、指定された例外のみがリトライされ、
        それ以外の例外は即座に再送出される
        **検証: 要件6.5**
        """
        exception_type, exception_instance = exception_choice
        
        # 指定された例外タイプのみリトライ対象
        mock_func = Mock(side_effect=exception_instance)
        mock_func.__name__ = "test_function"
        
        with patch('time.sleep'):
            decorated = retry(
                max_retries=max_retries,
                base_delay=0.01,
                exceptions=exception_type
            )(mock_func)
            
            with pytest.raises(type(exception_instance)):
                decorated()
        
        # 指定された例外タイプなので、リトライされる
        expected_calls = max_retries + 1
        assert mock_func.call_count == expected_calls, \
            f"例外タイプ{exception_type.__name__}はリトライ対象なので、{expected_calls}回呼び出されるべきですが、{mock_func.call_count}回でした"
    
    @given(
        max_retries=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=100)
    def test_property_non_retryable_exception_immediate_failure(self, max_retries):
        """
        リトライ対象外の例外は即座に失敗することを検証
        
        すべてのリトライ回数設定に対して、リトライ対象外の例外が発生した場合は
        リトライせずに即座に例外を再送出する
        """
        # ValueErrorのみリトライ対象だが、TypeErrorが発生
        mock_func = Mock(side_effect=TypeError("type error"))
        mock_func.__name__ = "test_function"
        
        decorated = retry(
            max_retries=max_retries,
            base_delay=0.01,
            exceptions=ValueError
        )(mock_func)
        
        with pytest.raises(TypeError):
            decorated()
        
        # リトライせずに1回だけ実行
        assert mock_func.call_count == 1, \
            f"リトライ対象外の例外なので1回だけ呼び出されるべきですが、{mock_func.call_count}回でした"
