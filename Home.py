"""
しのうたタイム - メインページ

VTuber「幽音しの」さんの配信で歌唱された楽曲を検索・閲覧できる
非公式ファンサイトのメインページです。

主な機能:
- 歌唱の一覧の表示と、データの時点(いつの配信までか)の表示
- キーワード検索（曲名、アーティスト、読み、配信タイトル）。Enter キーかボタンで検索
- YouTubeタイムスタンプ付きリンク
- 段階的表示（25件ずつ）

データソース:
- data/v2/: データモデル v2 の5つの TSV(contents・artists・songs・performances・aliases)。
  表示は src/ui/pages/home_page.py(読み込みは src/ui/v2_data.py)
"""

from src.ui.page_setup import setup_page
from src.ui.pages.home_page import HomePage

# ページの準備(ログの初期化・ページ設定・共通の CSS・サイト名の見出し。全ページで共通)
config = setup_page()

if __name__ == "__main__":
    home_page = HomePage(config)  # setup_page が読んだ設定を渡す(読み直さない)
    home_page.run()
