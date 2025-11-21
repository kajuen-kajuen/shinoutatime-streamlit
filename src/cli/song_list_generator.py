"""
曲リスト自動生成CLIモジュール

V_SONG_LIST.TSVを自動生成するコマンドラインインターフェースを提供します。
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List

from src.config.logging_config import setup_logging
from src.repositories.live_repository import LiveRepository
from src.repositories.timestamp_repository import TimestampRepository
from src.repositories.song_list_repository import SongListRepository
from src.services.song_list_service import SongListService
from src.models.song_list_models import SongInfo, SimilarityWarning, DiffResult
from src.exceptions.errors import DataLoadError, FileWriteError

# バージョン情報
__version__ = "1.0.0"


def create_parser() -> argparse.ArgumentParser:
    """
    コマンドライン引数パーサーを作成
    
    Returns:
        設定済みのArgumentParserオブジェクト
    """
    parser = argparse.ArgumentParser(
        prog='song_list_generator',
        description='V_SONG_LIST.TSVを自動生成するツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # デフォルトのファイルパスで実行
  python -m src.cli.song_list_generator
  
  # カスタムファイルパスを指定
  python -m src.cli.song_list_generator --live-file data/M_YT_LIVE.TSV \\
      --timestamp-file data/M_YT_LIVE_TIMESTAMP.TSV \\
      --output-file data/V_SONG_LIST.TSV
  
  # ドライランモード（ファイルを書き込まない）
  python -m src.cli.song_list_generator --dry-run
  
  # 詳細ログを表示
  python -m src.cli.song_list_generator --verbose
  
  # 類似性チェックを無効化
  python -m src.cli.song_list_generator --no-similarity-check
        """
    )
    
    # 入力ファイルのオプション
    parser.add_argument(
        '--live-file',
        type=str,
        default='data/M_YT_LIVE.TSV',
        help='M_YT_LIVE.TSVのパス (デフォルト: data/M_YT_LIVE.TSV)'
    )
    
    parser.add_argument(
        '--timestamp-file',
        type=str,
        default='data/M_YT_LIVE_TIMESTAMP.TSV',
        help='M_YT_LIVE_TIMESTAMP.TSVのパス (デフォルト: data/M_YT_LIVE_TIMESTAMP.TSV)'
    )
    
    # 出力ファイルのオプション
    parser.add_argument(
        '--output-file',
        type=str,
        default='data/V_SONG_LIST.TSV',
        help='V_SONG_LIST.TSVの出力パス (デフォルト: data/V_SONG_LIST.TSV)'
    )
    
    # ドライランモード
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='ドライランモード（ファイルを書き込まない）'
    )
    
    # 類似性チェックのオプション
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.85,
        help='類似度チェックの閾値 (0.0-1.0, デフォルト: 0.85)'
    )
    
    parser.add_argument(
        '--no-similarity-check',
        action='store_true',
        help='類似性チェックを無効化'
    )
    
    # ログレベルのオプション
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細ログを表示'
    )
    
    # バージョン情報
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    return parser


def setup_cli_logging(verbose: bool) -> None:
    """
    CLIのログ設定を行う
    
    Args:
        verbose: 詳細ログを有効にするか
    """
    # ログレベルを設定
    log_level = "DEBUG" if verbose else "INFO"
    
    # ログ設定を初期化（コンソール出力のみ）
    setup_logging(log_level=log_level, enable_file_logging=False)
    
    # ロガーを取得
    logger = logging.getLogger(__name__)
    
    if verbose:
        logger.debug("詳細ログモードが有効になりました")


def print_summary(
    songs: List[SongInfo],
    warnings: List[SimilarityWarning],
    diff_result: DiffResult,
    output_file: str,
    dry_run: bool
) -> None:
    """
    処理サマリーを表示
    
    Args:
        songs: 生成された曲リスト
        warnings: 類似性警告リスト
        diff_result: 差分結果
        output_file: 出力ファイルパス
        dry_run: ドライランモードかどうか
    """
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("処理サマリー")
    logger.info("=" * 60)
    
    # 処理されたレコード数
    logger.info(f"生成された曲数: {len(songs)}件")
    
    # 出力ファイルパス
    if dry_run:
        logger.info(f"出力ファイル: {output_file} (ドライランモード - 保存されていません)")
    else:
        logger.info(f"出力ファイル: {output_file}")
    
    # 差分情報
    logger.info("")
    logger.info("差分情報:")
    logger.info(f"  追加: {len(diff_result.added)}件")
    logger.info(f"  削除: {len(diff_result.removed)}件")
    logger.info(f"  更新: {len(diff_result.updated)}件")
    
    # 追加された曲の詳細（最大10件まで表示）
    if diff_result.added:
        logger.info("")
        logger.info("追加された曲（最大10件）:")
        for i, song in enumerate(diff_result.added[:10], 1):
            logger.info(f"  {i}. {song.artist} - {song.song_name}")
        if len(diff_result.added) > 10:
            logger.info(f"  ... 他 {len(diff_result.added) - 10}件")
    
    # 削除された曲の詳細（最大10件まで表示）
    if diff_result.removed:
        logger.info("")
        logger.info("削除された曲（最大10件）:")
        for i, song in enumerate(diff_result.removed[:10], 1):
            logger.info(f"  {i}. {song.artist} - {song.song_name}")
        if len(diff_result.removed) > 10:
            logger.info(f"  ... 他 {len(diff_result.removed) - 10}件")
    
    # 類似性警告
    if warnings:
        logger.info("")
        logger.warning(f"類似性警告: {len(warnings)}件")
        logger.warning("以下のアーティスト名または曲名が類似しています:")
        
        # アーティスト名の警告
        artist_warnings = [w for w in warnings if w.type == 'artist']
        if artist_warnings:
            logger.warning("")
            logger.warning("アーティスト名:")
            for i, warning in enumerate(artist_warnings[:10], 1):
                logger.warning(
                    f"  {i}. '{warning.item1}' と '{warning.item2}' "
                    f"(類似度: {warning.similarity:.2f})"
                )
            if len(artist_warnings) > 10:
                logger.warning(f"  ... 他 {len(artist_warnings) - 10}件")
        
        # 曲名の警告
        song_warnings = [w for w in warnings if w.type == 'song']
        if song_warnings:
            logger.warning("")
            logger.warning("曲名:")
            for i, warning in enumerate(song_warnings[:10], 1):
                logger.warning(
                    f"  {i}. '{warning.item1}' と '{warning.item2}' "
                    f"(類似度: {warning.similarity:.2f})"
                )
            if len(song_warnings) > 10:
                logger.warning(f"  ... 他 {len(song_warnings) - 10}件")
    else:
        logger.info("")
        logger.info("類似性警告: なし")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("処理が正常に完了しました")
    logger.info("=" * 60)


