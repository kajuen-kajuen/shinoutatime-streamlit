"""
設定管理モジュール

アプリケーション全体の設定を一元管理します。
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional

# ロガーの設定
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """アプリケーション設定
    
    アプリケーション全体で使用される設定値を管理します。
    環境変数からの読み込みやデフォルト値の提供を行います。
    """
    
    # ファイルパス
    lives_file_path: str = "data/M_YT_LIVE.TSV"
    songs_file_path: str = "data/M_YT_LIVE_TIMESTAMP.TSV"
    song_list_file_path: str = "data/V_SONG_LIST.TSV"
    tweet_embed_code_path: str = "data/tweet_embed_code.html"
    tweet_height_path: str = "data/tweet_height.txt"
    css_file_path: str = "src/ui/styles/style.css"
    # データモデル v2 の TSV のディレクトリ(画面はここを読む。上の3つの v1 の TSV は参照用)
    v2_data_dir: str = "data/v2"

    # 表示設定
    initial_display_limit: int = 25
    display_increment: int = 25
    
    # ページ設定
    page_title: str = "しのうたタイム"
    page_icon: str = "👻"
    layout: str = "wide"
    
    # パフォーマンス設定
    enable_cache: bool = True
    cache_ttl: int = 3600  # 秒
    
    @classmethod
    def from_env(cls) -> 'Config':
        """環境変数から設定を読み込む
        
        環境変数が設定されている場合はその値を使用し、
        設定されていない場合はデフォルト値を使用します。
        
        環境変数名の形式: SHINOUTA_<設定名の大文字>
        例: SHINOUTA_LIVES_FILE_PATH
        
        Returns:
            Config: 設定オブジェクト
        """
        logger.debug("環境変数から設定を読み込み中")
        
        config = cls(
            # ファイルパス
            lives_file_path=os.getenv(
                "SHINOUTA_LIVES_FILE_PATH",
                "data/M_YT_LIVE.TSV"
            ),
            songs_file_path=os.getenv(
                "SHINOUTA_SONGS_FILE_PATH",
                "data/M_YT_LIVE_TIMESTAMP.TSV"
            ),
            song_list_file_path=os.getenv(
                "SHINOUTA_SONG_LIST_FILE_PATH",
                "data/V_SONG_LIST.TSV"
            ),
            tweet_embed_code_path=os.getenv(
                "SHINOUTA_TWEET_EMBED_CODE_PATH",
                "data/tweet_embed_code.html"
            ),
            tweet_height_path=os.getenv(
                "SHINOUTA_TWEET_HEIGHT_PATH",
                "data/tweet_height.txt"
            ),
            css_file_path=os.getenv(
                "SHINOUTA_CSS_FILE_PATH",
                "src/ui/styles/style.css"
            ),
            v2_data_dir=os.getenv(
                "SHINOUTA_V2_DATA_DIR",
                "data/v2"
            ),
            # 表示設定
            initial_display_limit=int(os.getenv(
                "SHINOUTA_INITIAL_DISPLAY_LIMIT",
                "25"
            )),
            display_increment=int(os.getenv(
                "SHINOUTA_DISPLAY_INCREMENT",
                "25"
            )),
            # ページ設定
            page_title=os.getenv(
                "SHINOUTA_PAGE_TITLE",
                "しのうたタイム"
            ),
            page_icon=os.getenv(
                "SHINOUTA_PAGE_ICON",
                "👻"
            ),
            layout=os.getenv(
                "SHINOUTA_LAYOUT",
                "wide"
            ),
            # パフォーマンス設定
            enable_cache=os.getenv(
                "SHINOUTA_ENABLE_CACHE",
                "true"
            ).lower() in ("true", "1", "yes"),
            cache_ttl=int(os.getenv(
                "SHINOUTA_CACHE_TTL",
                "3600"
            ))
        )
        
        logger.debug("環境変数からの設定読み込みが完了しました")
        logger.debug(f"設定内容: enable_cache={config.enable_cache}, cache_ttl={config.cache_ttl}")
        
        return config
    
    def validate(self) -> bool:
        """設定値を検証する
        
        設定値が有効な範囲内にあるかを検証します。
        
        Returns:
            bool: 検証成功時True
        
        Raises:
            ConfigurationError: 設定値が不正な場合
        """
        from src.exceptions.errors import ConfigurationError
        
        logger.debug("設定値を検証中")
        
        # ファイルパスの検証（空でないこと）
        if not self.lives_file_path:
            raise ConfigurationError(
                "lives_file_path",
                "配信データファイルパスが空です"
            )
        if not self.songs_file_path:
            raise ConfigurationError(
                "songs_file_path",
                "楽曲データファイルパスが空です"
            )
        if not self.song_list_file_path:
            raise ConfigurationError(
                "song_list_file_path",
                "楽曲リストファイルパスが空です"
            )
        
        # 表示設定の検証（正の整数であること）
        if self.initial_display_limit <= 0:
            raise ConfigurationError(
                "initial_display_limit",
                f"初期表示件数は正の整数である必要があります: {self.initial_display_limit}"
            )
        if self.display_increment <= 0:
            raise ConfigurationError(
                "display_increment",
                f"表示増分は正の整数である必要があります: {self.display_increment}"
            )
        
        # ページ設定の検証
        if not self.page_title:
            raise ConfigurationError(
                "page_title",
                "ページタイトルが空です"
            )
        
        valid_layouts = ["centered", "wide"]
        if self.layout not in valid_layouts:
            raise ConfigurationError(
                "layout",
                f"レイアウトは {valid_layouts} のいずれかである必要があります: {self.layout}"
            )
        
        # パフォーマンス設定の検証
        if self.cache_ttl < 0:
            raise ConfigurationError(
                "cache_ttl",
                f"キャッシュTTLは0以上である必要があります: {self.cache_ttl}"
            )
        
        logger.debug("設定値の検証が完了しました")
        return True


@dataclass
class TwitterAPICredentials:
    """Twitter API認証情報
    
    Twitter APIへのアクセスに必要な認証情報を管理します。
    セキュリティのため、認証情報はログに出力されません。
    """
    
    api_key: Optional[str] = field(default=None, repr=False)
    api_secret: Optional[str] = field(default=None, repr=False)
    
    def __repr__(self) -> str:
        """文字列表現（認証情報を隠蔽）
        
        Returns:
            str: 認証情報を含まない文字列表現
        """
        return "TwitterAPICredentials(api_key=***, api_secret=***)"
    
    def __str__(self) -> str:
        """文字列表現（認証情報を隠蔽）
        
        Returns:
            str: 認証情報を含まない文字列表現
        """
        return self.__repr__()
    
    @classmethod
    def from_env(cls) -> 'TwitterAPICredentials':
        """環境変数から認証情報を読み込む
        
        環境変数TWITTER_API_KEYとTWITTER_API_SECRETから
        認証情報を読み込みます。
        
        Returns:
            TwitterAPICredentials: 認証情報オブジェクト
        
        Raises:
            ConfigurationError: 必須の認証情報が設定されていない場合
        """
        from src.exceptions.errors import ConfigurationError
        
        logger.info("環境変数からTwitter API認証情報を読み込み中")
        
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        
        # 注: Twitter oEmbed APIは認証不要ですが、
        # 将来の拡張のために認証情報の読み込み機能を提供します
        # 現時点では認証情報が未設定でも警告のみで処理を継続します
        
        if not api_key and not api_secret:
            logger.warning(
                "Twitter API認証情報が環境変数に設定されていません。"
                "oEmbed APIは認証不要ですが、将来の拡張のために設定を推奨します。"
            )
        elif not api_key:
            logger.warning("TWITTER_API_KEYが環境変数に設定されていません")
        elif not api_secret:
            logger.warning("TWITTER_API_SECRETが環境変数に設定されていません")
        else:
            logger.info("Twitter API認証情報の読み込みが完了しました")
        
        return cls(api_key=api_key, api_secret=api_secret)
    
    def validate(self, require_credentials: bool = False) -> bool:
        """認証情報を検証する
        
        認証情報が有効な形式であるかを検証します。
        
        Args:
            require_credentials: 認証情報を必須とするか（デフォルト: False）
        
        Returns:
            bool: 検証成功時True
        
        Raises:
            ConfigurationError: 認証情報が不正な場合
        """
        from src.exceptions.errors import ConfigurationError
        
        logger.info("Twitter API認証情報を検証中")
        
        # 認証情報が必須の場合のチェック
        if require_credentials:
            if not self.api_key:
                raise ConfigurationError(
                    "TWITTER_API_KEY",
                    "Twitter API認証キーが設定されていません。"
                    "環境変数TWITTER_API_KEYを設定してください。"
                )
            if not self.api_secret:
                raise ConfigurationError(
                    "TWITTER_API_SECRET",
                    "Twitter APIシークレットキーが設定されていません。"
                    "環境変数TWITTER_API_SECRETを設定してください。"
                )
        
        # 認証情報が設定されている場合の形式チェック
        if self.api_key is not None:
            if not isinstance(self.api_key, str) or len(self.api_key.strip()) == 0:
                raise ConfigurationError(
                    "TWITTER_API_KEY",
                    "Twitter API認証キーの形式が不正です"
                )
        
        if self.api_secret is not None:
            if not isinstance(self.api_secret, str) or len(self.api_secret.strip()) == 0:
                raise ConfigurationError(
                    "TWITTER_API_SECRET",
                    "Twitter APIシークレットキーの形式が不正です"
                )
        
        logger.info("Twitter API認証情報の検証が完了しました")
        return True
    
    def is_configured(self) -> bool:
        """認証情報が設定されているかを確認
        
        Returns:
            bool: 認証情報が設定されている場合True
        """
        return self.api_key is not None and self.api_secret is not None
    
    def mask_credentials(self) -> dict:
        """認証情報をマスクした辞書を返す
        
        ログ出力やデバッグ用に、認証情報をマスクした辞書を返します。
        
        Returns:
            dict: マスクされた認証情報
        """
        return {
            "api_key": "***" if self.api_key else None,
            "api_secret": "***" if self.api_secret else None,
            "is_configured": self.is_configured()
        }


@dataclass
class TwitterEmbedConfig:
    """Twitter埋め込みコード取得システムの設定
    
    Twitter埋め込みコード取得機能に関する設定を管理します。
    """
    
    # ファイルパス
    embed_code_path: str = "data/tweet_embed_code.html"
    height_path: str = "data/tweet_height.txt"
    backup_dir: str = "data/backups"
    
    # ログ設定
    log_level: str = "INFO"
    log_file: str = "logs/twitter_embed.log"
    
    # リトライ設定
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # API設定
    api_timeout: int = 30
    
    # デフォルト値
    default_height: int = 850
    
    # UI設定
    enable_admin_page: bool = False  # 管理ページを表示するか(既定は出さない。手元で使うときだけ True)
    
    # 認証情報
    credentials: TwitterAPICredentials = field(default_factory=TwitterAPICredentials)
    
    @classmethod
    def from_env(cls) -> 'TwitterEmbedConfig':
        """環境変数から設定を読み込む
        
        環境変数が設定されている場合はその値を使用し、
        設定されていない場合はデフォルト値を使用します。
        
        Returns:
            TwitterEmbedConfig: 設定オブジェクト
        """
        logger.info("環境変数からTwitter埋め込み設定を読み込み中")
        
        # 認証情報を読み込む
        credentials = TwitterAPICredentials.from_env()
        
        config = cls(
            # ファイルパス
            embed_code_path=os.getenv(
                "TWITTER_EMBED_CODE_PATH",
                "data/tweet_embed_code.html"
            ),
            height_path=os.getenv(
                "TWITTER_HEIGHT_PATH",
                "data/tweet_height.txt"
            ),
            backup_dir=os.getenv(
                "TWITTER_BACKUP_DIR",
                "data/backups"
            ),
            # ログ設定
            log_level=os.getenv(
                "TWITTER_EMBED_LOG_LEVEL",
                "INFO"
            ),
            log_file=os.getenv(
                "TWITTER_EMBED_LOG_FILE",
                "logs/twitter_embed.log"
            ),
            # リトライ設定
            max_retries=int(os.getenv(
                "TWITTER_API_MAX_RETRIES",
                "3"
            )),
            retry_delay=float(os.getenv(
                "TWITTER_API_RETRY_DELAY",
                "1.0"
            )),
            # API設定
            api_timeout=int(os.getenv(
                "TWITTER_API_TIMEOUT",
                "30"
            )),
            # デフォルト値
            default_height=int(os.getenv(
                "TWITTER_DEFAULT_HEIGHT",
                "850"
            )),
            # UI設定
            enable_admin_page=os.getenv(
                "TWITTER_ENABLE_ADMIN_PAGE",
                "false"
            ).lower() in ("true", "1", "yes"),
            # 認証情報
            credentials=credentials
        )
        
        logger.info("Twitter埋め込み設定の読み込みが完了しました")
        # 認証情報をマスクしてログ出力
        logger.debug(f"認証情報の状態: {config.credentials.mask_credentials()}")
        
        return config
    
    def validate(self, require_credentials: bool = False) -> bool:
        """設定値を検証する
        
        設定値が有効な範囲内にあるかを検証します。
        
        Args:
            require_credentials: 認証情報を必須とするか（デフォルト: False）
        
        Returns:
            bool: 検証成功時True
        
        Raises:
            ConfigurationError: 設定値が不正な場合
        """
        from src.exceptions.errors import ConfigurationError
        
        logger.info("Twitter埋め込み設定を検証中")
        
        # ファイルパスの検証
        if not self.embed_code_path:
            raise ConfigurationError(
                "embed_code_path",
                "埋め込みコードファイルパスが空です"
            )
        if not self.height_path:
            raise ConfigurationError(
                "height_path",
                "高さ設定ファイルパスが空です"
            )
        if not self.backup_dir:
            raise ConfigurationError(
                "backup_dir",
                "バックアップディレクトリパスが空です"
            )
        
        # リトライ設定の検証
        if self.max_retries < 0:
            raise ConfigurationError(
                "max_retries",
                f"最大リトライ回数は0以上である必要があります: {self.max_retries}"
            )
        if self.retry_delay < 0:
            raise ConfigurationError(
                "retry_delay",
                f"リトライ遅延時間は0以上である必要があります: {self.retry_delay}"
            )
        
        # API設定の検証
        if self.api_timeout <= 0:
            raise ConfigurationError(
                "api_timeout",
                f"APIタイムアウトは正の整数である必要があります: {self.api_timeout}"
            )
        
        # デフォルト値の検証
        if self.default_height <= 0:
            raise ConfigurationError(
                "default_height",
                f"デフォルト高さは正の整数である必要があります: {self.default_height}"
            )
        
        # ログレベルの検証
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ConfigurationError(
                "log_level",
                f"ログレベルは {valid_log_levels} のいずれかである必要があります: {self.log_level}"
            )
        
        # 認証情報の検証
        self.credentials.validate(require_credentials=require_credentials)
        
        logger.info("Twitter埋め込み設定の検証が完了しました")
        return True
