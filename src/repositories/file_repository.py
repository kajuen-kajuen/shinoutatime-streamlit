"""
ファイルリポジトリモジュール

埋め込みコードファイルの読み書きとバックアップを管理する
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging
import chardet # chardetをインポート

from src.exceptions.errors import FileWriteError


class FileRepository:
    """
    ファイルリポジトリ
    
    埋め込みコードファイルの読み書きとバックアップを管理
    """
    
    def __init__(
        self,
        embed_code_path: str,
        height_path: str,
        backup_dir: str = "data/backups"
    ):
        """
        リポジトリを初期化
        
        Args:
            embed_code_path: 埋め込みコードファイルのパス
            height_path: 高さ設定ファイルのパス
            backup_dir: バックアップディレクトリ
        """
        self.embed_code_path = Path(embed_code_path)
        self.height_path = Path(height_path)
        self.backup_dir = Path(backup_dir)
        self.logger = logging.getLogger(__name__)
        
        # バックアップディレクトリが存在しない場合は作成
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def read_embed_code(self) -> Optional[str]:
        """
        埋め込みコードを読み込む
        
        Returns:
            埋め込みコード（ファイルが存在しない場合はNone）
        """
        try:
            if not self.embed_code_path.exists():
                self.logger.warning(
                    f"埋め込みコードファイルが存在しません: {self.embed_code_path}"
                )
                return None
            
            # ファイルをバイナリモードで読み込み
            with open(self.embed_code_path, 'rb') as f_raw:
                raw_data = f_raw.read()
            
            # まずUTF-8での読み込みを試みる
            try:
                content = raw_data.decode('utf-8')
                self.logger.debug(
                    f"埋め込みコードを読み込みました: {self.embed_code_path} (エンコーディング: utf-8)"
                )
                return content
            except UnicodeDecodeError:
                self.logger.warning(
                    f"UTF-8での読み込みに失敗しました。エンコーディングの自動検出を試みます: {self.embed_code_path}"
                )

            # UTF-8で失敗した場合、エンコーディングを検出
            detected_encoding = chardet.detect(raw_data)['encoding']
            
            if detected_encoding:
                # 検出されたエンコーディングでファイルを読み込む
                try:
                    content = raw_data.decode(detected_encoding)
                    self.logger.info(
                        f"自動検出されたエンコーディングで読み込みました: {self.embed_code_path} (エンコーディング: {detected_encoding})"
                    )
                    return content
                except UnicodeDecodeError:
                    self.logger.warning(
                        f"検出されたエンコーディング ({detected_encoding}) での読み込みに失敗しました"
                    )
            
            # 最終手段: UTF-8でエラーを置換して読み込む
            self.logger.warning(
                f"エンコーディングの解決に失敗しました。UTF-8 (errors='replace') で読み込みます: {self.embed_code_path}"
            )
            content = raw_data.decode('utf-8', errors='replace')
            return content
            
        except Exception as e:
            self.logger.error(
                f"埋め込みコードの読み込みに失敗しました: {e}",
                exc_info=True
            )
            return None
    
    def write_embed_code(
        self,
        content: str
    ) -> bool:
        """
        埋め込みコードを書き込む
        
        Args:
            content: 書き込む内容
            
        Returns:
            書き込み成功の可否
            
        Raises:
            FileWriteError: ファイル書き込みに失敗した場合
        """
        try:
            # 親ディレクトリが存在しない場合は作成
            self.embed_code_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ファイルに書き込み
            with open(self.embed_code_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(
                f"埋め込みコードを保存しました: {self.embed_code_path}"
            )
            return True
            
        except PermissionError as e:
            error_msg = "ファイルへの書き込み権限がありません"
            self.logger.error(f"{error_msg}: {self.embed_code_path}", exc_info=True)
            raise FileWriteError(
                file_path=str(self.embed_code_path),
                message=error_msg,
                original_error=e
            ) from e
            
        except OSError as e:
            error_msg = "ファイルの書き込みに失敗しました"
            self.logger.error(f"{error_msg}: {e}", exc_info=True)
            raise FileWriteError(
                file_path=str(self.embed_code_path),
                message=error_msg,
                original_error=e
            ) from e
            
        except Exception as e:
            error_msg = "予期しないエラーが発生しました"
            self.logger.error(f"{error_msg}: {e}", exc_info=True)
            raise FileWriteError(
                file_path=str(self.embed_code_path),
                message=error_msg,
                original_error=e
            ) from e
    
    def create_backup(self) -> Optional[str]:
        """
        現在のファイルのバックアップを作成
        
        Returns:
            バックアップファイルのパス（失敗時はNone）
        """
        try:
            # ファイルが存在しない場合はバックアップ不要
            if not self.embed_code_path.exists():
                self.logger.info(
                    "埋め込みコードファイルが存在しないため、バックアップをスキップします"
                )
                return None
            
            # バックアップファイル名を生成（タイムスタンプ付き）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{self.embed_code_path.stem}_{timestamp}{self.embed_code_path.suffix}"
            backup_path = self.backup_dir / backup_filename
            
            # ファイルをコピー
            shutil.copy2(self.embed_code_path, backup_path)
            
            self.logger.info(
                f"バックアップを作成しました: {backup_path}"
            )
            return str(backup_path)
            
        except Exception as e:
            self.logger.warning(
                f"バックアップの作成に失敗しました: {e}",
                exc_info=True
            )
            return None
    
    def write_height(
        self,
        height: int
    ) -> bool:
        """
        表示高さを書き込む
        
        Args:
            height: 高さ（ピクセル）
            
        Returns:
            書き込み成功の可否
            
        Raises:
            FileWriteError: ファイル書き込みに失敗した場合
        """
        try:
            # 親ディレクトリが存在しない場合は作成
            self.height_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ファイルに書き込み
            with open(self.height_path, 'w', encoding='utf-8') as f:
                f.write(str(height))
            
            self.logger.info(
                f"表示高さを保存しました: {height}px -> {self.height_path}"
            )
            return True
            
        except PermissionError as e:
            error_msg = "ファイルへの書き込み権限がありません"
            self.logger.error(f"{error_msg}: {self.height_path}", exc_info=True)
            raise FileWriteError(
                file_path=str(self.height_path),
                message=error_msg,
                original_error=e
            ) from e
            
        except OSError as e:
            error_msg = "ファイルの書き込みに失敗しました"
            self.logger.error(f"{error_msg}: {e}", exc_info=True)
            raise FileWriteError(
                file_path=str(self.height_path),
                message=error_msg,
                original_error=e
            ) from e
            
        except Exception as e:
            error_msg = "予期しないエラーが発生しました"
            self.logger.error(f"{error_msg}: {e}", exc_info=True)
            raise FileWriteError(
                file_path=str(self.height_path),
                message=error_msg,
                original_error=e
            ) from e
    
    def read_height(
        self,
        default: int = 850
    ) -> int:
        """
        表示高さを読み込む
        
        Args:
            default: デフォルト値
            
        Returns:
            高さ（ピクセル）
        """
        try:
            if not self.height_path.exists():
                self.logger.info(
                    f"高さファイルが存在しないため、デフォルト値を使用します: {default}px"
                )
                return default
            
            with open(self.height_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 整数に変換
            height = int(content)
            
            self.logger.debug(
                f"表示高さを読み込みました: {height}px"
            )
            return height
            
        except ValueError as e:
            self.logger.warning(
                f"高さファイルの内容が不正です。デフォルト値を使用します: {e}"
            )
            return default
            
        except Exception as e:
            self.logger.warning(
                f"高さファイルの読み込みに失敗しました。デフォルト値を使用します: {e}"
            )
            return default
