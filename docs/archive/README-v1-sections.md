# README から移した v1・Twitter 埋め込みの節

> 2026-10-22 に、ルートの README.md から移しました。v1 のデータ(`data/*.TSV`・`data.xlsx`)の手順と、今は使っていない X(Twitter)の埋め込みの説明です。画面は v2(`data/v2/`)を読み、もう使いません(フェーズ3で消す予定)。
> 文中のリンクとパスは、README にあったときのまま(リポジトリの直下から見たもの)です。

## 主な機能の「管理者向け機能」から


### Twitter埋め込みコード自動取得機能

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
2. **Streamlit管理画面（UI）**
   - ブラウザから操作する(ローカル専用。`pages/*_Admin.py` は Git 管理外)

詳細は「[Twitter埋め込みコード自動取得機能](#twitter埋め込みコード自動取得機能)」セクションを参照してください。

### Excel to TSV変換ツール(旧フロー)

> 【旧フロー】v1 のデータ(`data/*.TSV`・`data.xlsx`)の仕組みです。画面は v2(`data/v2/`)に切り替え済みで、もう使いません(フェーズ3で消す予定)。今後のデータの追加は [`docs/prompts/update-data.md`](docs/prompts/update-data.md)。

**主な機能:**
- ✅ Excelファイルからの自動TSV生成
- ✅ データ検証機能（フィールド数、データ型、URL形式）
- ✅ 自動バックアップ機能
- ✅ 後続処理の自動実行（song_list_generator）
- ✅ エラーハンドリングとロールバック機能
- ✅ 詳細なログ記録

詳細は「[Excel to TSV変換ツール](#excel-to-tsv変換ツール管理者向け)」セクションを参照してください。

### アーティスト名ソート修正機能(旧フロー)

V_SONG_LIST.TSVのアーティスト名（ソート用）が誤っている場合に修正できる機能です。v2 では、アーティストの読みは `data/v2/artists.tsv` の `sort_name` に持ちます。

**主な機能:**
- ✅ 誤ったソート名の手動修正
- ✅ 修正マッピングの永続化
- ✅ コマンドラインインターフェース（CLI）
- ✅ 修正マッピングの追加・更新・削除・一覧表示
- ✅ 曲リスト生成時の自動適用

**使用例:**

```bash
# 修正マッピングを追加
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli add "Vaundy" "Vaundy"

# 修正マッピングを一覧表示
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli list

# 修正マッピングを削除
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli delete "Vaundy"
```

詳細は[アーティスト名ソート修正機能 使い方](docs/guides/artist-sort-correction-guide.md)を参照してください。


---

## データファイル構造

本アプリケーションは、`data/` ディレクトリ内のTSV（タブ区切り）ファイルからデータを読み込みます。

データは2つが並んでいます。
- **v2(正本。画面が読む)**: `data/v2/` の5つのテーブル(contents・artists・songs・performances・aliases)。YouTube などから取り込みの CLI で追加します。形の決まりは [`docs/specs/data-model.md`](docs/specs/data-model.md)、追加の手順は [`docs/prompts/update-data.md`](docs/prompts/update-data.md)。
- **v1(参照用。画面はもう読まない)**: `data/*.TSV`・`data.xlsx`。下の表はこちらの説明です。フェーズ3で消す予定です。

### ディレクトリ構造

```
data/
├── v2/                         # v2 のテーブル(TSV。取り込みの CLI で書く)
├── ingest/                     # 取り込み: skipped.tsv(曲なしの記録、Git 管理)、cache/・staged/(Git 管理外)
├── data.xlsx                   # 入力用Excelファイル（v1、管理者向け）
├── M_YT_LIVE.TSV               # 配信データ
├── M_YT_LIVE_TIMESTAMP.TSV     # 楽曲タイムスタンプデータ
├── V_SONG_LIST.TSV             # 楽曲リストデータ
├── ARTIST_SORT_MAPPING.TSV     # アーティスト名ソート修正マッピング
├── tweet_embed_code.html       # Twitter埋め込みコード
├── tweet_height.txt            # Twitter埋め込み高さ設定
└── backups/                    # バックアップディレクトリ
    ├── M_YT_LIVE_*.TSV         # 配信データのバックアップ
    ├── M_YT_LIVE_TIMESTAMP_*.TSV # タイムスタンプデータのバックアップ
    └── tweet_embed_code_*.html # Twitter埋め込みコードのバックアップ
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

#### ARTIST_SORT_MAPPING.TSV（アーティスト名ソート修正マッピング）
アーティスト名とその正しいソート名の対応関係を保存するファイルです。

| カラム名 | データ型 | 説明 |
|---------|---------|------|
| アーティスト名 | 文字列 | アーティスト名 |
| ソート名 | 文字列 | 正しいソート名 |

**形式**: TSV（タブ区切り）、UTF-8エンコーディング

**用途**: 自動生成されたソート名が誤っている場合に、正しいソート名を手動で設定できます。

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
docker compose exec shinouta-time python -m src.cli.twitter_embed_cli \
  https://twitter.com/user/status/1234567890
```

**ヘルプの表示:**

```bash
python -m src.cli.twitter_embed_cli --help
```

詳細は[Twitter埋め込みコード自動取得システム](docs/archive/specs/twitter-embed-automation/design.md)を参照してください。

#### 方法2: Streamlit管理画面（UI）

ブラウザから簡単に操作できる管理画面です。

1. Streamlitアプリケーションを起動
2. サイドバーから「Twitter Embed Admin」ページを選択
3. 管理者パスワードを入力してログイン
4. ツイートURLを入力して「取得」ボタンをクリック
5. プレビューを確認して「保存」ボタンをクリック

詳細は[Twitter埋め込みコード管理画面 使用ガイド](docs/archive/specs/twitter-embed-automation/design.md#ui-design)を参照してください。

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

よくある問題と解決方法については、[Twitter埋め込みコード自動取得システム](docs/archive/specs/twitter-embed-automation/design.md#troubleshooting)を参照してください。

## Excel to TSV変換ツール（管理者向け）

> 【旧フロー】この節は v1 のデータ(`data/*.TSV`・`data.xlsx`)の手順です。画面は v2(`data/v2/`)に切り替え済みで、もう使いません(フェーズ3で消す予定)。今後のデータの追加は [`docs/prompts/update-data.md`](docs/prompts/update-data.md)。

### 概要

Excel to TSV変換ツールは、Excelファイル（data.xlsx）から2つのTSVファイル（M_YT_LIVE.TSVとM_YT_LIVE_TIMESTAMP.TSV）を自動生成し、さらに既存のsong_list_generatorツールを呼び出してV_SONG_LIST.TSVを生成する一連の処理を自動化します。

**主な機能:**
- ✅ Excelファイルからの自動TSV生成
- ✅ データ検証機能（フィールド数、データ型、URL形式）
- ✅ 自動バックアップ機能
- ✅ 後続処理の自動実行（song_list_generator）
- ✅ エラーハンドリングとロールバック機能
- ✅ 詳細なログ記録

### 使用方法

#### 基本的な使用方法

**デフォルト設定で実行:**

```bash
# Python環境
python -m src.cli.excel_to_tsv_cli

# Docker環境
docker compose exec shinouta-time python -m src.cli.excel_to_tsv_cli
```

デフォルトでは、`data/data.xlsx`を読み込み、`data/`ディレクトリに以下のファイルを生成します：
- `M_YT_LIVE.TSV`
- `M_YT_LIVE_TIMESTAMP.TSV`
- `V_SONG_LIST.TSV`（song_list_generatorによって自動生成）

#### コマンドライン引数

| 引数 | 説明 | デフォルト値 |
|-----|------|------------|
| `--input-file` | 入力Excelファイルのパス | `data/data.xlsx` |
| `--output-dir` | 出力ディレクトリのパス | `data/` |
| `--dry-run` | ドライランモード（ファイルを書き込まない） | 無効 |
| `--skip-song-list` | song_list_generatorの実行をスキップ | 無効 |
| `--verbose`, `-v` | 詳細ログを表示 | 無効 |
| `--help`, `-h` | ヘルプメッセージを表示 | - |

#### 使用例

**カスタムファイルパスを指定:**

```bash
python -m src.cli.excel_to_tsv_cli \
  --input-file /path/to/custom.xlsx \
  --output-dir /path/to/output/
```

**ドライランモード（実際のファイル生成を行わない）:**

```bash
python -m src.cli.excel_to_tsv_cli --dry-run
```

**song_list_generatorの実行をスキップ:**

```bash
python -m src.cli.excel_to_tsv_cli --skip-song-list
```

**詳細ログを表示:**

```bash
python -m src.cli.excel_to_tsv_cli --verbose
```

**Docker環境での実行:**

```bash
# 基本的な実行
docker compose exec shinouta-time python -m src.cli.excel_to_tsv_cli

# カスタムオプション付き
docker compose exec shinouta-time python -m src.cli.excel_to_tsv_cli \
  --input-file data/custom.xlsx \
  --verbose
```

### データファイルの要件

#### 入力ファイル（data.xlsx）

Excelファイルには以下の2つのシートが必要です：

**1. M_YT_LIVE シート**

| カラム名 | データ型 | 必須 | 説明 |
|---------|---------|------|------|
| ID | 整数 | ✓ | 配信の一意識別子 |
| 配信日 | 文字列/数値 | ✓ | 配信日（YYYY/MM/DD形式またはUNIXミリ秒） |
| タイトル | 文字列 | ✓ | 配信タイトル |
| URL | 文字列 | ✓ | YouTube配信URL |

**2. M_YT_LIVE_TIMESTAMP シート**

| カラム名 | データ型 | 必須 | 説明 |
|---------|---------|------|------|
| ID | 整数 | ✓ | 楽曲レコードの一意識別子 |
| LIVE_ID | 整数 | ✓ | 配信IDへの外部キー |
| タイムスタンプ | 文字列 | ✓ | 歌唱開始時刻（HH:MM:SSまたはMM:SS形式） |
| 曲名 | 文字列 | ✓ | 楽曲名 |
| アーティスト | 文字列 | ✓ | アーティスト名 |

#### 出力ファイル

**生成されるファイル:**
- `M_YT_LIVE.TSV` - 配信データ（タブ区切り、UTF-8エンコーディング）
- `M_YT_LIVE_TIMESTAMP.TSV` - 楽曲タイムスタンプデータ（タブ区切り、UTF-8エンコーディング）
- `V_SONG_LIST.TSV` - 楽曲リストデータ（song_list_generatorによって生成）

**バックアップファイル:**
- `data/backups/M_YT_LIVE_YYYYMMDD_HHMMSS.TSV`
- `data/backups/M_YT_LIVE_TIMESTAMP_YYYYMMDD_HHMMSS.TSV`

### データ検証

ツールは以下の検証を自動的に実行します：

**1. フィールド数の検証**
- M_YT_LIVE.TSV: 各行に4つのフィールドが存在すること
- M_YT_LIVE_TIMESTAMP.TSV: 各行に5つのフィールドが存在すること

**2. データ型の検証**
- IDフィールドが数値であること
- 必須フィールドが空でないこと

**3. URL形式の検証**
- URLフィールドが有効なURL形式であること

検証エラーが発生した場合、警告メッセージが表示されますが、処理は継続されます。致命的なエラーの場合は処理が中断され、バックアップから復元されます。

### バックアップ機能

既存のTSVファイルが存在する場合、上書きする前に自動的にバックアップが作成されます。

**バックアップファイル名の形式:**
```
元のファイル名_YYYYMMDD_HHMMSS.TSV
```

**例:**
```
M_YT_LIVE_20250122_143025.TSV
M_YT_LIVE_TIMESTAMP_20250122_143025.TSV
```

バックアップファイルは`data/backups/`ディレクトリに保存されます。ディレクトリが存在しない場合は自動的に作成されます。

### エラーハンドリング

ツールは以下のエラーに対して適切に対処します：

**1. ファイル読み込みエラー**
- Excelファイルが存在しない
- Excelファイルが破損している
- ファイルが他のプロセスで開かれている
- 読み込み権限がない

**2. データ検証エラー**
- 必須シートが存在しない
- フィールド数が不正
- データ型が不正
- URL形式が不正

**3. ファイル書き込みエラー**
- 書き込み権限がない
- ディスク容量不足
- ファイルパスが不正

**4. 後続処理エラー**
- song_list_generatorの実行に失敗

エラー発生時は、詳細なエラーメッセージが表示され、既存のファイルはバックアップから復元されます。

### トラブルシューティング

#### 問題: Excelファイルが見つからない

**エラーメッセージ:**
```
Error: Excel file not found: data/data.xlsx
```

**解決方法:**
1. ファイルパスが正しいか確認してください
2. `--input-file`オプションで正しいパスを指定してください
3. ファイルが存在するか確認してください

#### 問題: シートが見つからない

**エラーメッセージ:**
```
Error: Required sheet 'M_YT_LIVE' not found in Excel file
```

**解決方法:**
1. Excelファイルに必要なシート（M_YT_LIVE、M_YT_LIVE_TIMESTAMP）が存在するか確認してください
2. シート名が正確に一致しているか確認してください（大文字小文字は区別されません）

#### 問題: データ検証エラー

**エラーメッセージ:**
```
Warning: Row 5 in M_YT_LIVE: Field count mismatch (expected 4, got 3)
```

**解決方法:**
1. 該当行のデータを確認してください
2. 必須フィールドがすべて入力されているか確認してください
3. データ型が正しいか確認してください

#### 問題: song_list_generatorの実行に失敗

**エラーメッセージ:**
```
Error: Failed to run song_list_generator
```

**解決方法:**
1. song_list_generatorが正しくインストールされているか確認してください
2. `--skip-song-list`オプションを使用して、TSVファイルのみを生成してください
3. 生成されたTSVファイルを確認し、手動でsong_list_generatorを実行してください

#### 問題: 書き込み権限がない

**エラーメッセージ:**
```
Error: Permission denied: data/M_YT_LIVE.TSV
```

**解決方法:**
1. 出力ディレクトリへの書き込み権限があるか確認してください
2. ファイルが他のプロセスで開かれていないか確認してください
3. 管理者権限で実行してください（必要な場合）

### ログ出力

ツールは詳細なログを出力します。ログレベルは環境変数で制御できます。

**ログレベルの設定:**

```bash
# DEBUGレベル（詳細なデバッグ情報）
export SHINOUTA_LOG_LEVEL=DEBUG
python -m src.cli.excel_to_tsv_cli

# INFOレベル（一般的な情報）
export SHINOUTA_LOG_LEVEL=INFO
python -m src.cli.excel_to_tsv_cli

# WARNINGレベル（警告のみ）
export SHINOUTA_LOG_LEVEL=WARNING
python -m src.cli.excel_to_tsv_cli
```

**ファイルログの有効化:**

```bash
export SHINOUTA_ENABLE_FILE_LOGGING=true
export SHINOUTA_LOG_FILE=logs/excel_to_tsv.log
python -m src.cli.excel_to_tsv_cli
```

### 関連ドキュメント

詳細な仕様と設計については、以下のドキュメントを参照してください：

- **要件定義書**: `docs/archive/specs/excel-to-tsv-converter/requirements.md`
- **設計書**: `docs/archive/specs/excel-to-tsv-converter/design.md`
- **実装タスクリスト**: `docs/archive/specs/excel-to-tsv-converter/tasks.md`


---

## 「ツールとスクリプト」から


`data/data.xlsx` からTSVファイルを自動生成する統合ツールです。v1 のデータ用で、画面が v2 に切り替わったのでもう使いません(フェーズ3で消す予定)。

**使い方:**
1. `data/data.xlsx` を `data/` フォルダに配置します。
2. `scripts/excel_to_tsv.bat` を実行します。

**モード:**
- `excel_to_tsv.bat full` (デフォルト): 全てのTSVファイルを生成します。
- `excel_to_tsv.bat tsv_only`: `V_SONG_LIST.TSV` を除くTSVファイルを生成します。
- `excel_to_tsv.bat dryrun`: ファイルを生成せずに処理を検証します。

詳細は [Excel to TSV変換ガイド](docs/guides/excel-to-tsv-guide.md) を参照してください。

