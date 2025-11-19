# しのうたタイム👻🫧

VTuber「幽音しの」さんの配信で歌唱された楽曲を検索・閲覧できる非公式ファンサイトです。

## 概要

「しのうたタイム」は、VTuber「幽音しの」さんのYouTubeライブ配信で歌唱された楽曲のデータベースアプリケーションです。ファンの皆様が、過去の配信で歌われた楽曲を簡単に検索し、該当箇所から視聴できるようにすることを目的としています。

**重要**: 本サイトは非公式ファンサイトであり、幽音しのさんご本人および所属事務所とは一切関係ありません。

## 主な機能

### 🔍 楽曲検索機能
- **キーワード検索**: 曲名、アーティスト名で楽曲を検索
- **ライブタイトル検索**: 配信タイトルからも検索可能（オプション）
- **部分一致検索**: 大文字小文字を区別せず、柔軟に検索
- **検索結果の表示**: 配信日、曲目番号、曲名、アーティスト、YouTubeリンクを一覧表示

### 📊 段階的表示機能
- 初期表示は25件に制限し、高速な読み込みを実現
- 「さらに25件表示」ボタンで25件ずつ追加表示
- 現在の表示件数と総件数を常に表示

### 🎬 YouTubeタイムスタンプ付きリンク機能
- 各楽曲に対して、配信動画の該当箇所へ直接ジャンプできるリンクを生成
- クリックするだけで、その楽曲が歌唱された瞬間から視聴開始

### 📋 楽曲リスト表示機能
- 全楽曲をアーティスト順に一覧表示
- 最近の歌唱へのリンク付き
- β版として提供中（ソート順の改善予定）

### 📢 情報ページ機能
- 配信スケジュールの表示
- お知らせ情報の表示
- Twitter投稿の埋め込み表示

### 🔧 Twitter埋め込みコード自動取得機能（管理者向け）

TwitterのツイートURLから埋め込みコードを自動的に取得し、情報ページに表示するための機能です。

**主な機能:**
- ✅ ツイートURLからの自動埋め込みコード取得
- ✅ 複数ツイートの一括処理
- ✅ 自動バックアップ機能
- ✅ エラーハンドリングとリトライ機能
- ✅ 取得履歴のログ記録
- ✅ 表示高さの自動設定

**2つのインターフェース:**

1. **コマンドラインインターフェース（CLI）**
   - スクリプトやバッチ処理での自動化に最適
   - 詳細は[Twitter埋め込みコード自動取得システム](docs/twitter-embed-automation.md)を参照

2. **Streamlit管理画面（UI）**
   - ブラウザから簡単に操作できる管理画面
   - パスワード認証によるアクセス制御
   - プレビュー機能
   - 詳細は[Twitter埋め込みコード管理画面 使用ガイド](docs/twitter-embed-admin-guide.md)を参照

## セットアップ手順

本アプリケーションは、以下の2つの方法で環境構築が可能です：

1. **Docker Compose を使用する方法（推奨）** - ローカル環境を汚さず、簡単にセットアップ
2. **Python 仮想環境を使用する方法** - 従来の方法

### 方法の選択

| 方法 | メリット | デメリット |
|-----|---------|-----------|
| **Docker Compose（推奨）** | ・ローカル環境にPythonや依存パッケージをインストール不要<br>・本番環境（Python 3.11）と同じ環境を再現<br>・環境のクリーンアップが容易<br>・`docker-compose up`コマンド一つで起動 | ・Dockerのインストールが必要<br>・初回起動時にイメージのビルドが必要 |
| **Python 仮想環境** | ・Dockerが不要<br>・軽量で高速 | ・ローカル環境にPython 3.11のインストールが必要<br>・依存パッケージの管理が必要<br>・環境の分離が不完全 |

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
docker-compose up
```

初回起動時は、Dockerイメージのビルドが行われるため、数分かかる場合があります。

#### 3. 動作確認

環境が正しく構築されたことを確認するため、動作確認スクリプトを実行します：

**Mac/Linux:**
```bash
bash verify_environment.sh
```

**Windows:**
```cmd
verify_environment.bat
```

または、手動でテストを実行：

```bash
docker-compose exec shinouta-time pytest tests/test_environment_verification.py -v
```

全てのテストが成功すれば、環境構築は完了です。

#### 4. アプリケーションへのアクセス

起動後、ブラウザで `http://localhost:8501` にアクセスしてください。

