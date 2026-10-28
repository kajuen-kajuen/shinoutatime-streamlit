"""
楽曲リスト表示ページ（β版）

このモジュールは、VTuber「幽音しの」さんの配信で歌唱された全楽曲のリストを
アーティスト順に表示する機能を提供します。

主な機能:
- データモデル v2(data/v2/)の曲ごとの集計(views.build_song_stats)を表示する
- 並びはアーティストの読み → 曲名の読み
- 列はアーティスト・曲名・歌唱回数・最終歌唱日・最新の歌唱へのリンク(切り抜きは除く)
- キーワード(曲名・アーティスト)・種類・歌唱回数で絞り込み(views.filter_song_stats)、
  絞った結果を ROWS_PER_PAGE 曲ずつ出す(裏ラジアーカイブスさんの上限)。超えたら表の上と下に
  ページ番号を出す(ひよクロ音楽リストさんの形)

データソース:
- data/v2/ の5つの TSV(src/ui/v2_data.py で読み、キャッシュする)
"""

import html
import logging

import streamlit as st
import pandas as pd
from src.core.views import filter_song_stats
from src.models.schema import SONG_KINDS
from src.ui.components.footer import display_footer
from src.ui.page_setup import setup_page
from src.ui.pages.home_page import LOAD_ERROR_HINT, escape_markdown
from src.ui.v2_data import load_song_stats

logger = logging.getLogger(__name__)

# 種類の絞り込みの「絞らない」選択肢
ALL_KINDS = "すべて"

# 1ページに出す曲の数(裏ラジアーカイブスさんの MAX_ROWS と同じ 250)。続きはページ番号で出す(ひよクロ音楽リストさんの形)。
# 全曲(約790行)を1つの表で出すと、スマホでは表の組み立てと配置の計算で表示が1秒ほど遅くなる(2026-10-28 に手元で測った)
ROWS_PER_PAGE = 250

# 表まわりの入れ物の key(Streamlit が st-key-<key> のクラスを付ける。画面を戻すときの目印にする)
RESULTS_KEY = "song_list_results"

# 下のページ番号を押したあと、表の先頭まで画面を戻すスクリプト(固定の文字列。データは入れない)。
# nonce を入れて毎回違う文字列にする(同じ文字列だと、続けて押したときに作り直されず動かない)。
# 画面の上に固定の帯(Streamlit のヘッダー)があり、先頭の件数の文が隠れるので、その分の余白(scroll-margin-top)を取る
SCROLL_TO_RESULTS_SCRIPT = """<script>/* {nonce} */
(function () {{
  var box = window.parent.document.querySelector(".st-key-{key}");
  if (box) {{
    box.style.scrollMarginTop = "5rem";
    box.scrollIntoView({{block: "start"}});
  }}
}})();
</script>"""

# --- ページの準備(ページ設定・共通の CSS(style.css)・見出し。全ページで共通) ---
setup_page("歌唱楽曲リスト(β版)", "🎵")

st.markdown(
    """
    こちらはVTuber「[幽音しの](https://www.774.ai/talent/shino-kasukane)」さんの配信で歌われた楽曲をまとめた非公式データベースです。
    """
)

# --- β版の制約について ---
# 並び順(読みの順)と重複(曲ごとに1行)は v2 で解消したので、機能の変更の注意だけ残す
with st.expander("β版の制約について"):
    st.info(
        """
        - **機能の変更:** 今後、予告なくレイアウトや機能が変更・削除されることがあります。
        """
    )
st.markdown("---")


def _cell(value) -> str:
    """表のセルの文字列(データ由来なのでエスケープする。欠損は空)"""
    return html.escape(str(value)) if pd.notna(value) else ""


def build_table_html(stats: pd.DataFrame) -> str:
    """
    アーティスト・曲名・歌唱回数・最終歌唱日・リンクの表の HTML を組み立てる

    データ由来の文字列はすべてエスケープする(曲名の < や & で表が壊れないように)。
    リンクは最新の歌唱(views.build_song_stats の latest_link)。最終歌唱日は Home の配信日と同じ YYYY/MM/DD。
    クラス名と見出しの左寄せは、以前の DataFrame.to_html(justify="left", classes="dataframe") と同じ。
    表は Home(src/ui/components の render_results_table)と同じ横スクロールの div で包む
    (列が改行しないので、スマホの幅では表が画面からはみ出すため)。
    """
    rows = []
    for artist, title, count, last_date, url, label in zip(
        stats["artist"], stats["title"], stats["count"], stats["last_date"],
        stats["latest_link"], stats["latest_link_label"],
    ):
        link = (
            f'<a href="{html.escape(str(url), quote=True)}" target="_blank" rel="noopener">{_cell(label)}</a>'
            if pd.notna(url) and url else ""
        )
        rows.append(
            f'<tr><td><div class="artist-cell">{_cell(artist)}</div></td><td>{_cell(title)}</td>'
            f'<td>{_cell(count)}</td><td>{_cell(last_date).replace("-", "/")}</td><td>{link}</td></tr>'
        )
    header = (
        '<tr style="text-align: left;"><th>アーティスト</th><th>曲名</th>'
        "<th>歌唱回数</th><th>最終歌唱日</th><th>リンク</th></tr>"
    )
    return (
        '<div style="overflow-x: auto; max-width: 100%;">'
        '<table border="1" class="dataframe">'
        f"<thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"
        "</div>"
    )


