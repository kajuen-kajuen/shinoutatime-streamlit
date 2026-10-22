"""
フィクスチャの動作確認テスト

作成したテストフィクスチャが正しく動作することを確認します。
"""

import pytest

from tests.fixtures import (
    VALID_TWITTER_EMBED_HTML,
    VALID_TWITTER_EMBED_HTML_WITH_HEIGHT,
    INVALID_HTML_MISSING_BLOCKQUOTE,
    INVALID_HTML_MISSING_CLASS,
    INVALID_HTML_EMPTY,
    create_mock_oembed_response,
    create_mock_rate_limit_headers,
    create_mock_error_response,
    create_mock_success_response,
)


class TestHTMLFixtures:
    """HTMLフィクスチャのテスト"""
    
    def test_valid_html_not_empty(self):
        """有効なHTMLが空でないことを確認"""
        assert len(VALID_TWITTER_EMBED_HTML) > 0
        assert "blockquote" in VALID_TWITTER_EMBED_HTML
        assert "twitter-tweet" in VALID_TWITTER_EMBED_HTML
    
    def test_valid_html_with_height_contains_height(self):
        """高さ情報付きHTMLに高さ属性が含まれることを確認"""
        assert "data-height" in VALID_TWITTER_EMBED_HTML_WITH_HEIGHT
    
    def test_invalid_html_missing_blockquote(self):
        """blockquote欠落HTMLにblockquoteタグがないことを確認"""
        # <blockquote>タグではなく<div>タグを使用していることを確認
        assert "<blockquote" not in INVALID_HTML_MISSING_BLOCKQUOTE
        assert "<div" in INVALID_HTML_MISSING_BLOCKQUOTE
    
    def test_invalid_html_missing_class(self):
        """クラス欠落HTMLにtwitter-tweetクラスがないことを確認"""
        # class="twitter-tweet"属性がないことを確認
        assert 'class="twitter-tweet"' not in INVALID_HTML_MISSING_CLASS
        assert "<blockquote>" in INVALID_HTML_MISSING_CLASS
    
    def test_invalid_html_empty(self):
        """空のHTMLが実際に空であることを確認"""
        assert INVALID_HTML_EMPTY == ""




class TestMockResponseHelpers:
    """モックレスポンスヘルパーのテスト"""
    
    def test_create_mock_oembed_response(self):
        """oEmbedレスポンス作成関数が正しく動作することを確認"""
        response = create_mock_oembed_response()
        
        assert "author_name" in response
        assert "html" in response
        assert "type" in response
        assert response["type"] == "rich"
        assert "blockquote" in response["html"]
        
        # urlを指定した場合はレスポンスに含まれる
        response_with_url = create_mock_oembed_response(url="https://twitter.com/user/status/123")
        assert "url" in response_with_url
        assert response_with_url["url"] == "https://twitter.com/user/status/123"
    
    def test_create_mock_oembed_response_with_custom_html(self):
        """カスタムHTML付きoEmbedレスポンスが正しく作成されることを確認"""
        custom_html = "<blockquote class='twitter-tweet'>カスタムHTML</blockquote>"
        response = create_mock_oembed_response(html=custom_html)
        
        assert response["html"] == custom_html
    
    def test_create_mock_rate_limit_headers(self):
        """レート制限ヘッダー作成関数が正しく動作することを確認"""
        headers = create_mock_rate_limit_headers()
        
        assert "x-rate-limit-limit" in headers
        assert "x-rate-limit-remaining" in headers
        assert "x-rate-limit-reset" in headers
        
        # 値が文字列であることを確認
        assert isinstance(headers["x-rate-limit-limit"], str)
        assert isinstance(headers["x-rate-limit-remaining"], str)
        assert isinstance(headers["x-rate-limit-reset"], str)
    
    def test_create_mock_error_response_404(self):
        """404エラーレスポンスが正しく作成されることを確認"""
        response = create_mock_error_response(404)
        
        assert response.status_code == 404
        assert response.ok is False
        assert "errors" in response.json()
    
    def test_create_mock_error_response_429(self):
        """429エラーレスポンス（レート制限）が正しく作成されることを確認"""
        response = create_mock_error_response(429)
        
        assert response.status_code == 429
        assert response.ok is False
        assert "x-rate-limit-remaining" in response.headers
        assert response.headers["x-rate-limit-remaining"] == "0"
    
    def test_create_mock_success_response(self):
        """成功レスポンスが正しく作成されることを確認"""
        data = {"test": "data"}
        response = create_mock_success_response(data)
        
        assert response.status_code == 200
        assert response.ok is True
        assert response.json() == data
        assert "x-rate-limit-limit" in response.headers


class TestFixturesIntegration:
    """フィクスチャの統合テスト"""
    
    def test_html_and_mock_response_integration(self):
        """HTMLフィクスチャとモックレスポンスの統合"""
        # HTMLフィクスチャを使用してモックレスポンスを作成
        response = create_mock_oembed_response(html=VALID_TWITTER_EMBED_HTML)
        
        assert response["html"] == VALID_TWITTER_EMBED_HTML
        assert "blockquote" in response["html"]
        assert "twitter-tweet" in response["html"]
