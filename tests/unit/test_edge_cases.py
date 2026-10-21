"""
エッジケースと境界値のテスト

空文字列、None値、最大値・最小値などの境界値をテストします。
要件: 全般
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import requests

from src.clients.twitter_api_client import TwitterAPIClient
from src.repositories.file_repository import FileRepository
from src.utils.html_validator import validate_html_structure, validate_twitter_embed_code
from src.utils.validators import validate_tweet_url, extract_tweet_id
from src.services.twitter_embed_service import TwitterEmbedService
from src.services.data_service import DataService
from src.repositories.live_repository import LiveRepository
from src.config.settings import Config, TwitterEmbedConfig
from src.exceptions.errors import InvalidURLError, FileWriteError, DataLoadError
from tests.fixtures.mock_responses import create_mock_success_response, create_mock_oembed_response


class TestEmptyStringEdgeCases:
    """空文字列のエッジケーステスト"""
    
    def test_html_validator_with_empty_string(self):
        """HTML検証で空文字列を処理できること"""
        is_valid, errors = validate_html_structure("")
        assert is_valid is False
        assert len(errors) > 0
        assert any("空" in error for error in errors)
    
    def test_html_validator_with_whitespace_only(self):
        """HTML検証で空白のみの文字列を処理できること"""
        is_valid, errors = validate_html_structure("   \n\t  ")
        assert is_valid is False
        assert len(errors) > 0
    
    def test_tweet_url_validator_with_empty_string(self):
        """ツイートURL検証で空文字列を処理できること"""
        is_valid, error = validate_tweet_url("")
        assert is_valid is False
        assert error is not None
    
    def test_extract_tweet_id_with_empty_string(self):
        """ツイートID抽出で空文字列を処理できること"""
        tweet_id = extract_tweet_id("")
        assert tweet_id is None
    
    def test_file_repository_write_empty_string(self):
        """ファイルリポジトリで空文字列を書き込めること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # 空文字列でも書き込みは成功する
            result = repo.write_embed_code("")
            assert result is True
            assert embed_path.read_text(encoding='utf-8') == ""
    
    def test_twitter_embed_service_with_empty_url(self):
        """Twitter埋め込みサービスで空URLを処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            api_client = TwitterAPIClient()
            file_repo = FileRepository(
                embed_code_path=str(Path(tmpdir) / "embed.html"),
                height_path=str(Path(tmpdir) / "height.txt"),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            service = TwitterEmbedService(
                api_client=api_client,
                file_repo=file_repo
            )
            
            result = service.fetch_embed_code("")
            assert result.success is False
            assert result.error_message is not None


class TestNoneValueEdgeCases:
    """None値のエッジケーステスト"""
    
    def test_html_validator_with_none(self):
        """HTML検証でNoneを処理できること"""
        # Noneを渡すと適切にエラーハンドリングされる
        # 実装によってはFalseを返すか、例外を発生させる
        try:
            is_valid, errors = validate_html_structure(None)
            # エラーハンドリングされる場合
            assert is_valid is False
        except (TypeError, AttributeError):
            # 例外が発生する場合も許容
            pass
    
    def test_tweet_url_validator_with_none(self):
        """ツイートURL検証でNoneを処理できること"""
        # Noneを渡すと適切にエラーハンドリングされる
        try:
            is_valid, error = validate_tweet_url(None)
            # エラーハンドリングされる場合
            assert is_valid is False
        except (TypeError, AttributeError):
            # 例外が発生する場合も許容
            pass
    
    def test_extract_tweet_id_with_none(self):
        """ツイートID抽出でNoneを処理できること"""
        # Noneを渡すと適切にエラーハンドリングされる
        try:
            tweet_id = extract_tweet_id(None)
            # エラーハンドリングされる場合
            assert tweet_id is None
        except (TypeError, AttributeError):
            # 例外が発生する場合も許容
            pass
    
    def test_file_repository_write_none(self):
        """ファイルリポジトリでNoneを書き込もうとするとエラーになること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # Noneを書き込もうとするとFileWriteErrorが発生する
            with pytest.raises((TypeError, AttributeError, FileWriteError)):
                repo.write_embed_code(None)
    
    def test_file_repository_read_height_with_none_default(self):
        """ファイルリポジトリでNoneをデフォルト値として使用できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "nonexistent_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # デフォルト値としてNoneを指定できる
            result = repo.read_height(default=None)
            assert result is None


class TestMaxMinValueEdgeCases:
    """最大値・最小値のエッジケーステスト"""
    
    def test_file_repository_with_very_large_content(self):
        """ファイルリポジトリで非常に大きなコンテンツを処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # 非常に大きなコンテンツ（10MB相当）
            large_content = "x" * (10 * 1024 * 1024)
            
            result = repo.write_embed_code(large_content)
            assert result is True
            
            read_content = repo.read_embed_code()
            assert len(read_content) == len(large_content)
    
    def test_file_repository_with_zero_height(self):
        """ファイルリポジトリで高さ0を処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            result = repo.write_height(0)
            assert result is True
            
            read_height = repo.read_height()
            assert read_height == 0
    
    def test_file_repository_with_negative_height(self):
        """ファイルリポジトリで負の高さを処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # 負の値も書き込める（バリデーションは別レイヤーで行う）
            result = repo.write_height(-100)
            assert result is True
            
            read_height = repo.read_height()
            assert read_height == -100
    
    def test_file_repository_with_very_large_height(self):
        """ファイルリポジトリで非常に大きな高さを処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            # 非常に大きな値
            large_height = 999999999
            
            result = repo.write_height(large_height)
            assert result is True
            
            read_height = repo.read_height()
            assert read_height == large_height
    
    def test_html_validator_with_very_long_html(self):
        """HTML検証で非常に長いHTMLを処理できること"""
        # 非常に長いHTMLを生成
        long_content = "x" * 100000
        html = f'<blockquote class="twitter-tweet"><p>{long_content}</p></blockquote>'
        
        is_valid, errors = validate_html_structure(html)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_html_validator_with_deeply_nested_tags(self):
        """HTML検証で深くネストされたタグを処理できること"""
        # 深くネストされたHTML
        nested_html = '<blockquote class="twitter-tweet">'
        for i in range(100):
            nested_html += f'<div id="level{i}">'
        nested_html += '<p>Deep content</p>'
        for i in range(100):
            nested_html += '</div>'
        nested_html += '</blockquote>'
        
        is_valid, errors = validate_html_structure(nested_html)
        assert is_valid is True


class TestSpecialCharacterEdgeCases:
    """特殊文字のエッジケーステスト"""
    
    def test_file_repository_with_unicode_emoji(self):
        """ファイルリポジトリでUnicode絵文字を処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            content_with_emoji = "🎵🎶🎤🎧🎼 音楽のツイート 🎵🎶"
            
            result = repo.write_embed_code(content_with_emoji)
            assert result is True
            
            read_content = repo.read_embed_code()
            assert read_content == content_with_emoji
    
    def test_file_repository_with_special_html_chars(self):
        """ファイルリポジトリで特殊HTML文字を処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embed_path = Path(tmpdir) / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            content_with_special = '<>&"\'`'
            
            result = repo.write_embed_code(content_with_special)
            assert result is True
            
            read_content = repo.read_embed_code()
            assert read_content == content_with_special
    
    def test_html_validator_with_html_entities(self):
        """HTML検証でHTMLエンティティを処理できること"""
        html = '<blockquote class="twitter-tweet"><p>&lt;&gt;&amp;&quot;&#39;</p></blockquote>'
        
        is_valid, errors = validate_html_structure(html)
        assert is_valid is True
    
    def test_tweet_url_with_special_characters(self):
        """ツイートURLに特殊文字が含まれる場合を処理できること"""
        # クエリパラメータ付きURL
        url_with_params = "https://twitter.com/user/status/1234567890?s=20&t=abc123"
        is_valid, error = validate_tweet_url(url_with_params)
        # クエリパラメータがあっても有効
        assert is_valid is True
    
    def test_extract_tweet_id_with_trailing_slash(self):
        """ツイートID抽出で末尾にスラッシュがある場合を処理できること"""
        url_with_slash = "https://twitter.com/user/status/1234567890/"
        tweet_id = extract_tweet_id(url_with_slash)
        assert tweet_id == "1234567890"


class TestBoundaryConditions:
    """境界条件のテスト"""
    
    def test_config_with_zero_timeout(self):
        """設定で0秒のタイムアウトを処理できること"""
        from src.exceptions.errors import ConfigurationError
        
        # 0秒のタイムアウトは無効な値として扱われる
        config = TwitterEmbedConfig(api_timeout=0)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "api_timeout" in str(exc_info.value)
    
    def test_config_with_negative_timeout(self):
        """設定で負のタイムアウトを処理できること"""
        from src.exceptions.errors import ConfigurationError
        
        # 負の値は無効として扱われる
        config = TwitterEmbedConfig(api_timeout=-10)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "api_timeout" in str(exc_info.value)
    
    def test_data_service_with_empty_dataframe(self):
        """データサービスで空のDataFrameを処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 空のTSVファイルを作成
            empty_tsv = Path(tmpdir) / "empty.tsv"
            empty_tsv.write_text("", encoding='utf-8')
            
            # 本物のリポジトリで空のファイルを読ませる
            config = Config(lives_file_path=str(empty_tsv))
            service = DataService(config, LiveRepository(str(empty_tsv)), Mock(), Mock())

            # 空のファイルは読み込みの失敗として DataLoadError になる
            with pytest.raises(DataLoadError):
                service.load_lives_data()
    
    def test_data_service_with_single_row(self):
        """データサービスで1行のみのデータを処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1行のみのTSVファイルを作成（ヘッダーのみ）
            single_row_tsv = Path(tmpdir) / "single.tsv"
            single_row_tsv.write_text("ID\tタイトル\n", encoding='utf-8')
            
            # 本物のリポジトリでヘッダーだけのファイルを読ませる
            config = Config(lives_file_path=str(single_row_tsv))
            service = DataService(config, LiveRepository(str(single_row_tsv)), Mock(), Mock())

            # ヘッダーだけ(データの行が無い)のファイルも DataLoadError になる
            with pytest.raises(DataLoadError):
                service.load_lives_data()


class TestPathEdgeCases:
    """パスのエッジケーステスト"""
    
    def test_file_repository_with_relative_path(self):
        """ファイルリポジトリで相対パスを処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 相対パスを使用
            embed_path = "test_embed.html"
            height_path = "test_height.txt"
            
            # 作業ディレクトリを一時ディレクトリに変更
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                repo = FileRepository(
                    embed_code_path=embed_path,
                    height_path=height_path,
                    backup_dir="backups"
                )
                
                content = "<blockquote>Test</blockquote>"
                result = repo.write_embed_code(content)
                assert result is True
                
                read_content = repo.read_embed_code()
                assert read_content == content
            finally:
                os.chdir(original_cwd)
    
    def test_file_repository_with_very_long_path(self):
        """ファイルリポジトリで非常に長いパスを処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 非常に長いパスを生成
            long_subdir = "a" * 50 + "/" + "b" * 50 + "/" + "c" * 50
            embed_path = Path(tmpdir) / long_subdir / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            content = "<blockquote>Test</blockquote>"
            result = repo.write_embed_code(content)
            assert result is True
            
            assert embed_path.exists()
    
    def test_file_repository_with_special_chars_in_path(self):
        """ファイルリポジトリでパスに特殊文字が含まれる場合を処理できること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 特殊文字を含むディレクトリ名（OSによって制限がある）
            # スペースやハイフンは一般的に使用可能
            special_dir = "test-dir with spaces"
            embed_path = Path(tmpdir) / special_dir / "test_embed.html"
            height_path = Path(tmpdir) / "test_height.txt"
            
            repo = FileRepository(
                embed_code_path=str(embed_path),
                height_path=str(height_path),
                backup_dir=str(Path(tmpdir) / "backups")
            )
            
            content = "<blockquote>Test</blockquote>"
            result = repo.write_embed_code(content)
            assert result is True
            
            assert embed_path.exists()
