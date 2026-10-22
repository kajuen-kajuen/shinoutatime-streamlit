"""
設定管理モジュール

アプリケーション全体の設定を一元管理します。
"""

import os
import logging
from dataclasses import dataclass

# ロガーの設定
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """アプリケーション設定
    
    アプリケーション全体で使用される設定値を管理します。
    環境変数からの読み込みやデフォルト値の提供を行います。
    """
    
    # ファイルパス
    tweet_embed_code_path: str = "data/tweet_embed_code.html"
    tweet_height_path: str = "data/tweet_height.txt"
    css_file_path: str = "src/ui/styles/style.css"
    # データモデル v2 の TSV のディレクトリ(画面はここを読む)
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
        例: SHINOUTA_V2_DATA_DIR
        
        Returns:
            Config: 設定オブジェクト
        """
        logger.debug("環境変数から設定を読み込み中")
        
        config = cls(
            # ファイルパス
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
