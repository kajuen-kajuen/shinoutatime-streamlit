"""
タイムスタンプ付きURLを生成するモジュール
"""
import re
import logging
from typing import Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

logger = logging.getLogger(__name__)


class URLGenerator:
    """
    タイムスタンプ付きYouTube URLを生成するクラス
    
    タイムスタンプを秒数に変換し、URLパラメータとして付加する。
    """
    
    def generate_timestamped_url(self, base_url: str, timestamp: str) -> str:
        """
        タイムスタンプ付きURLを生成
        
        Args:
            base_url: ベースとなるYouTube URL
            timestamp: タイムスタンプ文字列（"HH:MM:SS"、"H:MM:SS"、"MM:SS"形式）
            
        Returns:
            タイムスタンプパラメータ（&t=秒数）が付加されたURL
            
        Examples:
            >>> generator = URLGenerator()
            >>> generator.generate_timestamped_url("https://youtube.com/watch?v=abc", "1:23:45")
            'https://youtube.com/watch?v=abc&t=5025'
            >>> generator.generate_timestamped_url("https://youtube.com/watch?v=abc", "12:34")
            'https://youtube.com/watch?v=abc&t=754'
        """
        if not base_url or not timestamp:
            logger.warning(f"URLまたはタイムスタンプが空です: url={base_url}, timestamp={timestamp}")
            return base_url
        
        # タイムスタンプを秒数に変換
        seconds = self.parse_timestamp(timestamp)
        if seconds is None:
            logger.warning(f"タイムスタンプのパースに失敗しました: {timestamp}")
            return base_url
        
        # URLをパース
        parsed = urlparse(base_url)
        
        # 既存のクエリパラメータを取得
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        
        # タイムスタンプパラメータを追加（tパラメータ）
        query_params['t'] = [str(seconds)]
        
        # クエリパラメータを再構築（リストを単一の値に変換）
        query_string = urlencode({k: v[0] if isinstance(v, list) and len(v) == 1 else v 
                                  for k, v in query_params.items()}, doseq=True)
        
        # URLを再構築
        new_parsed = parsed._replace(query=query_string)
        return urlunparse(new_parsed)
    
    def parse_timestamp(self, timestamp: str) -> Optional[int]:
        """
        タイムスタンプ文字列を秒数に変換
        
        Args:
            timestamp: タイムスタンプ文字列（"HH:MM:SS"、"H:MM:SS"、"MM:SS"形式）
            
        Returns:
            秒数（変換失敗時はNone）
            
        Examples:
            >>> generator = URLGenerator()
            >>> generator.parse_timestamp("1:23:45")
            5025
            >>> generator.parse_timestamp("12:34")
            754
            >>> generator.parse_timestamp("01:02:03")
            3723
        """
        if not timestamp:
            return None
        
        # タイムスタンプのパターンをチェック
        # HH:MM:SS または H:MM:SS 形式
        pattern_hms = r'^(\d{1,2}):(\d{1,2}):(\d{1,2})$'
        # MM:SS 形式
        pattern_ms = r'^(\d{1,2}):(\d{1,2})$'
        
        match_hms = re.match(pattern_hms, timestamp)
        if match_hms:
            hours = int(match_hms.group(1))
            minutes = int(match_hms.group(2))
            seconds = int(match_hms.group(3))
            return hours * 3600 + minutes * 60 + seconds
        
        match_ms = re.match(pattern_ms, timestamp)
        if match_ms:
            minutes = int(match_ms.group(1))
            seconds = int(match_ms.group(2))
            return minutes * 60 + seconds
        
        logger.warning(f"タイムスタンプの形式が不正です: {timestamp}")
        return None
