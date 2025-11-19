"""
Twitter埋め込みコードCLIモジュール

コマンドラインからTwitter埋め込みコードを取得するためのインターフェースを提供します。
"""

import sys
import argparse
from typing import List, Optional
from pathlib import Path

from src.services.twitter_embed_service import TwitterEmbedService
from src.clients.twitter_api_client import TwitterAPIClient
from src.repositories.file_repository import FileRepository
from src.config.logging_config import setup_twitter_embed_logging
from src.exceptions.errors import (
    InvalidURLError,
    NetworkError,
    APITimeoutError,
    RateLimitError,
    FileWriteError
)


# 終了コード定義
EXIT_SUCCESS = 0
EXIT_INVALID_ARGS = 1
EXIT_INVALID_URL = 2
EXIT_NETWORK_ERROR = 3
EXIT_FILE_ERROR = 4
EXIT_UNKNOWN_ERROR = 99


def parse_arguments() -> argparse.Namespace:
    """
    コマンドライン引数を解析
    
    要件3.1に対応: コマンドライン引数としてツイートURLを受け取る
    
    Returns:
        解析された引数
    """
    parser = argparse.ArgumentParser(
        description="""
Twitter埋め込みコード自動取得ツール

TwitterのツイートURLから埋め込みコードを自動的に取得し、
data/tweet_embed_code.htmlファイルに保存します。

対応URL形式:
  - https://twitter.com/username/status/1234567890
  - https://x.com/username/status/1234567890
  - https://mobile.twitter.com/username/status/1234567890
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 単一のツイートを取得
  python -m src.cli.twitter_embed_cli https://twitter.com/user/status/1234567890
  
  # 複数のツイートを取得
  python -m src.cli.twitter_embed_cli \\
    https://twitter.com/user/status/123 \\
    https://twitter.com/user/status/456
  
  # バックアップを作成せずに保存
  python -m src.cli.twitter_embed_cli --no-backup \\
    https://twitter.com/user/status/1234567890
  
  # 詳細ログを表示
  python -m src.cli.twitter_embed_cli -v \\
    https://twitter.com/user/status/1234567890
  
  # カスタム出力パスを指定
  python -m src.cli.twitter_embed_cli \\
    -o custom/path/embed.html \\
    https://twitter.com/user/status/1234567890
  
  # リトライ設定をカスタマイズ
  python -m src.cli.twitter_embed_cli \\
    --max-retries 5 \\
    --retry-delay 2.0 \\
    https://twitter.com/user/status/1234567890

終了コード:
  0  - 成功
  1  - 無効な引数
  2  - 無効なURL
  3  - ネットワークエラー
  4  - ファイル書き込みエラー
  99 - 予期しないエラー

詳細なドキュメント:
  docs/twitter-embed-automation.md を参照してください
        """
    )
    
    parser.add_argument(
        "urls",
        nargs="+",
        metavar="URL",
        help="ツイートURL（複数指定可能）。twitter.com、x.com、mobile.twitter.comに対応"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        default="data/tweet_embed_code.html",
        metavar="PATH",
        help="埋め込みコードの出力ファイルパス（デフォルト: data/tweet_embed_code.html）"
    )
    
    parser.add_argument(
        "--height-output",
        default="data/tweet_height.txt",
        metavar="PATH",
        help="表示高さの出力ファイルパス（デフォルト: data/tweet_height.txt）"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="既存ファイルのバックアップを作成しない（デフォルトでは自動的にバックアップを作成）"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="詳細ログを表示（デバッグ情報を含む）"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        metavar="N",
        help="ネットワークエラー時の最大リトライ回数（デフォルト: 3）"
    )
    
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="リトライ間隔（秒）。指数バックオフが適用されます（デフォルト: 1.0）"
    )
    
    return parser.parse_args()


def print_progress(message: str, current: int, total: int) -> None:
    """
    進行状況を表示
    
    要件3.3に対応: 処理の進行状況をコンソールに出力
    
    Args:
        message: 表示するメッセージ
        current: 現在の処理数
        total: 全体の処理数
    """
    percentage = (current / total) * 100 if total > 0 else 0
    print(f"[{current}/{total}] ({percentage:.1f}%) {message}")


def print_summary(success_count: int, failure_count: int, failed_urls: List[str]) -> None:
    """
    処理結果のサマリーを表示
    
    Args:
        success_count: 成功数
        failure_count: 失敗数
        failed_urls: 失敗したURLのリスト
    """
    print("\n" + "=" * 60)
    print("処理結果サマリー")
    print("=" * 60)
    print(f"成功: {success_count}件")
    print(f"失敗: {failure_count}件")
    
    if failed_urls:
        print("\n失敗したURL:")
        for url in failed_urls:
            print(f"  - {url}")
    
    print("=" * 60)


