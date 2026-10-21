"""
データモデル v2 の操作

ID の採番、曲順(seq)の振り直し、重複した曲・アーティストのまとめ、アーティストの追加と削除。
どの操作も Dataset を書き換えるだけで、保存は TableRepository.save で行う。
"""

from typing import List

import pandas as pd

from src.core.text import normalize_for_match
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


def set_value(dataset: Dataset, table: str, key: str, column: str, value: str) -> str:
    """
    1行の1つの値を直す。直す前の値を返す

    key は主キーの値。主キーが複数の列のテーブル(performances・aliases)は、カンマで区切って並べる
    (例: "yt:rPoEadXC5ck,20")。主キーの列は直せない(ID が変わるので、merge などを使う)。
    """
    from src.models.schema import SCHEMAS
    if table not in SCHEMAS:
        raise ValueError(f"テーブル {table} はありません。{sorted(SCHEMAS)} のどれかにします")
    schema = SCHEMAS[table]
    if column not in schema.columns:
        raise ValueError(f"{table} に列 {column} はありません。{list(schema.columns)} のどれかにします")
    if column in schema.primary_key:
        raise ValueError(f"主キーの列 {column} は直せません")
    keys = key.split(",") if len(schema.primary_key) > 1 else [key]
    if len(keys) != len(schema.primary_key):
        raise ValueError(f"{table} の主キーは {schema.primary_key} です(カンマで区切って指定します)")
    df = dataset[table]
    mask = pd.Series(True, index=df.index)
    for col, val in zip(schema.primary_key, keys):
        mask &= df[col] == val
    if mask.sum() != 1:
        raise ValueError(f"{table} に {key} の行がありません")
    before = df.loc[mask, column].iloc[0]
    df.loc[mask, column] = value
    dataset[table] = df
    return before


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


def add_artist(dataset: Dataset, name: str, sort_name: str = "") -> str:
    """
    アーティストを1人足す。振った artist_id を返す

    同じ名前(normalize_for_match で同じ。取り込みの照合と同じ判定)のアーティストがいれば足さない。
    """
    name = name.strip()
    if not name:
        raise ValueError("名前を入れてください")
    artists = dataset["artists"]
    same = artists[artists["name"].map(normalize_for_match) == normalize_for_match(name)]
    if not same.empty:
        row = same.iloc[0]
        raise ValueError(f"アーティスト「{row['name']}」は既にいます({row['artist_id']})")
    artist_id = next_id(artists["artist_id"], "a")
    row = {"artist_id": artist_id, "name": name, "sort_name": sort_name.strip()}
    dataset["artists"] = pd.concat([artists, pd.DataFrame([row])], ignore_index=True).fillna("")
    return artist_id


def drop_artist(dataset: Dataset, artist_id: str) -> str:
    """
    どの曲からも参照されていないアーティストを消す。消したアーティストの名前を返す

    ID は最大値+1 で振るので、いちばん大きい ID を消すと、次に足したときに同じ ID が使われる
    (merge_artist でも同じ)。消した ID は再利用しない決まりなので、いちばん大きい ID は消さない運用にする。
    """
    artists = dataset["artists"]
    hit = artists[artists["artist_id"] == artist_id]
    if hit.empty:
        raise ValueError(f"アーティスト {artist_id} がいません")
    songs = dataset["songs"]
    used = list(songs.loc[songs["artist_id"] == artist_id, "song_id"])
    if used:
        more = "…" if len(used) > 5 else ""
        raise ValueError(
            f"{artist_id} は曲 {', '.join(used[:5])}{more} から参照されています。"
            f"merge-artist か set songs <song_id> artist_id で付け替えてから消してください"
        )
    dataset["artists"] = artists[artists["artist_id"] != artist_id]
    return hit.iloc[0]["name"]
