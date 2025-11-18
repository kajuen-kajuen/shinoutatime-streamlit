"""
データサービスモジュール

TSVファイルからのデータ読み込み、データの基本的な検証、
エラーハンドリングを担当するサービスクラスを提供します。
"""

import logging
from typing import Optional
import pandas as pd

from src.config.settings import Config
from src.exceptions.errors import DataLoadError

# ロガーの設定
logger = logging.getLogger(__name__)


class DataService:
    """
    データ読み込みサービス
    
    TSVファイルからのデータ読み込みとデータ結合を担当します。
    エラーハンドリングを内部で処理し、エラー情報を保持します。
    
    Attributes:
        config (Config): 設定オブジェクト
        error_message (Optional[str]): 最後に発生したエラーメッセージ
    
    Examples:
        >>> config = Config()
        >>> service = DataService(config)
        >>> lives_df = service.load_lives_data()
        >>> if lives_df is not None:
        ...     print(f"配信データ: {len(lives_df)}件")
    """
    
    def __init__(self, config: Config):
        """
        DataServiceを初期化する
        
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.error_message: Optional[str] = None
        logger.info("DataServiceを初期化しました")
    
    def load_lives_data(self) -> Optional[pd.DataFrame]:
        """
        配信データを読み込む
        
        M_YT_LIVE.TSVファイルから配信情報を読み込みます。
        ファイルが存在しない場合や読み込みに失敗した場合は、
        エラーメッセージを保持してNoneを返します。
        
        Returns:
            配信データのDataFrame。エラー時はNone
            
        Note:
            エラーが発生した場合、get_last_error()でエラーメッセージを取得できます
        """
        file_path = self.config.lives_file_path
        
        try:
            logger.info(f"配信データを読み込み中: {file_path}")
            df = pd.read_csv(file_path, delimiter="\t")
            logger.info(f"配信データを読み込みました: {len(df)}件")
            self.error_message = None
            return df
            
        except FileNotFoundError:
            error_msg = f'配信情報ファイル "{file_path}" が見つかりません'
            self.error_message = error_msg
            logger.error(error_msg)
            return None
            
        except Exception as e:
            error_msg = f'配信情報ファイル "{file_path}" の読み込み中にエラーが発生しました: {e}'
            self.error_message = error_msg
            logger.error(error_msg, exc_info=True)
            return None
    
    def load_songs_data(self) -> Optional[pd.DataFrame]:
        """
        楽曲データを読み込む
        
        M_YT_LIVE_TIMESTAMP.TSVファイルから楽曲タイムスタンプ情報を読み込みます。
        ファイルが存在しない場合や読み込みに失敗した場合は、
        エラーメッセージを保持してNoneを返します。
        
        Returns:
            楽曲データのDataFrame。エラー時はNone
            
        Note:
            エラーが発生した場合、get_last_error()でエラーメッセージを取得できます
        """
        file_path = self.config.songs_file_path
        
        try:
            logger.info(f"楽曲データを読み込み中: {file_path}")
            df = pd.read_csv(file_path, delimiter="\t")
            logger.info(f"楽曲データを読み込みました: {len(df)}件")
            self.error_message = None
            return df
            
        except FileNotFoundError:
            error_msg = f'楽曲情報ファイル "{file_path}" が見つかりません'
            self.error_message = error_msg
            logger.error(error_msg)
            return None
            
        except Exception as e:
            error_msg = f'楽曲情報ファイル "{file_path}" の読み込み中にエラーが発生しました: {e}'
            self.error_message = error_msg
            logger.error(error_msg, exc_info=True)
            return None
    
    def load_song_list_data(self) -> Optional[pd.DataFrame]:
        """
        楽曲リストデータを読み込む
        
        V_SONG_LIST.TSVファイルから楽曲リスト情報を読み込みます。
        ファイルが存在しない場合や読み込みに失敗した場合は、
        エラーメッセージを保持してNoneを返します。
        
        Returns:
            楽曲リストデータのDataFrame。エラー時はNone
            
        Note:
            エラーが発生した場合、get_last_error()でエラーメッセージを取得できます
        """
        file_path = self.config.song_list_file_path
        
        try:
            logger.info(f"楽曲リストデータを読み込み中: {file_path}")
            df = pd.read_csv(file_path, delimiter="\t")
            logger.info(f"楽曲リストデータを読み込みました: {len(df)}件")
            self.error_message = None
            return df
            
        except FileNotFoundError:
            error_msg = f'楽曲リストファイル "{file_path}" が見つかりません'
            self.error_message = error_msg
            logger.error(error_msg)
            return None
            
        except Exception as e:
            error_msg = f'楽曲リストファイル "{file_path}" の読み込み中にエラーが発生しました: {e}'
            self.error_message = error_msg
            logger.error(error_msg, exc_info=True)
            return None
    
    def merge_data(
        self, 
        lives_df: pd.DataFrame, 
        songs_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        配信データと楽曲データを結合する
        
        配信情報（lives_df）と楽曲情報（songs_df）をLIVE_IDをキーとして左結合します。
        楽曲データを基準として配信情報を紐付けることで、
        各楽曲がどの配信で歌われたかを特定できます。
        
        Args:
            lives_df: 配信データ（M_YT_LIVE.TSV）
            songs_df: 楽曲データ（M_YT_LIVE_TIMESTAMP.TSV）
        
        Returns:
            結合されたDataFrame
            
        Note:
            - 左結合（left join）により、楽曲データを基準とする
            - 結合後、不要な列（ID_live）は削除される
            - 列名は日本語名に変更される
        
        Examples:
            >>> lives_df = service.load_lives_data()
            >>> songs_df = service.load_songs_data()
            >>> merged_df = service.merge_data(lives_df, songs_df)
        """
        logger.info("配信データと楽曲データを結合中")
        
        try:
            # LIVE_IDをキーとして左結合
            df_merged = pd.merge(
                songs_df,
                lives_df[["ID", "配信日", "タイトル", "URL"]],
                left_on="LIVE_ID",
                right_on="ID",
                how="left",
                suffixes=("_song", "_live"),
            )
            
            # 不要な列を削除
            df_merged = df_merged.drop(columns=["ID_live"])
            
            # 列名を日本語名に変更
            df_merged = df_merged.rename(
                columns={
                    "ID_song": "楽曲ID",
                    "配信日": "ライブ配信日_original",
                    "タイトル": "ライブタイトル",
                    "URL": "元ライブURL",
                }
            )
            
            logger.info(f"データ結合が完了しました: {len(df_merged)}件")
            self.error_message = None
            return df_merged
            
        except Exception as e:
            error_msg = f"データ結合中にエラーが発生しました: {e}"
            self.error_message = error_msg
            logger.error(error_msg, exc_info=True)
            raise DataLoadError("merge_data", error_msg)
    
    def get_last_error(self) -> Optional[str]:
        """
        最後に発生したエラーメッセージを取得
        
        Returns:
            エラーメッセージ。エラーがない場合はNone
            
        Examples:
            >>> lives_df = service.load_lives_data()
            >>> if lives_df is None:
            ...     print(service.get_last_error())
        """
        return self.error_message
