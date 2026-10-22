"""
画面が読むデータ(データモデル v2)

data/v2/ の5つの TSV を読み、歌唱の一覧(Home 用)と曲ごとの集計(Song List 用)を返す。
キャッシュの鍵は views.cache_key(データと集計のコードの更新日時)なので、どちらかが変われば計算し直す。
読み込みに失敗したら DataLoadError を投げる。表示はページ側で行う(キャッシュ関数の中で st.* を出さない)。
"""

import logging
from pathlib import Path
from typing import Tuple

import pandas as pd
import streamlit as st

from src.config.settings import Config
from src.core.validation import validate_dataset
from src.core.views import build_performance_view, build_song_stats, cache_key
from src.exceptions.errors import DataLoadError
from src.repositories.table_repository import TableRepository

logger = logging.getLogger(__name__)


def _data_dir() -> str:
    return Config.from_env().v2_data_dir


# 鍵(更新日時)が変わったら前の結果は使わないので、1つだけ持つ(古い結果をメモリに残さない)
@st.cache_data(show_spinner="データを読み込み中...", max_entries=1)
def _load(data_dir: str, version: tuple) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    歌唱の一覧と曲ごとの集計を計算する(version はキャッシュの鍵にだけ使う)

    検査の error は、公開の画面には出さずログにだけ書く(データは取り込みのときに検査している)。
    """
    if not Path(data_dir).is_dir():
        raise DataLoadError(file_path=data_dir, message="データのディレクトリがありません")
    dataset = TableRepository(data_dir).load()
    for issue in validate_dataset(dataset):
        if issue.level == "error":
            logger.error(f"データの検査で問題があります: {issue}")
    view = build_performance_view(dataset)
    return view, build_song_stats(dataset, view)


def load_performance_view() -> pd.DataFrame:
    """歌唱の一覧(views.build_performance_view)"""
    data_dir = _data_dir()
    return _load(data_dir, cache_key(data_dir))[0]


def load_song_stats() -> pd.DataFrame:
    """曲ごとの集計(views.build_song_stats)"""
    data_dir = _data_dir()
    return _load(data_dir, cache_key(data_dir))[1]
