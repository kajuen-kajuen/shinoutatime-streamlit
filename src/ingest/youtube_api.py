"""
YouTube Data API v3 からの取得(将来の無人の定期取得用)

API キーは環境変数 YOUTUBE_API_KEY で渡す(リポジトリには書かない)。
複数のキーを使うときは YOUTUBE_API_KEYS(カンマ区切り)にも書く。上限に達したら次のキーに切り替える。
取得した内容は取得結果(Capture)にそろえる。
"""

import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Mapping, Optional, Sequence, Tuple

import requests

from src.ingest.capture import JST, Capture, Comment, now_jst_iso

API_BASE = "https://www.googleapis.com/youtube/v3"
CHANNEL_HANDLE = "@Shino_Kasukane"
# 本人以外のチャンネルを探す検索語。タイトルに本人の名前が無いコラボ(同期3人の「うるぱんおばけ」など)もあるため複数
OTHER_CHANNEL_QUERIES = ("幽音しの", "うるぱんおばけ")
WINDOW_DAYS = 7  # 本人以外のチャンネルを検索するときの区間の長さ
# API の上限で失敗したときの理由。このときだけ次のキーに切り替える
QUOTA_REASONS = ("quotaExceeded", "rateLimitExceeded", "dailyLimitExceeded")
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


class YouTubeApiError(Exception):
    """
    API の失敗。メッセージに URL を入れない(URL には API キーが入るため。ログや画面に出さない)

    reason は API のエラーの理由(例: commentsDisabled、quotaExceeded)。分からなければ空。
    """

    def __init__(self, path: str, status: Optional[int] = None, reason: str = ""):
        self.path, self.status, self.reason = path, status, reason
        detail = f"HTTP {status}" if status is not None else "通信の失敗"
        super().__init__(f"YouTube API の {path} が失敗しました({detail}{'、' + reason if reason else ''})")


def load_api_keys(env: Mapping[str, str] = os.environ) -> List[str]:
    """使う API キーの一覧: YOUTUBE_API_KEY → YOUTUBE_API_KEYS(カンマ区切り)の順。重複と空は除く"""
    keys = [env.get("YOUTUBE_API_KEY", "")] + env.get("YOUTUBE_API_KEYS", "").split(",")
    return list(dict.fromkeys(k.strip() for k in keys if k.strip()))


class YouTubeApiClient:
    def __init__(self, api_key: Optional[str] = None, session: Optional[requests.Session] = None, timeout: int = 30,
                 api_keys: Optional[Sequence[str]] = None):
        self.api_keys = [api_key] if api_key else list(api_keys or load_api_keys())
        if not self.api_keys:
            raise ValueError("環境変数 YOUTUBE_API_KEY(または YOUTUBE_API_KEYS)が設定されていません")
        self._key_index = 0  # 上限で切り替えたら、同じ実行の中では次のキーを使い続ける
        self.session = session or requests.Session()
        self.timeout = timeout

    @property
    def api_key(self) -> str:
        return self.api_keys[self._key_index]

    def _get(self, path: str, **params) -> dict:
        while True:
            try:
                return self._get_once(path, **params)
            except YouTubeApiError as e:
                if e.reason not in QUOTA_REASONS or self._key_index + 1 >= len(self.api_keys):
                    raise
                self._key_index += 1
                # キーの値は出さない(番号だけ)
                print(f"API の上限に達したので、次のキー({self._key_index + 1}/{len(self.api_keys)})に切り替えます",
                      file=sys.stderr)

    def _get_once(self, path: str, **params) -> dict:
        try:
            response = self.session.get(f"{API_BASE}/{path}", params={**params, "key": self.api_key}, timeout=self.timeout)
        except requests.RequestException as e:
            # requests の例外のメッセージには、キーの入った URL が含まれるので使わない
            raise YouTubeApiError(path, reason=type(e).__name__) from None
        if not response.ok:
            try:
                reason = response.json()["error"]["errors"][0]["reason"]
            except (ValueError, KeyError, IndexError, TypeError):
                reason = ""
            raise YouTubeApiError(path, response.status_code, reason)
        return response.json()

    def fetch_comments(self, video_id: str, max_pages: int = 10) -> List[Comment]:
        """トップレベルのコメント(関連度順。職人さんのコメントは上位に来やすい)"""
        comments, token = [], None
        for _ in range(max_pages):
            try:
                data = self._get("commentThreads", part="snippet", videoId=video_id, maxResults=100,
                                 order="relevance", textFormat="plainText", **({"pageToken": token} if token else {}))
            except YouTubeApiError as e:
                if e.reason == "commentsDisabled":  # コメントを受け付けていない動画(予定表の枠など)
                    return comments
                if e.reason == "forbidden":  # メンバー限定の動画(API キーではコメントを読めない)
                    return comments
                raise
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

    def search_other_channels(self, month: str, queries: Sequence[str] = OTHER_CHANNEL_QUERIES,
                              handle: str = CHANNEL_HANDLE,
                              now: Optional[datetime] = None) -> List[Tuple[VideoSummary, str]]:
        """
        その月(YYYY-MM、日本時間)に公開された、本人以外のチャンネルの動画を検索する

        コラボ相手・公式チャンネルの出演の候補を洗い出すため。search.list は 1ページ 100 ユニットと高い。
        検索語ごとに検索し、同じ動画は1つにまとめる。検索は関係の無い動画も返すので、
        タイトルか概要欄(先頭)に検索語が入っているものだけを残す。
        ファンの切り抜きなども混じるので、対象にするかは人(Claude)が判断する。戻り値は (動画, チャンネル名)。
        月の途中で流したときは、今(now。既定は今の時刻)までを検索する(未来の区間は search.list が 400 を返す)。
        """
        start = datetime.strptime(month, "%Y-%m").replace(tzinfo=JST)
        end = start.replace(year=start.year + 1, month=1) if start.month == 12 else start.replace(month=start.month + 1)
        end = min(end, (now or datetime.now(JST)).replace(microsecond=0))
        if start >= end:
            return []  # まだ来ていない月
        own = self._get("channels", part="id", forHandle=handle)["items"][0]["id"]
        # 1か月まとめて検索すると、結果の一部しか返らず、打つたびに件数が変わる(2026-10-20 に確認)。
        # 期間を区切って検索する(1か月で 検索語 × 5区間 × 100 ユニットほど)
        windows, cursor = [], start
        while cursor < end:
            windows.append((cursor, min(cursor + timedelta(days=WINDOW_DAYS), end)))
            cursor = windows[-1][1]
        found = {}
        for query, (after, before) in ((q, w) for q in queries for w in windows):
            token = None
            while True:
                data = self._get("search", part="snippet", q=query, type="video", maxResults=50, order="date",
                                 publishedAfter=after.isoformat(), publishedBefore=before.isoformat(),
                                 **({"pageToken": token} if token else {}))
                for item in data.get("items", []):
                    snippet = item["snippet"]
                    text = snippet.get("title", "") + "\n" + snippet.get("description", "")
                    if snippet.get("channelId") == own or query not in text:
                        continue
                    video_id = item["id"]["videoId"]
                    found.setdefault(video_id, (VideoSummary(
                        video_id=video_id,
                        published_jst=_to_jst(snippet["publishedAt"]),
                        duration_seconds=None,
                        is_live=snippet.get("liveBroadcastContent") not in (None, "none"),
                        title=snippet.get("title", ""),
                    ), snippet.get("channelTitle", "")))
                token = data.get("nextPageToken")
                if not token:
                    break
        return sorted(found.values(), key=lambda pair: pair[0].published_jst)

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
