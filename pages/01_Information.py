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
st.subheader("予定表ポスト")

# Twitterからコピーした特定のツイートの埋め込みコード
# このコードを<div>タグで囲み、中央寄せのスタイルを適用します。
tweet_embed_code = """
<div style="display: flex; justify-content: center; width: 100%;">
    <blockquote class="twitter-tweet" data-lang="ja">
        <p lang="ja" dir="ltr">📢スケジュール変更<br><br>👻明日からショート投稿を１９：００→１８：００に変更<br><br>👻今日配信→休み<br><br>👻７日休み→配信あり<br><br>になっていますーー🫡<br>７日がどこかしらで配信できそうなので<br>本日は作業Day にさせてもらうね！ <a href="https://t.co/Dh9XiCPVZc">pic.twitter.com/Dh9XiCPVZc</a></p>&mdash; 幽音しの👻🫧ななしいんく (@Shino_Kasukane_) <a href="https://twitter.com/Shino_Kasukane_/status/1930229052465655983?ref_src=twsrc%5Etfw">June 4, 2025</a>
    </blockquote> 
</div>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
"""

components.html(
    tweet_embed_code,
    height=850,  # ツイートの長さや画像・動画の有無によって調整
    scrolling=True,  # 必要に応じてスクロールを有効にする
)

st.markdown("---")
st.caption("Streamlit アプリケーション by Gemini")
st.caption(
    "本サイトに関する質問・バグの報告などは[@kajuen_kajuen](https://x.com/kajuen_kajuen)までお願いします。"
)
