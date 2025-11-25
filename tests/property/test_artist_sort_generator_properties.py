"""
ArtistSortGeneratorのプロパティベーステスト
"""
import tempfile
import os
from hypothesis import given, strategies as st, settings
from src.utils.artist_sort_generator import ArtistSortGenerator
from src.repositories.artist_sort_mapping_repository import ArtistSortMappingRepository


class TestArtistSortGeneratorProperties:
    """ArtistSortGeneratorのプロパティテストクラス"""
    
    @given(
        artist=st.text(
            alphabet=st.characters(min_codepoint=33, max_codepoint=126),
            min_size=1, 
            max_size=100
        ),
        sort_name=st.text(
            alphabet=st.characters(min_codepoint=33, max_codepoint=126),
            min_size=1, 
            max_size=100
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_5_mapping_priority(self, artist, sort_name):
        """
        Feature: artist-sort-correction, Property 5: マッピング優先の適用
        
        任意のアーティスト名について、そのアーティスト名に対するマッピングが存在する場合、
        generate()はマッピングのソート名を返す
        
        **検証: 要件 2.1**
        """
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.tsv') as f:
            temp_file = f.name
            # ヘッダーとマッピングを書き込む
            f.write("アーティスト名\tソート名\n")
            f.write(f"{artist}\t{sort_name}\n")
        
        try:
            # リポジトリとジェネレーターを初期化
            repository = ArtistSortMappingRepository(temp_file)
            generator = ArtistSortGenerator(mapping_repository=repository)
            
            # マッピングが存在する場合、マッピングのソート名が返されることを確認
            result = generator.generate(artist)
            assert result == sort_name, f"期待: {sort_name}, 実際: {result}"
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    @given(
        artist=st.text(
            alphabet=st.characters(min_codepoint=33, max_codepoint=126),
            min_size=1, 
            max_size=100
        ),
        other_artist=st.text(
            alphabet=st.characters(min_codepoint=33, max_codepoint=126),
            min_size=1, 
            max_size=100
        ),
        sort_name=st.text(
            alphabet=st.characters(min_codepoint=33, max_codepoint=126),
            min_size=1, 
            max_size=100
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_6_auto_generation_fallback(self, artist, other_artist, sort_name):
        """
        Feature: artist-sort-correction, Property 6: 自動生成のフォールバック
        
        任意のアーティスト名について、そのアーティスト名に対するマッピングが存在しない場合、
        generate()は自動生成されたソート名を返す
        
        **検証: 要件 2.2**
        """
        # artistとother_artistが異なることを確認
        if artist == other_artist:
            return
        
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.tsv') as f:
            temp_file = f.name
            # ヘッダーと別のアーティストのマッピングを書き込む
            f.write("アーティスト名\tソート名\n")
            f.write(f"{other_artist}\t{sort_name}\n")
        
        try:
            # リポジトリとジェネレーターを初期化
            repository = ArtistSortMappingRepository(temp_file)
            generator_with_mapping = ArtistSortGenerator(mapping_repository=repository)
            generator_without_mapping = ArtistSortGenerator()
            
            # マッピングが存在しない場合、自動生成されたソート名が返されることを確認
            result_with_mapping = generator_with_mapping.generate(artist)
            result_without_mapping = generator_without_mapping.generate(artist)
            
            # マッピングリポジトリの有無に関わらず、同じ結果が返されることを確認
            assert result_with_mapping == result_without_mapping, \
                f"マッピングなしの結果が一致しません: {result_with_mapping} != {result_without_mapping}"
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_file):
                os.unlink(temp_file)
