"""
文字列の類似度を計算するモジュール
"""
import logging

try:
    import Levenshtein
except ImportError:
    Levenshtein = None

logger = logging.getLogger(__name__)


class SimilarityChecker:
    """
    レーベンシュタイン距離を使用して文字列の類似度を計算するクラス
    """
    
    def __init__(self):
        """
        SimilarityCheckerを初期化
        
        python-Levenshteinが利用できない場合は警告を出力する。
        """
        if Levenshtein is None:
            logger.warning("python-Levenshteinが利用できません。類似度計算が実行できません。")
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        2つの文字列の類似度を計算
        
        レーベンシュタイン距離を使用して、0.0（完全に異なる）から1.0（完全に一致）の
        範囲で類似度を返す。
        
        類似度 = 1.0 - (レーベンシュタイン距離 / max(len(str1), len(str2)))
        
        Args:
            str1: 比較する文字列1
            str2: 比較する文字列2
            
        Returns:
            類似度（0.0-1.0）。Levenshteinが利用できない場合は0.0
            
        Examples:
            >>> checker = SimilarityChecker()
            >>> checker.calculate_similarity("hello", "hello")
            1.0
            >>> checker.calculate_similarity("hello", "hallo")
            0.8
        """
        if Levenshtein is None:
            logger.warning("python-Levenshteinが利用できないため、類似度を0.0として返します")
            return 0.0
        
        if not str1 or not str2:
            # 空文字列の場合
            if str1 == str2:
                return 1.0
            return 0.0
        
        # レーベンシュタイン距離を計算
        distance = Levenshtein.distance(str1, str2)
        
        # 最大長を取得
        max_len = max(len(str1), len(str2))
        
        # 類似度を計算（0.0-1.0の範囲）
        if max_len == 0:
            return 1.0
        
        similarity = 1.0 - (distance / max_len)
        return similarity
