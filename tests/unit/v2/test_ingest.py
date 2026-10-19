"""取り込み(取得結果・下書き・追記・YouTube API)のテスト。コメントはすべて架空"""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.core.validation import validate_dataset
from src.ingest.capture import Capture, Comment, from_ytdlp_info, load_capture, save_capture
from src.ingest.parser import (build_content_row, build_rows_from_title, build_staged_rows, choose_comment,
                               extract_timestamp_lines, match_song, song_from_title, split_feat,
                               split_song_text, style_hint)
from src.ingest.skips import add_skip, load_skips
from src.ingest.staging import apply_staged, load_staged, save_staged
from src.ingest.youtube_api import YouTubeApiClient, YouTubeApiError, parse_duration
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
        # 注記が曲名の先頭にあるもの(2025年6月の歌枠のコメント)
        ("(1chorus) 化けの歌/X", "化けの歌", "X", "", "", "1chorus", ""),
        ("(short ver)忘れじの歌/X", "忘れじの歌", "X", "", "", "short", ""),
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


class TestFeat:
    @pytest.mark.parametrize("artist, expected", [
        ("メル feat.IA", ("メル", "IA")),
        ("Eve feat. 初音ミク", ("Eve", "初音ミク")),
        ("架空P ft.架空ボーカル", ("架空P", "架空ボーカル")),
        ("テストバンド", ("テストバンド", "")),
        ("Feather", ("Feather", "")),  # 単語の途中の feat は分けない
    ])
    def test_split_feat(self, artist, expected):
        assert split_feat(artist) == expected

    def test_creator_gets_one_artist_and_feat_is_kept(self):
        comment = "0:01:00 架空の歌/架空P feat.IA/2015\n0:05:00 別の歌/架空P feat.初音ミク/2015"
        dataset = make_dataset()
        rows = build_staged_rows(dataset, extract_timestamp_lines(comment))
        assert list(rows["artist"]) == ["架空P", "架空P"]
        assert list(rows["feat"]) == ["IA", "初音ミク"]
        content_row = build_content_row(make_capture())
        result = apply_staged(dataset, content_row, rows)
        assert len(result.new_artists) == 1 and len(result.new_songs) == 2
        assert set(dataset["songs"]["feat"]) == {"IA", "初音ミク"}
        # 2回目は aliases(元の表記)で同じ曲に結び付く
        assert match_song(dataset, "架空の歌", "架空P feat.IA").kind == "alias"

    def test_display_artist_with_feat(self):
        from src.core.views import build_performance_view, build_song_stats
        dataset = make_dataset()
        rows = build_staged_rows(dataset, extract_timestamp_lines("0:01:00 架空の歌/架空P feat.IA"))
        apply_staged(dataset, build_content_row(make_capture()), rows)
        assert list(build_performance_view(dataset)["artist"]) == ["架空P feat.IA"]
        assert list(build_song_stats(dataset)["artist"]) == ["架空P feat.IA"]


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


