"""
データモデル v2 のテーブル定義

data/v2/ の5つの TSV(contents・artists・songs・performances・aliases)の
列・主キー・外部キー・値の形を宣言します。仕様は docs/specs/data-model.md。
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Pattern, Tuple


@dataclass(frozen=True)
class ForeignKey:
    """外部キー: column の値が ref_table.ref_column に存在すること"""
    column: str
    ref_table: str
    ref_column: str


@dataclass(frozen=True)
class TableSchema:
    """
    1つの TSV テーブルの定義

    Attributes:
        name: テーブル名(ファイル名は name + ".tsv")
        columns: 列名(この順で保存する)
        required: 空を許さない列
        primary_key: 主キーの列
        foreign_keys: 外部キー
        patterns: 列ごとの値の形(空は required でなければ許す)
        choices: 列ごとに許す値(空は required でなければ許す)
    """
    name: str
    columns: Tuple[str, ...]
    required: Tuple[str, ...]
    primary_key: Tuple[str, ...]
    foreign_keys: Tuple[ForeignKey, ...] = ()
    patterns: Dict[str, Pattern] = field(default_factory=dict)
    choices: Dict[str, Tuple[str, ...]] = field(default_factory=dict)

    @property
    def filename(self) -> str:
        return f"{self.name}.tsv"


DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HHMM_PATTERN = re.compile(r"^\d{2}:\d{2}$")
START_PATTERN = re.compile(r"^\d+:\d{2}:\d{2}$")
SEQ_PATTERN = re.compile(r"^[1-9]\d*$")
CONTENT_ID_PATTERN = re.compile(r"^[a-z]+:[A-Za-z0-9_-]+$")
ARTIST_ID_PATTERN = re.compile(r"^a\d{4,}$")
SONG_ID_PATTERN = re.compile(r"^s\d{4,}$")
YEAR_PATTERN = re.compile(r"^\d{4}$")
# リンク(href)にそのまま入るので、https のほか(javascript: など)を入れない
URL_PATTERN = re.compile(r"^https://")

PLATFORMS = ("youtube", "x", "zan", "goods")
CONTENT_TYPES = ("live", "video", "short", "post", "audio")
STYLES = ("音源", "弾き語り", "アカペラ")
ACCESS = ("public", "members", "paid")
SONG_KINDS = ("カバー", "オリジナル", "即興")
PARTS = ("1chorus", "1phrase", "short", "1番のみ")

# content_id の接頭辞とプラットフォームの対応
PLATFORM_PREFIX = {"youtube": "yt", "x": "x", "zan": "zan", "goods": "goods"}

CONTENTS = TableSchema(
    name="contents",
    columns=("content_id", "platform", "type", "url", "channel", "date", "start_time",
             "title", "kind", "default_style", "access", "available_until", "follows"),
    required=("content_id", "platform", "type", "url", "date", "title"),
    primary_key=("content_id",),
    # follows: 同じ公演の続きの部のとき、先の部の content_id(No. を「枝番-曲順」で続ける。views.py)
    foreign_keys=(ForeignKey("follows", "contents", "content_id"),),
    patterns={
        "content_id": CONTENT_ID_PATTERN,
        "follows": CONTENT_ID_PATTERN,
        "url": URL_PATTERN,
        "date": DATE_PATTERN,
        "start_time": HHMM_PATTERN,
        "available_until": DATE_PATTERN,
    },
    choices={
        "platform": PLATFORMS,
        "type": CONTENT_TYPES,
        "default_style": STYLES,
        "access": ACCESS,
    },
)

ARTISTS = TableSchema(
    name="artists",
    columns=("artist_id", "name", "sort_name"),
    required=("artist_id", "name"),
    primary_key=("artist_id",),
    patterns={"artist_id": ARTIST_ID_PATTERN},
)

# feat: 歌い手(ボーカロイドなど)。アーティストは作り手にまとめ、歌い手はここに持つ(表示は「作り手 feat.歌い手」)
SONGS = TableSchema(
    name="songs",
    columns=("song_id", "title", "sort_title", "artist_id", "feat", "kind", "work", "year"),
    required=("song_id", "title", "artist_id"),
    primary_key=("song_id",),
    foreign_keys=(ForeignKey("artist_id", "artists", "artist_id"),),
    patterns={"song_id": SONG_ID_PATTERN, "artist_id": ARTIST_ID_PATTERN, "year": YEAR_PATTERN},
    choices={"kind": SONG_KINDS},
)

PERFORMANCES = TableSchema(
    name="performances",
    columns=("content_id", "seq", "start", "song_id", "style", "part", "note"),
    required=("content_id", "seq", "song_id"),
    primary_key=("content_id", "seq"),
    foreign_keys=(
        ForeignKey("content_id", "contents", "content_id"),
        ForeignKey("song_id", "songs", "song_id"),
    ),
    patterns={"seq": SEQ_PATTERN, "start": START_PATTERN, "song_id": SONG_ID_PATTERN},
    choices={"style": STYLES, "part": PARTS},
)

ALIASES = TableSchema(
    name="aliases",
    columns=("raw_title", "raw_artist", "song_id"),
    required=("raw_title", "song_id"),
    primary_key=("raw_title", "raw_artist"),
    foreign_keys=(ForeignKey("song_id", "songs", "song_id"),),
    patterns={"song_id": SONG_ID_PATTERN},
)

# 読み込み・検査の順(外部キーの参照先が先)
ALL_SCHEMAS: Tuple[TableSchema, ...] = (CONTENTS, ARTISTS, SONGS, PERFORMANCES, ALIASES)
SCHEMAS: Dict[str, TableSchema] = {s.name: s for s in ALL_SCHEMAS}

# 曲順の刻み(間に足せるように 10 ずつ空ける)
SEQ_STEP = 10


def file_safe_id(content_id: str) -> str:
    """content_id をファイル名に使える形にする(Windows では ':' を使えない)"""
    return content_id.replace(":", "_")
