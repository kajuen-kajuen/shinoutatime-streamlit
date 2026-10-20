"""
取得結果から下書きを作る(prepare)

1. 職人さんのタイムスタンプのコメントを選ぶ
2. 時刻の行を抜き出し、「曲名/アーティスト/作品/年」に分ける
3. 曲名の注記((1chorus) など)を part・note に分ける
4. aliases・songs と照合して、既存の曲の候補を入れる

ここで作るのは下書きで、確定は Claude の判断(docs/prompts/update-data.md)のあと apply で行う。
"""

import os
import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import pandas as pd

from src.core.links import seconds_to_start, start_to_seconds
from src.core.text import normalize_for_match
from src.ingest.capture import Capture, Comment
from src.repositories.table_repository import Dataset

# 行の先頭(または [ ] で囲まれた)時刻。H:MM:SS / HH:MM:SS / MM:SS / M:SS
_TIMESTAMP = re.compile(r"^\s*[\[(【]?\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s*[\])】]?\s*(?:[-－–~～:：|｜]\s*)?(.*)$")
# 「/」の区切り(全角・前後の空白を含む)とタブ
_SEPARATOR = re.compile(r"\s*[/／]\s*|\t+")
# 区切りが無いときの「曲名（アーティスト）」
_PAREN_ARTIST = re.compile(r"^(.+?)\s*[（(]([^()（）]+)[)）]\s*$")
# セットリストのコメントの見出し
_SETLIST_HEADER = re.compile(r"セットリスト|セトリ|set\s*list", re.I)
# 「作り手 feat.歌い手」
_FEAT = re.compile(r"^(.*?)\s*\b(?:feat\.?|ft\.|featuring)\s*(.+)$", re.I)
# 動画・ショートのタイトル: 先頭の【印】、本文、以降の【…】や # を除く
_TITLE_TAGS = re.compile(r"^\s*((?:【[^】]*】\s*)+)")
_TITLE_TAIL = re.compile(r"\s*(?:【|#|＃|　).*$")
_TITLE_NOISE = re.compile(r"\s*(?:歌ってみた|弾いてみた|弾き語りで歌ってみた).*$")
# タイトルの印 → 演奏の形
_STYLE_TAGS = (("アカペラ", "アカペラ"), ("弾き語り", "弾き語り"), ("歌ってみた", "音源"))
_YEAR = re.compile(r"^(?:19|20)\d{2}$")
# メンバー限定のコンテンツのタイトルの印(下書きの access を members にする)
_MEMBERS_ONLY = re.compile(r"メン限|メンバー限定|メンバーシップ限定")
# 曲名の先頭・末尾の尺の注記(「(1chorus) 化けの花」「忘れじの言の葉(short ver)」の両方がある)
_PART_LABELS = (
    (r"1\s*chorus", "1chorus"),
    (r"1\s*phrase", "1phrase"),
    (r"short(?:\s*ver\.?)?", "short"),
    (r"1番のみ", "1番のみ"),
)
_PART_PATTERNS: Sequence[Tuple[re.Pattern, str]] = tuple(
    (re.compile(rf"^\s*[\(（]\s*{p}\s*[\)）]\s*|\s*[\(（]\s*{p}\s*[\)）]\s*$", re.I), v) for p, v in _PART_LABELS
)
# 曲名の先頭・末尾の、歌唱についての注記(note に移す)
_NOTE_PATTERN = re.compile(r"^\s*[\(（【]\s*(リクエスト|アカペラ|弾き語り|音源|再)\s*[\)）】]\s*|\s*[\(（【]\s*(リクエスト|アカペラ|弾き語り|音源)\s*[\)）】]\s*$")

STAGED_COLUMNS = [
    "include", "start", "raw_line", "raw_title", "raw_artist", "raw_work", "raw_year",
    "match", "song_id", "title", "sort_title", "artist", "artist_sort", "feat", "song_kind",
    "work", "year", "style", "part", "note", "flag",
]


def split_feat(artist: str) -> Tuple[str, str]:
    """「メル feat.IA」を ("メル", "IA") に分ける。feat. が無ければ (artist, "")"""
    m = _FEAT.match(artist.strip())
    if not m or not m.group(1).strip():
        return artist.strip(), ""
    return m.group(1).strip(), m.group(2).strip()


@dataclass
class TimestampLine:
    start: str  # H:MM:SS
    text: str
    raw_line: str


def extract_timestamp_lines(text: str) -> List[TimestampLine]:
    """コメントから、時刻で始まる行を抜き出す(時刻は H:MM:SS にそろえる)"""
    lines = []
    for raw in text.splitlines():
        m = _TIMESTAMP.match(raw)
        if not m:
            continue
        seconds = start_to_seconds(m.group(1))
        if seconds is None:
            continue
        # raw_line は人と Claude が読むためのものなので、タブは「 / 」にして下書きの TSV を読みやすくする
        lines.append(TimestampLine(start=seconds_to_start(seconds), text=m.group(2).strip(),
                                   raw_line=raw.strip().replace("\t", " / ")))
    return lines


