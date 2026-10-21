"""データモデル v2 のテスト用の共通データ(すべて架空)"""

import pandas as pd
import pytest

from src.models.schema import ALL_SCHEMAS
from src.repositories.table_repository import Dataset


def make_dataset(**tables) -> Dataset:
    """指定したテーブルの行(dict のリスト)から Dataset を作る。指定しないテーブルは空"""
    data = {}
    for schema in ALL_SCHEMAS:
        rows = tables.get(schema.name, [])
        df = pd.DataFrame([{c: r.get(c, "") for c in schema.columns} for r in rows], columns=list(schema.columns))
        data[schema.name] = df.fillna("").astype(str)
    return Dataset(data)


def content(cid, date, title="【歌枠】テスト", platform="youtube", type_="live", start_time="", **extra):
    url = {"youtube": f"https://www.youtube.com/watch?v={cid.split(':', 1)[1]}",
           "zan": f"https://www.zan-live.com/ja/live/detail/{cid.split(':', 1)[1]}",
           "x": f"https://x.com/example/status/{cid.split(':', 1)[1]}"}[platform]
    return {"content_id": cid, "platform": platform, "type": type_, "url": url, "date": date,
            "start_time": start_time, "title": title, **extra}


@pytest.fixture
def sample_dataset() -> Dataset:
    """配信2本(同じ日)・Z-aN の有料ライブ1本・X の投稿1本・切り抜きショート1本"""
    return make_dataset(
        contents=[
            content("yt:AAAAAAAAAAA", "2025-05-01", "【弾き語り】夜の歌枠", start_time="20:00", default_style="弾き語り", kind="歌枠"),
            content("yt:BBBBBBBBBBB", "2025-05-01", "【歌枠】深夜", start_time="23:30", default_style="音源", kind="歌枠"),
            content("zan:10001", "2025-06-01", "架空のライブ", platform="zan", access="paid", available_until="2025-06-30", kind="イベント"),
            content("x:1234567890", "2025-06-02", "歌ってみた(投稿)", platform="x", type_="post"),
            content("yt:CCCCCCCCCCC", "2025-06-03", "切り抜き", type_="short", kind="切り抜き"),
        ],
        artists=[
            {"artist_id": "a0001", "name": "テストバンド", "sort_name": "てすとばんど"},
            {"artist_id": "a0002", "name": "Alpha", "sort_name": ""},
        ],
        songs=[
            {"song_id": "s0001", "title": "はじまりの歌", "sort_title": "はじまりのうた", "artist_id": "a0001", "kind": "カバー"},
            {"song_id": "s0002", "title": "Blue Sky", "artist_id": "a0002", "kind": "カバー", "work": "アニメ「架空」OP", "year": "2010"},
        ],
        performances=[
            {"content_id": "yt:AAAAAAAAAAA", "seq": "10", "start": "0:05:00", "song_id": "s0001"},
            {"content_id": "yt:AAAAAAAAAAA", "seq": "20", "start": "0:10:30", "song_id": "s0002", "style": "音源"},
            {"content_id": "yt:BBBBBBBBBBB", "seq": "10", "start": "0:03:00", "song_id": "s0001", "part": "1chorus"},
            {"content_id": "zan:10001", "seq": "10", "song_id": "s0002"},
            {"content_id": "zan:10001", "seq": "20", "song_id": "s0001"},
            {"content_id": "x:1234567890", "seq": "10", "song_id": "s0002"},
            {"content_id": "yt:CCCCCCCCCCC", "seq": "10", "start": "0:00:00", "song_id": "s0001"},
        ],
        aliases=[
            {"raw_title": "はじまりの歌", "raw_artist": "テストバンド", "song_id": "s0001"},
            {"raw_title": "Blue Sky", "raw_artist": "Alpha", "song_id": "s0002"},
        ],
    )
