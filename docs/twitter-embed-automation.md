# Twitter埋め込みコード自動取得システム

## 概要

Twitter埋め込みコード自動取得システムは、TwitterのツイートURLから埋め込みコードを自動的に取得し、`data/tweet_embed_code.html`ファイルに保存する機能を提供します。

このシステムは以下の2つのインターフェースを提供します：

1. **コマンドラインインターフェース（CLI）**: スクリプトやバッチ処理での自動化に最適
2. **Streamlit管理画面（UI）**: ブラウザから簡単に操作できる管理画面

## 主な機能

- ✅ ツイートURLからの自動埋め込みコード取得
- ✅ 複数ツイートの一括処理
- ✅ 自動バックアップ機能
- ✅ エラーハンドリングとリトライ機能
- ✅ 取得履歴のログ記録
- ✅ 表示高さの自動設定
- ✅ プレビュー機能（UI）
- ✅ 認証機能（UI）

## セットアップ

### 前提条件

- Python 3.11以上
- Docker（推奨）または Python仮想環境
- インターネット接続

### インストール

#### Docker環境（推奨）

```bash
# リポジトリのクローン
git clone <repository-url>
cd <repository-directory>

# Docker Composeで起動
docker-compose up
```

#### Python仮想環境

```bash
# リポジトリのクローン
git clone <repository-url>
cd <repository-directory>

# 仮想環境の作成とアクティベート
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 環境変数の設定（オプション）

`.env.example`ファイルを`.env`にコピーして、必要に応じて編集します：

```bash
cp .env.example .env
```

**設定可能な環境変数:**

```bash
# Twitter API設定（将来の拡張用）
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret

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

# 管理画面認証
ADMIN_PASSWORD=your_admin_password
```

## 使用方法

### 方法1: コマンドラインインターフェース（CLI）

CLIは、スクリプトやバッチ処理での自動化に最適です。

#### 基本的な使用方法

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

# カスタム出力パスを指定
python -m src.cli.twitter_embed_cli \
  -o custom/path/embed.html \
  https://twitter.com/user/status/123
```

#### コマンドラインオプション

| オプション | 短縮形 | 説明 | デフォルト値 |
|-----------|--------|------|-------------|
| `urls` | - | ツイートURL（複数指定可能） | 必須 |
| `--output` | `-o` | 出力ファイルパス | `data/tweet_embed_code.html` |
| `--height-output` | - | 高さ出力ファイルパス | `data/tweet_height.txt` |
| `--no-backup` | - | バックアップを作成しない | False |
| `--verbose` | `-v` | 詳細ログを表示 | False |
| `--max-retries` | - | 最大リトライ回数 | 3 |
| `--retry-delay` | - | リトライ間隔（秒） | 1.0 |

#### 終了コード

CLIは以下の終了コードを返します：

| 終了コード | 説明 |
|-----------|------|
| 0 | 成功 |
| 1 | 無効な引数 |
| 2 | 無効なURL |
| 3 | ネットワークエラー |
| 4 | ファイル書き込みエラー |
| 99 | 予期しないエラー |

#### 使用例

**例1: 単一ツイートの取得**

```bash
$ python -m src.cli.twitter_embed_cli https://twitter.com/user/status/1234567890

埋め込みコードを取得中: https://twitter.com/user/status/1234567890
✓ 埋め込みコード取得成功
ファイルに保存中: data/tweet_embed_code.html
✓ 表示高さを保存しました: 850px
✓ ファイル保存成功: data/tweet_embed_code.html
```

**例2: 複数ツイートの取得**

```bash
$ python -m src.cli.twitter_embed_cli \
  https://twitter.com/user/status/123 \
  https://twitter.com/user/status/456 \
  https://twitter.com/user/status/789

3件のツイートを取得します

[1/3] (33.3%) 取得中: https://twitter.com/user/status/123
[2/3] (66.7%) 取得中: https://twitter.com/user/status/456
[3/3] (100.0%) 取得中: https://twitter.com/user/status/789

============================================================
処理結果サマリー
============================================================
成功: 3件
失敗: 0件
============================================================

ファイルに保存中: data/tweet_embed_code.html
✓ 表示高さを保存しました: 920px
✓ ファイル保存成功: data/tweet_embed_code.html

✓ 全てのツイートの取得に成功しました
```

