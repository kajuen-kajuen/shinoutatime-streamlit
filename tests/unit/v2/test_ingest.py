"""取り込み(取得結果・下書き・追記・YouTube API)のテスト。コメントはすべて架空"""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.core.validation import validate_dataset
from src.ingest.capture import Capture, Comment, from_ytdlp_info, load_capture, save_capture
from src.ingest.parser import (build_content_row, build_staged_rows, choose_comment,
                               extract_timestamp_lines, match_song, split_song_text)
from src.ingest.staging import apply_staged, load_staged, save_staged
from src.ingest.youtube_api import YouTubeApiClient, parse_duration
from tests.unit.v2.conftest import make_dataset

TIMESTAMP_COMMENT = """配信おつかれさまでした!
0:05:00 はじまりの歌/テストバンド/アニメ「架空」ED/2015
12:30 Blue Sky／Alpha
[1:02:03] (リクエスト)夜明けの歌 / 架空シンガー
1:10:00 ヒーロー(1chorus)/架空シンガー
雑談のひとこと
"""


def make_capture(**overrides) -> Capture:
    data = dict(
        content_id="yt:AAAAAAAAAAA", platform="youtube", type="live",
        url="https://www.youtube.com/watch?v=AAAAAAAAAAA", title="【弾き語り】夜の歌枠",
        published_at="2025-05-01T20:00:00+09:00", captured_by="browser", captured_at="2025-05-02T00:00:00+09:00",
        comments=[Comment("きれいな声!", "viewer1", 3), Comment(TIMESTAMP_COMMENT, "stamp", 10),
                  Comment("0:01:00 ここすき", "viewer2", 1)],
    )
    data.update(overrides)
    return Capture(**data)


class TestCapture:
    def test_valid(self):
        assert make_capture().validate() == []

    def test_invalid_prefix_and_type(self):
        problems = make_capture(content_id="x:1", type="movie").validate()
        assert len(problems) == 2

    def test_save_and_load(self, tmp_path):
        path = save_capture(make_capture(), tmp_path)
        assert path.name == "yt_AAAAAAAAAAA.json"
        assert load_capture(path).comments[1].author == "stamp"

    def test_from_ytdlp_info(self):
        info = {"id": "AAAAAAAAAAA", "title": "t", "release_timestamp": 1745753340, "description": "d",
                "channel": "c", "duration": 3600,
                "comments": [{"text": "0:01:00 x/y", "author": "a", "like_count": 2, "parent": "root"},
                             {"text": "reply", "author": "b", "parent": "zzz"}]}
        capture = from_ytdlp_info(info)
        assert capture.published_at == "2025-04-27T20:29:00+09:00"
        assert capture.url == "https://www.youtube.com/watch?v=AAAAAAAAAAA"
        assert [c.text for c in capture.comments] == ["0:01:00 x/y"]
        assert capture.validate() == []


class TestParser:
    def test_extract_lines(self):
        lines = extract_timestamp_lines(TIMESTAMP_COMMENT)
        assert [l.start for l in lines] == ["0:05:00", "0:12:30", "1:02:03", "1:10:00"]
        assert lines[2].text == "(リクエスト)夜明けの歌 / 架空シンガー"

    @pytest.mark.parametrize("text, title, artist, work, year, part, note", [
        ("はじまりの歌/テストバンド/アニメ「架空」ED/2015", "はじまりの歌", "テストバンド", "アニメ「架空」ED", "2015", "", ""),
        ("Blue Sky／Alpha", "Blue Sky", "Alpha", "", "", "", ""),
        ("(リクエスト)夜明けの歌 / 架空シンガー", "夜明けの歌", "架空シンガー", "", "", "", "リクエスト"),
        ("ヒーロー(1chorus)/架空シンガー", "ヒーロー", "架空シンガー", "", "", "1chorus", ""),
        ("忘れじの歌 (short ver)/X", "忘れじの歌", "X", "", "", "short", ""),
        ("曲名だけ", "曲名だけ", "", "", "", "", ""),
        ("はじまりの歌\tテストバンド", "はじまりの歌", "テストバンド", "", "", "", ""),
        ("はじまりの歌（テストバンド）", "はじまりの歌", "テストバンド", "", "", "", ""),
        ("夜明けの歌(リクエスト)", "夜明けの歌", "", "", "", "", "リクエスト"),
    ])
    def test_split(self, text, title, artist, work, year, part, note):
        s = split_song_text(text)
        assert (s.title, s.artist, s.work, s.year, s.part, s.note) == (title, artist, work, year, part, note)

    def test_choose_comment_with_most_lines(self):
        index, comment = choose_comment(make_capture())
        assert index == 1 and comment.author == "stamp"

    def test_paren_artist_is_flagged(self):
        assert split_song_text("はじまりの歌（テストバンド）").artist_from_paren
        assert not split_song_text("はじまりの歌/テストバンド").artist_from_paren

    def test_setlist_beats_chapter_list(self):
        """雑談の目次(時刻の行が多い)より、セットリスト(曲らしい行がある)を選ぶ"""
        chapters = "\n".join(f"0:{m:02d}:00 雑談その{m}" for m in range(10))
        setlist = "セットリスト\n0:01:00\t架空の歌\t架空シンガー\r\n0:05:00\t別の歌\t架空バンド"
        capture = make_capture(comments=[Comment(chapters, "a", 50), Comment(setlist, "b", 1)])
        index, _ = choose_comment(capture)
        assert index == 1

    def test_choose_comment_trusted(self, monkeypatch):
        monkeypatch.setenv("SHINOUTA_TRUSTED_COMMENTERS", "viewer2")
        index, _ = choose_comment(make_capture())
        assert index == 2

    def test_match_kinds(self, sample_dataset):
        assert match_song(sample_dataset, "はじまりの歌", "テストバンド").kind == "alias"
        assert match_song(sample_dataset, "ＢＬＵＥ　ＳＫＹ", "alpha").kind == "alias"
        sample_dataset["aliases"] = sample_dataset["aliases"].iloc[0:0]
        assert match_song(sample_dataset, "Blue Sky", "Alpha").kind == "exact"
        assert match_song(sample_dataset, "Blue Skyy", "?").kind == "similar"
        assert match_song(sample_dataset, "まったく別の曲", "?").kind == "new"

    def test_staged_rows(self, sample_dataset):
        rows = build_staged_rows(sample_dataset, extract_timestamp_lines(TIMESTAMP_COMMENT))
        assert list(rows["match"]) == ["alias", "alias", "new", "new"]
        assert rows.loc[0, "song_id"] == "s0001"
        assert rows.loc[3, "part"] == "1chorus"

    def test_content_row(self):
        row = build_content_row(make_capture())
        assert (row["date"], row["start_time"], row["default_style"]) == ("2025-05-01", "20:00", "弾き語り")


