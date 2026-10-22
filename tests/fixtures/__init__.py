"""
テストフィクスチャモジュール

テストで使用する共通のサンプルデータとヘルパー関数を提供します。
"""

from tests.fixtures.sample_html import (
    VALID_TWITTER_EMBED_HTML,
    VALID_TWITTER_EMBED_HTML_WITH_HEIGHT,
    INVALID_HTML_MISSING_BLOCKQUOTE,
    INVALID_HTML_MISSING_CLASS,
    INVALID_HTML_EMPTY,
    INVALID_HTML_MISMATCHED_TAGS,
)

from tests.fixtures.mock_responses import (
    create_mock_oembed_response,
    create_mock_rate_limit_headers,
    create_mock_error_response,
    create_mock_success_response,
    create_mock_network_error,
    create_mock_file_content,
    create_mock_oembed_response_with_rate_limit,
    create_mock_twitter_api_client,
    create_mock_file_repository,
)

__all__ = [
    # HTML fixtures
    "VALID_TWITTER_EMBED_HTML",
    "VALID_TWITTER_EMBED_HTML_WITH_HEIGHT",
    "INVALID_HTML_MISSING_BLOCKQUOTE",
    "INVALID_HTML_MISSING_CLASS",
    "INVALID_HTML_EMPTY",
    "INVALID_HTML_MISMATCHED_TAGS",
    # Mock response helpers
    "create_mock_oembed_response",
    "create_mock_rate_limit_headers",
    "create_mock_error_response",
    "create_mock_success_response",
    "create_mock_network_error",
    "create_mock_file_content",
    "create_mock_oembed_response_with_rate_limit",
    "create_mock_twitter_api_client",
    "create_mock_file_repository",
]