**例3: エラーハンドリング**

```bash
$ python -m src.cli.twitter_embed_cli \
  https://twitter.com/user/status/123 \
  https://twitter.com/invalid/url

2件のツイートを取得します

[1/2] (50.0%) 取得中: https://twitter.com/user/status/123
[2/2] (100.0%) 取得中: https://twitter.com/invalid/url

============================================================
処理結果サマリー
============================================================
成功: 1件
失敗: 1件

失敗したURL:
  - https://twitter.com/invalid/url
============================================================

ファイルに保存中: data/tweet_embed_code.html
✓ 表示高さを保存しました: 850px
✓ ファイル保存成功: data/tweet_embed_code.html

警告: 1件のツイート取得に失敗しました
```

#### Docker環境での実行

Docker環境で実行する場合：

```bash
# Docker Composeを使用
docker-compose exec shinouta-time python -m src.cli.twitter_embed_cli \
  https://twitter.com/user/status/1234567890

# または、Dockerコンテナ内でシェルを起動
docker-compose exec shinouta-time bash
python -m src.cli.twitter_embed_cli https://twitter.com/user/status/1234567890
```

### 方法2: Streamlit管理画面（UI）

Streamlit管理画面は、ブラウザから簡単に操作できる管理画面です。

#### アクセス方法

1. Streamlitアプリケーションを起動

```bash
# Docker環境
docker-compose up

# Python仮想環境
streamlit run Home.py
```

2. ブラウザで `http://localhost:8501` にアクセス
3. サイドバーから「Twitter Embed Admin」ページを選択
4. 管理者パスワードを入力してログイン

#### 認証

管理画面へのアクセスには管理者パスワードが必要です。

**パスワード設定:**

```bash
# 環境変数で設定
export ADMIN_PASSWORD=your_secure_password

# または.envファイルに記載
echo "ADMIN_PASSWORD=your_secure_password" >> .env
```

環境変数が設定されていない場合、デフォルトパスワード `admin` が使用されます。

**セキュリティ上の注意:**
- 本番環境では必ず強力なパスワードを設定してください
- `.env`ファイルに設定し、`.gitignore`に含めてください

#### 操作手順

1. **ログイン**
   - パスワードを入力
   - 「ログイン」ボタンをクリック

2. **ツイートURL入力**
   - テキストエリアにツイートURLを入力
   - 単一のツイート: 1つのURLを入力
   - 複数のツイート: 1行に1つずつURLを入力

3. **オプション設定**
   - ☑ バックアップを作成: 既存のファイルをバックアップ（推奨）
   - ☑ 取得後に自動保存: 取得成功後、自動的にファイルに保存

4. **取得実行**
   - 「取得」ボタンをクリック
   - 処理の進行状況を確認
   - 取得結果のサマリーを確認

5. **プレビュー確認**
   - 取得した埋め込みコードのプレビューを確認
   - 実際の表示を確認

6. **保存**
   - 「保存」ボタンをクリック
   - ファイルへの保存が完了

詳細は[Twitter埋め込みコード管理画面 使用ガイド](twitter-embed-admin-guide.md)を参照してください。

## 対応URL形式

以下のURL形式に対応しています：

- `https://twitter.com/username/status/1234567890`
- `https://x.com/username/status/1234567890`
- `https://mobile.twitter.com/username/status/1234567890`
- `https://twitter.com/i/web/status/1234567890`

## 出力ファイル

### 埋め込みコードファイル

**パス**: `data/tweet_embed_code.html`

Twitter埋め込みコードのHTMLが保存されます。

```html
<blockquote class="twitter-tweet">
  <p lang="ja" dir="ltr">ツイート本文...</p>
  &mdash; ユーザー名 (@username) 
  <a href="https://twitter.com/username/status/1234567890">日付</a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
```

### 表示高さファイル

**パス**: `data/tweet_height.txt`

埋め込みコードの推奨表示高さ（ピクセル）が保存されます。

