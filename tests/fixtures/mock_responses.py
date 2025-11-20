"""
モックレスポンスのヘルパー関数

Twitter API、ファイルシステム、その他の外部依存のモックレスポンスを生成するヘルパー関数を提供します。
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from unittest.mock import Mock
import requests


def create_mock_oembed_response(
    html: str = None,
    author_name: str = "テストユーザー",
    author_url: str = "https://twitter.com/testuser",
    provider_name: str = "Twitter",
    provider_url: str = "https://twitter.com",
    cache_age: Optional[int] = 3153600000,
    height: Optional[int] = None,
    width: Optional[int] = None,
    url: str = None
) -> Dict[str, Any]:
    """
    Twitter oEmbed APIのモックレスポンスを作成する
    
    Args:
        html: 埋め込みHTML（Noneの場合はデフォルトのHTMLを使用）
        author_name: 投稿者名
        author_url: 投稿者URL
        provider_name: プロバイダー名
        provider_url: プロバイダーURL
        cache_age: キャッシュ有効期限
        height: 高さ（ピクセル）
        width: 幅（ピクセル）
        url: ツイートURL
        
    Returns:
        oEmbedレスポンスの辞書
    """
    if html is None:
        html = """<blockquote class="twitter-tweet">
  <p lang="ja" dir="ltr">テストツイート</p>
  <a href="https://twitter.com/user/status/1234567890">January 1, 2024</a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>"""
    
    response = {
        "author_name": author_name,
        "author_url": author_url,
        "html": html,
        "width": width,
        "height": height,
        "type": "rich",
        "cache_age": cache_age,
        "provider_name": provider_name,
        "provider_url": provider_url,
        "version": "1.0"
    }
    
    # urlが指定されている場合は追加
    if url is not None:
        response["url"] = url
    
    return response


def create_mock_rate_limit_headers(
    limit: int = 300,
    remaining: int = 299,
    reset_timestamp: Optional[int] = None
) -> Dict[str, str]:
    """
    Twitter APIのレート制限ヘッダーを作成する
    
    Args:
        limit: レート制限の上限
        remaining: 残りのリクエスト数
        reset_timestamp: リセット時刻のUNIXタイムスタンプ（Noneの場合は15分後）
        
    Returns:
        レート制限ヘッダーの辞書
    """
    if reset_timestamp is None:
        # 15分後のタイムスタンプを計算
        reset_time = datetime.now() + timedelta(minutes=15)
        reset_timestamp = int(reset_time.timestamp())
    
    return {
        "x-rate-limit-limit": str(limit),
        "x-rate-limit-remaining": str(remaining),
        "x-rate-limit-reset": str(reset_timestamp)
    }


def create_mock_error_response(
    status_code: int,
    error_message: str = None,
    error_code: Optional[int] = None
) -> Mock:
    """
    エラーレスポンスのモックを作成する
    
    Args:
        status_code: HTTPステータスコード
        error_message: エラーメッセージ（Noneの場合はデフォルトメッセージ）
        error_code: Twitter APIのエラーコード
        
    Returns:
        モックレスポンスオブジェクト
    """
    if error_message is None:
        error_messages = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout"
        }
        error_message = error_messages.get(status_code, "Unknown Error")
    
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = status_code
    mock_response.ok = status_code < 400
    mock_response.text = error_message
    
    # JSONレスポンスを設定
    error_data = {
        "errors": [
            {
                "message": error_message,
                "code": error_code if error_code else status_code
            }
        ]
    }
    mock_response.json.return_value = error_data
    
    # ヘッダーを設定
    mock_response.headers = {}
    
    # レート制限エラーの場合はヘッダーを追加
    if status_code == 429:
        mock_response.headers.update(create_mock_rate_limit_headers(
            limit=300,
            remaining=0
        ))
    
    return mock_response


def create_mock_success_response(
    data: Dict[str, Any],
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Mock:
    """
    成功レスポンスのモックを作成する
    
    Args:
        data: レスポンスデータ
        status_code: HTTPステータスコード
        headers: レスポンスヘッダー
        
    Returns:
        モックレスポンスオブジェクト
    """
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = status_code
    mock_response.ok = True
    mock_response.json.return_value = data
    
    # ヘッダーを設定
    if headers is None:
        headers = create_mock_rate_limit_headers()
    mock_response.headers = headers
    
    return mock_response


def create_mock_network_error(error_type: str = "connection") -> Exception:
    """
    ネットワークエラーのモックを作成する
    
    Args:
        error_type: エラータイプ（"connection", "timeout", "ssl"）
        
    Returns:
        モック例外オブジェクト
    """
    error_types = {
        "connection": requests.exceptions.ConnectionError("接続エラー"),
        "timeout": requests.exceptions.Timeout("タイムアウト"),
        "ssl": requests.exceptions.SSLError("SSL証明書エラー"),
        "request": requests.exceptions.RequestException("リクエストエラー")
    }
    
    return error_types.get(error_type, requests.exceptions.RequestException("不明なエラー"))


def create_mock_file_content(
    content: str,
    encoding: str = "utf-8"
) -> Mock:
    """
    ファイル読み込みのモックを作成する
    
    Args:
        content: ファイルの内容
        encoding: エンコーディング
        
    Returns:
        モックファイルオブジェクト
    """
    mock_file = Mock()
    mock_file.read.return_value = content
    mock_file.__enter__.return_value = mock_file
    mock_file.__exit__.return_value = None
    
    return mock_file


def create_mock_oembed_response_with_rate_limit(
    html: str = None,
    remaining: int = 299
) -> tuple[Dict[str, Any], Dict[str, str]]:
    """
    レート制限情報付きのoEmbedレスポンスを作成する
    
    Args:
        html: 埋め込みHTML
        remaining: 残りのリクエスト数
        
    Returns:
        (oEmbedレスポンス, レート制限ヘッダー)のタプル
    """
    response_data = create_mock_oembed_response(html=html)
    headers = create_mock_rate_limit_headers(remaining=remaining)
    
    return response_data, headers


def create_mock_twitter_api_client(
    should_succeed: bool = True,
    html: str = None,
    error_type: Optional[str] = None
) -> Mock:
    """
    TwitterAPIClientのモックを作成する
    
    Args:
        should_succeed: 成功するかどうか
        html: 埋め込みHTML
        error_type: エラータイプ（"invalid_url", "network", "timeout", "rate_limit"）
        
    Returns:
        モックTwitterAPIClientオブジェクト
    """
    mock_client = Mock()
    
    if should_succeed:
        # 成功時のモック
        from src.models.oembed_response import OEmbedResponse
        
        response_data = create_mock_oembed_response(html=html)
        mock_client.get_oembed.return_value = OEmbedResponse(**response_data)
    else:
        # エラー時のモック
        from src.exceptions.errors import (
            InvalidURLError,
            NetworkError,
            APITimeoutError,
            RateLimitError
        )
        
        error_map = {
            "invalid_url": InvalidURLError("https://invalid.com"),
            "network": NetworkError(),
            "timeout": APITimeoutError(30.0),
            "rate_limit": RateLimitError()
        }
        
        error = error_map.get(error_type, NetworkError())
        mock_client.get_oembed.side_effect = error
    
    return mock_client


def create_mock_file_repository(
    should_succeed: bool = True,
    content: str = None,
    error_type: Optional[str] = None
) -> Mock:
    """
    FileRepositoryのモックを作成する
    
    Args:
        should_succeed: 成功するかどうか
        content: ファイルの内容
        error_type: エラータイプ（"not_found", "permission", "write"）
        
    Returns:
        モックFileRepositoryオブジェクト
    """
    mock_repo = Mock()
    
    if should_succeed:
        # 成功時のモック
        mock_repo.read_embed_code.return_value = content or "<blockquote class='twitter-tweet'></blockquote>"
        mock_repo.write_embed_code.return_value = None
        mock_repo.create_backup.return_value = None
    else:
        # エラー時のモック
        from src.exceptions.errors import FileWriteError
        
        error_map = {
            "not_found": FileNotFoundError("ファイルが見つかりません"),
            "permission": PermissionError("書き込み権限がありません"),
            "write": FileWriteError("test.html", "書き込みに失敗しました")
        }
        
        error = error_map.get(error_type, FileNotFoundError())
        mock_repo.read_embed_code.side_effect = error
        mock_repo.write_embed_code.side_effect = error
    
    return mock_repo
