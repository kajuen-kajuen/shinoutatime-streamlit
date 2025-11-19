"""
データモデルパッケージ

Twitter埋め込みコード取得システムのデータモデルを提供します。
"""

from src.models.embed_result import EmbedCodeResult, MultipleEmbedCodeResult
from src.models.oembed_response import OEmbedResponse, RateLimitInfo

__all__ = [
    "EmbedCodeResult",
    "MultipleEmbedCodeResult",
    "OEmbedResponse",
    "RateLimitInfo",
]
