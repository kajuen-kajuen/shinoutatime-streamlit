"""
Twitter API Clientのプロパティベーステスト

普遍的な性質を多数のランダム入力で検証します。
"""

import pytest
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings, HealthCheck
import requests

from src.clients.twitter_api_client import TwitterAPIClient
from src.models.oembed_response import OEmbedResponse
from src.exceptions.errors import (
    InvalidURLError,
    NetworkError,
    APITimeoutError
)
from tests.fixtures.mock_responses import (
    create_mock_oembed_response,
    create_mock_success_response,
    create_mock_error_response
)


# 有効なツイートURLのパターンを生成する戦略
@st.composite
def valid_tweet_urls(draw):
    """有効なツイートURLを生成する"""
    username = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), min_codepoint=48, max_codepoint=122),
        min_size=1,
        max_size=15
    ).filter(lambda x: x and x[0].isalpha()))
    
    tweet_id = draw(st.integers(min_value=1000000000000000000, max_value=9999999999999999999))
    
    return f"https://twitter.com/{username}/status/{tweet_id}"


# 無効なURLのパターンを生成する戦略
@st.composite
def invalid_urls(draw):
    """無効なURLを生成する"""
    invalid_patterns = [
        # 完全に無効なURL
        st.text(min_size=1, max_size=50).filter(lambda x: not x.startswith('http')),
        # ドメインが違う
        st.builds(lambda: "https://example.com/status/123"),
        # パスが違う
        st.builds(lambda: "https://twitter.com/invalid/path"),
        # IDが無効
        st.builds(lambda: "https://twitter.com/user/status/abc"),
    ]
    
    return draw(st.one_of(*invalid_patterns))


class TestTwitterAPIClientProperties:
    """Twitter API Clientのプロパティベーステスト"""
    
    @given(valid_tweet_urls())
    @settings(max_examples=20, deadline=None)
    def test_property_valid_url_processing_consistency(self, tweet_url):
        """
        Feature: test-coverage-improvement, Property 1: 有効なURL処理の一貫性
        
        プロパティ1: 有効なURL処理の一貫性
        すべての有効なツイートURLに対して、API呼び出しが成功した場合、
        返されるHTMLは空でなく、OEmbedResponse型である
        検証: 要件1.1
        """
        # Arrange
        client = TwitterAPIClient()
        
        mock_response_data = create_mock_oembed_response(
            html="<blockquote class='twitter-tweet'>test</blockquote>",
            url=tweet_url
        )
        mock_response = create_mock_success_response(mock_response_data)
        
        # Act
        with patch('requests.get', return_value=mock_response):
            result = client.get_oembed(tweet_url)
        
        # Assert - プロパティの検証
        assert isinstance(result, OEmbedResponse), "結果はOEmbedResponse型である必要があります"
        assert result.html is not None, "HTMLはNoneであってはいけません"
        assert len(result.html) > 0, "HTMLは空であってはいけません"
        assert result.type == "rich", "typeは'rich'である必要があります"
        assert result.version == "1.0", "versionは'1.0'である必要があります"
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=20, deadline=None)
    def test_property_invalid_url_rejection_consistency(self, invalid_url):
        """
        Feature: test-coverage-improvement, Property 2: 無効なURL拒否の一貫性
        
        プロパティ2: 無効なURL拒否の一貫性
        すべての無効なツイートURLに対して、InvalidURLErrorまたはそれに相当するエラーが発生する
        検証: 要件1.2
        """
        # 有効なTwitter URLのパターンを除外
        if invalid_url.startswith('https://twitter.com/') and '/status/' in invalid_url:
            parts = invalid_url.split('/status/')
            if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) >= 10:
                # これは有効なURLパターンなのでスキップ
                return
        
        # Arrange
        client = TwitterAPIClient()
        
        # 404エラーを返すモックレスポンス
        mock_response = create_mock_error_response(404)
        
        # Act & Assert
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(InvalidURLError):
                client.get_oembed(invalid_url)
    
    @given(valid_tweet_urls(), st.sampled_from(['connection', 'timeout']))
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_property_network_error_handling_consistency(self, tweet_url, error_type):
        """
        Feature: test-coverage-improvement, Property 3: ネットワークエラーの適切な処理
        
        プロパティ3: ネットワークエラーの適切な処理
        すべてのネットワークエラー（ConnectionError、Timeout）に対して、
        NetworkErrorまたはAPITimeoutErrorが発生する
        検証: 要件1.4
        """
        # Arrange
        client = TwitterAPIClient(max_retries=1, retry_delay=0.1)
        
        # time.sleepをモックして高速化
        with patch('time.sleep'):
            # エラータイプに応じてテスト
            if error_type == 'connection':
                with patch('requests.get', side_effect=requests.exceptions.ConnectionError("接続失敗")):
                    with pytest.raises(NetworkError):
                        client.get_oembed(tweet_url)
            else:  # timeout
                with patch('requests.get', side_effect=requests.exceptions.Timeout("タイムアウト")):
                    with pytest.raises(APITimeoutError):
                        client.get_oembed(tweet_url)
