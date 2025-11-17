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
    
    この関数は、外部ファイルからTwitterの埋め込みHTMLコードと表示高さを読み込み、
    Streamlitの3カラムレイアウトの中央に表示します。ファイルが見つからない場合や
    読み込みエラーが発生した場合は、適切なメッセージを表示します。

    Args:
        embed_code_path (str): 埋め込みコードが書かれたHTMLファイルのパス。
                              Twitter公式の埋め込みコードを含むHTMLファイルを指定します。
        height_path (str): 高さが書かれたテキストファイルのパス。
                          表示高さ（ピクセル単位）を整数値で記述したファイルを指定します。
        default_height (int, optional): デフォルトの高さ（ピクセル単位）。
                                       高さ設定ファイルが見つからない場合や無効な値の場合に使用されます。
                                       デフォルトは850ピクセル。

    Returns:
        None: この関数は戻り値を返しません。Streamlitコンポーネントとして直接表示します。

    Raises:
        FileNotFoundError: 埋め込みコードファイルが見つからない場合、情報メッセージを表示して終了します。
                          高さ設定ファイルが見つからない場合は、デフォルト値を使用して続行します。
        Exception: 高さ設定ファイルの読み込み中にエラーが発生した場合、警告メッセージを表示し、
                  デフォルト値を使用して続行します。

    使用例:
        display_embedded_tweet("data/tweet_embed_code.html", "data/tweet_height.txt", 850)
    
    要件: 9.2, 9.3, 9.4, 9.5
    """
    # 変数の初期化
    tweet_embed_code = ""
    tweet_height = default_height

    # 埋め込みコードのファイルを読み込む
    # Twitter公式の埋め込みHTMLコードを外部ファイルから取得します
    try:
        with open(embed_code_path, "r", encoding="utf-8") as f:
            tweet_embed_code = f.read()
    except FileNotFoundError:
        # ファイルが見つからない場合は、エラーではなく情報メッセージを表示する
        st.info(f"情報: 表示するコンテンツがありません。（{os.path.basename(embed_code_path)}）")
        return

    # 高さ設定ファイルを読み込む
    # 埋め込みコンポーネントの表示高さをピクセル単位で取得します
    try:
        with open(height_path, "r", encoding="utf-8") as f:
            height_str = f.read().strip()
            # 数値として有効かチェック
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
    # 比率 [1, 2, 1] により、中央カラムが最も広くなり、コンテンツが中央に表示されます
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if tweet_embed_code:
            # Streamlitのcomponents.htmlを使用してTwitter埋め込みコードを表示
            # scrolling=Trueにより、コンテンツが高さを超える場合にスクロール可能になります
            components.html(
                tweet_embed_code,
                height=tweet_height,
                scrolling=True,
            )
        else:
            # 埋め込みコードが空だった場合の情報メッセージ
            st.info("Twitterの埋め込み情報が読み込まれませんでした。")


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

# Twitter埋め込み表示関数を呼び出し
display_embedded_tweet(tweet_file_path, tweet_height_file_path)
st.write("---")


# --- 過去のInformationセクション ---
# st.expander を使用して、クリックで開閉できるセクションを作成
# 過去のお知らせ情報を展開可能な形式で表示します
# 要件: 9.6
with st.expander("過去のInformationはこちら"):
    # このアンカーは目次からのリンクのために設定
    st.subheader("", anchor="past_information") 
    
    # --- 日付とグッズ情報を1行の見出しに統合 ---
    # 各お知らせは日付とタイトルを含む見出しで表示されます

    # TODO: 秋ボイス
    # TODO: From now on リリース

    st.subheader("【2025/09/20】誕生日グッズ発売（～10月4日(土) 23:59まで）")
    
    # Twitter埋め込みコードを直接記述
    # 過去のお知らせは外部ファイルではなく、コード内に直接記述されています
    tweet_embed_code = """
    <blockquote class="twitter-tweet"><p lang="ja" dir="ltr">┈┈┈┈✧ 🎂 ✧┈┈┈┈<br>　　👻<a href="https://twitter.com/hashtag/%E5%B9%BD%E9%9F%B3%E3%81%97%E3%81%AE?src=hash&amp;ref_src=twsrc%5Etfw">#幽音しの</a> 🫧<br>　誕生日グッズが発売❕<br> ┈┈┈┈┈┈┈┈┈┈┈<br>全部セットには直筆サイン＆<br>メッセージ入りポストカード付🖊ღ✦<br><br>▼ ご購入はこちら<br>￤🛒 <a href="https://t.co/fdcGLXeI35">https://t.co/fdcGLXeI35</a><br>￤📅 ～ 10月4日(土) 23:59 <a href="https://t.co/kNjLJfoHo3">pic.twitter.com/kNjLJfoHo3</a></p>&mdash; ななしいんく公式🍩 (@774inc_official) <a href="https://twitter.com/774inc_official/status/1969056913905127628?ref_src=twsrc%5Etfw">September 19, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """

    # 3カラムレイアウトで中央に表示
    g_col1, g_col2, g_col3 = st.columns([1, 2, 1])
    with g_col2:
        # Twitter埋め込みコードをHTMLコンポーネントとして表示
        components.html(
            tweet_embed_code,
            height=800,
            scrolling=True,
        )

    st.subheader("【2025/07/22】ななしいんく夏ボイス販売（～8月31日(日) 23:59まで）")
    
    # 夏ボイス販売のお知らせ用Twitter埋め込みコード
    tweet_embed_code = """
    <blockquote class="twitter-tweet"><p lang="ja" dir="ltr">☀️⁺‧┈┈┈┈┈┈┈┈┈┈‧⁺<br> 　<a href="https://twitter.com/hashtag/%E3%81%AA%E3%81%AA%E3%81%97%E3%81%84%E3%82%93%E3%81%8F%E5%A4%8F%E3%83%9C%E3%82%A4%E3%82%B9?src=hash&amp;ref_src=twsrc%5Etfw">#ななしいんく夏ボイス</a><br>⁺‧┈┈┈┈┈┈┈┈┈┈┈‧⁺☀️<a href="https://twitter.com/hashtag/%E3%81%AA%E3%81%AA%E3%81%97%E3%81%84%E3%82%93%E3%81%8F?src=hash&amp;ref_src=twsrc%5Etfw">#ななしいんく</a> と四季を過ごす<br>期間限定❕季節ボイスが発売🏫⟡<br>￤🛒 <a href="https://t.co/TrfzfYCNjM">https://t.co/TrfzfYCNjM</a><br>￤📅 ～8月31日(日) 23:59まで<br><br>メンバーとどんな夏を過ごしますか❔💭 <a href="https://t.co/0CdPAdmYe8">pic.twitter.com/0CdPAdmYe8</a></p>&mdash; ななしいんく公式🍩 (@774inc_official) <a href="https://twitter.com/774inc_official/status/1947491819123790119?ref_src=twsrc%5Etfw">July 22, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>     
    """
    
    # 3カラムレイアウトで中央に表示
    g_col1, g_col2, g_col3 = st.columns([1, 2, 1])
    with g_col2:
        # Twitter埋め込みコードをHTMLコンポーネントとして表示
        components.html(
            tweet_embed_code,
            height=800,
            scrolling=True,
        )

    st.subheader("【2025/06/27】オフィシャルグッズ受注販売（～7月11日(金) 23:59まで）")
    
    # オフィシャルグッズ販売のお知らせ用Twitter埋め込みコード
    goods_tweet_embed_code = """
    <blockquote class="twitter-tweet"><p lang="ja" dir="ltr">┈┈┈┈┈✧ 🎁 ✧┈┈┈┈<br>　 新オフィシャルグッズ<br>　 受注販売開始❕<br>┈┈┈┈┈┈┈┈┈┈┈┈┈<br>待望の初グッズがついに登場📣ˎˊ˗<br>この機会をお見逃しなく👀✧<a href="https://twitter.com/hashtag/%E5%A4%A9%E7%B5%86%E3%81%95%E3%81%95%E3%81%AF?src=hash&amp;ref_src=twsrc%5Etfw">#天絆ささは</a><a href="https://twitter.com/hashtag/%E5%B9%BD%E9%9F%B3%E3%81%97%E3%81%AE?src=hash&amp;ref_src=twsrc%5Etfw">#幽音しの</a><a href="https://twitter.com/hashtag/%E7%BE%BD%E6%B5%81%E9%B7%B2%E3%82%8A%E3%82%8A%E3%82%8A?src=hash&amp;ref_src=twsrc%5Etfw">#羽流鷲りりり</a><br><br>▼ ご購入はこちら<br>￤🛒<a href="https://t.co/fdcGLXffSD">https://t.co/fdcGLXffSD</a><br>￤📅 ～ 7月11日(金) 23:59まで <a href="https://t.co/jzPc4prw5B">pic.twitter.com/jzPc4prw5B</a></p>&mdash; ななしいんく公式🍩 (@774inc_official) <a href="https://twitter.com/774inc_official/status/1938561806253052194?ref_src=twsrc%5Etfw">June 27, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """
    
    # 3カラムレイアウトで中央に表示
    g_col1, g_col2, g_col3 = st.columns([1, 2, 1])
    with g_col2:
        # Twitter埋め込みコードをHTMLコンポーネントとして表示
        components.html(
            goods_tweet_embed_code,
            height=800,
            scrolling=True,
        )

st.write("---")

# --- フッター ---
display_footer()
