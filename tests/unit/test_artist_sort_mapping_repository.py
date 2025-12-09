"""ArtistSortMappingRepositoryのユニットテスト"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
import builtins

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

    def test_load_mappings_unicode_decode_error(self):
        """エンコーディングエラーのテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            repo = ArtistSortMappingRepository(str(file_path))
            
            # ファイルが存在する状態にする
            file_path.touch()

            # open関数がUnicodeDecodeErrorを発生させるようにモック
            with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')):
                with pytest.raises(ValueError, match="エンコーディングが不正です"):
                    repo.load_mappings()

    def test_load_mappings_generic_error(self):
        """予期しない読み込みエラーのテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            repo = ArtistSortMappingRepository(str(file_path))
            file_path.touch()

            with patch('builtins.open', side_effect=IOError("Disk Error")):
                with pytest.raises(ValueError, match="読み込みに失敗しました"):
                    repo.load_mappings()
    
    def test_save_mapping_permission_error(self):
        """保存時の権限エラーテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            repo = ArtistSortMappingRepository(str(file_path))

            with patch('builtins.open', side_effect=PermissionError("Denied")):
                with pytest.raises(IOError, match="書き込み権限がありません"):
                    repo.save_mapping('Artist', 'Sort')

    def test_save_mapping_os_error(self):
        """保存時のOSエラーテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            repo = ArtistSortMappingRepository(str(file_path))

            with patch('builtins.open', side_effect=OSError("Disk Full")):
                with pytest.raises(IOError, match="書き込みに失敗しました"):
                    repo.save_mapping('Artist', 'Sort')

    def test_delete_mapping_permission_error(self):
        """削除時の保存（書き込み）権限エラーテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            # ファイルを作成してデータを書き込む
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('アーティスト名\tソート名\n')
                f.write('Target\tSort\n')
                
            repo = ArtistSortMappingRepository(str(file_path))

            # loadは成功させて、その後のwriteでエラーにする
            # _write_mappingsがopenを呼ぶので、そのタイミングでエラーにしたいが
            # loadでもopenを使うため、モックの制御が少し複雑。
            # ここではシンプルに、load_mappingsの実装は依存なしとして、
            # _write_mappings内のopenをモックするのは難しい（メソッド内で完結しているため）。
            # したがって、ArtistSortMappingRepository._write_mappings をモックする手もあるが、
            # テスト対象はdelete_mappingなので、内部呼び出しのエラーをシミュレートする。
            
            with patch.object(ArtistSortMappingRepository, '_write_mappings', side_effect=PermissionError("Denied")):
                 with pytest.raises(IOError, match="書き込み権限がありません"):
                     repo.delete_mapping('Target')

    def test_delete_mapping_os_error(self):
        """削除時の保存（書き込み）OSエラーテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('アーティスト名\tソート名\n')
                f.write('Target\tSort\n')
                
            repo = ArtistSortMappingRepository(str(file_path))

            with patch.object(ArtistSortMappingRepository, '_write_mappings', side_effect=OSError("Disk Error")):
                 with pytest.raises(IOError, match="書き込みに失敗しました"):
                     repo.delete_mapping('Target')

    def test_get_all_mappings_fallback(self):
        """get_all_mappingsのエラーフォールバックテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_mapping.tsv"
            repo = ArtistSortMappingRepository(str(file_path))
            
            # load_mappings が ValueError を投げる状況を作る
            with patch.object(repo, 'load_mappings', side_effect=ValueError("Invalid Format")):
                mappings = repo.get_all_mappings()
                assert mappings == {}

