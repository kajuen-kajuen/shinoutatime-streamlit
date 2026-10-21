"""
下書き(staged)の読み書きと、データへの追記(apply)

下書きは data/ingest/staged/ に置く(Git 管理外):
  <id>.content.tsv  contents の1行(kind・default_style などを判断で埋める)
  <id>.tsv          歌唱の下書き(parser.STAGED_COLUMNS。include=n の行は取り込まない)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import pandas as pd

from src.core.dataset_ops import next_id, seq_values
from src.core.links import start_to_seconds
from src.core.text import normalize_for_match
from src.ingest.parser import STAGED_COLUMNS
from src.models.schema import CONTENTS, file_safe_id
from src.repositories.table_repository import Dataset

STAGED_DIR = Path("data/ingest/staged")


def staged_paths(content_id: str, staged_dir: Path = STAGED_DIR):
    base = Path(staged_dir) / file_safe_id(content_id)
    return base.with_suffix(".content.tsv"), base.with_suffix(".tsv")


def _write_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        df.to_csv(f, sep="\t", index=False, lineterminator="\n")


def _read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8")


def save_staged(content_row: dict, rows: pd.DataFrame, staged_dir: Path = STAGED_DIR):
    content_path, rows_path = staged_paths(content_row["content_id"], staged_dir)
    _write_tsv(pd.DataFrame([content_row], columns=list(CONTENTS.columns)), content_path)
    _write_tsv(rows[STAGED_COLUMNS], rows_path)
    return content_path, rows_path


def load_staged(content_id: str, staged_dir: Path = STAGED_DIR):
    content_path, rows_path = staged_paths(content_id, staged_dir)
    content = _read_tsv(content_path)
    if len(content) != 1:
        raise ValueError(f"{content_path} は1行にします")
    return content.iloc[0].to_dict(), _read_tsv(rows_path)


@dataclass
class ApplyResult:
    performances: int = 0
    new_songs: List[str] = field(default_factory=list)
    new_artists: List[str] = field(default_factory=list)
    new_aliases: int = 0
    skipped: int = 0


def _find_artist(dataset: Dataset, name: str) -> str:
    artists = dataset["artists"]
    hit = artists[artists["name"].map(normalize_for_match) == normalize_for_match(name)]
    return hit.iloc[0]["artist_id"] if not hit.empty else ""


def _find_song(dataset: Dataset, title: str, artist_id: str) -> str:
    songs = dataset["songs"]
    hit = songs[(songs["title"].map(normalize_for_match) == normalize_for_match(title))
                & (songs["artist_id"] == artist_id)]
    return hit.iloc[0]["song_id"] if not hit.empty else ""


def _append(dataset: Dataset, table: str, row: dict) -> None:
    dataset[table] = pd.concat([dataset[table], pd.DataFrame([row])], ignore_index=True).fillna("")


def apply_staged(dataset: Dataset, content_row: dict, rows: pd.DataFrame, replace: bool = False) -> ApplyResult:
    """
    判断の終わった下書きを Dataset に追記する

    - song_id があればその曲、無ければ title・artist で既存の曲・アーティストを探し、無ければ新しく登録する
    - 元の表記(raw_title・raw_artist)を aliases に足す
    - 曲順は時刻の順(時刻が無ければ下書きの行の順)に 10, 20, 30… と振る
    - 同じ content_id が既にあれば、replace=True のときだけ置き換える
    """
    content_id = content_row["content_id"]
    contents = dataset["contents"]
    if content_id in set(contents["content_id"]):
        if not replace:
            raise ValueError(f"{content_id} は既に登録されています(置き換えるなら --replace)")
        dataset["contents"] = contents[contents["content_id"] != content_id]
        perf = dataset["performances"]
        dataset["performances"] = perf[perf["content_id"] != content_id]

    result = ApplyResult()
    _append(dataset, "contents", {c: content_row.get(c, "") for c in CONTENTS.columns})

    included = rows[rows["include"].str.lower().isin(["y", "yes", "1", "true"])].copy()
    result.skipped = len(rows) - len(included)
    included["_sec"] = included["start"].map(start_to_seconds)
    if included["_sec"].notna().all():
        included = included.sort_values("_sec", kind="mergesort")

    for seq, (_, r) in zip(seq_values(len(included)), included.iterrows()):
        song_id = r["song_id"]
        if not song_id:
            if not r["title"] or not r["artist"]:
                raise ValueError(f"曲名とアーティストを入れてください: {r['raw_line']}")
            artist_id = _find_artist(dataset, r["artist"])
            if not artist_id:
                artist_id = next_id(dataset["artists"]["artist_id"], "a")
                _append(dataset, "artists", {"artist_id": artist_id, "name": r["artist"], "sort_name": r["artist_sort"]})
                result.new_artists.append(artist_id)
            song_id = _find_song(dataset, r["title"], artist_id)
            if not song_id:
                song_id = next_id(dataset["songs"]["song_id"], "s")
                _append(dataset, "songs", {
                    "song_id": song_id, "title": r["title"], "sort_title": r["sort_title"],
                    "artist_id": artist_id, "feat": r.get("feat", ""), "kind": r["song_kind"],
                    "work": r["work"], "year": r["year"],
                })
                result.new_songs.append(song_id)
        elif song_id not in set(dataset["songs"]["song_id"]):
            raise ValueError(f"曲 {song_id} がありません: {r['raw_line']}")

        _append(dataset, "performances", {
            "content_id": content_id, "seq": seq, "start": r["start"], "song_id": song_id,
            "style": r["style"], "part": r["part"], "note": r["note"],
        })
        result.performances += 1

        aliases = dataset["aliases"]
        known = ((aliases["raw_title"] == r["raw_title"]) & (aliases["raw_artist"] == r["raw_artist"])).any()
        if r["raw_title"] and not known:
            _append(dataset, "aliases", {"raw_title": r["raw_title"], "raw_artist": r["raw_artist"], "song_id": song_id})
            result.new_aliases += 1
    return result
