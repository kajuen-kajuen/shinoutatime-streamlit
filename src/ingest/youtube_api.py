"""
YouTube Data API v3 からの取得(将来の無人の定期取得用)

API キーは環境変数 YOUTUBE_API_KEY で渡す(リポジトリには書かない)。
取得した内容は取得結果(Capture)にそろえる。
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import requests

from src.ingest.capture import JST, Capture, Comment, now_jst_iso

API_BASE = "https://www.googleapis.com/youtube/v3"
CHANNEL_HANDLE = "@Shino_Kasukane"
_DURATION = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")


@dataclass
class VideoSummary:
    """チャンネルの一覧の1行"""
    video_id: str
    published_jst: datetime  # ライブは開始日時、それ以外は公開日時
    duration_seconds: Optional[int]
    is_live: bool
    title: str

    @property
    def content_id(self) -> str:
        return f"yt:{self.video_id}"


def _to_jst(value: str) -> datetime:
    """API の UTC の日時('2025-04-27T11:29:44Z')を日本時間にする"""
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(JST)


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

    def list_uploads(self, handle: str = CHANNEL_HANDLE) -> List[VideoSummary]:
        """チャンネルの投稿(ライブのアーカイブ・動画・ショート)を古い順に並べる"""
        channel = self._get("channels", part="contentDetails", forHandle=handle)["items"][0]
        playlist = channel["contentDetails"]["relatedPlaylists"]["uploads"]
        ids, token = [], None
        while True:
            data = self._get("playlistItems", part="contentDetails", playlistId=playlist, maxResults=50,
                             **({"pageToken": token} if token else {}))
            ids += [i["contentDetails"]["videoId"] for i in data.get("items", [])]
            token = data.get("nextPageToken")
            if not token:
                break
        videos = []
        for i in range(0, len(ids), 50):
            data = self._get("videos", part="snippet,contentDetails,liveStreamingDetails", id=",".join(ids[i:i + 50]))
            for item in data.get("items", []):
                live = item.get("liveStreamingDetails", {})
                videos.append(VideoSummary(
                    video_id=item["id"],
                    published_jst=_to_jst(live.get("actualStartTime") or item["snippet"]["publishedAt"]),
                    duration_seconds=parse_duration(item.get("contentDetails", {}).get("duration", "")),
                    is_live=bool(live),
                    title=item["snippet"].get("title", ""),
                ))
        return sorted(videos, key=lambda v: v.published_jst)

    def detect_type(self, video_id: str, is_live: bool) -> str:
        """
        live / short / video を決める

        ライブのアーカイブは live。それ以外は /shorts/<ID> がリダイレクトされなければ short、されれば video。
        """
        if is_live:
            return "live"
        response = self.session.head(f"https://www.youtube.com/shorts/{video_id}", allow_redirects=False,
                                     timeout=self.timeout)
        return "short" if response.status_code == 200 else "video"

    def fetch_capture(self, video_id: str, content_type: Optional[str] = None) -> Capture:
        """取得結果を作る。content_type を省くと、種類を自動で決める"""
        data = self._get("videos", part="snippet,contentDetails,liveStreamingDetails", id=video_id)
        items = data.get("items", [])
        if not items:
            raise ValueError(f"動画が見つかりません: {video_id}")
        item = items[0]
        snippet = item["snippet"]
        live = item.get("liveStreamingDetails", {})
        published = _to_jst(live.get("actualStartTime") or snippet["publishedAt"])
        content_type = content_type or self.detect_type(video_id, bool(live))
        url = (f"https://www.youtube.com/shorts/{video_id}" if content_type == "short"
               else f"https://www.youtube.com/watch?v={video_id}")
        return Capture(
            content_id=f"yt:{video_id}",
            platform="youtube",
            type=content_type,
            url=url,
            title=snippet.get("title", ""),
            published_at=published.isoformat(timespec="seconds"),
            captured_by="api",
            captured_at=now_jst_iso(),
            description=snippet.get("description", ""),
            channel=snippet.get("channelTitle", ""),
            duration_seconds=parse_duration(item.get("contentDetails", {}).get("duration", "")),
            comments=self.fetch_comments(video_id),
        )
