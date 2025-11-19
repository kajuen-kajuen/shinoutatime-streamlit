"""
URL検証とツイートID抽出のユーティリティモジュール

このモジュールは、ツイートURLの検証とツイートIDの抽出機能を提供します。
"""

import re
from typing import Optional, Tuple


# ツイートURLのパターン（twitter.com、x.com、モバイル版をサポート）
TWEET_URL_PATTERNS = [
    r"https?://(?:www\.)?twitter\.com/\w+/status/(\d+)",
    r"https?://(?:www\.)?x\.com/\w+/status/(\d+)",
    r"https?://mobile\.twitter\.com/\w+/status/(\d+)",
    r"https?://(?:www\.)?twitter\.com/i/web/status/(\d+)",
]


def validate_tweet_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    ツイートURLの妥当性を検証
    
    Args:
        url: 検証するURL
        
    Returns:
        (妥当性, エラーメッセージ)
        妥当な場合は (True, None)
        不正な場合は (False, エラーメッセージ)
    """
    # 空文字列チェック
    if not url or not url.strip():
        return False, "URLが空です"
    
    # URL長さチェック（最大2048文字）
    if len(url) > 2048:
        return False, "URLが長すぎます（最大2048文字）"
    
    # パターンマッチング
    for pattern in TWEET_URL_PATTERNS:
        if re.match(pattern, url):
            return True, None
    
    return False, "無効なツイートURL形式です。twitter.comまたはx.comのツイートURLを指定してください"


def extract_tweet_id(url: str) -> Optional[str]:
    """
    ツイートURLからツイートIDを抽出
    
    Args:
        url: ツイートURL
        
    Returns:
        ツイートID（抽出失敗時はNone）
    """
    # 空文字列チェック
    if not url or not url.strip():
        return None
    
    # 各パターンで試行
    for pattern in TWEET_URL_PATTERNS:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    
    return None


def is_valid_tweet_id(tweet_id: str) -> bool:
    """
    ツイートIDの妥当性を検証
    
    Args:
        tweet_id: 検証するツイートID
        
    Returns:
        妥当性（数字のみで構成されているか）
    """
    if not tweet_id or not tweet_id.strip():
        return False
    
    return tweet_id.isdigit()
