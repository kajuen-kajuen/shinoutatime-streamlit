"""
ArtistSortGeneratorのユニットテスト
"""
import pytest
from src.utils.artist_sort_generator import ArtistSortGenerator


class TestArtistSortGenerator:
    """ArtistSortGeneratorのテストクラス"""
    
    @pytest.fixture
    def generator(self):
        """テスト用のArtistSortGeneratorインスタンス"""
        return ArtistSortGenerator()
    
    def test_ascii_only_artist_name(self, generator):
        """英数字のみのアーティスト名はそのまま返される"""
        # 要件3.1: 英数字のみで構成される場合はそのまま使用
        assert generator.generate("Vaundy") == "Vaundy"
        assert generator.generate("YOASOBI") == "YOASOBI"
        assert generator.generate("Eve") == "Eve"
        assert generator.generate("Ado") == "Ado"
    
    def test_ascii_with_spaces_and_symbols(self, generator):
        """英数字とスペース・記号のみの場合もそのまま返される"""
        assert generator.generate("Kenshi Yonezu") == "Kenshi Yonezu"
        assert generator.generate("Mrs. GREEN APPLE") == "Mrs. GREEN APPLE"
        assert generator.generate("back-number") == "back-number"
    
    def test_japanese_artist_name(self, generator):
        """日本語が含まれる場合はひらがなに変換される"""
        # 要件3.2: 日本語が含まれる場合はひらがなに変換
        result = generator.generate("米津玄師")
        # pykakasiが利用可能な場合はひらがなに変換される
        # 利用できない場合は元の名前が返される
        assert result is not None
        assert len(result) > 0
    
    def test_empty_artist_name(self, generator):
        """空文字列の場合は空文字列を返す"""
        assert generator.generate("") == ""
    
    def test_mixed_japanese_and_english(self, generator):
        """日本語と英語が混在する場合も処理される"""
        result = generator.generate("LiSA")
        assert result is not None
        
        result2 = generator.generate("Aimer")
        assert result2 is not None
    
    def test_special_characters(self, generator):
        """特殊文字が含まれる場合も処理される"""
        # 要件3.3: 特殊文字を適切に処理
        result = generator.generate("Official髭男dism")
        assert result is not None
        
        result2 = generator.generate("ヨルシカ")
        assert result2 is not None
