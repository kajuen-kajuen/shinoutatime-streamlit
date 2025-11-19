"""
URL検証とツイートID抽出のテスト

src/utils/validators.pyの各関数が正しく動作することを確認するテストです。
"""

import pytest

from src.utils.validators import (
    validate_tweet_url,
    extract_tweet_id,
    is_valid_tweet_id,
)


class TestValidateTweetUrl:
    """validate_tweet_url関数のテスト"""
    
    def test_valid_twitter_com_url(self):
        """twitter.comの標準URLが有効と判定されることを確認"""
        url = "https://twitter.com/user/status/1234567890"
        is_valid, error = validate_tweet_url(url)
        assert is_valid is True
        assert error is None
    
    def test_valid_twitter_com_with_www(self):
        """www付きtwitter.comのURLが有効と判定されることを確認"""
        url = "https://www.twitter.com/user/status/1234567890"
        is_valid, error = validate_tweet_url(url)
        assert is_valid is True
        assert error is None
    
    def test_valid_x_com_url(self):
        """x.comのURLが有効と判定されることを確認"""
        url = "https://x.com/user/status/1234567890"
        is_valid, error = validate_tweet_url(url)
        assert is_valid is True
        assert error is None
    
    def test_valid_x_com_with_www(self):
        """www付きx.comのURLが有効と判定されることを確認"""
        url = "https://www.x.com/user/status/1234567890"
        is_valid, error = validate_tweet_url(url)
        assert is_valid is True
        assert error is None
    
    def test_valid_mobile_twitter_url(self):
        """モバイル版twitter.comのURLが有効と判定されることを確認"""
        url = "https://mobile.twitter.com/user/status/1234567890"
        is_valid, error = validate_tweet_url(url)
        assert is_valid is True
        assert error is None
    
    def test_valid_twitter_web_status_url(self):
        """twitter.com/i/web/status形式のURLが有効と判定されることを確認"""
        url = "https://twitter.com/i/web/status/1234567890"
        is_valid, error = validate_tweet_url(url)
        assert is_valid is True
        assert error is None
    
    def test_valid_http_url(self):
        """httpプロトコルのURLが有効と判定されることを確認"""
        url = "http://twitter.com/user/status/1234567890"
        is_valid, error = validate_tweet_url(url)
        assert is_valid is True
        assert error is None
    
    def test_empty_string(self):
        """空文字列が無効と判定されることを確認"""
        is_valid, error = validate_tweet_url("")
        assert is_valid is False
        assert error == "URLが空です"
    
    def test_whitespace_only(self):
        """空白のみの文字列が無効と判定されることを確認"""
        is_valid, error = validate_tweet_url("   ")
        assert is_valid is False
        assert error == "URLが空です"
    
    def test_too_long_url(self):
        """2048文字を超えるURLが無効と判定されることを確認"""
        long_url = "https://twitter.com/user/status/" + "1" * 2050
        is_valid, error = validate_tweet_url(long_url)
        assert is_valid is False
        assert error == "URLが長すぎます（最大2048文字）"
    
    def test_invalid_domain(self):
        """twitter/x以外のドメインが無効と判定されることを確認"""
        url = "https://facebook.com/post/123"
        is_valid, error = validate_tweet_url(url)
        assert is_valid is False
        assert "無効なツイートURL形式" in error
    
    def test_twitter_url_without_status(self):
        """statusを含まないtwitter URLが無効と判定されることを確認"""
        url = "https://twitter.com/user"
        is_valid, error = validate_tweet_url(url)
        assert is_valid is False
        assert "無効なツイートURL形式" in error
    
    def test_not_a_url(self):
        """URL形式でない文字列が無効と判定されることを確認"""
        is_valid, error = validate_tweet_url("not a url")
        assert is_valid is False
        assert "無効なツイートURL形式" in error


