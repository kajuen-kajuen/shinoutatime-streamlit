"""
埋め込みコード取得結果のデータモデル

このモジュールは、Twitter埋め込みコード取得の結果を表すデータクラスを提供します。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class EmbedCodeResult:
    """
    埋め込みコード取得結果
    
    単一のツイートに対する埋め込みコード取得の結果を表します。
    
    Attributes:
        success: 取得が成功したかどうか
        tweet_url: ツイートURL
        embed_code: 取得した埋め込みHTMLコード（失敗時はNone）
        height: ツイートの推奨表示高さ（ピクセル、失敗時はNone）
        error_message: エラーメッセージ（成功時はNone）
        timestamp: 取得日時
    """
    success: bool
    tweet_url: str
    embed_code: Optional[str] = None
    height: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MultipleEmbedCodeResult:
    """
    複数の埋め込みコード取得結果
    
    複数のツイートに対する埋め込みコード取得の結果を表します。
    
    Attributes:
        total_count: 処理した総ツイート数
        success_count: 成功したツイート数
        failure_count: 失敗したツイート数
        combined_embed_code: 連結された埋め込みHTMLコード
        max_height: 全ツイートの中で最大の表示高さ（ピクセル）
        results: 個別の取得結果のリスト
        failed_urls: 失敗したツイートURLのリスト
    """
    total_count: int
    success_count: int
    failure_count: int
    combined_embed_code: str
    max_height: int
    results: List[EmbedCodeResult]
    failed_urls: List[str]
