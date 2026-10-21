"""
Streamlit Community Cloud のアプリをブラウザで開き、スリープしていれば起こす

GitHub Actions(.github/workflows/wake_up_streamlit.yml)から定期的に呼ぶ。
HTML を取るだけ(curl など)ではアプリは起きないので、Playwright の Chromium で開き、
スリープ画面の「Yes, get this app back up!」ボタンがあれば押して、アプリの見出しが出るまで待つ。

使い方:
    python tools/wake_up_streamlit.py https://shinoutatime.streamlit.app/
    python tools/wake_up_streamlit.py URL [URL ...] --expect しのうたタイム --timeout 180

終了コード: すべての URL でアプリの見出しが出れば 0、1つでも出なければ 1。
出なかった URL はスクリーンショットを wake_up_screenshots/ に保存する(Actions の artifact で見る)。
playwright はアプリの依存に入れない(ワークフローの中で pip install する)。
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

WAKE_UP_BUTTON = "Yes, get this app back up!"
DEFAULT_EXPECT = "しのうたタイム"
DEFAULT_TIMEOUT_SEC = 180
POLL_INTERVAL_SEC = 2
SCREENSHOT_DIR = Path("wake_up_screenshots")


def _app_is_shown(page: Page, expect: str) -> bool:
    """どれかのフレームに見出しの文字が出ているか(Cloud はアプリを iframe で出すことがある)"""
    for frame in page.frames:
        try:
            if frame.get_by_text(expect).count() > 0:
                return True
        except PlaywrightError:
            # 読み込み中に外れたフレームは飛ばす
            continue
    return False


def _click_wake_up_button(page: Page) -> bool:
    """スリープ画面のボタンがあれば押す。押したら True"""
    for frame in page.frames:
        try:
            button = frame.get_by_role("button", name=WAKE_UP_BUTTON)
            if button.count() > 0 and button.first.is_visible():
                button.first.click()
                return True
        except PlaywrightError:
            continue
    return False


def wake_up(page: Page, url: str, expect: str, timeout_sec: int) -> bool:
    """URL を開き、必要ならボタンを押して、見出しが出るまで待つ。出れば True"""
    print(f"[{url}] 開きます", flush=True)
    page.goto(url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)

    woke = False
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if _app_is_shown(page, expect):
            state = "スリープ中だったので起こしました" if woke else "起動済みでした"
            print(f"[{url}] OK: {state}", flush=True)
            return True
        if not woke and _click_wake_up_button(page):
            woke = True
            print(f"[{url}] スリープ中でした。「{WAKE_UP_BUTTON}」を押しました", flush=True)
        page.wait_for_timeout(POLL_INTERVAL_SEC * 1000)

    SCREENSHOT_DIR.mkdir(exist_ok=True)
    screenshot = SCREENSHOT_DIR / f"{urlparse(url).hostname or 'app'}.png"
    page.screenshot(path=str(screenshot), full_page=True)
    print(f"[{url}] NG: {timeout_sec} 秒待っても「{expect}」が出ません(画面: {screenshot})", flush=True)
    return False


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Streamlit Cloud のアプリをブラウザで開いて起こす")
    parser.add_argument("urls", nargs="+", help="開くアプリの URL")
    parser.add_argument("--expect", default=DEFAULT_EXPECT, help=f"アプリが出たと判断する文字(既定: {DEFAULT_EXPECT})")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SEC, help="URL ごとに待つ秒数")
    args = parser.parse_args(argv)

    all_ok = True
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for url in args.urls:
            page = browser.new_page()
            try:
                all_ok = wake_up(page, url, args.expect, args.timeout) and all_ok
            except PlaywrightError as e:
                print(f"[{url}] NG: ブラウザの操作に失敗しました: {e}", flush=True)
                all_ok = False
            finally:
                page.close()
        browser.close()
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
