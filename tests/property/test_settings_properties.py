"""
Settingsモジュールのプロパティベーステスト

設定管理機能の普遍的な性質を検証します。
"""

import os
from unittest.mock import patch
from hypothesis import given, strategies as st, settings
from src.config.settings import Config, TwitterAPICredentials, TwitterEmbedConfig


class TestConfigProperties:
    """Config設定のプロパティテスト"""
    
    @given(
        lives_path=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters='\x00')),
        songs_path=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters='\x00')),
        song_list_path=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters='\x00')),
        display_limit=st.integers(min_value=1, max_value=1000),
        cache_ttl=st.integers(min_value=0, max_value=86400)
    )
    @settings(max_examples=100)
    def test_property_21_environment_variable_loading_consistency(
        self,
        lives_path,
        songs_path,
        song_list_path,
        display_limit,
        cache_ttl
    ):
        """
        Feature: test-coverage-improvement, Property 21: 環境変数読み込みの一貫性
        
        **検証: 要件9.1**
        
        *すべての*環境変数設定に対して、設定値が正しく読み込まれ、型変換が正しく行われる
        """
        env_vars = {
            "SHINOUTA_LIVES_FILE_PATH": lives_path,
            "SHINOUTA_SONGS_FILE_PATH": songs_path,
            "SHINOUTA_SONG_LIST_FILE_PATH": song_list_path,
            "SHINOUTA_INITIAL_DISPLAY_LIMIT": str(display_limit),
            "SHINOUTA_CACHE_TTL": str(cache_ttl)
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            
            # 環境変数から読み込まれた値が正しいことを確認
            assert config.lives_file_path == lives_path
            assert config.songs_file_path == songs_path
            assert config.song_list_file_path == song_list_path
            
            # 型変換が正しく行われていることを確認
            assert isinstance(config.initial_display_limit, int)
            assert config.initial_display_limit == display_limit
            
            assert isinstance(config.cache_ttl, int)
            assert config.cache_ttl == cache_ttl
    
    @given(
        enable_cache=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_21_boolean_conversion_consistency(self, enable_cache):
        """
        Feature: test-coverage-improvement, Property 21: 環境変数読み込みの一貫性（ブール値）
        
        **検証: 要件9.1**
        
        *すべての*ブール値設定に対して、型変換が正しく行われる
        """
        # ブール値を文字列に変換
        bool_str = "true" if enable_cache else "false"
        
        env_vars = {
            "SHINOUTA_ENABLE_CACHE": bool_str
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            
            # ブール値が正しく変換されていることを確認
            assert isinstance(config.enable_cache, bool)
            assert config.enable_cache == enable_cache


class TestTwitterAPICredentialsProperties:
    """TwitterAPICredentials認証情報のプロパティテスト"""
    
    @given(
        api_key=st.one_of(
            st.none(), 
            st.text(
                min_size=1, 
                max_size=100, 
                alphabet=st.characters(
                    blacklist_characters='\x00',
                    blacklist_categories=('Cs',)  # サロゲート文字を除外
                )
            )
        ),
        api_secret=st.one_of(
            st.none(), 
            st.text(
                min_size=1, 
                max_size=100, 
                alphabet=st.characters(
                    blacklist_characters='\x00',
                    blacklist_categories=('Cs',)  # サロゲート文字を除外
                )
            )
        )
    )
    @settings(max_examples=100)
    def test_property_21_credentials_loading_consistency(self, api_key, api_secret):
        """
        Feature: test-coverage-improvement, Property 21: 環境変数読み込みの一貫性（認証情報）
        
        **検証: 要件9.1**
        
        *すべての*認証情報設定に対して、設定値が正しく読み込まれる
        """
        env_vars = {}
        if api_key is not None:
            env_vars["TWITTER_API_KEY"] = api_key
        if api_secret is not None:
            env_vars["TWITTER_API_SECRET"] = api_secret
        
        with patch.dict(os.environ, env_vars, clear=True):
            credentials = TwitterAPICredentials.from_env()
            
            # 環境変数から読み込まれた値が正しいことを確認
            assert credentials.api_key == api_key
            assert credentials.api_secret == api_secret
            
            # is_configured()が正しく動作することを確認
            expected_configured = (api_key is not None and api_secret is not None)
            assert credentials.is_configured() == expected_configured


class TestTwitterEmbedConfigProperties:
    """TwitterEmbedConfig設定のプロパティテスト"""
    
    @given(
        max_retries=st.integers(min_value=0, max_value=10),
        retry_delay=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        api_timeout=st.integers(min_value=1, max_value=300),
        default_height=st.integers(min_value=1, max_value=2000)
    )
    @settings(max_examples=100)
    def test_property_21_embed_config_loading_consistency(
        self,
        max_retries,
        retry_delay,
        api_timeout,
        default_height
    ):
        """
        Feature: test-coverage-improvement, Property 21: 環境変数読み込みの一貫性（埋め込み設定）
        
        **検証: 要件9.1**
        
        *すべての*埋め込み設定に対して、設定値が正しく読み込まれ、型変換が正しく行われる
        """
        env_vars = {
            "TWITTER_API_MAX_RETRIES": str(max_retries),
            "TWITTER_API_RETRY_DELAY": str(retry_delay),
            "TWITTER_API_TIMEOUT": str(api_timeout),
            "TWITTER_DEFAULT_HEIGHT": str(default_height)
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = TwitterEmbedConfig.from_env()
            
            # 環境変数から読み込まれた値が正しいことを確認
            assert isinstance(config.max_retries, int)
            assert config.max_retries == max_retries
            
            assert isinstance(config.retry_delay, float)
            assert abs(config.retry_delay - retry_delay) < 0.01  # 浮動小数点の比較
            
            assert isinstance(config.api_timeout, int)
            assert config.api_timeout == api_timeout
            
            assert isinstance(config.default_height, int)
            assert config.default_height == default_height



class TestConfigValidationProperties:
    """Config設定値検証のプロパティテスト"""
    
    @given(
        initial_display_limit=st.integers(max_value=0)
    )
    @settings(max_examples=100)
    def test_property_22_invalid_initial_display_limit_validation(self, initial_display_limit):
        """
        Feature: test-coverage-improvement, Property 22: 無効な値検証の一貫性
        
        **検証: 要件9.3**
        
        *すべての*無効な初期表示件数（0以下）に対して、適切なバリデーションエラーが発生する
        """
        from src.exceptions.errors import ConfigurationError
        
        config = Config(initial_display_limit=initial_display_limit)
        
        # 無効な値に対してエラーが発生することを確認
        try:
            config.validate()
            assert False, f"Expected ConfigurationError for initial_display_limit={initial_display_limit}"
        except ConfigurationError as e:
            # エラーメッセージに適切な情報が含まれていることを確認
            assert "initial_display_limit" in str(e)
    
    @given(
        display_increment=st.integers(max_value=0)
    )
    @settings(max_examples=100)
    def test_property_22_invalid_display_increment_validation(self, display_increment):
        """
        Feature: test-coverage-improvement, Property 22: 無効な値検証の一貫性
        
        **検証: 要件9.3**
        
        *すべての*無効な表示増分（0以下）に対して、適切なバリデーションエラーが発生する
        """
        from src.exceptions.errors import ConfigurationError
        
        config = Config(display_increment=display_increment)
        
        # 無効な値に対してエラーが発生することを確認
        try:
            config.validate()
            assert False, f"Expected ConfigurationError for display_increment={display_increment}"
        except ConfigurationError as e:
            # エラーメッセージに適切な情報が含まれていることを確認
            assert "display_increment" in str(e)
    
    @given(
        cache_ttl=st.integers(max_value=-1)
    )
    @settings(max_examples=100)
    def test_property_22_invalid_cache_ttl_validation(self, cache_ttl):
        """
        Feature: test-coverage-improvement, Property 22: 無効な値検証の一貫性
        
        **検証: 要件9.3**
        
        *すべての*無効なキャッシュTTL（負の値）に対して、適切なバリデーションエラーが発生する
        """
        from src.exceptions.errors import ConfigurationError
        
        config = Config(cache_ttl=cache_ttl)
        
        # 無効な値に対してエラーが発生することを確認
        try:
            config.validate()
            assert False, f"Expected ConfigurationError for cache_ttl={cache_ttl}"
        except ConfigurationError as e:
            # エラーメッセージに適切な情報が含まれていることを確認
            assert "cache_ttl" in str(e)
    
    @given(
        layout=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(blacklist_characters='\x00')
        ).filter(lambda x: x not in ["centered", "wide"])
    )
    @settings(max_examples=100)
    def test_property_22_invalid_layout_validation(self, layout):
        """
        Feature: test-coverage-improvement, Property 22: 無効な値検証の一貫性
        
        **検証: 要件9.3**
        
        *すべての*無効なレイアウト値に対して、適切なバリデーションエラーが発生する
        """
        from src.exceptions.errors import ConfigurationError
        
        config = Config(layout=layout)
        
        # 無効な値に対してエラーが発生することを確認
        try:
            config.validate()
            assert False, f"Expected ConfigurationError for layout={layout}"
        except ConfigurationError as e:
            # エラーメッセージに適切な情報が含まれていることを確認
            assert "layout" in str(e)


class TestTwitterEmbedConfigValidationProperties:
    """TwitterEmbedConfig設定値検証のプロパティテスト"""
    
    @given(
        max_retries=st.integers(max_value=-1)
    )
    @settings(max_examples=100)
    def test_property_22_invalid_max_retries_validation(self, max_retries):
        """
        Feature: test-coverage-improvement, Property 22: 無効な値検証の一貫性
        
        **検証: 要件9.3**
        
        *すべての*無効な最大リトライ回数（負の値）に対して、適切なバリデーションエラーが発生する
        """
        from src.exceptions.errors import ConfigurationError
        
        config = TwitterEmbedConfig(max_retries=max_retries)
        
        # 無効な値に対してエラーが発生することを確認
        try:
            config.validate(require_credentials=False)
            assert False, f"Expected ConfigurationError for max_retries={max_retries}"
        except ConfigurationError as e:
            # エラーメッセージに適切な情報が含まれていることを確認
            assert "max_retries" in str(e)
    
    @given(
        retry_delay=st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_property_22_invalid_retry_delay_validation(self, retry_delay):
        """
        Feature: test-coverage-improvement, Property 22: 無効な値検証の一貫性
        
        **検証: 要件9.3**
        
        *すべての*無効なリトライ遅延時間（負の値）に対して、適切なバリデーションエラーが発生する
        """
        from src.exceptions.errors import ConfigurationError
        
        config = TwitterEmbedConfig(retry_delay=retry_delay)
        
        # 無効な値に対してエラーが発生することを確認
        try:
            config.validate(require_credentials=False)
            assert False, f"Expected ConfigurationError for retry_delay={retry_delay}"
        except ConfigurationError as e:
            # エラーメッセージに適切な情報が含まれていることを確認
            assert "retry_delay" in str(e)
    
    @given(
        api_timeout=st.integers(max_value=0)
    )
    @settings(max_examples=100)
    def test_property_22_invalid_api_timeout_validation(self, api_timeout):
        """
        Feature: test-coverage-improvement, Property 22: 無効な値検証の一貫性
        
        **検証: 要件9.3**
        
        *すべての*無効なAPIタイムアウト（0以下）に対して、適切なバリデーションエラーが発生する
        """
        from src.exceptions.errors import ConfigurationError
        
        config = TwitterEmbedConfig(api_timeout=api_timeout)
        
        # 無効な値に対してエラーが発生することを確認
        try:
            config.validate(require_credentials=False)
            assert False, f"Expected ConfigurationError for api_timeout={api_timeout}"
        except ConfigurationError as e:
            # エラーメッセージに適切な情報が含まれていることを確認
            assert "api_timeout" in str(e)
    
    @given(
        default_height=st.integers(max_value=0)
    )
    @settings(max_examples=100)
    def test_property_22_invalid_default_height_validation(self, default_height):
        """
        Feature: test-coverage-improvement, Property 22: 無効な値検証の一貫性
        
        **検証: 要件9.3**
        
        *すべての*無効なデフォルト高さ（0以下）に対して、適切なバリデーションエラーが発生する
        """
        from src.exceptions.errors import ConfigurationError
        
        config = TwitterEmbedConfig(default_height=default_height)
        
        # 無効な値に対してエラーが発生することを確認
        try:
            config.validate(require_credentials=False)
            assert False, f"Expected ConfigurationError for default_height={default_height}"
        except ConfigurationError as e:
            # エラーメッセージに適切な情報が含まれていることを確認
            assert "default_height" in str(e)
    
    @given(
        log_level=st.text(
            min_size=1, 
            max_size=20, 
            alphabet=st.characters(blacklist_characters='\x00')
        ).filter(
            lambda x: x.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
    )
    @settings(max_examples=100)
    def test_property_22_invalid_log_level_validation(self, log_level):
        """
        Feature: test-coverage-improvement, Property 22: 無効な値検証の一貫性
        
        **検証: 要件9.3**
        
        *すべての*無効なログレベルに対して、適切なバリデーションエラーが発生する
        """
        from src.exceptions.errors import ConfigurationError
        
        config = TwitterEmbedConfig(log_level=log_level)
        
        # 無効な値に対してエラーが発生することを確認
        try:
            config.validate(require_credentials=False)
            assert False, f"Expected ConfigurationError for log_level={log_level}"
        except ConfigurationError as e:
            # エラーメッセージに適切な情報が含まれていることを確認
            assert "log_level" in str(e)



class TestConfigPathProperties:
    """Config パス設定のプロパティテスト"""
    
    @given(
        path=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters='\x00'))
    )
    @settings(max_examples=100)
    def test_property_23_path_preservation_consistency(self, path):
        """
        Feature: test-coverage-improvement, Property 23: パス解決の一貫性
        
        **検証: 要件9.4**
        
        *すべての*パス文字列に対して、設定されたパスが保持される
        """
        config = Config(lives_file_path=path)
        
        # パスが正しく保持されていることを確認
        assert config.lives_file_path == path
    
    @given(
        relative_path=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(blacklist_characters='\x00')
        ).filter(lambda x: not os.path.isabs(x))
    )
    @settings(max_examples=100)
    def test_property_23_relative_path_consistency(self, relative_path):
        """
        Feature: test-coverage-improvement, Property 23: パス解決の一貫性（相対パス）
        
        **検証: 要件9.4**
        
        *すべての*相対パスに対して、相対パスとして保持される
        """
        config = Config(
            lives_file_path=relative_path,
            songs_file_path=relative_path,
            song_list_file_path=relative_path
        )
        
        # 相対パスが保持されていることを確認
        assert config.lives_file_path == relative_path
        assert config.songs_file_path == relative_path
        assert config.song_list_file_path == relative_path


class TestTwitterEmbedConfigPathProperties:
    """TwitterEmbedConfig パス設定のプロパティテスト"""
    
    @given(
        path=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters='\x00'))
    )
    @settings(max_examples=100)
    def test_property_23_embed_path_preservation_consistency(self, path):
        """
        Feature: test-coverage-improvement, Property 23: パス解決の一貫性（埋め込み設定）
        
        **検証: 要件9.4**
        
        *すべての*パス文字列に対して、設定されたパスが保持される
        """
        config = TwitterEmbedConfig(
            embed_code_path=path,
            height_path=path,
            backup_dir=path
        )
        
        # パスが正しく保持されていることを確認
        assert config.embed_code_path == path
        assert config.height_path == path
        assert config.backup_dir == path
    
    @given(
        relative_path=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(blacklist_characters='\x00')
        ).filter(lambda x: not os.path.isabs(x))
    )
    @settings(max_examples=100)
    def test_property_23_embed_relative_path_consistency(self, relative_path):
        """
        Feature: test-coverage-improvement, Property 23: パス解決の一貫性（相対パス・埋め込み設定）
        
        **検証: 要件9.4**
        
        *すべての*相対パスに対して、相対パスとして保持される
        """
        config = TwitterEmbedConfig(
            embed_code_path=relative_path,
            height_path=relative_path,
            backup_dir=relative_path,
            log_file=relative_path
        )
        
        # 相対パスが保持されていることを確認
        assert config.embed_code_path == relative_path
        assert config.height_path == relative_path
        assert config.backup_dir == relative_path
        assert config.log_file == relative_path


