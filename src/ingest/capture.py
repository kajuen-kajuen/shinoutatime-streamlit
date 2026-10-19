"""
取得結果 JSON

どの取得方法(ブラウザ・YouTube Data API・yt-dlp)でも、この形にそろえて
data/ingest/cache/<content_id のファイル名>.json に保存する(Git 管理外)。
コメントの投稿者名はここにだけ置き、data/v2/ には入れない。
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from src.models.schema import CONTENT_TYPES, PLATFORM_PREFIX, PLATFORMS, file_safe_id

JST = timezone(timedelta(hours=9))
CAPTURED_BY = ("browser", "api", "ytdlp", "manual")
CACHE_DIR = Path("data/ingest/cache")


@dataclass
class Comment:
    text: str
    author: str = ""
    likes: int = 0


@dataclass
class Capture:
    """1つのコンテンツの取得結果"""
    content_id: str
    platform: str
    type: str
    url: str
    title: str
    published_at: str  # ISO 8601(日本時間 +09:00)
    captured_by: str
    captured_at: str
    description: str = ""
    channel: str = ""
    duration_seconds: Optional[int] = None
    comments: List[Comment] = field(default_factory=list)

    def validate(self) -> List[str]:
        """形の問題の一覧(空なら問題なし)"""
        problems = []
        if self.platform not in PLATFORMS:
            problems.append(f"platform は {PLATFORMS} のどれかにします: {self.platform}")
        elif not self.content_id.startswith(PLATFORM_PREFIX[self.platform] + ":"):
            problems.append(f"content_id の接頭辞が platform と合っていません: {self.content_id}")
        if self.type not in CONTENT_TYPES:
            problems.append(f"type は {CONTENT_TYPES} のどれかにします: {self.type}")
        if self.captured_by not in CAPTURED_BY:
            problems.append(f"captured_by は {CAPTURED_BY} のどれかにします: {self.captured_by}")
        for name in ("url", "title", "published_at"):
            if not getattr(self, name):
                problems.append(f"{name} が空です")
        try:
            datetime.fromisoformat(self.published_at)
        except ValueError:
            problems.append(f"published_at が ISO 8601 ではありません: {self.published_at}")
        return problems

    @property
    def published_jst(self) -> datetime:
        dt = datetime.fromisoformat(self.published_at)
        return (dt if dt.tzinfo else dt.replace(tzinfo=JST)).astimezone(JST)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "Capture":
        comments = [Comment(**c) for c in data.get("comments", [])]
        return cls(**{**data, "comments": comments})


def cache_path(content_id: str, cache_dir: Path = CACHE_DIR) -> Path:
    return Path(cache_dir) / f"{file_safe_id(content_id)}.json"


def save_capture(capture: Capture, cache_dir: Path = CACHE_DIR) -> Path:
    problems = capture.validate()
    if problems:
        raise ValueError("取得結果の形が正しくありません: " + " / ".join(problems))
    path = cache_path(capture.content_id, cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(capture.to_json() + "\n", encoding="utf-8")
    return path


def load_capture(path: Path) -> Capture:
    capture = Capture.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
    problems = capture.validate()
    if problems:
        raise ValueError(f"{path}: " + " / ".join(problems))
    return capture


def now_jst_iso() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def from_ytdlp_info(info: dict, content_type: str = "live") -> Capture:
    """yt-dlp の info.json(--write-comments 付き)を取得結果にする"""
    epoch = info.get("release_timestamp") or info.get("timestamp")
    if epoch is None and info.get("upload_date"):
        published = datetime.strptime(info["upload_date"], "%Y%m%d").replace(tzinfo=JST)
    else:
        published = datetime.fromtimestamp(int(epoch), JST)
    comments = [
        Comment(text=c.get("text", ""), author=c.get("author", ""), likes=int(c.get("like_count") or 0))
        for c in info.get("comments") or []
        if c.get("parent", "root") == "root"
    ]
    video_id = info["id"]
    return Capture(
        content_id=f"yt:{video_id}",
        platform="youtube",
        type=content_type,
        url=f"https://www.youtube.com/watch?v={video_id}",
        title=info.get("title", ""),
        published_at=published.isoformat(timespec="seconds"),
        captured_by="ytdlp",
        captured_at=now_jst_iso(),
        description=info.get("description", ""),
        channel=info.get("channel", ""),
        duration_seconds=info.get("duration"),
        comments=comments,
    )