class TestExtractTweetId:
    """extract_tweet_id関数のテスト"""
    
    def test_extract_from_twitter_com(self):
        """twitter.comのURLからツイートIDを抽出できることを確認"""
        url = "https://twitter.com/user/status/1234567890"
        tweet_id = extract_tweet_id(url)
        assert tweet_id == "1234567890"
    
    def test_extract_from_twitter_com_with_www(self):
        """www付きtwitter.comのURLからツイートIDを抽出できることを確認"""
        url = "https://www.twitter.com/user/status/9876543210"
        tweet_id = extract_tweet_id(url)
        assert tweet_id == "9876543210"
    
    def test_extract_from_x_com(self):
        """x.comのURLからツイートIDを抽出できることを確認"""
        url = "https://x.com/user/status/1111111111"
        tweet_id = extract_tweet_id(url)
        assert tweet_id == "1111111111"
    
    def test_extract_from_x_com_with_www(self):
        """www付きx.comのURLからツイートIDを抽出できることを確認"""
        url = "https://www.x.com/user/status/2222222222"
        tweet_id = extract_tweet_id(url)
        assert tweet_id == "2222222222"
    
    def test_extract_from_mobile_twitter(self):
        """モバイル版twitter.comのURLからツイートIDを抽出できることを確認"""
        url = "https://mobile.twitter.com/user/status/3333333333"
        tweet_id = extract_tweet_id(url)
        assert tweet_id == "3333333333"
    
    def test_extract_from_twitter_web_status(self):
        """twitter.com/i/web/status形式のURLからツイートIDを抽出できることを確認"""
        url = "https://twitter.com/i/web/status/4444444444"
        tweet_id = extract_tweet_id(url)
        assert tweet_id == "4444444444"
    
    def test_extract_from_http_url(self):
        """httpプロトコルのURLからツイートIDを抽出できることを確認"""
        url = "http://twitter.com/user/status/5555555555"
        tweet_id = extract_tweet_id(url)
        assert tweet_id == "5555555555"
    
    def test_empty_string_returns_none(self):
        """空文字列の場合にNoneを返すことを確認"""
        tweet_id = extract_tweet_id("")
        assert tweet_id is None
    
    def test_whitespace_only_returns_none(self):
        """空白のみの文字列の場合にNoneを返すことを確認"""
        tweet_id = extract_tweet_id("   ")
        assert tweet_id is None
    
    def test_invalid_url_returns_none(self):
        """無効なURLの場合にNoneを返すことを確認"""
        tweet_id = extract_tweet_id("https://facebook.com/post/123")
        assert tweet_id is None
    
    def test_twitter_url_without_status_returns_none(self):
        """statusを含まないtwitter URLの場合にNoneを返すことを確認"""
        tweet_id = extract_tweet_id("https://twitter.com/user")
        assert tweet_id is None
    
    def test_not_a_url_returns_none(self):
        """URL形式でない文字列の場合にNoneを返すことを確認"""
        tweet_id = extract_tweet_id("not a url")
        assert tweet_id is None


class TestIsValidTweetId:
    """is_valid_tweet_id関数のテスト"""
    
    def test_valid_numeric_id(self):
        """数字のみのIDが有効と判定されることを確認"""
        assert is_valid_tweet_id("1234567890") is True
        assert is_valid_tweet_id("9876543210") is True
        assert is_valid_tweet_id("1111111111") is True
    
    def test_empty_string_is_invalid(self):
        """空文字列が無効と判定されることを確認"""
        assert is_valid_tweet_id("") is False
    
    def test_whitespace_only_is_invalid(self):
        """空白のみの文字列が無効と判定されることを確認"""
        assert is_valid_tweet_id("   ") is False
    
    def test_alphanumeric_is_invalid(self):
        """英数字混在のIDが無効と判定されることを確認"""
        assert is_valid_tweet_id("abc123") is False
        assert is_valid_tweet_id("123abc") is False
    
    def test_with_special_characters_is_invalid(self):
        """特殊文字を含むIDが無効と判定されることを確認"""
        assert is_valid_tweet_id("12-34") is False
        assert is_valid_tweet_id("12_34") is False
        assert is_valid_tweet_id("12.34") is False
