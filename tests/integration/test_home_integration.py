"""
Home.pyの統合テスト

Streamlitアプリのデータ処理部分をテストします。
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# srcモジュールをインポートできるようにする
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services.data_service import DataService
from src.core.data_pipeline import DataPipeline
from src.services.search_service import SearchService
from src.config.settings import Config
from src.ui.components import render_search_form, render_results_table, render_pagination


class TestHomeIntegration:
    """Home.pyの統合テスト"""

    @pytest.fixture
    def config(self):
        """設定オブジェクトのフィクスチャ"""
        config = Config()
        config.enable_cache = True
        return config

    @pytest.fixture
    def sample_data(self):
        """サンプルデータのフィクスチャ"""
        return pd.DataFrame({
            '曲名': ['曲A', '曲B'],
            'アーティスト': ['アーティストA', 'アーティストB'],
            'ライブタイトル': ['ライブ1', 'ライブ2'],
            'ライブ配信日': ['2023-01-01', '2023-01-02'],
            '曲目': [1, 2],
            'YouTubeタイムスタンプ付きURL': ['https://example.com/1', 'https://example.com/2']
        })

    def test_data_pipeline_execution_with_cache(self, config, sample_data):
        """DataPipelineの実行とキャッシュ動作をテスト"""
        with patch('src.services.data_service.DataService') as mock_data_service_class:
            mock_data_service = MagicMock()
            mock_data_service_class.return_value = mock_data_service
            mock_data_service.load_lives_data.return_value = sample_data
            mock_data_service.load_songs_data.return_value = sample_data
            mock_data_service.merge_data.return_value = sample_data

            data_service = DataService(config)
            pipeline = DataPipeline(data_service, config)

            # 初回実行
            result1 = pipeline.execute()
            assert result1 is not None
            assert len(result1) > 0

            # キャッシュから2回目実行
            result2 = pipeline.execute()
            assert result2 is not None
            assert result1 is result2  # 同じオブジェクトを返す

            # キャッシュクリア後
            pipeline.clear_cache()
            result3 = pipeline.execute()
            assert result3 is not None
            # キャッシュがクリアされたので新しいオブジェクト

    def test_search_service_integration(self, sample_data):
        """SearchServiceの統合テスト"""
        search_service = SearchService()

        # 曲名検索
        results = search_service.search(sample_data, '曲A', ['曲名'], case_sensitive=False)
        assert len(results) == 1
        assert results.iloc[0]['曲名'] == '曲A'

        # アーティスト検索
        results = search_service.search(sample_data, 'アーティストB', ['アーティスト'], case_sensitive=False)
        assert len(results) == 1
        assert results.iloc[0]['アーティスト'] == 'アーティストB'

        # ライブタイトル検索
        results = search_service.search(sample_data, 'ライブ1', ['ライブタイトル'], case_sensitive=False)
        assert len(results) == 1
        assert results.iloc[0]['ライブタイトル'] == 'ライブ1'

    @patch('streamlit.text_input')
    @patch('streamlit.checkbox')
    @patch('streamlit.button')
    def test_render_search_form(self, mock_button, mock_checkbox, mock_text_input):
        """render_search_formのテスト"""
        mock_text_input.return_value = 'テストクエリ'
        mock_checkbox.return_value = True
        mock_button.return_value = True

        query, include_title, clicked = render_search_form('デフォルト', True)

        assert query == 'テストクエリ'
        assert include_title is True
        assert clicked is True

        mock_text_input.assert_called_once_with(
            "キーワード検索（曲名、アーティスト）",
            value='デフォルト',
            key="search_input_box",
            placeholder="ここにキーワードを入力",
        )
        mock_checkbox.assert_called_once_with(
            "検索対象にライブ配信タイトルを含める",
            value=True,
            key="include_live_title_checkbox",
        )
        mock_button.assert_called_once_with("検索")

    @patch('streamlit.write')
    def test_render_results_table(self, mock_write, sample_data):
        """render_results_tableのテスト"""
        columns = ['曲名', 'アーティスト']
        headers = {'曲名': '曲名', 'アーティスト': 'アーティスト'}

        render_results_table(sample_data, columns, headers)

        # HTMLテーブルが生成され、unsafe_allow_html=Trueで表示されることを確認
        args, kwargs = mock_write.call_args
        assert kwargs.get('unsafe_allow_html') is True
        assert '<table' in args[0]
        assert '曲名' in args[0]

    @patch('streamlit.button')
    @patch('streamlit.info')
    def test_render_pagination(self, mock_info, mock_button):
        """render_paginationのテスト"""
        # さらに表示する場合
        mock_button.return_value = True
        new_limit = render_pagination(100, 25, 25)
        assert new_limit == 50

        # 全件表示済みの場合
        mock_button.return_value = False
        new_limit = render_pagination(25, 25, 25)
        assert new_limit is None
        mock_info.assert_called_with("全ての25件が表示されています。")

    def test_load_and_process_data_caching(self, config, sample_data):
        """load_and_process_dataのキャッシュ動作をテスト"""
        with patch('src.services.data_service.DataService') as mock_data_service_class, \
             patch('src.core.data_pipeline.DataPipeline') as mock_pipeline_class:

            mock_data_service = MagicMock()
            mock_data_service_class.return_value = mock_data_service
            mock_pipeline = MagicMock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.execute.return_value = sample_data

            # 初回実行
            from Home import load_and_process_data
            result1 = load_and_process_data('lives.tsv', 'songs.tsv', True)
            assert result1 is not None

            # 同じパラメータで2回目実行（キャッシュから）
            result2 = load_and_process_data('lives.tsv', 'songs.tsv', True)
            assert result2 is not None