#### 5. 停止とクリーンアップ

アプリケーションを停止するには、`Ctrl+C` を押してください。

コンテナを完全に削除するには：

```bash
docker-compose down
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

#### 必要な環境
- **Python 3.11** (本番環境と同じバージョンを推奨)
- **pip** (Pythonパッケージマネージャー)

#### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd <repository-directory>
```

#### 2. Python仮想環境の作成とアクティベート

**Linux/Mac:**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

必要なパッケージ:
- `streamlit` - Webアプリケーションフレームワーク
- `pandas` - データ処理ライブラリ

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

## データファイル構造

本アプリケーションは、`data/` ディレクトリ内のTSV（タブ区切り）ファイルからデータを読み込みます。

### ディレクトリ構造

```
data/
├── M_YT_LIVE.TSV               # 配信データ
├── M_YT_LIVE_TIMESTAMP.TSV     # 楽曲タイムスタンプデータ
├── V_SONG_LIST.TSV             # 楽曲リストデータ
├── tweet_embed_code.html       # Twitter埋め込みコード
└── tweet_height.txt            # Twitter埋め込み高さ設定
```

### データファイルの詳細

#### M_YT_LIVE.TSV（配信データ）
配信情報を格納するファイルです。

| カラム名 | データ型 | 説明 |
|---------|---------|------|
| ID | 整数 | 配信の一意識別子 |
| 配信日 | 文字列/数値 | 配信日（UNIXミリ秒またはYYYY/MM/DD形式） |
| タイトル | 文字列 | 配信タイトル |
| URL | 文字列 | YouTube配信URL |

#### M_YT_LIVE_TIMESTAMP.TSV（楽曲タイムスタンプデータ）
各配信で歌唱された楽曲の情報を格納するファイルです。

| カラム名 | データ型 | 説明 |
|---------|---------|------|
| ID | 整数 | 楽曲レコードの一意識別子 |
| LIVE_ID | 整数 | 配信IDへの外部キー（M_YT_LIVE.TSVのIDと対応） |
| 曲名 | 文字列 | 楽曲名 |
| アーティスト | 文字列 | アーティスト名 |
| タイムスタンプ | 文字列 | 歌唱開始時刻（HH:MM:SSまたはMM:SS形式） |

#### V_SONG_LIST.TSV（楽曲リストデータ）
全楽曲のリスト情報を格納するファイルです。

| カラム名 | データ型 | 説明 |
|---------|---------|------|
| アーティスト | 文字列 | アーティスト名（表示用） |
| アーティスト(ソート用) | 文字列 | アーティスト名（ソート用） |
| 曲名 | 文字列 | 楽曲名 |
| 最近の歌唱 | 文字列 | 最近の歌唱へのYouTube URL |

## Twitter埋め込みコード自動取得機能

### 概要

Twitter埋め込みコード自動取得機能は、TwitterのツイートURLから埋め込みコードを自動的に取得し、情報ページに表示するための機能です。手動でのコピー&ペースト作業を排除し、運用効率を向上させます。

### 使用方法

#### 方法1: コマンドラインインターフェース（CLI）

スクリプトやバッチ処理での自動化に最適です。

**基本的な使用方法:**

```bash
# 単一のツイートを取得
python -m src.cli.twitter_embed_cli https://twitter.com/user/status/1234567890

# 複数のツイートを取得
python -m src.cli.twitter_embed_cli \
  https://twitter.com/user/status/123 \
  https://twitter.com/user/status/456

# バックアップを作成せずに保存
python -m src.cli.twitter_embed_cli --no-backup https://twitter.com/user/status/123

# 詳細ログを表示
python -m src.cli.twitter_embed_cli -v https://twitter.com/user/status/123
```

**Docker環境での実行:**

```bash
# Docker Composeを使用
docker-compose exec shinouta-time python -m src.cli.twitter_embed_cli \
  https://twitter.com/user/status/1234567890
```

**ヘルプの表示:**

```bash
python -m src.cli.twitter_embed_cli --help
```

詳細は[Twitter埋め込みコード自動取得システム](docs/twitter-embed-automation.md)を参照してください。

#### 方法2: Streamlit管理画面（UI）

ブラウザから簡単に操作できる管理画面です。

1. Streamlitアプリケーションを起動
2. サイドバーから「Twitter Embed Admin」ページを選択
3. 管理者パスワードを入力してログイン
4. ツイートURLを入力して「取得」ボタンをクリック
5. プレビューを確認して「保存」ボタンをクリック

