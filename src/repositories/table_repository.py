"""
データモデル v2 の TSV リポジトリ

data/v2/ の5つのテーブルを、スキーマ(src/models/schema.py)に沿って読み書きします。
保存するときは毎回、決まった順(docs/specs/data-model.md「並び順」)に並べ直します。
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import pandas as pd

from src.exceptions.errors import DataLoadError, DataSaveError
from src.models.schema import ALL_SCHEMAS, TableSchema

logger = logging.getLogger(__name__)


@dataclass
class Dataset:
    """5つのテーブル(すべての値は文字列。空は "")"""
    tables: Dict[str, pd.DataFrame] = field(default_factory=dict)

    def __getitem__(self, name: str) -> pd.DataFrame:
        return self.tables[name]

    def __setitem__(self, name: str, df: pd.DataFrame) -> None:
        self.tables[name] = df

    @classmethod
    def empty(cls) -> "Dataset":
        return cls({s.name: pd.DataFrame(columns=list(s.columns), dtype=str) for s in ALL_SCHEMAS})


def _id_number(value: str) -> int:
    """'a0012' や 's0003' の数字の部分"""
    digits = value[1:]
    return int(digits) if digits.isdigit() else 0


def sort_table(name: str, df: pd.DataFrame, dataset: Dataset) -> pd.DataFrame:
    """テーブルを決まった順に並べる"""
    if df.empty:
        return df.reset_index(drop=True)
    if name == "contents":
        keys = df.assign(_has_time=df["start_time"] != "")
        keys = keys.sort_values(["date", "_has_time", "start_time", "content_id"], kind="mergesort")
        return keys.drop(columns="_has_time").reset_index(drop=True)
    if name == "performances":
        order = {cid: i for i, cid in enumerate(sort_table("contents", dataset["contents"], dataset)["content_id"])}
        keyed = df.assign(
            _content=df["content_id"].map(order).fillna(len(order)),
            _seq=pd.to_numeric(df["seq"], errors="coerce").fillna(0),
        )
        keyed = keyed.sort_values(["_content", "content_id", "_seq"], kind="mergesort")
        return keyed.drop(columns=["_content", "_seq"]).reset_index(drop=True)
    if name in ("artists", "songs"):
        id_col = "artist_id" if name == "artists" else "song_id"
        keyed = df.assign(_n=df[id_col].map(_id_number))
        return keyed.sort_values(["_n", id_col], kind="mergesort").drop(columns="_n").reset_index(drop=True)
    if name == "aliases":
        keyed = df.assign(_n=df["song_id"].map(_id_number))
        keyed = keyed.sort_values(["_n", "raw_title", "raw_artist"], kind="mergesort")
        return keyed.drop(columns="_n").reset_index(drop=True)
    return df.reset_index(drop=True)


class TableRepository:
    """data/v2/ のようなディレクトリの5テーブルを読み書きする"""

    def __init__(self, directory: str):
        self.directory = Path(directory)

    def path(self, schema: TableSchema) -> Path:
        return self.directory / schema.filename

    def load_table(self, schema: TableSchema) -> pd.DataFrame:
        """1テーブルを読む。ファイルが無ければ空のテーブル"""
        path = self.path(schema)
        if not path.exists():
            return pd.DataFrame(columns=list(schema.columns), dtype=str)
        try:
            df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8")
        except Exception as e:
            raise DataLoadError(file_path=str(path), message=f"TSV を読めません: {e}")
        missing = [c for c in schema.columns if c not in df.columns]
        essential = [c for c in missing if c in schema.required or c in schema.primary_key]
        if essential:
            raise DataLoadError(file_path=str(path), message=f"列が足りません: {essential}")
        for column in missing:
            # 後から足した任意の列は、古いファイルでは空として読む(次の保存で列が加わる)
            logger.info("%s に列 %s が無いので空として読みます", path, column)
            df[column] = ""
        extra = [c for c in df.columns if c not in schema.columns]
        if extra:
            raise DataLoadError(file_path=str(path), message=f"知らない列があります: {extra}")
        return df[list(schema.columns)]

    def load(self) -> Dataset:
        """5テーブルをまとめて読む"""
        return Dataset({s.name: self.load_table(s) for s in ALL_SCHEMAS})

    def save(self, dataset: Dataset) -> None:
        """5テーブルを、決まった順に並べ直して保存する(UTF-8、LF、タブ区切り)"""
        self.directory.mkdir(parents=True, exist_ok=True)
        for schema in ALL_SCHEMAS:
            df = dataset[schema.name].reindex(columns=list(schema.columns)).fillna("").astype(str)
            df = sort_table(schema.name, df, dataset)
            path = self.path(schema)
            try:
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    df.to_csv(f, sep="\t", index=False, lineterminator="\n")
            except OSError as e:
                raise DataSaveError(file_path=str(path), message=str(e))
            logger.info("保存しました: %s (%d 行)", path, len(df))
