"""
データモデル v2 の集計とビュー

画面に出す表は、ここで5つのテーブルから計算する(生成物のファイルは持たない)。
- build_performance_view: 歌唱の一覧(Home 用)
- build_song_stats: 曲ごとの集計(Song List 用。GROUP BY song_id)
- filter_song_stats: 曲ごとの集計の絞り込み(Song List の検索)
"""

import pandas as pd

from src.core.links import build_link
from src.core.text import normalize_for_match, reading_sort_key
from src.repositories.table_repository import Dataset

# 既定の歌唱回数から外す種類(配信の切り抜きは、元の配信と二重に数えないため)
EXCLUDED_FROM_COUNT_KINDS = ("切り抜き",)

# 画面に出さないコンテンツの access(メンバー限定)。歌唱の一覧にも曲ごとの集計にも入れない
HIDDEN_ACCESS = ("members",)

# 画面の「種類」の列の表示(contents.type → 日本語)。知らない値はそのまま表示する
CONTENT_TYPE_LABELS = {"live": "配信", "short": "ショート", "video": "動画", "post": "投稿", "audio": "音源"}

# 画面のリンクの文言(contents.platform → 文言)。知らない値は「リンク👻」
LINK_LABELS = {"youtube": "YouTubeへ👻", "x": "Xへ👻", "zan": "Z-aNへ👻", "goods": "詳細ページへ👻"}

VIEW_COLUMNS = [
    "content_id", "date", "no", "title", "display_title", "artist", "style", "part", "note",
    "link", "link_label", "platform", "type", "type_label", "content_title", "song_id", "artist_id",
    "search", "search_song",
]


def _normalized(series: pd.Series) -> pd.Series:
    """normalize_for_match を、重複を除いた値にだけかける(同じ曲名・アーティストが多いため)"""
    series = series.fillna("")
    return series.map({v: normalize_for_match(v) for v in series.unique()})


def cache_key(data_dir: str) -> tuple:
    """
    画面の @st.cache_data に渡す鍵: データファイルと、集計・読み込みのコードの更新日時

    データだけを鍵にすると、コード(列の追加など)を変えても古い集計結果が返る。
    起動したままのアプリでも、どちらかが変われば計算し直す。
    """
    from pathlib import Path
    from src.models import schema
    from src.repositories import table_repository
    from src.core import links, text
    code_files = [Path(__file__), Path(schema.__file__), Path(table_repository.__file__),
                  Path(links.__file__), Path(text.__file__)]
    data_files = [Path(data_dir) / s.filename for s in schema.ALL_SCHEMAS]
    return tuple((p.name, p.stat().st_mtime if p.exists() else 0) for p in data_files + code_files)


def display_artist(name: pd.Series, feat: pd.Series) -> pd.Series:
    """表示用のアーティスト: 歌い手(feat)があれば「作り手 feat.歌い手」"""
    feat = feat.fillna("")
    return name.fillna("").where(feat == "", name.fillna("") + " feat." + feat)


def display_title(title: pd.Series, part: pd.Series) -> pd.Series:
    """表示用の曲名: 尺(part)があれば「曲名(1chorus)」(v1 の画面と同じ半角の括弧)"""
    title, part = title.fillna(""), part.fillna("")
    return title.where(part == "", title + "(" + part + ")")


def link_label(platform: pd.Series) -> pd.Series:
    """リンクの文言(LINK_LABELS)"""
    return platform.map(lambda p: LINK_LABELS.get(p, "リンク👻"))


def search_text(*columns: pd.Series) -> pd.Series:
    """検索用の文字列: 各列を normalize_for_match し、改行で区切ってつなぐ"""
    result = _normalized(columns[0])
    for column in columns[1:]:
        result = result + "\n" + _normalized(column)
    return result