def main() -> int:
    """
    CLIのメインエントリーポイント
    
    要件3.1, 3.2, 3.3, 3.4, 3.5に対応:
    - コマンドライン引数の解析
    - 引数不足時のエラー処理
    - 進行状況の表示
    - 成功時の終了コード0
    - 失敗時の非ゼロ終了コード
    
    Returns:
        終了コード
    """
    try:
        # コマンドライン引数を解析
        args = parse_arguments()
        
    except SystemExit as e:
        # 引数解析エラー（argparseが自動的に使用方法を表示）
        # 要件3.2に対応: 引数不足時のエラー処理
        return EXIT_INVALID_ARGS
    
    # ロガーを設定
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_twitter_embed_logging(log_level=log_level)
    
    logger.info("Twitter埋め込みコードCLIを開始します")
    logger.info(f"取得対象URL数: {len(args.urls)}")
    
    try:
        # サービスを初期化
        api_client = TwitterAPIClient(
            max_retries=args.max_retries,
            retry_delay=args.retry_delay
        )
        file_repo = FileRepository(
            embed_code_path=args.output,
            height_path=args.height_output
        )
        service = TwitterEmbedService(
            api_client=api_client,
            file_repo=file_repo,
            logger=logger
        )
        
        # 単一URLの場合
        if len(args.urls) == 1:
            url = args.urls[0]
            print(f"埋め込みコードを取得中: {url}")
            
            result = service.fetch_embed_code(url)
            
            if not result.success:
                print(f"エラー: {result.error_message}")
                logger.error(f"埋め込みコード取得失敗: {url}")
                
                # エラーの種類に応じて終了コードを返す
                if "URL" in result.error_message or "形式" in result.error_message:
                    return EXIT_INVALID_URL
                else:
                    return EXIT_NETWORK_ERROR
            
            print(f"✓ 埋め込みコード取得成功")
            
            # ファイルに保存
            print(f"ファイルに保存中: {args.output}")
            create_backup = not args.no_backup
            
            if not service.save_embed_code(result.embed_code, create_backup):
                print("エラー: ファイルの保存に失敗しました")
                logger.error("ファイル保存失敗")
                return EXIT_FILE_ERROR
            
            # 高さを保存
            if result.height:
                file_repo.write_height(result.height)
                print(f"✓ 表示高さを保存しました: {result.height}px")
            
            print(f"✓ ファイル保存成功: {args.output}")
            
            # 要件3.4に対応: 成功時の終了コード0
            logger.info("処理が正常に完了しました")
            return EXIT_SUCCESS
        
        # 複数URLの場合
        else:
            print(f"{len(args.urls)}件のツイートを取得します\n")
            
            # 進行状況を表示しながら取得
            # 要件3.3に対応: 進行状況の表示
            results = []
            for i, url in enumerate(args.urls, 1):
                print_progress(f"取得中: {url}", i, len(args.urls))
                result = service.fetch_embed_code(url)
                results.append(result)
            
            # 結果を集計
            success_count = sum(1 for r in results if r.success)
            failure_count = sum(1 for r in results if not r.success)
            failed_urls = [r.tweet_url for r in results if not r.success]
            
            # 成功したコードを連結
            embed_codes = [r.embed_code for r in results if r.success and r.embed_code]
            combined_code = "\n\n".join(embed_codes)
            
            # 最大高さを取得
            heights = [r.height for r in results if r.success and r.height]
            max_height = max(heights) if heights else 850
            
            # サマリーを表示
            print_summary(success_count, failure_count, failed_urls)
            
            # 成功したコードがある場合は保存
            if combined_code:
                print(f"\nファイルに保存中: {args.output}")
                create_backup = not args.no_backup
                
                if not service.save_embed_code(combined_code, create_backup):
                    print("エラー: ファイルの保存に失敗しました")
                    logger.error("ファイル保存失敗")
                    return EXIT_FILE_ERROR
                
                # 高さを保存
                file_repo.write_height(max_height)
                print(f"✓ 表示高さを保存しました: {max_height}px")
                
                print(f"✓ ファイル保存成功: {args.output}")
            
            # 全て失敗した場合
            if failure_count == len(args.urls):
                print("\nエラー: 全てのツイートの取得に失敗しました")
                logger.error("全てのツイート取得失敗")
                # 要件3.5に対応: 失敗時の非ゼロ終了コード
                return EXIT_NETWORK_ERROR
            
            # 一部失敗した場合
            elif failure_count > 0:
                print(f"\n警告: {failure_count}件のツイート取得に失敗しました")
                logger.warning(f"{failure_count}件のツイート取得失敗")
                # 要件3.4に対応: 部分的成功でも終了コード0
                return EXIT_SUCCESS
            
            # 全て成功した場合
            else:
                print("\n✓ 全てのツイートの取得に成功しました")
                logger.info("全てのツイート取得成功")
                # 要件3.4に対応: 成功時の終了コード0
                return EXIT_SUCCESS
    
    except InvalidURLError as e:
        print(f"エラー: {e}")
        logger.error(f"URL検証エラー: {e}")
        # 要件3.5に対応: 失敗時の非ゼロ終了コード
        return EXIT_INVALID_URL
    
    except (NetworkError, APITimeoutError) as e:
        print(f"エラー: {e}")
        logger.error(f"ネットワークエラー: {e}")
        # 要件3.5に対応: 失敗時の非ゼロ終了コード
        return EXIT_NETWORK_ERROR
    
    except RateLimitError as e:
        print(f"エラー: {e}")
        if e.reset_time:
            print(f"レート制限解除時刻: {e.reset_time}")
        logger.error(f"レート制限エラー: {e}")
        # 要件3.5に対応: 失敗時の非ゼロ終了コード
        return EXIT_NETWORK_ERROR
    
    except FileWriteError as e:
        print(f"エラー: {e}")
        logger.error(f"ファイル書き込みエラー: {e}")
        # 要件3.5に対応: 失敗時の非ゼロ終了コード
        return EXIT_FILE_ERROR
    
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        # 要件3.5に対応: 失敗時の非ゼロ終了コード
        return EXIT_UNKNOWN_ERROR


if __name__ == "__main__":
    sys.exit(main())
