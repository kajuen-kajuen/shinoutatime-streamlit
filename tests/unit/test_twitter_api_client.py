"""
Twitter API Clientのユニットテスト

Twitter API Clientの各機能をテストします。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests

from src.clients.twitter_api_client import TwitterAPIClient
from src.models.oembed_response import OEmbedResponse, RateLimitInfo
from src.exceptions.errors import (
    InvalidURLError,
    NetworkError,
    APITimeoutError,
    RateLimitError
)
from tests.fixtures.mock_responses import (
    create_mock_oembed_response,
    create_mock_success_response,
    create_mock_error_response,
    create_mock_rate_limit_headers
)
from tests.fixtures.sample_html import VALID_TWITTER_EMBED_HTML


class TestTwitterAPIClientBasic:
    """基本的なAPI呼び出しのテスト（要件1.1）"""
    
    def test_get_oembed_success_with_valid_url(self):
        """有効なURLでのAPI呼び出しが成功する"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        mock_response_data = create_mock_oembed_response(
            html=VALID_TWITTER_EMBED_HTML,
            url=tweet_url
        )
        mock_response = create_mock_success_response(mock_response_data)
        
        # Act
        with patch('requests.get', return_value=mock_response):
            result = client.get_oembed(tweet_url)
        
        # Assert
        assert isinstance(result, OEmbedResponse)
        assert result.html == VALID_TWITTER_EMBED_HTML
        assert result.type == "rich"
        assert result.version == "1.0"
        assert result.provider_name == "Twitter"
    
    def test_get_oembed_parses_response_correctly(self):
        """レスポンスが正しくパースされる"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        mock_response_data = create_mock_oembed_response(
            html="<blockquote>test</blockquote>",
            author_name="テストユーザー",
            author_url="https://twitter.com/testuser",
            width=550,
            height=400
        )
        mock_response = create_mock_success_response(mock_response_data)
        
        # Act
        with patch('requests.get', return_value=mock_response):
            result = client.get_oembed(tweet_url)
        
        # Assert
        assert result.html == "<blockquote>test</blockquote>"
        assert result.author_name == "テストユーザー"
        assert result.author_url == "https://twitter.com/testuser"
        assert result.width == 550
        assert result.height == 400
    
    def test_get_oembed_creates_oembed_response_object(self):
        """OEmbedResponseオブジェクトが正しく生成される"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        mock_response_data = create_mock_oembed_response()
        mock_response = create_mock_success_response(mock_response_data)
        
        # Act
        with patch('requests.get', return_value=mock_response):
            result = client.get_oembed(tweet_url)
        
        # Assert
        assert isinstance(result, OEmbedResponse)
        assert hasattr(result, 'html')
        assert hasattr(result, 'width')
        assert hasattr(result, 'height')
        assert hasattr(result, 'type')
        assert hasattr(result, 'version')
        assert hasattr(result, 'author_name')
        assert hasattr(result, 'author_url')
        assert hasattr(result, 'provider_name')
        assert hasattr(result, 'provider_url')
    
    def test_get_oembed_with_optional_parameters(self):
        """オプションパラメータが正しく渡される"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        mock_response_data = create_mock_oembed_response()
        mock_response = create_mock_success_response(mock_response_data)
        
        # Act
        with patch('requests.get', return_value=mock_response) as mock_get:
            result = client.get_oembed(
                tweet_url,
                max_width=500,
                hide_media=True,
                hide_thread=True,
                omit_script=True,
                theme="dark"
            )
        
        # Assert
        assert isinstance(result, OEmbedResponse)
        # リクエストパラメータを確認
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['url'] == tweet_url
        assert params['maxwidth'] == 500
        assert params['hide_media'] == "true"
        assert params['hide_thread'] == "true"
        assert params['omit_script'] == "true"
        assert params['theme'] == "dark"
    
    def test_get_oembed_returns_non_empty_html(self):
        """取得したHTMLが空でない"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        mock_response_data = create_mock_oembed_response(
            html=VALID_TWITTER_EMBED_HTML
        )
        mock_response = create_mock_success_response(mock_response_data)
        
        # Act
        with patch('requests.get', return_value=mock_response):
            result = client.get_oembed(tweet_url)
        
        # Assert
        assert result.html is not None
        assert len(result.html) > 0
        assert "blockquote" in result.html



