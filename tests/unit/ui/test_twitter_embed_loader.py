"""
load_twitter_embed・render_twitter_embed(Information の今週のスケジュールの埋め込み)のテスト

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


def test_render_wraps_embed_with_auto_height_script():
    """表示では、埋め込みを包みの要素に入れ、枠の高さを中身に合わせるスクリプトを後ろに付ける"""
    from unittest.mock import MagicMock, patch

    from src.ui.components import EMBED_WRAPPER_ID, render_twitter_embed

    columns = [MagicMock(), MagicMock(), MagicMock()]
    with patch("src.ui.components.st.columns", return_value=columns), \
            patch("streamlit.components.v1.html") as html:
        render_twitter_embed(EMBED, 850)

    (code,), kwargs = html.call_args
    assert code.startswith(f'<div id="{EMBED_WRAPPER_ID}" style="display: flow-root;">{EMBED}</div>')
    assert "window.frameElement" in code and "ResizeObserver" in code
    # 外の入れ物は flex の基準の大きさで高さが決まるので、flex も合わせる
    assert "stElementContainer" in code and "\"flex\"" in code
    # 合わせられないときは、渡した高さのままスクロールできる
    assert kwargs == {"height": 850, "scrolling": True}
