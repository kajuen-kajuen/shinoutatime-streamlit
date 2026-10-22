"""テスト全体の設定

- 時間のかかるテスト(slow)は --runslow を付けたときだけ流す
- ブラウザの確認(tests/browser/)は --runbrowser を付けたときだけ集める
  (playwright はアプリのコンテナに入っていないので、付けないときは import もしない)
"""

from pathlib import Path

import pytest

BROWSER_TESTS_DIR = Path(__file__).parent / "browser"


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="時間のかかるテスト(slow)も流す")
    parser.addoption("--runbrowser", action="store_true", default=False,
                     help="ブラウザの確認(tests/browser/)を流す。browser のコンテナで使う")
    parser.addoption("--base-url", default="http://shinouta-time:8501/",
                     help="ブラウザの確認で開くアプリの URL(既定: 手元のコンテナ。stg・本番の URL も渡せる)")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: 時間のかかるテスト(--runslow を付けたときだけ流す)")


def pytest_ignore_collect(collection_path, config):
    if config.getoption("--runbrowser"):
        return None
    if collection_path == BROWSER_TESTS_DIR or BROWSER_TESTS_DIR in collection_path.parents:
        return True
    return None


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        return
    skip = pytest.mark.skip(reason="--runslow を付けたときだけ流す")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)
