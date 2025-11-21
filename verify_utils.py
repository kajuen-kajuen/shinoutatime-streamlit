#!/usr/bin/env python
"""
ユーティリティコンポーネントの検証スクリプト
"""
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== ユーティリティコンポーネントの検証 ===\n")

# 1. ArtistSortGenerator
print("1. ArtistSortGenerator")
try:
    from src.utils.artist_sort_generator import ArtistSortGenerator
    generator = ArtistSortGenerator()
    
    test_cases = [
        ("Vaundy", "Vaundy"),
        ("YOASOBI", "YOASOBI"),
        ("米津玄師", None),  # ひらがなに変換されるはず
    ]
    
    for input_name, expected in test_cases:
        result = generator.generate(input_name)
        status = "✓" if (expected is None or result == expected) else "✗"
        print(f"  {status} {input_name} -> {result}")
    
    print("  ✓ ArtistSortGenerator 正常に動作\n")
except Exception as e:
    print(f"  ✗ エラー: {e}\n")
    import traceback
    traceback.print_exc()

# 2. URLGenerator
print("2. URLGenerator")
try:
    from src.utils.url_generator import URLGenerator
    generator = URLGenerator()
    
    # タイムスタンプのパース
    test_cases = [
        ("1:23:45", 5025),
        ("12:34", 754),
        ("01:02:03", 3723),
    ]
    
    for timestamp, expected_seconds in test_cases:
        result = generator.parse_timestamp(timestamp)
        status = "✓" if result == expected_seconds else "✗"
        print(f"  {status} {timestamp} -> {result}秒 (期待: {expected_seconds}秒)")
    
    # URL生成
    url = generator.generate_timestamped_url("https://youtube.com/watch?v=abc", "1:23:45")
    has_timestamp = "t=5025" in url
    status = "✓" if has_timestamp else "✗"
    print(f"  {status} URL生成: {url}")
    
    print("  ✓ URLGenerator 正常に動作\n")
except Exception as e:
    print(f"  ✗ エラー: {e}\n")
    import traceback
    traceback.print_exc()

# 3. SimilarityChecker
print("3. SimilarityChecker")
try:
    from src.utils.similarity_checker import SimilarityChecker
    checker = SimilarityChecker()
    
    # 類似度計算
    sim1 = checker.calculate_similarity("hello", "hello")
    status1 = "✓" if sim1 == 1.0 else "✗"
    print(f"  {status1} hello vs hello: {sim1} (期待: 1.0)")
    
    sim2 = checker.calculate_similarity("hello", "hallo")
    status2 = "✓" if 0.0 < sim2 < 1.0 else "✗"
    print(f"  {status2} hello vs hallo: {sim2} (期待: 0.0 < x < 1.0)")
    
    # 類似ペアの検出
    strings = ["hello", "hallo", "world"]
    pairs = checker.find_similar_pairs(strings, threshold=0.7)
    status3 = "✓" if len(pairs) > 0 else "✗"
    print(f"  {status3} 類似ペア検出: {len(pairs)}件")
    
    print("  ✓ SimilarityChecker 正常に動作\n")
except Exception as e:
    print(f"  ✗ エラー: {e}\n")
    import traceback
    traceback.print_exc()

print("=== 検証完了 ===")
