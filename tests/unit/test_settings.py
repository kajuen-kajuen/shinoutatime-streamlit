"""
Settingsモジュールのユニットテスト

設定管理機能の正確性を検証します。
"""

import os
import pytest
from unittest.mock import patch
from src.config.settings import Config
from src.exceptions.errors import ConfigurationError


class TestConfigEnvironmentVariables:
    """Config環境変数読み込みのテスト"""
    
    def test_from_env_with_defaults(self):
        """デフォルト値を使用した設定読み込み"""
        # 環境変数をクリアした状態でテスト
        with patch.dict(os.environ, {}, clear=True):
            config = Config.from_env()
            
            # デフォルト値が正しく設定されていることを確認
            assert config.v2_data_dir == "data/v2"
            assert config.tweet_embed_code_path == "data/tweet_embed_code.html"
            assert config.tweet_height_path == "data/tweet_height.txt"
            assert config.css_file_path == "src/ui/styles/style.css"
            assert config.initial_display_limit == 25
            assert config.display_increment == 25
            assert config.page_title == "しのうたタイム"
            assert config.page_icon == "👻"
            assert config.layout == "wide"
            assert config.enable_cache is True
            assert config.cache_ttl == 3600
    
    def test_from_env_with_custom_values(self):
        """環境変数からカスタム値を読み込み"""
        env_vars = {
            "SHINOUTA_V2_DATA_DIR": "custom/v2",
            "SHINOUTA_TWEET_EMBED_CODE_PATH": "custom/embed.html",
            "SHINOUTA_TWEET_HEIGHT_PATH": "custom/height.txt",
            "SHINOUTA_CSS_FILE_PATH": "custom/style.css",
            "SHINOUTA_INITIAL_DISPLAY_LIMIT": "50",
            "SHINOUTA_DISPLAY_INCREMENT": "10",
            "SHINOUTA_PAGE_TITLE": "カスタムタイトル",
            "SHINOUTA_PAGE_ICON": "🎵",
            "SHINOUTA_LAYOUT": "centered",
            "SHINOUTA_ENABLE_CACHE": "false",
            "SHINOUTA_CACHE_TTL": "7200"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            
            # カスタム値が正しく読み込まれていることを確認
            assert config.v2_data_dir == "custom/v2"
            assert config.tweet_embed_code_path == "custom/embed.html"
            assert config.tweet_height_path == "custom/height.txt"
            assert config.css_file_path == "custom/style.css"
            assert config.initial_display_limit == 50
            assert config.display_increment == 10
            assert config.page_title == "カスタムタイトル"
            assert config.page_icon == "🎵"
            assert config.layout == "centered"
            assert config.enable_cache is False
            assert config.cache_ttl == 7200
    
    def test_from_env_boolean_conversion(self):
        """ブール値の型変換テスト"""
        # trueの様々な表現
        for true_value in ["true", "True", "TRUE", "1", "yes", "Yes", "YES"]:
            with patch.dict(os.environ, {"SHINOUTA_ENABLE_CACHE": true_value}, clear=True):
                config = Config.from_env()
                assert config.enable_cache is True, f"'{true_value}' should be True"
        
        # falseの様々な表現
        for false_value in ["false", "False", "FALSE", "0", "no", "No", "NO"]:
            with patch.dict(os.environ, {"SHINOUTA_ENABLE_CACHE": false_value}, clear=True):
                config = Config.from_env()
                assert config.enable_cache is False, f"'{false_value}' should be False"
    
    def test_from_env_integer_conversion(self):
        """整数値の型変換テスト"""
        env_vars = {
            "SHINOUTA_INITIAL_DISPLAY_LIMIT": "100",
            "SHINOUTA_DISPLAY_INCREMENT": "50",
            "SHINOUTA_CACHE_TTL": "1800"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            
            # 型が正しく変換されていることを確認
            assert isinstance(config.initial_display_limit, int)
            assert isinstance(config.display_increment, int)
            assert isinstance(config.cache_ttl, int)
            assert config.initial_display_limit == 100
            assert config.display_increment == 50
            assert config.cache_ttl == 1800


class TestConfigValidation:
    """Config設定値検証のテスト"""
    
    def test_validate_with_valid_config(self):
        """有効な設定値での検証成功"""
        config = Config()
        assert config.validate() is True

    def test_validate_negative_initial_display_limit(self):
        """初期表示件数が負の場合のエラー"""
        config = Config(initial_display_limit=-1)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "initial_display_limit" in str(exc_info.value)
        assert "正の整数である必要があります" in str(exc_info.value)
    
    def test_validate_zero_initial_display_limit(self):
        """初期表示件数が0の場合のエラー"""
        config = Config(initial_display_limit=0)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "initial_display_limit" in str(exc_info.value)
        assert "正の整数である必要があります" in str(exc_info.value)
    
    def test_validate_negative_display_increment(self):
        """表示増分が負の場合のエラー"""
        config = Config(display_increment=-5)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "display_increment" in str(exc_info.value)
        assert "正の整数である必要があります" in str(exc_info.value)
    
    def test_validate_zero_display_increment(self):
        """表示増分が0の場合のエラー"""
        config = Config(display_increment=0)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "display_increment" in str(exc_info.value)
        assert "正の整数である必要があります" in str(exc_info.value)
    
    def test_validate_empty_page_title(self):
        """ページタイトルが空の場合のエラー"""
        config = Config(page_title="")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "page_title" in str(exc_info.value)
        assert "ページタイトルが空です" in str(exc_info.value)
    
    def test_validate_invalid_layout(self):
        """無効なレイアウト値の場合のエラー"""
        config = Config(layout="invalid_layout")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "layout" in str(exc_info.value)
        assert "centered" in str(exc_info.value) or "wide" in str(exc_info.value)
    
    def test_validate_negative_cache_ttl(self):
        """キャッシュTTLが負の場合のエラー"""
        config = Config(cache_ttl=-100)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "cache_ttl" in str(exc_info.value)
        assert "0以上である必要があります" in str(exc_info.value)
    
    def test_validate_zero_cache_ttl(self):
        """キャッシュTTLが0の場合は有効（キャッシュ無効化）"""
        config = Config(cache_ttl=0)
        assert config.validate() is True


class TestConfigPaths:
    """Config パス設定のテスト"""
    
    def test_default_paths_are_relative(self):
        """デフォルトのパスが相対パスであることを確認"""
        config = Config()
        
        # デフォルトパスが相対パスであることを確認
        assert not os.path.isabs(config.v2_data_dir)
        assert not os.path.isabs(config.tweet_embed_code_path)
        assert not os.path.isabs(config.tweet_height_path)
        assert not os.path.isabs(config.css_file_path)
    
    def test_custom_paths_can_be_absolute(self):
        """カスタムパスに絶対パスを設定できることを確認"""
        if os.name == 'nt':  # Windows
            abs_path = "C:\\custom\\path\\file.tsv"
        else:  # Unix-like
            abs_path = "/custom/path/file.tsv"
        
        config = Config(css_file_path=abs_path)
        assert config.css_file_path == abs_path
        assert os.path.isabs(config.css_file_path)
    
    def test_paths_preserve_format(self):
        """パスの形式が保持されることを確認"""
        custom_path = "custom/directory/file.tsv"
        config = Config(css_file_path=custom_path)
        
        assert config.css_file_path == custom_path
