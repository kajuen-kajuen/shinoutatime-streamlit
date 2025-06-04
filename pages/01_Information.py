import streamlit as st
import streamlit.components.v1 as components
import os  # ファイルパスを扱うためにosモジュールをインポート

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

# Twitterの埋め込みコードが記載されたファイルを読み込む
# ファイルパスは、このスクリプト（01_Information.py）からの相対パスで指定します。
# 01_Information.pyはpagesディレクトリにあるので、
# dataディレクトリのファイルは '../data/ファイル名' となります。
tweet_file_path = os.path.join(
    os.path.dirname(__file__), "..", "data", "tweet_embed_code.html"
)

try:
    with open(tweet_file_path, "r", encoding="utf-8") as f:
        tweet_embed_code = f.read()
except FileNotFoundError:
    st.error(
        f"エラー: Twitterの埋め込みコードファイルが見つかりません。パスを確認してください: {tweet_file_path}"
    )
    tweet_embed_code = ""  # エラー時に空文字列を設定

if tweet_embed_code:  # ファイルが正しく読み込まれた場合のみ表示
    components.html(
        tweet_embed_code,
        height=850,  # ツイートの長さや画像・動画の有無によって調整
        scrolling=True,  # 必要に応じてスクロールを有効にする
    )
else:
    st.info("Twitterの埋め込み情報が読み込まれませんでした。")

st.markdown("---")
st.caption("Streamlit アプリケーション by Gemini")
st.caption(
    "本サイトに関する質問・バグの報告などは[@kajuen_kajuen](https://x.com/kajuen_kajuen)までお願いします。"
)
