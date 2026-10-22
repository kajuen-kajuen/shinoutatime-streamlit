"""
File Repositoryのユニットテスト

要件2.1, 2.2, 2.3, 2.4をテスト
"""

import os
import tempfile
from pathlib import Path
import pytest

from src.repositories.file_repository import FileRepository
from src.exceptions.errors import FileWriteError


class TestFileRepositoryWrite:
    """ファイル書き込みのテスト（要件2.2）"""
    
    def test_write_embed_code_success(self):
        """正常な書き込み"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            test_content = "<blockquote>Test tweet</blockquote>"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            result = repo.write_embed_code(test_content)
            
            assert result is True
            assert embed_path.exists()
            assert embed_path.read_text(encoding='utf-8') == test_content
    
    def test_write_embed_code_creates_directory(self):
        """ディレクトリの自動作成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 存在しないディレクトリ内のパスを指定
            embed_path = Path(tmpdir) / "subdir" / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            test_content = "<blockquote>Test tweet</blockquote>"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            result = repo.write_embed_code(test_content)
            
            assert result is True
            assert embed_path.parent.exists()
            assert embed_path.exists()
    
    def test_write_embed_code_with_unicode(self):
        """Unicode文字を含む書き込み"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            test_content = "<blockquote>日本語のツイート 🎵</blockquote>"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            result = repo.write_embed_code(test_content)
            
            assert result is True
            assert embed_path.read_text(encoding='utf-8') == test_content
    
    def test_write_height_success(self):
        """高さの正常な書き込み"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            test_height = 1200
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            result = repo.write_height(test_height)
            
            assert result is True
            assert height_path.exists()
            assert height_path.read_text(encoding='utf-8') == str(test_height)
    
    def test_write_height_creates_directory(self):
        """高さファイルのディレクトリ自動作成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "subdir" / "test_height.txt"
            test_height = 1200
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            result = repo.write_height(test_height)
            
            assert result is True
            assert height_path.parent.exists()
            assert height_path.exists()


class TestFileRepositoryWriteErrors:
    """ファイル書き込みエラーのテスト（要件2.2, 2.3）"""
    
    def test_write_embed_code_permission_error(self):
        """write_embed_codeでPermissionErrorが発生した場合のFileWriteError"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            test_content = "<blockquote>Test tweet</blockquote>"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # open関数をモックしてPermissionErrorを発生させる
            import unittest.mock as mock
            with mock.patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with pytest.raises(FileWriteError) as exc_info:
                    repo.write_embed_code(test_content)
                
                # エラーメッセージを検証
                assert "書き込み権限がありません" in str(exc_info.value)
                assert str(embed_path) in str(exc_info.value)
    
    def test_write_embed_code_os_error(self):
        """write_embed_codeでOSErrorが発生した場合のFileWriteError"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            test_content = "<blockquote>Test tweet</blockquote>"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # open関数をモックしてOSErrorを発生させる
            import unittest.mock as mock
            with mock.patch('builtins.open', side_effect=OSError("Disk full")):
                with pytest.raises(FileWriteError) as exc_info:
                    repo.write_embed_code(test_content)
                
                # エラーメッセージを検証
                assert "書き込みに失敗しました" in str(exc_info.value)
    
    def test_write_height_permission_error(self):
        """write_heightでPermissionErrorが発生した場合のFileWriteError"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            test_height = 1200
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # open関数をモックしてPermissionErrorを発生させる
            import unittest.mock as mock
            with mock.patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with pytest.raises(FileWriteError) as exc_info:
                    repo.write_height(test_height)
                
                # エラーメッセージを検証
                assert "書き込み権限がありません" in str(exc_info.value)
                assert str(height_path) in str(exc_info.value)
    
    def test_write_height_os_error(self):
        """write_heightでOSErrorが発生した場合のFileWriteError"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            test_height = 1200
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # open関数をモックしてOSErrorを発生させる
            import unittest.mock as mock
            with mock.patch('builtins.open', side_effect=OSError("Disk full")):
                with pytest.raises(FileWriteError) as exc_info:
                    repo.write_height(test_height)
                
                # エラーメッセージを検証
                assert "書き込みに失敗しました" in str(exc_info.value)


class TestFileRepositoryBackup:
    """バックアップ機能のテスト（要件2.4）"""
    
    def test_create_backup_success(self):
        """バックアップファイルの作成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            backup_dir = Path(tmpdir) / "backups"
            test_content = "<blockquote>Test tweet</blockquote>"
            
            # 元ファイルを作成
            embed_path.write_text(test_content, encoding='utf-8')
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(backup_dir)
            )
            
            backup_path = repo.create_backup()
            
            assert backup_path is not None
            assert Path(backup_path).exists()
            assert Path(backup_path).read_text(encoding='utf-8') == test_content
    
    def test_create_backup_with_timestamp(self):
        """タイムスタンプ付きファイル名"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            backup_dir = Path(tmpdir) / "backups"
            test_content = "<blockquote>Test tweet</blockquote>"
            
            embed_path.write_text(test_content, encoding='utf-8')
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(backup_dir)
            )
            
            backup_path = repo.create_backup()
            
            assert backup_path is not None
            # ファイル名にタイムスタンプが含まれていることを確認
            backup_filename = Path(backup_path).name
            assert "test_embed" in backup_filename
            assert ".html" in backup_filename
            # タイムスタンプ形式（YYYYMMDD_HHMMSS）が含まれていることを確認
            assert "_" in backup_filename
    
    def test_create_backup_file_not_exists(self):
        """元ファイルが存在しない場合"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "nonexistent.html"
            height_path = Path(tmpdir) / "test_height.txt"
            backup_dir = Path(tmpdir) / "backups"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(backup_dir)
            )
            
            backup_path = repo.create_backup()
            
            # ファイルが存在しない場合はNoneを返す
            assert backup_path is None
    
    def test_create_backup_preserves_content(self):
        """バックアップが元ファイルの内容を保持する"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            backup_dir = Path(tmpdir) / "backups"
            test_content = "<blockquote>日本語のツイート 🎵</blockquote>"
            
            embed_path.write_text(test_content, encoding='utf-8')
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(backup_dir)
            )
            
            backup_path = repo.create_backup()
            
            assert backup_path is not None
            # バックアップの内容が元ファイルと一致することを確認
            backup_content = Path(backup_path).read_text(encoding='utf-8')
            assert backup_content == test_content
