"""
データモデル v2 の集計とビュー

画面に出す表は、ここで5つのテーブルから計算する(生成物のファイルは持たない)。
- build_performance_view: 歌唱の一覧(Home 用)
- build_song_stats: 曲ごとの集計(Song List 用。GROUP BY song_id)
"""

import pandas as pd

from src.core.links import build_link
from src.core.text import normalize_for_match, reading_sort_key
from src.repositories.table_repository import Dataset

# 既定の歌唱回数から外す種類(配信の切り抜きは、元の配信と二重に数えないため)
EXCLUDED_FROM_COUNT_KINDS = ("切り抜き",)


def _normalized(series: pd.Series) -> pd.Series:
    """normalize_for_match を、重複を除いた値にだけかける(同じ曲名・アーティストが多いため)"""
    series = series.fillna("")
    return series.map({v: normalize_for_match(v) for v in series.unique()})


def build_performance_view(dataset: Dataset) -> pd.DataFrame:
    """
    歌唱1件を1行にした一覧

    並び: コンテンツの新しい順(date 降順 → start_time 降順) → コンテンツの中は seq 昇順。
    No. はコンテンツの中での順位(1, 2, 3…)。同じ日に複数のコンテンツがあるときは「枝番-順位」。
    """
    perf = dataset["performances"]
    if perf.empty:
        return pd.DataFrame(columns=[
            "content_id", "date", "no", "title", "artist", "style", "part", "note",
            "link", "platform", "type", "content_title", "song_id", "artist_id", "search",
        ])
    contents = dataset["contents"]
    songs = dataset["songs"].rename(columns={"kind": "song_kind"})
    artists = dataset["artists"].rename(columns={"name": "artist"})

    view = (
        perf.merge(contents.rename(columns={"title": "content_title"}), on="content_id", how="left")
        .merge(songs[["song_id", "title", "artist_id", "song_kind"]], on="song_id", how="left")
        .merge(artists[["artist_id", "artist"]], on="artist_id", how="left")
    )
    view["seq_n"] = pd.to_numeric(view["seq"])
    view["no_in_content"] = view.groupby("content_id")["seq_n"].rank(method="first").astype(int)

    # 同じ日のコンテンツに、時刻の早い順で枝番を振る
    day_order = (
        contents.assign(_t=contents["start_time"].replace("", "99:99"))
        .sort_values(["date", "_t", "content_id"])
        .assign(branch=lambda d: d.groupby("date").cumcount() + 1,
                per_day=lambda d: d.groupby("date")["content_id"].transform("size"))
    )[["content_id", "branch", "per_day"]]
    view = view.merge(day_order, on="content_id", how="left")
    no_in_content = view["no_in_content"].astype(str)
    view["no"] = no_in_content.where(view["per_day"] <= 1, view["branch"].astype(str) + "-" + no_in_content)

    view["style"] = view["style"].where(view["style"] != "", view["default_style"])
    view["link"] = [build_link(p, u, s) for p, u, s in zip(view["platform"], view["url"], view["start"])]
    # 検索語も normalize_for_match してから照合する。項目をまたいで一致しないよう改行で区切る
    view["search"] = (_normalized(view["title"]) + "\n" + _normalized(view["artist"])
                      + "\n" + _normalized(view["content_title"]))

    view = view.sort_values(
        ["date", "start_time", "content_id", "seq_n"],
        ascending=[False, False, True, True],
        kind="mergesort",
    ).reset_index(drop=True)
    return view[[
        "content_id", "date", "no", "title", "artist", "style", "part", "note",
        "link", "platform", "type", "content_title", "song_id", "artist_id", "search",
    ]]


def build_song_stats(dataset: Dataset, view: pd.DataFrame = None) -> pd.DataFrame:
    """
    曲ごとの集計(GROUP BY song_id)

    歌唱回数・初歌唱日・最終歌唱日・最新のリンク・種類ごとの回数・演奏の形ごとの回数。
    切り抜きのショートは歌唱回数に数えない。並びはアーティストの読み → 曲の読み。
    """
    if view is None:
        view = build_performance_view(dataset)
    songs = dataset["songs"].merge(
        dataset["artists"].rename(columns={"name": "artist"}), on="artist_id", how="left"
    )
    columns = ["song_id", "title", "artist", "kind", "work", "year", "count", "first_date",
               "last_date", "latest_link", "live_count", "has_video", "has_short",
               "acoustic_count", "sort_name", "sort_title"]
    if view.empty or songs.empty:
        return pd.DataFrame(columns=columns)

    kinds = dataset["contents"][["content_id", "kind"]].rename(columns={"kind": "content_kind"})
    counted = view.merge(kinds, on="content_id", how="left")
    counted = counted[~counted["content_kind"].isin(EXCLUDED_FROM_COUNT_KINDS)]

    latest = counted.sort_values(["date"], kind="mergesort").groupby("song_id").tail(1)
    # lambda や Arrow の文字列のまま集計すると曲ごとに遅い処理になるので、
    # NumPy の bool と datetime の列を先に作ってから数える
    flags = pd.DataFrame({
        "song_id": counted["song_id"].to_numpy(dtype=object),
        "_date": pd.to_datetime(counted["date"]).to_numpy(),
        "_live": (counted["type"] == "live").to_numpy(dtype=bool),
        "_video": (counted["type"] == "video").to_numpy(dtype=bool),
        "_short": (counted["type"] == "short").to_numpy(dtype=bool),
        "_acoustic": (counted["style"] == "弾き語り").to_numpy(dtype=bool),
    })
    stats = flags.groupby("song_id").agg(
        count=("_date", "size"),
        first_date=("_date", "min"),
        last_date=("_date", "max"),
        live_count=("_live", "sum"),
        has_video=("_video", "any"),
        has_short=("_short", "any"),
        acoustic_count=("_acoustic", "sum"),
    ).reset_index()
    stats["first_date"] = stats["first_date"].dt.strftime("%Y-%m-%d")
    stats["last_date"] = stats["last_date"].dt.strftime("%Y-%m-%d")
    stats = stats.merge(latest[["song_id", "link"]].rename(columns={"link": "latest_link"}), on="song_id")

    result = songs.merge(stats, on="song_id", how="inner")
    order = [
        (reading_sort_key(sn, a), reading_sort_key(st, t))
        for sn, a, st, t in zip(result["sort_name"], result["artist"], result["sort_title"], result["title"])
    ]
    result = result.assign(_order=order).sort_values("_order", kind="mergesort").drop(columns="_order")
    return result[columns].reset_index(drop=True)