class TestApply:
    def _staged(self, dataset):
        rows = build_staged_rows(dataset, extract_timestamp_lines(TIMESTAMP_COMMENT))
        rows.loc[2, "song_kind"] = "カバー"
        return build_content_row(make_capture(content_id="yt:DDDDDDDDDDD", url="https://www.youtube.com/watch?v=DDDDDDDDDDD")), rows

    def test_apply_into_empty_dataset(self):
        dataset = make_dataset()
        content_row, rows = self._staged(dataset)
        result = apply_staged(dataset, content_row, rows)
        assert result.performances == 4
        assert len(result.new_songs) == 4 and len(result.new_artists) == 3
        assert list(dataset["performances"]["seq"]) == ["10", "20", "30", "40"]
        assert [i for i in validate_dataset(dataset) if i.level == "error"] == []

    def test_apply_reuses_existing(self, sample_dataset):
        content_row, rows = self._staged(sample_dataset)
        result = apply_staged(sample_dataset, content_row, rows)
        assert result.new_songs == ["s0003", "s0004"]
        assert result.new_artists == ["a0003"]

    def test_excluded_rows(self):
        dataset = make_dataset()
        content_row, rows = self._staged(dataset)
        rows.loc[3, "include"] = "n"
        assert apply_staged(dataset, content_row, rows).skipped == 1

    def test_duplicate_content_needs_replace(self, sample_dataset):
        content_row, rows = self._staged(sample_dataset)
        content_row["content_id"] = "yt:AAAAAAAAAAA"
        with pytest.raises(ValueError):
            apply_staged(sample_dataset, content_row, rows)
        apply_staged(sample_dataset, content_row, rows, replace=True)
        assert (sample_dataset["performances"]["content_id"] == "yt:AAAAAAAAAAA").sum() == 4

    def test_missing_artist_for_new_song(self):
        dataset = make_dataset()
        content_row, rows = self._staged(dataset)
        rows.loc[2, "artist"] = ""
        with pytest.raises(ValueError):
            apply_staged(dataset, content_row, rows)

    def test_staged_roundtrip(self, tmp_path, sample_dataset):
        content_row, rows = self._staged(sample_dataset)
        save_staged(content_row, rows, tmp_path)
        loaded_content, loaded_rows = load_staged("yt:DDDDDDDDDDD", tmp_path)
        assert loaded_content["content_id"] == "yt:DDDDDDDDDDD"
        assert len(loaded_rows) == 4


class TestYouTubeApi:
    def test_parse_duration(self):
        assert parse_duration("PT1H2M3S") == 3723
        assert parse_duration("PT45S") == 45
        assert parse_duration("") is None

    def test_requires_key(self, monkeypatch):
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        with pytest.raises(ValueError):
            YouTubeApiClient()

    def test_fetch_capture(self):
        session = MagicMock()
        video = {"items": [{"snippet": {"title": "t", "description": "d", "channelTitle": "c",
                                        "publishedAt": "2025-04-27T10:00:00Z"},
                            "contentDetails": {"duration": "PT2H"},
                            "liveStreamingDetails": {"actualStartTime": "2025-04-27T11:29:00Z"}}]}
        comments = {"items": [{"snippet": {"topLevelComment": {"snippet": {
            "textOriginal": "0:01:00 x/y", "authorDisplayName": "a", "likeCount": 4}}}}]}
        session.get.return_value.json.side_effect = [video, comments]
        capture = YouTubeApiClient(api_key="dummy", session=session).fetch_capture("AAAAAAAAAAA")
        assert capture.published_at == "2025-04-27T20:29:00+09:00"
        assert capture.duration_seconds == 7200
        assert capture.comments[0].likes == 4
        assert capture.validate() == []
