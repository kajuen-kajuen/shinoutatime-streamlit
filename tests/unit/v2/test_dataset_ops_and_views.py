"""データの操作(採番・曲順・まとめ)と、集計・ビューのテスト"""

import pytest

from src.core import dataset_ops
from src.core.validation import validate_dataset
from src.core.views import build_performance_view, build_song_stats


class TestIdsAndSeq:
    def test_next_id(self, sample_dataset):
        assert dataset_ops.next_id(sample_dataset["songs"]["song_id"], "s") == "s0003"

    def test_next_id_empty(self, sample_dataset):
        assert dataset_ops.next_id(sample_dataset["songs"]["song_id"].iloc[0:0], "s") == "s0001"

    def test_seq_values(self):
        assert dataset_ops.seq_values(3) == ["10", "20", "30"]

    @pytest.mark.parametrize("before, after, expected", [("10", "20", "15"), ("20", "", "30"), ("", "10", "5")])
    def test_seq_between(self, before, after, expected):
        assert dataset_ops.seq_between(before, after) == expected

    def test_seq_between_without_room(self):
        with pytest.raises(ValueError):
            dataset_ops.seq_between("10", "11")

    def test_renumber(self, sample_dataset):
        perf = sample_dataset["performances"]
        perf.loc[perf["content_id"] == "zan:10001", "seq"] = ["15", "17"]
        assert dataset_ops.renumber(sample_dataset, "zan:10001") == 2
        zan = sample_dataset["performances"].query("content_id == 'zan:10001'")
        assert list(zan["seq"]) == ["10", "20"]
        assert list(zan["song_id"]) == ["s0002", "s0001"]


class TestSetValue:
    def test_set_song_column(self, sample_dataset):
        before = dataset_ops.set_value(sample_dataset, "songs", "s0001", "work", "アニメ「架空」ED")
        assert before == ""
        assert sample_dataset["songs"].set_index("song_id").loc["s0001", "work"] == "アニメ「架空」ED"

    def test_set_with_composite_key(self, sample_dataset):
        dataset_ops.set_value(sample_dataset, "performances", "yt:AAAAAAAAAAA,20", "note", "リクエスト")
        perf = sample_dataset["performances"].set_index(["content_id", "seq"])
        assert perf.loc[("yt:AAAAAAAAAAA", "20"), "note"] == "リクエスト"

    @pytest.mark.parametrize("table, key, column", [
        ("nope", "s0001", "work"),        # テーブルが無い
        ("songs", "s0001", "nope"),       # 列が無い
        ("songs", "s0001", "song_id"),    # 主キーは直せない
        ("songs", "s9999", "work"),       # 行が無い
        ("performances", "yt:AAAAAAAAAAA", "note"),  # 主キーが足りない
    ])
    def test_invalid(self, sample_dataset, table, key, column):
        with pytest.raises(ValueError):
            dataset_ops.set_value(sample_dataset, table, key, column, "x")


class TestMerge:
    def test_merge_song_moves_performances_and_aliases(self, sample_dataset):
        moved = dataset_ops.merge_song(sample_dataset, "s0001", "s0002")
        assert moved == 3
        assert set(sample_dataset["performances"]["song_id"]) == {"s0001"}
        assert set(sample_dataset["aliases"]["song_id"]) == {"s0001"}
        assert "s0002" not in set(sample_dataset["songs"]["song_id"])
        assert [i for i in validate_dataset(sample_dataset) if i.level == "error"] == []

    def test_merge_artist(self, sample_dataset):
        assert dataset_ops.merge_artist(sample_dataset, "a0001", "a0002") == 1
        assert set(sample_dataset["songs"]["artist_id"]) == {"a0001"}

    def test_merge_unknown_raises(self, sample_dataset):
        with pytest.raises(ValueError):
            dataset_ops.merge_song(sample_dataset, "s0001", "s9999")


