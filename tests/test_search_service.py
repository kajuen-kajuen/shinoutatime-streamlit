"""
検索サービスのテスト

src/services/search_service.pyのSearchServiceクラスが正しく動作することを確認するテストです。
"""

import pytest
import pandas as pd

from src.services.search_service import SearchService


class TestSearchService:
    """SearchServiceクラスのテスト"""
    
    @pytest.fixture
    def search_service(self):
        """SearchServiceのインスタンスを提供するフィクスチャ"""
        return SearchService()
    
    @pytest.fixture
    def sample_df(self):
        """テスト用のサンプルDataFrameを提供するフィクスチャ"""
        return pd.DataFrame({
            "曲名": ["Lemon", "Pretender", "紅蓮華", "炎", "夜に駆ける"],
            "アーティスト": ["米津玄師", "Official髭男dism", "LiSA", "LiSA", "YOASOBI"],
            "ライブタイトル": ["歌枠1", "歌枠2", "アニソン特集", "アニソン特集", "夜の歌枠"],
            "配信日": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-03", "2024-01-04"],
        })
    
    # ========================================
    # search メソッドのテスト
    # ========================================
    
    def test_search_single_field_found(self, search_service, sample_df):
        """単一フィールドで検索し、結果が見つかることを確認"""
        result = search_service.search(sample_df, "Lemon", ["曲名"])
        
        assert len(result) == 1
        assert result.iloc[0]["曲名"] == "Lemon"
    
    def test_search_single_field_not_found(self, search_service, sample_df):
        """単一フィールドで検索し、結果が見つからないことを確認"""
        result = search_service.search(sample_df, "存在しない曲", ["曲名"])
        
        assert len(result) == 0
    
    def test_search_multiple_fields(self, search_service, sample_df):
        """複数フィールドで検索し、OR検索が動作することを確認"""
        result = search_service.search(sample_df, "LiSA", ["曲名", "アーティスト"])
        
        # "LiSA"がアーティスト列に含まれる行が2件
        assert len(result) == 2
        assert all(result["アーティスト"] == "LiSA")
    
    def test_search_case_insensitive(self, search_service, sample_df):
        """大文字小文字を区別しない検索が動作することを確認"""
        result = search_service.search(sample_df, "lemon", ["曲名"], case_sensitive=False)
        
        assert len(result) == 1
        assert result.iloc[0]["曲名"] == "Lemon"
    
    def test_search_case_sensitive(self, search_service, sample_df):
        """大文字小文字を区別する検索が動作することを確認"""
        result = search_service.search(sample_df, "lemon", ["曲名"], case_sensitive=True)
        
        # 大文字小文字を区別するため、"lemon"は見つからない
        assert len(result) == 0
    
    def test_search_empty_query(self, search_service, sample_df):
        """空のクエリの場合、元のDataFrameを返すことを確認"""
        result = search_service.search(sample_df, "", ["曲名"])
        
        assert len(result) == len(sample_df)
        assert result.equals(sample_df)
    
    def test_search_whitespace_query(self, search_service, sample_df):
        """空白のみのクエリの場合、元のDataFrameを返すことを確認"""
        result = search_service.search(sample_df, "   ", ["曲名"])
        
        assert len(result) == len(sample_df)
        assert result.equals(sample_df)
    
    def test_search_nonexistent_field(self, search_service, sample_df):
        """存在しないフィールドを指定した場合、空の結果を返すことを確認"""
        result = search_service.search(sample_df, "Lemon", ["存在しない列"])
        
        assert len(result) == 0
    
    def test_search_partial_match(self, search_service, sample_df):
        """部分一致検索が動作することを確認"""
        result = search_service.search(sample_df, "歌枠", ["ライブタイトル"])
        
        # "歌枠"を含むタイトルが3件
        assert len(result) == 3
    
    def test_search_japanese_characters(self, search_service, sample_df):
        """日本語文字での検索が正しく動作することを確認"""
        result = search_service.search(sample_df, "紅蓮華", ["曲名"])
        
        assert len(result) == 1
        assert result.iloc[0]["曲名"] == "紅蓮華"
    
    def test_search_multiple_results(self, search_service, sample_df):
        """複数の結果が返されることを確認"""
        result = search_service.search(sample_df, "アニソン", ["ライブタイトル"])
        
        # "アニソン特集"が2件
        assert len(result) == 2
    
    # ========================================
    # filter_by_multiple_conditions メソッドのテスト
    # ========================================
    
    def test_filter_single_condition(self, search_service, sample_df):
        """単一条件でフィルタリングできることを確認"""
        conditions = {"アーティスト": "LiSA"}
        result = search_service.filter_by_multiple_conditions(sample_df, conditions)
        
        assert len(result) == 2
        assert all(result["アーティスト"] == "LiSA")
    
    def test_filter_multiple_conditions(self, search_service, sample_df):
        """複数条件（AND）でフィルタリングできることを確認"""
        conditions = {
            "アーティスト": "LiSA",
            "ライブタイトル": "アニソン特集"
        }
        result = search_service.filter_by_multiple_conditions(sample_df, conditions)
        
        assert len(result) == 2
        assert all(result["アーティスト"] == "LiSA")
        assert all(result["ライブタイトル"] == "アニソン特集")
    
    def test_filter_no_match(self, search_service, sample_df):
        """条件に一致する行がない場合、空の結果を返すことを確認"""
        conditions = {"アーティスト": "存在しないアーティスト"}
        result = search_service.filter_by_multiple_conditions(sample_df, conditions)
        
        assert len(result) == 0
    
    def test_filter_empty_conditions(self, search_service, sample_df):
        """空の条件の場合、元のDataFrameを返すことを確認"""
        result = search_service.filter_by_multiple_conditions(sample_df, {})
        
        assert len(result) == len(sample_df)
        assert result.equals(sample_df)
    
    def test_filter_nonexistent_field(self, search_service, sample_df):
        """存在しないフィールドを指定した場合、元のDataFrameを返すことを確認"""
        conditions = {"存在しない列": "値"}
        result = search_service.filter_by_multiple_conditions(sample_df, conditions)
        
        # 存在しないフィールドはスキップされ、全行が返される
        assert len(result) == len(sample_df)
    
    def test_filter_exact_match(self, search_service, sample_df):
        """完全一致でフィルタリングされることを確認"""
        conditions = {"配信日": "2024-01-03"}
        result = search_service.filter_by_multiple_conditions(sample_df, conditions)
        
        assert len(result) == 2
        assert all(result["配信日"] == "2024-01-03")
    
    # ========================================
    # エッジケースのテスト
    # ========================================
    
    def test_search_with_nan_values(self, search_service):
        """NaN値を含むDataFrameで検索が正しく動作することを確認"""
        df = pd.DataFrame({
            "曲名": ["Lemon", None, "紅蓮華"],
            "アーティスト": ["米津玄師", "不明", None],
        })
        
        result = search_service.search(df, "Lemon", ["曲名"])
        
        assert len(result) == 1
        assert result.iloc[0]["曲名"] == "Lemon"
    
    def test_search_empty_dataframe(self, search_service):
        """空のDataFrameで検索しても例外が発生しないことを確認"""
        df = pd.DataFrame(columns=["曲名", "アーティスト"])
        
        result = search_service.search(df, "Lemon", ["曲名"])
        
        assert len(result) == 0
    
    def test_filter_empty_dataframe(self, search_service):
        """空のDataFrameでフィルタリングしても例外が発生しないことを確認"""
        df = pd.DataFrame(columns=["曲名", "アーティスト"])
        
        result = search_service.filter_by_multiple_conditions(df, {"曲名": "Lemon"})
        
        assert len(result) == 0
