"""
ユーティリティコンポーネントの手動テスト
"""
from src.utils.artist_sort_generator import ArtistSortGenerator
from src.utils.url_generator import URLGenerator
from src.utils.similarity_checker import SimilarityChecker


def test_artist_sort_generator():
    """ArtistSortGeneratorのテスト"""
    print("=== ArtistSortGenerator テスト ===")
    generator = ArtistSortGenerator()
    
    # 英数字のみ
    result1 = generator.generate("Vaundy")
    print(f"Vaundy -> {result1}")
    assert result1 == "Vaundy", f"期待: Vaundy, 実際: {result1}"
    
    # 日本語
    result2 = generator.generate("米津玄師")
    print(f"米津玄師 -> {result2}")
    # ひらがなに変換されているはず
    
    # 混在
    result3 = generator.generate("YOASOBI")
    print(f"YOASOBI -> {result3}")
    assert result3 == "YOASOBI", f"期待: YOASOBI, 実際: {result3}"
    
    print("✓ ArtistSortGenerator テスト完了\n")


def test_url_generator():
    """URLGeneratorのテスト"""
    print("=== URLGenerator テスト ===")
    generator = URLGenerator()
    
    # タイムスタンプのパース
    seconds1 = generator.parse_timestamp("1:23:45")
    print(f"1:23:45 -> {seconds1}秒")
    assert seconds1 == 5025, f"期待: 5025, 実際: {seconds1}"
    
    seconds2 = generator.parse_timestamp("12:34")
    print(f"12:34 -> {seconds2}秒")
    assert seconds2 == 754, f"期待: 754, 実際: {seconds2}"
    
    seconds3 = generator.parse_timestamp("01:02:03")
    print(f"01:02:03 -> {seconds3}秒")
    assert seconds3 == 3723, f"期待: 3723, 実際: {seconds3}"
    
    # URL生成
    url1 = generator.generate_timestamped_url("https://youtube.com/watch?v=abc", "1:23:45")
    print(f"URL生成: {url1}")
    assert "t=5025" in url1, f"t=5025が含まれていません: {url1}"
    
    # 既存のクエリパラメータがある場合
    url2 = generator.generate_timestamped_url("https://youtube.com/watch?v=abc&list=xyz", "12:34")
    print(f"URL生成（既存パラメータあり）: {url2}")
    assert "t=754" in url2, f"t=754が含まれていません: {url2}"
    assert "list=xyz" in url2, f"list=xyzが保持されていません: {url2}"
    
    print("✓ URLGenerator テスト完了\n")


def test_similarity_checker():
    """SimilarityCheckerのテスト"""
    print("=== SimilarityChecker テスト ===")
    checker = SimilarityChecker()
    
    # 完全一致
    sim1 = checker.calculate_similarity("hello", "hello")
    print(f"hello vs hello -> {sim1}")
    assert sim1 == 1.0, f"期待: 1.0, 実際: {sim1}"
    
    # 類似
    sim2 = checker.calculate_similarity("hello", "hallo")
    print(f"hello vs hallo -> {sim2}")
    assert 0.7 < sim2 < 1.0, f"類似度が範囲外: {sim2}"
    
    # 完全に異なる
    sim3 = checker.calculate_similarity("abc", "xyz")
    print(f"abc vs xyz -> {sim3}")
    assert sim3 == 0.0, f"期待: 0.0, 実際: {sim3}"
    
    # 類似ペアの検出
    strings = ["米津玄師", "米津玄帥", "YOASOBI", "yoasobi"]
    pairs = checker.find_similar_pairs(strings, threshold=0.85)
    print(f"類似ペア検出: {len(pairs)}件")
    for str1, str2, similarity in pairs:
        print(f"  {str1} vs {str2}: {similarity:.2f}")
    
    print("✓ SimilarityChecker テスト完了\n")


if __name__ == "__main__":
    test_artist_sort_generator()
    test_url_generator()
    test_similarity_checker()
    print("=== すべてのテスト完了 ===")
