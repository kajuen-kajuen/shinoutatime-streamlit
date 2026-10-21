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
- お知らせ・グッズ・活動の記録は、ななしいんく 非公式Wiki・本人の X・公式サイトへの案内

使い方の詳細は [ユーザーガイド](docs/guides/user-guide.md)、よくある質問は [FAQ](docs/faq.md) にあります。

## セットアップ手順

本アプリケーションは、以下の2つの方法で環境構築が可能です：

1. **Docker Compose を使用する方法（推奨）** - ローカル環境を汚さず、簡単にセットアップ
2. **Python 仮想環境を使用する方法** - 従来の方法

### 方法の選択

| 方法 | メリット | デメリット |
|-----|---------|-----------|
| **Docker Compose（推奨）** | ・ローカル環境にPythonや依存パッケージをインストール不要<br>・本番環境（Python 3.14）と同じ環境を再現<br>・環境のクリーンアップが容易<br>・`docker compose up`コマンド一つで起動 | ・Dockerのインストールが必要<br>・初回起動時にイメージのビルドが必要 |
| **Python 仮想環境** | ・Dockerが不要<br>・軽量で高速 | ・ローカル環境にPython 3.14のインストールが必要<br>・依存パッケージの管理が必要<br>・環境の分離が不完全 |

**推奨**: ローカル環境を汚さず、本番環境と同じ構成で動作させるため、**Docker Compose を使用する方法**を推奨します。

---

### 方法1: Docker Compose を使用する（推奨）

#### 必要な環境
- **Docker Desktop** (Windows/Mac) または **Docker Engine** (Linux)
- **Git**

#### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd <repository-directory>
```

#### 2. Docker Compose で起動

```bash
docker compose up
```

初回起動時は、Dockerイメージのビルドが行われるため、数分かかる場合があります。

#### 3. 動作確認

環境が正しく構築されたことを確認するため、動作確認スクリプトを実行します：

**Mac/Linux:**
```bash
bash scripts/verify_environment.sh
```

**Windows:**
```cmd
scripts/verify_environment.bat
```

または、手動でテストを実行：

```bash
docker compose exec shinouta-time pytest tests/integration/test_environment_verification.py -v
```

全てのテストが成功すれば、環境構築は完了です。

#### 4. アプリケーションへのアクセス

起動後、ブラウザで `http://localhost:8501` にアクセスしてください。

#### 5. 停止とクリーンアップ

アプリケーションを停止するには、`Ctrl+C` を押してください。

コンテナを完全に削除するには：

```bash
docker compose down
```

#### 環境変数の設定（オプション）

`.env.example` ファイルを `.env` にコピーして、必要に応じて環境変数を編集できます：

```bash
cp .env.example .env
```

詳細は「ロギング設定（オプション）」セクションを参照してください。

#### トラブルシューティング

Docker Compose使用時の問題については、[TROUBLESHOOTING.md](TROUBLESHOOTING.md) を参照してください。

---

### 方法2: Python 仮想環境を使用する

> **注意**: このリポジトリの開発・テスト・データの取り込みは、**方法1(Docker)で行う決まり**です([`CONTRIBUTING.md`](CONTRIBUTING.md)・[`CLAUDE.md`](CLAUDE.md))。方法2は、手元で画面を見るだけのための参考です。AI エージェントは使いません。

#### 必要な環境
- **Python 3.14** (本番環境と同じバージョンを推奨)
- **pip** (Pythonパッケージマネージャー)

#### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd <repository-directory>
```

#### 2. Python仮想環境の作成とアクティベート

**Linux/Mac:**
```bash
python3.14 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. 依存パッケージのインストール

```bash
pip install -r requirements-dev.txt
```

依存は用途ごとに3つのファイルに分け、版を `==` で固定しています:
- `requirements.txt` - 本番（Streamlit Community Cloud）で使うもの。`streamlit`、`pandas` など
  - Cloud のビルドのたびに版が変わらないよう、間接の依存(`numpy`・`pyarrow` など)まで固定しています。直接の依存を上げたら、ファイルの中の手順で間接の依存も取り直してください
