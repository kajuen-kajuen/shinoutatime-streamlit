import streamlit as st
import streamlit.components.v1 as components
import os
from footer import display_footer  # ★ここを追加★

st.set_page_config(
    page_title="Information - しのうたタイム",
    page_icon="👻",
    layout="wide",
)

st.title("Information")

st.write("---")
st.subheader("オフィシャルグッズ受注販売（～ 7月11日(金) 23:59まで）")

# ここにTwitterからコピーした特定のツイートの埋め込みコードを貼り付けます
tweet_embed_code = """
<blockquote class="twitter-tweet"><p lang="ja" dir="ltr">┈┈┈┈┈✧ 🎁 ✧┈┈┈┈<br>　 新オフィシャルグッズ<br>　 受注販売開始❕<br>┈┈┈┈┈┈┈┈┈┈┈┈┈<br>待望の初グッズがついに登場📣ˎˊ˗<br>この機会をお見逃しなく👀✧<a href="https://twitter.com/hashtag/%E5%A4%A9%E7%B5%86%E3%81%95%E3%81%95%E3%81%AF?src=hash&amp;ref_src=twsrc%5Etfw">#天絆ささは</a><a href="https://twitter.com/hashtag/%E5%B9%BD%E9%9F%B3%E3%81%97%E3%81%AE?src=hash&amp;ref_src=twsrc%5Etfw">#幽音しの</a><a href="https://twitter.com/hashtag/%E7%BE%BD%E6%B5%81%E9%B7%B2%E3%82%8A%E3%82%8A%E3%82%8A?src=hash&amp;ref_src=twsrc%5Etfw">#羽流鷲りりり</a><br><br>▼ ご購入はこちら<br>￤🛒<a href="https://t.co/fdcGLXffSD">https://t.co/fdcGLXffSD</a><br>￤📅 ～ 7月11日(金) 23:59まで <a href="https://t.co/jzPc4prw5B">pic.twitter.com/jzPc4prw5B</a></p>&mdash; ななしいんく公式🍩 (@774inc_official) <a href="https://twitter.com/774inc_official/status/1938561806253052194?ref_src=twsrc%5Etfw">June 27, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> """

# 3つのカラムを作成：左の空白、中央のコンテンツ、右の空白
col1, col2, col3 = st.columns([1, 2, 1])  # 割合を調整して中央のカラムの幅を決めます

with col2:  # 中央のカラムにコンテンツを配置
    if tweet_embed_code:
        components.html(
            tweet_embed_code,
            height=800,
            scrolling=True,
        )
    else:
        st.info("Twitterの埋め込み情報が読み込まれませんでした。")

# YouTube動画のURLを指定 (前回のコードからそのまま)
youtube_url = "https://www.youtube.com/watch?v=LRowhAcHngc"

st.write("---")
st.subheader("ふりちゃという名の予定表置き場")
st.video(youtube_url)

st.write("---")
st.subheader("WEEKLY SCHEDULE")

# Twitterの埋め込みコードが記載されたファイルを読み込む
# footer.pyがHome.pyと同じ階層にあるので、親ディレクトリを一つ上がる
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
    tweet_embed_code = ""

# 高さの値を読み込む
tweet_height = 850  # デフォルト値（ファイルが見つからない場合や読み込みエラーの場合）
try:
    with open(tweet_height_file_path, "r", encoding="utf-8") as f:
        height_str = f.read().strip()
        if height_str.isdigit():
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

# --- ここから変更 ---
# 3つのカラムを作成：左の空白、中央のコンテンツ、右の空白
col1, col2, col3 = st.columns([1, 2, 1])  # 割合を調整して中央のカラムの幅を決めます

with col2:  # 中央のカラムにコンテンツを配置
    if tweet_embed_code:
        components.html(
            tweet_embed_code,
            height=tweet_height,
            scrolling=True,
        )
    else:
        st.info("Twitterの埋め込み情報が読み込まれませんでした。")
# --- 変更ここまで ---

# st.markdown("---")
# st.caption("Streamlit アプリケーション by Gemini")
# st.caption(
#     "本サイトに関する質問・バグの報告などは[@kajuen_kajuen](https://x.com/kajuen_kajuen)までお願いします。"
# )
# ★上記の既存フッターコードを削除し、以下に置き換えます★

display_footer()  # ★ここを呼び出す★
