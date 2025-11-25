"""
アーティストフィルタリング処理のユニットテスト

pages/99_Song_List_beta.pyのアーティスト名「-」フィルタリング処理の
エッジケースを検証します。
"""

import pytest
import pandas as pd


def filter_hyphen_artists(df: pd.DataFrame) -> pd.DataFrame:
    """
    アーティスト名が「-」の楽曲を除外する
    
    pages/99_Song_List_beta.pyの実装と同じロジック
    
    Args:
        df: 楽曲データを含むDataFrame
        
    Returns:
        フィルタリング済みのDataFrame
    """
    if df.empty:
        return df.copy()
    
    return df[df["アーティスト"] != "-"].copy()


class TestArtistFilterEdgeCases:
    """アーティストフィルタリング処理のエッジケーステスト"""
    
    def test_empty_dataframe(self):
        """
        空のDataFrameに対する処理をテスト
        
        要件: 3.4
        """
        # 空のDataFrameを作成
        df_empty = pd.DataFrame({
            "アーティスト": [],
            "アーティスト(ソート用)": [],
            "曲名": [],
            "最近の歌唱": []
        })
        
        # フィルタリング処理を適用
        df_filtered = filter_hyphen_artists(df_empty)
        
        # 検証：空のDataFrameが返される
        assert df_filtered.empty, "空のDataFrameに対してフィルタリングを適用した結果が空ではありません"
        assert len(df_filtered) == 0, "空のDataFrameに対してフィルタリングを適用した結果の行数が0ではありません"
    
    def test_all_hyphen_artists(self):
        """
        すべての行がハイフンの場合をテスト
        
        要件: 3.4
        """
        # すべての行がハイフンのDataFrameを作成
        df_all_hyphen = pd.DataFrame({
            "アーティスト": ["-", "-", "-"],
            "アーティスト(ソート用)": ["-", "-", "-"],
            "曲名": ["曲1", "曲2", "曲3"],
            "最近の歌唱": ["url1", "url2", "url3"]
        })
        
        # フィルタリング処理を適用
        df_filtered = filter_hyphen_artists(df_all_hyphen)
        
        # 検証：空のDataFrameが返される
        assert df_filtered.empty, "すべての行がハイフンの場合、空のDataFrameが返されるべきです"
        assert len(df_filtered) == 0, "すべての行がハイフンの場合、行数が0であるべきです"
    
    def test_no_hyphen_artists(self):
        """
        ハイフンが存在しない場合をテスト
        
        要件: 3.4
        """
        # ハイフンが存在しないDataFrameを作成
        df_no_hyphen = pd.DataFrame({
            "アーティスト": ["アーティストA", "アーティストB", "アーティストC"],
            "アーティスト(ソート用)": ["アーティストA", "アーティストB", "アーティストC"],
            "曲名": ["曲1", "曲2", "曲3"],
            "最近の歌唱": ["url1", "url2", "url3"]
        })
        
        # フィルタリング処理を適用
        df_filtered = filter_hyphen_artists(df_no_hyphen)
        
        # 検証：元のDataFrameと同じ内容が返される
        assert len(df_filtered) == len(df_no_hyphen), \
            "ハイフンが存在しない場合、元のDataFrameと同じ行数が返されるべきです"
        assert df_filtered["アーティスト"].tolist() == df_no_hyphen["アーティスト"].tolist(), \
            "ハイフンが存在しない場合、元のDataFrameと同じ内容が返されるべきです"
    
    def test_missing_artist_column(self):
        """
        アーティスト列が存在しない場合の動作をテスト
        
        要件: 3.5
        """
        # アーティスト列が存在しないDataFrameを作成
        df_no_artist_column = pd.DataFrame({
            "曲名": ["曲1", "曲2", "曲3"],
            "最近の歌唱": ["url1", "url2", "url3"]
        })
        
        # フィルタリング処理を適用し、KeyErrorが発生することを確認
        with pytest.raises(KeyError):
            filter_hyphen_artists(df_no_artist_column)
    
    def test_mixed_hyphen_and_non_hyphen(self):
        """
        ハイフンと非ハイフンが混在する場合をテスト
        """
        # ハイフンと非ハイフンが混在するDataFrameを作成
        df_mixed = pd.DataFrame({
            "アーティスト": ["アーティストA", "-", "アーティストB", "-", "アーティストC"],
            "アーティスト(ソート用)": ["アーティストA", "-", "アーティストB", "-", "アーティストC"],
            "曲名": ["曲1", "曲2", "曲3", "曲4", "曲5"],
            "最近の歌唱": ["url1", "url2", "url3", "url4", "url5"]
        })
        
        # フィルタリング処理を適用
        df_filtered = filter_hyphen_artists(df_mixed)
        
        # 検証：ハイフンの行が除外され、非ハイフンの行が保持される
        assert len(df_filtered) == 3, "ハイフンの行が除外され、非ハイフンの行が保持されるべきです"
        assert not (df_filtered["アーティスト"] == "-").any(), \
            "フィルタリング後にハイフンの行が存在してはいけません"
        assert df_filtered["アーティスト"].tolist() == ["アーティストA", "アーティストB", "アーティストC"], \
            "非ハイフンの行が正しく保持されるべきです"
