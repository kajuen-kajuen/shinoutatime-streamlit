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

    def test_home_page_search_no_hit(self):
        """Home.py: 当たらない検索語でも例外を出さず、0件と表示する"""
        at = AppTest.from_file(app_path("Home.py"), default_timeout=30)
        at.run()

        at.text_input[0].set_value("存在しない曲名のテスト").run()
        [b for b in at.button if b.label == "検索"][0].click().run()

        assert not at.exception
        assert any("検索した結果: 0件" in m.value for m in at.markdown)

    def test_home_page_load_error(self, tmp_path, monkeypatch):
        """Home.py: データを読めないときは、例外を画面に出さずエラーを表示する"""
        monkeypatch.setenv("SHINOUTA_V2_DATA_DIR", str(tmp_path / "nope"))
        st.cache_data.clear()
        at = AppTest.from_file(app_path("Home.py"), default_timeout=30)
        at.run()
        st.cache_data.clear()

        assert not at.exception
        assert any("データの読み込みまたは処理中にエラーが発生しました" in e.value for e in at.error)
        assert not [m for m in at.markdown if "<table" in m.value]

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
        """99_Song_List_beta.py: 本物の data/v2 を読み、最初は25曲を出す"""
        at = AppTest.from_file(app_path("pages/99_Song_List_beta.py"), default_timeout=30)
        at.run()
        assert not at.exception
        table = next(m.value for m in at.markdown if "<table" in m.value)
        assert table.count("<tr>") == 25
        assert any(m.value.startswith("**全 ") for m in at.markdown)

    def test_song_list_beta_page_pagination(self):
        """99_Song_List_beta.py: 「さらに表示」で表示件数が増える"""
        at = AppTest.from_file(app_path("pages/99_Song_List_beta.py"), default_timeout=30)
        at.run()

        [b for b in at.button if b.label.startswith("さらに")][0].click().run()

        assert not at.exception
        assert at.session_state.song_list_limit == 50
        table = next(m.value for m in at.markdown if "<table" in m.value)
        assert table.count("<tr>") == 50

    def test_song_list_beta_page_load_error(self, tmp_path, monkeypatch):
        """99_Song_List_beta.py: 読み込みに失敗しても例外を画面に出さず、エラーを表示する"""
        monkeypatch.setenv("SHINOUTA_V2_DATA_DIR", str(tmp_path / "nope"))
        st.cache_data.clear()  # ほかのテストで読み込んだ結果を使わない
        at = AppTest.from_file(app_path("pages/99_Song_List_beta.py"), default_timeout=30)
        at.run()
        st.cache_data.clear()

        assert not at.exception
        assert any("楽曲リストを読み込めませんでした" in e.value for e in at.error)
        assert any("楽曲データが読み込めませんでした" in w.value for w in at.warning)

    def test_song_list_beta_page_empty(self, tmp_path, monkeypatch):
        """99_Song_List_beta.py: データが空(TSV が無い)ときは、空の表ではなく警告を出す"""
        monkeypatch.setenv("SHINOUTA_V2_DATA_DIR", str(tmp_path))
        st.cache_data.clear()
        at = AppTest.from_file(app_path("pages/99_Song_List_beta.py"), default_timeout=30)
        at.run()
        st.cache_data.clear()

        assert not at.exception
        assert not at.error
        assert any("楽曲データが読み込めませんでした" in w.value for w in at.warning)
