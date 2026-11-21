"""今週のスケジュールの画像と、投稿へのリンク

埋め込み HTML から投稿の URL を取り、同じ投稿 ID の画像ファイルを探す。
X の widgets.js は使わない（ログインしていないと画像が描かれないため）。
"""

import re
from pathlib import Path


_STATUS_URL = re.compile(
    r"https://(?:x|twitter)\.com/([A-Za-z0-9_]{1,15})/status/(\d+)"
)


def status_url_from_embed(embed_code: str) -> str | None:
    """埋め込み HTML にある最初の投稿 URL。無ければ None

    返す URL は https://x.com/<ユーザー>/status/<数字>（クエリは付けない）。
    """
    if not embed_code:
        return None
    match = _STATUS_URL.search(embed_code)
    if not match:
        return None
    return f"https://x.com/{match.group(1)}/status/{match.group(2)}"


def find_schedule_image(data_dir: Path, status_url: str | None) -> Path | None:
    """投稿 URL と同じ ID の schedule-<ID>.jpg / .png。無ければ None"""
    if not status_url:
        return None
    match = _STATUS_URL.fullmatch(status_url)
    if not match:
        return None
    status_id = match.group(2)
    for extension in ("jpg", "png"):
        path = data_dir / f"schedule-{status_id}.{extension}"
        if path.is_file():
            return path
    return None
