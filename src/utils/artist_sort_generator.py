"""
アーティスト名からソート用読み仮名を生成するモジュール
"""
import re
import logging
from typing import Optional

try:
    import pykakasi
except ImportError:
    pykakasi = None

logger = logging.getLogger(__name__)


class ArtistSortGenerator:
    """
    アーティスト名からソート用の読み仮名を生成するクラス
    
    日本語が含まれる場合はひらがなに変換し、英数字のみの場合はそのまま返す。
    """
    
    def __init__(self):
        """
        ArtistSortGeneratorを初期化
        
        pykakasiが利用可能な場合は初期化する。
        """
        self._kakasi = None
        if pykakasi is not None:
            try:
                self._kakasi = pykakasi.kakasi()
            except Exception as e:
                logger.warning(f"pykakasiの初期化に失敗しました: {e}")
    
    def generate(self, artist_name: str) -> str:
        """
        アーティスト名からソート用アーティスト名を生成
        
        Args:
            artist_name: 元のアーティスト名
            
        Returns:
            ソート用アーティスト名（英数字のみの場合はそのまま、日本語が含まれる場合はひらがな）
            
        Examples:
            >>> generator = ArtistSortGenerator()
            >>> generator.generate("Vaundy")
            'Vaundy'
            >>> generator.generate("米津玄師")
            'よねづけんし'
        """
        if not artist_name:
            return artist_name
        
        # 英数字のみかチェック（スペース、ハイフン、アンダースコアなども許可）
        if self._is_ascii_only(artist_name):
            return artist_name
        
        # 日本語が含まれる場合は読み仮名に変換
        return self._convert_to_hiragana(artist_name)
    
    def _is_ascii_only(self, text: str) -> bool:
        """
        テキストが英数字と基本的な記号のみで構成されているかチェック
        
        Args:
            text: チェックするテキスト
            
        Returns:
            英数字と基本記号のみの場合True
        """
        # ASCII文字（英数字、スペース、基本的な記号）のみかチェック
        return all(ord(char) < 128 for char in text)
    
    def _convert_to_hiragana(self, text: str) -> str:
        """
        テキストをひらがなに変換
        
        Args:
            text: 変換するテキスト
            
        Returns:
            ひらがなに変換されたテキスト（変換失敗時は元のテキスト）
        """
        if self._kakasi is None:
            logger.warning(f"pykakasiが利用できないため、読み仮名の生成をスキップします: {text}")
            return text
        
        try:
            # pykakasiを使用してひらがなに変換
            result = self._kakasi.convert(text)
            # 各要素のhiraフィールドを結合
            hiragana = ''.join([item['hira'] for item in result])
            return hiragana
        except Exception as e:
            logger.warning(f"読み仮名の生成に失敗しました（元の名前を使用）: {text}, エラー: {e}")
            return text
