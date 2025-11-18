"""
データパイプラインモジュール

データ処理の全体フローを管理するパイプラインクラスを提供します。
データの読み込み、結合、変換、ソートの各ステップを明確に分離し、
キャッシング機能とエラーハンドリングを提供します。
"""

import logging
from typing import Optional, Tuple
import pandas as pd

from src.services.data_service import DataService
from src.config.settings import Config
from src.core.utils import (
    convert_timestamp_to_seconds,
    generate_youtube_url,
    generate_song_numbers,
    convert_date_string,
)
from src.exceptions.errors import DataProcessingError, log_error

# ロガーの設定
logger = logging.getLogger(__name__)


class DataPipeline:
    """
    データ処理パイプライン
    
    データの読み込みから最終的な表示用データの生成までの
    全体フローを管理します。各処理ステップを明確に分離し、
    キャッシング機能により効率的なデータ処理を実現します。
    
    処理フロー:
        1. データ読み込み（_load_data）
        2. データ結合（_merge_data）
        3. データ変換（_transform_data）
        4. データソート（_sort_data）
    
    Attributes:
        data_service (DataService): データサービス
        config (Config): 設定オブジェクト
        _cache (dict): 処理結果のキャッシュ
    
    Examples:
        >>> config = Config()
        >>> data_service = DataService(config)
        >>> pipeline = DataPipeline(data_service, config)
        >>> df = pipeline.execute()
        >>> if df is not None:
        ...     print(f"処理完了: {len(df)}件")
    """
    
    def __init__(self, data_service: DataService, config: Config):
        """
        DataPipelineを初期化する
        
        Args:
            data_service: データサービス
            config: 設定オブジェクト
        """
        self.data_service = data_service
        self.config = config
        self._cache = {}
        logger.info("DataPipelineを初期化しました")
    
    def execute(self) -> Optional[pd.DataFrame]:
        """
        パイプライン全体を実行する
        
        データの読み込みから最終的な表示用データの生成までの
        全ての処理ステップを順次実行します。
        キャッシュが有効な場合、2回目以降はキャッシュから結果を返します。
        
        Returns:
            処理済みDataFrame。エラー時はNone
            
        Note:
            各ステップでエラーが発生した場合、適切なエラーメッセージを
            ログに記録し、Noneを返します。
        """
        # キャッシュチェック
        if self.config.enable_cache and "final_data" in self._cache:
            logger.info("キャッシュからデータを返します")
            return self._cache["final_data"]
        
        logger.info("データパイプラインを実行開始")
        
        try:
            # ステップ1: データ読み込み
            lives_df, songs_df = self._load_data()
            if lives_df is None or songs_df is None:
                logger.error("データ読み込みに失敗しました")
                return None
            
            if not self._validate_step_result(lives_df, "load_lives"):
                return None
            if not self._validate_step_result(songs_df, "load_songs"):
                return None
            
            # ステップ2: データ結合
            merged_df = self._merge_data(lives_df, songs_df)
            if not self._validate_step_result(merged_df, "merge"):
                return None
            
            # ステップ3: データ変換
            transformed_df = self._transform_data(merged_df)
            if not self._validate_step_result(transformed_df, "transform"):
                return None
            
            # ステップ4: データソート
            sorted_df = self._sort_data(transformed_df)
            if not self._validate_step_result(sorted_df, "sort"):
                return None
            
            # キャッシュに保存
            if self.config.enable_cache:
                self._cache["final_data"] = sorted_df
                logger.info("処理結果をキャッシュに保存しました")
            
            logger.info(f"データパイプライン実行完了: {len(sorted_df)}件")
            return sorted_df
            
        except Exception as e:
            error_msg = f"データパイプライン実行中にエラーが発生しました: {e}"
            logger.error(error_msg, exc_info=True)
            log_error(DataProcessingError("execute", str(e)))
            return None
    
    def _load_data(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        データ読み込みステップ
        
        配信データと楽曲データをTSVファイルから読み込みます。
        
        Returns:
            (配信データ, 楽曲データ)のタプル。エラー時は(None, None)
        """
        logger.info("ステップ1: データ読み込み開始")
        
        lives_df = self.data_service.load_lives_data()
        songs_df = self.data_service.load_songs_data()
        
        if lives_df is None:
            logger.error(f"配信データの読み込みに失敗: {self.data_service.get_last_error()}")
            return None, None
        
        if songs_df is None:
            logger.error(f"楽曲データの読み込みに失敗: {self.data_service.get_last_error()}")
            return None, None
        
        logger.info(f"データ読み込み完了: 配信{len(lives_df)}件、楽曲{len(songs_df)}件")
        return lives_df, songs_df
    
    def _merge_data(
        self, 
        lives_df: pd.DataFrame, 
        songs_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        データ結合ステップ
        
        配信データと楽曲データをLIVE_IDをキーとして結合します。
        
        Args:
            lives_df: 配信データ
            songs_df: 楽曲データ
        
        Returns:
            結合されたDataFrame
        """
        logger.info("ステップ2: データ結合開始")
        
        try:
            merged_df = self.data_service.merge_data(lives_df, songs_df)
            
            # 表示用の「ライブ配信日」列を作成（元データをそのまま使用）
            merged_df["ライブ配信日"] = merged_df["ライブ配信日_original"]
            
            logger.info(f"データ結合完了: {len(merged_df)}件")
            return merged_df
            
        except Exception as e:
            error_msg = f"データ結合中にエラーが発生しました: {e}"
            logger.error(error_msg, exc_info=True)
            raise DataProcessingError("merge", str(e))
    
    def _transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        データ変換ステップ
        
        タイムスタンプ変換、日付変換、URL生成、曲目番号生成を実行します。
        
        Args:
            df: 変換対象のDataFrame
        
        Returns:
            変換後のDataFrame
        """
        logger.info("ステップ3: データ変換開始")
        
        try:
            df_result = df.copy()
            
            # タイムスタンプ変換: HH:MM:SSまたはMM:SS形式を秒数に変換
            logger.debug("タイムスタンプを秒数に変換中")
            df_result["タイムスタンプ_秒"] = df_result["タイムスタンプ"].apply(
                convert_timestamp_to_seconds
            )
            
            # 日付変換: ソート用に配信日を日付型（datetime）に変換
            logger.debug("配信日をdatetime型に変換中")
            # まずUNIXミリ秒として変換を試みる
            df_result["ライブ配信日_sortable"] = pd.to_datetime(
                df_result["ライブ配信日_original"], unit="ms", errors="coerce"
            )
            
            # UNIXミリ秒で変換できなかった行（NaT）に対して、YYYY/MM/DD形式として再変換
            mask_nat_sortable = df_result["ライブ配信日_sortable"].isna()
            if mask_nat_sortable.any():
                try:
                    df_result.loc[mask_nat_sortable, "ライブ配信日_sortable"] = pd.to_datetime(
                        df_result.loc[mask_nat_sortable, "ライブ配信日_original"],
                        errors="coerce",
                    )
                except Exception as e:
                    logger.warning(f"ソート用の「ライブ配信日」変換中にエラーが発生しました: {e}")
            
            # YouTubeタイムスタンプ付きURL生成
            logger.debug("YouTubeタイムスタンプ付きURLを生成中")
            df_result["YouTubeタイムスタンプ付きURL"] = df_result.apply(
                lambda row: generate_youtube_url(
                    row["元ライブURL"], 
                    row["タイムスタンプ_秒"]
                ),
                axis=1,
            )
            
            logger.info("データ変換完了")
            return df_result
            
        except Exception as e:
            error_msg = f"データ変換中にエラーが発生しました: {e}"
            logger.error(error_msg, exc_info=True)
            raise DataProcessingError("transform", str(e))
    
    def _sort_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        データソートステップ
        
        データをソートし、曲目番号を生成します。
        
        Args:
            df: ソート対象のDataFrame
        
        Returns:
            ソート後のDataFrame
        """
        logger.info("ステップ4: データソート開始")
        
        try:
            # データをソート: 配信日降順（新しい順）→ LIVE_ID昇順 → タイムスタンプ昇順
            logger.debug("データをソート中")
            df_result = df.sort_values(
                by=["ライブ配信日_sortable", "LIVE_ID", "タイムスタンプ_秒"],
                ascending=[False, True, True],
            ).reset_index(drop=True)
            
            # 曲目番号生成
            logger.debug("曲目番号を生成中")
            df_result = generate_song_numbers(df_result)
            
            logger.info("データソート完了")
            return df_result
            
        except Exception as e:
            error_msg = f"データソート中にエラーが発生しました: {e}"
            logger.error(error_msg, exc_info=True)
            raise DataProcessingError("sort", str(e))
    
    def _validate_step_result(self, df: pd.DataFrame, step_name: str) -> bool:
        """
        ステップ結果を検証する
        
        各処理ステップの結果が有効かどうかを検証します。
        
        Args:
            df: 検証対象のDataFrame
            step_name: ステップ名
        
        Returns:
            検証成功時True、失敗時False
        """
        if df is None:
            logger.error(f"ステップ '{step_name}' の結果がNoneです")
            return False
        
        if not isinstance(df, pd.DataFrame):
            logger.error(f"ステップ '{step_name}' の結果がDataFrameではありません")
            return False
        
        if len(df) == 0:
            logger.warning(f"ステップ '{step_name}' の結果が空のDataFrameです")
            # 空のDataFrameは警告のみで処理を継続
        
        return True
    
    def clear_cache(self):
        """
        キャッシュをクリアする
        
        パイプラインの処理結果キャッシュをクリアします。
        データファイルが更新された場合などに使用します。
        """
        self._cache.clear()
        logger.info("キャッシュをクリアしました")