```
850
```

### バックアップファイル

**パス**: `data/backups/tweet_embed_code_YYYYMMDD_HHMMSS.html`

既存のファイルのバックアップが保存されます（オプション有効時）。

## ログファイル

### ログファイルの場所

**パス**: `logs/twitter_embed.log`

全ての操作がログファイルに記録されます。

### ログ内容

- 埋め込みコード取得の成功/失敗
- ファイル保存の成功/失敗
- エラー情報
- 認証の成功/失敗（UI）
- タイムスタンプ

### ログローテーション

ログファイルは自動的にローテーションされます：

- **最大ファイルサイズ**: 10MB
- **保持するバックアップ数**: 5個
- **ファイル名形式**: `twitter_embed.log`, `twitter_embed.log.1`, `twitter_embed.log.2`, ...

### ログレベルの設定

環境変数でログレベルを設定できます：

```bash
# DEBUGレベル（詳細ログ）
export TWITTER_EMBED_LOG_LEVEL=DEBUG

# INFOレベル（通常ログ）
export TWITTER_EMBED_LOG_LEVEL=INFO

# WARNINGレベル（警告のみ）
export TWITTER_EMBED_LOG_LEVEL=WARNING

# ERRORレベル（エラーのみ）
export TWITTER_EMBED_LOG_LEVEL=ERROR
```

## エラーハンドリング

### エラーの種類

システムは以下のエラーを適切に処理します：

#### 1. 入力検証エラー

- **無効なURL形式**: ツイートURLの形式が正しくない
- **空のURL**: URLが入力されていない
- **ツイートID抽出失敗**: URLからツイートIDを抽出できない

**対処方法**: URL形式を確認し、正しいツイートURLを入力してください

#### 2. API通信エラー

- **ネットワークエラー**: インターネット接続の問題
- **APIタイムアウト**: APIの応答が遅い
- **レート制限**: APIの呼び出し制限に達した
- **API応答エラー**: APIからエラーレスポンスが返された

**対処方法**: 
- インターネット接続を確認
- しばらく待ってから再試行
- レート制限の場合は、表示された待機時間後に再試行

#### 3. ファイルシステムエラー

- **ファイルが見つからない**: 指定されたファイルが存在しない
- **ファイルアクセス権限エラー**: ファイルへの書き込み権限がない
- **ディスク容量不足**: ディスクの空き容量が不足
- **ファイル書き込みエラー**: ファイルへの書き込みに失敗

**対処方法**:
- ファイルパスを確認
- ファイルの書き込み権限を確認
- ディスクの空き容量を確認

#### 4. データ検証エラー

- **不正なHTML形式**: 取得したHTMLコードが不正
- **空のAPI応答**: APIから空の応答が返された
- **不正なAPI応答形式**: APIの応答形式が期待と異なる

**対処方法**: ツイートが存在するか、公開設定かを確認

### リトライ機能

ネットワークエラーやAPIタイムアウトが発生した場合、自動的にリトライします。

**リトライ設定:**

- **最大リトライ回数**: 3回（デフォルト）
- **リトライ間隔**: 1秒（デフォルト）
- **指数バックオフ**: リトライごとに待機時間が増加

**カスタマイズ:**

```bash
# CLIでリトライ設定をカスタマイズ
python -m src.cli.twitter_embed_cli \
  --max-retries 5 \
  --retry-delay 2.0 \
  https://twitter.com/user/status/123
```

## トラブルシューティング

### よくある問題と解決方法

#### Q1: URLが無効と表示される

**原因**: URL形式が正しくない

**解決方法**:
- URL形式を確認（`https://twitter.com/username/status/数字`）
- twitter.comまたはx.comのURLか確認
- ツイートIDが含まれているか確認

#### Q2: 取得に失敗する

**原因**: ネットワーク接続、ツイートの削除、非公開設定など

**解決方法**:
- インターネット接続を確認
- ツイートが存在するか確認（削除されていないか）
- ツイートが公開設定か確認
- ログファイルでエラー詳細を確認

#### Q3: 保存に失敗する

**原因**: ファイルの書き込み権限、ディスク容量不足など

