"""TsvRepositoryのユニットテスト"""

import pytest
import tempfile
import os
from pathlib import Path
from src.repositories.tsv_repository import TsvRepository


class TestTsvRepository:
    """TsvRepositoryクラスのテスト"""
    
    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリを作成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def tsv_repo(self, temp_dir):
        """TsvRepositoryインスタンスを作成"""
        return TsvRepository(temp_dir)
    
    def test_save_tsv_basic(self, tsv_repo, temp_dir):
        """基本的なTSVファイルの保存をテスト"""
        headers = ["ID", "Name", "Value"]
        rows = [
            [1, "Test", "100"],
            [2, "Sample", "200"]
        ]
        
        tsv_repo.save_tsv("test.tsv", headers, rows)
        
        # ファイルが作成されたことを確認
        file_path = Path(temp_dir) / "test.tsv"
        assert file_path.exists()
        
        # ファイルの内容を確認
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        assert len(lines) == 3  # ヘッダー + 2行
        assert lines[0].strip() == "ID\tName\tValue"
        assert lines[1].strip() == "1\tTest\t100"
        assert lines[2].strip() == "2\tSample\t200"
    
    def test_save_tsv_with_newlines(self, tsv_repo, temp_dir):
        """改行文字を含むデータのテスト"""
        headers = ["ID", "Text"]
        rows = [
            [1, "Line1\nLine2"],
            [2, "Line1\r\nLine2"]
        ]
        
        tsv_repo.save_tsv("test.tsv", headers, rows)
        
        file_path = Path(temp_dir) / "test.tsv"
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 改行文字がスペースに置換されていることを確認
        assert "Line1 Line2" in lines[1]
        # \r\nは2つのスペースになる
        assert "Line1  Line2" in lines[2]
    
    def test_save_tsv_with_tabs(self, tsv_repo, temp_dir):
        """タブ文字を含むデータのテスト"""
        headers = ["ID", "Text"]
        rows = [
            [1, "Field1\tField2"]
        ]
        
        tsv_repo.save_tsv("test.tsv", headers, rows)
        
        file_path = Path(temp_dir) / "test.tsv"
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # タブ文字がスペースに置換されていることを確認
        lines = content.strip().split('\n')
        assert lines[1] == "1\tField1 Field2"
    
    def test_save_tsv_with_none_values(self, tsv_repo, temp_dir):
        """None値を含むデータのテスト"""
        headers = ["ID", "Name", "Value"]
        rows = [
            [1, None, "100"],
            [2, "Test", None]
        ]
        
        tsv_repo.save_tsv("test.tsv", headers, rows)
        
        file_path = Path(temp_dir) / "test.tsv"
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # None値が空文字列として出力されることを確認
        assert lines[1].strip() == "1\t\t100"
        # 末尾のNoneは空文字列になるが、タブは出力されない
        assert lines[2].strip() == "2\tTest"
    
    def test_save_tsv_utf8_encoding(self, tsv_repo, temp_dir):
        """UTF-8エンコーディングのテスト"""
        headers = ["ID", "日本語"]
        rows = [
            [1, "テスト"],
            [2, "サンプル"]
        ]
        
        tsv_repo.save_tsv("test.tsv", headers, rows)
        
        file_path = Path(temp_dir) / "test.tsv"
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        assert "日本語" in lines[0]
        assert "テスト" in lines[1]
        assert "サンプル" in lines[2]
    
    def test_file_exists(self, tsv_repo, temp_dir):
        """file_existsメソッドのテスト"""
        # ファイルが存在しない場合
        assert not tsv_repo.file_exists("nonexistent.tsv")
        
        # ファイルを作成
        headers = ["ID"]
        rows = [[1]]
        tsv_repo.save_tsv("test.tsv", headers, rows)
        
        # ファイルが存在する場合
        assert tsv_repo.file_exists("test.tsv")
    
    def test_save_tsv_creates_directory(self, temp_dir):
        """存在しないディレクトリを自動作成するテスト"""
        nested_dir = os.path.join(temp_dir, "nested", "dir")
        tsv_repo = TsvRepository(nested_dir)
        
        headers = ["ID"]
        rows = [[1]]
        tsv_repo.save_tsv("test.tsv", headers, rows)
        
        # ディレクトリとファイルが作成されたことを確認
        file_path = Path(nested_dir) / "test.tsv"
        assert file_path.exists()
    
    def test_save_tsv_empty_rows(self, tsv_repo, temp_dir):
        """空のデータ行のテスト"""
        headers = ["ID", "Name"]
        rows = []
        
        tsv_repo.save_tsv("test.tsv", headers, rows)
        
        file_path = Path(temp_dir) / "test.tsv"
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # ヘッダーのみが出力されることを確認
        assert len(lines) == 1
        assert lines[0].strip() == "ID\tName"