詳細は[Twitter埋め込みコード管理画面 使用ガイド](docs/twitter-embed-admin-guide.md)を参照してください。

### 対応URL形式

以下のURL形式に対応しています：

- `https://twitter.com/username/status/1234567890`
- `https://x.com/username/status/1234567890`
- `https://mobile.twitter.com/username/status/1234567890`
- `https://twitter.com/i/web/status/1234567890`

### 出力ファイル

- **埋め込みコード**: `data/tweet_embed_code.html`
- **表示高さ**: `data/tweet_height.txt`
- **バックアップ**: `data/backups/tweet_embed_code_YYYYMMDD_HHMMSS.html`

### 環境変数の設定（オプション）

```bash
# 管理画面認証
ADMIN_PASSWORD=your_admin_password

# ファイルパス
TWITTER_EMBED_CODE_PATH=data/tweet_embed_code.html
TWITTER_HEIGHT_PATH=data/tweet_height.txt
TWITTER_BACKUP_DIR=data/backups

# ログ設定
TWITTER_EMBED_LOG_LEVEL=INFO
TWITTER_EMBED_LOG_FILE=logs/twitter_embed.log

# リトライ設定
TWITTER_API_MAX_RETRIES=3
TWITTER_API_RETRY_DELAY=1.0
```

### トラブルシューティング