**解決方法**:
- ファイルの書き込み権限を確認
- ディスク容量を確認
- `data`ディレクトリが存在するか確認
- ログファイルでエラー詳細を確認

#### Q4: ログインできない（UI）

**原因**: パスワードが正しくない、環境変数が設定されていない

**解決方法**:
- パスワードが正しいか確認
- 環境変数`ADMIN_PASSWORD`が設定されているか確認
- ブラウザのキャッシュをクリア

#### Q5: Docker環境で実行できない

**原因**: Dockerが起動していない、コンテナが起動していない

**解決方法**:
- Dockerが起動しているか確認
- `docker-compose up`でコンテナを起動
- `docker-compose ps`でコンテナの状態を確認

### ログファイルの確認

問題が発生した場合は、ログファイルを確認してください：

```bash
# ログファイルの内容を表示
cat logs/twitter_embed.log

# 最新のログを表示
tail -n 50 logs/twitter_embed.log

# エラーログのみを表示
grep ERROR logs/twitter_embed.log
```

## 高度な使用方法

### スクリプトでの自動化

CLIを使用して、定期的な更新を自動化できます。

**例: cronジョブでの定期実行**

```bash
# crontabを編集
crontab -e

# 毎日午前9時に実行
0 9 * * * cd /path/to/project && python -m src.cli.twitter_embed_cli https://twitter.com/user/status/123
```

**例: シェルスクリプトでの一括処理**

```bash
#!/bin/bash

# urls.txtから複数のURLを読み込んで処理
while IFS= read -r url; do
    python -m src.cli.twitter_embed_cli "$url"
done < urls.txt
```

### カスタム設定

環境変数を使用して、システムの動作をカスタマイズできます。

**例: カスタム設定ファイル**

```bash
# .env.custom
TWITTER_EMBED_CODE_PATH=custom/path/embed.html
TWITTER_HEIGHT_PATH=custom/path/height.txt
TWITTER_BACKUP_DIR=custom/backups
TWITTER_EMBED_LOG_LEVEL=DEBUG
TWITTER_API_MAX_RETRIES=5
TWITTER_API_RETRY_DELAY=2.0
```

```bash
# カスタム設定で実行
source .env.custom
python -m src.cli.twitter_embed_cli https://twitter.com/user/status/123
```

## セキュリティ考慮事項

### 認証情報の管理

- 環境変数を使用した安全な管理
- `.env`ファイルを`.gitignore`に追加
- ログやエラーメッセージに認証情報を含めない

### アクセス制御

- 管理画面へのアクセスには認証が必要
- セッションベースの認証状態管理
- 強力なパスワードの使用を推奨

### ファイルシステムセキュリティ

- ファイルパスのサニタイゼーション
- ディレクトリトラバーサル攻撃の防止
- 適切なファイルパーミッションの設定

### API通信のセキュリティ

- HTTPS通信の強制
- SSL証明書の検証
- タイムアウトの設定

## パフォーマンス

### API呼び出しの最適化

- レート制限の遵守
- 適切なリトライ間隔
- バッチ処理による効率化

### ファイル操作の最適化

- バッファリングを使用した効率的な読み書き
- 大きなファイルの処理時のメモリ管理

## 関連ドキュメント

- [Twitter埋め込みコード管理画面 使用ガイド](twitter-embed-admin-guide.md)
- [Twitter埋め込み機能 技術ドキュメント](twitter-embed-credentials.md)
- [設計書](../.kiro/specs/twitter-embed-automation/design.md)
- [要件定義書](../.kiro/specs/twitter-embed-automation/requirements.md)
- [実装タスクリスト](../.kiro/specs/twitter-embed-automation/tasks.md)

## サポート

問題が発生した場合は、以下を確認してください：

1. ログファイル: `logs/twitter_embed.log`
2. エラーメッセージ
3. ブラウザのコンソール（UI使用時）
4. [トラブルシューティング](#トラブルシューティング)セクション

それでも解決しない場合は、開発チームに連絡してください。

## ライセンス

本プロジェクトは Apache License 2.0 のもとで公開されています。