class TestTwitterAPIClientErrorHandling:
    """エラーハンドリングのテスト（要件1.2, 1.4, 1.5）"""
    
    def test_get_oembed_raises_invalid_url_error_on_404(self):
        """404エラー時にInvalidURLErrorが発生する"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/9999999999"
        
        mock_response = create_mock_error_response(404)
        
        # Act & Assert
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(InvalidURLError) as exc_info:
                client.get_oembed(tweet_url)
            
            assert tweet_url in str(exc_info.value)
            assert "見つかりません" in str(exc_info.value)
    
    def test_get_oembed_raises_rate_limit_error_on_429(self):
        """429エラー時にRateLimitErrorが発生する"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        mock_response = create_mock_error_response(429)
        
        # Act & Assert
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(RateLimitError) as exc_info:
                client.get_oembed(tweet_url)
            
            assert "レート制限" in str(exc_info.value)
    
    def test_get_oembed_raises_network_error_on_connection_error(self):
        """ConnectionError時にNetworkErrorが発生する"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        # Act & Assert
        with patch('requests.get', side_effect=requests.exceptions.ConnectionError("接続失敗")):
            with pytest.raises(NetworkError) as exc_info:
                client.get_oembed(tweet_url)
            
            assert "ネットワーク" in str(exc_info.value)
    
    def test_get_oembed_raises_timeout_error_on_timeout(self):
        """Timeout時にAPITimeoutErrorが発生する"""
        # Arrange
        client = TwitterAPIClient(timeout=5.0)
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        # Act & Assert
        with patch('requests.get', side_effect=requests.exceptions.Timeout("タイムアウト")):
            with pytest.raises(APITimeoutError) as exc_info:
                client.get_oembed(tweet_url)
            
            assert "タイムアウト" in str(exc_info.value)
            assert exc_info.value.timeout_seconds == 5.0
    
    def test_get_oembed_raises_network_error_on_request_exception(self):
        """RequestException時にNetworkErrorが発生する"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        # Act & Assert
        with patch('requests.get', side_effect=requests.exceptions.RequestException("リクエストエラー")):
            with pytest.raises(NetworkError) as exc_info:
                client.get_oembed(tweet_url)
            
            assert "リクエストエラー" in str(exc_info.value)
    
    def test_get_oembed_raises_network_error_on_invalid_json(self):
        """JSONパースエラー時にNetworkErrorが発生する"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.headers = {}
        
        # Act & Assert
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(NetworkError) as exc_info:
                client.get_oembed(tweet_url)
            
            assert "形式が不正" in str(exc_info.value)
    
    def test_get_oembed_raises_network_error_on_500(self):
        """500エラー時にNetworkErrorが発生する"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        mock_response = create_mock_error_response(500)
        
        # Act & Assert
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(NetworkError) as exc_info:
                client.get_oembed(tweet_url)
            
            assert "500" in str(exc_info.value)



