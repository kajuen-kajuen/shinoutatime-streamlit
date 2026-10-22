"""
エラーハンドリングのテスト

src/exceptions/errors.pyのカスタム例外クラスが正しく動作することを確認するテストです。
"""

import pytest

from src.exceptions.errors import (
    ShinoutaTimeError,
    DataLoadError,
    ConfigurationError,
    TwitterEmbedError,
    InvalidURLError,
    NetworkError,
    APITimeoutError,
    RateLimitError,
    FileWriteError,
)


class TestCustomExceptions:
    """カスタム例外クラスのテスト"""
    
    def test_shinouta_time_error(self):
        """基底例外クラスが正しく動作することを確認"""
        error = ShinoutaTimeError("テストエラー")
        
        assert isinstance(error, Exception)
        assert str(error) == "テストエラー"
    
    def test_data_load_error(self):
        """データ読み込みエラーが正しく動作することを確認"""
        file_path = "data/test.tsv"
        message = "ファイルが見つかりません"
        
        error = DataLoadError(file_path, message)
        
        assert isinstance(error, ShinoutaTimeError)
        assert error.file_path == file_path
        assert error.message == message
        assert file_path in str(error)
        assert message in str(error)
    
    
    def test_configuration_error(self):
        """設定エラーが正しく動作することを確認"""
        setting = "cache_ttl"
        message = "キャッシュTTLは0以上である必要があります"
        
        error = ConfigurationError(setting, message)
        
        assert isinstance(error, ShinoutaTimeError)
        assert error.setting == setting
        assert error.message == message
        assert setting in str(error)
        assert message in str(error)
    
    def test_exception_inheritance(self):
        """全てのカスタム例外がShinoutaTimeErrorを継承していることを確認"""
        assert issubclass(DataLoadError, ShinoutaTimeError)
        assert issubclass(ConfigurationError, ShinoutaTimeError)
        assert issubclass(TwitterEmbedError, ShinoutaTimeError)
        assert issubclass(InvalidURLError, TwitterEmbedError)
        assert issubclass(NetworkError, TwitterEmbedError)
        assert issubclass(APITimeoutError, TwitterEmbedError)
        assert issubclass(RateLimitError, TwitterEmbedError)
        assert issubclass(FileWriteError, TwitterEmbedError)
    
    def test_exception_can_be_raised(self):
        """例外が正しく発生することを確認"""
        with pytest.raises(DataLoadError) as exc_info:
            raise DataLoadError("test.tsv", "テストエラー")
        
        assert "test.tsv" in str(exc_info.value)
        assert "テストエラー" in str(exc_info.value)
    
    def test_exception_can_be_caught_as_base_class(self):
        """基底クラスで例外をキャッチできることを確認"""
        try:
            raise DataLoadError("test.tsv", "テストエラー")
        except ShinoutaTimeError as e:
            assert isinstance(e, DataLoadError)
        except Exception:
            pytest.fail("ShinoutaTimeErrorでキャッチできませんでした")


