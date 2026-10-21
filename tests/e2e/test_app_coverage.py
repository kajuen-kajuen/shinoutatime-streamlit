"""
アプリケーション全体のカバレッジ向上のためのE2Eテスト
"""
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch

# AppTest.from_file の相対パスは、呼び出したファイル(このテスト)からの位置になるので絶対パスで渡す
ROOT = Path(__file__).resolve().parents[2]


def app_path(relative: str) -> str:
    return str(ROOT / relative)

class TestAppCoverage:
    """各ページの起動と基本動作を確認してカバレッジを向上させるテスト"""

    def test_home_page_startup(self):
        """Home.py の起動テスト"""
        at = AppTest.from_file(app_path("Home.py"), default_timeout=10)
        at.run()
        assert not at.exception
        assert "しのうたタイム" in at.title[0].value

    def test_home_page_search(self):
        """Home.py の検索機能テスト"""
        # データのモック化が必要な場合はここでパッチを当てることを検討するが、
        # AppTestは別プロセスで動くため、ファイルベースのモックデータ利用が推奨される。
        # ここでは基本動作（入力してボタン押下）までを確認。
        at = AppTest.from_file(app_path("Home.py"), default_timeout=10)
        at.run()
        
        # 検索入力
        if at.text_input:
            at.text_input[0].set_value("Test Song").run()
            
            # 検索ボタン押下（もしあれば）
            search_buttons = [b for b in at.button if b.label == "検索"]
            if search_buttons:
                search_buttons[0].click().run()
                assert not at.exception

    def test_information_page(self):
        """01_Information.py の起動テスト"""
        at = AppTest.from_file(app_path("pages/01_Information.py"), default_timeout=10)
        at.run()
        assert not at.exception

    def test_about_us_page(self):
        """02_About_Us.py の起動テスト"""
        at = AppTest.from_file(app_path("pages/02_About_Us.py"), default_timeout=10)
        at.run()
        assert not at.exception
        
    def test_song_list_beta_page(self):
        """99_Song_List_beta.py の起動テスト"""
        at = AppTest.from_file(app_path("pages/99_Song_List_beta.py"), default_timeout=10)
        at.run()
        assert not at.exception

    def test_song_list_beta_page_load_error(self):
        """99_Song_List_beta.py: 読み込みに失敗しても例外を画面に出さず、エラーを表示する"""
        from src.exceptions.errors import DataLoadError

        st.cache_data.clear()  # ほかのテストで読み込んだ結果を使わない
        with patch(
            "src.repositories.song_list_repository.SongListRepository.load_as_dataframe",
            side_effect=DataLoadError("data/V_SONG_LIST.TSV", "列が足りません"),
        ):
            at = AppTest.from_file(app_path("pages/99_Song_List_beta.py"), default_timeout=10)
            at.run()
        st.cache_data.clear()

        assert not at.exception
        assert any("楽曲リストを読み込めませんでした" in e.value for e in at.error)
        assert any("楽曲データが読み込めませんでした" in w.value for w in at.warning)

    def test_song_list_beta_page_empty(self):
        """99_Song_List_beta.py: ファイルが無い(空の DataFrame)ときは、空の表ではなく警告を出す"""
        st.cache_data.clear()
        with patch(
            "src.repositories.song_list_repository.SongListRepository.load_as_dataframe",
            return_value=pd.DataFrame(),
        ):
            at = AppTest.from_file(app_path("pages/99_Song_List_beta.py"), default_timeout=10)
            at.run()
        st.cache_data.clear()

        assert not at.exception
        assert not at.error
        assert any("楽曲データが読み込めませんでした" in w.value for w in at.warning)
