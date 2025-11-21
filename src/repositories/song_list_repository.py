"""
曲リストリポジトリモジュール

V_SONG_LIST.TSVファイルの読み書きを管理します。
"""

import csv
import logging
from pathlib import Path
from typing import List, Optional
import chardet

from src.models.song_list_models import SongInfo
from src.exceptions.errors import DataLoadError, FileWriteError


class SongListRepository:
    """
    曲リストリポジトリ
    
    V_SONG_LIST.TSVファイルの読み込みと書き込みを管理します。
    """
    
    def __init__(self, file_path: str):
        """
        リポジトリを初期化
        
        Args:
            file_path: V_SONG_LIST.TSVファイルのパス
        """
        self.file_path = Path(file_path)
        self.logger = logging.getLogger(__name__)
    
    def load_all(self) -> List[SongInfo]:
        """
        既存の曲リストを読み込む
        
        Returns:
            曲情報のリスト（ファイルが存在しない場合は空リスト）
            
        Raises:
            DataLoadError: ファイルの読み込みに失敗した場合
        """
        # ファイルが存在しない場合は空リストを返す
        if not self.file_path.exists():
            self.logger.info(
                f"ファイルが存在しないため、空リストを返します: {self.file_path}"
            )
            return []
        
        try:
            # エンコーディングを検出
            encoding = self._detect_encoding()
            self.logger.debug(f"検出されたエンコーディング: {encoding}")
            
            # TSVファイルを読み込む
            song_infos = []
            with open(self.file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                # ヘッダーの検証
                expected_headers = ['アーティスト', 'アーティスト(ソート用)', '曲名', '最近の歌唱']
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
                        song_info = self._parse_row(row, line_num)
                        song_infos.append(song_info)
                    except Exception as e:
                        error_msg = f"行 {line_num} の解析に失敗しました: {e}"
                        self.logger.error(error_msg)
                        raise DataLoadError(
                            file_path=str(self.file_path),
                            message=error_msg
                        )
            
            self.logger.info(
                f"曲リストを読み込みました: {len(song_infos)}件 ({self.file_path})"
            )
            return song_infos
            
        except DataLoadError:
            raise
        except Exception as e:
            error_msg = f"ファイルの読み込みに失敗しました: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise DataLoadError(
                file_path=str(self.file_path),
                message=error_msg
            )
    
    def save_all(self, songs: List[SongInfo]) -> None:
        """
        曲リストを保存
        
        Args:
            songs: 保存する曲情報のリスト
            
        Raises:
            FileWriteError: ファイルの書き込みに失敗した場合
        """
        try:
            # 親ディレクトリが存在しない場合は作成
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # UTF-8エンコーディングでTSVファイルに書き込む
            with open(self.file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                
                # ヘッダーを書き込む
                writer.writerow(['アーティスト', 'アーティスト(ソート用)', '曲名', '最近の歌唱'])
                
                # データ行を書き込む
                for song in songs:
                    writer.writerow([
                        song.artist,
                        song.artist_sort,
                        song.song_name,
                        song.latest_url
                    ])
            
            self.logger.info(
                f"曲リストを保存しました: {len(songs)}件 ({self.file_path})"
            )
            
        except PermissionError as e:
            error_msg = "ファイルへの書き込み権限がありません"
            self.logger.error(f"{error_msg}: {self.file_path}", exc_info=True)
            raise FileWriteError(
                file_path=str(self.file_path),
                message=error_msg,
                original_error=e
            ) from e
            
        except OSError as e:
            error_msg = "ファイルの書き込みに失敗しました"
            self.logger.error(f"{error_msg}: {e}", exc_info=True)
            raise FileWriteError(
                file_path=str(self.file_path),
                message=error_msg,
                original_error=e
            ) from e
            
        except Exception as e:
            error_msg = "予期しないエラーが発生しました"
            self.logger.error(f"{error_msg}: {e}", exc_info=True)
            raise FileWriteError(
                file_path=str(self.file_path),
                message=error_msg,
                original_error=e
            ) from e
    
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
    
    def _parse_row(self, row: dict, line_num: int) -> SongInfo:
        """
        TSVの1行をSongInfoオブジェクトに変換
        
        Args:
            row: TSVの行データ（辞書形式）
            line_num: 行番号（エラーメッセージ用）
            
        Returns:
            SongInfoオブジェクト
            
        Raises:
            ValueError: データの解析に失敗した場合
        """
        try:
            # 各フィールドを取得
            artist = row['アーティスト'].strip()
            artist_sort = row['アーティスト(ソート用)'].strip()
            song_name = row['曲名'].strip()
            latest_url = row['最近の歌唱'].strip()
            
            return SongInfo(
                artist=artist,
                artist_sort=artist_sort,
                song_name=song_name,
                latest_url=latest_url
            )
            
        except KeyError as e:
            raise ValueError(f"必須フィールドが見つかりません: {e}")
