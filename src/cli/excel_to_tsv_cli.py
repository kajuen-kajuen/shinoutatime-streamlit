"""
Excel to TSV変換CLIモジュール

ExcelファイルからTSVファイルへの変換を行うコマンドラインインターフェースを提供します。
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.config.logging_config import setup_logging
from src.repositories.excel_repository import ExcelRepository
from src.repositories.tsv_repository import TsvRepository
from src.repositories.backup_repository import BackupRepository
from src.services.excel_to_tsv_service import ExcelToTsvService
from src.models.excel_to_tsv_models import ConversionResult
from src.exceptions.errors import DataLoadError, DataSaveError

# バージョン情報
__version__ = "1.0.0"


def create_parser() -> argparse.ArgumentParser:
    """
    コマンドライン引数パーサーを作成
    
    Returns:
        設定済みのArgumentParserオブジェクト
    """
    parser = argparse.ArgumentParser(
        prog='excel_to_tsv',
        description='ExcelファイルからTSVファイルへの変換ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # デフォルトのファイルパスで実行
  python -m src.cli.excel_to_tsv_cli
  
  # カスタムファイルパスを指定
  python -m src.cli.excel_to_tsv_cli --input-file data/data.xlsx \\
      --output-dir data/
  
  # ドライランモード（ファイルを書き込まない）
  python -m src.cli.excel_to_tsv_cli --dry-run
  
  # 詳細ログを表示
  python -m src.cli.excel_to_tsv_cli --verbose
  
  # song_list_generatorの実行をスキップ
  python -m src.cli.excel_to_tsv_cli --skip-song-list
        """
    )
    
    # 入力ファイルのオプション（要件6.1, 6.2）
    parser.add_argument(
        '--input-file',
        type=str,
        default='data/data.xlsx',
        help='入力Excelファイルのパス (デフォルト: data/data.xlsx)'
    )
    
    # 出力ディレクトリのオプション（要件6.3）
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/',
        help='出力ディレクトリのパス (デフォルト: data/)'
    )
    
    # ドライランモード（要件6.5）
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='ドライランモード（ファイルを書き込まない）'
    )
    
    # song_list_generatorのスキップオプション（要件9.5）
    parser.add_argument(
        '--skip-song-list',
        action='store_true',
        help='song_list_generatorの実行をスキップ'
    )
    
    # ログレベルのオプション
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細ログを表示'
    )
    
    # ヘルプオプション（要件6.4）
    # argparseが自動的に--helpを追加するため、明示的な定義は不要
    
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


def print_header(input_file: str, output_dir: str, dry_run: bool, skip_song_list: bool) -> None:
    """
    ヘッダー情報を表示（要件5.1）
    
    Args:
        input_file: 入力ファイルパス
        output_dir: 出力ディレクトリパス
        dry_run: ドライランモードかどうか
        skip_song_list: song_list_generatorをスキップするか
    """
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info(f"Excel to TSV変換ツール v{__version__}")
    logger.info("=" * 60)
    logger.info(f"入力ファイル: {input_file}")
    logger.info(f"出力ディレクトリ: {output_dir}")
    logger.info(f"ドライランモード: {dry_run}")
    logger.info(f"song_list_generator実行: {'スキップ' if skip_song_list else '有効'}")
    logger.info("=" * 60)


def print_summary(result: ConversionResult, start_time: datetime, dry_run: bool) -> None:
    """
    処理サマリーを表示（要件5.5）
    
    Args:
        result: 変換処理の結果
        start_time: 処理開始時刻
        dry_run: ドライランモードかどうか
    """
    logger = logging.getLogger(__name__)
    
    # 処理時間を計算
    end_time = datetime.now()
    elapsed_time = (end_time - start_time).total_seconds()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("処理サマリー")
    logger.info("=" * 60)
    
    # 成功/失敗の統計
    if result.success:
        logger.info(f"結果: 成功")
    else:
        logger.warning(f"結果: 失敗")
    
    # 生成されたファイル
    logger.info(f"生成されたファイル: {len(result.files_created)}件")
    if result.files_created:
        for file_path in result.files_created:
            if dry_run:
                logger.info(f"  [ドライラン] {file_path}")
            else:
                logger.info(f"  {file_path}")
    
    # バックアップファイル
    if result.backup_files:
        logger.info(f"バックアップファイル: {len(result.backup_files)}件")
        for backup_path in result.backup_files:
            logger.info(f"  {backup_path}")
    
    # 警告
    if result.warnings:
        logger.warning(f"警告: {len(result.warnings)}件")
        # 警告の詳細を表示（最大10件まで）
        for i, warning in enumerate(result.warnings[:10], 1):
            logger.warning(
                f"  {i}. シート '{warning.sheet_name}' 行{warning.row_number}: "
                f"{warning.message}"
            )
        if len(result.warnings) > 10:
            logger.warning(f"  ... 他 {len(result.warnings) - 10}件")
    else:
        logger.info("警告: なし")
    
    # エラー
    if result.errors:
        logger.error(f"エラー: {len(result.errors)}件")
        for i, error in enumerate(result.errors, 1):
            logger.error(f"  {i}. {error}")
    else:
        logger.info("エラー: なし")
    
    # 処理時間
    logger.info(f"処理時間: {elapsed_time:.2f}秒")
    
    logger.info("=" * 60)
    
    if result.success:
        logger.info("処理が正常に完了しました")
    else:
        logger.error("処理が失敗しました")
    
    logger.info("=" * 60)


