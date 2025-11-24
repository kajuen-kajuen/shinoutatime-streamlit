"""
テスト用のサンプルHTMLデータ

Twitter埋め込みコードのテストで使用するサンプルHTMLを定義します。
"""

# 有効なTwitter埋め込みHTML（基本形）
VALID_TWITTER_EMBED_HTML = """<blockquote class="twitter-tweet">
  <p lang="ja" dir="ltr">
    これはテスト用のツイートです。
    <a href="https://t.co/example">https://t.co/example</a>
  </p>
  &mdash; テストユーザー (@testuser) 
  <a href="https://twitter.com/testuser/status/1234567890123456789?ref_src=twsrc%5Etfw">
    January 1, 2024
  </a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>"""

# 有効なTwitter埋め込みHTML（高さ情報付き）
VALID_TWITTER_EMBED_HTML_WITH_HEIGHT = """<blockquote class="twitter-tweet" data-height="500">
  <p lang="ja" dir="ltr">
    高さ情報付きのテストツイートです。
  </p>
  &mdash; テストユーザー (@testuser) 
  <a href="https://twitter.com/testuser/status/1234567890123456789?ref_src=twsrc%5Etfw">
    January 1, 2024
  </a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>"""

# 無効なHTML（blockquoteタグ欠落）
INVALID_HTML_MISSING_BLOCKQUOTE = """<div class="twitter-tweet">
  <p lang="ja" dir="ltr">
    blockquoteタグがありません。
  </p>
  &mdash; テストユーザー (@testuser) 
  <a href="https://twitter.com/testuser/status/1234567890123456789?ref_src=twsrc%5Etfw">
    January 1, 2024
  </a>
</div>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>"""

# 無効なHTML（twitter-tweetクラス欠落）
INVALID_HTML_MISSING_CLASS = """<blockquote>
  <p lang="ja" dir="ltr">
    twitter-tweetクラスがありません。
  </p>
  &mdash; テストユーザー (@testuser) 
  <a href="https://twitter.com/testuser/status/1234567890123456789?ref_src=twsrc%5Etfw">
    January 1, 2024
  </a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>"""

# 無効なHTML（空のHTML）
INVALID_HTML_EMPTY = ""

# 無効なHTML（タグの不一致）
INVALID_HTML_MISMATCHED_TAGS = """<blockquote class="twitter-tweet">
  <p lang="ja" dir="ltr">
    タグが正しく閉じられていません。
  </p>
  &mdash; テストユーザー (@testuser) 
  <a href="https://twitter.com/testuser/status/1234567890123456789?ref_src=twsrc%5Etfw">
    January 1, 2024
  </a>
</div>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>"""

# 複数のツイート埋め込みHTML
MULTIPLE_TWEETS_HTML = """<blockquote class="twitter-tweet" data-height="400">
  <p lang="ja" dir="ltr">最初のツイート</p>
  <a href="https://twitter.com/user1/status/1111111111111111111?ref_src=twsrc%5Etfw">
    January 1, 2024
  </a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

<blockquote class="twitter-tweet" data-height="600">
  <p lang="ja" dir="ltr">2番目のツイート</p>
  <a href="https://twitter.com/user2/status/2222222222222222222?ref_src=twsrc%5Etfw">
    January 2, 2024
  </a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>"""

# 最小限の有効なHTML
MINIMAL_VALID_HTML = """<blockquote class="twitter-tweet"></blockquote>"""

# 特殊文字を含むHTML
HTML_WITH_SPECIAL_CHARS = """<blockquote class="twitter-tweet">
  <p lang="ja" dir="ltr">
    特殊文字のテスト: &lt; &gt; &amp; &quot; &#39;
    絵文字: 🎉 🎊 ✨
  </p>
  <a href="https://twitter.com/testuser/status/1234567890123456789?ref_src=twsrc%5Etfw">
    January 1, 2024
  </a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>"""
