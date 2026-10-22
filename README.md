# しのうたタイム👻🫧

VTuber「幽音しの」さんの配信で歌唱された楽曲を検索・閲覧できる非公式ファンサイトです。

## 概要

「しのうたタイム」は、VTuber「幽音しの」さんのYouTubeライブ配信で歌唱された楽曲のデータベースアプリケーションです。ファンの皆様が、過去の配信で歌われた楽曲を簡単に検索し、該当箇所から視聴できるようにすることを目的としています。

**重要**: 本サイトは非公式ファンサイトであり、幽音しのさんご本人および所属事務所とは一切関係ありません。

## 主な機能

### 🔍 楽曲検索機能
- **キーワード検索**: 曲名、アーティスト名で楽曲を検索(かなの読みでも当たる。例: 「かいじゅう」で「怪獣の花唄」)
- **ライブタイトル検索**: 配信タイトルからも検索可能（オプション）
- **部分一致検索**: 大文字小文字・全角半角・カタカナとひらがな・空白の有無を区別せず、柔軟に検索。Enter キーでも検索できる
- **検索結果の表示**: 配信日、No.(配信の中の曲順。同じ日に配信が複数あれば「1-3」)、曲名、アーティスト、種類(配信・ショート・動画・投稿)、リンクを一覧表示
- **データの時点**: 「データは YYYY/MM/DD の配信まで(歌唱 N 件)」を検索欄の上に表示
- メンバー限定の配信は載せない

### 📊 段階的表示機能
- 初期表示は25件に制限し、高速な読み込みを実現
- 「さらに25件表示」ボタンで25件ずつ追加表示
- 現在の表示件数と総件数を常に表示

### 🎬 歌唱箇所へのリンク
- YouTube は歌い始めの時刻付きのリンク(「YouTubeへ👻」)。クリックするだけで、その曲のところから視聴できる
- X の投稿(「Xへ👻」)・Z-aN(「Z-aNへ👻」)は時刻を指定できないので、投稿・ページへのリンク

### 📋 楽曲リスト表示機能
- 全楽曲を1曲1行で、アーティストの読み → 曲名の読みの順に一覧表示(25件ずつ)
- その曲の最新の歌唱(切り抜きを除く)へのリンク付き
- β版として提供中

### 📢 情報ページ機能
- 配信の予定表(ふりちゃ)の動画
- 今週のスケジュール(本人の X の投稿の埋め込み。毎週更新)
- お知らせ・グッズ・活動の記録は、ななしいんく 非公式Wiki・本人の X・公式サイトへの案内

使い方の詳細は [ユーザーガイド](docs/guides/user-guide.md)、よくある質問は [FAQ](docs/faq.md) にあります。

## はじめかた(開発する人向け)

Docker Desktop と Git があれば動きます。コマンドは Git Bash で打ちます。

```bash
git clone https://github.com/kajuen-kajuen/shinoutatime-streamlit.git
cd shinoutatime-streamlit
docker compose up -d                                  # http://localhost:8501 で開く
docker compose exec shinouta-time pytest tests/e2e -q # 本物の data/v2/ でページを起動・検索できるか確かめる
```

- 環境変数(ログ・取り込みの API キー)、確かめ方、止め方は [SETUP.md](SETUP.md)。困ったときは [TROUBLESHOOTING.md](TROUBLESHOOTING.md)。
- 開発の決まり(ブランチ・コミット・テスト)は [CONTRIBUTING.md](CONTRIBUTING.md)。AI エージェントは [CLAUDE.md](CLAUDE.md) から読みます。

## データ

画面が読むのは `data/v2/` の5つのテーブル(contents・artists・songs・performances・aliases。UTF-8・タブ区切り)です。形は [データモデル v2](docs/specs/data-model.md) にあります。

- 歌唱の追加は、取り込みの CLI(`ingest`・`data`)で行います。TSV を手で編集しません。手順は [`docs/prompts/update-data.md`](docs/prompts/update-data.md)、コマンドは [`docs/prompts/_commands.md`](docs/prompts/_commands.md)。
- 曲の無いコンテンツは `data/ingest/skipped.tsv` に記録します。取得したコメントと下書き(`data/ingest/cache/`・`staged/`)は Git に入れません。
- v1 のデータ(`data/*.TSV`・`data/data.xlsx`)とその道具は、2026-10-23 のフェーズ3で消しました(Git の履歴に残ります)。古い手順は [`docs/archive/`](docs/archive/README.md) にあります。

## プロジェクト構造