- `requirements-tools.txt` - データ生成の CLI で使うもの。`pykakasi`（読み）、`python-Levenshtein`（類似曲の検出）
- `requirements-dev.txt` - テストで使うもの。`pytest`、`hypothesis` など（上の2つも含む）

#### 4. アプリケーションの起動

```bash
streamlit run Home.py
```

起動後、ブラウザで `http://localhost:8501` にアクセスしてください。

#### 5. 仮想環境の終了

作業が終わったら、仮想環境を終了します：

```bash
deactivate
```

---

### 詳細なセットアップ手順

より詳細なセットアップ手順については、[SETUP.md](SETUP.md) を参照してください。

### 4. ロギング設定（オプション）

アプリケーションは標準でコンソールにログを出力します。環境変数を設定することで、ログレベルやファイル出力を制御できます。

#### 環境変数

| 環境変数名 | 説明 | デフォルト値 | 設定例 |
|-----------|------|------------|--------|
| `SHINOUTA_LOG_LEVEL` | ログレベル（DEBUG、INFO、WARNING、ERROR） | INFO | INFO |
| `SHINOUTA_ENABLE_FILE_LOGGING` | ファイルへのログ出力を有効化 | false | true |
| `SHINOUTA_LOG_FILE` | ログファイルのパス | logs/shinouta.log | logs/app.log |

#### 使用例

**開発環境（DEBUGレベル、ファイルログ有効）:**
```bash
export SHINOUTA_LOG_LEVEL=DEBUG
export SHINOUTA_ENABLE_FILE_LOGGING=true
streamlit run Home.py
```

**本番環境（INFOレベル、ファイルログ有効）:**
```bash
export SHINOUTA_LOG_LEVEL=INFO
export SHINOUTA_ENABLE_FILE_LOGGING=true
export SHINOUTA_LOG_FILE=logs/production.log
streamlit run Home.py
```

#### ログファイルのローテーション

ファイルログが有効な場合、以下の設定で自動的にローテーションされます：
- **最大ファイルサイズ**: 10MB
- **保持するバックアップ数**: 5個
- **ファイル名形式**: `shinouta.log`, `shinouta.log.1`, `shinouta.log.2`, ...

#### ログレベルの説明

- **DEBUG**: 詳細なデバッグ情報（開発時のみ推奨）
- **INFO**: 一般的な情報メッセージ（本番環境推奨）
- **WARNING**: 警告メッセージ
- **ERROR**: エラーメッセージ

## データ

画面が読むのは `data/v2/` の5つのテーブル(contents・artists・songs・performances・aliases。UTF-8・タブ区切り)です。形は [データモデル v2](docs/specs/data-model.md) にあります。

- 歌唱の追加は、取り込みの CLI(`ingest`・`data`)で行います。TSV を手で編集しません。手順は [`docs/prompts/update-data.md`](docs/prompts/update-data.md)、コマンドは [`docs/prompts/_commands.md`](docs/prompts/_commands.md)。
- 曲の無いコンテンツは `data/ingest/skipped.tsv` に記録します。取得したコメントと下書き(`data/ingest/cache/`・`staged/`)は Git に入れません。
- v1 のデータ(`data/*.TSV`・`data/data.xlsx`)は参照用に残しているだけで、画面はもう読みません(フェーズ3で消す予定)。古い手順は [`docs/archive/`](docs/archive/README.md) にあります。

## プロジェクト構造

