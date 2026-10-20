"""
データモデル v2 の操作 CLI

使い方(コンテナの中で。--dir はサブコマンドの前に書く):
  python -m src.cli.data [--dir data/v2] validate
  python -m src.cli.data [--dir data/v2] show [--limit 30]
  python -m src.cli.data [--dir data/v2] renumber <content_id>
  python -m src.cli.data [--dir data/v2] merge-song <残す song_id> <消す song_id>
  python -m src.cli.data [--dir data/v2] merge-artist <残す artist_id> <消す artist_id>
  python -m src.cli.data [--dir data/v2] set <テーブル> <主キー> <列> <値>   # 例: set songs s0003 kind オリジナル
  python -m src.cli.data [--dir data/v2] normalize   # 並べ直して保存し直す
"""

import argparse
import sys
from typing import List, Optional

import pandas as pd

from src.core import dataset_ops
from src.core.validation import has_errors, validate_dataset
from src.core.views import build_performance_view, build_song_stats
from src.repositories.table_repository import TableRepository

DEFAULT_DIR = "data/v2"


def _print_issues(issues) -> None:
    if not issues:
        print("問題はありません")
    for issue in issues:
        print(issue)


def cmd_validate(repo: TableRepository, args) -> int:
    issues = validate_dataset(repo.load())
    _print_issues(issues)
    return 1 if has_errors(issues) else 0


def cmd_show(repo: TableRepository, args) -> int:
    dataset = repo.load()
    view = build_performance_view(dataset)
    stats = build_song_stats(dataset, view)
    with pd.option_context("display.max_rows", args.limit, "display.max_columns", None,
                           "display.width", 200, "display.unicode.east_asian_width", True):
        print(f"== 歌唱の一覧({len(view)} 件。先頭 {args.limit} 件)")
        print(view[["date", "no", "title", "artist", "style", "part", "link"]].head(args.limit).to_string(index=False))
        print(f"\n== 曲ごとの集計({len(stats)} 曲)")
        print(stats[["title", "artist", "count", "last_date", "acoustic_count", "latest_link"]]
              .head(args.limit).to_string(index=False))
    return 0


def _save_after(repo: TableRepository, dataset) -> int:
    issues = validate_dataset(dataset)
    if has_errors(issues):
        _print_issues(issues)
        print("検査で問題があったので、保存しませんでした")
        return 1
    repo.save(dataset)
    return 0


def cmd_renumber(repo: TableRepository, args) -> int:
    dataset = repo.load()
    count = dataset_ops.renumber(dataset, args.content_id)
    print(f"{args.content_id}: {count} 件の曲順を振り直しました")
    return _save_after(repo, dataset)


def cmd_merge_song(repo: TableRepository, args) -> int:
    dataset = repo.load()
    moved = dataset_ops.merge_song(dataset, args.keep, args.drop)
    print(f"{args.drop} を {args.keep} にまとめました(歌唱 {moved} 件を付け替え)")
    return _save_after(repo, dataset)


def cmd_merge_artist(repo: TableRepository, args) -> int:
    dataset = repo.load()
    moved = dataset_ops.merge_artist(dataset, args.keep, args.drop)
    print(f"{args.drop} を {args.keep} にまとめました(曲 {moved} 件を付け替え)")
    return _save_after(repo, dataset)


def cmd_set(repo: TableRepository, args) -> int:
    dataset = repo.load()
    before = dataset_ops.set_value(dataset, args.table, args.key, args.column, args.value)
    print(f"{args.table} {args.key} の {args.column}: 「{before}」→「{args.value}」")
    return _save_after(repo, dataset)


def cmd_normalize(repo: TableRepository, args) -> int:
    return _save_after(repo, repo.load())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="data", description="データモデル v2 の検査と操作")
    parser.add_argument("--dir", default=DEFAULT_DIR, help=f"データのディレクトリ(既定: {DEFAULT_DIR})")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="整合性を検査する").set_defaults(func=cmd_validate)
    show = sub.add_parser("show", help="歌唱の一覧と曲ごとの集計を表示する")
    show.add_argument("--limit", type=int, default=30)
    show.set_defaults(func=cmd_show)
    renumber = sub.add_parser("renumber", help="コンテンツの曲順を 10, 20, 30… に振り直す")
    renumber.add_argument("content_id")
    renumber.set_defaults(func=cmd_renumber)
    for name, func, label in (("merge-song", cmd_merge_song, "song_id"),
                              ("merge-artist", cmd_merge_artist, "artist_id")):
        p = sub.add_parser(name, help=f"同じだった2つの {label} をまとめる")
        p.add_argument("keep", help=f"残す {label}")
        p.add_argument("drop", help=f"消す {label}")
        p.set_defaults(func=func)
    p = sub.add_parser("set", help="1行の1つの値を直す(検査を通ったときだけ保存する)")
    p.add_argument("table", help="contents / artists / songs / performances / aliases")
    p.add_argument("key", help="主キーの値。複数の列のときはカンマ区切り(例: yt:rPoEadXC5ck,20)")
    p.add_argument("column")
    p.add_argument("value", help="新しい値(空にするときは \"\")")
    p.set_defaults(func=cmd_set)
    sub.add_parser("normalize", help="決まった順に並べ直して保存し直す").set_defaults(func=cmd_normalize)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(TableRepository(args.dir), args)
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
