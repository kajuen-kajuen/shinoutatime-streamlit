"""
Settingsモジュールのプロパティベーステスト

設定管理機能の普遍的な性質を検証します。
"""

import os
from unittest.mock import patch
from hypothesis import given, strategies as st, settings
from src.config.settings import Config


class TestConfigProperties:
    """Config設定のプロパティテスト"""
    
    @given(
        data_dir_path=st.text(
            min_size=1, 
            max_size=100, 
            alphabet=st.characters(
                blacklist_characters='\x00',
                blacklist_categories=('Cs',)  # サロゲート文字を除外
            )
        ),
        css_path=st.text(
            min_size=1, 
            max_size=100, 
            alphabet=st.characters(
                blacklist_characters='\x00',
                blacklist_categories=('Cs',)  # サロゲート文字を除外
            )
        ),
        embed_path=st.text(
            min_size=1, 
            max_size=100, 
            alphabet=st.characters(
                blacklist_characters='\x00',
                blacklist_categories=('Cs',)  # サロゲート文字を除外
            )
        ),
        display_limit=st.integers(min_value=1, max_value=1000),
        cache_ttl=st.integers(min_value=0, max_value=86400)
    )
    @settings(max_examples=100)
    def test_property_21_environment_variable_loading_consistency(
        self,
        data_dir_path,
        css_path,
        embed_path,
        display_limit,
        cache_ttl
    ):
        """
        Feature: test-coverage-improvement, Property 21: 環境変数読み込みの一貫性
        
        **検証: 要件9.1**
        
        *すべての*環境変数設定に対して、設定値が正しく読み込まれ、型変換が正しく行われる
        """
        env_vars = {
            "SHINOUTA_V2_DATA_DIR": data_dir_path,
            "SHINOUTA_CSS_FILE_PATH": css_path,
            "SHINOUTA_TWEET_EMBED_CODE_PATH": embed_path,
            "SHINOUTA_INITIAL_DISPLAY_LIMIT": str(display_limit),
            "SHINOUTA_CACHE_TTL": str(cache_ttl)
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            
            # 環境変数から読み込まれた値が正しいことを確認
            assert config.v2_data_dir == data_dir_path
            assert config.css_file_path == css_path
            assert config.tweet_embed_code_path == embed_path
            
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
        config = Config(v2_data_dir=path)
        
        # パスが正しく保持されていることを確認
        assert config.v2_data_dir == path
    
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
            v2_data_dir=relative_path,
            css_file_path=relative_path,
            tweet_embed_code_path=relative_path
        )
        
        # 相対パスが保持されていることを確認
        assert config.v2_data_dir == relative_path
        assert config.css_file_path == relative_path
        assert config.tweet_embed_code_path == relative_path


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
            v2_data_dir=initial_path,
            css_file_path=initial_path,
            tweet_embed_code_path=initial_path
        )
        
        # 初期値が正しく設定されていることを確認
        assert config.v2_data_dir == initial_path
        assert config.css_file_path == initial_path
        assert config.tweet_embed_code_path == initial_path
        
        # 設定を更新
        config.v2_data_dir = new_path
        config.css_file_path = new_path
        config.tweet_embed_code_path = new_path
        
        # 更新後の値が正しく反映されていることを確認
        assert config.v2_data_dir == new_path
        assert config.css_file_path == new_path
        assert config.tweet_embed_code_path == new_path
