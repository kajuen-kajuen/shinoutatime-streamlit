"""
ページの準備(src/ui/page_setup.py)の単体テスト
"""
from unittest.mock import MagicMock, patch

import pytest

from src.config.settings import Config
from src.ui.page_setup import SITE_HEADING, load_css, page_tab_title, setup_page


@pytest.fixture
def config(tmp_path):
    css = tmp_path / "style.css"
    css.write_text("body { color: red; }", encoding="utf-8")
    return Config(css_file_path=str(css))


class TestPageTabTitle:
    def test_home_is_site_name(self, config):
        assert page_tab_title(config, None) == "しのうたタイム"

    def test_other_page_is_page_and_site(self, config):
        assert page_tab_title(config, "Information") == "Information - しのうたタイム"


class TestLoadCss:
    @patch("src.ui.page_setup.st")
    def test_reads_css_into_style_tag(self, mock_st, config):
        load_css(config.css_file_path)
        args, kwargs = mock_st.markdown.call_args
        assert args[0] == "<style>body { color: red; }</style>"
        assert kwargs["unsafe_allow_html"] is True

    @patch("src.ui.page_setup.st")
    def test_missing_css_shows_error(self, mock_st, tmp_path):
        load_css(str(tmp_path / "none.css"))
        mock_st.markdown.assert_not_called()
        assert "見つかりません" in mock_st.error.call_args.args[0]


class TestSetupPage:
    @patch("src.ui.page_setup.st")
    def test_home(self, mock_st, config):
        with patch("src.ui.page_setup.Config.from_env", return_value=config):
            assert setup_page() is config

        mock_st.set_page_config.assert_called_once_with(
            page_title="しのうたタイム", page_icon=config.page_icon, layout=config.layout)
        mock_st.title.assert_called_once_with(SITE_HEADING)
        mock_st.header.assert_not_called()  # Home はページ名を出さない

    @patch("src.ui.page_setup.st")
    def test_other_page_has_page_name_with_icon(self, mock_st, config):
        with patch("src.ui.page_setup.Config.from_env", return_value=config):
            setup_page("Information", "📢")

        assert mock_st.set_page_config.call_args.kwargs["page_title"] == "Information - しのうたタイム"
        mock_st.title.assert_called_once_with(SITE_HEADING)
        mock_st.header.assert_called_once_with("📢 Information")

    @patch("src.ui.page_setup.st")
    def test_page_config_comes_first(self, mock_st, config):
        """set_page_config は最初の Streamlit の命令でなければならない"""
        with patch("src.ui.page_setup.Config.from_env", return_value=config):
            setup_page("Information", "📢")
        assert mock_st.method_calls[0][0] == "set_page_config"
