"""
Settingsモジュールのユニットテスト

設定管理機能の正確性を検証します。
"""

import os
import pytest
from unittest.mock import patch
from src.config.settings import Config, TwitterAPICredentials, TwitterEmbedConfig
from src.exceptions.errors import ConfigurationError


class TestConfigEnvironmentVariables:
    """Config環境変数読み込みのテスト"""
    
    def test_from_env_with_defaults(self):
        """デフォルト値を使用した設定読み込み"""
        # 環境変数をクリアした状態でテスト
        with patch.dict(os.environ, {}, clear=True):
            config = Config.from_env()
            
            # デフォルト値が正しく設定されていることを確認
            assert config.lives_file_path == "data/M_YT_LIVE.TSV"
            assert config.songs_file_path == "data/M_YT_LIVE_TIMESTAMP.TSV"
            assert config.song_list_file_path == "data/V_SONG_LIST.TSV"
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
            "SHINOUTA_LIVES_FILE_PATH": "custom/lives.tsv",
            "SHINOUTA_SONGS_FILE_PATH": "custom/songs.tsv",
            "SHINOUTA_SONG_LIST_FILE_PATH": "custom/song_list.tsv",
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
            assert config.lives_file_path == "custom/lives.tsv"
            assert config.songs_file_path == "custom/songs.tsv"
            assert config.song_list_file_path == "custom/song_list.tsv"
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


