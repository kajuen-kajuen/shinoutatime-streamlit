"""
HomePageクラスの単体テスト(データは v2 の歌唱の一覧。すべて架空)
"""
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from src.config.settings import Config
from src.core.views import build_performance_view
from src.exceptions.errors import DataLoadError
from src.ui.pages.home_page import HomePage, TABLE_COLUMNS, build_table, data_as_of, filter_view
from tests.unit.v2.conftest import content, make_dataset


class MockSessionState(dict):
    """SessionStateのモック（属性アクセスと辞書アクセス両対応）"""
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture
def view():
    """配信1本(3曲)と、尺付きの歌唱・記号を含む曲名とアーティスト"""
    dataset = make_dataset(
        contents=[content("yt:AAAAAAAAAAA", "2025-05-01", "【歌枠】夜のうた", start_time="20:00", kind="歌枠")],
        artists=[
            {"artist_id": "a0001", "name": "テストバンド", "sort_name": "てすとばんど"},
            {"artist_id": "a0002", "name": "A & <B>", "sort_name": ""},
        ],
        songs=[
            {"song_id": "s0001", "title": "怪獣の歌", "sort_title": "かいじゅうのうた", "artist_id": "a0001"},
            {"song_id": "s0002", "title": "<Song>", "artist_id": "a0002"},
            {"song_id": "s0003", "title": "Blue Sky", "artist_id": "a0001"},
        ],
        performances=[
            {"content_id": "yt:AAAAAAAAAAA", "seq": "10", "start": "0:05:00", "song_id": "s0001"},
            {"content_id": "yt:AAAAAAAAAAA", "seq": "20", "start": "0:10:00", "song_id": "s0002"},
            {"content_id": "yt:AAAAAAAAAAA", "seq": "30", "start": "0:15:00", "song_id": "s0003", "part": "1chorus"},
        ],
    )
    return build_performance_view(dataset)


class TestFilterView:
    def test_empty_query_returns_all(self, view):
        assert len(filter_view(view, "", True)) == 3
        assert len(filter_view(view, "   ", True)) == 3

    def test_matches_reading_and_width(self, view):
        assert list(filter_view(view, "カイジュウ", True)["title"]) == ["怪獣の歌"]
        assert list(filter_view(view, "ＢＬＵＥ", True)["title"]) == ["Blue Sky"]

    def test_live_title_only_when_included(self, view):
        assert len(filter_view(view, "夜のうた", True)) == 3
        assert filter_view(view, "夜のうた", False).empty


class TestDataAsOf:
    def test_latest_date_and_count(self, view):
        assert data_as_of(view) == "データは 2025/05/01 の配信まで(歌唱 3 件)"

    def test_uses_max_date_not_last_row(self):
        dates = pd.DataFrame({"date": ["2025-05-01", "2026-10-20", "2025-12-31"] * 400})
        assert data_as_of(dates) == "データは 2026/10/20 の配信まで(歌唱 1,200 件)"

    def test_empty_view_is_blank(self, view):
        assert data_as_of(view.iloc[0:0]) == ""


class TestBuildTable:
    def test_columns_and_values(self, view):
        table = build_table(view)
        assert list(table.columns) == TABLE_COLUMNS
        row = table.iloc[2]
        assert row["配信日"] == "2025/05/01"
        assert row["No."] == "3"
        assert row["曲名"] == "Blue Sky(1chorus)"
        assert row["種類"] == "配信"
        assert row["リンク"] == (
            '<a href="https://www.youtube.com/watch?v=AAAAAAAAAAA&amp;t=900s" target="_blank" rel="noopener">YouTubeへ👻</a>'
        )

    def test_artist_is_escaped_and_title_is_left_raw(self, view):
        row = build_table(view).iloc[1]
        assert row["アーティスト"] == '<div class="artist-cell">A &amp; &lt;B&gt;</div>'
        # 曲名はそのまま渡し、render_results_table 側でエスケープする
        assert row["曲名"] == "<Song>"