```
.
├── .devcontainer/          # Dev Container設定
├── .github/                # GitHub設定
├── .streamlit/             # Streamlit設定
├── .claude/skills/         # AI エージェント向けのスキルの入口(本体は docs/prompts/)
├── data/                   # データファイル
│   ├── v2/                 # v2 のテーブル(正本。画面が読む)
│   ├── ingest/             # 取り込み(skipped.tsv。cache/・staged/ は Git 管理外)
│   ├── backups/            # バックアップ(v1)
│   ├── data.xlsx           # 入力データ(v1)
│   └── *.TSV               # 生成されたTSVファイル(v1)
├── docs/                   # ドキュメント(一覧は docs/README.md)
│   ├── architecture/       # 構成の概要(overview.md)
│   ├── development/        # 開発関連ドキュメント
│   ├── guides/             # ガイド
│   ├── prompts/            # AI エージェント向けの手順(スキルの本体)
│   ├── specs/              # 仕様書(data-model.md など)
│   ├── testing/            # テスト関連
│   └── archive/            # 古い仕様
├── pages/                  # Streamlitページ(*_Admin.py・*_Preview.py はローカル専用)
├── scripts/                # 実行スクリプト
├── src/                    # ソースコード
│   ├── cli/                # CLIツール(v2 の ingest・data を含む)
│   ├── clients/            # 外部APIクライアント
│   ├── config/             # 設定
│   ├── core/               # コア機能(v2 の集計 views.py を含む)
│   ├── exceptions/         # 例外定義
│   ├── ingest/             # v2 の取り込み(YouTube API・コメントの解析・下書き・曲なしの記録)
│   ├── models/             # データモデル(v2 のテーブル定義 schema.py を含む)
│   ├── repositories/       # データアクセス層
│   ├── services/           # ビジネスロジック
│   ├── ui/                 # UI(components/・pages/・styles/)
│   └── utils/              # ユーティリティ
├── tests/                  # テスト
│   ├── e2e/                # ページの起動(Streamlit の AppTest)
│   ├── fixtures/           # テストフィクスチャ
│   ├── integration/        # 統合テスト
│   ├── performance/        # 性能テスト(--runslow のときだけ)
│   ├── property/           # プロパティベーステスト
│   └── unit/               # ユニットテスト(v2 は unit/v2)
├── tools/check-rules.sh    # 絶対制約の確認(読み取り専用)
├── .gitignore              # Git除外設定
├── docker-compose.yml      # Docker Compose設定
├── Dockerfile              # Dockerイメージ定義
├── Home.py                 # Streamlitメインページ
├── README.md               # プロジェクト概要
├── requirements.txt        # Python依存関係(本番。Streamlit Cloud はこれだけを読む)
├── requirements-tools.txt  # データ生成の CLI 用
└── requirements-dev.txt    # テスト用(コンテナはこれを入れる)
```

### モジュール構造の説明

本アプリケーションは、保守性とテスト可能性を向上させるため、レイヤー化されたアーキテクチャを採用しています。

#### srcディレクトリ

アプリケーションのコアロジックを格納するディレクトリです。各サブディレクトリは明確な責務を持ちます。

##### services/（ビジネスロジック層）

データ処理と検索機能を提供するサービスクラスを格納します。

- **data_service.py**: TSVファイルからのデータ読み込み、データ結合、エラーハンドリングを担当
  - `DataService`クラス: 配信データ、楽曲データ、楽曲リストデータの読み込みと結合
  - エラー発生時の適切なエラーメッセージ管理
  
- **search_service.py**: 検索機能を提供
  - `SearchService`クラス: キーワード検索、複数フィールド検索、大文字小文字を区別しない検索
  - 複数条件によるフィルタリング機能

- **song_list_service.py**: 楽曲リスト(Song List)の生成
  - `SongListService`クラス: 配信・楽曲データから `V_SONG_LIST.TSV` を作る(v1)

- **excel_to_tsv_service.py**・**twitter_embed_service.py**: Excel から TSV への変換(v1)と、Twitter 埋め込みコードの取得

##### core/（コア機能層）

データ処理パイプラインとユーティリティ関数を格納します。

- **data_pipeline.py**: データ処理の全体フローを管理
  - `DataPipeline`クラス: データ読み込み→結合→変換→ソートの一連の処理を実行
  - キャッシング機能による高速化
  - 各ステップの結果検証
  