class TestPerformanceView:
    def test_order_newest_day_first_then_earlier_content_then_seq(self, sample_dataset):
        """日付は新しい順。同じ日(2025-05-01)は早い時間(20:00 の AAAA)が上。今の Home と同じ"""
        view = build_performance_view(sample_dataset)
        assert list(view["content_id"]) == [
            "yt:CCCCCCCCCCC", "x:1234567890", "zan:10001", "zan:10001",
            "yt:AAAAAAAAAAA", "yt:AAAAAAAAAAA", "yt:BBBBBBBBBBB"]
        assert list(view["no"].tail(3)) == ["1-1", "1-2", "2-1"]

    def test_no_with_branch_for_same_day(self, sample_dataset):
        view = build_performance_view(sample_dataset).set_index(["content_id", "title"])
        assert view.loc[("yt:AAAAAAAAAAA", "はじまりの歌"), "no"] == "1-1"
        assert view.loc[("yt:AAAAAAAAAAA", "Blue Sky"), "no"] == "1-2"
        assert view.loc[("yt:BBBBBBBBBBB", "はじまりの歌"), "no"] == "2-1"
        assert view.loc[("zan:10001", "Blue Sky"), "no"] == "1"

    def test_short_on_same_day_does_not_change_live_numbers(self):
        """同じ日にショートとライブ配信が1本ずつなら、ライブの No. は枝番なし(今の Home と同じ)"""
        from tests.unit.v2.conftest import content, make_dataset
        dataset = make_dataset(
            contents=[content("yt:SSSSSSSSSSS", "2025-04-29", "【アカペラ】架空", type_="short", start_time="19:00"),
                      content("yt:LLLLLLLLLLL", "2025-04-29", "【歌枠】架空", start_time="21:00")],
            artists=[{"artist_id": "a0001", "name": "架空"}],
            songs=[{"song_id": "s0001", "title": "歌1", "artist_id": "a0001"},
                   {"song_id": "s0002", "title": "歌2", "artist_id": "a0001"}],
            performances=[{"content_id": "yt:SSSSSSSSSSS", "seq": "10", "start": "0:00:00", "song_id": "s0001"},
                          {"content_id": "yt:LLLLLLLLLLL", "seq": "10", "start": "0:05:00", "song_id": "s0001"},
                          {"content_id": "yt:LLLLLLLLLLL", "seq": "20", "start": "0:10:00", "song_id": "s0002"}],
        )
        view = build_performance_view(dataset)
        assert list(view["content_id"]) == ["yt:SSSSSSSSSSS", "yt:LLLLLLLLLLL", "yt:LLLLLLLLLLL"]  # 時刻の早い順
        assert list(view["no"]) == ["", "1", "2"]  # ショートは空欄

    def test_no_is_blank_for_single_song_non_live(self, sample_dataset):
        """1曲だけのショート・投稿は No. が空欄(Z-aN のライブは live なので付く)"""
        no = build_performance_view(sample_dataset).drop_duplicates("content_id").set_index("content_id")["no"]
        assert no["yt:CCCCCCCCCCC"] == "" and no["x:1234567890"] == ""
        assert no["zan:10001"] == "1"

    def test_no_for_multi_song_short(self):
        """複数の曲が入ったショート(例: ボカロファンテスト)は、曲順を付ける(枝番は付けない)"""
        from tests.unit.v2.conftest import content, make_dataset
        dataset = make_dataset(
            contents=[content("yt:SSSSSSSSSSS", "2025-04-26", "【ファンテスト】架空", type_="short", start_time="19:00"),
                      content("yt:TTTTTTTTTTT", "2025-04-26", "【アカペラ】架空", type_="short", start_time="20:00")],
            artists=[{"artist_id": "a0001", "name": "架空"}],
            songs=[{"song_id": f"s000{i}", "title": f"歌{i}", "artist_id": "a0001"} for i in (1, 2, 3)],
            performances=[{"content_id": "yt:SSSSSSSSSSS", "seq": "10", "song_id": "s0001"},
                          {"content_id": "yt:SSSSSSSSSSS", "seq": "20", "song_id": "s0002"},
                          {"content_id": "yt:SSSSSSSSSSS", "seq": "30", "song_id": "s0003"},
                          {"content_id": "yt:TTTTTTTTTTT", "seq": "10", "start": "0:00:00", "song_id": "s0001"}],
        )
        assert list(build_performance_view(dataset)["no"]) == ["1", "2", "3", ""]

    def test_cache_key_changes_with_data_and_code(self, tmp_path):
        """画面のキャッシュの鍵は、データファイルとコードの更新日時で変わる(古い集計を返さないため)"""
        import os
        from src.core import views
        from src.core.views import cache_key
        (tmp_path / "songs.tsv").write_text("x", encoding="utf-8")
        before = cache_key(str(tmp_path))
        assert any(name == "views.py" for name, _ in before)  # コードも鍵に入っている
        os.utime(tmp_path / "songs.tsv", (1, 1))
        assert cache_key(str(tmp_path)) != before

    def test_type_label(self, sample_dataset):
        """画面の「種類」の列: contents.type を日本語で表示する"""
        labels = build_performance_view(sample_dataset).drop_duplicates("content_id").set_index("content_id")["type_label"]
        assert labels.to_dict() == {
            "yt:CCCCCCCCCCC": "ショート", "x:1234567890": "投稿", "zan:10001": "配信",
            "yt:AAAAAAAAAAA": "配信", "yt:BBBBBBBBBBB": "配信",
        }

    def test_style_falls_back_to_content_default(self, sample_dataset):
        view = build_performance_view(sample_dataset).set_index(["content_id", "title"])
        assert view.loc[("yt:AAAAAAAAAAA", "はじまりの歌"), "style"] == "弾き語り"
        assert view.loc[("yt:AAAAAAAAAAA", "Blue Sky"), "style"] == "音源"

    def test_links(self, sample_dataset):
        view = build_performance_view(sample_dataset).set_index(["content_id", "title"])
        assert view.loc[("yt:AAAAAAAAAAA", "Blue Sky"), "link"].endswith("&t=630s")
        assert view.loc[("zan:10001", "Blue Sky"), "link"] == "https://www.zan-live.com/ja/live/detail/10001"

    def test_search_column_is_normalized(self, sample_dataset):
        from src.core.text import normalize_for_match
        view = build_performance_view(sample_dataset)
        assert view["search"].str.contains(normalize_for_match("ＢＬＵＥ ＳＫＹ"), regex=False).any()
        # 曲名の終わりとアーティスト名の始まりをまたいで一致しない
        assert not view["search"].str.contains(normalize_for_match("skyalpha"), regex=False).any()

    def test_search_by_reading(self, sample_dataset):
        """漢字の曲名・アーティストも、読み(かな・カタカナ)で見つかる"""
        from src.core.text import normalize_for_match
        view = build_performance_view(sample_dataset)
        hits = view[view["search"].str.contains(normalize_for_match("ハジマリ"), regex=False)]
        assert set(hits["title"]) == {"はじまりの歌"}
        stats = build_song_stats(sample_dataset)
        assert stats["search"].str.contains(normalize_for_match("てすとばんど"), regex=False).sum() == 1


