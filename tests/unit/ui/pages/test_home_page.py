"""
HomePageクラスの単体テスト
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import streamlit as st

# srcモジュールをインポートできるようにする
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from src.ui.pages.home_page import HomePage
from src.config.settings import Config

class MockSessionState(dict):
    """SessionStateのモック（属性アクセスと辞書アクセス両対応）"""
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")
    
    def __setattr__(self, key, value):
        self[key] = value

class TestHomePage:
    """HomePageクラスのテスト"""

    @pytest.fixture
    def mock_config(self):
        """Configのモック"""
        config = MagicMock(spec=Config)
        config.page_title = "Test Title"
        config.page_icon = "🧪"
        config.layout = "wide"
        config.css_file_path = "style.css"
        config.lives_file_path = "lives.tsv"
        config.songs_file_path = "songs.tsv"
        config.enable_cache = True
        config.initial_display_limit = 25
        config.display_increment = 25
        return config

    @pytest.fixture
    def mock_search_service(self):
        """SearchServiceのモック"""
        return MagicMock()

    @pytest.fixture
    def home_page(self, mock_config, mock_search_service):
        """HomePageインスタンスのフィクスチャ"""
        with patch('src.ui.pages.home_page.Config.from_env', return_value=mock_config), \
             patch('src.ui.pages.home_page.SearchService', return_value=mock_search_service):
            page = HomePage()
            return page

    @pytest.fixture
    def sample_df(self):
        """サンプルデータ"""
        return pd.DataFrame({
            '曲名': ['Song A', 'Song B'],
            'アーティスト': ['Artist A', 'Artist B'],
            'ライブタイトル': ['Live 1', 'Live 2'],
            'YouTubeタイムスタンプ付きURL': ['http://url1', 'http://url2']
        })

    def test_init(self, home_page):
        """初期化のテスト"""
        assert home_page.config is not None
        assert home_page.search_service is not None

    @patch('src.ui.pages.home_page.st')
    @patch('src.ui.pages.home_page.load_and_process_data')
    @patch('src.ui.pages.home_page.display_footer')
    def test_run_success(self, mock_footer, mock_load_data, mock_st, home_page, sample_df):
        """正常系の実行テスト"""
        # Session Stateのモック
        mock_st.session_state = MockSessionState()
        
        # セットアップ
        mock_load_data.return_value = sample_df
        # メソッドのモック化（privateメソッドの呼び出し確認のため）
        home_page._load_css = MagicMock()
        home_page._render_header = MagicMock()
        home_page._handle_search_and_display = MagicMock()

        # 実行
        home_page.run()

        # 検証
        home_page._load_css.assert_called_once()
        home_page._render_header.assert_called_once()
        mock_load_data.assert_called_once_with(
            home_page.config.lives_file_path,
            home_page.config.songs_file_path,
            home_page.config.enable_cache
        )
        home_page._handle_search_and_display.assert_called_once_with(sample_df)
        mock_footer.assert_called_once()

    @patch('src.ui.pages.home_page.st')
    @patch('src.ui.pages.home_page.load_and_process_data')
    def test_run_failure(self, mock_load_data, mock_st, home_page):
        """データ読み込み失敗時のテスト"""
        # Session Stateのモック
        mock_st.session_state = MockSessionState()
        
        # セットアップ
        mock_load_data.return_value = None
        home_page._load_css = MagicMock()
        home_page._render_header = MagicMock()
        home_page._handle_error = MagicMock()

        # 実行
        home_page.run()

        # 検証
        home_page._handle_error.assert_called_once()

    @patch('builtins.open')
    @patch('src.ui.pages.home_page.st')
    def test_load_css_success(self, mock_st, mock_open, home_page):
        """CSS読み込み成功テスト"""
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "body { color: red; }"
        mock_open.return_value = mock_file

        home_page._load_css()

        mock_st.markdown.assert_called_once()
        args, kwargs = mock_st.markdown.call_args
        assert "<style>body { color: red; }</style>" in args[0]

    @patch('src.ui.pages.home_page.render_search_form')
    @patch('src.ui.pages.home_page.st')
    def test_handle_search_and_display_initial(
        self, mock_st, mock_render_form, home_page, sample_df
    ):
        """検索フォーム初期表示テスト"""
        # Session Stateのモック
        mock_st.session_state = MockSessionState()
        
        # 検索フォームの戻り値 (query, include_title, clicked)
        mock_render_form.return_value = ("", True, False)
        
        # 内部メソッドのモック
        home_page._render_results = MagicMock()

        # 実行
        home_page._handle_search_and_display(sample_df)

        # 検証
        assert mock_st.session_state.search_query == ""
        assert mock_st.session_state.display_limit == home_page.config.initial_display_limit
        home_page._render_results.assert_called_once()

    @patch('src.ui.pages.home_page.render_search_form')
    @patch('src.ui.pages.home_page.st')
    def test_perform_search(self, mock_st, mock_render_form, home_page, sample_df):
        """検索実行テスト"""
        # Session Stateのモック
        mock_st.session_state = MockSessionState()
        
        # 検索ボタン押下状態
        mock_render_form.return_value = ("Query", True, True)
        
        home_page.search_service.search.return_value = sample_df.iloc[[0]]
        home_page._render_results = MagicMock()

        # 実行
        home_page._handle_search_and_display(sample_df)

        # 検証
        assert mock_st.session_state.search_query == "Query"
        home_page.search_service.search.assert_called_once()
        home_page._render_results.assert_called_once()
        
    @patch('src.ui.pages.home_page.render_results_table')
    @patch('src.ui.pages.home_page.render_pagination')
    @patch('src.ui.pages.home_page.st')
    def test_render_results(self, mock_st, mock_pagination, mock_results_table, home_page, sample_df):
        """結果表示テスト"""
        mock_st.session_state = MockSessionState()
        mock_st.session_state.display_limit = 25
        
        mock_pagination.return_value = None  # ページネーションボタン押下なし

        home_page._render_results(sample_df)

        mock_results_table.assert_called_once()
        mock_pagination.assert_called_once()
        mock_st.rerun.assert_not_called()

    @patch('src.ui.pages.home_page.render_results_table')
    @patch('src.ui.pages.home_page.render_pagination')
    @patch('src.ui.pages.home_page.st')
    def test_render_results_pagination_click(self, mock_st, mock_pagination, mock_results_table, home_page, sample_df):
        """ページネーションボタン押下時のテスト"""
        mock_st.session_state = MockSessionState()
        mock_st.session_state.display_limit = 25
        
        mock_pagination.return_value = 50  # ボタン押下で新しいリミットが返る

        home_page._render_results(sample_df)

        assert mock_st.session_state.display_limit == 50
        mock_st.rerun.assert_called_once()
