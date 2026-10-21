"""
情報ページモジュール

このモジュールは「しのうたタイム」アプリケーションの情報ページを提供します。

主な機能:
- 本人の予定表置き場(フリーチャットの枠)の動画の埋め込み表示
- お知らせ・グッズ・活動の記録の案内(ななしいんく 非公式Wiki と公式へのリンク)

お知らせ・グッズ・活動の記録は、非公式Wiki の幽音しののページ(告知・略歴・グッズ・オリジナル曲など)が
新しく詳しいので、このサイトでは X の投稿を埋め込んで並べず、Wiki へ案内する(2026-10-21 決定)。

要件: 9.1
"""

import streamlit as st
from src.ui.components.footer import display_footer  # footer.pyから関数をインポート

# 非公式Wiki の幽音しののページ(URL の日本語はエンコードしておく)
WIKI_URL = "https://wikiwiki.jp/774inc/%E5%B9%BD%E9%9F%B3%E3%81%97%E3%81%AE"

# --- ページ設定 ---
st.set_page_config(
    page_title="Information - しのうたタイム",
    page_icon="👻",
    layout="wide",
)

# --- ヘッダー ---
st.title("Information")

# --- 目次 ---
st.markdown("## 目次")
st.markdown(
    """
    - [ふりちゃという名の予定表置き場](#youtube_schedule)
    - [お知らせ・グッズ・活動の記録](#news)
    """
)
st.write("---")


# --- YouTubeセクション ---
# 本人の予定表置き場(フリーチャットの枠)を埋め込み表示します
# st.video()を使用することで、Streamlitが自動的にYouTube動画プレーヤーを埋め込みます
# 要件: 9.1
st.header("ふりちゃという名の予定表置き場", anchor="youtube_schedule")
st.video("https://www.youtube.com/watch?v=LRowhAcHngc")
st.write("---")


# --- お知らせ・グッズ・活動の記録 ---
st.header("お知らせ・グッズ・活動の記録", anchor="news")
st.markdown(
    f"""
    お知らせ(グッズ・ボイスの販売など)、これまでの活動の記録(略歴・出演イベント)、オリジナル曲の一覧は、
    [ななしいんく 非公式Wiki の幽音しののページ]({WIKI_URL})にまとまっています。

    最新のお知らせは、[幽音しのさんの X](https://x.com/Shino_Kasukane_)と
    [公式サイト](https://www.774.ai/talent/shino-kasukane)をご覧ください。
    """
)
st.write("---")

# --- フッター ---
display_footer()