def run_generation(
    live_file: str,
    timestamp_file: str,
    output_file: str,
    dry_run: bool,
    similarity_threshold: float,
    no_similarity_check: bool
) -> tuple[List[SongInfo], List[SimilarityWarning], DiffResult]:
    """
    曲リスト生成処理を実行
    
    Args:
        live_file: M_YT_LIVE.TSVのパス
        timestamp_file: M_YT_LIVE_TIMESTAMP.TSVのパス
        output_file: V_SONG_LIST.TSVの出力パス
        dry_run: ドライランモード
        similarity_threshold: 類似度チェックの閾値
        no_similarity_check: 類似性チェックを無効化するか
        
    Returns:
        (生成された曲リスト, 類似性警告リスト, 差分結果)のタプル
        
    Raises:
        DataLoadError: データの読み込みに失敗した場合
        FileWriteError: ファイルの書き込みに失敗した場合
    """
    logger = logging.getLogger(__name__)
    
    # リポジトリを初期化
    logger.info("リポジトリを初期化しています...")
    live_repo = LiveRepository(live_file)
    timestamp_repo = TimestampRepository(timestamp_file)
    song_list_repo = SongListRepository(output_file)
    
    # サービスを初期化
    logger.info("サービスを初期化しています...")
    service = SongListService(live_repo, timestamp_repo)
    
    # 曲リストを生成
    logger.info("曲リストを生成しています...")
    songs = service.generate_song_list()
    
    # 類似性チェック
    warnings = []
    if not no_similarity_check:
        logger.info("類似性チェックを実行しています...")
        warnings = service.check_similarity(songs, similarity_threshold)
    else:
        logger.info("類似性チェックはスキップされました")
    
    # 既存ファイルとの差分を検出
    logger.info("既存ファイルとの差分を検出しています...")
    diff_result = service.compare_with_existing(songs, output_file)
    
    # ファイルに保存（ドライランモードでない場合）
    if not dry_run:
        logger.info("曲リストをファイルに保存しています...")
        song_list_repo.save_all(songs)
        logger.info(f"曲リストを保存しました: {output_file}")
    else:
        logger.info("ドライランモード: ファイルは保存されませんでした")
    
    return songs, warnings, diff_result


def main():
    """
    メイン処理
    
    コマンドライン引数を解析し、曲リスト生成処理を実行します。
    """
    # 引数パーサーを作成
    parser = create_parser()
    args = parser.parse_args()
    
    # ログ設定を初期化
    setup_cli_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # ヘッダー情報を表示
        logger.info("=" * 60)
        logger.info(f"曲リスト自動生成ツール v{__version__}")
        logger.info("=" * 60)
        logger.info(f"入力ファイル:")
        logger.info(f"  配信情報: {args.live_file}")
        logger.info(f"  タイムスタンプ情報: {args.timestamp_file}")
        logger.info(f"出力ファイル: {args.output_file}")
        logger.info(f"ドライランモード: {args.dry_run}")
        
        if args.no_similarity_check:
            logger.info("類似性チェック: 無効")
        else:
            logger.info(f"類似性チェック: 有効 (閾値: {args.similarity_threshold})")
        
        logger.info("=" * 60)
        
        # 曲リスト生成処理を実行
        songs, warnings, diff_result = run_generation(
            live_file=args.live_file,
            timestamp_file=args.timestamp_file,
            output_file=args.output_file,
            dry_run=args.dry_run,
            similarity_threshold=args.similarity_threshold,
            no_similarity_check=args.no_similarity_check
        )
        
        # 処理サマリーを表示
        print_summary(songs, warnings, diff_result, args.output_file, args.dry_run)
        
        return 0
        
    except DataLoadError as e:
        # データ読み込みエラー
        logger.error("=" * 60)
        logger.error(f"[ERROR] データの読み込みに失敗しました")
        logger.error(f"  ファイル: {e.file_path}")
        logger.error(f"  詳細: {e.message}")
        logger.error("=" * 60)
        return 1
        
    except FileWriteError as e:
        # ファイル書き込みエラー
        logger.error("=" * 60)
        logger.error(f"[ERROR] ファイルの書き込みに失敗しました")
        logger.error(f"  ファイル: {e.file_path}")
        logger.error(f"  詳細: {e.message}")
        logger.error("=" * 60)
        return 1
        
    except Exception as e:
        # 予期しないエラー
        logger.error("=" * 60)
        logger.error(f"[ERROR] 予期しないエラーが発生しました")
        logger.error(f"  エラー: {type(e).__name__}: {e}")
        logger.error("=" * 60)
        logger.exception("詳細なエラー情報:")
        return 1


if __name__ == '__main__':
    sys.exit(main())
