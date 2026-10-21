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

    @patch('streamlit.form')
    @patch('streamlit.text_input')
    @patch('streamlit.checkbox')
    @patch('streamlit.form_submit_button')
    def test_render_search_form(self, mock_button, mock_checkbox, mock_text_input, mock_form):
        """render_search_formのテスト(st.form の中に置き、Enter キーでも送信される)"""
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
        mock_form.assert_called_once_with("search_form", border=False)

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

    @patch('streamlit.write')
    def test_render_results_table_escapes_data(self, mock_write):
        """データ由来のセルはエスケープし、html_columns の列だけそのまま出す"""
        df = pd.DataFrame({
            '曲名': ['<b>Rock & Roll</b>', None],
            'リンク': ['<a href="https://example.com/1">YouTubeへ👻</a>', ''],
        })

        render_results_table(df, ['曲名', 'リンク'], {'曲名': '曲<名>', 'リンク': 'リンク'},
                             html_columns={'リンク'})

        html_out = mock_write.call_args.args[0]
        assert '&lt;b&gt;Rock &amp; Roll&lt;/b&gt;' in html_out
        assert '<b>' not in html_out
        assert '<a href="https://example.com/1">YouTubeへ👻</a>' in html_out
        assert '<th>曲&lt;名&gt;</th>' in html_out
        # 欠損は "None" や "nan" ではなく空
        assert '<tr><td></td><td></td></tr>' in html_out
        assert '<table border="1" class="dataframe">' in html_out
        assert '<tr style="text-align: left;">' in html_out

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

    def test_v2_data_is_cached(self, tmp_path, monkeypatch):
        """画面のデータは st.cache_data で、2回読んでも集計は1回だけ動く(データが変わらない限り)"""
        from src.repositories.table_repository import TableRepository
        from src.ui import v2_data
        from tests.unit.v2.conftest import content, make_dataset

        TableRepository(str(tmp_path)).save(make_dataset(
            contents=[content("yt:AAAAAAAAAAA", "2025-05-01")],
            artists=[{"artist_id": "a0001", "name": "テストバンド"}],
            songs=[{"song_id": "s0001", "title": "曲A", "artist_id": "a0001"}],
            performances=[{"content_id": "yt:AAAAAAAAAAA", "seq": "10", "song_id": "s0001"}],
        ))
        monkeypatch.setenv("SHINOUTA_V2_DATA_DIR", str(tmp_path))

        # v2_data が import した名前にパッチを当てる(src.core.views 側では効かない)
        with patch('src.ui.v2_data.build_performance_view', wraps=v2_data.build_performance_view) as spy:
            v2_data._load.clear()
            try:
                view = v2_data.load_performance_view()
                stats = v2_data.load_song_stats()
            finally:
                v2_data._load.clear()  # ほかのテストに結果を残さない

        assert len(view) == 1
        assert list(stats["title"]) == ["曲A"]
        spy.assert_called_once()