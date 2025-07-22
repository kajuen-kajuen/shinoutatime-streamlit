import streamlit as st
import streamlit.components.v1 as components
import os
from footer import display_footer # footer.pyから関数をインポート

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


# --- 関数定義 ---
def display_embedded_tweet(embed_code_path, height_path, default_height=850):
    """
    ファイルからTwitterの埋め込みコードと高さを読み込み、中央カラムに表示する関数。

    Args:
        embed_code_path (str): 埋め込みコードが書かれたHTMLファイルのパス。
        height_path (str): 高さが書かれたテキストファイルのパス。
        default_height (int, optional): デフォルトの高さ。
    """
    tweet_embed_code = ""
    tweet_height = default_height

    # 埋め込みコードのファイルを読み込む
    try:
        with open(embed_code_path, "r", encoding="utf-8") as f:
            tweet_embed_code = f.read()
    except FileNotFoundError:
        # ファイルが見つからない場合は、エラーではなく情報メッセージを表示する
        st.info(f"情報: 表示するコンテンツがありません。（{os.path.basename(embed_code_path)}）")
        return

    # 高さ設定ファイルを読み込む
    try:
        with open(height_path, "r", encoding="utf-8") as f:
            height_str = f.read().strip()
            if height_str.isdigit():
                tweet_height = int(height_str)
            else:
                st.warning(f"警告: '{height_path}' に無効な高さが指定されています。デフォルト値 ({default_height}px) を使用します。")
    except FileNotFoundError:
        # ファイルがない場合は警告を出さず、デフォルト値で続行する
        pass
    except Exception as e:
        st.warning(f"警告: 高さ設定ファイルの読み込み中にエラーが発生しました: {e}。デフォルト値 ({default_height}px) を使用します。")

    # 画面レイアウトを3つのカラムに分割し、中央にコンテンツを配置
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if tweet_embed_code:
            components.html(
                tweet_embed_code,
                height=tweet_height,
                scrolling=True,
            )
        else:
            # 埋め込みコードが空だった場合の情報メッセージ
            st.info("Twitterの埋め込み情報が読み込まれませんでした。")


# --- YouTubeセクション ---
st.header("ふりちゃという名の予定表置き場", anchor="youtube_schedule")
st.video("https://www.youtube.com/watch?v=LRowhAcHngc")
st.write("---")


# --- WEEKLY SCHEDULEセクション ---
st.header("WEEKLY SCHEDULE", anchor="weekly_schedule")

base_dir = os.path.dirname(__file__)
tweet_file_path = os.path.join(base_dir, "..", "data", "tweet_embed_code.html")
tweet_height_file_path = os.path.join(base_dir, "..", "data", "tweet_height.txt")

display_embedded_tweet(tweet_file_path, tweet_height_file_path)
st.write("---")


# --- 過去のInformationセクション ---
# st.expander を使用して、クリックで開閉できるセクションを作成
with st.expander("過去のInformationはこちら"):
    # このアンカーは目次からのリンクのために設定
    st.subheader("", anchor="past_information") 
    
    # --- 日付の見出し (親) ---
    st.subheader("2025/06/27")

    # --- オフィシャルグッズ受注販売セクション（子） ---
    # Markdownを使って、より小さいレベルの見出しを作成
    st.markdown("#### オフィシャルグッズ受注販売（～ 7月11日(金) 23:59まで）")
    
    goods_tweet_embed_code = """
    <blockquote class="twitter-tweet"><p lang="ja" dir="ltr">┈┈┈┈┈✧ 🎁 ✧┈┈┈┈<br>　 新オフィシャルグッズ<br>　 受注販売開始❕<br>┈┈┈┈┈┈┈┈┈┈┈┈┈<br>待望の初グッズがついに登場📣ˎˊ˗<br>この機会をお見逃しなく👀✧<a href="https://twitter.com/hashtag/%E5%A4%A9%E7%B5%86%E3%81%95%E3%81%95%E3%81%AF?src=hash&amp;ref_src=twsrc%5Etfw">#天絆ささは</a><a href="https://twitter.com/hashtag/%E5%B9%BD%E9%9F%B3%E3%81%97%E3%81%AE?src=hash&amp;ref_src=twsrc%5Etfw">#幽音しの</a><a href="https://twitter.com/hashtag/%E7%BE%BD%E6%B5%81%E9%B7%B2%E3%82%8A%E3%82%8A%E3%82%8A?src=hash&amp;ref_src=twsrc%5Etfw">#羽流鷲りりり</a><br><br>▼ ご購入はこちら<br>￤🛒<a href="https://t.co/fdcGLXffSD">https://t.co/fdcGLXffSD</a><br>￤� ～ 7月11日(金) 23:59まで <a href="https://t.co/jzPc4prw5B">pic.twitter.com/jzPc4prw5B</a></p>&mdash; ななしいんく公式🍩 (@774inc_official) <a href="https://twitter.com/774inc_official/status/1938561806253052194?ref_src=twsrc%5Etfw">June 27, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """
    
    g_col1, g_col2, g_col3 = st.columns([1, 2, 1])
    with g_col2:
        components.html(
            goods_tweet_embed_code,
            height=800,
            scrolling=True,
        )

st.write("---")

# --- フッター ---
display_footer()
