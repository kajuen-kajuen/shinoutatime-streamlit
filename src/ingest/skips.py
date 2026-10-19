"""
曲の無いコンテンツの記録(data/ingest/skipped.tsv。Git で管理する)

ティザーや曲の無い雑談の配信は data/v2/ に入れない(contents は「歌が含まれるコンテンツ」)。
次の取り込みで迷わないよう、content_id と理由だけを記録する(曲名もコメントも入れない)。
"""

from datetime import datetime
from pathlib import Path
from typing import Dict

import pandas as pd

from src.ingest.capture import JST

SKIPPED_PATH = Path("data/ingest/skipped.tsv")
COLUMNS = ["content_id", "reason", "date"]


def load_skips(path: Path = SKIPPED_PATH) -> Dict[str, str]:
    """content_id → 理由"""
    if not Path(path).exists():
        return {}
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8")
    return dict(zip(df["content_id"], df["reason"]))


def add_skip(content_id: str, reason: str, path: Path = SKIPPED_PATH) -> None:
    """記録を足す(同じ content_id があれば理由を置き換える)。content_id の順に並べて保存する"""
    if not reason.strip():
        raise ValueError("理由を書いてください")
    path = Path(path)
    rows = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8") \
        if path.exists() else pd.DataFrame(columns=COLUMNS)
    rows = rows[rows["content_id"] != content_id]
    rows = pd.concat([rows, pd.DataFrame([{
        "content_id": content_id, "reason": reason.strip(), "date": datetime.now(JST).strftime("%Y-%m-%d"),
    }])], ignore_index=True).sort_values("content_id")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        rows[COLUMNS].to_csv(f, sep="\t", index=False, lineterminator="\n")
