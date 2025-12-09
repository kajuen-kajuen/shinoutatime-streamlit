"""
アプリケーション全体のカバレッジ向上のためのE2Eテスト
"""
import pytest
from streamlit.testing.v1 import AppTest
import pandas as pd
from unittest.mock import MagicMock, patch

class TestAppCoverage:
    """各ページの起動と基本動作を確認してカバレッジを向上させるテスト"""

    def test_home_page_startup(self):
        """Home.py の起動テスト"""
        at = AppTest.from_file("Home.py", default_timeout=10)
        at.run()
        assert not at.exception
        assert "しのうたタイム" in at.title[0].value

    def test_home_page_search(self):
        """Home.py の検索機能テスト"""
        # データのモック化が必要な場合はここでパッチを当てることを検討するが、
        # AppTestは別プロセスで動くため、ファイルベースのモックデータ利用が推奨される。
        # ここでは基本動作（入力してボタン押下）までを確認。
        at = AppTest.from_file("Home.py", default_timeout=10)
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
        at = AppTest.from_file("pages/01_Information.py", default_timeout=10)
        at.run()
        assert not at.exception

    def test_about_us_page(self):
        """02_About_Us.py の起動テスト"""
        at = AppTest.from_file("pages/02_About_Us.py", default_timeout=10)
        at.run()
        assert not at.exception
        
    def test_song_list_beta_page(self):
        """99_Song_List_beta.py の起動テスト"""
        at = AppTest.from_file("pages/99_Song_List_beta.py", default_timeout=10)
        at.run()
        assert not at.exception
