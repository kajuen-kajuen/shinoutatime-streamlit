"""ブラウザでの確認: ページが開くこと、検索とリンク、スマホ幅でのはみ出し、今週のスケジュールの枠

AppTest(tests/e2e/)では見えない、本物のブラウザでの描画を確かめる。本物の data/v2/ を読むので、
件数は決め打ちせず「1件以上」で確かめる。
"""

import pytest
from playwright.sync_api import Page, expect

from tests.browser.conftest import PAGES, SITE_TITLE, open_app_page

# 読み込みに失敗したときの案内(src/ui/pages/home_page.py の LOAD_ERROR_HINT。
# このコンテナには streamlit が無いので import せずに書く)
LOAD_ERROR_HINT = "時間をおいて、ページを開き直してください。"
# 本物のデータに必ずある曲(tests/e2e/test_app_e2e.py と同じ)
SEARCH_QUERY = "怪獣の花唄"


def horizontal_overflow(page: Page) -> int:
    """ページ(と Streamlit の本文の入れ物)が横にはみ出している幅(px)。表は overflow-x: auto の枠の中で動くので数えない"""
    return page.evaluate(
        """() => {
            const boxes = [document.documentElement,
                           ...document.querySelectorAll('[data-testid="stMain"], [data-testid="stAppViewContainer"]')];
            return Math.max(0, ...boxes.map(el => el.scrollWidth - el.clientWidth));
        }"""
    )


@pytest.mark.parametrize("viewport", ["pc", "mobile"])
@pytest.mark.parametrize("page_name", list(PAGES))
def test_page_opens_without_error(request, base_url, page_name, viewport):
    """どのページも、PC とスマホの幅で、見出しが出て、例外と読み込み失敗の案内が無い"""
    page = request.getfixturevalue(f"{viewport}_page")
    open_app_page(page, base_url, PAGES[page_name])

    expect(page.locator('[data-testid="stException"]')).to_have_count(0)
    expect(page.locator('[data-testid="stHeading"]', has_text=SITE_TITLE).first).to_be_visible()
    expect(page.get_by_text(LOAD_ERROR_HINT)).to_have_count(0)


def test_home_search_shows_rows_and_links(pc_page, base_url):
    """Home で検索すると表に行が出て、リンクは https で、時刻(t=)付きの YouTube のものがある"""
    page = pc_page
    open_app_page(page, base_url, PAGES["home"])

    search_box = page.get_by_placeholder("ここにキーワードを入力")
    search_box.fill(SEARCH_QUERY)
    search_box.press("Enter")  # 検索欄は st.form の中なので Enter で送信できる

    expect(page.get_by_text(f"「{SEARCH_QUERY}」で検索した結果")).to_be_visible()
    rows = page.locator("table.dataframe tbody tr")
    expect(rows.first).to_be_visible()
    expect(rows.first).to_contain_text(SEARCH_QUERY)

    hrefs = page.locator("table.dataframe a").evaluate_all("links => links.map(a => a.href)")
    assert hrefs, "表にリンクがありません"
    assert all(h.startswith("https://") for h in hrefs), hrefs
    assert any(h.startswith("https://www.youtube.com/") and "t=" in h for h in hrefs), \
        "時刻(t=)付きの YouTube のリンクがありません"


@pytest.mark.parametrize("page_name", ["home", "song_list"])
def test_mobile_page_does_not_overflow(mobile_page, base_url, page_name):
    """スマホの幅で、表のあるページが横にはみ出さない(表は枠の中で横に動く)"""
    open_app_page(mobile_page, base_url, PAGES[page_name])
    expect(mobile_page.locator("table.dataframe").first).to_be_visible()

    assert horizontal_overflow(mobile_page) <= 1


def test_information_has_schedule_frame(pc_page, base_url):
    """Information に今週のスケジュール(X の埋め込み)の枠がある。中身は X の読み込み次第なので見ない"""
    open_app_page(pc_page, base_url, PAGES["information"])

    expect(pc_page.locator('iframe[srcdoc*="shinouta-embed"]')).to_have_count(1)