def build_performance_view(dataset: Dataset) -> pd.DataFrame:
    """
    歌唱1件を1行にした一覧

    並び: 日付の新しい順 → 同じ日の中は時刻の早い順(枝番の順) → コンテンツの中は seq 昇順。
    No. はコンテンツの中での順位(1, 2, 3…)。同じ日に複数のコンテンツがあるときは「枝番-順位」。
    同じ公演の続きの部(contents.follows)は、先の部と同じ枝番で順位を続け、並びも先の部の直後にする。
    """
    # メンバー限定のコンテンツは、データには持つが画面には出さない(2026-10-20 決定)。
    # 同じ日の枝番も、出すコンテンツだけで数える
    contents = dataset["contents"]
    contents = contents[~contents["access"].isin(HIDDEN_ACCESS)]
    perf = dataset["performances"]
    perf = perf[perf["content_id"].isin(contents["content_id"])]
    if perf.empty:
        return pd.DataFrame(columns=VIEW_COLUMNS)
    songs = dataset["songs"].rename(columns={"kind": "song_kind"})
    artists = dataset["artists"].rename(columns={"name": "artist"})

    view = (
        perf.merge(contents.rename(columns={"title": "content_title"}), on="content_id", how="left")
        .merge(songs[["song_id", "title", "sort_title", "artist_id", "feat", "song_kind"]], on="song_id", how="left")
        .merge(artists[["artist_id", "artist", "sort_name"]], on="artist_id", how="left")
    )
    view["artist"] = display_artist(view["artist"], view["feat"])
    view["seq_n"] = pd.to_numeric(view["seq"])

    # 同じ日のライブ配信どうしに、時刻の早い順で枝番を振る。
    # ショート・動画は枝番を付けない(同じ日にあっても、ライブ配信の No. を変えないため)
    # 同じ公演の続きの部(follows)は、先の部と同じ枝番で、曲順を先の部から続ける(例: 2-1, 2-2 → 2-3, 2-4)。
    # 先の部が無い(メン限で非表示など)・live どうしでないときは、follows を無視して普通のコンテンツにする
    live_ids = set(contents.loc[contents["type"] == "live", "content_id"])
    follows = contents["follows"].where(contents["follows"].isin(live_ids) & contents["content_id"].isin(live_ids), "")
    ordered = (
        contents.assign(_t=contents["start_time"].replace("", "99:99"), head=follows)
        .sort_values(["date", "_t", "content_id"])
    )
    ordered["head"] = ordered["head"].where(ordered["head"] != "", ordered["content_id"])
    ordered["day_pos"] = ordered.groupby("date").cumcount()
    heads = ordered[(ordered["type"] == "live") & (ordered["head"] == ordered["content_id"])]
    branches = heads.assign(
        branch=heads.groupby("date").cumcount() + 1,
        per_day=heads.groupby("date")["content_id"].transform("size"),
    )[["content_id", "branch", "per_day"]].rename(columns={"content_id": "head"})
    day_order = ordered[["content_id", "head", "day_pos"]].merge(branches, on="head", how="left")
    day_order["group_pos"] = day_order["head"].map(ordered.set_index("content_id")["day_pos"])
    view = view.merge(day_order, on="content_id", how="left")
    # コンテンツの中の曲順。続きの部は、先の部の歌唱数のあとから数える
    in_order = view.sort_values(["head", "day_pos", "seq_n"], kind="mergesort")
    view["no_in_content"] = (in_order.groupby("head").cumcount() + 1).reindex(view.index)
    no_in_content = view["no_in_content"].astype(str)
    has_branch = view["per_day"].fillna(1) > 1
    view["no"] = no_in_content.where(~has_branch, view["branch"].fillna(0).astype(int).astype(str) + "-" + no_in_content)
    # No. は「コンテンツの中の曲順」。1曲だけのショート・動画・投稿は空欄にする(種類の列で分かる)。
    # 複数の曲が入ったもの(例: ボカロファンテスト)は曲順を付ける。枝番はライブ配信だけ
    songs_in_content = view.groupby("content_id")["seq_n"].transform("size")
    view["no"] = view["no"].where((view["type"] == "live") | (songs_in_content > 1), "")

    view["style"] = view["style"].where(view["style"] != "", view["default_style"])
    view["type_label"] = view["type"].map(lambda t: CONTENT_TYPE_LABELS.get(t, t))
    view["link"] = [build_link(p, u, s) for p, u, s in zip(view["platform"], view["url"], view["start"])]
    view["link_label"] = link_label(view["platform"])
    view["display_title"] = display_title(view["title"], view["part"])
    # 検索語も normalize_for_match してから照合する。項目をまたいで一致しないよう改行で区切る。
    # 読み(sort_title・sort_name)も入れて、「かいじゅう」で「怪獣の花唄」を見つけられるようにする
    view["search_song"] = search_text(view["title"], view["sort_title"], view["artist"], view["sort_name"])
    view["search"] = view["search_song"] + "\n" + search_text(view["content_title"])

    # 日付は新しい順、同じ日の中は時刻の早い順(2026-10-21 決定。v1 の画面は遅い配信が上だった)、
    # コンテンツの中は曲順
    view = view.sort_values(
        ["date", "group_pos", "day_pos", "seq_n"],
        ascending=[False, True, True, True],
        kind="mergesort",
    ).reset_index(drop=True)
    return view[VIEW_COLUMNS]


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
    songs["artist"] = display_artist(songs["artist"], songs["feat"])
    columns = ["song_id", "title", "artist", "kind", "work", "year", "count", "first_date",
               "last_date", "latest_link", "latest_link_label", "live_count", "has_video", "has_short",
               "acoustic_count", "sort_name", "sort_title"]
    if view.empty or songs.empty:
        return pd.DataFrame(columns=columns + ["search"])

    kinds = dataset["contents"][["content_id", "kind"]].rename(columns={"kind": "content_kind"})
    counted = view.merge(kinds, on="content_id", how="left")
    counted = counted[~counted["content_kind"].isin(EXCLUDED_FROM_COUNT_KINDS)]

    # 最新のリンクは、購入ページ(音源)より動画・配信を優先する(音源しか無い曲は音源)
    latest = (
        counted.assign(_not_audio=counted["type"] != "audio")
        .sort_values(["_not_audio", "date"], kind="mergesort")
        .groupby("song_id").tail(1)
    )
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
    stats = stats.merge(
        latest[["song_id", "link", "link_label"]].rename(columns={"link": "latest_link", "link_label": "latest_link_label"}),
        on="song_id",
    )

    result = songs.merge(stats, on="song_id", how="inner")
    order = [
        (reading_sort_key(sn, a), reading_sort_key(st, t))
        for sn, a, st, t in zip(result["sort_name"], result["artist"], result["sort_title"], result["title"])
    ]
    result = result.assign(_order=order).sort_values("_order", kind="mergesort").drop(columns="_order")
    result["search"] = search_text(result["title"], result["sort_title"], result["artist"], result["sort_name"])
    return result[columns + ["search"]].reset_index(drop=True)


def filter_song_stats(stats: pd.DataFrame, query: str = "", kind: str = None, min_count: int = 1) -> pd.DataFrame:
    """
    曲ごとの集計(build_song_stats)を絞る

    キーワードは Home の検索と同じく normalize_for_match してから search 列(曲名・アーティストと読み)に部分一致。
    空(空白だけを含む)のキーワードと kind=None は絞らない。歌唱回数は min_count 以上。並びは変えない。
    """
    mask = stats["count"] >= min_count
    needle = normalize_for_match(query)
    if needle:
        mask &= stats["search"].str.contains(needle, regex=False)
    if kind is not None:
        mask &= stats["kind"] == kind
    return stats[mask]