- **utils.py**: 汎用的なユーティリティ関数
  - `convert_timestamp_to_seconds()`: タイムスタンプ文字列を秒数に変換
  - `generate_youtube_url()`: YouTubeタイムスタンプ付きURL生成
  - `generate_song_numbers()`: 曲目番号の自動生成
  - `convert_date_string()`: 日付文字列の変換

- **v2 の部品**(仕様は [`docs/specs/data-model.md`](docs/specs/data-model.md))
  - **views.py**: 歌唱の一覧と曲ごとの集計を、5つのテーブルから計算する
  - **validation.py**・**dataset_ops.py**: テーブルの検査と、値の修正・曲順の振り直し・まとめ
  - **text.py**・**links.py**: 照合用の文字列のならし・読みの並べ方と、リンクの組み立て

##### ingest/（v2 の取り込み）

YouTube などの取得結果から歌唱を読み取り、`data/v2/` に追記するための部品です(`python -m src.cli.ingest`)。

- **youtube_api.py**: YouTube Data API からの取得(月ごとの一覧、1本の取得、本人以外のチャンネルの検索)
- **parser.py**: 職人さんのコメントの選び方、時刻の行の分け方、既存の曲との照合
- **staging.py**: 下書き(`data/ingest/staged/`)の読み書きと、`data/v2/` への追記
- **skips.py**: 曲の無いコンテンツの記録(`data/ingest/skipped.tsv`)

##### ui/（UIコンポーネント層）

再利用可能なUIコンポーネントを格納します。

- **components/**: Streamlit UIコンポーネント(`__init__.py`)とフッター(`footer.py`)
  - `render_search_form()`: 検索フォームの表示
  - `render_results_table()`: 検索結果テーブルの表示
  - `render_pagination()`: ページネーション（段階的表示）
  - `render_twitter_embed()`: Twitter埋め込み表示
- **pages/home_page.py**: Home の画面(`HomePage`。`Home.py` から呼ぶ)
- **styles/style.css**: 画面のスタイル

##### config/（設定管理層）

アプリケーション設定とロギング設定を格納します。

- **settings.py**: アプリケーション設定の一元管理
  - `Config`クラス: ファイルパス、表示設定、ページ設定、パフォーマンス設定
  - 環境変数からの設定読み込み
  - 設定値の検証
  
- **logging_config.py**: ロギング設定
  - ログレベル、フォーマット、ファイル出力、ローテーション設定
  - 環境変数による制御

##### exceptions/（例外処理層）

カスタム例外クラスを格納します。

- **errors.py**: アプリケーション固有の例外クラス
  - `ShinoutaTimeError`: 基底例外クラス
  - `DataLoadError`: データ読み込みエラー
  - `DataProcessingError`: データ処理エラー
  - `ConfigurationError`: 設定エラー
  - `log_error()`: エラーログ記録関数

## 技術スタック

- **フレームワーク**: Streamlit
- **プログラミング言語**: Python 3.14(Docker イメージ `python:3.14.8-slim-trixie`)
- **データ処理**: Pandas
- **データ形式**: TSV (Tab-Separated Values)
- **スタイリング**: CSS

## ドキュメント

`docs/` ディレクトリに、より詳細なドキュメントがあります。

- **`docs/README.md`**: ドキュメントの一覧
- **`docs/specs/`**: 仕様書(データモデル v2 は `data-model.md`)
- **`docs/prompts/`**: AI エージェント向けの手順(データの取り込みは `update-data.md`)
- **`docs/guides/`**: ユーザーおよび開発者向けのガイド
- **`docs/architecture/overview.md`**: 構成の概要(層・データの流れ・エラー・キャッシュ)
- **`docs/development/`**: 開発プロセスや規約に関するドキュメント
- **`docs/testing/`**: テストに関するドキュメント

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


## 🛠️ ツールとスクリプト

### 環境検証スクリプト

開発環境が正しくセットアップされているか確認するスクリプトです。

- `scripts/verify_environment.bat` (Windows)
- `scripts/verify_environment.sh` (Linux/Mac)