def render_filter_form(max_count: int) -> None:
    """
    絞り込みのフォーム(キーワード・種類・歌唱回数)

    st.form の中なので、Enter キーか「検索」ボタンでまとめて送信する。送信した条件は
    Song List 専用の session_state(song_list_*)に写す(Home の search_query と混ぜない。
    別のページから戻っても条件が残る)。歌唱回数のスライダーは、最多の回数が 1 のときは出さない。
    部品には key を付ける。key が無いと、Streamlit は value(写した前回の条件)から部品の ID を作るので、
    条件が変わった次の送信で ID が変わり、入力した値が捨てられて前回の条件が返る。
    """
    kinds = [ALL_KINDS, *SONG_KINDS]
    with st.form("song_list_search_form", border=False):
        query = st.text_input(
            "キーワード検索（曲名、アーティスト）",
            value=st.session_state.song_list_query,
            key="song_list_search_box",
            placeholder="ここにキーワードを入力",
        )
        kind = st.radio(
            "種類",
            kinds,
            index=kinds.index(st.session_state.song_list_kind),
            key="song_list_kind_radio",
            horizontal=True,
        )
        min_count = 1
        if max_count > 1:
            min_count = st.slider(
                "歌唱回数(この回数以上)",
                min_value=1,
                max_value=max_count,
                value=min(st.session_state.song_list_min_count, max_count),
                key="song_list_min_count_slider",
            )
        submitted = st.form_submit_button("検索")

    if submitted:
        logger.info(f"楽曲リストの絞り込み: キーワード='{query}', 種類={kind}, 歌唱回数>={min_count}")
        st.session_state.song_list_query = query
        st.session_state.song_list_kind = kind
        st.session_state.song_list_min_count = min_count
        st.session_state.song_list_page = 1  # 条件が変わったら1ページ目から


def _on_page_change(source_key: str) -> None:
    """ページ番号の on_change: 押した側の値を song_list_page に写す。下で押したら、表の先頭へ戻す印を立てる"""
    st.session_state.song_list_page = st.session_state[source_key]
    if source_key == "song_list_page_bottom":
        st.session_state.song_list_scroll_to_top = True
        st.session_state.song_list_scroll_nonce += 1


def render_page_selector(key: str, pages: int) -> None:
    """
    ページ番号(1〜pages)。表の上と下に、別の key で2つ出す

    作る前に key の値を song_list_page に合わせ、上下をそろえる(default は渡さない。値の二重指定になる)。
    required=True なので、選んだページを押しても選択は外れない。
    """
    st.session_state[key] = st.session_state.song_list_page
    st.segmented_control(
        "ページ",
        list(range(1, pages + 1)),
        required=True,
        key=key,
        on_change=_on_page_change,
        args=(key,),
    )


try:
    stats = load_song_stats()
except Exception as e:  # DataLoadError のほか、集計中の想定外の失敗も画面に出して止める
    # 公開の画面なので、例外のメッセージ(サーバー上のパスを含む)は出さず、Home と同じ短い案内にする
    logger.error(f"楽曲リストの読み込みに失敗しました: {e}", exc_info=True)
    st.error("楽曲リストを読み込めませんでした。")
    st.info(LOAD_ERROR_HINT)
    stats = None

# --- メインコンテンツの表示 ---
if stats is None:
    pass  # 失敗の表示は上で出した
elif stats.empty:
    st.warning("楽曲データが読み込めませんでした。")
else:
    st.session_state.setdefault("song_list_query", "")
    st.session_state.setdefault("song_list_kind", ALL_KINDS)
    st.session_state.setdefault("song_list_min_count", 1)
    st.session_state.setdefault("song_list_page", 1)
    st.session_state.setdefault("song_list_scroll_to_top", False)
    st.session_state.setdefault("song_list_scroll_nonce", 0)

    max_count = int(stats["count"].max())
    render_filter_form(max_count)

    query = st.session_state.song_list_query
    kind = st.session_state.song_list_kind
    min_count = min(st.session_state.song_list_min_count, max_count)
    filtered = filter_song_stats(stats, query, None if kind == ALL_KINDS else kind, min_count)

    # 表示するページ(データが減ってページが無くなったら、最後のページに寄せる)
    pages = max(1, -(-len(filtered) // ROWS_PER_PAGE))
    page = min(st.session_state.song_list_page, pages)
    st.session_state.song_list_page = page
    start = (page - 1) * ROWS_PER_PAGE
    shown = filtered.iloc[start:start + ROWS_PER_PAGE]

    with st.container(key=RESULTS_KEY):
        # 件数の文(1ページに収まれば裏ラジアーカイブスさんの「全N件を表示しています。」、
        # 収まらなければひよクロ音楽リストさんの「N件中 1 - M件目を表示」の形)
        if pages > 1:
            summary = f"全 {len(filtered)} 曲中 {start + 1} - {start + len(shown)} 曲目を表示しています。"
        else:
            summary = f"全 {len(filtered)} 曲を表示しています。"
        if query.strip():
            summary = f"「{escape_markdown(query)}」で検索した結果: {summary}"
        st.write(summary)

        if filtered.empty:
            st.info("条件に合う曲が見つかりませんでした。")
        else:
            # テーブルの表示(並びは views の読みの順: アーティスト → 曲名)。ページ番号は表の上と下
            if pages > 1:
                render_page_selector("song_list_page_top", pages)
            st.write(build_table_html(shown), unsafe_allow_html=True)
            if pages > 1:
                render_page_selector("song_list_page_bottom", pages)

    if st.session_state.song_list_scroll_to_top:
        st.session_state.song_list_scroll_to_top = False
        st.html(
            SCROLL_TO_RESULTS_SCRIPT.format(nonce=st.session_state.song_list_scroll_nonce, key=RESULTS_KEY),
            unsafe_allow_javascript=True,
        )

# --- フッターを表示 ---
display_footer()
