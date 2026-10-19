"""文字列の正規化・読みの並び順・時刻付きリンクのテスト"""

import pytest

from src.core.links import build_link, seconds_to_start, start_to_seconds
from src.core.text import normalize_for_match, reading_sort_key, to_hiragana


class TestNormalize:
    def test_katakana_to_hiragana(self):
        assert to_hiragana("サカナクション") == "さかなくしょん"

    @pytest.mark.parametrize("a, b", [
        ("Ｂｌｕｅ　Ｓｋｙ", "blue sky"),
        ("Eve feat. 初音ミク", "eve feat.初音ミク"),
        ("ドライフラワー", "どらいふらわー"),
    ])
    def test_same_after_normalize(self, a, b):
        assert normalize_for_match(a) == normalize_for_match(b)

    def test_empty(self):
        assert normalize_for_match("") == ""


class TestReadingSortKey:
    def test_group_order_symbol_alpha_kana(self):
        names = ["あいみょん", "Vaundy", "123", "yama", "いきものがかり"]
        ordered = sorted(names, key=lambda n: reading_sort_key(n))
        assert ordered == ["123", "Vaundy", "yama", "あいみょん", "いきものがかり"]

    def test_case_insensitive(self):
        assert reading_sort_key("abc") == reading_sort_key("ABC")

    def test_fallback_when_reading_empty(self):
        assert reading_sort_key("", "カ") > reading_sort_key("", "Z")

    def test_katakana_reading_equals_hiragana(self):
        assert reading_sort_key("ヨネヅ") == reading_sort_key("よねづ")


class TestLinks:
    @pytest.mark.parametrize("value, expected", [
        ("0:01:47", 107), ("1:02:03", 3723), ("26:27", 1587), ("", None), ("1:99:00", None), ("abc", None),
    ])
    def test_start_to_seconds(self, value, expected):
        assert start_to_seconds(value) == expected

    def test_seconds_to_start(self):
        assert seconds_to_start(3723) == "1:02:03"

    def test_youtube_watch(self):
        assert build_link("youtube", "https://www.youtube.com/watch?v=abc", "0:01:47") == \
            "https://www.youtube.com/watch?v=abc&t=107s"

    def test_youtube_shorts_has_no_query_yet(self):
        assert build_link("youtube", "https://www.youtube.com/shorts/abc", "0:00:05") == \
            "https://www.youtube.com/shorts/abc?t=5s"

    def test_existing_t_is_replaced(self):
        assert build_link("youtube", "https://www.youtube.com/watch?v=abc&t=10s", "0:00:20") == \
            "https://www.youtube.com/watch?v=abc&t=20s"

    @pytest.mark.parametrize("platform", ["zan", "x"])
    def test_platform_without_seek_keeps_url(self, platform):
        assert build_link(platform, "https://example.com/1", "0:10:00") == "https://example.com/1"

    def test_no_start_keeps_url(self):
        assert build_link("youtube", "https://www.youtube.com/watch?v=abc", "") == "https://www.youtube.com/watch?v=abc"
