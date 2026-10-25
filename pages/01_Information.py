"""
情報ページモジュール

このモジュールは「しのうたタイム」アプリケーションの情報ページを提供します。

主な機能:
- 本人の予定表置き場(フリーチャットの枠)の動画の埋め込み表示
- 今週のスケジュール(本人の X の「今週のスケジュール」の投稿の埋め込み表示。毎週更新)
- お知らせ・グッズ・活動の記録の案内(ななしいんく 非公式Wiki と公式へのリンク)

お知らせ・グッズ・活動の記録は、非公式Wiki の幽音しののページ(告知・略歴・グッズ・オリジナル曲など)が
新しく詳しいので、このサイトでは X の投稿を埋め込んで並べず、Wiki へ案内する(2026-10-21 決定)。
今週のスケジュールだけは、2026-10-22 に埋め込みを戻した(更新の手順は docs/prompts/update-data.md)。

要件: 9.1
"""

from pathlib import Path

import streamlit as st
from src.ui.components import load_twitter_embed, render_twitter_embed
from src.ui.components.footer import display_footer  # footer.pyから関数をインポート
from src.ui.page_setup import setup_page

# 非公式Wiki の幽音しののページ(URL の日本語はエンコードしておく)
WIKI_URL = "https://wikiwiki.jp/774inc/%E5%B9%BD%E9%9F%B3%E3%81%97%E3%81%AE"
X_URL = "https://x.com/Shino_Kasukane_"

# 今週のスケジュールの埋め込み(取り込みのツールが保存する。このリポジトリの外)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCHEDULE_EMBED_PATH = DATA_DIR / "tweet_embed_code.html"
SCHEDULE_HEIGHT_PATH = DATA_DIR / "tweet_height.txt"

# --- ページの準備(ページ設定・共通の CSS・見出し。全ページで共通) ---
setup_page("Information", "📢")

# --- 目次 ---
st.subheader("目次")
st.markdown(
    """
    - [ふりちゃという名の予定表置き場](#youtube_schedule)
    - [今週のスケジュール](#weekly_schedule)
    - [お知らせ・グッズ・活動の記録](#news)
    """
)
st.markdown("---")


# --- YouTubeセクション ---
# 本人の予定表置き場(フリーチャットの枠)を埋め込み表示します
# st.video()を使用することで、Streamlitが自動的にYouTube動画プレーヤーを埋め込みます
# 要件: 9.1
st.subheader("ふりちゃという名の予定表置き場", anchor="youtube_schedule")
st.video("https://www.youtube.com/watch?v=LRowhAcHngc")
st.markdown("---")


# --- 今週のスケジュール ---
# 本人の X の「今週のスケジュール」の投稿を埋め込む。読めないときは X へ案内して続ける
st.subheader("今週のスケジュール", anchor="weekly_schedule")
st.caption(f"毎週更新しています。最新の予定は[幽音しのさんの X]({X_URL})をご覧ください。")
schedule_embed = load_twitter_embed(SCHEDULE_EMBED_PATH, SCHEDULE_HEIGHT_PATH)
if schedule_embed:
    render_twitter_embed(*schedule_embed)
else:
    st.info(f"今週のスケジュールを表示できませんでした。[幽音しのさんの X]({X_URL})をご覧ください。")
st.markdown("---")


# --- お知らせ・グッズ・活動の記録 ---
st.subheader("お知らせ・グッズ・活動の記録", anchor="news")
st.markdown(
    f"""
    お知らせ(グッズ・ボイスの販売など)、これまでの活動の記録(略歴・出演イベント)、オリジナル曲の一覧は、
    [ななしいんく 非公式Wiki の幽音しののページ]({WIKI_URL})にまとまっています。

    最新のお知らせは、[幽音しのさんの X]({X_URL})と
    [公式サイト](https://www.774.ai/talent/shino-kasukane)をご覧ください。
    """
)

# --- フッター(区切り線はフッターが引く) ---
display_footer()