def _trusted_names() -> List[str]:
    value = os.environ.get("SHINOUTA_TRUSTED_COMMENTERS", "")
    return [v.strip() for v in value.split(",") if v.strip()]


def _song_like_count(text: str) -> int:
    """曲らしい行(区切りで曲名とアーティストに分けられる行)の数"""
    return sum(1 for line in extract_timestamp_lines(text) if split_song_text(line.text).artist)


def rank_timestamp_comments(comments: List[Comment]) -> List[Tuple[int, Comment, int]]:
    """
    職人さんのセットリストらしい順に (元の番号, コメント, 時刻の行数) を並べる(時刻の行が無いものは除く)

    順の決め方: 「セットリスト」などの見出しがある → 曲らしい行が多い → 時刻の行が多い → いいねが多い。
    雑談の目次(配信開始・自己紹介…)は時刻の行が多くても、曲らしい行が少ないので下がる。
    """
    ranked = []
    for i, c in enumerate(comments):
        total = len(extract_timestamp_lines(c.text))
        if total == 0:
            continue
        has_header = bool(_SETLIST_HEADER.search(c.text))
        ranked.append(((-int(has_header), -_song_like_count(c.text), -total, -c.likes, i), (i, c, total)))
    return [item for _, item in sorted(ranked, key=lambda r: r[0])]


def is_setlist_like(text: str) -> bool:
    """セットリストらしいコメント: 「セットリスト」などの見出しがあるか、曲らしい行が1行以上ある"""
    return bool(_SETLIST_HEADER.search(text)) or _song_like_count(text) > 0


def choose_comment(capture: Capture, index: Optional[int] = None) -> Optional[Tuple[int, Comment]]:
    """
    職人さんのコメントを選ぶ

    index を指定すればそれ。環境変数 SHINOUTA_TRUSTED_COMMENTERS(投稿者名のカンマ区切り)が
    あれば、その人のコメントの中から選ぶ。
    動画・ショートは、セットリストらしいコメント(is_setlist_like)が無ければ None
    (「0:20 の歌い方が好き」のような感想を曲と取り違えないため。タイトルから下書きを作る)。
    """
    if index is not None:
        return index, capture.comments[index]
    ranked = rank_timestamp_comments(capture.comments)
    trusted = _trusted_names()
    if trusted:
        ranked = [r for r in ranked if r[1].author in trusted]
    if capture.type in ("video", "short"):
        ranked = [r for r in ranked if is_setlist_like(r[1].text)]
    return (ranked[0][0], ranked[0][1]) if ranked else None


@dataclass
class SplitText:
    title: str
    artist: str = ""
    work: str = ""
    year: str = ""
    part: str = ""
    note: str = ""
    artist_from_paren: bool = False


def split_song_text(text: str) -> SplitText:
    """
    「曲名/アーティスト/作品/年」を分ける(区切りは「/」「／」とタブ)

    年は4桁の数字の項目。区切りが無ければ全体を曲名とし、「曲名（アーティスト）」の形なら
    括弧の中をアーティストの候補にする(artist_from_paren=True。判断で確かめる)。
    曲名の注記((1chorus) など)は part、(リクエスト) などは note に移す。
    """
    parts = [p.strip() for p in _SEPARATOR.split(text.strip()) if p.strip() != ""]
    year = ""
    if len(parts) >= 2 and _YEAR.match(parts[-1]):
        year = parts.pop()
    title = parts[0] if parts else ""
    artist = parts[1] if len(parts) > 1 else ""
    work = "/".join(parts[2:]) if len(parts) > 2 else ""

    artist_from_paren = False
    if not artist:
        m = _PAREN_ARTIST.match(title)
        is_annotation = m and (any(p.search(title) for p, _ in _PART_PATTERNS) or _NOTE_PATTERN.search(title))
        if m and not is_annotation:
            title, artist, artist_from_paren = m.group(1), m.group(2).strip(), True

    part = ""
    for pattern, value in _PART_PATTERNS:
        if pattern.search(title):
            title, part = pattern.sub("", title), value
            break
    notes = []
    while True:
        m = _NOTE_PATTERN.search(title)
        if not m:
            break
        notes.append(m.group(1) or m.group(2))
        title = (title[:m.start()] + title[m.end():]).strip()
    return SplitText(title=title.strip(), artist=artist.strip(), work=work.strip(),
                     year=year, part=part, note="・".join(notes), artist_from_paren=artist_from_paren)


@dataclass
class Match:
    kind: str  # alias / exact / similar / new
    song_id: str = ""
    score: float = 0.0


