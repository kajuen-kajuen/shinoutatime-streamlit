"""
アーティストフィルタリング処理のプロパティベーステスト

pages/99_Song_List_beta.pyのアーティスト名「-」フィルタリング処理の
普遍的な性質を多数のランダム入力で検証します。
"""

import pytest
import pandas as pd
from hypothesis import given, strategies as st, settings


# カスタム戦略：楽曲データを含むDataFrameを生成
@st.composite
def song_dataframe_strategy(draw):
    """
    楽曲データを含むDataFrameを生成する戦略
    
    アーティスト名には「-」（ハイフン）と通常のアーティスト名の両方を含む
    """
    # 行数を生成（0〜100行）
    num_rows = draw(st.integers(min_value=0, max_value=100))
    
    if num_rows == 0:
        # 空のDataFrameを返す
        return pd.DataFrame({
            "アーティスト": [],
            "アーティスト(ソート用)": [],
            "曲名": [],
            "最近の歌唱": []
        })
    
    # アーティスト名の生成（「-」を含む）
    artist_strategy = st.one_of(
        st.just("-"),  # ハイフン
        st.text(min_size=1, max_size=50).filter(lambda x: x != "-" and x.strip() != "")  # 通常のアーティスト名
    )
    
    # 各行のデータを生成
    artists = [draw(artist_strategy) for _ in range(num_rows)]
    artists_sort = artists.copy()  # ソート用も同じ値を使用
    song_names = [draw(st.text(min_size=1, max_size=100)) for _ in range(num_rows)]
    urls = [f"https://youtube.com/watch?v={draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=6, max_size=11))}" 
            for _ in range(num_rows)]
    
    return pd.DataFrame({
        "アーティスト": artists,
        "アーティスト(ソート用)": artists_sort,
        "曲名": song_names,
        "最近の歌唱": urls
    })


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


class TestArtistFilterProperties:
    """アーティストフィルタリング処理のプロパティベーステスト"""
    
    @given(song_dataframe_strategy())
    @settings(max_examples=100, deadline=5000)
    def test_property_1_hyphen_artists_excluded(self, df):
        """
        Feature: artist-filter-hyphen, Property 1: ハイフンアーティストの除外
        
        任意の楽曲データを含むDataFrameに対して、フィルタリング処理を適用した後、
        アーティスト名が「-」である行は存在してはならない
        
        **検証: 要件 1.1**
        """
        # フィルタリング処理を適用
        df_filtered = filter_hyphen_artists(df)
        
        # プロパティ検証：アーティスト名が「-」の行が存在しない
        if not df_filtered.empty:
            assert not (df_filtered["アーティスト"] == "-").any(), \
                "フィルタリング後にアーティスト名が「-」の行が存在します"
    
    @given(song_dataframe_strategy())
    @settings(max_examples=100, deadline=5000)
    def test_property_2_non_hyphen_artists_preserved(self, df):
        """
        Feature: artist-filter-hyphen, Property 2: 非ハイフンアーティストの保持
        
        任意の楽曲データを含むDataFrameに対して、フィルタリング処理を適用した後、
        アーティスト名が「-」以外である行はすべて保持されなければならない
        
        **検証: 要件 1.5**
        """
        # 元のDataFrameで「-」以外のアーティスト名を持つ行を特定
        non_hyphen_rows = df[df["アーティスト"] != "-"]
        
        # フィルタリング処理を適用
        df_filtered = filter_hyphen_artists(df)
        
        # プロパティ検証：「-」以外のアーティスト名を持つ行がすべて保持されている
        assert len(df_filtered) == len(non_hyphen_rows), \
            f"フィルタリング後の行数が期待値と一致しません。期待: {len(non_hyphen_rows)}, 実際: {len(df_filtered)}"
        
        # プロパティ検証：フィルタリング後のすべての行が元のDataFrameに存在する
        if not df_filtered.empty:
            for idx, row in df_filtered.iterrows():
                assert row["アーティスト"] != "-", \
                    "フィルタリング後にハイフンアーティストが含まれています"
    
    @given(song_dataframe_strategy())
    @settings(max_examples=100, deadline=5000)
    def test_property_3_filtered_count_accuracy(self, df):
        """
        Feature: artist-filter-hyphen, Property 3: フィルタリング後の件数の正確性
        
        任意の楽曲データを含むDataFrameに対して、フィルタリング処理を適用した後、
        結果のDataFrameの行数は、元のDataFrameからアーティスト名が「-」である行を
        除いた行数と等しくなければならない
        
        **検証: 要件 1.4**
        """
        # 元のDataFrameでアーティスト名が「-」の行数をカウント
        hyphen_count = (df["アーティスト"] == "-").sum()
        expected_count = len(df) - hyphen_count
        
        # フィルタリング処理を適用
        df_filtered = filter_hyphen_artists(df)
        
        # プロパティ検証：フィルタリング後の行数が期待値と一致
        assert len(df_filtered) == expected_count, \
            f"フィルタリング後の行数が期待値と一致しません。期待: {expected_count}, 実際: {len(df_filtered)}"
