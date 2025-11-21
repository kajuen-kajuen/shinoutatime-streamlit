"""
配信情報リポジトリモジュール

M_YT_LIVE.TSVファイルの読み込みを管理します。
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import chardet

from src.models.song_list_models import LiveInfo
from src.exceptions.errors import DataLoadError


class LiveRepository:
    """
    配信情報リポジトリ
    
    M_YT_LIVE.TSVファイルから配信情報を読み込みます。
    """
    
    def __init__(self, file_path: str):
        """
        リポジトリを初期化
        
        Args:
            file_path: M_YT_LIVE.TSVファイルのパス
        """
        self.file_path = Path(file_path)
        self.logger = logging.getLogger(__name__)
        self._cache: Optional[List[LiveInfo]] = None
    
    def load_all(self) -> List[LiveInfo]:
        """
        すべての配信情報を読み込む
        
        Returns:
            配信情報のリスト
            
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
            live_infos = []
            with open(self.file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                # ヘッダーの検証
                expected_headers = ['ID', '配信日', 'タイトル', 'URL']
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
                        live_info = self._parse_row(row, line_num)
                        live_infos.append(live_info)
                    except Exception as e:
                        error_msg = f"行 {line_num} の解析に失敗しました: {e}"
                        self.logger.error(error_msg)
                        raise DataLoadError(
                            file_path=str(self.file_path),
                            message=error_msg
                        )
            
            self.logger.info(
                f"配信情報を読み込みました: {len(live_infos)}件 ({self.file_path})"
            )
            self._cache = live_infos
            return live_infos
            
        except DataLoadError:
            raise
        except Exception as e:
            error_msg = f"ファイルの読み込みに失敗しました: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise DataLoadError(
                file_path=str(self.file_path),
                message=error_msg
            )
    
    def get_by_id(self, live_id: int) -> Optional[LiveInfo]:
        """
        IDで配信情報を取得
        
        Args:
            live_id: 配信ID
            
        Returns:
            配信情報（見つからない場合はNone）
        """
        # キャッシュがない場合は読み込む
        if self._cache is None:
            self.load_all()
        
        # IDで検索
        for live_info in self._cache:
            if live_info.id == live_id:
                return live_info
        
        return None
    
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
    
    def _parse_row(self, row: dict, line_num: int) -> LiveInfo:
        """
        TSVの1行をLiveInfoオブジェクトに変換
        
        Args:
            row: TSVの行データ（辞書形式）
            line_num: 行番号（エラーメッセージ用）
            
        Returns:
            LiveInfoオブジェクト
            
        Raises:
            ValueError: データの解析に失敗した場合
        """
        try:
            # IDを整数に変換
            live_id = int(row['ID'])
            
            # 配信日をパース（YYYY/M/D形式）
            date_str = row['配信日'].strip()
            date = self._parse_date(date_str)
            
            # タイトルとURLを取得
            title = row['タイトル'].strip()
            url = row['URL'].strip()
            
            return LiveInfo(
                id=live_id,
                date=date,
                title=title,
                url=url
            )
            
        except KeyError as e:
            raise ValueError(f"必須フィールドが見つかりません: {e}")
        except ValueError as e:
            raise ValueError(f"データ形式が不正です: {e}")
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        配信日文字列をdatetimeオブジェクトに変換
        
        Args:
            date_str: 配信日文字列（YYYY/M/D形式）
            
        Returns:
            datetimeオブジェクト
            
        Raises:
            ValueError: 日付の解析に失敗した場合
        """
        try:
            # YYYY/M/D形式をパース
            parts = date_str.split('/')
            if len(parts) != 3:
                raise ValueError(f"日付形式が不正です: {date_str}")
            
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            
            return datetime(year, month, day)
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"日付の解析に失敗しました: {date_str} ({e})")