class TestConfigUpdateProperties:
    """Config設定更新のプロパティテスト"""
    
    @given(
        initial_limit=st.integers(min_value=1, max_value=1000),
        new_limit=st.integers(min_value=1, max_value=1000),
        initial_increment=st.integers(min_value=1, max_value=500),
        new_increment=st.integers(min_value=1, max_value=500)
    )
    @settings(max_examples=100)
    def test_property_24_config_update_consistency(
        self,
        initial_limit,
        new_limit,
        initial_increment,
        new_increment
    ):
        """
        Feature: test-coverage-improvement, Property 24: 設定更新の一貫性
        
        **検証: 要件9.5**
        
        *すべての*設定値に対して、更新後の値が正しく反映され、取得できる
        """
        # 初期設定でConfigを作成
        config = Config(
            initial_display_limit=initial_limit,
            display_increment=initial_increment
        )
        
        # 初期値が正しく設定されていることを確認
        assert config.initial_display_limit == initial_limit
        assert config.display_increment == initial_increment
        
        # 設定を更新
        config.initial_display_limit = new_limit
        config.display_increment = new_increment
        
        # 更新後の値が正しく反映されていることを確認
        assert config.initial_display_limit == new_limit
        assert config.display_increment == new_increment
    
    @given(
        initial_cache_ttl=st.integers(min_value=0, max_value=86400),
        new_cache_ttl=st.integers(min_value=0, max_value=86400),
        initial_enable_cache=st.booleans(),
        new_enable_cache=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_24_cache_config_update_consistency(
        self,
        initial_cache_ttl,
        new_cache_ttl,
        initial_enable_cache,
        new_enable_cache
    ):
        """
        Feature: test-coverage-improvement, Property 24: 設定更新の一貫性（キャッシュ設定）
        
        **検証: 要件9.5**
        
        *すべての*キャッシュ設定値に対して、更新後の値が正しく反映され、取得できる
        """
        # 初期設定でConfigを作成
        config = Config(
            cache_ttl=initial_cache_ttl,
            enable_cache=initial_enable_cache
        )
        
        # 初期値が正しく設定されていることを確認
        assert config.cache_ttl == initial_cache_ttl
        assert config.enable_cache == initial_enable_cache
        
        # 設定を更新
        config.cache_ttl = new_cache_ttl
        config.enable_cache = new_enable_cache
        
        # 更新後の値が正しく反映されていることを確認
        assert config.cache_ttl == new_cache_ttl
        assert config.enable_cache == new_enable_cache
    
    @given(
        initial_path=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters='\x00')),
        new_path=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters='\x00'))
    )
    @settings(max_examples=100)
    def test_property_24_path_config_update_consistency(
        self,
        initial_path,
        new_path
    ):
        """
        Feature: test-coverage-improvement, Property 24: 設定更新の一貫性（パス設定）
        
        **検証: 要件9.5**
        
        *すべての*パス設定値に対して、更新後の値が正しく反映され、取得できる
        """
        # 初期設定でConfigを作成
        config = Config(
            lives_file_path=initial_path,
            songs_file_path=initial_path,
            song_list_file_path=initial_path
        )
        
        # 初期値が正しく設定されていることを確認
        assert config.lives_file_path == initial_path
        assert config.songs_file_path == initial_path
        assert config.song_list_file_path == initial_path
        
        # 設定を更新
        config.lives_file_path = new_path
        config.songs_file_path = new_path
        config.song_list_file_path = new_path
        
        # 更新後の値が正しく反映されていることを確認
        assert config.lives_file_path == new_path
        assert config.songs_file_path == new_path
        assert config.song_list_file_path == new_path


