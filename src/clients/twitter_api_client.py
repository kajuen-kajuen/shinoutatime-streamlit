"""
Twitter APIクライアントモジュール

Twitter oEmbed APIとの通信を管理し、埋め込みコードを取得します。
"""

import logging
import requests
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

from src.models.oembed_response import OEmbedResponse, RateLimitInfo
from src.exceptions.errors import (
    NetworkError,
    APITimeoutError,
    RateLimitError,
    InvalidURLError
)
from src.utils.retry import retry


logger = logging.getLogger(__name__)


class TwitterAPIClient:
    """
    Twitter API クライアント
    
    Twitter oEmbed APIとの通信を管理し、ツイートの埋め込みコードを取得します。
    レート制限の管理とリトライ機能を提供します。
    """
    
    # oEmbed APIエンドポイント
    OEMBED_ENDPOINT = "https://publish.twitter.com/oembed"
    
    # デフォルトのタイムアウト時間（秒）
    DEFAULT_TIMEOUT = 30
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = DEFAULT_TIMEOUT
    ):
        """
        APIクライアントを初期化
        
        Args:
            api_key: API認証キー（oEmbed APIでは不要だが将来の拡張用）
            max_retries: 最大リトライ回数
            retry_delay: リトライ間隔（秒）
            timeout: リクエストタイムアウト時間（秒）
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self._rate_limit_info: Optional[RateLimitInfo] = None
        
        logger.info(
            f"TwitterAPIClientを初期化しました "
            f"(max_retries={max_retries}, retry_delay={retry_delay}, timeout={timeout})"
        )
    
    @retry(
        max_retries=3,
        base_delay=1.0,
        exceptions=(NetworkError, APITimeoutError)
    )
    def get_oembed(
        self,
        tweet_url: str,
        max_width: Optional[int] = None,
        hide_media: bool = False,
        hide_thread: bool = False,
        omit_script: bool = False,
        theme: Optional[str] = None
    ) -> OEmbedResponse:
        """
        oEmbed APIを使用して埋め込みコードを取得
        
        Args:
            tweet_url: ツイートURL
            max_width: 最大幅（ピクセル）
            hide_media: メディアを非表示にするか
            hide_thread: スレッドを非表示にするか
            omit_script: スクリプトタグを省略するか
            theme: テーマ（"light"または"dark"）
            
        Returns:
            oEmbed APIレスポンス
            
        Raises:
            InvalidURLError: URLが無効な場合
            NetworkError: ネットワークエラーが発生した場合
            APITimeoutError: タイムアウトが発生した場合
            RateLimitError: レート制限に達した場合
        """
        logger.info(f"oEmbed APIを呼び出します: {tweet_url}")
        
        # クエリパラメータを構築
        params = {"url": tweet_url}
        
        if max_width is not None:
            params["maxwidth"] = max_width
        if hide_media:
            params["hide_media"] = "true"
        if hide_thread:
            params["hide_thread"] = "true"
        if omit_script:
            params["omit_script"] = "true"
        if theme:
            params["theme"] = theme
        
        try:
            # APIリクエストを実行
            response = requests.get(
                self.OEMBED_ENDPOINT,
                params=params,
                timeout=self.timeout
            )
            
            # レート制限情報を更新
            self._update_rate_limit_info(response)
            
            # ステータスコードをチェック
            if response.status_code == 404:
                raise InvalidURLError(
                    tweet_url,
                    "ツイートが見つかりません。URLを確認してください"
                )
            elif response.status_code == 429:
                reset_time = self._get_rate_limit_reset_time(response)
                raise RateLimitError(
                    reset_time=reset_time,
                    message="APIレート制限に達しました"
                )
            elif response.status_code != 200:
                raise NetworkError(
                    f"APIリクエストが失敗しました (ステータスコード: {response.status_code})"
                )
            
            # レスポンスをパース
            data = response.json()
            
            # OEmbedResponseオブジェクトを作成
            oembed_response = OEmbedResponse(
                html=data.get("html", ""),
                width=data.get("width"),
                height=data.get("height"),
                type=data.get("type", "rich"),
                version=data.get("version", "1.0"),
                author_name=data.get("author_name"),
                author_url=data.get("author_url"),
                provider_name=data.get("provider_name", "Twitter"),
                provider_url=data.get("provider_url", "https://twitter.com"),
                cache_age=data.get("cache_age")
            )
            
            logger.info(f"埋め込みコードの取得に成功しました: {tweet_url}")
            return oembed_response
            
        except requests.exceptions.Timeout as e:
            logger.error(f"APIリクエストがタイムアウトしました: {tweet_url}")
            raise APITimeoutError(
                timeout_seconds=self.timeout,
                message="APIリクエストがタイムアウトしました"
            ) from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"ネットワーク接続エラーが発生しました: {tweet_url}")
            raise NetworkError(
                message="ネットワーク接続エラーが発生しました",
                original_error=e
            ) from e
        except requests.exceptions.RequestException as e:
            logger.error(f"APIリクエストエラーが発生しました: {tweet_url}")
            raise NetworkError(
                message="APIリクエストエラーが発生しました",
                original_error=e
            ) from e
        except ValueError as e:
            logger.error(f"APIレスポンスのパースに失敗しました: {tweet_url}")
            raise NetworkError(
                message="APIレスポンスの形式が不正です",
                original_error=e
            ) from e
    
    def check_rate_limit(self) -> Optional[RateLimitInfo]:
        """
        レート制限の状態を確認
        
        Returns:
            レート制限情報（情報が利用できない場合はNone）
        """
        return self._rate_limit_info
    
    def _update_rate_limit_info(self, response: requests.Response) -> None:
        """
        レスポンスヘッダーからレート制限情報を更新
        
        Args:
            response: APIレスポンス
        """
        try:
            # レート制限ヘッダーを取得
            limit = response.headers.get("x-rate-limit-limit")
            remaining = response.headers.get("x-rate-limit-remaining")
            reset = response.headers.get("x-rate-limit-reset")
            
            if limit and remaining and reset:
                self._rate_limit_info = RateLimitInfo(
                    limit=int(limit),
                    remaining=int(remaining),
                    reset_time=datetime.fromtimestamp(int(reset))
                )
                
                logger.debug(
                    f"レート制限情報を更新しました: "
                    f"残り {self._rate_limit_info.remaining}/{self._rate_limit_info.limit}"
                )
        except (ValueError, TypeError) as e:
            logger.warning(f"レート制限情報の解析に失敗しました: {e}")
    
    def _get_rate_limit_reset_time(self, response: requests.Response) -> Optional[str]:
        """
        レート制限リセット時刻を取得
        
        Args:
            response: APIレスポンス
            
        Returns:
            リセット時刻の文字列表現（取得できない場合はNone）
        """
        try:
            reset = response.headers.get("x-rate-limit-reset")
            if reset:
                reset_datetime = datetime.fromtimestamp(int(reset))
                return reset_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError) as e:
            logger.warning(f"レート制限リセット時刻の解析に失敗しました: {e}")
        
        return None
