"""ArtistSortMappingRepositoryのプロパティベーステスト

Property 1, 2, 3, 4, 7を検証
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

from src.repositories.artist_sort_mapping_repository import ArtistSortMappingRepository


# 有効なアーティスト名とソート名の生成戦略
# タブ文字、改行文字、その他の制御文字を含まない、空でない文字列
valid_name = st.text(
    min_size=1,
    max_size=100,
    alphabet=st.characters(
        blacklist_categories=('Cc', 'Cs'),  # 制御文字とサロゲートを除外
        blacklist_characters='\t\n\r'
    )
).filter(lambda x: x.strip())  # 空白のみの文字列を除外


class TestArtistSortMappingRepositoryProperties:
    """ArtistSortMappingRepositoryのプロパティテスト"""
    
    @given(st.dictionaries(valid_name, valid_name, min_size=0, max_size=50))
    @settings(max_examples=100)
    def test_property_1_file_roundtrip_consistency(self, mappings):
        """
        Feature: artist-sort-correction, Property 1: ファイル読み込みの往復一貫性
        
        任意の有効なマッピング辞書について、それをファイルに保存してから読み込むと、
        元の辞書と等しい辞書が得られる（ただし、空白はトリムされる）
        **検証: 要件 1.1, 1.4**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            repo = ArtistSortMappingRepository(str(file_path))
            
            # マッピングを保存
            for artist, sort_name in mappings.items():
                repo.save_mapping(artist, sort_name)
            
            # マッピングを読み込み
            loaded_mappings = repo.load_mappings()
            
            # 往復一貫性を検証（空白がトリムされることを考慮）
            expected_mappings = {k.strip(): v.strip() for k, v in mappings.items()}
            assert loaded_mappings == expected_mappings
    
    @given(valid_name, valid_name)
    @settings(max_examples=100)
    def test_property_2_mapping_persistence(self, artist, sort_name):
        """
        Feature: artist-sort-correction, Property 2: マッピング追加の永続性
        
        任意のアーティスト名とソート名について、マッピングを追加した後に
        ファイルから読み込むと、そのマッピングが含まれている（空白はトリムされる）
        **検証: 要件 1.4**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            repo = ArtistSortMappingRepository(str(file_path))
            
            # マッピングを追加
            repo.save_mapping(artist, sort_name)
            
            # マッピングを読み込み
            loaded_mappings = repo.load_mappings()
            
            # マッピングが含まれていることを検証（空白がトリムされることを考慮）
            expected_artist = artist.strip()
            expected_sort_name = sort_name.strip()
            assert expected_artist in loaded_mappings
            assert loaded_mappings[expected_artist] == expected_sort_name
    
    @given(valid_name, valid_name, valid_name)
    @settings(max_examples=100)
    def test_property_3_mapping_update_overwrite(self, artist, old_sort_name, new_sort_name):
        """
        Feature: artist-sort-correction, Property 3: マッピング更新の上書き
        
        任意の既存のマッピングについて、新しいソート名で更新した後に
        ファイルから読み込むと、新しいソート名が使用されている（空白はトリムされる）
        **検証: 要件 1.5**
        """
        # 新旧のソート名が異なることを前提とする（空白トリム後）
        assume(old_sort_name.strip() != new_sort_name.strip())
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            repo = ArtistSortMappingRepository(str(file_path))
            
            # 既存のマッピングを追加
            repo.save_mapping(artist, old_sort_name)
            
            # マッピングを更新
            repo.save_mapping(artist, new_sort_name)
            
            # マッピングを読み込み
            loaded_mappings = repo.load_mappings()
            
            # 新しいソート名が使用されていることを検証（空白がトリムされることを考慮）
            expected_artist = artist.strip()
            expected_sort_name = new_sort_name.strip()
            assert loaded_mappings[expected_artist] == expected_sort_name
    
    @given(valid_name, valid_name)
    @settings(max_examples=100)
    def test_property_4_mapping_deletion_removal(self, artist, sort_name):
        """
        Feature: artist-sort-correction, Property 4: マッピング削除の除去
        
        任意の既存のマッピングについて、削除した後に
        ファイルから読み込むと、そのマッピングは含まれていない
        **検証: 要件 3.3**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            repo = ArtistSortMappingRepository(str(file_path))
            
            # マッピングを追加
            repo.save_mapping(artist, sort_name)
            
            # マッピングを削除
            result = repo.delete_mapping(artist)
            assert result is True
            
            # マッピングを読み込み
            loaded_mappings = repo.load_mappings()
            
            # マッピングが含まれていないことを検証
            assert artist not in loaded_mappings

    @given(st.lists(
        st.text(min_size=1, max_size=100).filter(lambda x: not x.startswith('アーティスト名')),
        min_size=1,
        max_size=20
    ))
    @settings(max_examples=100)
    def test_property_7_invalid_format_error_handling(self, invalid_lines):
        """
        Feature: artist-sort-correction, Property 7: 不正形式のエラー処理
        
        任意の不正な形式のファイル（ヘッダーなし）について、
        読み込もうとするとValueErrorが発生する
        **検証: 要件 1.3**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            # ヘッダーなしの不正なファイルを作成
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in invalid_lines:
                    f.write(f"{line}\n")
            
            repo = ArtistSortMappingRepository(str(file_path))
            
            # 不正な形式のファイルを読み込もうとするとValueErrorが発生することを検証
            try:
                repo.load_mappings()
                # ヘッダーがない場合は必ずエラーになるはず
                assert False, "ValueErrorが発生すべきでした"
            except ValueError:
                # 期待通りのエラー
                pass
