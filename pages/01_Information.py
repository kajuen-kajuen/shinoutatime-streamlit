"""
情報ページモジュール

このモジュールは「しのうたタイム」アプリケーションの情報ページを提供します。
配信スケジュール、お知らせ情報、Twitter投稿の埋め込み表示などを行います。

主な機能:
- YouTube動画の埋め込み表示（配信スケジュール）
- Twitter投稿の埋め込み表示（WEEKLY SCHEDULE）
- 過去のお知らせ情報の展開可能な表示

要件: 9.1-9.6
"""

import streamlit as st
import streamlit.components.v1 as components
import os
from src.ui.components.footer import display_footer  # footer.pyから関数をインポート
from src.ui.components import render_twitter_embed  # UIコンポーネントをインポート

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
    - [WEEKLY SCHEDULE](#weekly_schedule)
    - [過去のInformation](#past_information)
    """
)
st.write("---")





# --- YouTubeセクション ---
# 配信スケジュールを示すYouTube動画を埋め込み表示します
# st.video()を使用することで、Streamlitが自動的にYouTube動画プレーヤーを埋め込みます
# 要件: 9.1
st.header("ふりちゃという名の予定表置き場", anchor="youtube_schedule")
st.video("https://www.youtube.com/watch?v=LRowhAcHngc")
st.write("---")


# --- WEEKLY SCHEDULEセクション ---
# Twitter投稿の埋め込み表示により、週間スケジュールを表示します
# 要件: 9.2, 9.3, 9.4
st.header("WEEKLY SCHEDULE", anchor="weekly_schedule")

# 現在のファイルのディレクトリを基準に、dataディレクトリ内のファイルパスを構築
base_dir = os.path.dirname(__file__)
tweet_file_path = os.path.join(base_dir, "..", "data", "tweet_embed_code.html")
tweet_height_file_path = os.path.join(base_dir, "..", "data", "tweet_height.txt")

# UIコンポーネントを使用してTwitter埋め込みを表示
render_twitter_embed(tweet_file_path, tweet_height_file_path)
st.write("---")


# --- ヘルパー関数 ---
def render_past_tweet(title: str, embed_code: str, height: int = 800) -> None:
    """
    過去のお知らせのTwitter埋め込みを表示する
    
    Args:
        title: お知らせのタイトル
        embed_code: Twitter埋め込みHTMLコード
        height: 表示高さ（ピクセル単位、デフォルト: 800）
    """
    st.subheader(title)
    
    # 3カラムレイアウトで中央に表示
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        components.html(embed_code, height=height, scrolling=True)


# --- 過去のInformationセクション ---
# st.expander を使用して、クリックで開閉できるセクションを作成
# 過去のお知らせ情報を展開可能な形式で表示します
# 要件: 9.6
with st.expander("過去のInformationはこちら"):
    # このアンカーは目次からのリンクのために設定
    st.subheader("", anchor="past_information")
    
    # TODO: 秋ボイス
    # TODO: From now on リリース
    
    # 誕生日グッズ発売のお知らせ
    render_past_tweet(
        "【2025/09/20】誕生日グッズ発売（～10月4日(土) 23:59まで）",
        """
        <blockquote class="twitter-tweet"><p lang="ja" dir="ltr">┈┈┈┈✧ 🎂 ✧┈┈┈┈<br>　　👻<a href="https://twitter.com/hashtag/%E5%B9%BD%E9%9F%B3%E3%81%97%E3%81%AE?src=hash&amp;ref_src=twsrc%5Etfw">#幽音しの</a> 🫧<br>　誕生日グッズが発売❕<br> ┈┈┈┈┈┈┈┈┈┈┈<br>全部セットには直筆サイン＆<br>メッセージ入りポストカード付🖊ღ✦<br><br>▼ ご購入はこちら<br>￤🛒 <a href="https://t.co/fdcGLXeI35">https://t.co/fdcGLXeI35</a><br>￤📅 ～ 10月4日(土) 23:59 <a href="https://t.co/kNjLJfoHo3">pic.twitter.com/kNjLJfoHo3</a></p>&mdash; ななしいんく公式🍩 (@774inc_official) <a href="https://twitter.com/774inc_official/status/1969056913905127628?ref_src=twsrc%5Etfw">September 19, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
        """
    )
    
    # 夏ボイス販売のお知らせ
    render_past_tweet(
        "【2025/07/22】ななしいんく夏ボイス販売（～8月31日(日) 23:59まで）",
        """
        <blockquote class="twitter-tweet"><p lang="ja" dir="ltr">☀️⁺‧┈┈┈┈┈┈┈┈┈┈‧⁺<br> 　<a href="https://twitter.com/hashtag/%E3%81%AA%E3%81%AA%E3%81%97%E3%81%84%E3%82%93%E3%81%8F%E5%A4%8F%E3%83%9C%E3%82%A4%E3%82%B9?src=hash&amp;ref_src=twsrc%5Etfw">#ななしいんく夏ボイス</a><br>⁺‧┈┈┈┈┈┈┈┈┈┈┈‧⁺☀️<a href="https://twitter.com/hashtag/%E3%81%AA%E3%81%AA%E3%81%97%E3%81%84%E3%82%93%E3%81%8F?src=hash&amp;ref_src=twsrc%5Etfw">#ななしいんく</a> と四季を過ごす<br>期間限定❕季節ボイスが発売🏫⟡<br>￤🛒 <a href="https://t.co/TrfzfYCNjM">https://t.co/TrfzfYCNjM</a><br>￤📅 ～8月31日(日) 23:59まで<br><br>メンバーとどんな夏を過ごしますか❔💭 <a href="https://t.co/0CdPAdmYe8">pic.twitter.com/0CdPAdmYe8</a></p>&mdash; ななしいんく公式🍩 (@774inc_official) <a href="https://twitter.com/774inc_official/status/1947491819123790119?ref_src=twsrc%5Etfw">July 22, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>     
        """
    )
    
    # オフィシャルグッズ受注販売のお知らせ
    render_past_tweet(
        "【2025/06/27】オフィシャルグッズ受注販売（～7月11日(金) 23:59まで）",
        """
        <blockquote class="twitter-tweet"><p lang="ja" dir="ltr">┈┈┈┈┈✧ 🎁 ✧┈┈┈┈<br>　 新オフィシャルグッズ<br>　 受注販売開始❕<br>┈┈┈┈┈┈┈┈┈┈┈┈┈<br>待望の初グッズがついに登場📣ˎˊ˗<br>この機会をお見逃しなく👀✧<a href="https://twitter.com/hashtag/%E5%A4%A9%E7%B5%86%E3%81%95%E3%81%95%E3%81%AF?src=hash&amp;ref_src=twsrc%5Etfw">#天絆ささは</a><a href="https://twitter.com/hashtag/%E5%B9%BD%E9%9F%B3%E3%81%97%E3%81%AE?src=hash&amp;ref_src=twsrc%5Etfw">#幽音しの</a><a href="https://twitter.com/hashtag/%E7%BE%BD%E6%B5%81%E9%B7%B2%E3%82%8A%E3%82%8A%E3%82%8A?src=hash&amp;ref_src=twsrc%5Etfw">#羽流鷲りりり</a><br><br>▼ ご購入はこちら<br>￤🛒<a href="https://t.co/fdcGLXffSD">https://t.co/fdcGLXffSD</a><br>￤📅 ～ 7月11日(金) 23:59まで <a href="https://t.co/jzPc4prw5B">pic.twitter.com/jzPc4prw5B</a></p>&mdash; ななしいんく公式🍩 (@774inc_official) <a href="https://twitter.com/774inc_official/status/1938561806253052194?ref_src=twsrc%5Etfw">June 27, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
        """
    )

st.write("---")

# --- フッター ---
display_footer()
