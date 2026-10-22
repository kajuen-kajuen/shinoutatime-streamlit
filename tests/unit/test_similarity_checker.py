"""
SimilarityCheckerのユニットテスト
"""
import pytest
from src.utils.similarity_checker import SimilarityChecker


class TestSimilarityChecker:
    """SimilarityCheckerのテストクラス"""
    
    @pytest.fixture
    def checker(self):
        """テスト用のSimilarityCheckerインスタンス"""
        return SimilarityChecker()
    
    def test_calculate_similarity_identical_strings(self, checker):
        """完全に一致する文字列の類似度は1.0"""
        assert checker.calculate_similarity("hello", "hello") == 1.0
        assert checker.calculate_similarity("米津玄師", "米津玄師") == 1.0
        assert checker.calculate_similarity("", "") == 1.0
    
    def test_calculate_similarity_completely_different(self, checker):
        """完全に異なる文字列の類似度は0.0"""
        # 要件9.3: レーベンシュタイン距離を使用
        similarity = checker.calculate_similarity("abc", "xyz")
        assert similarity == 0.0
    
    def test_calculate_similarity_similar_strings(self, checker):
        """類似した文字列の類似度は0.0と1.0の間"""
        similarity = checker.calculate_similarity("hello", "hallo")
        assert 0.0 < similarity < 1.0
        
        similarity2 = checker.calculate_similarity("米津玄師", "米津玄帥")
        assert 0.0 < similarity2 < 1.0
    
    def test_calculate_similarity_symmetry(self, checker):
        """類似度計算は対称的（順序を入れ替えても同じ結果）"""
        # プロパティ12: 類似性チェックの対称性
        # 要件9.3: similarity(str1, str2) = similarity(str2, str1)
        sim1 = checker.calculate_similarity("hello", "hallo")
        sim2 = checker.calculate_similarity("hallo", "hello")
        assert sim1 == sim2
        
        sim3 = checker.calculate_similarity("米津玄師", "YOASOBI")
        sim4 = checker.calculate_similarity("YOASOBI", "米津玄師")
        assert sim3 == sim4
    
    def test_calculate_similarity_empty_strings(self, checker):
        """空文字列の処理"""
        assert checker.calculate_similarity("", "") == 1.0
        assert checker.calculate_similarity("hello", "") == 0.0
        assert checker.calculate_similarity("", "world") == 0.0
