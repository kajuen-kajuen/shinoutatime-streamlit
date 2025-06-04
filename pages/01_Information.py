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
tweet_file_path = os.path.join(
    os.path.dirname(__file__), "..", "data", "tweet_embed_code.html"
)

# ツイートの高さを記述したファイルを読み込む
tweet_height_file_path = os.path.join(
    os.path.dirname(__file__), "..", "data", "tweet_height.txt"
)

try:
    with open(tweet_file_path, "r", encoding="utf-8") as f:
        tweet_embed_code = f.read()
except FileNotFoundError:
    st.error(
        f"エラー: Twitterの埋め込みコードファイルが見つかりません。パスを確認してください: {tweet_file_path}"
    )
    tweet_embed_code = ""  # エラー時に空文字列を設定

# 高さの値を読み込む
tweet_height = 850  # デフォルト値（ファイルが見つからない場合や読み込みエラーの場合）
try:
    with open(tweet_height_file_path, "r", encoding="utf-8") as f:
        height_str = f.read().strip()  # 前後の空白や改行を削除
        if height_str.isdigit():  # 読み込んだ文字列が数値かどうかをチェック
            tweet_height = int(height_str)
        else:
            st.warning(
                f"警告: '{tweet_height_file_path}' に無効な高さの値が指定されています。デフォルト値 {tweet_height} を使用します。"
            )
except FileNotFoundError:
    st.warning(
        f"警告: ツイートの高さ設定ファイルが見つかりません: {tweet_height_file_path}。デフォルト値 {tweet_height} を使用します。"
    )
except Exception as e:
    st.warning(
        f"警告: ツイートの高さ設定ファイルの読み込み中にエラーが発生しました: {e}。デフォルト値 {tweet_height} を使用します。"
    )


if tweet_embed_code:  # ファイルが正しく読み込まれた場合のみ表示
    components.html(
        tweet_embed_code,
        height=tweet_height,  # ファイルから読み込んだ高さを適用
        scrolling=True,  # 必要に応じてスクロールを有効にする
    )
else:
    st.info("Twitterの埋め込み情報が読み込まれませんでした。")

st.markdown("---")
st.caption("Streamlit アプリケーション by Gemini")
st.caption(
    "本サイトに関する質問・バグの報告などは[@kajuen_kajuen](https://x.com/kajuen_kajuen)までお願いします。"
)
