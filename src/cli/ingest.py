"""
取り込み CLI(取得結果 → 下書き → 追記)

使い方(コンテナの中で):
  python -m src.cli.ingest from-ytdlp <info.json> [--type live]   # yt-dlp の JSON を取得結果にする
  python -m src.cli.ingest from-api <動画ID> [--type live]       # YouTube Data API(YOUTUBE_API_KEY)
  python -m src.cli.ingest check <取得結果.json>                  # 取得結果の形を確かめる
  python -m src.cli.ingest comments <content_id>                  # 時刻の行があるコメントの候補を表示
  python -m src.cli.ingest prepare <content_id> [--comment N]     # 下書きを作る
  python -m src.cli.ingest apply <content_id> [--dry-run] [--replace]
  python -m src.cli.ingest status

ブラウザで取得するときは、Claude が取得結果 JSON を data/ingest/cache/ に書き、check で確かめる。
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from src.core.validation import has_errors, validate_dataset
from src.ingest.capture import CACHE_DIR, cache_path, from_ytdlp_info, load_capture, save_capture
from src.ingest.parser import (build_content_row, build_staged_rows, choose_comment,
                               extract_timestamp_lines, rank_timestamp_comments)
from src.ingest.staging import STAGED_DIR, apply_staged, load_staged, save_staged, staged_paths
from src.repositories.table_repository import TableRepository

DEFAULT_DIR = "data/v2"


def cmd_from_ytdlp(args) -> int:
    info = json.loads(Path(args.info_json).read_text(encoding="utf-8"))
    path = save_capture(from_ytdlp_info(info, args.type))
    print(f"保存しました: {path}")
    return 0


def cmd_from_api(args) -> int:
    from src.ingest.youtube_api import YouTubeApiClient
    path = save_capture(YouTubeApiClient().fetch_capture(args.video_id, args.type))
    print(f"保存しました: {path}")
    return 0


def cmd_check(args) -> int:
    capture = load_capture(Path(args.path))
    print(f"OK: {capture.content_id} / {capture.title} / コメント {len(capture.comments)} 件")
    return 0


def cmd_comments(args) -> int:
    capture = load_capture(cache_path(args.content_id))
    ranked = rank_timestamp_comments(capture.comments)
    if not ranked:
        print("時刻の行があるコメントはありません")
        return 1
    for index, comment, count in ranked[:args.limit]:
        first = extract_timestamp_lines(comment.text)[0].raw_line
        print(f"[{index}] 時刻の行 {count} / いいね {comment.likes} / 先頭: {first[:60]}")
    return 0


def cmd_prepare(args) -> int:
    capture = load_capture(cache_path(args.content_id))
    chosen = choose_comment(capture, args.comment)
    if chosen is None:
        print("職人さんのコメント(時刻の行があるコメント)が見つかりません")
        return 1
    index, comment = chosen
    dataset = TableRepository(args.dir).load()
    rows = build_staged_rows(dataset, extract_timestamp_lines(comment.text))
    content_path, rows_path = save_staged(build_content_row(capture), rows)
    print(f"コメント [{index}] から {len(rows)} 行の下書きを作りました")
    print(f"  {content_path}\n  {rows_path}")
    print(rows["match"].value_counts().to_string())
    return 0


def cmd_apply(args) -> int:
    repo = TableRepository(args.dir)
    dataset = repo.load()
    content_row, rows = load_staged(args.content_id)
    result = apply_staged(dataset, content_row, rows, replace=args.replace)
    issues = validate_dataset(dataset)
    for issue in issues:
        print(issue)
    print(f"歌唱 {result.performances} 件 / 新しい曲 {len(result.new_songs)} / 新しいアーティスト "
          f"{len(result.new_artists)} / 新しい表記 {result.new_aliases} / 取り込まない行 {result.skipped}")
    if has_errors(issues):
        print("検査で問題があったので、保存しませんでした")
        return 1
    if args.dry_run:
        print("(dry-run のため保存していません)")
        return 0
    repo.save(dataset)
    print(f"保存しました: {args.dir}")
    return 0


def cmd_status(args) -> int:
    registered = set(TableRepository(args.dir).load()["contents"]["content_id"])
    for path in sorted(Path(CACHE_DIR).glob("*.json")):
        capture = load_capture(path)
        staged = staged_paths(capture.content_id)[1].exists()
        state = "登録済み" if capture.content_id in registered else ("下書きあり" if staged else "未処理")
        print(f"{state}\t{capture.content_id}\t{capture.published_jst:%Y-%m-%d}\t{capture.title[:40]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ingest", description="データの取り込み")
    parser.add_argument("--dir", default=DEFAULT_DIR, help=f"データのディレクトリ(既定: {DEFAULT_DIR})")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("from-ytdlp", help="yt-dlp の info.json を取得結果にする")
    p.add_argument("info_json")
    p.add_argument("--type", default="live", choices=["live", "video", "short"])
    p.set_defaults(func=cmd_from_ytdlp)

    p = sub.add_parser("from-api", help="YouTube Data API で取得する(YOUTUBE_API_KEY が必要)")
    p.add_argument("video_id")
    p.add_argument("--type", default="live", choices=["live", "video", "short"])
    p.set_defaults(func=cmd_from_api)

    p = sub.add_parser("check", help="取得結果 JSON の形を確かめる")
    p.add_argument("path")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("comments", help="時刻の行があるコメントの候補を表示する")
    p.add_argument("content_id")
    p.add_argument("--limit", type=int, default=5)
    p.set_defaults(func=cmd_comments)

    p = sub.add_parser("prepare", help="下書きを作る")
    p.add_argument("content_id")
    p.add_argument("--comment", type=int, help="使うコメントの番号(comments で表示される番号)")
    p.set_defaults(func=cmd_prepare)

    p = sub.add_parser("apply", help="判断の終わった下書きをデータに追記する")
    p.add_argument("content_id")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--replace", action="store_true", help="同じコンテンツが登録済みなら置き換える")
    p.set_defaults(func=cmd_apply)

    sub.add_parser("status", help="取得結果と登録の状況").set_defaults(func=cmd_status)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError) as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