class TestTitleDraft:
    """セットリストのコメントが無い動画・ショートは、タイトルから下書きを作る(タイトルは架空)"""

    @pytest.mark.parametrize("title, song, artist, style", [
        ("【アカペラ】架空の歌/架空バンド【幽音しの / ななしいんく】#アカペラ　#shorts", "架空の歌", "架空バンド", "アカペラ"),
        ("【アカペラ】夜の歌/架空シンガー　歌ってみた【幽音しの / ななしいんく】", "夜の歌", "架空シンガー", "アカペラ"),
        ("【アカペラ】朝の歌/架空P 歌ってみた　#shorts", "朝の歌", "架空P", "アカペラ"),
        ("【アカペラ】ずっと一緒!/架空シンガー歌ってみた　#shorts", "ずっと一緒!", "架空シンガー", "アカペラ"),
        ("【歌ってみた】架空の歌/deco*00 　ひとこと【幽音しの】#架空", "架空の歌", "deco*00", "音源"),
        ("【弾き語り】月の歌/架空シンガー　弾き語りで歌ってみたよ!【幽音しの】", "月の歌", "架空シンガー", "弾き語り"),
        ("【アカペラ】　春の歌／架空バンド　春だから歌ってみたよ　#shorts", "春の歌", "架空バンド", "アカペラ"),
    ])
    def test_song_from_title(self, title, song, artist, style):
        split = song_from_title(title)
        assert (split.title, split.artist) == (song, artist)
        assert style_hint(title) == style

    def test_rows_and_content_for_short(self):
        capture = make_capture(content_id="yt:SSSSSSSSSSS", type="short", url="https://www.youtube.com/shorts/SSSSSSSSSSS",
                               title="【アカペラ】架空の歌/架空バンド【幽音しの】#shorts",
                               published_at="2025-04-20T19:00:00+09:00", comments=[Comment("かわいい", "a", 1)])
        rows = build_rows_from_title(make_dataset(), capture)
        assert len(rows) == 1
        assert (rows.loc[0, "start"], rows.loc[0, "title"], rows.loc[0, "artist"]) == ("0:00:00", "架空の歌", "架空バンド")
        assert "タイトルから読み取った" in rows.loc[0, "flag"]
        content = build_content_row(capture)
        assert (content["type"], content["kind"], content["default_style"], content["start_time"]) == \
            ("short", "歌ショート", "アカペラ", "19:00")

    def test_short_ignores_impression_comment_with_time(self):
        """ショートで「0:20 の歌い方が好き」のような感想は、セットリストとして選ばない"""
        capture = make_capture(type="short", title="【歌ってみた】架空の歌/架空バンド #shorts",
                               comments=[Comment("0:20 のところの歌い方が特に好き", "a", 5)])
        assert choose_comment(capture) is None
        setlist = make_capture(type="short", comments=[Comment("0:00 架空の歌/架空バンド\n0:20 別の歌/架空P", "b", 1)])
        assert choose_comment(setlist) is not None

    def test_title_without_song_is_flagged(self):
        capture = make_capture(type="short", title="【ティザー】初配信を見に来てね!#shorts")
        rows = build_rows_from_title(make_dataset(), capture)
        assert "アーティストが無い" in rows.loc[0, "flag"]


