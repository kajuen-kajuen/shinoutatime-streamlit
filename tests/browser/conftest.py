"""ブラウザの確認(Playwright)の共通の部品

--runbrowser を付けたときだけ集める(tests/conftest.py)。browser のコンテナで流す:
    docker compose --profile browser run --rm browser pytest tests/browser --runbrowser
本番(リリースのあと)は、スリープしていると起きないので、先に tools/wake_up_streamlit.py で起こす:
    docker compose --profile browser run --rm browser sh -c "python tools/wake_up_streamlit.py \\
        https://shinoutatime.streamlit.app/ && pytest tests/browser --runbrowser \\
        --base-url https://shinoutatime.streamlit.app/"
stg はログインが要るので、このテストでは開けない(ブラウザで目で見る)。

失敗したテストの画面は browser_screenshots/ に残す(Git 管理外)。
"""

import re
from pathlib import Path
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

SITE_TITLE = "しのうたタイム"
# どのページでも最後に出すフッター(src/ui/components/footer.py)。これが出たら描き終わったとみなす
FOOTER_TEXT = "Made with Streamlit"
# Cloud のスリープ明けや、起動直後の最初の読み込みも待てるように長めにする
PAGE_TIMEOUT_MS = 120_000
SCREENSHOT_DIR = Path("browser_screenshots")

VIEWPORTS = {
    "pc": {"width": 1280, "height": 800},
    "mobile": {"width": 390, "height": 844},  # iPhone 12〜15 相当
}

PAGES = {
    "home": "",
    "information": "Information",
    "about_us": "About_Us",
    "song_list": "Song_List_beta",
}


def app_base_url(url: str) -> str:
    """開く URL のもと。Streamlit Cloud(*.streamlit.app)は、外枠を通らずアプリを直接開ける /~/+/ にする

    外枠はアプリを /~/+/<ページ> の iframe で出している(2026-10-23 に本番で確かめた)。
    ログインの要るアプリ(stg)の /~/+/ は share.streamlit.io の not_found に転送される。
    """
    url = url if url.endswith("/") else url + "/"
    host = urlparse(url).hostname or ""
    if host.endswith(".streamlit.app") and "/~/+/" not in url:
        url += "~/+/"
    return url


@pytest.fixture(scope="session")
def base_url(pytestconfig) -> str:
    return app_base_url(pytestconfig.getoption("--base-url"))


@pytest.fixture(scope="session")
def browser() -> Browser:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    if report.when == "call":
        item.call_failed = report.failed
    return report


def _new_page(browser: Browser, request, viewport: str) -> Page:
    context = browser.new_context(viewport=VIEWPORTS[viewport], locale="ja-JP")
    page = context.new_page()
    page.set_default_timeout(PAGE_TIMEOUT_MS)

    def finalize():
        if getattr(request.node, "call_failed", False):
            SCREENSHOT_DIR.mkdir(exist_ok=True)
            name = re.sub(r"[^\w.-]+", "_", request.node.name)
            page.screenshot(path=str(SCREENSHOT_DIR / f"{name}.png"), full_page=True)
        context.close()

    request.addfinalizer(finalize)
    return page


@pytest.fixture
def pc_page(browser, request) -> Page:
    return _new_page(browser, request, "pc")


@pytest.fixture
def mobile_page(browser, request) -> Page:
    return _new_page(browser, request, "mobile")


def open_app_page(page: Page, base_url: str, path: str) -> None:
    """ページを開き、フッター(描き終わり)か例外の表示が出るまで待つ"""
    page.goto(base_url + path, wait_until="domcontentloaded")
    finished = page.get_by_text(FOOTER_TEXT).or_(page.locator('[data-testid="stException"]'))
    finished.first.wait_for(state="visible")
