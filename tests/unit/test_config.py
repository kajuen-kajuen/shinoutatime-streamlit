"""
設定管理のテスト

src/config/settings.pyのConfigクラスが正しく動作することを確認するテストです。
"""

import pytest
import os

from src.config.settings import Config
from src.exceptions.errors import ConfigurationError


class TestConfig:
    """Configクラスのテスト"""
    
    def test_default_values(self):
        """デフォルト値が正しく設定されることを確認"""
        config = Config()
        
        assert config.v2_data_dir == "data/v2"
        assert config.initial_display_limit == 25
        assert config.display_increment == 25
        assert config.page_title == "しのうたタイム"
        assert config.page_icon == "👻"
        assert config.layout == "wide"
        assert config.enable_cache is True
        assert config.cache_ttl == 3600
    
    def test_from_env_with_environment_variables(self):
        """環境変数から設定を読み込めることを確認"""
        # 環境変数を設定
        os.environ["SHINOUTA_V2_DATA_DIR"] = "custom/v2"
        os.environ["SHINOUTA_INITIAL_DISPLAY_LIMIT"] = "50"
        os.environ["SHINOUTA_ENABLE_CACHE"] = "false"
        os.environ["SHINOUTA_PAGE_TITLE"] = "カスタムタイトル"
        
        try:
            config = Config.from_env()
            
            assert config.v2_data_dir == "custom/v2"
            assert config.initial_display_limit == 50
            assert config.enable_cache is False
            assert config.page_title == "カスタムタイトル"
        finally:
            # 環境変数をクリア
            del os.environ["SHINOUTA_V2_DATA_DIR"]
            del os.environ["SHINOUTA_INITIAL_DISPLAY_LIMIT"]
            del os.environ["SHINOUTA_ENABLE_CACHE"]
            del os.environ["SHINOUTA_PAGE_TITLE"]
    
    def test_from_env_boolean_parsing(self):
        """環境変数のブール値が正しく解析されることを確認"""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
        ]
        
        for env_value, expected in test_cases:
            os.environ["SHINOUTA_ENABLE_CACHE"] = env_value
            
            try:
                config = Config.from_env()
                assert config.enable_cache == expected, \
                    f"環境変数'{env_value}'が{expected}として解析されませんでした"
            finally:
                del os.environ["SHINOUTA_ENABLE_CACHE"]
    
    def test_validate_success(self):
        """有効な設定値の検証が成功することを確認"""
        config = Config()
        assert config.validate() is True
    
    def test_validate_invalid_initial_display_limit(self):
        """初期表示件数が0以下の場合に例外が発生することを確認"""
        config = Config(initial_display_limit=0)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "initial_display_limit" in str(exc_info.value)
    
    def test_validate_invalid_display_increment(self):
        """表示増分が0以下の場合に例外が発生することを確認"""
        config = Config(display_increment=-1)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "display_increment" in str(exc_info.value)
    
    def test_validate_empty_page_title(self):
        """ページタイトルが空の場合に例外が発生することを確認"""
        config = Config(page_title="")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "page_title" in str(exc_info.value)
    
    def test_validate_invalid_layout(self):
        """無効なレイアウトの場合に例外が発生することを確認"""
        config = Config(layout="invalid")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "layout" in str(exc_info.value)
    
    def test_validate_negative_cache_ttl(self):
        """キャッシュTTLが負の値の場合に例外が発生することを確認"""
        config = Config(cache_ttl=-1)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "cache_ttl" in str(exc_info.value)
    
    def test_validate_zero_cache_ttl(self):
        """キャッシュTTLが0の場合は有効であることを確認"""
        config = Config(cache_ttl=0)
        assert config.validate() is True
    
    def test_valid_layouts(self):
        """有効なレイアウト値が検証を通過することを確認"""
        for layout in ["centered", "wide"]:
            config = Config(layout=layout)
            assert config.validate() is True


class TestConfigIntegration:
    """Config統合テスト"""
    
    def test_config_lifecycle(self):
        """設定のライフサイクル全体が正しく動作することを確認"""
        # 1. デフォルト設定で作成
        config1 = Config()
        assert config1.validate() is True
        
        # 2. 環境変数から読み込み
        os.environ["SHINOUTA_PAGE_TITLE"] = "統合テスト"
        os.environ["SHINOUTA_CACHE_TTL"] = "7200"
        
        try:
            config2 = Config.from_env()
            assert config2.page_title == "統合テスト"
            assert config2.cache_ttl == 7200
            assert config2.validate() is True
        finally:
            del os.environ["SHINOUTA_PAGE_TITLE"]
            del os.environ["SHINOUTA_CACHE_TTL"]
    
    def test_config_immutability_after_validation(self):
        """検証後も設定値を変更できることを確認（データクラスの動作）"""
        config = Config()
        config.validate()
        
        # データクラスなので変更可能
        config.page_title = "新しいタイトル"
        assert config.page_title == "新しいタイトル"