class TestTwitterEmbedConfigUpdateProperties:
    """TwitterEmbedConfig設定更新のプロパティテスト"""
    
    @given(
        initial_retries=st.integers(min_value=0, max_value=10),
        new_retries=st.integers(min_value=0, max_value=10),
        initial_delay=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        new_delay=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_property_24_embed_config_update_consistency(
        self,
        initial_retries,
        new_retries,
        initial_delay,
        new_delay
    ):
        """
        Feature: test-coverage-improvement, Property 24: 設定更新の一貫性（埋め込み設定）
        
        **検証: 要件9.5**
        
        *すべての*埋め込み設定値に対して、更新後の値が正しく反映され、取得できる
        """
        # 初期設定でTwitterEmbedConfigを作成
        config = TwitterEmbedConfig(
            max_retries=initial_retries,
            retry_delay=initial_delay
        )
        
        # 初期値が正しく設定されていることを確認
        assert config.max_retries == initial_retries
        assert abs(config.retry_delay - initial_delay) < 0.01
        
        # 設定を更新
        config.max_retries = new_retries
        config.retry_delay = new_delay
        
        # 更新後の値が正しく反映されていることを確認
        assert config.max_retries == new_retries
        assert abs(config.retry_delay - new_delay) < 0.01
    
    @given(
        initial_timeout=st.integers(min_value=1, max_value=300),
        new_timeout=st.integers(min_value=1, max_value=300),
        initial_height=st.integers(min_value=1, max_value=2000),
        new_height=st.integers(min_value=1, max_value=2000)
    )
    @settings(max_examples=100)
    def test_property_24_embed_api_config_update_consistency(
        self,
        initial_timeout,
        new_timeout,
        initial_height,
        new_height
    ):
        """
        Feature: test-coverage-improvement, Property 24: 設定更新の一貫性（API設定）
        
        **検証: 要件9.5**
        
        *すべての*API設定値に対して、更新後の値が正しく反映され、取得できる
        """
        # 初期設定でTwitterEmbedConfigを作成
        config = TwitterEmbedConfig(
            api_timeout=initial_timeout,
            default_height=initial_height
        )
        
        # 初期値が正しく設定されていることを確認
        assert config.api_timeout == initial_timeout
        assert config.default_height == initial_height
        
        # 設定を更新
        config.api_timeout = new_timeout
        config.default_height = new_height
        
        # 更新後の値が正しく反映されていることを確認
        assert config.api_timeout == new_timeout
        assert config.default_height == new_height
