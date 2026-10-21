"""
データモデル v2 の性能テスト(架空の 2万件)

読み込みから集計までが 1秒以内であること。時間がかかるので、ふだんは流さない:
  docker compose exec shinouta-time pytest tests/performance --runslow
"""

import time

import numpy as np
import pandas as pd
import pytest

from src.core.views import build_performance_view, build_song_stats
from src.repositories.table_repository import Dataset, TableRepository

pytestmark = pytest.mark.slow


def make_large_dataset(n_performances: int = 20_000) -> Dataset:
    rng = np.random.default_rng(0)
    n_contents, n_songs = n_performances // 8, n_performances // 3
    n_artists = n_songs // 3
    dates = pd.date_range("2025-04-27", periods=n_contents, freq="D").strftime("%Y-%m-%d")
    contents = pd.DataFrame({
        "content_id": [f"yt:{i:011d}" for i in range(n_contents)], "platform": "youtube", "type": "live",
        "url": [f"https://www.youtube.com/watch?v={i:011d}" for i in range(n_contents)], "channel": "",
        "date": dates, "start_time": "20:00", "title": [f"【歌枠】{i}" for i in range(n_contents)], "kind": "歌枠",
        "default_style": rng.choice(["音源", "弾き語り"], n_contents), "access": "", "available_until": "",
    })
    artists = pd.DataFrame({"artist_id": [f"a{i:05d}" for i in range(1, n_artists + 1)],
                            "name": [f"アーティスト{i}" for i in range(n_artists)], "sort_name": ""})
    songs = pd.DataFrame({"song_id": [f"s{i:05d}" for i in range(1, n_songs + 1)],
                          "title": [f"曲{i}" for i in range(n_songs)], "sort_title": "",
                          "artist_id": rng.choice(artists["artist_id"], n_songs), "kind": "カバー", "work": "", "year": ""})
    per_content = n_performances // n_contents
    perf = pd.DataFrame({
        "content_id": np.repeat(contents["content_id"].to_numpy(), per_content),
        "seq": np.tile([str(10 * (i + 1)) for i in range(per_content)], n_contents),
        "start": np.tile([f"0:{i:02d}:00" for i in range(per_content)], n_contents),
        "song_id": rng.choice(songs["song_id"], n_contents * per_content), "style": "", "part": "", "note": "",
    })
    aliases = pd.DataFrame(columns=["raw_title", "raw_artist", "song_id"])
    return Dataset({"contents": contents, "artists": artists, "songs": songs, "performances": perf, "aliases": aliases})


def test_load_and_aggregate_within_one_second(tmp_path):
    repo = TableRepository(str(tmp_path))
    repo.save(make_large_dataset())

    started = time.perf_counter()
    dataset = repo.load()
    view = build_performance_view(dataset)
    stats = build_song_stats(dataset, view)
    elapsed = time.perf_counter() - started

    assert len(view) == 20_000
    assert stats["count"].sum() == 20_000
    assert elapsed < 1.0, f"読み込みから集計まで {elapsed:.2f} 秒かかりました"
