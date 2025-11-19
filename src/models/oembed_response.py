"""
Twitter oEmbed APIレスポンスのデータモデル

このモジュールは、Twitter oEmbed APIのレスポンスとレート制限情報を表すデータクラスを提供します。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OEmbedResponse:
    """
    oEmbed APIレスポンス
    
    Twitter oEmbed APIから返されるレスポンスデータを表します。
    
    Attributes:
        html: 埋め込み用HTMLコード
        width: 埋め込みの幅（ピクセル、オプション）
        height: 埋め込みの高さ（ピクセル、オプション）
        type: oEmbedタイプ（通常は"rich"）
        version: oEmbedバージョン（通常は"1.0"）
        author_name: ツイート作成者の名前（オプション）
        author_url: ツイート作成者のURL（オプション）
        provider_name: プロバイダー名（通常は"Twitter"）
        provider_url: プロバイダーURL（通常は"https://twitter.com"）
        cache_age: キャッシュ有効期間（秒、オプション）
    """
    html: str
    width: Optional[int] = None
    height: Optional[int] = None
    type: str = "rich"
    version: str = "1.0"
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    provider_name: str = "Twitter"
    provider_url: str = "https://twitter.com"
    cache_age: Optional[int] = None


@dataclass
class RateLimitInfo:
    """
    レート制限情報
    
    APIのレート制限に関する情報を表します。
    
    Attributes:
        limit: レート制限の上限値
        remaining: 残りの利用可能回数
        reset_time: レート制限がリセットされる日時
    """
    limit: int
    remaining: int
    reset_time: datetime