def match_song(dataset: Dataset, raw_title: str, raw_artist: str, threshold: float = 0.85) -> Match:
    """既存の曲との照合: aliases の一致 → 曲名とアーティストの一致 → 曲名の類似 → 新しい曲"""
    nt = normalize_for_match(raw_title)
    na_raw = normalize_for_match(raw_artist)  # aliases は元の表記のまま照合する
    na = normalize_for_match(split_feat(raw_artist)[0])  # 曲の照合は作り手で行う
    aliases = dataset["aliases"]
    if not aliases.empty:
        hit = aliases[(aliases["raw_title"].map(normalize_for_match) == nt)
                      & (aliases["raw_artist"].map(normalize_for_match) == na_raw)]
        if not hit.empty:
            return Match("alias", hit.iloc[0]["song_id"], 1.0)

    songs = dataset["songs"].merge(dataset["artists"], on="artist_id", how="left")
    if songs.empty:
        return Match("new")
    songs = songs.assign(_t=songs["title"].map(normalize_for_match), _a=songs["name"].map(normalize_for_match))
    exact = songs[(songs["_t"] == nt) & (songs["_a"] == na)]
    if not exact.empty:
        return Match("exact", exact.iloc[0]["song_id"], 1.0)

    from src.utils.similarity_checker import SimilarityChecker
    checker = SimilarityChecker()
    best = max(((checker.calculate_similarity(nt, t), sid) for t, sid in zip(songs["_t"], songs["song_id"])),
               default=(0.0, ""))
    if best[0] >= threshold:
        return Match("similar", best[1], round(best[0], 3))
    return Match("new")


def build_staged_rows(dataset: Dataset, lines: List[TimestampLine]) -> pd.DataFrame:
    """時刻の行を、下書きの表(STAGED_COLUMNS)にする"""
    rows = []
    for line in lines:
        split = split_song_text(line.text)
        match = match_song(dataset, split.title, split.artist)
        creator, feat = split_feat(split.artist)
        flags = []
        if not split.artist:
            flags.append("アーティストが無い")
        if split.artist_from_paren:
            flags.append("括弧の中をアーティストとみなした")
        if match.kind == "similar":
            flags.append(f"似た曲あり({match.score})")
        rows.append({
            "include": "y",
            "start": line.start,
            "raw_line": line.raw_line,
            "raw_title": split.title,
            "raw_artist": split.artist,
            "raw_work": split.work,
            "raw_year": split.year,
            "match": match.kind,
            "song_id": match.song_id if match.kind in ("alias", "exact") else "",
            "title": split.title,
            "sort_title": "",
            "artist": creator,
            "artist_sort": "",
            "feat": feat,
            "song_kind": "",
            "work": split.work,
            "year": split.year,
            "style": "",
            "part": split.part,
            "note": split.note,
            "flag": "・".join(flags),
        })
    return pd.DataFrame(rows, columns=STAGED_COLUMNS)


def title_tags(title: str) -> List[str]:
    """タイトルの先頭の【…】の中身(例: ['アカペラ'])"""
    m = _TITLE_TAGS.match(title)
    return re.findall(r"【([^】]*)】", m.group(1)) if m else []


def style_hint(title: str) -> str:
    """タイトルの印から演奏の形の候補(アカペラ / 弾き語り / 音源)。分からなければ空"""
    tags = " ".join(title_tags(title)) or title
    for word, style in _STYLE_TAGS:
        if word in tags:
            return style
    return ""


def song_from_title(title: str) -> SplitText:
    """
    動画・ショートのタイトルから曲名とアーティストの候補を取る

    例: 「【アカペラ】アポリア/ヨルシカ　歌ってみた【幽音しの / ななしいんく】#shorts」→ アポリア / ヨルシカ
    """
    body = _TITLE_TAGS.sub("", title)
    body = _TITLE_TAIL.sub("", body)
    split = split_song_text(body)
    split.title = _TITLE_NOISE.sub("", split.title).strip()
    split.artist = _TITLE_NOISE.sub("", split.artist).strip()
    return split


def build_rows_from_title(dataset: Dataset, capture: Capture) -> pd.DataFrame:
    """セットリストのコメントが無い動画・ショートの、タイトルからの1行の下書き"""
    split = song_from_title(capture.title)
    line = TimestampLine(start="0:00:00", text="/".join(p for p in (split.title, split.artist) if p),
                         raw_line=capture.title)
    rows = build_staged_rows(dataset, [line])
    rows["flag"] = rows["flag"].map(lambda f: "・".join(x for x in ("タイトルから読み取った", f) if x))
    return rows


def build_content_row(capture: Capture) -> dict:
    """取得結果から contents の下書き1行を作る(kind・default_style・access の候補はタイトルから。判断で直す)"""
    published = capture.published_jst
    kind = {"short": "歌ショート", "video": "歌ってみた"}.get(capture.type, "")
    return {
        "content_id": capture.content_id,
        "platform": capture.platform,
        "type": capture.type,
        "url": capture.url,
        "channel": "",
        "date": published.strftime("%Y-%m-%d"),
        "start_time": published.strftime("%H:%M"),
        "title": capture.title,
        "kind": kind,
        "default_style": style_hint(capture.title),
        "access": "members" if _MEMBERS_ONLY.search(capture.title) else "",
        "available_until": "",
    }
