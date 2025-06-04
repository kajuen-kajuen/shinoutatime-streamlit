import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Information - しのうたタイム",
    page_icon="👻",
    layout="wide",
)

st.title("Information")

# YouTube動画のURLを指定 (前回のコードからそのまま)
youtube_url = "https://www.youtube.com/watch?v=LRowhAcHngc"

st.write("---")
st.subheader("ふりちゃという名の予定表置き場")
st.video(youtube_url)

st.write("---")
st.subheader("特定のツイートの埋め込み")

# ここにTwitterからコピーした特定のツイートの埋め込みコードを貼り付けます
# 例としてStreamlitの公式ツイートを埋め込みます
tweet_embed_code = """
<blockquote class="twitter-tweet"><p lang="ja" dir="ltr">📢スケジュール変更<br><br>👻明日からショート投稿を１９：００→１８：００に変更<br><br>👻今日配信→休み<br><br>👻７日休み→配信あり<br><br>になっていますーー🫡<br>７日がどこかしらで配信できそうなので<br>本日は作業Day にさせてもらうね！ <a href="https://t.co/Dh9XiCPVZc">pic.twitter.com/Dh9XiCPVZc</a></p>&mdash; 幽音しの👻🫧ななしいんく (@Shino_Kasukane_) <a href="https://twitter.com/Shino_Kasukane_/status/1930229052465655983?ref_src=twsrc%5Etfw">June 4, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> 
"""

components.html(
    tweet_embed_code, height=1000
)  # heightはツイートの長さによって調整してください