よくある問題と解決方法については、[Twitter埋め込みコード自動取得システム](docs/twitter-embed-automation.md#トラブルシューティング)を参照してください。

## プロジェクト構造

```
.
├── Home.py                          # メインページ（検索機能）
├── pages/
│   ├── 01_Information.py           # 情報ページ
│   ├── 02_About_Us.py              # About Usページ
│   ├── 80_Twitter_Embed_Admin.py   # Twitter埋め込みコード管理画面
│   └── 99_Song_List_beta.py        # 楽曲リストページ（β版）
├── src/                             # ソースコードモジュール
│   ├── services/                    # ビジネスロジック層
│   │   ├── __init__.py
│   │   ├── data_service.py         # データ読み込みサービス
│   │   ├── search_service.py       # 検索サービス
│   │   └── twitter_embed_service.py # Twitter埋め込みサービス
│   ├── clients/                     # APIクライアント層
│   │   ├── __init__.py
│   │   └── twitter_api_client.py   # Twitter APIクライアント
│   ├── repositories/                # データアクセス層
│   │   ├── __init__.py
│   │   └── file_repository.py      # ファイルリポジトリ
│   ├── models/                      # データモデル層
│   │   ├── __init__.py
│   │   ├── embed_result.py         # 埋め込みコード取得結果
│   │   └── oembed_response.py      # oEmbedレスポンス
│   ├── core/                        # コア機能層
│   │   ├── __init__.py
│   │   ├── data_pipeline.py        # データ処理パイプライン
│   │   └── utils.py                # ユーティリティ関数
│   ├── ui/                          # UIコンポーネント層
│   │   ├── __init__.py
│   │   ├── components.py           # 再利用可能なUIコンポーネント
│   │   └── twitter_embed_admin.py  # Twitter埋め込み管理画面UI
│   ├── cli/                         # コマンドラインインターフェース層
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── twitter_embed_cli.py    # Twitter埋め込みCLI
│   ├── utils/                       # ユーティリティ層
│   │   ├── __init__.py
│   │   ├── validators.py           # バリデーター
│   │   ├── retry.py                # リトライロジック
│   │   └── html_validator.py       # HTML検証
│   ├── config/                      # 設定管理層
│   │   ├── __init__.py
│   │   ├── settings.py             # アプリケーション設定
│   │   └── logging_config.py       # ロギング設定
│   ├── exceptions/                  # 例外処理層
│   │   ├── __init__.py
│   │   └── errors.py               # カスタム例外クラス
│   └── __init__.py
├── data/
│   ├── M_YT_LIVE.TSV               # 配信データ
│   ├── M_YT_LIVE_TIMESTAMP.TSV     # 楽曲タイムスタンプデータ
│   ├── V_SONG_LIST.TSV             # 楽曲リストデータ
│   ├── tweet_embed_code.html       # Twitter埋め込みコード
│   ├── tweet_height.txt            # Twitter埋め込み高さ設定
│   └── backups/                    # バックアップディレクトリ
│       └── tweet_embed_code_*.html # バックアップファイル
├── docs/                            # ドキュメント
│   ├── architecture.md             # アーキテクチャドキュメント
│   ├── data-flow.md               # データフロードキュメント
│   ├── data-management.md         # データ管理ドキュメント
│   ├── deployment.md              # デプロイメントガイド
│   ├── developer-guide.md         # 開発者ガイド
│   ├── error-handling.md          # エラーハンドリングガイド
│   ├── faq.md                     # よくある質問
│   ├── user-guide.md              # ユーザーガイド
│   ├── twitter-embed-automation.md # Twitter埋め込み自動取得システム
│   ├── twitter-embed-admin-guide.md # Twitter埋め込み管理画面ガイド
│   └── twitter-embed-credentials.md # Twitter埋め込み技術ドキュメント
├── tests/                           # テストコード
│   ├── unit/                       # ユニットテスト
│   ├── property/                   # プロパティベーステスト
│   ├── integration/                # 統合テスト
│   └── __init__.py
├── logs/                            # ログファイル（自動生成）
│   ├── shinouta.log                # アプリケーションログ
│   └── twitter_embed.log           # Twitter埋め込み機能ログ
├── footer.py                        # フッター表示モジュール
├── style.css                        # カスタムCSSスタイル
├── requirements.txt                 # 依存関係
└── README.md                        # このファイル
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

##### ui/（UIコンポーネント層）

再利用可能なUIコンポーネントを格納します。

- **components.py**: Streamlit UIコンポーネント
  - `render_search_form()`: 検索フォームの表示
  - `render_results_table()`: 検索結果テーブルの表示
  - `render_pagination()`: ページネーション（段階的表示）
  - `render_twitter_embed()`: Twitter埋め込み表示

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
- **プログラミング言語**: Python 3.x
- **データ処理**: Pandas
- **データ形式**: TSV (Tab-Separated Values)
- **スタイリング**: CSS

## ドキュメント

### 仕様書・設計書

詳細な仕様書と設計書は `.kiro/specs/` ディレクトリにあります：

**リファクタリング:**
- `.kiro/specs/refactoring/requirements.md` - リファクタリング要件定義書
- `.kiro/specs/refactoring/design.md` - リファクタリング設計書
- `.kiro/specs/refactoring/tasks.md` - リファクタリング実装タスクリスト

**Twitter埋め込み自動取得:**
- `.kiro/specs/twitter-embed-automation/requirements.md` - 要件定義書
- `.kiro/specs/twitter-embed-automation/design.md` - 設計書
- `.kiro/specs/twitter-embed-automation/tasks.md` - 実装タスクリスト

### 開発者向けドキュメント

`docs/` ディレクトリに各種ドキュメントがあります：

**一般:**
- `architecture.md` - アーキテクチャドキュメント（システム構成、レイヤー構造）
- `developer-guide.md` - 開発者ガイド（セットアップ、コーディング規約、モジュール使用方法）
- `data-flow.md` - データフロードキュメント（データ処理の流れ）
- `data-management.md` - データ管理ドキュメント（TSVファイルの管理方法）
- `error-handling.md` - エラーハンドリングガイド（エラー処理の実装方法）
- `deployment.md` - デプロイメントガイド（本番環境へのデプロイ方法）
- `user-guide.md` - ユーザーガイド（アプリケーションの使い方）
- `faq.md` - よくある質問

**Twitter埋め込み機能:**
- `twitter-embed-automation.md` - Twitter埋め込みコード自動取得システム（使用方法、セットアップ手順）
- `twitter-embed-admin-guide.md` - Twitter埋め込みコード管理画面 使用ガイド
- `twitter-embed-credentials.md` - Twitter埋め込み機能 技術ドキュメント

## 注意事項

### 非公式サイトについて
本サイトは非公式ファンサイトであり、幽音しのさんご本人および所属事務所とは一切関係ありません。公式情報については、公式チャンネルや公式Twitterをご確認ください。

### データの正確性について
本サイトのデータは、有志による手作業での情報収集に基づいています。そのため、以下の点にご注意ください：

- **誤りの可能性**: データ入力時の誤りや漏れがある可能性があります
- **最新情報の反映遅延**: 最新の配信情報が即座に反映されない場合があります
- **β版機能**: 一部機能（楽曲リストのソート順など）は改善中です

データに誤りを発見された場合は、お手数ですが管理者までご連絡ください。

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
