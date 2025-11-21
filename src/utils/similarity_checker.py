"""
文字列の類似度を計算するモジュール
"""
import logging
from typing import List, Tuple

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
    
    def find_similar_pairs(
        self, 
        strings: List[str], 
        threshold: float = 0.85
    ) -> List[Tuple[str, str, float]]:
        """
        文字列リストから類似度が閾値以上のペアを検出
        
        Args:
            strings: 比較する文字列のリスト
            threshold: 類似度の閾値（0.0-1.0、デフォルト: 0.85）
            
        Returns:
            類似ペアのリスト。各要素は(str1, str2, similarity)のタプル
            
        Examples:
            >>> checker = SimilarityChecker()
            >>> checker.find_similar_pairs(["hello", "hallo", "world"], 0.8)
            [('hello', 'hallo', 0.8)]
        """
        if Levenshtein is None:
            logger.warning("python-Levenshteinが利用できないため、空のリストを返します")
            return []
        
        similar_pairs = []
        
        # すべてのペアを比較
        for i in range(len(strings)):
            for j in range(i + 1, len(strings)):
                str1 = strings[i]
                str2 = strings[j]
                
                # 同じ文字列はスキップ
                if str1 == str2:
                    continue
                
                # 類似度を計算
                similarity = self.calculate_similarity(str1, str2)
                
                # 閾値以上の場合はリストに追加
                if similarity >= threshold:
                    similar_pairs.append((str1, str2, similarity))
        
        # 類似度の降順でソート
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        
        return similar_pairs
