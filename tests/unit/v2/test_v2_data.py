"""画面が読むデータ(src/ui/v2_data.py)のテスト。架空のデータを tmp_path に置いて読む"""

import pytest

from src.exceptions.errors import DataLoadError
from src.repositories.table_repository import TableRepository
from src.ui import v2_data


@pytest.fixture(autouse=True)
def clear_cache():
    v2_data._load.clear()
    yield
    v2_data._load.clear()


def test_loads_view_and_stats(tmp_path, monkeypatch, sample_dataset):
    TableRepository(str(tmp_path)).save(sample_dataset)
    monkeypatch.setenv("SHINOUTA_V2_DATA_DIR", str(tmp_path))

    view = v2_data.load_performance_view()
    stats = v2_data.load_song_stats()

    assert len(view) == len(sample_dataset["performances"])
    assert set(stats["song_id"]) == {"s0001", "s0002"}


def test_reloads_when_data_changes(tmp_path, monkeypatch, sample_dataset):
    repo = TableRepository(str(tmp_path))
    repo.save(sample_dataset)
    monkeypatch.setenv("SHINOUTA_V2_DATA_DIR", str(tmp_path))
    before = len(v2_data.load_performance_view())

    perf = sample_dataset["performances"]
    sample_dataset["performances"] = perf[perf["content_id"] != "zan:10001"]
    repo.save(sample_dataset)
    import os
    os.utime(tmp_path / "performances.tsv", (1, 1))  # 書き込みが同じ時刻に収まっても鍵が変わるように

    assert len(v2_data.load_performance_view()) == before - 2


def test_missing_dir_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("SHINOUTA_V2_DATA_DIR", str(tmp_path / "nope"))
    with pytest.raises(DataLoadError):
        v2_data.load_performance_view()


def test_broken_file_raises(tmp_path, monkeypatch, sample_dataset):
    TableRepository(str(tmp_path)).save(sample_dataset)
    (tmp_path / "songs.tsv").write_text("song_id\tnope\n", encoding="utf-8")  # 必須の列が無い
    monkeypatch.setenv("SHINOUTA_V2_DATA_DIR", str(tmp_path))
    with pytest.raises(DataLoadError):
        v2_data.load_song_stats()
