"""テスト全体の設定: 時間のかかるテスト(slow)は --runslow を付けたときだけ流す"""

import pytest


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="時間のかかるテスト(slow)も流す")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: 時間のかかるテスト(--runslow を付けたときだけ流す)")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        return
    skip = pytest.mark.skip(reason="--runslow を付けたときだけ流す")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)