class TestHomePage:
    """HomePageクラスのテスト"""

    @pytest.fixture
    def mock_config(self):
        """Configのモック"""
        config = MagicMock(spec=Config)
        config.css_file_path = "style.css"
        config.initial_display_limit = 25
        config.display_increment = 25
        return config

    @pytest.fixture
    def home_page(self, mock_config):
        """HomePageインスタンスのフィクスチャ"""
        with patch('src.ui.pages.home_page.Config.from_env', return_value=mock_config):
            return HomePage()

    @patch('src.ui.pages.home_page.st')
    @patch('src.ui.pages.home_page.load_performance_view')
    @patch('src.ui.pages.home_page.display_footer')
    def test_run_success(self, mock_footer, mock_load, mock_st, home_page, view):
        """正常系の実行テスト"""
        mock_st.session_state = MockSessionState()
        mock_load.return_value = view
        home_page._load_css = MagicMock()
        home_page._render_header = MagicMock()
        home_page._handle_search_and_display = MagicMock()

        home_page.run()

        home_page._load_css.assert_called_once()
        home_page._render_header.assert_called_once()
        home_page._handle_search_and_display.assert_called_once_with(view)
        mock_footer.assert_called_once()

    @patch('src.ui.pages.home_page.st')
    @patch('src.ui.pages.home_page.load_performance_view')
    @patch('src.ui.pages.home_page.display_footer')
    def test_run_failure(self, mock_footer, mock_load, mock_st, home_page):
        """データ読み込み失敗時は、エラーを出して検索と表は出さない"""
        mock_st.session_state = MockSessionState()
        mock_load.side_effect = DataLoadError("data/v2", "読み込めません")
        home_page._load_css = MagicMock()
        home_page._render_header = MagicMock()
        home_page._handle_error = MagicMock()
        home_page._handle_search_and_display = MagicMock()

        home_page.run()

        home_page._handle_error.assert_called_once()
        home_page._handle_search_and_display.assert_not_called()
        mock_footer.assert_called_once()

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
    def test_handle_search_and_display_initial(self, mock_st, mock_render_form, home_page, view):
        """初期表示: 全件を出す"""
        mock_st.session_state = MockSessionState()
        mock_render_form.return_value = ("", True, False)
        home_page._render_results = MagicMock()

        home_page._handle_search_and_display(view)

        assert mock_st.session_state.search_query == ""
        assert mock_st.session_state.display_limit == home_page.config.initial_display_limit
        assert len(home_page._render_results.call_args.args[0]) == 3
        mock_st.write.assert_called_once_with("検索キーワードが入力されていません。全件表示します。")

    @patch('src.ui.pages.home_page.render_search_form')
    @patch('src.ui.pages.home_page.st')
    def test_search_button_saves_query_and_resets_limit(self, mock_st, mock_render_form, home_page, view):
        """検索ボタン: 検索語を保存し、表示件数を戻して絞った結果を出す"""
        mock_st.session_state = MockSessionState(display_limit=75)
        mock_render_form.return_value = ("かいじゅう", True, True)
        home_page._render_results = MagicMock()

        home_page._handle_search_and_display(view)

        assert mock_st.session_state.search_query == "かいじゅう"
        assert mock_st.session_state.display_limit == 25
        assert list(home_page._render_results.call_args.args[0]["title"]) == ["怪獣の歌"]
        mock_st.write.assert_called_once_with("「かいじゅう」で検索した結果: 1件")

    @patch('src.ui.pages.home_page.render_search_form')
    @patch('src.ui.pages.home_page.st')
    def test_saved_query_is_used_without_button(self, mock_st, mock_render_form, home_page, view):
        """検索済みのあと(さらに表示など)は、保存した検索語で絞り続ける"""
        mock_st.session_state = MockSessionState(search_query="blue", include_live_title=False, display_limit=50)
        mock_render_form.return_value = ("書きかけ", False, False)
        home_page._render_results = MagicMock()

        home_page._handle_search_and_display(view)

        assert list(home_page._render_results.call_args.args[0]["title"]) == ["Blue Sky"]
        assert mock_st.session_state.display_limit == 50

    @patch('src.ui.pages.home_page.render_results_table')
    @patch('src.ui.pages.home_page.render_pagination')
    @patch('src.ui.pages.home_page.st')
    def test_render_results(self, mock_st, mock_pagination, mock_results_table, home_page, view):
        """表示件数だけ表に出し、html_columns でアーティストとリンクを渡す"""
        mock_st.session_state = MockSessionState(display_limit=2)
        mock_pagination.return_value = None

        home_page._render_results(view)

        table, columns, _headers = mock_results_table.call_args.args
        assert len(table) == 2
        assert columns == TABLE_COLUMNS
        assert mock_results_table.call_args.kwargs['html_columns'] == {'アーティスト', 'リンク'}
        assert mock_pagination.call_args.kwargs['total_count'] == 3
        mock_st.rerun.assert_not_called()

    @patch('src.ui.pages.home_page.render_results_table')
    @patch('src.ui.pages.home_page.render_pagination')
    @patch('src.ui.pages.home_page.st')
    def test_render_results_pagination_click(self, mock_st, mock_pagination, mock_results_table, home_page, view):
        """ページネーションボタン押下時のテスト"""
        mock_st.session_state = MockSessionState(display_limit=25)
        mock_pagination.return_value = 50  # ボタン押下で新しいリミットが返る

        home_page._render_results(view)

        assert mock_st.session_state.display_limit == 50
        mock_st.rerun.assert_called_once()
