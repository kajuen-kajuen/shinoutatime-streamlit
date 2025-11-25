"""ArtistSortCLIのユニットテスト"""

import tempfile
import pytest
from pathlib import Path
from io import StringIO
import sys

from src.cli.artist_sort_cli import ArtistSortCLI
from src.repositories.artist_sort_mapping_repository import ArtistSortMappingRepository


class TestArtistSortCLI:
    """ArtistSortCLIのユニットテスト"""
    
    def test_add_mapping(self, capsys):
        """add_mapping()のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            cli = ArtistSortCLI(repo)
            
            # マッピングを追加
            cli.add_mapping('Vaundy', 'Vaundy')
            
            # 出力を確認
            captured = capsys.readouterr()
            assert '✓ 修正マッピングを追加しました' in captured.out
            assert 'アーティスト名: Vaundy' in captured.out
            assert 'ソート名: Vaundy' in captured.out
            
            # マッピングが保存されたことを確認
            mappings = repo.get_all_mappings()
            assert mappings['Vaundy'] == 'Vaundy'
    
    def test_list_mappings_empty(self, capsys):
        """list_mappings()のテスト（空の場合）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            cli = ArtistSortCLI(repo)
            
            # マッピングを一覧表示
            cli.list_mappings()
            
            # 出力を確認
            captured = capsys.readouterr()
            assert '修正マッピングは登録されていません。' in captured.out
    
    def test_list_mappings_with_data(self, capsys):
        """list_mappings()のテスト（データがある場合）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            cli = ArtistSortCLI(repo)
            
            # マッピングを追加
            repo.save_mapping('Vaundy', 'Vaundy')
            repo.save_mapping('米津玄師', 'よねづけんし')
            
            # マッピングを一覧表示
            cli.list_mappings()
            
            # 出力を確認
            captured = capsys.readouterr()
            assert '修正マッピング一覧' in captured.out
            assert '登録件数: 2件' in captured.out
            assert 'Vaundy' in captured.out
            assert '米津玄師' in captured.out
            assert 'よねづけんし' in captured.out
    
    def test_delete_mapping_existing(self, capsys):
        """delete_mapping()のテスト（存在するマッピング）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            cli = ArtistSortCLI(repo)
            
            # マッピングを追加
            repo.save_mapping('Vaundy', 'Vaundy')
            
            # マッピングを削除
            cli.delete_mapping('Vaundy')
            
            # 出力を確認
            captured = capsys.readouterr()
            assert '✓ 修正マッピングを削除しました' in captured.out
            assert 'アーティスト名: Vaundy' in captured.out
            
            # マッピングが削除されたことを確認
            mappings = repo.get_all_mappings()
            assert 'Vaundy' not in mappings
    
    def test_delete_mapping_nonexistent(self, capsys):
        """delete_mapping()のテスト（存在しないマッピング）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            cli = ArtistSortCLI(repo)
            
            # 存在しないマッピングを削除しようとする
            with pytest.raises(SystemExit) as exc_info:
                cli.delete_mapping('Nonexistent')
            
            # 終了コードを確認
            assert exc_info.value.code == 1
            
            # 出力を確認
            captured = capsys.readouterr()
            assert 'エラー: 指定されたアーティスト名の修正マッピングが見つかりません' in captured.out
            assert 'アーティスト名: Nonexistent' in captured.out
    
    def test_update_mapping_existing(self, capsys):
        """update_mapping()のテスト（既存のマッピング）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            cli = ArtistSortCLI(repo)
            
            # マッピングを追加
            repo.save_mapping('Vaundy', 'ばうんでぃ')
            
            # マッピングを更新
            cli.update_mapping('Vaundy', 'Vaundy')
            
            # 出力を確認
            captured = capsys.readouterr()
            assert '✓ 修正マッピングを更新しました' in captured.out
            assert 'アーティスト名: Vaundy' in captured.out
            assert '旧ソート名: ばうんでぃ' in captured.out
            assert '新ソート名: Vaundy' in captured.out
            
            # マッピングが更新されたことを確認
            mappings = repo.get_all_mappings()
            assert mappings['Vaundy'] == 'Vaundy'
    
    def test_update_mapping_nonexistent(self, capsys):
        """update_mapping()のテスト（存在しないマッピング）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            cli = ArtistSortCLI(repo)
            
            # 存在しないマッピングを更新（新規追加として扱われる）
            cli.update_mapping('Vaundy', 'Vaundy')
            
            # 出力を確認
            captured = capsys.readouterr()
            assert '注意: 指定されたアーティスト名の修正マッピングが存在しないため、新規追加します' in captured.out
            assert '✓ 修正マッピングを追加しました' in captured.out
            
            # マッピングが追加されたことを確認
            mappings = repo.get_all_mappings()
            assert mappings['Vaundy'] == 'Vaundy'
    
    def test_add_mapping_with_whitespace(self, capsys):
        """add_mapping()のテスト（前後に空白がある場合）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            cli = ArtistSortCLI(repo)
            
            # 前後に空白があるマッピングを追加
            cli.add_mapping('  Vaundy  ', '  Vaundy  ')
            
            # マッピングが保存されたことを確認（空白はトリムされる）
            mappings = repo.get_all_mappings()
            assert mappings['Vaundy'] == 'Vaundy'
    
    def test_list_mappings_sorted(self, capsys):
        """list_mappings()のテスト（ソート順の確認）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            
            repo = ArtistSortMappingRepository(str(file_path))
            cli = ArtistSortCLI(repo)
            
            # マッピングを追加（順不同）
            repo.save_mapping('米津玄師', 'よねづけんし')
            repo.save_mapping('Vaundy', 'Vaundy')
            repo.save_mapping('YOASOBI', 'YOASOBI')
            
            # マッピングを一覧表示
            cli.list_mappings()
            
            # 出力を確認
            captured = capsys.readouterr()
            output = captured.out
            
            # アーティスト名がソートされていることを確認
            vaundy_pos = output.find('Vaundy')
            yoasobi_pos = output.find('YOASOBI')
            yonezu_pos = output.find('米津玄師')
            
            assert vaundy_pos < yoasobi_pos < yonezu_pos
