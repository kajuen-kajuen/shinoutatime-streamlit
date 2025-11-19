"""
Twitter埋め込みコード取得サービス

このモジュールは、ツイートURLから埋め込みコードを取得し、ファイルに保存する
ビジネスロジックを提供します。
"""

import logging
from typing import List, Optional, Tuple

from src.clients.twitter_api_client import TwitterAPIClient
from src.repositories.file_repository import FileRepository
from src.models.embed_result import EmbedCodeResult, MultipleEmbedCodeResult
from src.utils.validators import validate_tweet_url, extract_tweet_id
from src.utils.html_validator import validate_twitter_embed_code
from src.exceptions.errors import InvalidURLError


class TwitterEmbedService:
    """
    Twitter埋め込みコード取得サービス
    
    ツイートURLから埋め込みコードを取得し、ファイルに保存する機能を提供します。
    単一ツイートと複数ツイートの両方に対応しています。
    
    Attributes:
        api_client: Twitter APIクライアント
        file_repo: ファイルリポジトリ
        logger: ロガー
    """
    
    def __init__(
        self,
        api_client: TwitterAPIClient,
        file_repo: FileRepository,
        logger: Optional[logging.Logger] = None
    ):
        """
        サービスを初期化
        
        Args:
            api_client: Twitter APIクライアント
            file_repo: ファイルリポジトリ
            logger: ロガー（Noneの場合はデフォルトロガーを使用）
        """
        self.api_client = api_client
        self.file_repo = file_repo
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_tweet_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        ツイートURLの妥当性を検証
        
        Args:
            url: 検証するURL
            
        Returns:
            (妥当性, エラーメッセージ)
            妥当な場合は (True, None)
            不正な場合は (False, エラーメッセージ)
        """
        return validate_tweet_url(url)
    
    def extract_tweet_id(self, url: str) -> Optional[str]:
        """
        ツイートURLからツイートIDを抽出
        
        Args:
            url: ツイートURL
            
        Returns:
            ツイートID（抽出失敗時はNone）
        """
        return extract_tweet_id(url)
    
    def fetch_embed_code(self, tweet_url: str) -> EmbedCodeResult:
        """
        単一のツイートの埋め込みコードを取得
        
        Args:
            tweet_url: ツイートURL
            
        Returns:
            取得結果（成功/失敗、埋め込みコード、エラーメッセージ）
        """
        self.logger.info(f"埋め込みコード取得を開始: {tweet_url}")
        
        # URL検証
        is_valid, error_message = self.validate_tweet_url(tweet_url)
        if not is_valid:
            self.logger.warning(f"URL検証失敗: {tweet_url} - {error_message}")
            return EmbedCodeResult(
                success=False,
                tweet_url=tweet_url,
                error_message=error_message
            )
        
        # ツイートID抽出
        tweet_id = self.extract_tweet_id(tweet_url)
        if not tweet_id:
            error_msg = "ツイートIDの抽出に失敗しました"
            self.logger.error(f"{error_msg}: {tweet_url}")
            return EmbedCodeResult(
                success=False,
                tweet_url=tweet_url,
                error_message=error_msg
            )
        
        try:
            # oEmbed APIを使用して埋め込みコードを取得
            oembed_response = self.api_client.get_oembed(tweet_url)
            
            # HTML検証を実行（要件6.1）
            is_valid, validation_messages = validate_twitter_embed_code(oembed_response.html)
            
            # 検証結果をログに記録
            if is_valid and validation_messages:
                # 警告がある場合
                for warning in validation_messages:
                    self.logger.warning(f"HTML検証警告: {warning}")
            elif not is_valid:
                # エラーがある場合（要件6.2）
                for error in validation_messages:
                    self.logger.error(f"HTML検証エラー: {error}")
            
            self.logger.info(
                f"埋め込みコード取得成功: {tweet_url} "
                f"(高さ: {oembed_response.height}px)"
            )
            
            return EmbedCodeResult(
                success=True,
                tweet_url=tweet_url,
                embed_code=oembed_response.html,
                height=oembed_response.height
            )
            
        except Exception as e:
            error_msg = f"埋め込みコード取得エラー: {str(e)}"
            self.logger.error(f"{error_msg}: {tweet_url}", exc_info=True)
            return EmbedCodeResult(
                success=False,
                tweet_url=tweet_url,
                error_message=error_msg
            )
    
    def fetch_multiple_embed_codes(
        self,
        tweet_urls: List[str]
    ) -> MultipleEmbedCodeResult:
        """
        複数のツイートの埋め込みコードを取得
        
        Args:
            tweet_urls: ツイートURLのリスト
            
        Returns:
            取得結果（成功数、失敗数、埋め込みコード、失敗リスト）
        """
        self.logger.info(f"複数ツイートの埋め込みコード取得を開始: {len(tweet_urls)}件")
        
        results: List[EmbedCodeResult] = []
        success_count = 0
        failure_count = 0
        failed_urls: List[str] = []
        embed_codes: List[str] = []
        heights: List[int] = []
        
        # 各URLを順次処理
        for i, url in enumerate(tweet_urls, 1):
            self.logger.info(f"処理中 ({i}/{len(tweet_urls)}): {url}")
            
            result = self.fetch_embed_code(url)
            results.append(result)
            
            if result.success:
                success_count += 1
                if result.embed_code:
                    embed_codes.append(result.embed_code)
                if result.height:
                    heights.append(result.height)
            else:
                failure_count += 1
                failed_urls.append(url)
        
        # 埋め込みコードを連結
        combined_embed_code = "\n\n".join(embed_codes)
        
        # 最大高さを選択（デフォルトは850）
        max_height = max(heights) if heights else 850
        
        self.logger.info(
            f"複数ツイート取得完了: 成功={success_count}, 失敗={failure_count}, "
            f"最大高さ={max_height}px"
        )
        
        return MultipleEmbedCodeResult(
            total_count=len(tweet_urls),
            success_count=success_count,
            failure_count=failure_count,
            combined_embed_code=combined_embed_code,
            max_height=max_height,
            results=results,
            failed_urls=failed_urls
        )
    
    def save_embed_code(
        self,
        embed_code: str,
        create_backup: bool = True
    ) -> bool:
        """
        埋め込みコードをファイルに保存
        
        Args:
            embed_code: 埋め込みHTMLコード
            create_backup: バックアップを作成するか
            
        Returns:
            保存成功の可否
        """
        self.logger.info(
            f"埋め込みコード保存を開始 (バックアップ: {create_backup})"
        )
        
        try:
            # バックアップ作成
            if create_backup:
                backup_path = self.file_repo.create_backup()
                if backup_path:
                    self.logger.info(f"バックアップ作成成功: {backup_path}")
                else:
                    self.logger.warning("バックアップ作成に失敗しましたが、処理を継続します")
            
            # ファイルに書き込み
            success = self.file_repo.write_embed_code(embed_code)
            
            if success:
                self.logger.info("埋め込みコード保存成功")
            else:
                self.logger.error("埋め込みコード保存失敗")
            
            return success
            
        except Exception as e:
            self.logger.error(f"埋め込みコード保存エラー: {str(e)}", exc_info=True)
            return False
