"""
File Repositoryのプロパティベーステスト

プロパティ4, 5を検証
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings

from src.repositories.file_repository import FileRepository


class TestFileRepositoryProperties:
    """File Repositoryのプロパティテスト"""
    
    @given(st.text(min_size=1, max_size=10000).filter(lambda x: '\r' not in x or '\n' in x))
    @settings(max_examples=100)
    def test_property_4_file_write_read_roundtrip(self, content):
        """
        Feature: test-coverage-improvement, Property 4: ファイル読み書きのラウンドトリップ
        
        すべての文字列コンテンツに対して、書き込んでから読み込むと元の内容と一致する
        **検証: 要件2.1, 2.2**
        
        注: Pythonのテキストモードでは改行文字が正規化されるため、
        単独の\rは\nに変換されます。これは正常な動作です。
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # 書き込み
            write_result = repo.write_embed_code(content)
            assert write_result is True
            
            # 読み込み
            read_content = repo.read_embed_code()
            
            # ラウンドトリップの検証
            # Pythonのテキストモードでは改行が正規化されるため、
            # 書き込み前に正規化した内容と比較
            normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
            assert read_content == normalized_content
    
    @given(st.text(min_size=1, max_size=10000).filter(lambda x: '\r' not in x or '\n' in x))
    @settings(max_examples=100)
    def test_property_5_backup_consistency(self, content):
        """
        Feature: test-coverage-improvement, Property 5: バックアップの一貫性
        
        すべてのファイル内容に対して、バックアップを作成すると
        元ファイルと同じ内容のバックアップファイルが作成される
        **検証: 要件2.4**
        
        注: Pythonのテキストモードでは改行文字が正規化されるため、
        単独の\rは\nに変換されます。これは正常な動作です。
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            backup_dir = Path(tmpdir) / "backups"
            
            # 元ファイルを作成（改行を正規化）
            normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
            embed_path.write_text(normalized_content, encoding='utf-8')
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(backup_dir)
            )
            
            # バックアップを作成
            backup_path = repo.create_backup()
            
            # バックアップが作成されたことを確認
            assert backup_path is not None
            assert Path(backup_path).exists()
            
            # バックアップの内容が元ファイルと一致することを確認
            backup_content = Path(backup_path).read_text(encoding='utf-8')
            original_content = embed_path.read_text(encoding='utf-8')
            assert backup_content == original_content
