"""
load_twitter_embed(Information の今週のスケジュールの埋め込みの読み込み)のテスト

読めないときは画面を止めずに None を返し、ページが X へ案内する。
"""

import pytest

from src.ui.components import load_twitter_embed

EMBED = '<blockquote class="twitter-tweet"><p>今週のスケジュール</p></blockquote>'


@pytest.fixture
def paths(tmp_path):
    return tmp_path / "tweet_embed_code.html", tmp_path / "tweet_height.txt"


def test_reads_embed_and_height(paths):
    embed_path, height_path = paths
    embed_path.write_text(EMBED + "\n", encoding="utf-8")
    height_path.write_text("850\n", encoding="utf-8")
    assert load_twitter_embed(embed_path, height_path) == (EMBED, 850)


def test_missing_file_returns_none(paths):
    embed_path, height_path = paths
    height_path.write_text("850", encoding="utf-8")
    assert load_twitter_embed(embed_path, height_path) is None


@pytest.mark.parametrize("embed, height", [
    ("", "850"),          # 埋め込みが空
    ("   \n", "850"),     # 空白だけ
    (EMBED, "abc"),       # 高さが数でない
    (EMBED, ""),          # 高さが空
    (EMBED, "0"),         # 高さが正でない
    (EMBED, "-10"),
])
def test_invalid_content_returns_none(paths, embed, height):
    embed_path, height_path = paths
    embed_path.write_text(embed, encoding="utf-8")
    height_path.write_text(height, encoding="utf-8")
    assert load_twitter_embed(embed_path, height_path) is None


def test_real_data_files_are_valid():
    """リポジトリの data/ の埋め込みは、そのまま表示できる形になっている"""
    from pathlib import Path

    data_dir = Path(__file__).resolve().parents[3] / "data"
    result = load_twitter_embed(data_dir / "tweet_embed_code.html", data_dir / "tweet_height.txt")
    assert result is not None
    embed_code, _ = result
    assert 'class="twitter-tweet"' in embed_code
    assert "https://twitter.com/Shino_Kasukane_/status/" in embed_code or "https://x.com/Shino_Kasukane_/status/" in embed_code
