"""
バックアップリポジトリモジュール

ファイルのバックアップを管理します。
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.exceptions.errors import DataSaveError


class BackupRepository:
    """
    バックアップリポジトリ
    
    ファイルのバックアップを作成・管理します。
    """
    
    def __init__(self, backup_dir: str = "data/backups"):
        """
        リポジトリを初期化
        
        Args:
            backup_dir: バックアップディレクトリのパス（デフォルト: data/backups）
        """
        self.backup_dir = Path(backup_dir)
        self.logger = logging.getLogger(__name__)
        
        # バックアップディレクトリを自動作成（要件7.3）
        self._ensure_backup_dir()
    
    def create_backup(self, file_path: str) -> str:
        """
        ファイルのバックアップを作成
        
        Args:
            file_path: バックアップ対象のファイルパス
            
        Returns:
            作成されたバックアップファイルのパス
            
        Raises:
            DataSaveError: バックアップの作成に失敗した場合
        """
        source_path = Path(file_path)
        
        # ファイルが存在しない場合はエラー
        if not source_path.exists():
            error_msg = f"バックアップ対象のファイルが存在しません: {file_path}"
            self.logger.error(error_msg)
            raise DataSaveError(
                file_path=file_path,
                message=error_msg
            )
        
        try:
            # バックアップファイルのパスを生成（要件7.2）
            backup_path = self.get_backup_path(file_path)
            
            # ファイルをコピー
            shutil.copy2(source_path, backup_path)
            
            self.logger.info(f"バックアップを作成しました: {backup_path}")
            return str(backup_path)
            
        except PermissionError as e:
            error_msg = f"バックアップの作成に失敗しました（権限エラー）: {file_path}"
            self.logger.error(error_msg, exc_info=True)
            raise DataSaveError(
                file_path=file_path,
                message=error_msg
            ) from e
            
        except Exception as e:
            error_msg = f"バックアップの作成に失敗しました: {file_path} ({e})"
            self.logger.error(error_msg, exc_info=True)
            raise DataSaveError(
                file_path=file_path,
                message=error_msg
            ) from e
    
    def get_backup_path(self, file_path: str) -> Path:
        """
        バックアップファイルのパスを生成
        
        タイムスタンプ（YYYYMMDD_HHMMSS）を付加したファイル名を生成します。
        
        Args:
            file_path: 元のファイルパス
            
        Returns:
            バックアップファイルのパス
        """
        source_path = Path(file_path)
        
        # タイムスタンプを生成（要件7.2）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # ファイル名を生成: 元のファイル名_YYYYMMDD_HHMMSS.拡張子
        file_stem = source_path.stem  # 拡張子を除いたファイル名
        file_suffix = source_path.suffix  # 拡張子
        backup_filename = f"{file_stem}_{timestamp}{file_suffix}"
        
        # バックアップディレクトリ内のパスを返す
        backup_path = self.backup_dir / backup_filename
        
        self.logger.debug(f"バックアップパスを生成しました: {backup_path}")
        return backup_path
    
    def _ensure_backup_dir(self) -> None:
        """
        バックアップディレクトリが存在することを確認し、必要に応じて作成
        
        Raises:
            DataSaveError: ディレクトリの作成に失敗した場合
        """
        try:
            # ディレクトリが存在しない場合は作成（要件7.3）
            if not self.backup_dir.exists():
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(
                    f"バックアップディレクトリを作成しました: {self.backup_dir}"
                )
            else:
                self.logger.debug(
                    f"バックアップディレクトリは既に存在します: {self.backup_dir}"
                )
                
        except PermissionError as e:
            error_msg = f"バックアップディレクトリの作成に失敗しました（権限エラー）: {self.backup_dir}"
            self.logger.error(error_msg, exc_info=True)
            raise DataSaveError(
                file_path=str(self.backup_dir),
                message=error_msg
            ) from e
            
        except Exception as e:
            error_msg = f"バックアップディレクトリの作成に失敗しました: {self.backup_dir} ({e})"
            self.logger.error(error_msg, exc_info=True)
            raise DataSaveError(
                file_path=str(self.backup_dir),
                message=error_msg
            ) from e