class TestTwitterAPICredentialsEnvironmentVariables:
    """TwitterAPICredentials環境変数読み込みのテスト"""
    
    def test_from_env_with_no_credentials(self):
        """認証情報なしでの読み込み（警告のみ）"""
        with patch.dict(os.environ, {}, clear=True):
            credentials = TwitterAPICredentials.from_env()
            
            # 認証情報がNoneであることを確認
            assert credentials.api_key is None
            assert credentials.api_secret is None
            assert credentials.is_configured() is False
    
    def test_from_env_with_credentials(self):
        """認証情報ありでの読み込み"""
        env_vars = {
            "TWITTER_API_KEY": "test_api_key_12345",
            "TWITTER_API_SECRET": "test_api_secret_67890"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            credentials = TwitterAPICredentials.from_env()
            
            # 認証情報が正しく読み込まれていることを確認
            assert credentials.api_key == "test_api_key_12345"
            assert credentials.api_secret == "test_api_secret_67890"
            assert credentials.is_configured() is True
    
    def test_from_env_with_partial_credentials(self):
        """部分的な認証情報での読み込み（警告のみ）"""
        # API Keyのみ
        with patch.dict(os.environ, {"TWITTER_API_KEY": "test_key"}, clear=True):
            credentials = TwitterAPICredentials.from_env()
            assert credentials.api_key == "test_key"
            assert credentials.api_secret is None
            assert credentials.is_configured() is False
        
        # API Secretのみ
        with patch.dict(os.environ, {"TWITTER_API_SECRET": "test_secret"}, clear=True):
            credentials = TwitterAPICredentials.from_env()
            assert credentials.api_key is None
            assert credentials.api_secret == "test_secret"
            assert credentials.is_configured() is False


class TestTwitterEmbedConfigEnvironmentVariables:
    """TwitterEmbedConfig環境変数読み込みのテスト"""
    
    def test_from_env_with_defaults(self):
        """デフォルト値を使用した設定読み込み"""
        with patch.dict(os.environ, {}, clear=True):
            config = TwitterEmbedConfig.from_env()
            
            # デフォルト値が正しく設定されていることを確認
            assert config.embed_code_path == "data/tweet_embed_code.html"
            assert config.height_path == "data/tweet_height.txt"
            assert config.backup_dir == "data/backups"
            assert config.log_level == "INFO"
            assert config.log_file == "logs/twitter_embed.log"
            assert config.max_retries == 3
            assert config.retry_delay == 1.0
            assert config.api_timeout == 30
            assert config.default_height == 850
            assert config.enable_admin_page is False  # 既定は管理ページを出さない
    
    def test_from_env_with_custom_values(self):
        """環境変数からカスタム値を読み込み"""
        env_vars = {
            "TWITTER_EMBED_CODE_PATH": "custom/embed.html",
            "TWITTER_HEIGHT_PATH": "custom/height.txt",
            "TWITTER_BACKUP_DIR": "custom/backups",
            "TWITTER_EMBED_LOG_LEVEL": "DEBUG",
            "TWITTER_EMBED_LOG_FILE": "custom/logs/twitter.log",
            "TWITTER_API_MAX_RETRIES": "5",
            "TWITTER_API_RETRY_DELAY": "2.5",
            "TWITTER_API_TIMEOUT": "60",
            "TWITTER_DEFAULT_HEIGHT": "1000",
            "TWITTER_ENABLE_ADMIN_PAGE": "true"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = TwitterEmbedConfig.from_env()
            
            # カスタム値が正しく読み込まれていることを確認
            assert config.embed_code_path == "custom/embed.html"
            assert config.height_path == "custom/height.txt"
            assert config.backup_dir == "custom/backups"
            assert config.log_level == "DEBUG"
            assert config.log_file == "custom/logs/twitter.log"
            assert config.max_retries == 5
            assert config.retry_delay == 2.5
            assert config.api_timeout == 60
            assert config.default_height == 1000
            assert config.enable_admin_page is True
    
    def test_from_env_type_conversion(self):
        """型変換のテスト"""
        env_vars = {
            "TWITTER_API_MAX_RETRIES": "10",
            "TWITTER_API_RETRY_DELAY": "3.14",
            "TWITTER_API_TIMEOUT": "120",
            "TWITTER_DEFAULT_HEIGHT": "900"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = TwitterEmbedConfig.from_env()
            
            # 型が正しく変換されていることを確認
            assert isinstance(config.max_retries, int)
            assert isinstance(config.retry_delay, float)
            assert isinstance(config.api_timeout, int)
            assert isinstance(config.default_height, int)
            assert config.max_retries == 10
            assert config.retry_delay == 3.14
            assert config.api_timeout == 120
            assert config.default_height == 900



class TestConfigValidation:
    """Config設定値検証のテスト"""
    
    def test_validate_with_valid_config(self):
        """有効な設定値での検証成功"""
        config = Config()
        assert config.validate() is True
    
    def test_validate_empty_lives_file_path(self):
        """配信データファイルパスが空の場合のエラー"""
        config = Config(lives_file_path="")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "lives_file_path" in str(exc_info.value)
        assert "配信データファイルパスが空です" in str(exc_info.value)
    
    def test_validate_empty_songs_file_path(self):
        """楽曲データファイルパスが空の場合のエラー"""
        config = Config(songs_file_path="")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "songs_file_path" in str(exc_info.value)
        assert "楽曲データファイルパスが空です" in str(exc_info.value)
    
    def test_validate_empty_song_list_file_path(self):
        """楽曲リストファイルパスが空の場合のエラー"""
        config = Config(song_list_file_path="")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "song_list_file_path" in str(exc_info.value)
        assert "楽曲リストファイルパスが空です" in str(exc_info.value)
    
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


class TestTwitterAPICredentialsValidation:
    """TwitterAPICredentials検証のテスト"""
    
    def test_validate_without_requiring_credentials(self):
        """認証情報を必須としない場合の検証成功"""
        credentials = TwitterAPICredentials()
        assert credentials.validate(require_credentials=False) is True
    
    def test_validate_with_credentials_not_required(self):
        """認証情報が設定されていて、必須でない場合の検証成功"""
        credentials = TwitterAPICredentials(
            api_key="test_key",
            api_secret="test_secret"
        )
        assert credentials.validate(require_credentials=False) is True
    
    def test_validate_requiring_credentials_without_api_key(self):
        """認証情報必須でAPI Keyがない場合のエラー"""
        credentials = TwitterAPICredentials(api_secret="test_secret")
        
        with pytest.raises(ConfigurationError) as exc_info:
            credentials.validate(require_credentials=True)
        
        assert "TWITTER_API_KEY" in str(exc_info.value)
        assert "設定されていません" in str(exc_info.value)
    
    def test_validate_requiring_credentials_without_api_secret(self):
        """認証情報必須でAPI Secretがない場合のエラー"""
        credentials = TwitterAPICredentials(api_key="test_key")
        
        with pytest.raises(ConfigurationError) as exc_info:
            credentials.validate(require_credentials=True)
        
        assert "TWITTER_API_SECRET" in str(exc_info.value)
        assert "設定されていません" in str(exc_info.value)
    
    def test_validate_requiring_credentials_with_both(self):
        """認証情報必須で両方設定されている場合の検証成功"""
        credentials = TwitterAPICredentials(
            api_key="test_key",
            api_secret="test_secret"
        )
        assert credentials.validate(require_credentials=True) is True
    
    def test_validate_empty_api_key(self):
        """空のAPI Keyの場合のエラー"""
        credentials = TwitterAPICredentials(api_key="   ")
        
        with pytest.raises(ConfigurationError) as exc_info:
            credentials.validate(require_credentials=False)
        
        assert "TWITTER_API_KEY" in str(exc_info.value)
        assert "形式が不正です" in str(exc_info.value)
    
    def test_validate_empty_api_secret(self):
        """空のAPI Secretの場合のエラー"""
        credentials = TwitterAPICredentials(api_secret="   ")
        
        with pytest.raises(ConfigurationError) as exc_info:
            credentials.validate(require_credentials=False)
        
        assert "TWITTER_API_SECRET" in str(exc_info.value)
        assert "形式が不正です" in str(exc_info.value)
    
    def test_is_configured_with_both_credentials(self):
        """両方の認証情報が設定されている場合"""
        credentials = TwitterAPICredentials(
            api_key="test_key",
            api_secret="test_secret"
        )
        assert credentials.is_configured() is True
    
    def test_is_configured_with_partial_credentials(self):
        """部分的な認証情報の場合"""
        credentials = TwitterAPICredentials(api_key="test_key")
        assert credentials.is_configured() is False
        
        credentials = TwitterAPICredentials(api_secret="test_secret")
        assert credentials.is_configured() is False
    
    def test_is_configured_without_credentials(self):
        """認証情報がない場合"""
        credentials = TwitterAPICredentials()
        assert credentials.is_configured() is False
    
    def test_mask_credentials(self):
        """認証情報のマスク処理"""
        credentials = TwitterAPICredentials(
            api_key="test_key_12345",
            api_secret="test_secret_67890"
        )
        
        masked = credentials.mask_credentials()
        
        assert masked["api_key"] == "***"
        assert masked["api_secret"] == "***"
        assert masked["is_configured"] is True
    
    def test_mask_credentials_without_credentials(self):
        """認証情報がない場合のマスク処理"""
        credentials = TwitterAPICredentials()
        
        masked = credentials.mask_credentials()
        
        assert masked["api_key"] is None
        assert masked["api_secret"] is None
        assert masked["is_configured"] is False
    
    def test_repr_hides_credentials(self):
        """repr()が認証情報を隠蔽することを確認"""
        credentials = TwitterAPICredentials(
            api_key="test_key_12345",
            api_secret="test_secret_67890"
        )
        
        repr_str = repr(credentials)
        
        assert "test_key_12345" not in repr_str
        assert "test_secret_67890" not in repr_str
        assert "***" in repr_str
    
    def test_str_hides_credentials(self):
        """str()が認証情報を隠蔽することを確認"""
        credentials = TwitterAPICredentials(
            api_key="test_key_12345",
            api_secret="test_secret_67890"
        )
        
        str_str = str(credentials)
        
        assert "test_key_12345" not in str_str
        assert "test_secret_67890" not in str_str
        assert "***" in str_str


class TestTwitterEmbedConfigValidation:
    """TwitterEmbedConfig検証のテスト"""
    
    def test_validate_with_valid_config(self):
        """有効な設定値での検証成功"""
        config = TwitterEmbedConfig()
        assert config.validate(require_credentials=False) is True
    
    def test_validate_empty_embed_code_path(self):
        """埋め込みコードファイルパスが空の場合のエラー"""
        config = TwitterEmbedConfig(embed_code_path="")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate(require_credentials=False)
        
        assert "embed_code_path" in str(exc_info.value)
        assert "埋め込みコードファイルパスが空です" in str(exc_info.value)
    
    def test_validate_empty_height_path(self):
        """高さ設定ファイルパスが空の場合のエラー"""
        config = TwitterEmbedConfig(height_path="")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate(require_credentials=False)
        
        assert "height_path" in str(exc_info.value)
        assert "高さ設定ファイルパスが空です" in str(exc_info.value)
    
    def test_validate_empty_backup_dir(self):
        """バックアップディレクトリパスが空の場合のエラー"""
        config = TwitterEmbedConfig(backup_dir="")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate(require_credentials=False)
        
        assert "backup_dir" in str(exc_info.value)
        assert "バックアップディレクトリパスが空です" in str(exc_info.value)
    
    def test_validate_negative_max_retries(self):
        """最大リトライ回数が負の場合のエラー"""
        config = TwitterEmbedConfig(max_retries=-1)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate(require_credentials=False)
        
        assert "max_retries" in str(exc_info.value)
        assert "0以上である必要があります" in str(exc_info.value)
    
    def test_validate_zero_max_retries(self):
        """最大リトライ回数が0の場合は有効（リトライなし）"""
        config = TwitterEmbedConfig(max_retries=0)
        assert config.validate(require_credentials=False) is True
    
    def test_validate_negative_retry_delay(self):
        """リトライ遅延時間が負の場合のエラー"""
        config = TwitterEmbedConfig(retry_delay=-0.5)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate(require_credentials=False)
        
        assert "retry_delay" in str(exc_info.value)
        assert "0以上である必要があります" in str(exc_info.value)
    
    def test_validate_zero_retry_delay(self):
        """リトライ遅延時間が0の場合は有効（即座にリトライ）"""
        config = TwitterEmbedConfig(retry_delay=0.0)
        assert config.validate(require_credentials=False) is True
    
    def test_validate_negative_api_timeout(self):
        """APIタイムアウトが負の場合のエラー"""
        config = TwitterEmbedConfig(api_timeout=-10)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate(require_credentials=False)
        
        assert "api_timeout" in str(exc_info.value)
        assert "正の整数である必要があります" in str(exc_info.value)
    
    def test_validate_zero_api_timeout(self):
        """APIタイムアウトが0の場合のエラー"""
        config = TwitterEmbedConfig(api_timeout=0)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate(require_credentials=False)
        
        assert "api_timeout" in str(exc_info.value)
        assert "正の整数である必要があります" in str(exc_info.value)
    
    def test_validate_negative_default_height(self):
        """デフォルト高さが負の場合のエラー"""
        config = TwitterEmbedConfig(default_height=-100)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate(require_credentials=False)
        
        assert "default_height" in str(exc_info.value)
        assert "正の整数である必要があります" in str(exc_info.value)
    
    def test_validate_zero_default_height(self):
        """デフォルト高さが0の場合のエラー"""
        config = TwitterEmbedConfig(default_height=0)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate(require_credentials=False)
        
        assert "default_height" in str(exc_info.value)
        assert "正の整数である必要があります" in str(exc_info.value)
    
    def test_validate_invalid_log_level(self):
        """無効なログレベルの場合のエラー"""
        config = TwitterEmbedConfig(log_level="INVALID")
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate(require_credentials=False)
        
        assert "log_level" in str(exc_info.value)
        assert "DEBUG" in str(exc_info.value) or "INFO" in str(exc_info.value)
    
    def test_validate_valid_log_levels(self):
        """有効なログレベルの検証"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            config = TwitterEmbedConfig(log_level=level)
            assert config.validate(require_credentials=False) is True
    
    def test_validate_log_level_case_insensitive(self):
        """ログレベルの大文字小文字を区別しない検証"""
        # 小文字でも検証が通ることを確認
        config = TwitterEmbedConfig(log_level="info")
        assert config.validate(require_credentials=False) is True
        
        config = TwitterEmbedConfig(log_level="Debug")
        assert config.validate(require_credentials=False) is True



class TestConfigPaths:
    """Config パス設定のテスト"""
    
    def test_default_paths_are_relative(self):
        """デフォルトのパスが相対パスであることを確認"""
        config = Config()
        
        # デフォルトパスが相対パスであることを確認
        assert not os.path.isabs(config.lives_file_path)
        assert not os.path.isabs(config.songs_file_path)
        assert not os.path.isabs(config.song_list_file_path)
        assert not os.path.isabs(config.tweet_embed_code_path)
        assert not os.path.isabs(config.tweet_height_path)
        assert not os.path.isabs(config.css_file_path)
    
    def test_custom_paths_can_be_absolute(self):
        """カスタムパスに絶対パスを設定できることを確認"""
        if os.name == 'nt':  # Windows
            abs_path = "C:\\custom\\path\\file.tsv"
        else:  # Unix-like
            abs_path = "/custom/path/file.tsv"
        
        config = Config(lives_file_path=abs_path)
        assert config.lives_file_path == abs_path
        assert os.path.isabs(config.lives_file_path)
    
    def test_paths_preserve_format(self):
        """パスの形式が保持されることを確認"""
        custom_path = "custom/directory/file.tsv"
        config = Config(lives_file_path=custom_path)
        
        assert config.lives_file_path == custom_path


class TestTwitterEmbedConfigPaths:
    """TwitterEmbedConfig パス設定のテスト"""
    
    def test_default_paths_are_relative(self):
        """デフォルトのパスが相対パスであることを確認"""
        config = TwitterEmbedConfig()
        
        # デフォルトパスが相対パスであることを確認
        assert not os.path.isabs(config.embed_code_path)
        assert not os.path.isabs(config.height_path)
        assert not os.path.isabs(config.backup_dir)
        assert not os.path.isabs(config.log_file)
    
    def test_custom_paths_can_be_absolute(self):
        """カスタムパスに絶対パスを設定できることを確認"""
        if os.name == 'nt':  # Windows
            abs_path = "C:\\custom\\embed.html"
        else:  # Unix-like
            abs_path = "/custom/embed.html"
        
        config = TwitterEmbedConfig(embed_code_path=abs_path)
        assert config.embed_code_path == abs_path
        assert os.path.isabs(config.embed_code_path)
    
    def test_paths_preserve_format(self):
        """パスの形式が保持されることを確認"""
        custom_path = "custom/directory/embed.html"
        config = TwitterEmbedConfig(embed_code_path=custom_path)
        
        assert config.embed_code_path == custom_path