class TestTwitterAPIClientRateLimit:
    """レート制限情報の更新テスト（要件1.3）"""
    
    def test_update_rate_limit_info_from_response_headers(self):
        """レスポンスヘッダーからレート制限情報が抽出される"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        reset_timestamp = int((datetime.now() + timedelta(minutes=15)).timestamp())
        headers = create_mock_rate_limit_headers(
            limit=300,
            remaining=250,
            reset_timestamp=reset_timestamp
        )
        
        mock_response_data = create_mock_oembed_response()
        mock_response = create_mock_success_response(mock_response_data, headers=headers)
        
        # Act
        with patch('requests.get', return_value=mock_response):
            client.get_oembed(tweet_url)
        
        # Assert
        rate_limit_info = client.check_rate_limit()
        assert rate_limit_info is not None
        assert isinstance(rate_limit_info, RateLimitInfo)
        assert rate_limit_info.limit == 300
        assert rate_limit_info.remaining == 250
        assert isinstance(rate_limit_info.reset_time, datetime)
    
    def test_rate_limit_info_object_creation(self):
        """RateLimitInfoオブジェクトが正しく生成される"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        reset_timestamp = int((datetime.now() + timedelta(minutes=15)).timestamp())
        headers = create_mock_rate_limit_headers(
            limit=100,
            remaining=50,
            reset_timestamp=reset_timestamp
        )
        
        mock_response_data = create_mock_oembed_response()
        mock_response = create_mock_success_response(mock_response_data, headers=headers)
        
        # Act
        with patch('requests.get', return_value=mock_response):
            client.get_oembed(tweet_url)
        
        # Assert
        rate_limit_info = client.check_rate_limit()
        assert hasattr(rate_limit_info, 'limit')
        assert hasattr(rate_limit_info, 'remaining')
        assert hasattr(rate_limit_info, 'reset_time')
    
    def test_check_rate_limit_returns_none_initially(self):
        """初期状態ではcheck_rate_limitがNoneを返す"""
        # Arrange
        client = TwitterAPIClient()
        
        # Act
        rate_limit_info = client.check_rate_limit()
        
        # Assert
        assert rate_limit_info is None
    
    def test_rate_limit_info_updates_on_each_request(self):
        """各リクエストでレート制限情報が更新される"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        # 最初のリクエスト
        headers1 = create_mock_rate_limit_headers(remaining=299)
        mock_response1 = create_mock_success_response(
            create_mock_oembed_response(),
            headers=headers1
        )
        
        # 2回目のリクエスト
        headers2 = create_mock_rate_limit_headers(remaining=298)
        mock_response2 = create_mock_success_response(
            create_mock_oembed_response(),
            headers=headers2
        )
        
        # Act
        with patch('requests.get', return_value=mock_response1):
            client.get_oembed(tweet_url)
        
        rate_limit_info1 = client.check_rate_limit()
        
        with patch('requests.get', return_value=mock_response2):
            client.get_oembed(tweet_url)
        
        rate_limit_info2 = client.check_rate_limit()
        
        # Assert
        assert rate_limit_info1.remaining == 299
        assert rate_limit_info2.remaining == 298
    
    def test_rate_limit_info_handles_missing_headers(self):
        """レート制限ヘッダーがない場合でもエラーにならない"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        mock_response_data = create_mock_oembed_response()
        mock_response = create_mock_success_response(mock_response_data, headers={})
        
        # Act
        with patch('requests.get', return_value=mock_response):
            client.get_oembed(tweet_url)
        
        # Assert - エラーが発生しないことを確認
        # レート制限情報は更新されない（以前の値が保持される）
        rate_limit_info = client.check_rate_limit()
        # 初回なのでNoneのまま
        assert rate_limit_info is None
    
    def test_rate_limit_reset_time_extraction(self):
        """レート制限リセット時刻が正しく抽出される"""
        # Arrange
        client = TwitterAPIClient()
        tweet_url = "https://twitter.com/user/status/1234567890"
        
        # 特定の時刻を設定
        expected_reset_time = datetime(2024, 12, 31, 23, 59, 59)
        reset_timestamp = int(expected_reset_time.timestamp())
        
        headers = create_mock_rate_limit_headers(reset_timestamp=reset_timestamp)
        mock_response_data = create_mock_oembed_response()
        mock_response = create_mock_success_response(mock_response_data, headers=headers)
        
        # Act
        with patch('requests.get', return_value=mock_response):
            client.get_oembed(tweet_url)
        
        # Assert
        rate_limit_info = client.check_rate_limit()
        # タイムスタンプが正しく変換されているか確認
        assert rate_limit_info.reset_time.year == expected_reset_time.year
        assert rate_limit_info.reset_time.month == expected_reset_time.month
        assert rate_limit_info.reset_time.day == expected_reset_time.day
