"""
データモデル v2 の整合性の検査

主キー・外部キー・値の形・曲順と時刻の関係・並び順を確かめます。
error があればデータとして不正、warning は直したほうがよいもの。
"""

from dataclasses import dataclass
from typing import List

import pandas as pd

from src.core.links import start_to_seconds
from src.models.schema import ALL_SCHEMAS, PLATFORM_PREFIX
from src.repositories.table_repository import Dataset, sort_table


@dataclass(frozen=True)
class Issue:
    level: str  # "error" または "warning"
    table: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level}] {self.table}: {self.message}"


def _rows(df: pd.DataFrame, mask: pd.Series, limit: int = 5) -> str:
    """問題のある行番号(ファイルの行。ヘッダーが1行目)"""
    lines = [str(i + 2) for i in df.index[mask][:limit]]
    more = "…" if mask.sum() > limit else ""
    return ", ".join(lines) + more


def validate_dataset(dataset: Dataset) -> List[Issue]:
    """データ全体を検査して、問題の一覧を返す"""
    issues: List[Issue] = []

    for schema in ALL_SCHEMAS:
        df = dataset[schema.name]
        name = schema.name

        for col in schema.required:
            empty = df[col] == ""
            if empty.any():
                issues.append(Issue("error", name, f"{col} が空の行があります(行 {_rows(df, empty)})"))

        dup = df.duplicated(list(schema.primary_key), keep=False)
        if dup.any():
            issues.append(Issue("error", name, f"主キー {schema.primary_key} が重複しています(行 {_rows(df, dup)})"))

        for col, pattern in schema.patterns.items():
            bad = (df[col] != "") & ~df[col].str.match(pattern)
            if bad.any():
                issues.append(Issue("error", name, f"{col} の形が正しくありません(行 {_rows(df, bad)})"))

        for col, allowed in schema.choices.items():
            bad = (df[col] != "") & ~df[col].isin(allowed)
            if bad.any():
                issues.append(Issue("error", name, f"{col} は {allowed} のどれかにします(行 {_rows(df, bad)})"))

        for fk in schema.foreign_keys:
            refs = set(dataset[fk.ref_table][fk.ref_column])
            bad = (df[fk.column] != "") & ~df[fk.column].isin(refs)
            if bad.any():
                issues.append(Issue("error", name, f"{fk.column} の参照先が {fk.ref_table} にありません(行 {_rows(df, bad)})"))

        if not df.equals(sort_table(name, df, dataset)):
            issues.append(Issue("warning", name, "並び順が決まった順になっていません(保存し直すと直ります)"))

    issues.extend(_check_contents(dataset))
    issues.extend(_check_performances(dataset))
    issues.extend(_check_unused(dataset))
    return issues


def _check_contents(dataset: Dataset) -> List[Issue]:
    """content_id の接頭辞(yt: など)が platform と合っていること"""
    df = dataset["contents"]
    if df.empty:
        return []
    expected = df["platform"].map(PLATFORM_PREFIX)
    bad = expected.notna() & (df["content_id"].str.split(":", n=1).str[0] != expected)
    if bad.any():
        return [Issue("error", "contents", f"content_id の接頭辞が platform と合っていません(行 {_rows(df, bad)})")]
    return []


def _check_performances(dataset: Dataset) -> List[Issue]:
    """時刻があるときは、曲順(seq)の順に時刻が増えていること"""
    issues = []
    df = dataset["performances"]
    if df.empty:
        return issues
    keyed = df.assign(
        _seq=pd.to_numeric(df["seq"], errors="coerce"),
        _sec=df["start"].map(start_to_seconds),
    )
    for content_id, group in keyed.groupby("content_id", sort=False):
        timed = group.dropna(subset=["_seq", "_sec"]).sort_values("_seq")
        if (timed["_sec"].diff().dropna() <= 0).any():
            issues.append(Issue("error", "performances", f"{content_id}: 曲順(seq)と時刻(start)の順が合っていません"))
    return issues


def _check_unused(dataset: Dataset) -> List[Issue]:
    issues = []
    used_songs = set(dataset["performances"]["song_id"])
    unused = sorted(set(dataset["songs"]["song_id"]) - used_songs)
    if unused:
        issues.append(Issue("warning", "songs", f"どの歌唱からも参照されていない曲があります: {', '.join(unused[:10])}"))
    used_artists = set(dataset["songs"]["artist_id"])
    unused_a = sorted(set(dataset["artists"]["artist_id"]) - used_artists)
    if unused_a:
        issues.append(Issue("warning", "artists", f"どの曲からも参照されていないアーティストがいます: {', '.join(unused_a[:10])}"))
    return issues


def has_errors(issues: List[Issue]) -> bool:
    return any(i.level == "error" for i in issues)
