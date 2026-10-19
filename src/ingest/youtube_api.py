"""
YouTube Data API v3 からの取得(将来の無人の定期取得用)

API キーは環境変数 YOUTUBE_API_KEY で渡す(リポジトリには書かない)。
取得した内容は取得結果(Capture)にそろえる。
"""

import os
import re
from datetime import datetime
from typing import List, Optional

import requests

from src.ingest.capture import JST, Capture, Comment, now_jst_iso

API_BASE = "https://www.googleapis.com/youtube/v3"
_DURATION = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")


def parse_duration(value: str) -> Optional[int]:
    """'PT1H2M3S' を秒にする"""
    m = _DURATION.match(value or "")
    if not m:
        return None
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


class YouTubeApiClient:
    def __init__(self, api_key: Optional[str] = None, session: Optional[requests.Session] = None, timeout: int = 30):
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY", "")
        if not self.api_key:
            raise ValueError("環境変数 YOUTUBE_API_KEY が設定されていません")
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get(self, path: str, **params) -> dict:
        response = self.session.get(f"{API_BASE}/{path}", params={**params, "key": self.api_key}, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def fetch_comments(self, video_id: str, max_pages: int = 10) -> List[Comment]:
        """トップレベルのコメント(関連度順。職人さんのコメントは上位に来やすい)"""
        comments, token = [], None
        for _ in range(max_pages):
            data = self._get("commentThreads", part="snippet", videoId=video_id, maxResults=100,
                             order="relevance", textFormat="plainText", **({"pageToken": token} if token else {}))
            for item in data.get("items", []):
                top = item["snippet"]["topLevelComment"]["snippet"]
                comments.append(Comment(text=top.get("textOriginal", ""), author=top.get("authorDisplayName", ""),
                                        likes=int(top.get("likeCount", 0))))
            token = data.get("nextPageToken")
            if not token:
                break
        return comments

    def fetch_capture(self, video_id: str, content_type: str = "live") -> Capture:
        data = self._get("videos", part="snippet,contentDetails,liveStreamingDetails", id=video_id)
        items = data.get("items", [])
        if not items:
            raise ValueError(f"動画が見つかりません: {video_id}")
        item = items[0]
        snippet = item["snippet"]
        live = item.get("liveStreamingDetails", {})
        started = live.get("actualStartTime") or snippet["publishedAt"]
        published = datetime.fromisoformat(started.replace("Z", "+00:00")).astimezone(JST)
        return Capture(
            content_id=f"yt:{video_id}",
            platform="youtube",
            type=content_type,
            url=f"https://www.youtube.com/watch?v={video_id}",
            title=snippet.get("title", ""),
            published_at=published.isoformat(timespec="seconds"),
            captured_by="api",
            captured_at=now_jst_iso(),
            description=snippet.get("description", ""),
            channel=snippet.get("channelTitle", ""),
            duration_seconds=parse_duration(item.get("contentDetails", {}).get("duration", "")),
            comments=self.fetch_comments(video_id),
        )
