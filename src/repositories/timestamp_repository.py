"""
タイムスタンプ情報リポジトリモジュール

M_YT_LIVE_TIMESTAMP.TSVファイルの読み込みを管理します。
"""

import csv
import logging
from pathlib import Path
from typing import List, Optional
import chardet

from src.models.song_list_models import TimestampInfo
from src.exceptions.errors import DataLoadError


class TimestampRepository:
    """
    タイムスタンプ情報リポジトリ
    
    M_YT_LIVE_TIMESTAMP.TSVファイルからタイムスタンプ情報を読み込みます。
    """
    
    def __init__(self, file_path: str):
        """
        リポジトリを初期化
        
        Args:
            file_path: M_YT_LIVE_TIMESTAMP.TSVファイルのパス
        """
        self.file_path = Path(file_path)
        self.logger = logging.getLogger(__name__)
        self._cache: Optional[List[TimestampInfo]] = None
    
    def load_all(self) -> List[TimestampInfo]:
        """
        すべてのタイムスタンプ情報を読み込む
        
        Returns:
            タイムスタンプ情報のリスト
            
        Raises:
            DataLoadError: ファイルの読み込みに失敗した場合
        """
        # ファイルの存在確認
        if not self.file_path.exists():
            error_msg = f"ファイルが存在しません: {self.file_path}"
            self.logger.error(error_msg)
            raise DataLoadError(
                file_path=str(self.file_path),
                message=error_msg
            )
        
        try:
            # エンコーディングを検出
            encoding = self._detect_encoding()
            self.logger.debug(f"検出されたエンコーディング: {encoding}")
            
            # TSVファイルを読み込む
            timestamp_infos = []
            with open(self.file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                # ヘッダーの検証
                expected_headers = ['ID', 'LIVE_ID', 'タイムスタンプ', '曲名', 'アーティスト']
                if reader.fieldnames != expected_headers:
                    error_msg = (
                        f"ファイル形式が不正です。"
                        f"期待されるヘッダー: {expected_headers}, "
                        f"実際のヘッダー: {reader.fieldnames}"
                    )
                    self.logger.error(error_msg)
                    raise DataLoadError(
                        file_path=str(self.file_path),
                        message=error_msg
                    )
                
                # データ行を読み込む
                for line_num, row in enumerate(reader, start=2):  # ヘッダーが1行目なので2から開始
                    try:
                        timestamp_info = self._parse_row(row, line_num)
                        timestamp_infos.append(timestamp_info)
                    except Exception as e:
                        error_msg = f"行 {line_num} の解析に失敗しました: {e}"
                        self.logger.error(error_msg)
                        raise DataLoadError(
                            file_path=str(self.file_path),
                            message=error_msg
                        )
            
            self.logger.info(
                f"タイムスタンプ情報を読み込みました: {len(timestamp_infos)}件 ({self.file_path})"
            )
            self._cache = timestamp_infos
            return timestamp_infos
            
        except DataLoadError:
            raise
        except Exception as e:
            error_msg = f"ファイルの読み込みに失敗しました: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise DataLoadError(
                file_path=str(self.file_path),
                message=error_msg
            )
    
    def get_by_live_id(self, live_id: int) -> List[TimestampInfo]:
        """
        配信IDでタイムスタンプ情報を取得
        
        Args:
            live_id: 配信ID
            
        Returns:
            タイムスタンプ情報のリスト
        """
        # キャッシュがない場合は読み込む
        if self._cache is None:
            self.load_all()
        
        # 配信IDで検索
        return [ts for ts in self._cache if ts.live_id == live_id]
    
    def _detect_encoding(self) -> str:
        """
        ファイルのエンコーディングを検出
        
        Returns:
            検出されたエンコーディング名
        """
        try:
            with open(self.file_path, 'rb') as f:
                raw_data = f.read()
            
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            
            # UTF-8の場合はそのまま返す
            if encoding and encoding.lower().startswith('utf'):
                return 'utf-8'
            
            # その他のエンコーディングの場合
            return encoding if encoding else 'utf-8'
            
        except Exception as e:
            self.logger.warning(
                f"エンコーディングの検出に失敗しました。UTF-8を使用します: {e}"
            )
            return 'utf-8'
    
    def _parse_row(self, row: dict, line_num: int) -> TimestampInfo:
        """
        TSVの1行をTimestampInfoオブジェクトに変換
        
        Args:
            row: TSVの行データ（辞書形式）
            line_num: 行番号（エラーメッセージ用）
            
        Returns:
            TimestampInfoオブジェクト
            
        Raises:
            ValueError: データの解析に失敗した場合
        """
        try:
            # IDとLIVE_IDを整数に変換
            timestamp_id = int(row['ID'])
            live_id = int(row['LIVE_ID'])
            
            # タイムスタンプ、曲名、アーティストを取得
            timestamp = row['タイムスタンプ'].strip()
            song_name = row['曲名'].strip()
            artist = row['アーティスト'].strip()
            
            return TimestampInfo(
                id=timestamp_id,
                live_id=live_id,
                timestamp=timestamp,
                song_name=song_name,
                artist=artist
            )
            
        except KeyError as e:
            raise ValueError(f"必須フィールドが見つかりません: {e}")
        except ValueError as e:
            raise ValueError(f"データ形式が不正です: {e}")
