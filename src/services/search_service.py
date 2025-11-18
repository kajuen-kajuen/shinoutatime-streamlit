"""
検索サービスモジュール

キーワード検索、フィルタリング、検索結果の管理を担当するサービスクラスを提供します。
"""

import logging
from typing import List, Dict, Any
import pandas as pd

# ロガーの設定
logger = logging.getLogger(__name__)


class SearchService:
    """
    検索サービス
    
    DataFrameに対するキーワード検索とフィルタリング機能を提供します。
    複数フィールドに対する検索や、大文字小文字を区別しない検索に対応しています。
    
    Examples:
        >>> service = SearchService()
        >>> results = service.search(df, "紅蓮華", ["楽曲名", "アーティスト"])
        >>> filtered = service.filter_by_multiple_conditions(df, {"配信日": "2024-01-01"})
    """
    
    def __init__(self):
        """検索サービスの初期化"""
        logger.info("SearchServiceを初期化しました")
    
    def search(
        self,
        df: pd.DataFrame,
        query: str,
        fields: List[str],
        case_sensitive: bool = False
    ) -> pd.DataFrame:
        """
        データフレームを検索する
        
        指定されたフィールドに対してキーワード検索を実行します。
        複数のフィールドを指定した場合、いずれかのフィールドに
        クエリが含まれる行を返します（OR検索）。
        
        Args:
            df: 検索対象のDataFrame
            query: 検索クエリ（キーワード）
            fields: 検索対象フィールドのリスト
            case_sensitive: 大文字小文字を区別するか（デフォルト: False）
        
        Returns:
            フィルタリングされたDataFrame
            
        Note:
            - クエリが空文字列の場合、元のDataFrameをそのまま返します
            - 指定されたフィールドが存在しない場合、そのフィールドはスキップされます
            - デフォルトでは大文字小文字を区別しません
        
        Examples:
            >>> service = SearchService()
            >>> # 楽曲名とアーティストから「紅蓮華」を検索
            >>> results = service.search(df, "紅蓮華", ["楽曲名", "アーティスト"])
            >>> # 大文字小文字を区別して検索
            >>> results = service.search(df, "LiSA", ["アーティスト"], case_sensitive=True)
        """
        # クエリが空の場合は元のDataFrameを返す
        if not query or query.strip() == "":
            logger.debug("検索クエリが空のため、元のDataFrameを返します")
            return df
        
        logger.info(f"検索を実行中: クエリ='{query}', フィールド={fields}, 大文字小文字区別={case_sensitive}")
        
        # 検索条件を構築
        mask = pd.Series([False] * len(df), index=df.index)
        
        for field in fields:
            # フィールドが存在するか確認
            if field not in df.columns:
                logger.warning(f"フィールド '{field}' が存在しないためスキップします")
                continue
            
            # 文字列型に変換してから検索
            field_data = df[field].astype(str)
            
            if case_sensitive:
                # 大文字小文字を区別する検索
                mask |= field_data.str.contains(query, na=False, regex=False)
            else:
                # 大文字小文字を区別しない検索
                mask |= field_data.str.contains(query, case=False, na=False, regex=False)
        
        result_df = df[mask]
        logger.info(f"検索結果: {len(result_df)}件")
        
        return result_df
    
    def filter_by_multiple_conditions(
        self,
        df: pd.DataFrame,
        conditions: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        複数条件でフィルタリングする
        
        指定された条件（フィールド名と値の辞書）に基づいて
        DataFrameをフィルタリングします。全ての条件を満たす行のみを返します（AND条件）。
        
        Args:
            df: フィルタリング対象のDataFrame
            conditions: フィールド名と値の辞書
                       例: {"配信日": "2024-01-01", "アーティスト": "LiSA"}
        
        Returns:
            フィルタリングされたDataFrame
            
        Note:
            - 条件が空の場合、元のDataFrameをそのまま返します
            - 指定されたフィールドが存在しない場合、そのフィールドはスキップされます
            - 全ての条件がANDで結合されます
        
        Examples:
            >>> service = SearchService()
            >>> # 特定の配信日とアーティストでフィルタリング
            >>> conditions = {"配信日": "2024-01-01", "アーティスト": "LiSA"}
            >>> results = service.filter_by_multiple_conditions(df, conditions)
        """
        # 条件が空の場合は元のDataFrameを返す
        if not conditions:
            logger.debug("フィルタリング条件が空のため、元のDataFrameを返します")
            return df
        
        logger.info(f"複数条件でフィルタリング中: {conditions}")
        
        # フィルタリング条件を構築
        mask = pd.Series([True] * len(df), index=df.index)
        
        for field, value in conditions.items():
            # フィールドが存在するか確認
            if field not in df.columns:
                logger.warning(f"フィールド '{field}' が存在しないためスキップします")
                continue
            
            # 条件を適用（AND条件）
            mask &= (df[field] == value)
        
        result_df = df[mask]
        logger.info(f"フィルタリング結果: {len(result_df)}件")
        
        return result_df

