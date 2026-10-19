"""
データモデル v2 の操作

ID の採番、曲順(seq)の振り直し、重複した曲・アーティストのまとめ。
どの操作も Dataset を書き換えるだけで、保存は TableRepository.save で行う。
"""

from typing import List

import pandas as pd

from src.models.schema import SEQ_STEP
from src.repositories.table_repository import Dataset


def next_id(existing: pd.Series, prefix: str) -> str:
    """'a0001' 形式の次の ID。消した ID は再利用しない運用なので、最大値+1"""
    numbers = [int(v[1:]) for v in existing if v.startswith(prefix) and v[1:].isdigit()]
    return f"{prefix}{(max(numbers) + 1) if numbers else 1:04d}"


def seq_values(count: int) -> List[str]:
    """count 曲ぶんの曲順(10, 20, 30…)"""
    return [str(SEQ_STEP * (i + 1)) for i in range(count)]


def seq_between(before: str, after: str) -> str:
    """
    2つの曲順の間に入れる曲順

    after が空なら末尾(before + 10)。間に整数の余地が無ければ ValueError(renumber してから入れる)。
    """
    low = int(before) if before else 0
    if not after:
        return str(low + SEQ_STEP)
    high = int(after)
    if high - low < 2:
        raise ValueError(f"曲順 {low} と {high} の間に空きがありません。先に renumber してください")
    return str((low + high) // 2)


def renumber(dataset: Dataset, content_id: str) -> int:
    """1つのコンテンツの曲順を 10, 20, 30… に振り直す。振り直した件数を返す"""
    perf = dataset["performances"]
    mask = perf["content_id"] == content_id
    if not mask.any():
        return 0
    ordered = perf[mask].assign(_seq=pd.to_numeric(perf.loc[mask, "seq"])).sort_values("_seq").index
    perf.loc[ordered, "seq"] = seq_values(len(ordered))
    dataset["performances"] = perf
    return len(ordered)


def merge_song(dataset: Dataset, keep_id: str, drop_id: str) -> int:
    """
    同じ曲だった2つをまとめる

    歌唱と aliases の参照を drop_id から keep_id に付け替え、drop_id の曲を消す。
    付け替えた歌唱の件数を返す。
    """
    songs = dataset["songs"]
    for sid in (keep_id, drop_id):
        if sid not in set(songs["song_id"]):
            raise ValueError(f"曲 {sid} がありません")
    if keep_id == drop_id:
        raise ValueError("同じ曲は指定できません")
    perf = dataset["performances"]
    moved = int((perf["song_id"] == drop_id).sum())
    perf.loc[perf["song_id"] == drop_id, "song_id"] = keep_id
    aliases = dataset["aliases"]
    aliases.loc[aliases["song_id"] == drop_id, "song_id"] = keep_id
    dataset["aliases"] = aliases.drop_duplicates(["raw_title", "raw_artist"], keep="first")
    dataset["songs"] = songs[songs["song_id"] != drop_id]
    dataset["performances"] = perf
    return moved


def merge_artist(dataset: Dataset, keep_id: str, drop_id: str) -> int:
    """同じアーティストだった2つをまとめる。付け替えた曲の件数を返す"""
    artists = dataset["artists"]
    for aid in (keep_id, drop_id):
        if aid not in set(artists["artist_id"]):
            raise ValueError(f"アーティスト {aid} がいません")
    if keep_id == drop_id:
        raise ValueError("同じアーティストは指定できません")
    songs = dataset["songs"]
    moved = int((songs["artist_id"] == drop_id).sum())
    songs.loc[songs["artist_id"] == drop_id, "artist_id"] = keep_id
    dataset["songs"] = songs
    dataset["artists"] = artists[artists["artist_id"] != drop_id]
    return moved
