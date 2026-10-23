"""TableRepository(読み書き・並べ直し)と、整合性の検査のテスト"""

import pandas as pd
import pytest

from src.core.validation import has_errors, validate_dataset
from src.exceptions.errors import DataLoadError
from src.models.schema import SONGS
from src.repositories.table_repository import TableRepository
from tests.unit.v2.conftest import content, make_dataset


class TestTableRepository:
    def test_roundtrip(self, tmp_path, sample_dataset):
        repo = TableRepository(str(tmp_path))
        repo.save(sample_dataset)
        loaded = repo.load()
        for name in ("contents", "songs", "performances"):
            assert len(loaded[name]) == len(sample_dataset[name])
        assert validate_dataset(loaded) == []

    def test_files_are_utf8_lf_tab(self, tmp_path, sample_dataset):
        TableRepository(str(tmp_path)).save(sample_dataset)
        raw = (tmp_path / "songs.tsv").read_bytes()
        assert b"\r\n" not in raw
        assert raw.decode("utf-8").splitlines()[0] == "\t".join(SONGS.columns)

    def test_missing_files_mean_empty_tables(self, tmp_path):
        dataset = TableRepository(str(tmp_path)).load()
        assert all(dataset[name].empty for name in dataset.tables)

    def test_missing_optional_column_is_read_as_empty(self, tmp_path):
        """後から足した任意の列(songs.feat)が無い古いファイルも読める"""
        (tmp_path / "songs.tsv").write_text(
            "song_id\ttitle\tsort_title\tartist_id\tkind\twork\tyear\ns0001\t曲\t\ta0001\t\t\t\n", encoding="utf-8")
        songs = TableRepository(str(tmp_path)).load()["songs"]
        assert list(songs.columns) == list(SONGS.columns)
        assert songs.loc[0, "feat"] == ""

    def test_missing_required_column_is_error(self, tmp_path):
        (tmp_path / "songs.tsv").write_text("song_id\tsort_title\n", encoding="utf-8")
        with pytest.raises(DataLoadError):
            TableRepository(str(tmp_path)).load()

    def test_unknown_column_is_error(self, tmp_path):
        (tmp_path / "artists.tsv").write_text("artist_id\tname\tsort_name\textra\n", encoding="utf-8")
        with pytest.raises(DataLoadError):
            TableRepository(str(tmp_path)).load()

    def test_save_sorts_rows(self, tmp_path):
        dataset = make_dataset(
            contents=[content("yt:BBBBBBBBBBB", "2025-05-02"), content("yt:AAAAAAAAAAA", "2025-05-01")],
            artists=[{"artist_id": "a0010", "name": "B"}, {"artist_id": "a0002", "name": "A"}],
            songs=[{"song_id": "s0001", "title": "x", "artist_id": "a0002"},
                   {"song_id": "s0002", "title": "y", "artist_id": "a0010"}],
            performances=[
                {"content_id": "yt:BBBBBBBBBBB", "seq": "10", "song_id": "s0001"},
                {"content_id": "yt:AAAAAAAAAAA", "seq": "20", "song_id": "s0002"},
                {"content_id": "yt:AAAAAAAAAAA", "seq": "10", "song_id": "s0001"},
            ],
        )
        repo = TableRepository(str(tmp_path))
        repo.save(dataset)
        loaded = repo.load()
        assert list(loaded["contents"]["content_id"]) == ["yt:AAAAAAAAAAA", "yt:BBBBBBBBBBB"]
        assert list(loaded["artists"]["artist_id"]) == ["a0002", "a0010"]
        assert list(zip(loaded["performances"]["content_id"], loaded["performances"]["seq"])) == [
            ("yt:AAAAAAAAAAA", "10"), ("yt:AAAAAAAAAAA", "20"), ("yt:BBBBBBBBBBB", "10")]
        assert validate_dataset(loaded) == []


class TestValidation:
    def test_sample_is_valid(self, sample_dataset):
        assert validate_dataset(sample_dataset) == []

    def _errors(self, dataset):
        return [str(i) for i in validate_dataset(dataset) if i.level == "error"]

    def test_duplicate_primary_key(self, sample_dataset):
        perf = sample_dataset["performances"]
        sample_dataset["performances"] = pd.concat([perf, perf.iloc[[0]]], ignore_index=True)
        assert any("主キー" in e for e in self._errors(sample_dataset))

    def test_missing_foreign_key(self, sample_dataset):
        sample_dataset["performances"].loc[0, "song_id"] = "s9999"
        assert any("参照先" in e for e in self._errors(sample_dataset))

    def test_bad_patterns_and_choices(self, sample_dataset):
        sample_dataset["contents"].loc[0, "date"] = "2025/5/1"
        sample_dataset["contents"].loc[1, "default_style"] = "ギター"
        errors = self._errors(sample_dataset)
        assert any("date" in e for e in errors)
        assert any("default_style" in e for e in errors)

    def test_url_must_be_https(self, sample_dataset):
        sample_dataset["contents"].loc[0, "url"] = "javascript:alert(1)"
        sample_dataset["contents"].loc[1, "url"] = "http://www.youtube.com/watch?v=BBBBBBBBBBB"
        assert "url の形が正しくありません(行 2, 3)" in " ".join(self._errors(sample_dataset))

    def test_seq_and_start_order_must_match(self, sample_dataset):
        sample_dataset["performances"].loc[1, "start"] = "0:01:00"  # seq 20 なのに seq 10 より早い
        assert any("曲順" in e for e in self._errors(sample_dataset))

    def test_start_can_be_empty(self, sample_dataset):
        zan = sample_dataset["performances"]["content_id"] == "zan:10001"
        assert (sample_dataset["performances"].loc[zan, "start"] == "").all()
        assert not has_errors(validate_dataset(sample_dataset))

    def test_prefix_must_match_platform(self, sample_dataset):
        sample_dataset["contents"].loc[0, "platform"] = "zan"
        assert any("接頭辞" in e for e in self._errors(sample_dataset))

    def test_unused_song_is_warning(self, sample_dataset):
        sample_dataset["songs"] = pd.concat([sample_dataset["songs"], pd.DataFrame([{
            "song_id": "s0003", "title": "未使用", "sort_title": "", "artist_id": "a0001", "kind": "", "work": "", "year": ""}])],
            ignore_index=True)
        issues = validate_dataset(sample_dataset)
        assert not has_errors(issues)
        assert any(i.level == "warning" and "s0003" in i.message for i in issues)