class TestSkips:
    def test_add_and_load(self, tmp_path):
        path = tmp_path / "skipped.tsv"
        add_skip("yt:BBBBBBBBBBB", "ティザー(曲なし)", path)
        add_skip("yt:AAAAAAAAAAA", "雑談(曲なし)", path)
        add_skip("yt:BBBBBBBBBBB", "ティザー", path)  # 置き換え
        assert load_skips(path) == {"yt:AAAAAAAAAAA": "雑談(曲なし)", "yt:BBBBBBBBBBB": "ティザー"}
        assert path.read_text(encoding="utf-8").splitlines()[1].startswith("yt:AAAAAAAAAAA")

    def test_reason_required(self, tmp_path):
        with pytest.raises(ValueError):
            add_skip("yt:AAAAAAAAAAA", " ", tmp_path / "skipped.tsv")

    def test_missing_file_is_empty(self, tmp_path):
        assert load_skips(tmp_path / "none.tsv") == {}


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
        assert capture.type == "live"
        session.head.assert_not_called()  # ライブは問い合わせない
        assert capture.validate() == []

    @staticmethod
    def _error_response(status, reason):
        response = MagicMock(ok=False, status_code=status)
        response.json.return_value = {"error": {"errors": [{"reason": reason}]}}
        return response

    def test_error_message_does_not_contain_key(self):
        """失敗のメッセージに API キー(URL)を入れない。ログや画面に出さないため"""
        session = MagicMock()
        session.get.return_value = self._error_response(403, "quotaExceeded")
        with pytest.raises(YouTubeApiError) as e:
            YouTubeApiClient(api_key="SECRET-KEY", session=session).fetch_comments("AAAAAAAAAAA")
        assert e.value.reason == "quotaExceeded" and e.value.status == 403
        assert "SECRET-KEY" not in str(e.value) and "http" not in str(e.value)

    def test_network_error_does_not_contain_key(self):
        import requests
        session = MagicMock()
        session.get.side_effect = requests.ConnectionError("https://x/?key=SECRET-KEY")
        with pytest.raises(YouTubeApiError) as e:
            YouTubeApiClient(api_key="SECRET-KEY", session=session).fetch_comments("AAAAAAAAAAA")
        assert "SECRET-KEY" not in str(e.value)
        assert e.value.__suppress_context__  # 元の例外(URL 入り)をトレースバックに連ねない

    def test_search_other_channels_excludes_own_and_limits_month(self):
        """本人以外のチャンネルの検索: 本人のチャンネルを除き、日本時間のその月で絞る"""
        session = MagicMock()
        responses = [
            {"items": [{"id": "UC_OWN"}]},
            {"items": [
                {"id": {"videoId": "AAAAAAAAAAA"}, "snippet": {"channelId": "UC_OWN", "channelTitle": "本人",
                                                               "title": "a", "publishedAt": "2025-05-02T10:00:00Z"}},
                {"id": {"videoId": "BBBBBBBBBBB"}, "snippet": {"channelId": "UC_X", "channelTitle": "コラボ相手",
                                                               "title": "b", "publishedAt": "2025-05-04T13:20:00Z",
                                                               "liveBroadcastContent": "none"}},
            ]},
        ]
        session.get.return_value.json.side_effect = responses
        found = YouTubeApiClient(api_key="dummy", session=session).search_other_channels("2025-05")
        assert [(v.video_id, ch) for v, ch in found] == [("BBBBBBBBBBB", "コラボ相手")]
        assert found[0][0].published_jst.strftime("%Y-%m-%d %H:%M") == "2025-05-04 22:20"
        params = session.get.call_args_list[1].kwargs["params"]
        assert params["publishedAfter"] == "2025-05-01T00:00:00+09:00"
        assert params["publishedBefore"] == "2025-06-01T00:00:00+09:00"

    def test_comments_disabled_returns_empty(self):
        """コメントを受け付けていない動画(予定表の枠など)は、コメント0件として扱う"""
        session = MagicMock()
        session.get.return_value = self._error_response(403, "commentsDisabled")
        assert YouTubeApiClient(api_key="dummy", session=session).fetch_comments("AAAAAAAAAAA") == []

    @pytest.mark.parametrize("status, expected", [(200, "short"), (303, "video")])
    def test_detect_type_by_shorts_url(self, status, expected):
        session = MagicMock()
        session.head.return_value.status_code = status
        client = YouTubeApiClient(api_key="dummy", session=session)
        assert client.detect_type("AAAAAAAAAAA", is_live=False) == expected
        assert client.detect_type("AAAAAAAAAAA", is_live=True) == "live"

    def test_short_capture_uses_shorts_url(self):
        session = MagicMock()
        video = {"items": [{"snippet": {"title": "t", "publishedAt": "2025-04-20T10:00:00Z"},
                            "contentDetails": {"duration": "PT30S"}}]}
        session.get.return_value.json.side_effect = [video, {"items": []}]
        session.head.return_value.status_code = 200
        capture = YouTubeApiClient(api_key="dummy", session=session).fetch_capture("SSSSSSSSSSS")
        assert capture.type == "short"
        assert capture.url == "https://www.youtube.com/shorts/SSSSSSSSSSS"
        assert capture.published_at == "2025-04-20T19:00:00+09:00"

    def test_list_uploads_pages_and_sorts(self):
        session = MagicMock()
        responses = [
            {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU1"}}}]},
            {"items": [{"contentDetails": {"videoId": "BBBBBBBBBBB"}}], "nextPageToken": "p2"},
            {"items": [{"contentDetails": {"videoId": "AAAAAAAAAAA"}}]},
            {"items": [
                {"id": "BBBBBBBBBBB", "snippet": {"title": "b", "publishedAt": "2025-04-28T10:00:00Z"},
                 "contentDetails": {"duration": "PT40S"}},
                {"id": "AAAAAAAAAAA", "snippet": {"title": "a", "publishedAt": "2025-04-27T10:00:00Z"},
                 "contentDetails": {"duration": "PT30M"}, "liveStreamingDetails": {"actualStartTime": "2025-04-27T11:29:44Z"}},
            ]},
        ]
        session.get.return_value.json.side_effect = responses
        videos = YouTubeApiClient(api_key="dummy", session=session).list_uploads()
        assert [v.video_id for v in videos] == ["AAAAAAAAAAA", "BBBBBBBBBBB"]
        assert videos[0].is_live and videos[0].published_jst.strftime("%Y-%m-%d %H:%M") == "2025-04-27 20:29"
        assert videos[1].duration_seconds == 40 and videos[1].content_id == "yt:BBBBBBBBBBB"
