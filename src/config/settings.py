"""
設定管理モジュール

アプリケーション全体の設定を一元管理します。
"""

import os
from dataclasses import dataclass
from typing import Optional


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
    css_file_path: str = "style.css"
    
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
        return cls(
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
                "style.css"
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
    
    def validate(self) -> bool:
        """設定値を検証する
        
        設定値が有効な範囲内にあるかを検証します。
        
        Returns:
            bool: 検証成功時True
        
        Raises:
            ConfigurationError: 設定値が不正な場合
        """
        from src.exceptions.errors import ConfigurationError
        
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
        
        return True
