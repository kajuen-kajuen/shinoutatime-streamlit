"""
アーティスト名ソート修正CLIモジュール

コマンドラインからアーティスト名ソート修正マッピングを管理するための
インターフェースを提供します。
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from src.repositories.artist_sort_mapping_repository import ArtistSortMappingRepository
from src.config.logging_config import setup_logging


# 終了コード定義
EXIT_SUCCESS = 0
EXIT_ERROR = 1


class ArtistSortCLI:
    """アーティスト名ソート修正のCLIインターフェース
    
    コマンドラインから修正マッピングの追加、更新、削除、一覧表示を行う。
    """
    
    def __init__(self, repository: ArtistSortMappingRepository):
        """CLIを初期化
        
        Args:
            repository: 修正マッピングリポジトリ
        """
        self.repository = repository
        self.logger = logging.getLogger(__name__)
    
    def add_mapping(self, artist: str, sort_name: str) -> None:
        """修正マッピングを追加
        
        既存のマッピングがある場合は更新される。
        
        Args:
            artist: アーティスト名
            sort_name: 正しいソート名
        """
        try:
            # マッピングを保存
            self.repository.save_mapping(artist, sort_name)
            
            # 成功メッセージを表示
            print(f"✓ 修正マッピングを追加しました")
            print(f"  アーティスト名: {artist}")
            print(f"  ソート名: {sort_name}")
            
        except IOError as e:
            # エラーメッセージを表示
            print(f"エラー: 修正マッピングの保存に失敗しました")
            print(f"  詳細: {e}")
            self.logger.error(f"修正マッピングの保存に失敗: {e}", exc_info=True)
            sys.exit(EXIT_ERROR)
    
    def list_mappings(self) -> None:
        """すべての修正マッピングを表示"""
        try:
            # すべてのマッピングを取得
            mappings = self.repository.get_all_mappings()
            
            if not mappings:
                print("修正マッピングは登録されていません。")
                return
            
            # ヘッダーを表示
            print("=" * 60)
            print("修正マッピング一覧")
            print("=" * 60)
            print(f"登録件数: {len(mappings)}件\n")
            
            # マッピングを表示（アーティスト名でソート）
            for artist in sorted(mappings.keys()):
                sort_name = mappings[artist]
                print(f"  {artist}")
                print(f"    → {sort_name}")
                print()
            
            print("=" * 60)
            
        except Exception as e:
            # エラーメッセージを表示
            print(f"エラー: 修正マッピングの取得に失敗しました")
            print(f"  詳細: {e}")
            self.logger.error(f"修正マッピングの取得に失敗: {e}", exc_info=True)
            sys.exit(EXIT_ERROR)
    
    def delete_mapping(self, artist: str) -> None:
        """修正マッピングを削除
        
        Args:
            artist: アーティスト名
        """
        try:
            # マッピングを削除
            success = self.repository.delete_mapping(artist)
            
            if success:
                # 成功メッセージを表示
                print(f"✓ 修正マッピングを削除しました")
                print(f"  アーティスト名: {artist}")
            else:
                # マッピングが存在しない場合
                print(f"エラー: 指定されたアーティスト名の修正マッピングが見つかりません")
                print(f"  アーティスト名: {artist}")
                sys.exit(EXIT_ERROR)
            
        except IOError as e:
            # エラーメッセージを表示
            print(f"エラー: 修正マッピングの削除に失敗しました")
            print(f"  詳細: {e}")
            self.logger.error(f"修正マッピングの削除に失敗: {e}", exc_info=True)
            sys.exit(EXIT_ERROR)
    
    def update_mapping(self, artist: str, sort_name: str) -> None:
        """修正マッピングを更新
        
        Args:
            artist: アーティスト名
            sort_name: 新しいソート名
        """
        try:
            # 既存のマッピングを確認
            existing_sort_name = self.repository.get_mapping(artist)
            
            if existing_sort_name is None:
                # マッピングが存在しない場合は新規追加として扱う
                print(f"注意: 指定されたアーティスト名の修正マッピングが存在しないため、新規追加します")
            
            # マッピングを保存（内部的にはsave_mappingと同じ）
            self.repository.save_mapping(artist, sort_name)
            
            # 成功メッセージを表示
            if existing_sort_name:
                print(f"✓ 修正マッピングを更新しました")
                print(f"  アーティスト名: {artist}")
                print(f"  旧ソート名: {existing_sort_name}")
                print(f"  新ソート名: {sort_name}")
            else:
                print(f"✓ 修正マッピングを追加しました")
                print(f"  アーティスト名: {artist}")
                print(f"  ソート名: {sort_name}")
            
        except IOError as e:
            # エラーメッセージを表示
            print(f"エラー: 修正マッピングの更新に失敗しました")
            print(f"  詳細: {e}")
            self.logger.error(f"修正マッピングの更新に失敗: {e}", exc_info=True)
            sys.exit(EXIT_ERROR)
    
    def run(self) -> None:
        """CLIのメインループを実行
        
        このメソッドは対話型モードで使用される想定だが、
        現在の実装ではargparseによるサブコマンド方式を採用しているため、
        実際には使用されない。
        """
        # 将来の拡張用に残しておく
        pass


def create_parser() -> argparse.ArgumentParser:
    """コマンドライン引数パーサーを作成
    
    Returns:
        設定済みのArgumentParserオブジェクト
    """
    parser = argparse.ArgumentParser(
        prog='artist_sort_cli',
        description='アーティスト名ソート修正マッピング管理ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 修正マッピングを追加
  python -m src.cli.artist_sort_cli add "Vaundy" "Vaundy"
  
  # 修正マッピングを一覧表示
  python -m src.cli.artist_sort_cli list
  
  # 修正マッピングを更新
  python -m src.cli.artist_sort_cli update "米津玄師" "よねづけんし"
  
  # 修正マッピングを削除
  python -m src.cli.artist_sort_cli delete "Vaundy"
  
  # カスタムファイルパスを指定
  python -m src.cli.artist_sort_cli --file data/custom_mapping.tsv list
        """
    )
    
    # ファイルパスのオプション
    parser.add_argument(
        '--file',
        type=str,
        default='data/ARTIST_SORT_MAPPING.TSV',
        help='修正マッピングファイルのパス (デフォルト: data/ARTIST_SORT_MAPPING.TSV)'
    )
    
    # ログレベルのオプション
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細ログを表示'
    )
    
    # サブコマンドを作成
    subparsers = parser.add_subparsers(
        dest='command',
        help='実行するコマンド',
        required=True
    )
    
    # addサブコマンド
    add_parser = subparsers.add_parser(
        'add',
        help='修正マッピングを追加'
    )
    add_parser.add_argument(
        'artist',
        help='アーティスト名'
    )
    add_parser.add_argument(
        'sort_name',
        help='正しいソート名'
    )
    
    # listサブコマンド
    subparsers.add_parser(
        'list',
        help='すべての修正マッピングを表示'
    )
    
    # updateサブコマンド
    update_parser = subparsers.add_parser(
        'update',
        help='修正マッピングを更新'
    )
    update_parser.add_argument(
        'artist',
        help='アーティスト名'
    )
    update_parser.add_argument(
        'sort_name',
        help='新しいソート名'
    )
    
    # deleteサブコマンド
    delete_parser = subparsers.add_parser(
        'delete',
        help='修正マッピングを削除'
    )
    delete_parser.add_argument(
        'artist',
        help='アーティスト名'
    )
    
    return parser


def main() -> int:
    """CLIのメインエントリーポイント
    
    Returns:
        終了コード
    """
    # 引数パーサーを作成
    parser = create_parser()
    args = parser.parse_args()
    
    # ログ設定を初期化
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level=log_level, enable_file_logging=False)
    logger = logging.getLogger(__name__)
    
    logger.info("アーティスト名ソート修正CLIを開始します")
    
    try:
        # リポジトリを初期化
        repository = ArtistSortMappingRepository(args.file)
        
        # CLIを初期化
        cli = ArtistSortCLI(repository)
        
        # コマンドに応じて処理を実行
        if args.command == 'add':
            cli.add_mapping(args.artist, args.sort_name)
        
        elif args.command == 'list':
            cli.list_mappings()
        
        elif args.command == 'update':
            cli.update_mapping(args.artist, args.sort_name)
        
        elif args.command == 'delete':
            cli.delete_mapping(args.artist)
        
        logger.info("処理が正常に完了しました")
        return EXIT_SUCCESS
        
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
