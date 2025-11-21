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
    
    def test_find_similar_pairs_no_similar(self, checker):
        """類似したペアがない場合は空リストを返す"""
        strings = ["abc", "xyz", "123"]
        pairs = checker.find_similar_pairs(strings, threshold=0.9)
        assert len(pairs) == 0
    
    def test_find_similar_pairs_with_similar(self, checker):
        """類似したペアを検出"""
        # 要件9.1, 9.2: 類似したアーティスト名・曲名を検出
        strings = ["hello", "hallo", "world"]
        pairs = checker.find_similar_pairs(strings, threshold=0.7)
        
        # helloとhalloは類似しているはず
        assert len(pairs) > 0
        
        # 最初のペアを確認
        str1, str2, similarity = pairs[0]
        assert (str1 == "hello" and str2 == "hallo") or (str1 == "hallo" and str2 == "hello")
        assert similarity >= 0.7
    
    def test_find_similar_pairs_threshold(self, checker):
        """閾値によってフィルタリングされる"""
        # 要件9.4: 指定された閾値以上のペアのみを検出
        strings = ["hello", "hallo", "world"]
        
        # 低い閾値
        pairs_low = checker.find_similar_pairs(strings, threshold=0.5)
        
        # 高い閾値
        pairs_high = checker.find_similar_pairs(strings, threshold=0.95)
        
        # 低い閾値の方が多くのペアを検出するはず
        assert len(pairs_low) >= len(pairs_high)
    
    def test_find_similar_pairs_sorted_by_similarity(self, checker):
        """類似ペアは類似度の降順でソートされる"""
        strings = ["hello", "hallo", "hella", "world"]
        pairs = checker.find_similar_pairs(strings, threshold=0.5)
        
        if len(pairs) > 1:
            # 類似度が降順になっているか確認
            for i in range(len(pairs) - 1):
                assert pairs[i][2] >= pairs[i + 1][2]
    
    def test_find_similar_pairs_no_duplicates(self, checker):
        """同じ文字列のペアは検出されない"""
        strings = ["hello", "hello", "world"]
        pairs = checker.find_similar_pairs(strings, threshold=0.5)
        
        # "hello"と"hello"のペアは含まれないはず
        for str1, str2, _ in pairs:
            assert str1 != str2