```
.
├── Home.py                 # 入口(Home の本体は src/ui/pages/home_page.py)
├── pages/                  # ほかのページ(Information・About Us・Song List beta)
├── src/
│   ├── ui/                 # 画面の部品・ページの準備・style.css・v2 のデータの読み込み(キャッシュ付き)
│   ├── core/               # v2 の集計(views.py)・検査・データの操作・文字列・リンク
│   ├── repositories/       # v2 の TSV の読み書き(table_repository.py)・X の埋め込みコードの保存
│   ├── models/             # v2 のテーブルの定義(schema.py)
│   ├── ingest/             # v2 の取り込み(YouTube API・コメントの解析・下書き・曲なしの記録)
│   ├── cli/                # ingest・data(v2)・twitter_embed_cli(今週のスケジュール)
│   ├── config/             # 設定(環境変数 SHINOUTA_*)とログ
│   └── services/ clients/ exceptions/ utils/
├── data/
│   ├── v2/                 # 画面が読むデータ(正本)
│   ├── ingest/             # skipped.tsv(cache/・staged/ は Git 管理外)
│   └── tweet_*             # Information の今週のスケジュール(X の埋め込み)
├── tests/                  # unit(v2 は unit/v2、画面は unit/ui)・property・integration・e2e・performance
├── tools/                  # check-rules.sh(絶対制約の確認)・wake_up_streamlit.py(本番のスリープ防止)
├── docs/                   # 文書(一覧は docs/README.md)
├── Dockerfile・docker-compose.yml
└── requirements.txt・requirements-tools.txt・requirements-dev.txt
```

層とデータの流れ・エラー・キャッシュは [構成の概要](docs/architecture/overview.md) にあります。

## 技術スタック

- **言語・画面**: Python 3.14、[Streamlit](https://streamlit.io/) 1.66、pandas
- **データ**: TSV(UTF-8・タブ区切り)。データベースは使わない
- **取り込み**: YouTube Data API v3(取り込みの CLI だけが使う。画面は外部の API を使わない)
- **動かす場所**: 手元は Docker(`python:3.14.8-slim-trixie`)、公開は Streamlit Community Cloud(`main` → 本番、`develop` → stg)
- **依存**: `==` で固定し、`requirements.txt`(本番)・`requirements-tools.txt`(データの CLI)・`requirements-dev.txt`(テスト。コンテナはこれを入れる)に分ける

## ドキュメント

| 文書 | 中身 |
|---|---|
| [ユーザーガイド](docs/guides/user-guide.md)・[FAQ](docs/faq.md) | サイトの使い方 |
| [SETUP.md](SETUP.md)・[TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 手元で動かす・困ったとき |
| [CONTRIBUTING.md](CONTRIBUTING.md)・[ブランチ戦略](docs/development/BRANCH_STRATEGY.md) | 開発の決まり・ブランチとリリース |
| [構成の概要](docs/architecture/overview.md)・[データモデル v2](docs/specs/data-model.md) | 構成とデータの形 |
| [データの取り込み](docs/prompts/update-data.md)・[コマンド集](docs/prompts/_commands.md) | 取り込みの手順とコマンド |
| [デプロイ](docs/deployment.md)・[テスト](docs/testing/README.md) | 公開の環境とスリープ防止・テストの流し方 |
| [docs/README.md](docs/README.md) | 文書の一覧 |

## 注意事項

### 非公式サイトについて
本サイトは非公式ファンサイトであり、幽音しのさんご本人および所属事務所とは一切関係ありません。公式情報については、公式チャンネルや公式の X をご確認ください。

### データの正確性について
本サイトのデータは、タイムスタンプ職人さんのコメントや X の投稿などをもとに、有志が確かめて登録しています。そのため、以下の点にご注意ください：

- **誤りの可能性**: 曲名・アーティストの誤りや、歌唱の漏れがある可能性があります
- **最新情報の反映遅延**: 更新は不定期です。どの配信まで入っているかは、Home の「データは YYYY/MM/DD の配信まで」で確かめられます

データに誤りを発見された場合は、各ページのフッターにある連絡先([@kajuen_kajuen](https://x.com/kajuen_kajuen))か、GitHub の Issue でお知らせください。

### 免責事項
本サイトの利用により生じたいかなる損害についても、制作者は一切の責任を負いません。データの正確性については保証いたしかねますので、あらかじめご了承ください。

## ライセンス

本プロジェクトは Apache License 2.0 のもとで公開されています。詳細は [LICENSE](LICENSE) ファイルをご確認ください。

## 謝辞

本サイトの制作にあたり、多くのファンの皆様からの情報提供や協力をいただきました。この場を借りて感謝申し上げます。

---

**制作**: ファン有志  
**対象VTuber**: 幽音しの（[@Shino_Kasukane_](https://x.com/Shino_Kasukane_)）  
**公式YouTubeチャンネル**: [幽音しの / Shino Kasukane](https://www.youtube.com/@Shino_Kasukane)
