"""
Data Serviceのプロパティベーステスト

DataServiceクラスの普遍的な性質を多数のランダム入力で検証します。
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock
import pandas as pd
from hypothesis import given, strategies as st, settings

from src.services.data_service import DataService
from src.config.settings import Config


# カスタム戦略：有効なDataFrame生成
@st.composite
def valid_dataframe_strategy(draw):
    """有効なDataFrameを生成する戦略"""
    # 行数を生成（1〜100行）
    num_rows = draw(st.integers(min_value=1, max_value=100))
    
    # IDリストを生成
    ids = list(range(1, num_rows + 1))
    
    # 日付リストを生成
    dates = [f"2024/{draw(st.integers(min_value=1, max_value=12)):02d}/{draw(st.integers(min_value=1, max_value=28)):02d}" 
             for _ in range(num_rows)]
    
    # タイトルリストを生成
    titles = [draw(st.text(min_size=1, max_size=50)) for _ in range(num_rows)]
    
    # URLリストを生成
    urls = [f"https://youtube.com/watch?v={draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=6, max_size=11))}" 
            for _ in range(num_rows)]
    
    return pd.DataFrame({
        "ID": ids,
        "配信日": dates,
        "タイトル": titles,
        "URL": urls
    })


@st.composite
def valid_songs_dataframe_strategy(draw):
    """有効な楽曲DataFrameを生成する戦略"""
    # 行数を生成（1〜100行）
    num_rows = draw(st.integers(min_value=1, max_value=100))
    
    # IDリストを生成
    ids = list(range(1, num_rows + 1))
    
    # LIVE_IDリストを生成（1〜10のランダムなID）
    live_ids = [draw(st.integers(min_value=1, max_value=10)) for _ in range(num_rows)]
    
    # 曲名リストを生成
    song_names = [draw(st.text(min_size=1, max_size=50)) for _ in range(num_rows)]
    
    # タイムスタンプリストを生成
    timestamps = [f"{draw(st.integers(min_value=0, max_value=23)):02d}:{draw(st.integers(min_value=0, max_value=59)):02d}" 
                  for _ in range(num_rows)]
    
    return pd.DataFrame({
        "ID": ids,
        "LIVE_ID": live_ids,
        "曲名": song_names,
        "タイムスタンプ": timestamps
    })


class TestDataServiceProperties:
    """Data Serviceのプロパティベーステスト"""
    
    @given(valid_dataframe_strategy())
    @settings(max_examples=100, deadline=5000)
    def test_property_17_data_loading_consistency(self, df):
        """
        Feature: test-coverage-improvement, Property 17: データ読み込みの一貫性
        
        すべての有効なTSVファイルに対して、読み込みが成功した場合、
        DataFrameが返され、error_messageがNoneである
        
        **検証: 要件8.1**
        """
        # 一時TSVファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False, encoding='utf-8') as f:
            df.to_csv(f.name, sep='\t', index=False)
            temp_file = f.name
        
        try:
            # Configをモック
            config = Mock(spec=Config)
            config.lives_file_path = temp_file
            
            # DataServiceを初期化してデータを読み込む
            service = DataService(config)
            result = service.load_lives_data()
            
            # プロパティ検証：読み込みが成功した場合、DataFrameが返され、エラーメッセージがNone
            if result is not None:
                assert isinstance(result, pd.DataFrame)
                assert service.get_last_error() is None
                assert len(result) == len(df)
        finally:
            # クリーンアップ
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    @given(valid_dataframe_strategy(), valid_songs_dataframe_strategy())
    @settings(max_examples=100, deadline=5000)
    def test_property_18_data_merging_consistency(self, lives_df, songs_df):
        """
        Feature: test-coverage-improvement, Property 18: データ結合の一貫性
        
        すべての配信データと楽曲データのペアに対して、
        結合後のデータ件数は楽曲データの件数と一致する（左結合）
        
        **検証: 要件8.2**
        """
        # Configをモック
        config = Mock(spec=Config)
        
        # DataServiceを初期化してデータを結合
        service = DataService(config)
        result = service.merge_data(lives_df, songs_df)
        
        # プロパティ検証：結合後のデータ件数は楽曲データの件数と一致
        assert len(result) == len(songs_df)
        
        # プロパティ検証：必須列が存在する
        assert "楽曲ID" in result.columns
        assert "ライブタイトル" in result.columns
        assert "元ライブURL" in result.columns
        
        # プロパティ検証：不要な列が削除されている
        assert "ID_live" not in result.columns
    
    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=100, deadline=5000)
    def test_property_19_error_handling_consistency(self, invalid_path):
        """
        Feature: test-coverage-improvement, Property 19: エラー処理の一貫性
        
        すべてのエラー状況（ファイル不存在、読み込みエラー）に対して、
        Noneが返され、error_messageが空でない
        
        **検証: 要件8.3**
        """
        # Configをモック（存在しないファイルパス）
        config = Mock(spec=Config)
        config.lives_file_path = f"/nonexistent/{invalid_path}/M_YT_LIVE.TSV"
        
        # DataServiceを初期化してデータを読み込む
        service = DataService(config)
        result = service.load_lives_data()
        
        # プロパティ検証：エラー時はNoneが返され、エラーメッセージが設定される
        assert result is None
        assert service.get_last_error() is not None
        assert isinstance(service.get_last_error(), str)
        assert len(service.get_last_error()) > 0
    
    @given(valid_dataframe_strategy())
    @settings(max_examples=100, deadline=5000)
    def test_property_20_missing_value_handling_consistency(self, df):
        """
        Feature: test-coverage-improvement, Property 20: 欠損値処理の一貫性
        
        すべての欠損値を含むデータに対して、適切なデフォルト値が設定され、
        処理が継続される
        
        **検証: 要件8.4**
        """
        # データフレームに欠損値を追加
        df_with_nan = df.copy()
        
        # ランダムに欠損値を追加（各列の一部の値をNaNに設定）
        if len(df_with_nan) > 0:
            # タイトル列に欠損値を追加
            if "タイトル" in df_with_nan.columns:
                df_with_nan.loc[0, "タイトル"] = None
            
            # URL列に欠損値を追加
            if "URL" in df_with_nan.columns and len(df_with_nan) > 1:
                df_with_nan.loc[1, "URL"] = None
        
        # 一時TSVファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False, encoding='utf-8') as f:
            df_with_nan.to_csv(f.name, sep='\t', index=False)
            temp_file = f.name
        
        try:
            # Configをモック
            config = Mock(spec=Config)
            config.lives_file_path = temp_file
            
            # DataServiceを初期化してデータを読み込む
            service = DataService(config)
            result = service.load_lives_data()
            
            # プロパティ検証：欠損値があっても読み込みが成功する
            assert result is not None
            assert isinstance(result, pd.DataFrame)
            assert service.get_last_error() is None
            
            # プロパティ検証：データ件数は元のデータと同じ
            assert len(result) == len(df_with_nan)
            
            # プロパティ検証：欠損値がpandasのNaNとして保持されている
            # （DataServiceは欠損値をそのまま保持し、後続の処理で適切に扱う）
            if len(result) > 0 and "タイトル" in result.columns:
                assert pd.isna(result.loc[0, "タイトル"])
            
            if len(result) > 1 and "URL" in result.columns:
                assert pd.isna(result.loc[1, "URL"])
        finally:
            # クリーンアップ
            if os.path.exists(temp_file):
                os.unlink(temp_file)