def run_conversion(
    input_file: str,
    output_dir: str,
    dry_run: bool,
    skip_song_list: bool
) -> ConversionResult:
    """
    Excel to TSV変換処理を実行
    
    Args:
        input_file: 入力Excelファイルのパス
        output_dir: 出力ディレクトリのパス
        dry_run: ドライランモード
        skip_song_list: song_list_generatorをスキップするか
        
    Returns:
        変換処理の結果
        
    Raises:
        DataLoadError: データの読み込みに失敗した場合
        DataSaveError: データの保存に失敗した場合
    """
    logger = logging.getLogger(__name__)
    
    # リポジトリを初期化
    logger.info("リポジトリを初期化しています...")
    excel_repo = ExcelRepository(input_file)
    tsv_repo = TsvRepository(output_dir)
    backup_repo = BackupRepository()
    
    # サービスを初期化
    logger.info("サービスを初期化しています...")
    service = ExcelToTsvService(excel_repo, tsv_repo, backup_repo)
    
    # Excel to TSV変換を実行
    logger.info("Excel to TSV変換を開始します...")
    result = service.convert_excel_to_tsv(
        input_file=input_file,
        output_dir=output_dir,
        dry_run=dry_run
    )
    
    # song_list_generatorを実行（要件9.1, 9.2, 9.5）
    if not skip_song_list and result.success and not dry_run:
        logger.info("")
        logger.info("song_list_generatorを実行します...")
        
        # 生成されたTSVファイルのパスを取得
        live_file = str(Path(output_dir) / "M_YT_LIVE.TSV")
        timestamp_file = str(Path(output_dir) / "M_YT_LIVE_TIMESTAMP.TSV")
        output_file = str(Path(output_dir) / "V_SONG_LIST.TSV")
        
        # song_list_generatorを実行
        song_list_success = service.run_song_list_generator(
            live_file=live_file,
            timestamp_file=timestamp_file,
            output_file=output_file
        )
        
        if song_list_success:
            logger.info(f"V_SONG_LIST.TSVが生成されました: {output_file}")
        else:
            # song_list_generatorのエラーは警告として扱う（要件9.4）
            logger.warning(
                "song_list_generatorの実行に失敗しましたが、"
                "TSVファイルは正常に生成されています"
            )
    
    return result


def main() -> int:
    """
    メイン処理
    
    コマンドライン引数を解析し、Excel to TSV変換処理を実行します。
    
    Returns:
        終了コード（0: 成功、1: 失敗）
    """
    # 引数パーサーを作成
    parser = create_parser()
    args = parser.parse_args()
    
    # ログ設定を初期化
    setup_cli_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # 処理開始時刻を記録
    start_time = datetime.now()
    
    try:
        # ヘッダー情報を表示（要件5.1）
        print_header(
            input_file=args.input_file,
            output_dir=args.output_dir,
            dry_run=args.dry_run,
            skip_song_list=args.skip_song_list
        )
        
        # Excel to TSV変換処理を実行
        result = run_conversion(
            input_file=args.input_file,
            output_dir=args.output_dir,
            dry_run=args.dry_run,
            skip_song_list=args.skip_song_list
        )
        
        # 処理サマリーを表示（要件5.5）
        print_summary(result, start_time, args.dry_run)
        
        # 終了コードを返す
        return 0 if result.success else 1
        
    except DataLoadError as e:
        # データ読み込みエラー（要件5.4）
        logger.error("")
        logger.error("=" * 60)
        logger.error("[ERROR] データの読み込みに失敗しました")
        logger.error(f"  ファイル: {e.file_path}")
        logger.error(f"  詳細: {e.message}")
        logger.error("=" * 60)
        return 1
        
    except DataSaveError as e:
        # データ保存エラー（要件5.4）
        logger.error("")
        logger.error("=" * 60)
        logger.error("[ERROR] データの保存に失敗しました")
        logger.error(f"  ファイル: {e.file_path}")
        logger.error(f"  詳細: {e.message}")
        logger.error("=" * 60)
        return 1
        
    except Exception as e:
        # 予期しないエラー（要件5.4）
        logger.error("")
        logger.error("=" * 60)
        logger.error("[ERROR] 予期しないエラーが発生しました")
        logger.error(f"  エラー: {type(e).__name__}: {e}")
        logger.error("=" * 60)
        logger.exception("詳細なエラー情報:")
        return 1


if __name__ == '__main__':
    sys.exit(main())
