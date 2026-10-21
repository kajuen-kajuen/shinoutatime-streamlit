"""
E2E tests for the Shinoutatime Streamlit app using AppTest.

本物の data/v2/ を読む。件数は取り込みのたびに変わるので、「1件以上」「全件より少ない」で確かめる。
"""
import re

import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest

# AppTest.from_file の相対パスは、呼び出したファイル(このテスト)からの位置になるので絶対パスで渡す
HOME_SCRIPT = str(Path(__file__).resolve().parents[2] / "Home.py")


def result_count(app) -> int:
    """「「…」で検索した結果: N件」の N"""
    for markdown in app.markdown:
        m = re.search(r"で検索した結果: (\d+)件", markdown.value)
        if m:
            return int(m.group(1))
    raise AssertionError("検索結果の件数が表示されていません")


def table_html(app) -> str:
    return next(m.value for m in app.markdown if "<table" in m.value)


class TestAppE2E:
    """E2E tests for the main application"""

    @pytest.fixture
    def app(self):
        """Fixture to initialize the app"""
        at = AppTest.from_file(HOME_SCRIPT, default_timeout=30)
        at.run()
        return at

    def search(self, app, query: str):
        app.text_input[0].set_value(query).run()
        [b for b in app.button if b.label == "検索"][0].click().run()

    def test_app_startup(self, app):
        """起動し、v2 の一覧の表(配信日・No.・曲名・アーティスト・種類・リンク)を出す"""
        assert not app.exception
        assert "しのうたタイム" in app.title[0].value
        html = table_html(app)
        for header in ["配信日", "No.", "曲名", "アーティスト", "種類", "リンク"]:
            assert f"<th>{header}</th>" in html
        assert html.count("<tr>") == 25  # 最初は25件
        # データの時点(本物のデータなので日付と件数は決め打ちしない)
        assert any(re.fullmatch(r"データは \d{4}/\d{2}/\d{2} の配信まで\(歌唱 [\d,]+ 件\)", c.value)
                   for c in app.caption)

    def test_search_functionality(self, app):
        """曲名で検索すると、全件より少ない1件以上に絞られる"""
        self.search(app, "怪獣の花唄")

        assert not app.exception
        assert app.session_state.search_query == "怪獣の花唄"
        assert 1 <= result_count(app) < 2000
        assert "怪獣の花唄" in table_html(app)

    def test_search_by_reading(self, app):
        """読み(かな)でも見つかる"""
        self.search(app, "かいじゅうのはなうた")

        assert result_count(app) >= 1
        assert "怪獣の花唄" in table_html(app)

    def test_pagination(self, app):
        """「さらに表示」で表示件数が増える"""
        assert app.session_state.display_limit == 25

        more = [b for b in app.button if b.label.startswith("さらに")]
        more[0].click().run()

        assert app.session_state.display_limit == 50
        assert table_html(app).count("<tr>") == 50
