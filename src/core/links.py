"""
時刻付きリンクの組み立て

プラットフォームごとに、元の URL と開始時刻からリンクを作ります。
時刻を指定できないプラットフォーム(X・Z-aN)は URL をそのまま返します。
"""

from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def start_to_seconds(start: str) -> Optional[int]:
    """'H:MM:SS' または 'MM:SS' を秒にする。空や不正な値は None"""
    if not start:
        return None
    try:
        parts = [int(p) for p in start.split(":")]
    except ValueError:
        return None
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, (m, s) = 0, parts
    else:
        return None
    if not (0 <= m < 60 and 0 <= s < 60) or h < 0:
        return None
    return h * 3600 + m * 60 + s


def seconds_to_start(seconds: int) -> str:
    """秒を 'H:MM:SS' にする"""
    h, rest = divmod(int(seconds), 3600)
    m, s = divmod(rest, 60)
    return f"{h}:{m:02d}:{s:02d}"


def youtube_url(video_id: str) -> str:
    """YouTube の通常の URL"""
    return f"https://www.youtube.com/watch?v={video_id}"


def _with_query(url: str, key: str, value: str) -> str:
    """URL のクエリに key=value を足す(同じ key があれば置き換える)"""
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != key]
    query.append((key, value))
    return urlunsplit(parts._replace(query=urlencode(query)))


def build_link(platform: str, url: str, start: str = "") -> str:
    """
    時刻付きのリンクを作る

    YouTube は t=秒(watch と shorts の両方)。それ以外と、時刻が空のときは url のまま。
    """
    seconds = start_to_seconds(start)
    # 0秒からの再生(ショートや歌ってみた動画)は、時刻を付けなくても同じなので url のまま
    if platform != "youtube" or not seconds or not url:
        return url
    if "t=" in url:
        return _with_query(url, "t", f"{seconds}s")
    # よくある形(t の無い URL)は、解析せずにつなぐ(件数が多いので速さを優先)
    return f"{url}{'&' if '?' in url else '?'}t={seconds}s"
