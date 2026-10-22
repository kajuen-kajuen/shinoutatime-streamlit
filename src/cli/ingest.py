"""
取り込み CLI(取得結果 → 下書き → 追記)

使い方(コンテナの中で):
  python -m src.cli.ingest list [--month 2025-04]                  # チャンネルの投稿の一覧(読むだけ)
  python -m src.cli.ingest fetch --month 2025-04 [--force]         # その月の投稿をまとめて API で取得
  python -m src.cli.ingest others --month 2025-04                  # 本人以外のチャンネルの動画を検索(読むだけ)
  python -m src.cli.ingest from-api <動画ID> [--type live]       # 1本を YouTube Data API で取得(種類は自動)
  python -m src.cli.ingest from-ytdlp <info.json> [--type live]   # yt-dlp の JSON を取得結果にする
  python -m src.cli.ingest check <取得結果.json>                  # 取得結果の形を確かめる
  python -m src.cli.ingest comments <content_id>                  # 時刻の行があるコメントの候補を表示
  python -m src.cli.ingest prepare <content_id> [--comment N]     # 下書きを作る(コメントが無ければタイトルから)
  python -m src.cli.ingest apply <content_id> [--dry-run] [--replace]
  python -m src.cli.ingest skip <content_id> "<理由>"             # 曲の無いコンテンツとして記録する
  python -m src.cli.ingest unskip <content_id>                    # 曲なしの記録を外す(登録し直すとき)
  python -m src.cli.ingest status [--month 2025-04]

API キーは環境変数 YOUTUBE_API_KEY(.env から docker-compose で渡す)。複数のキーは YOUTUBE_API_KEYS(カンマ区切り)に書く。

ブラウザで取得するときは、Claude が取得結果 JSON を data/ingest/cache/ に書き、check で確かめる。
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from src.core.validation import has_errors, validate_dataset
from src.ingest.capture import CACHE_DIR, cache_path, from_ytdlp_info, load_capture, save_capture
from src.ingest.parser import (build_content_row, build_rows_from_title, build_staged_rows, choose_comment,
                               extract_timestamp_lines, rank_timestamp_comments)
from src.ingest.skips import add_skip, load_skips, remove_skip
from src.ingest.staging import STAGED_DIR, apply_staged, load_staged, save_staged, staged_paths
from src.repositories.table_repository import TableRepository, sort_table

DEFAULT_DIR = "data/v2"


def cmd_from_ytdlp(args) -> int:
    info = json.loads(Path(args.info_json).read_text(encoding="utf-8"))
    path = save_capture(from_ytdlp_info(info, args.type))
    print(f"保存しました: {path}")
    return 0


def cmd_from_api(args) -> int:
    from src.ingest.youtube_api import YouTubeApiClient
    capture = YouTubeApiClient().fetch_capture(args.video_id, args.type)
    path = save_capture(capture)
    print(f"保存しました: {path}({capture.type}、コメント {len(capture.comments)} 件)")
    return 0


def _uploads(month: Optional[str]):
    from src.ingest.youtube_api import YouTubeApiClient
    client = YouTubeApiClient()
    videos = client.list_uploads()
    if month:
        videos = [v for v in videos if v.published_jst.strftime("%Y-%m") == month]
    return client, videos


def cmd_list(args) -> int:
    _, videos = _uploads(args.month)
    for v in videos:
        kind = "live" if v.is_live else f"{v.duration_seconds}s"
        print(f"{v.published_jst:%Y-%m-%d %H:%M}\t{v.content_id}\t{kind}\t{v.title[:50]}")
    print(f"{len(videos)} 本")
    return 0


def cmd_others(args) -> int:
    from src.ingest.youtube_api import YouTubeApiClient
    found = YouTubeApiClient().search_other_channels(args.month)
    skips = load_skips()
    for v, channel in found:
        state = "曲なし" if v.content_id in skips else ("取得済み" if cache_path(v.content_id).exists() else "")
        print(f"{v.published_jst:%Y-%m-%d %H:%M}\t{v.content_id}\t{channel[:20]}\t{state}\t{v.title[:50]}")
    print(f"{len(found)} 本(ファンの切り抜きなども混じる。対象にするかは update-data.md の決まりで判断する)")
    return 0


def cmd_fetch(args) -> int:
    from src.ingest.youtube_api import QUOTA_REASONS, YouTubeApiError
    client, videos = _uploads(args.month)
    fetched = skipped = failed = 0
    for v in videos:
        if cache_path(v.content_id).exists() and not args.force:
            skipped += 1
            continue
        try:
            capture = client.fetch_capture(v.video_id)
        except YouTubeApiError as e:
            # 1本の失敗で止めず、残りを取る。すべてのキーで上限のときは、続けても失敗するので止める
            failed += 1
            print(f"失敗: {v.content_id}\t{e}", file=sys.stderr)
            if e.reason in QUOTA_REASONS:
                break
            continue
        save_capture(capture)
        fetched += 1
        print(f"取得: {v.content_id}\t{capture.type}\tコメント {len(capture.comments)} 件\t{v.title[:40]}")
    print(f"取得 {fetched} 本 / 取得済みのため飛ばした {skipped} 本 / 失敗 {failed} 本")
    return 1 if failed else 0


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
    dataset = TableRepository(args.dir).load()
    chosen = choose_comment(capture, args.comment)
    if chosen is None and capture.type in ("video", "short"):
        rows = build_rows_from_title(dataset, capture)
        source = "タイトル"
    elif chosen is None:
        print("職人さんのコメント(時刻の行があるコメント)が見つかりません。曲が無ければ skip で記録してください")
        return 1
    else:
        index, comment = chosen
        rows = build_staged_rows(dataset, extract_timestamp_lines(comment.text))
        source = f"コメント [{index}]"
    content_path, rows_path = save_staged(build_content_row(capture), rows)
    print(f"{source} から {len(rows)} 行の下書きを作りました")
    print(f"  {content_path}\n  {rows_path}")
    print(rows["match"].value_counts().to_string())
    return 0


def cmd_apply(args) -> int:
    # 曲なしの記録があるものを登録すると、登録済みと曲なしの両方になる(skip は登録済みを拒むので、逆も止める)
    skips = load_skips()
    if args.content_id in skips:
        print(f"{args.content_id} は曲なしとして記録されています({skips[args.content_id]})。"
              f"登録するなら先に unskip してください")
        return 1
    repo = TableRepository(args.dir)
    dataset = repo.load()
    content_row, rows = load_staged(args.content_id)
    result = apply_staged(dataset, content_row, rows, replace=args.replace)
    # 保存のときと同じ順に並べてから検査する(dry-run で並び順の警告が出ないように)
    for name in list(dataset.tables):
        dataset[name] = sort_table(name, dataset[name], dataset)
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


def cmd_skip(args) -> int:
    registered = set(TableRepository(args.dir).load()["contents"]["content_id"])
    if args.content_id in registered:
        print(f"{args.content_id} は登録済みです(曲なしにはできません)")
        return 1
    add_skip(args.content_id, args.reason)
    print(f"曲なしとして記録しました: {args.content_id}({args.reason})")
    return 0


def cmd_unskip(args) -> int:
    try:
        reason = remove_skip(args.content_id)
    except KeyError:
        print(f"{args.content_id} は曲なしとして記録されていません")
        return 1
    print(f"曲なしの記録を外しました: {args.content_id}({reason})")
    return 0


def cmd_status(args) -> int:
    registered = set(TableRepository(args.dir).load()["contents"]["content_id"])
    skips = load_skips()
    counts = {}
    for path in sorted(Path(CACHE_DIR).glob("*.json")):
        capture = load_capture(path)
        if args.month and capture.published_jst.strftime("%Y-%m") != args.month:
            continue
        if capture.content_id in registered:
            state = "登録済み"
        elif capture.content_id in skips:
            state = "曲なし"
        elif staged_paths(capture.content_id)[1].exists():
            state = "下書きあり"
        else:
            state = "未処理"
        counts[state] = counts.get(state, 0) + 1
        print(f"{state}\t{capture.content_id}\t{capture.type}\t{capture.published_jst:%Y-%m-%d}\t{capture.title[:40]}")
    print(" / ".join(f"{k} {v}" for k, v in counts.items()) or "取得結果がありません")
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
    p.add_argument("--type", default=None, choices=["live", "video", "short"], help="省くと自動で決める")
    p.set_defaults(func=cmd_from_api)

    p = sub.add_parser("list", help="チャンネルの投稿の一覧(読むだけ)")
    p.add_argument("--month", help="YYYY-MM(日本時間)")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("others", help="その月の、本人以外のチャンネルの動画を検索する(読むだけ。100 ユニット/ページ)")
    p.add_argument("--month", required=True, help="YYYY-MM")
    p.set_defaults(func=cmd_others)

    p = sub.add_parser("fetch", help="その月の投稿をまとめて API で取得する")
    p.add_argument("--month", required=True, help="YYYY-MM(日本時間)")
    p.add_argument("--force", action="store_true", help="取得済みのものも取り直す")
    p.set_defaults(func=cmd_fetch)

    p = sub.add_parser("skip", help="曲の無いコンテンツとして記録する(data/ingest/skipped.tsv)")
    p.add_argument("content_id")
    p.add_argument("reason")
    p.set_defaults(func=cmd_skip)

    p = sub.add_parser("unskip", help="曲なしの記録を外す(曲なしにしていたものを登録するとき)")
    p.add_argument("content_id")
    p.set_defaults(func=cmd_unskip)

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

    p = sub.add_parser("status", help="取得結果と登録の状況")
    p.add_argument("--month", help="YYYY-MM(日本時間)")
    p.set_defaults(func=cmd_status)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    from src.ingest.youtube_api import QUOTA_REASONS, YouTubeApiError
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError) as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1
    except YouTubeApiError as e:
        # メッセージには URL(API キー)を入れていない(YouTubeApiError)
        print(f"エラー: {e}", file=sys.stderr)
        if e.reason in QUOTA_REASONS:
            print("すべての API キーで上限に達しました。時間をおいて(日本時間の16〜17時以降に)流し直してください",
                  file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
