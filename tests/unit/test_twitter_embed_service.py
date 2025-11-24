"""
Twitter Embed Serviceのユニットテスト

Twitter埋め込みコード取得サービスの機能をテストします。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import logging

from src.services.twitter_embed_service import TwitterEmbedService
from src.models.embed_result import EmbedCodeResult, MultipleEmbedCodeResult
from src.models.oembed_response import OEmbedResponse
from src.exceptions.errors import (
    InvalidURLError,
    NetworkError,
    APITimeoutError,
    RateLimitError,
    FileWriteError
)
from tests.fixtures.sample_html import (
    VALID_TWITTER_EMBED_HTML,
    VALID_TWITTER_EMBED_HTML_WITH_HEIGHT
)
from tests.fixtures.mock_responses import (
    create_mock_oembed_response,
    create_mock_twitter_api_client,
    create_mock_file_repository
)


class TestTwitterEmbedServiceFetchEmbedCode:
    """埋め込みコード取得のテスト（タスク7.1）"""
    
    def test_fetch_embed_code_success(self):
        """
        成功ケース: 有効なURLで埋め込みコードを取得できる
        要件: 4.1
        """
        # Arrange
        tweet_url = "https://twitter.com/user/status/1234567890"
        mock_api_client = create_mock_twitter_api_client(
            should_succeed=True,
            html=VALID_TWITTER_EMBED_HTML
        )
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(tweet_url)
        
        # Assert
        assert result.success is True
        assert result.tweet_url == tweet_url
        assert result.embed_code == VALID_TWITTER_EMBED_HTML
        assert result.error_message is None
        mock_api_client.get_oembed.assert_called_once_with(tweet_url)
    
    def test_fetch_embed_code_with_height(self):
        """
        成功ケース: 高さ情報付きの埋め込みコードを取得できる
        要件: 4.1
        """
        # Arrange
        tweet_url = "https://twitter.com/user/status/1234567890"
        expected_height = 500
        
        mock_oembed = OEmbedResponse(
            author_name="テストユーザー",
            author_url="https://twitter.com/testuser",
            html=VALID_TWITTER_EMBED_HTML_WITH_HEIGHT,
            width=550,
            height=expected_height,
            type="rich",
            cache_age=3153600000,
            provider_name="Twitter",
            provider_url="https://twitter.com",
            version="1.0"
        )
        
        mock_api_client = Mock()
        mock_api_client.get_oembed.return_value = mock_oembed
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(tweet_url)
        
        # Assert
        assert result.success is True
        assert result.height == expected_height
        assert result.embed_code == VALID_TWITTER_EMBED_HTML_WITH_HEIGHT
    
    def test_fetch_embed_code_url_validation(self):
        """
        URL検証: 無効なURLは拒否される
        要件: 4.1
        """
        # Arrange
        invalid_url = "https://example.com/not-a-tweet"
        mock_api_client = Mock()
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(invalid_url)
        
        # Assert
        assert result.success is False
        assert result.tweet_url == invalid_url
        assert result.error_message is not None
        assert "URL" in result.error_message or "形式" in result.error_message
        # API呼び出しは行われない
        mock_api_client.get_oembed.assert_not_called()
    
    def test_fetch_embed_code_tweet_id_extraction(self):
        """
        ツイートID抽出: URLからツイートIDを正しく抽出できる
        要件: 4.1
        """
        # Arrange
        tweet_url = "https://twitter.com/user/status/1234567890"
        mock_api_client = create_mock_twitter_api_client(should_succeed=True)
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        tweet_id = service.extract_tweet_id(tweet_url)
        
        # Assert
        assert tweet_id == "1234567890"
    
    def test_fetch_embed_code_invalid_tweet_id(self):
        """
        ツイートID抽出失敗: IDが抽出できない場合はエラー
        要件: 4.1
        """
        # Arrange
        # 有効なTwitter URLだがステータスIDがない形式
        invalid_url = "https://twitter.com/user"
        mock_api_client = Mock()
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(invalid_url)
        
        # Assert
        assert result.success is False
        # URL検証で失敗するため、エラーメッセージにはURL形式に関する内容が含まれる
        assert result.error_message is not None


class TestTwitterEmbedServiceSaveEmbedCode:
    """埋め込みコード保存のテスト（タスク7.2）"""
    
    def test_save_embed_code_success(self):
        """
        保存成功: 埋め込みコードを正常に保存できる
        要件: 4.2
        """
        # Arrange
        embed_code = VALID_TWITTER_EMBED_HTML
        mock_api_client = Mock()
        mock_file_repo = Mock()
        mock_file_repo.write_embed_code.return_value = True
        mock_file_repo.create_backup.return_value = "/path/to/backup.html"
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.save_embed_code(embed_code, create_backup=True)
        
        # Assert
        assert result is True
        mock_file_repo.write_embed_code.assert_called_once_with(embed_code)
        mock_file_repo.create_backup.assert_called_once()
    
    def test_save_embed_code_with_backup(self):
        """
        バックアップ作成: バックアップが正しく作成される
        要件: 4.5
        """
        # Arrange
        embed_code = VALID_TWITTER_EMBED_HTML
        backup_path = "/path/to/backup_20240101_120000.html"
        
        mock_api_client = Mock()
        mock_file_repo = Mock()
        mock_file_repo.write_embed_code.return_value = True
        mock_file_repo.create_backup.return_value = backup_path
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.save_embed_code(embed_code, create_backup=True)
        
        # Assert
        assert result is True
        mock_file_repo.create_backup.assert_called_once()
    
    def test_save_embed_code_without_backup(self):
        """
        バックアップなし: バックアップを作成せずに保存できる
        要件: 4.2
        """
        # Arrange
        embed_code = VALID_TWITTER_EMBED_HTML
        mock_api_client = Mock()
        mock_file_repo = Mock()
        mock_file_repo.write_embed_code.return_value = True
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.save_embed_code(embed_code, create_backup=False)
        
        # Assert
        assert result is True
        mock_file_repo.create_backup.assert_not_called()
        mock_file_repo.write_embed_code.assert_called_once_with(embed_code)
    
    def test_save_embed_code_backup_failure_continues(self):
        """
        バックアップ失敗時の処理: バックアップ失敗でも保存は継続される
        要件: 4.5
        """
        # Arrange
        embed_code = VALID_TWITTER_EMBED_HTML
        mock_api_client = Mock()
        mock_file_repo = Mock()
        mock_file_repo.create_backup.return_value = None  # バックアップ失敗
        mock_file_repo.write_embed_code.return_value = True
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.save_embed_code(embed_code, create_backup=True)
        
        # Assert
        assert result is True  # 保存自体は成功
        mock_file_repo.write_embed_code.assert_called_once()
    
    def test_save_embed_code_write_failure(self):
        """
        保存失敗: ファイル書き込みに失敗した場合
        要件: 4.2
        """
        # Arrange
        embed_code = VALID_TWITTER_EMBED_HTML
        mock_api_client = Mock()
        mock_file_repo = Mock()
        mock_file_repo.write_embed_code.return_value = False
        mock_file_repo.create_backup.return_value = "/path/to/backup.html"
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.save_embed_code(embed_code, create_backup=True)
        
        # Assert
        assert result is False
    
    def test_save_embed_code_exception_handling(self):
        """
        例外処理: 保存中に例外が発生した場合
        要件: 4.2
        """
        # Arrange
        embed_code = VALID_TWITTER_EMBED_HTML
        mock_api_client = Mock()
        mock_file_repo = Mock()
        mock_file_repo.write_embed_code.side_effect = Exception("書き込みエラー")
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.save_embed_code(embed_code, create_backup=False)
        
        # Assert
        assert result is False



class TestTwitterEmbedServiceMultipleTweets:
    """複数ツイート処理のテスト（タスク7.3）"""
    
    def test_fetch_multiple_embed_codes_all_success(self):
        """
        複数URL処理: すべてのURLで成功する
        要件: 4.1
        """
        # Arrange
        tweet_urls = [
            "https://twitter.com/user1/status/1111111111",
            "https://twitter.com/user2/status/2222222222",
            "https://twitter.com/user3/status/3333333333"
        ]
        
        mock_api_client = create_mock_twitter_api_client(should_succeed=True)
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_multiple_embed_codes(tweet_urls)
        
        # Assert
        assert result.total_count == 3
        assert result.success_count == 3
        assert result.failure_count == 0
        assert len(result.failed_urls) == 0
        assert result.combined_embed_code != ""
        assert mock_api_client.get_oembed.call_count == 3
    
    def test_fetch_multiple_embed_codes_partial_success(self):
        """
        成功・失敗の集計: 一部のURLが失敗する
        要件: 4.1
        """
        # Arrange
        tweet_urls = [
            "https://twitter.com/user1/status/1111111111",
            "https://invalid.com/not-a-tweet",  # 無効なURL
            "https://twitter.com/user3/status/3333333333"
        ]
        
        mock_api_client = create_mock_twitter_api_client(should_succeed=True)
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_multiple_embed_codes(tweet_urls)
        
        # Assert
        assert result.total_count == 3
        assert result.success_count == 2
        assert result.failure_count == 1
        assert len(result.failed_urls) == 1
        assert "https://invalid.com/not-a-tweet" in result.failed_urls
    
    def test_fetch_multiple_embed_codes_max_height_selection(self):
        """
        最大高さの選択: 複数のツイートから最大の高さを選択する
        要件: 4.1
        """
        # Arrange
        tweet_urls = [
            "https://twitter.com/user1/status/1111111111",
            "https://twitter.com/user2/status/2222222222"
        ]
        
        # 異なる高さのレスポンスを返すモックを作成
        mock_api_client = Mock()
        
        oembed1 = OEmbedResponse(
            author_name="User1",
            author_url="https://twitter.com/user1",
            html=VALID_TWITTER_EMBED_HTML,
            width=550,
            height=400,
            type="rich",
            cache_age=3153600000,
            provider_name="Twitter",
            provider_url="https://twitter.com",
            version="1.0"
        )
        
        oembed2 = OEmbedResponse(
            author_name="User2",
            author_url="https://twitter.com/user2",
            html=VALID_TWITTER_EMBED_HTML,
            width=550,
            height=600,  # より高い
            type="rich",
            cache_age=3153600000,
            provider_name="Twitter",
            provider_url="https://twitter.com",
            version="1.0"
        )
        
        mock_api_client.get_oembed.side_effect = [oembed1, oembed2]
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_multiple_embed_codes(tweet_urls)
        
        # Assert
        assert result.max_height == 600  # 最大の高さが選択される
    
    def test_fetch_multiple_embed_codes_default_height(self):
        """
        デフォルト高さ: 高さ情報がない場合はデフォルト値を使用
        要件: 4.1
        """
        # Arrange
        tweet_urls = []  # 空のリスト
        
        mock_api_client = Mock()
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_multiple_embed_codes(tweet_urls)
        
        # Assert
        assert result.max_height == 850  # デフォルト値
        assert result.total_count == 0
        assert result.success_count == 0
    
    def test_fetch_multiple_embed_codes_combined_html(self):
        """
        埋め込みコード連結: 複数のHTMLが正しく連結される
        要件: 4.1
        """
        # Arrange
        tweet_urls = [
            "https://twitter.com/user1/status/1111111111",
            "https://twitter.com/user2/status/2222222222"
        ]
        
        mock_api_client = create_mock_twitter_api_client(should_succeed=True)
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_multiple_embed_codes(tweet_urls)
        
        # Assert
        # 2つのHTMLが改行2つで連結されている
        assert "\n\n" in result.combined_embed_code
        assert result.combined_embed_code.count("blockquote") >= 2


class TestTwitterEmbedServiceErrorHandling:
    """エラー処理のテスト（タスク7.4）"""
    
    def test_fetch_embed_code_invalid_url_error(self):
        """
        無効なURL: 無効なURLでエラーが返される
        要件: 4.4
        """
        # Arrange
        invalid_url = "not-a-url"
        mock_api_client = Mock()
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(invalid_url)
        
        # Assert
        assert result.success is False
        assert result.error_message is not None
        assert result.embed_code is None
    
    def test_fetch_embed_code_api_network_error(self):
        """
        API呼び出し失敗: ネットワークエラーが発生した場合
        要件: 4.4
        """
        # Arrange
        tweet_url = "https://twitter.com/user/status/1234567890"
        mock_api_client = create_mock_twitter_api_client(
            should_succeed=False,
            error_type="network"
        )
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(tweet_url)
        
        # Assert
        assert result.success is False
        assert result.error_message is not None
        assert "エラー" in result.error_message
    
    def test_fetch_embed_code_api_timeout_error(self):
        """
        API呼び出し失敗: タイムアウトエラーが発生した場合
        要件: 4.4
        """
        # Arrange
        tweet_url = "https://twitter.com/user/status/1234567890"
        mock_api_client = create_mock_twitter_api_client(
            should_succeed=False,
            error_type="timeout"
        )
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(tweet_url)
        
        # Assert
        assert result.success is False
        assert result.error_message is not None
    
    def test_fetch_embed_code_rate_limit_error(self):
        """
        API呼び出し失敗: レート制限エラーが発生した場合
        要件: 4.4
        """
        # Arrange
        tweet_url = "https://twitter.com/user/status/1234567890"
        mock_api_client = create_mock_twitter_api_client(
            should_succeed=False,
            error_type="rate_limit"
        )
        mock_file_repo = Mock()
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.fetch_embed_code(tweet_url)
        
        # Assert
        assert result.success is False
        assert result.error_message is not None
    
    def test_save_embed_code_file_write_error(self):
        """
        ファイル書き込み失敗: 書き込み権限がない場合
        要件: 4.4
        """
        # Arrange
        embed_code = VALID_TWITTER_EMBED_HTML
        mock_api_client = Mock()
        mock_file_repo = Mock()
        mock_file_repo.write_embed_code.side_effect = PermissionError("権限がありません")
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo)
        
        # Act
        result = service.save_embed_code(embed_code, create_backup=False)
        
        # Assert
        assert result is False
    
    def test_fetch_embed_code_logs_errors(self):
        """
        エラーログ: エラーが適切にログに記録される
        要件: 4.4
        """
        # Arrange
        tweet_url = "https://twitter.com/user/status/1234567890"
        mock_api_client = create_mock_twitter_api_client(
            should_succeed=False,
            error_type="network"
        )
        mock_file_repo = Mock()
        mock_logger = Mock(spec=logging.Logger)
        
        service = TwitterEmbedService(mock_api_client, mock_file_repo, logger=mock_logger)
        
        # Act
        result = service.fetch_embed_code(tweet_url)
        
        # Assert
        assert result.success is False
        # エラーログが記録されている
        assert mock_logger.error.called
