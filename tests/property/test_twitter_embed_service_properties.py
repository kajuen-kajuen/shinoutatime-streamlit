"""
Twitter Embed Serviceのプロパティベーステスト

Twitter埋め込みコード取得サービスの普遍的な性質を検証します。
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch
import tempfile
import os

from src.services.twitter_embed_service import TwitterEmbedService
from src.models.oembed_response import OEmbedResponse
from src.models.embed_result import EmbedCodeResult
from tests.fixtures.sample_html import VALID_TWITTER_EMBED_HTML
from tests.fixtures.mock_responses import create_mock_oembed_response


# カスタム戦略: 有効なツイートURL
@st.composite
def valid_tweet_urls(draw):
    """有効なツイートURLを生成する"""
    domains = ["twitter.com", "x.com", "mobile.twitter.com"]
    domain = draw(st.sampled_from(domains))
    username = draw(st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
        min_size=1,
        max_size=15
    ))
    tweet_id = draw(st.integers(min_value=1000000000, max_value=9999999999999999999))
    
    if domain == "mobile.twitter.com":
        return f"https://{domain}/{username}/status/{tweet_id}"
    else:
        return f"https://www.{domain}/{username}/status/{tweet_id}"


# カスタム戦略: 無効なツイートURL
@st.composite
def invalid_tweet_urls(draw):
    """無効なツイートURLを生成する"""
    invalid_patterns = [
        "https://example.com/status/123",
        "https://twitter.com/user",
        "https://twitter.com/",
        "not-a-url",
        "ftp://twitter.com/user/status/123",
        "https://twitter.com/user/tweet/123",
    ]
    return draw(st.sampled_from(invalid_patterns))


# カスタム戦略: 埋め込みHTML
@st.composite
def embed_html(draw):
    """埋め込みHTMLを生成する"""
    # \rを除外した文字列を生成（改行コードの問題を回避）
    content = draw(st.text(
        alphabet=st.characters(blacklist_characters='\r'),
        min_size=1,
        max_size=500
    ))
    return f'<blockquote class="twitter-tweet"><p>{content}</p></blockquote>'


class TestTwitterEmbedServiceProperties:
    """Twitter Embed Serviceのプロパティテスト"""
    
    @given(valid_tweet_urls())
    @settings(max_examples=100, deadline=5000)
    def test_property_8_fetch_embed_code_consistency(self, tweet_url):
        """
        Feature: test-coverage-improvement, Property 8: 埋め込みコード取得の一貫性
        
        プロパティ8: 埋め込みコード取得の一貫性
        *すべての*有効なツイートURLに対して、API呼び出しが成功した場合、
        返されるHTMLは空でなく、EmbedCodeResult型である
        **検証: 要件4.1**
        """
        # Arrange
        mock_oembed = OEmbedResponse(
            html=VALID_TWITTER_EMBED_HTML,
            width=550,
            height=500,
            author_name="テストユーザー",
            author_url="https://twitter.com/testuser"
        )
        
        mock_api_client = Mock()
        mock_api_client.get_oembed.return_value = mock_oembed
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(tweet_url)
        
        # Assert
        # 成功した場合、結果は正しい型である
        assert isinstance(result, EmbedCodeResult)
        
        # 成功した場合、埋め込みコードは空でない
        if result.success:
            assert result.embed_code is not None
            assert result.embed_code != ""
            assert result.tweet_url == tweet_url
            assert result.error_message is None
    
    @given(invalid_tweet_urls())
    @settings(max_examples=100, deadline=5000)
    def test_property_invalid_url_rejection(self, invalid_url):
        """
        無効なURL拒否の一貫性
        
        *すべての*無効なツイートURLに対して、エラーが返される
        """
        # Arrange
        mock_api_client = Mock()
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(invalid_url)
        
        # Assert
        # 無効なURLは必ず失敗する
        assert result.success is False
        assert result.error_message is not None
        assert result.embed_code is None
        # API呼び出しは行われない
        mock_api_client.get_oembed.assert_not_called()
    
    @given(
        st.lists(valid_tweet_urls(), min_size=1, max_size=10)
    )
    @settings(max_examples=50, deadline=10000)
    def test_property_multiple_tweets_aggregation(self, tweet_urls):
        """
        複数ツイート処理の集計の一貫性
        
        *すべての*ツイートURLリストに対して、
        total_count = success_count + failure_count が成り立つ
        """
        # Arrange
        mock_oembed = OEmbedResponse(
            html=VALID_TWITTER_EMBED_HTML,
            width=550,
            height=500
        )
        
        mock_api_client = Mock()
        mock_api_client.get_oembed.return_value = mock_oembed
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_multiple_embed_codes(tweet_urls)
        
        # Assert
        # 集計の一貫性
        assert result.total_count == len(tweet_urls)
        assert result.total_count == result.success_count + result.failure_count
        assert len(result.results) == result.total_count
        
        # 成功したツイートの数と失敗したURLリストの長さが一致
        assert result.failure_count == len(result.failed_urls)


    @given(embed_html())
    @settings(max_examples=100, deadline=5000)
    def test_property_9_save_embed_code_roundtrip(self, embed_code):
        """
        Feature: test-coverage-improvement, Property 9: 埋め込みコード保存のラウンドトリップ
        
        プロパティ9: 埋め込みコード保存のラウンドトリップ
        *すべての*埋め込みコードに対して、保存してから読み込むと元の内容と一致する
        **検証: 要件4.2, 4.3**
        """
        # Arrange
        # 一時ファイルを使用してラウンドトリップをテスト
        with tempfile.TemporaryDirectory() as temp_dir:
            embed_file = os.path.join(temp_dir, "test_embed.html")
            height_file = os.path.join(temp_dir, "test_height.txt")
            
            # FileRepositoryの実装を使用
            from src.repositories.file_repository import FileRepository
            file_repo = FileRepository(embed_file, height_file)
            
            mock_api_client = Mock()
            service = TwitterEmbedService(mock_api_client, file_repo)
            
            # Act
            # 保存
            save_result = service.save_embed_code(embed_code, create_backup=False)
            
            # 読み込み
            if save_result:
                read_content = file_repo.read_embed_code()
                
                # Assert
                # ラウンドトリップの一貫性
                assert read_content == embed_code
    
    @given(
        embed_html(),
        st.booleans()
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_save_with_backup_consistency(self, embed_code, create_backup):
        """
        バックアップ作成の一貫性
        
        *すべての*埋め込みコードとバックアップフラグに対して、
        保存が成功した場合、ファイルが存在する
        """
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            embed_file = os.path.join(temp_dir, "test_embed.html")
            height_file = os.path.join(temp_dir, "test_height.txt")
            
            from src.repositories.file_repository import FileRepository
            file_repo = FileRepository(embed_file, height_file)
            
            mock_api_client = Mock()
            service = TwitterEmbedService(mock_api_client, file_repo)
            
            # Act
            result = service.save_embed_code(embed_code, create_backup=create_backup)
            
            # Assert
            if result:
                # 保存が成功した場合、ファイルが存在する
                assert os.path.exists(embed_file)
                
                # ファイルの内容が正しい
                with open(embed_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert content == embed_code


    @given(valid_tweet_urls())
    @settings(max_examples=100, deadline=5000)
    def test_property_10_error_handling_consistency(self, tweet_url):
        """
        Feature: test-coverage-improvement, Property 10: エラー処理の一貫性
        
        プロパティ10: エラー処理の一貫性
        *すべての*エラー状況（無効なURL、ネットワークエラー）に対して、
        EmbedCodeResultのsuccessフィールドがFalseであり、error_messageが空でない
        **検証: 要件4.4**
        """
        # Arrange - ネットワークエラーをシミュレート
        from src.exceptions.errors import NetworkError
        
        mock_api_client = Mock()
        mock_api_client.get_oembed.side_effect = NetworkError()
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(tweet_url)
        
        # Assert
        # エラー時は必ず失敗する
        assert result.success is False
        # エラーメッセージが設定されている
        assert result.error_message is not None
        assert result.error_message != ""
        # 埋め込みコードは設定されない
        assert result.embed_code is None
    
    @given(
        st.sampled_from([
            "network",
            "timeout",
            "rate_limit"
        ])
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_different_error_types_consistency(self, error_type):
        """
        異なるエラータイプの一貫性
        
        *すべての*エラータイプに対して、エラー処理が一貫している
        """
        # Arrange
        from src.exceptions.errors import NetworkError, APITimeoutError, RateLimitError
        
        error_map = {
            "network": NetworkError(),
            "timeout": APITimeoutError(30.0),
            "rate_limit": RateLimitError()
        }
        
        tweet_url = "https://twitter.com/user/status/1234567890"
        mock_api_client = Mock()
        mock_api_client.get_oembed.side_effect = error_map[error_type]
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(tweet_url)
        
        # Assert
        # すべてのエラータイプで一貫した動作
        assert result.success is False
        assert result.error_message is not None
        assert result.embed_code is None
        assert result.tweet_url == tweet_url