class TestTwitterEmbedExceptions:
    """Twitter埋め込み機能用の例外クラスのテスト"""
    
    def test_twitter_embed_error(self):
        """Twitter埋め込み機能の基底例外クラスが正しく動作することを確認"""
        error = TwitterEmbedError("テストエラー")
        
        assert isinstance(error, ShinoutaTimeError)
        assert str(error) == "テストエラー"
    
    def test_invalid_url_error(self):
        """無効なURL形式エラーが正しく動作することを確認"""
        url = "https://example.com/invalid"
        error = InvalidURLError(url)
        
        assert isinstance(error, TwitterEmbedError)
        assert error.url == url
        assert url in str(error)
        assert "無効なツイートURL形式です" in str(error)
    
    def test_invalid_url_error_with_custom_message(self):
        """カスタムメッセージ付きの無効なURL形式エラーが正しく動作することを確認"""
        url = "https://example.com/invalid"
        message = "カスタムエラーメッセージ"
        error = InvalidURLError(url, message)
        
        assert error.url == url
        assert error.message == message
        assert url in str(error)
        assert message in str(error)
    
    def test_network_error(self):
        """ネットワーク接続エラーが正しく動作することを確認"""
        error = NetworkError()
        
        assert isinstance(error, TwitterEmbedError)
        assert "ネットワーク接続エラーが発生しました" in str(error)
    
    def test_network_error_with_original_error(self):
        """元の例外付きのネットワーク接続エラーが正しく動作することを確認"""
        original = ConnectionError("接続がタイムアウトしました")
        error = NetworkError("接続に失敗しました", original)
        
        assert error.original_error == original
        assert "接続に失敗しました" in str(error)
        assert "接続がタイムアウトしました" in str(error)
    
    def test_api_timeout_error(self):
        """APIタイムアウトエラーが正しく動作することを確認"""
        timeout = 30.0
        error = APITimeoutError(timeout)
        
        assert isinstance(error, TwitterEmbedError)
        assert error.timeout_seconds == timeout
        assert "APIリクエストがタイムアウトしました" in str(error)
        assert "30.0秒" in str(error)
    
    def test_rate_limit_error(self):
        """レート制限エラーが正しく動作することを確認"""
        error = RateLimitError()
        
        assert isinstance(error, TwitterEmbedError)
        assert "APIレート制限に達しました" in str(error)
    
    def test_rate_limit_error_with_reset_time(self):
        """リセット時刻付きのレート制限エラーが正しく動作することを確認"""
        reset_time = "2024-01-01 12:00:00"
        error = RateLimitError(reset_time)
        
        assert error.reset_time == reset_time
        assert "APIレート制限に達しました" in str(error)
        assert reset_time in str(error)
    
    def test_file_write_error(self):
        """ファイル書き込みエラーが正しく動作することを確認"""
        file_path = "data/tweet_embed_code.html"
        error = FileWriteError(file_path)
        
        assert isinstance(error, TwitterEmbedError)
        assert error.file_path == file_path
        assert file_path in str(error)
        assert "ファイルへの書き込みに失敗しました" in str(error)
    
    def test_file_write_error_with_original_error(self):
        """元の例外付きのファイル書き込みエラーが正しく動作することを確認"""
        file_path = "data/tweet_embed_code.html"
        original = PermissionError("書き込み権限がありません")
        error = FileWriteError(file_path, "書き込みに失敗", original)
        
        assert error.file_path == file_path
        assert error.original_error == original
        assert file_path in str(error)
        assert "書き込みに失敗" in str(error)
        assert "書き込み権限がありません" in str(error)
    
    def test_twitter_embed_exceptions_can_be_raised(self):
        """Twitter埋め込み機能の例外が正しく発生することを確認"""
        with pytest.raises(InvalidURLError) as exc_info:
            raise InvalidURLError("https://example.com")
        
        assert "https://example.com" in str(exc_info.value)
        
        with pytest.raises(NetworkError):
            raise NetworkError()
        
        with pytest.raises(APITimeoutError):
            raise APITimeoutError(30.0)
        
        with pytest.raises(RateLimitError):
            raise RateLimitError()
        
        with pytest.raises(FileWriteError):
            raise FileWriteError("test.html")
    
    def test_twitter_embed_exceptions_can_be_caught_as_base_class(self):
        """Twitter埋め込み機能の例外が基底クラスでキャッチできることを確認"""
        try:
            raise InvalidURLError("https://example.com")
        except TwitterEmbedError as e:
            assert isinstance(e, InvalidURLError)
        except Exception:
            pytest.fail("TwitterEmbedErrorでキャッチできませんでした")


class TestErrorScenarios:
    """実際のエラーシナリオのテスト"""
    
    def test_data_load_error_scenario(self):
        """データ読み込みエラーのシナリオをテスト"""
        def load_data(file_path):
            """データ読み込みをシミュレート"""
            if not file_path.endswith(".tsv"):
                raise DataLoadError(file_path, "TSVファイルではありません")
            return True
        
        # 正常系
        assert load_data("data.tsv") is True
        
        # 異常系
        with pytest.raises(DataLoadError) as exc_info:
            load_data("data.csv")
        
        assert "data.csv" in str(exc_info.value)
        assert "TSVファイルではありません" in str(exc_info.value)
    
    
    def test_configuration_error_scenario(self):
        """設定エラーのシナリオをテスト"""
        def validate_config(cache_ttl):
            """設定検証をシミュレート"""
            if cache_ttl < 0:
                raise ConfigurationError(
                    "cache_ttl",
                    f"キャッシュTTLは0以上である必要があります: {cache_ttl}"
                )
            return True
        
        # 正常系
        assert validate_config(3600) is True
        assert validate_config(0) is True
        
        # 異常系
        with pytest.raises(ConfigurationError) as exc_info:
            validate_config(-1)
        
        assert "cache_ttl" in str(exc_info.value)
        assert "0以上" in str(exc_info.value)