class TestSongStats:
    def test_counts_exclude_clips(self, sample_dataset):
        stats = build_song_stats(sample_dataset).set_index("song_id")
        # s0001: 配信2 + Z-aN 1(切り抜きのショートは数えない)
        assert stats.loc["s0001", "count"] == 3
        assert stats.loc["s0002", "count"] == 3
        assert stats.loc["s0001", "live_count"] == 3

    def test_first_and_last_date(self, sample_dataset):
        stats = build_song_stats(sample_dataset).set_index("song_id")
        assert stats.loc["s0002", "first_date"] == "2025-05-01"
        assert stats.loc["s0002", "last_date"] == "2025-06-02"
        assert stats.loc["s0002", "latest_link"].startswith("https://x.com/")

    def test_acoustic_count(self, sample_dataset):
        stats = build_song_stats(sample_dataset).set_index("song_id")
        assert stats.loc["s0001", "acoustic_count"] == 1
        assert stats.loc["s0002", "acoustic_count"] == 0

    def test_sorted_by_artist_reading(self, sample_dataset):
        stats = build_song_stats(sample_dataset)
        assert list(stats["artist"]) == ["Alpha", "テストバンド"]  # 英字 → かな

    def test_empty_dataset(self):
        from tests.unit.v2.conftest import make_dataset
        assert build_song_stats(make_dataset()).empty
        assert build_performance_view(make_dataset()).empty
