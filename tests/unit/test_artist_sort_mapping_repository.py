"""ArtistSortMappingRepositoryのユニットテスト"""

import tempfile
import pytest
from pathlib import Path

from src.repositories.artist_sort_mapping_repository import ArtistSortMappingRepository


class TestArtistSortMappingRepository:
    """ArtistSortMappingRepositoryのユニットテスト"""
    
    def test_load_mappings_normal_file(self):
        """正常なTSVファイルの読み込みテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            # テストデータを作成
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('アーティスト名\tソート名\n')
                f.write('Vaundy\tVaundy\n')
                f.write('米津玄師\tよねづけんし\n')
            
            repo = ArtistSortMappingRepository(str(file_path))
            mappings = repo.load_mappings()
            
            assert len(mappings) == 2
            assert mappings['Vaundy'] == 'Vaundy'
            assert mappings['米津玄師'] == 'よねづけんし'
    
    def test_load_mappings_empty_file(self):
        """空ファイルの読み込みテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            # 空ファイルを作成
            file_path.touch()
            
            repo = ArtistSortMappingRepository(str(file_path))
            mappings = repo.load_mappings()
            
            assert mappings == {}
    
    def test_load_mappings_nonexistent_file(self):
        """存在しないファイルの読み込みテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "nonexistent.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            mappings = repo.load_mappings()
            
            assert mappings == {}
    
    def test_save_mapping_new(self):
        """新規マッピングの追加テスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            repo.save_mapping('Vaundy', 'Vaundy')
            
            # ファイルが作成されたことを確認
            assert file_path.exists()
            
            # マッピングが保存されたことを確認
            mappings = repo.load_mappings()
            assert mappings['Vaundy'] == 'Vaundy'
    
    def test_save_mapping_update(self):
        """既存マッピングの更新テスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            
            # 最初のマッピングを追加
            repo.save_mapping('Vaundy', 'ばうんでぃ')
            
            # マッピングを更新
            repo.save_mapping('Vaundy', 'Vaundy')
            
            # 更新されたマッピングを確認
            mappings = repo.load_mappings()
            assert mappings['Vaundy'] == 'Vaundy'
    
    def test_delete_mapping_existing(self):
        """マッピングの削除テスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            
            # マッピングを追加
            repo.save_mapping('Vaundy', 'Vaundy')
            repo.save_mapping('米津玄師', 'よねづけんし')
            
            # マッピングを削除
            result = repo.delete_mapping('Vaundy')
            
            assert result is True
            
            # 削除されたことを確認
            mappings = repo.load_mappings()
            assert 'Vaundy' not in mappings
            assert '米津玄師' in mappings
    
    def test_delete_mapping_nonexistent(self):
        """存在しないマッピングの削除テスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            
            # 存在しないマッピングを削除
            result = repo.delete_mapping('Nonexistent')
            
            assert result is False
    
    def test_load_mappings_duplicate_entries(self):
        """重複エントリの処理テスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            # 重複エントリを含むファイルを作成
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('アーティスト名\tソート名\n')
                f.write('Vaundy\tばうんでぃ\n')
                f.write('Vaundy\tVaundy\n')
            
            repo = ArtistSortMappingRepository(str(file_path))
            mappings = repo.load_mappings()
            
            # 最後のエントリが有効になることを確認
            assert mappings['Vaundy'] == 'Vaundy'
    
    def test_load_mappings_empty_lines(self):
        """空行の処理テスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            # 空行を含むファイルを作成
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('アーティスト名\tソート名\n')
                f.write('Vaundy\tVaundy\n')
                f.write('\n')
                f.write('米津玄師\tよねづけんし\n')
            
            repo = ArtistSortMappingRepository(str(file_path))
            mappings = repo.load_mappings()
            
            # 空行が無視されることを確認
            assert len(mappings) == 2
            assert mappings['Vaundy'] == 'Vaundy'
            assert mappings['米津玄師'] == 'よねづけんし'
    
    def test_load_mappings_invalid_format_no_header(self):
        """ヘッダーなしの不正形式ファイルのテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            # ヘッダーなしのファイルを作成
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('Vaundy\tVaundy\n')
            
            repo = ArtistSortMappingRepository(str(file_path))
            
            with pytest.raises(ValueError, match="ヘッダー行が見つかりません"):
                repo.load_mappings()
    
    def test_load_mappings_invalid_format_wrong_columns(self):
        """カラム数が不正なファイルのテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            # カラム数が不正なファイルを作成
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('アーティスト名\tソート名\n')
                f.write('Vaundy\n')  # カラムが1つしかない
            
            repo = ArtistSortMappingRepository(str(file_path))
            
            with pytest.raises(ValueError, match="カラム数が不正です"):
                repo.load_mappings()
    
    def test_get_mapping_existing(self):
        """特定のマッピングの取得テスト（存在する場合）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            repo.save_mapping('Vaundy', 'Vaundy')
            
            sort_name = repo.get_mapping('Vaundy')
            assert sort_name == 'Vaundy'
    
    def test_get_mapping_nonexistent(self):
        """特定のマッピングの取得テスト（存在しない場合）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            
            sort_name = repo.get_mapping('Nonexistent')
            assert sort_name is None
    
    def test_get_all_mappings(self):
        """すべてのマッピングの取得テスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            repo.save_mapping('Vaundy', 'Vaundy')
            repo.save_mapping('米津玄師', 'よねづけんし')
            
            mappings = repo.get_all_mappings()
            
            assert len(mappings) == 2
            assert mappings['Vaundy'] == 'Vaundy'
            assert mappings['米津玄師'] == 'よねづけんし'
