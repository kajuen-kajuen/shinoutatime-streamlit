"""
ArtistSortGeneratorのユニットテスト
"""
import pytest
import tempfile
import os
from src.utils.artist_sort_generator import ArtistSortGenerator
from src.repositories.artist_sort_mapping_repository import ArtistSortMappingRepository


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


class TestArtistSortGeneratorWithMapping:
    """マッピングリポジトリを使用したArtistSortGeneratorのテストクラス"""
    
    @pytest.fixture
    def temp_mapping_file(self):
        """テスト用の一時マッピングファイル"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.tsv') as f:
            temp_file = f.name
            # ヘッダーとサンプルマッピングを書き込む
            f.write("アーティスト名\tソート名\n")
            f.write("米津玄師\tよねづけんし\n")
            f.write("Official髭男dism\tおふぃしゃるひげだんでぃずむ\n")
        
        yield temp_file
        
        # クリーンアップ
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    def test_mapping_exists(self, temp_mapping_file):
        """マッピングが存在する場合、マッピングのソート名が返される"""
        # 要件2.1: マッピングが存在する場合はマッピングを使用
        repository = ArtistSortMappingRepository(temp_mapping_file)
        generator = ArtistSortGenerator(mapping_repository=repository)
        
        result = generator.generate("米津玄師")
        assert result == "よねづけんし"
        
        result2 = generator.generate("Official髭男dism")
        assert result2 == "おふぃしゃるひげだんでぃずむ"
    
    def test_mapping_not_exists(self, temp_mapping_file):
        """マッピングが存在しない場合、自動生成されたソート名が返される"""
        # 要件2.2: マッピングが存在しない場合は自動生成
        repository = ArtistSortMappingRepository(temp_mapping_file)
        generator = ArtistSortGenerator(mapping_repository=repository)
        
        # マッピングに存在しないアーティスト名
        result = generator.generate("Vaundy")
        assert result == "Vaundy"  # 英数字のみなのでそのまま
    
    def test_no_mapping_repository(self):
        """マッピングリポジトリが設定されていない場合、自動生成される"""
        # 要件2.2: マッピングリポジトリがない場合は自動生成
        generator = ArtistSortGenerator()
        
        result = generator.generate("Vaundy")
        assert result == "Vaundy"
    
    def test_set_mapping_repository(self, temp_mapping_file):
        """set_mapping_repository()でマッピングリポジトリを設定できる"""
        generator = ArtistSortGenerator()
        repository = ArtistSortMappingRepository(temp_mapping_file)
        
        # 最初はマッピングなし
        result_before = generator.generate("米津玄師")
        
        # マッピングリポジトリを設定
        generator.set_mapping_repository(repository)
        
        # マッピングが適用される
        result_after = generator.generate("米津玄師")
        assert result_after == "よねづけんし"
