"""
URLGeneratorのユニットテスト
"""
import pytest
from src.utils.url_generator import URLGenerator


class TestURLGenerator:
    """URLGeneratorのテストクラス"""
    
    @pytest.fixture
    def generator(self):
        """テスト用のURLGeneratorインスタンス"""
        return URLGenerator()
    
    def test_parse_timestamp_hms_format(self, generator):
        """HH:MM:SS形式のタイムスタンプをパース"""
        # 要件4.2: "HH:MM:SS"形式を秒数に変換
        assert generator.parse_timestamp("01:23:45") == 5025
        assert generator.parse_timestamp("00:00:01") == 1
        assert generator.parse_timestamp("10:30:15") == 37815
    
    def test_parse_timestamp_hms_single_digit_hour(self, generator):
        """H:MM:SS形式（時間が1桁）のタイムスタンプをパース"""
        # 要件4.4: 時間部分が1桁の場合も正しく変換
        assert generator.parse_timestamp("1:23:45") == 5025
        assert generator.parse_timestamp("2:00:00") == 7200
        assert generator.parse_timestamp("9:59:59") == 35999
    
    def test_parse_timestamp_ms_format(self, generator):
        """MM:SS形式のタイムスタンプをパース"""
        # 要件4.3: "MM:SS"形式を秒数に変換
        assert generator.parse_timestamp("12:34") == 754
        assert generator.parse_timestamp("00:30") == 30
        assert generator.parse_timestamp("59:59") == 3599
    
    def test_parse_timestamp_invalid_format(self, generator):
        """不正な形式のタイムスタンプはNoneを返す"""
        assert generator.parse_timestamp("invalid") is None
        assert generator.parse_timestamp("12") is None
        assert generator.parse_timestamp("12:34:56:78") is None
        assert generator.parse_timestamp("") is None
    
    def test_generate_timestamped_url_basic(self, generator):
        """基本的なタイムスタンプ付きURL生成"""
        # 要件4.1: ベースURLにタイムスタンプパラメータを付加
        url = generator.generate_timestamped_url(
            "https://youtube.com/watch?v=abc123",
            "1:23:45"
        )
        assert "youtube.com/watch" in url
        assert "v=abc123" in url
        assert "t=5025" in url
    
    def test_generate_timestamped_url_with_existing_params(self, generator):
        """既存のクエリパラメータがある場合"""
        # 要件4.5: 既存のパラメータを保持しつつタイムスタンプを追加
        url = generator.generate_timestamped_url(
            "https://youtube.com/watch?v=abc123&list=playlist",
            "12:34"
        )
        assert "v=abc123" in url
        assert "list=playlist" in url
        assert "t=754" in url
    
    def test_generate_timestamped_url_empty_inputs(self, generator):
        """空の入力の場合はベースURLをそのまま返す"""
        url1 = generator.generate_timestamped_url("", "12:34")
        assert url1 == ""
        
        url2 = generator.generate_timestamped_url("https://youtube.com/watch?v=abc", "")
        assert url2 == "https://youtube.com/watch?v=abc"
    
    def test_generate_timestamped_url_invalid_timestamp(self, generator):
        """不正なタイムスタンプの場合はベースURLをそのまま返す"""
        base_url = "https://youtube.com/watch?v=abc123"
        url = generator.generate_timestamped_url(base_url, "invalid")
        assert url == base_url
