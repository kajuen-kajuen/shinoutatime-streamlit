"""アーティスト名ソート修正マッピングのリポジトリモジュール

修正マッピングファイルの読み書きを管理する
"""

import logging
from pathlib import Path
from typing import Dict, Optional

from src.models.artist_sort_models import ArtistSortMapping


class ArtistSortMappingRepository:
    """アーティスト名ソート修正マッピングのリポジトリ
    
    TSV形式のファイルからアーティスト名とソート名のマッピングを
    読み込み、保存、削除する機能を提供する。
    """
    
    def __init__(self, file_path: str):
        """リポジトリを初期化
        
        Args:
            file_path: 修正マッピングファイルのパス
        """
        self.file_path = Path(file_path)
        self.logger = logging.getLogger(__name__)
    
    def load_mappings(self) -> Dict[str, str]:
        """修正マッピングをファイルから読み込む
        
        Returns:
            アーティスト名をキー、ソート名を値とする辞書
            
        Raises:
            ValueError: ファイル形式が不正な場合
        """
        # ファイルが存在しない場合は空の辞書を返す
        if not self.file_path.exists():
            self.logger.info(
                f"修正マッピングファイルが見つかりません。空のマッピングとして処理します。"
            )
            return {}
        
        try:
            mappings = {}
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 空ファイルの場合
            if not lines:
                self.logger.info("修正マッピングファイルが空です。")
                return {}
            
            # ヘッダー行をスキップ
            header_found = False
            for i, line in enumerate(lines):
                line = line.strip()
                
                # 空行をスキップ
                if not line:
                    continue
                
                # ヘッダー行を検出
                if not header_found:
                    if line.startswith('アーティスト名'):
                        header_found = True
                        continue
                    else:
                        # ヘッダーがない場合はエラー
                        raise ValueError(
                            f"修正マッピングファイルの形式が不正です: "
                            f"ヘッダー行が見つかりません"
                        )
                
                # データ行を処理
                parts = line.split('\t')
                if len(parts) != 2:
                    raise ValueError(
                        f"修正マッピングファイルの形式が不正です: "
                        f"行{i+1}のカラム数が不正です（期待: 2, 実際: {len(parts)}）"
                    )
                
                # フィールドの先頭・末尾の空白をトリム
                artist = parts[0].strip()
                sort_name = parts[1].strip()
                
                # 重複したアーティスト名がある場合、最後のエントリを有効とする
                mappings[artist] = sort_name
            
            self.logger.info(
                f"修正マッピングを読み込みました: {len(mappings)}件"
            )
            return mappings
            
        except UnicodeDecodeError as e:
            error_msg = (
                "修正マッピングファイルのエンコーディングが不正です。"
                "UTF-8で保存してください。"
            )
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e
        
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            error_msg = f"修正マッピングファイルの読み込みに失敗しました: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

    def save_mapping(self, artist: str, sort_name: str) -> None:
        """修正マッピングを保存
        
        既存のマッピングがある場合は更新、ない場合は追加。
        
        Args:
            artist: アーティスト名
            sort_name: 正しいソート名
            
        Raises:
            IOError: ファイルへの書き込みに失敗した場合
        """
        try:
            # 入力値の先頭・末尾の空白をトリム
            artist = artist.strip()
            sort_name = sort_name.strip()
            
            # 既存のマッピングを読み込む
            try:
                mappings = self.load_mappings()
            except ValueError:
                # ファイル形式エラーの場合は空のマッピングから開始
                self.logger.warning(
                    "既存のマッピングファイルの形式が不正なため、新規作成します。"
                )
                mappings = {}
            
            # マッピングを追加または更新
            mappings[artist] = sort_name
            
            # ファイルに書き込む
            self._write_mappings(mappings)
            
            self.logger.info(
                f"修正マッピングを保存しました: {artist} -> {sort_name}"
            )
            
        except PermissionError as e:
            error_msg = "ファイルへの書き込み権限がありません"
            self.logger.error(
                f"{error_msg}: {self.file_path}",
                exc_info=True
            )
            raise IOError(error_msg) from e
        
        except OSError as e:
            error_msg = f"ファイルへの書き込みに失敗しました: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise IOError(error_msg) from e
    
    def delete_mapping(self, artist: str) -> bool:
        """修正マッピングを削除
        
        Args:
            artist: アーティスト名
            
        Returns:
            削除に成功した場合True、該当するマッピングがない場合False
            
        Raises:
            IOError: ファイルへの書き込みに失敗した場合
        """
        try:
            # 入力値の先頭・末尾の空白をトリム
            artist = artist.strip()
            
            # 既存のマッピングを読み込む
            try:
                mappings = self.load_mappings()
            except ValueError:
                # ファイル形式エラーの場合は削除対象なし
                self.logger.warning(
                    "マッピングファイルの形式が不正なため、削除できません。"
                )
                return False
            
            # マッピングが存在しない場合
            if artist not in mappings:
                self.logger.warning(
                    f"削除対象のマッピングが見つかりません: {artist}"
                )
                return False
            
            # マッピングを削除
            del mappings[artist]
            
            # ファイルに書き込む
            self._write_mappings(mappings)
            
            self.logger.info(
                f"修正マッピングを削除しました: {artist}"
            )
            return True
            
        except PermissionError as e:
            error_msg = "ファイルへの書き込み権限がありません"
            self.logger.error(
                f"{error_msg}: {self.file_path}",
                exc_info=True
            )
            raise IOError(error_msg) from e
        
        except OSError as e:
            error_msg = f"ファイルへの書き込みに失敗しました: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise IOError(error_msg) from e
    
    def get_all_mappings(self) -> Dict[str, str]:
        """すべての修正マッピングを取得
        
        Returns:
            アーティスト名をキー、ソート名を値とする辞書
        """
        try:
            return self.load_mappings()
        except ValueError:
            # ファイル形式エラーの場合は空の辞書を返す
            self.logger.warning(
                "マッピングファイルの形式が不正なため、空のマッピングを返します。"
            )
            return {}
    
    def get_mapping(self, artist: str) -> Optional[str]:
        """特定のアーティスト名の修正マッピングを取得
        
        Args:
            artist: アーティスト名
            
        Returns:
            ソート名（マッピングが存在しない場合はNone）
        """
        # 入力値の先頭・末尾の空白をトリム
        artist = artist.strip()
        
        mappings = self.get_all_mappings()
        return mappings.get(artist)
    
    def _write_mappings(self, mappings: Dict[str, str]) -> None:
        """マッピングをファイルに書き込む（内部メソッド）
        
        Args:
            mappings: アーティスト名をキー、ソート名を値とする辞書
            
        Raises:
            IOError: ファイルへの書き込みに失敗した場合
        """
        # 親ディレクトリが存在しない場合は作成
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ファイルに書き込み
        with open(self.file_path, 'w', encoding='utf-8') as f:
            # ヘッダー行を書き込む
            f.write('アーティスト名\tソート名\n')
            
            # データ行を書き込む
            for artist, sort_name in mappings.items():
                f.write(f'{artist}\t{sort_name}\n')
