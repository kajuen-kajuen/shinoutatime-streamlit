# しのうたタイム - ローカル環境構築ガイド

本ドキュメントでは、「しのうたタイム」アプリケーションをローカル環境で動作させるための手順を説明します。

## 目次

1. [前提条件](#前提条件)
2. [リポジトリの取得](#リポジトリの取得)
3. [環境変数の設定（オプション）](#環境変数の設定オプション)
4. [アプリケーションの起動](#アプリケーションの起動)
5. [動作確認](#動作確認)
6. [停止方法](#停止方法)
7. [トラブルシューティング](#トラブルシューティング)

## 前提条件

ローカル環境で「しのうたタイム」を実行するには、以下のソフトウェアがインストールされている必要があります。

### 必須

- **Docker Desktop** (Windows/Mac) または **Docker Engine** (Linux)
  - バージョン: 20.10以降を推奨
  - インストール方法: [Docker公式サイト](https://www.docker.com/get-started)
- **Docker Compose**
  - Docker Desktopには含まれています
  - Linux環境では別途インストールが必要な場合があります
- **Git**
  - リポジトリのクローンに使用します
  - インストール方法: [Git公式サイト](https://git-scm.com/)

### 確認方法

以下のコマンドでインストール状況を確認できます：

```bash
# Dockerのバージョン確認
docker --version

# Docker Composeのバージョン確認
docker-compose --version

# Gitのバージョン確認
git --version
```

## リポジトリの取得

### 1. リポジトリのクローン

ターミナル（コマンドプロンプト、PowerShell、またはbash）を開き、以下のコマンドを実行します：

```bash
git clone https://github.com/your-username/shinouta-time.git
cd shinouta-time
```

### 2. ブランチの確認

現在のブランチを確認します：

```bash
git branch
```

開発作業を行う場合は、`develop`ブランチに切り替えることを推奨します：

```bash
git checkout develop
```

### 3. ディレクトリ構造の確認

リポジトリには以下のファイルとディレクトリが含まれています：

```
shinouta-time/
├── Dockerfile              # Docker設定ファイル
├── docker-compose.yml      # Docker Compose設定ファイル
├── requirements.txt        # Python依存パッケージ
├── Home.py                 # メインアプリケーション
├── pages/                  # ページコンポーネント
├── src/                    # ソースコード
├── data/                   # データファイル（TSV）
│   ├── M_YT_LIVE.TSV
│   ├── M_YT_LIVE_TIMESTAMP.TSV
│   └── V_SONG_LIST.TSV
└── .env.example            # 環境変数のサンプル
```

## 環境変数の設定（オプション）

環境変数を設定することで、ログレベルなどの動作をカスタマイズできます。

### 1. .envファイルの作成

`.env.example`をコピーして`.env`ファイルを作成します：

```bash
# Windows (コマンドプロンプト)
copy .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env

# Mac/Linux
cp .env.example .env
```

### 2. 環境変数の編集

`.env`ファイルをテキストエディタで開き、必要に応じて値を変更します：

```env
# ログレベル（DEBUG, INFO, WARNING, ERROR）
SHINOUTA_LOG_LEVEL=DEBUG

# ファイルログの有効化
SHINOUTA_ENABLE_FILE_LOGGING=true

# ログファイルのパス
SHINOUTA_LOG_FILE=logs/shinouta.log
```

**注意**: `.env`ファイルは`.gitignore`に含まれており、Gitリポジトリにコミットされません。

## アプリケーションの起動

### 1. Docker Composeでの起動

リポジトリのルートディレクトリで以下のコマンドを実行します：

```bash
docker-compose up
```

初回起動時は、Dockerイメージのビルドに数分かかる場合があります。

### 2. バックグラウンドでの起動

バックグラウンドで起動する場合は、`-d`オプションを使用します：

```bash
docker-compose up -d
```

### 3. ログの確認

バックグラウンドで起動した場合、ログを確認するには：

```bash
docker-compose logs -f
```

ログの表示を停止するには、`Ctrl+C`を押します。

### 4. 起動完了の確認

以下のようなメッセージが表示されれば、起動成功です：

```
shinouta-time_1  | You can now view your Streamlit app in your browser.
shinouta-time_1  | 
shinouta-time_1  |   Local URL: http://localhost:8501
shinouta-time_1  |   Network URL: http://172.18.0.2:8501
```

## 動作確認

### 1. クイックスタート（推奨）

環境が正しく構築されたことを確認するため、動作確認スクリプトを実行します：

**Mac/Linux:**
```bash
bash verify_environment.sh
```

**Windows:**
```cmd
verify_environment.bat
```

このスクリプトは以下を自動的に確認します：
- Dockerのインストール確認
- コンテナの起動確認
- データファイルの存在確認
- Pythonバージョンの確認
- 必須パッケージの確認
- 自動テストの実行

### 2. 手動での自動テスト実行

スクリプトを使用せず、手動でテストを実行する場合：

```bash
docker-compose exec shinouta-time pytest tests/integration/test_environment_verification.py -v
```

**テスト内容:**
- データファイルの存在確認
- Pythonバージョンの確認（Python 3.11）
- データ読み込み機能の確認
- 検索機能の確認
- データ処理の正確性確認
- 環境分離の確認
- 本番環境との整合性確認

**成功例:**
```
tests/test_environment_verification.py::TestEnvironmentVerification::test_data_files_exist PASSED
tests/test_environment_verification.py::TestEnvironmentVerification::test_python_version PASSED
tests/test_environment_verification.py::TestEnvironmentVerification::test_load_lives_data PASSED
...
======================== XX passed in X.XXs ========================
```

全てのテストが`PASSED`と表示されれば、環境構築は成功です。

**失敗した場合:**
- エラーメッセージを確認して問題を解決してください
- 詳細は[トラブルシューティング](#トラブルシューティング)を参照してください

### 2. ブラウザでアクセス

Webブラウザを開き、以下のURLにアクセスします：

```
http://localhost:8501
```

### 3. 基本機能の手動確認

以下の項目を確認してください：

- [ ] ホームページが正しく表示される
- [ ] 検索フォームが表示される
- [ ] 検索キーワードを入力して検索できる
- [ ] 検索結果が表示される（配信日、曲名、アーティスト名など）
- [ ] ページ間の移動ができる（Information、About Usなど）

### 4. データ読み込みの確認

検索結果に以下の情報が含まれていることを確認します：

- 配信日
- 曲名
- アーティスト名
- YouTube配信へのリンク

### 5. エラーがないことの確認

ターミナルのログにエラーメッセージが表示されていないことを確認します。

## 停止方法

### 1. フォアグラウンドで起動した場合

ターミナルで`Ctrl+C`を押してサーバーを停止します。

### 2. バックグラウンドで起動した場合

以下のコマンドでコンテナを停止します：

```bash
docker-compose stop
```

### 3. コンテナの削除

コンテナを完全に削除する場合は：

```bash
docker-compose down
```

### 4. イメージとボリュームも削除する場合

イメージとボリュームも含めて完全にクリーンアップする場合は：

```bash
docker-compose down --rmi all --volumes
```

**注意**: この操作を行うと、次回起動時に再度イメージのビルドが必要になります。

## トラブルシューティング

### ポート8501が既に使用されている

**症状**: `Bind for 0.0.0.0:8501 failed: port is already allocated`というエラーが表示される

**解決方法**:

1. 使用中のプロセスを確認して停止する
2. または、`docker-compose.yml`のポート番号を変更する

```yaml
ports:
  - "8502:8501"  # ホスト側のポートを8502に変更
```

変更後、`http://localhost:8502`でアクセスします。

### Dockerが起動していない

**症状**: `Cannot connect to the Docker daemon`というエラーが表示される

**解決方法**:

- Docker Desktopを起動してください
- Linuxの場合は、`sudo systemctl start docker`でDockerサービスを起動してください

### データファイルが見つからない

**症状**: アプリケーション起動時に「データファイルが見つかりません」というエラーが表示される

**解決方法**:

1. `data/`ディレクトリが存在することを確認
2. 必須ファイルが存在することを確認：
   - `M_YT_LIVE.TSV`
   - `M_YT_LIVE_TIMESTAMP.TSV`
   - `V_SONG_LIST.TSV`
3. ファイルが欠落している場合は、リポジトリを再クローンしてください

### コンテナのビルドに失敗する

**症状**: `docker-compose up`実行時にビルドエラーが発生する

**解決方法**:

1. インターネット接続を確認
2. Dockerのキャッシュをクリアして再ビルド：

```bash
docker-compose build --no-cache
docker-compose up
```

### 文字化けが発生する

**症状**: 日本語が正しく表示されない

**解決方法**:

- ブラウザの文字エンコーディング設定を「UTF-8」に変更してください
- Dockerコンテナは自動的にUTF-8を使用するため、通常は問題ありません

## 開発ワークフロー

### コードの変更

ローカルでコードを変更すると、ボリュームマウントにより自動的にコンテナ内に反映されます。Streamlitは変更を検知して自動的にリロードします。

### ブランチ戦略

- **develop**: 開発用ブランチ（ステージング環境: stg-shinoutatime.streamlit.app）
- **main**: 本番用ブランチ（本番環境: shinoutatime.streamlit.app）
- **update-data**: データファイル更新専用ブランチ

詳細は`BRANCH_STRATEGY.md`を参照してください。

## 追加情報

### Dev Containerを使用する場合

VS Codeユーザーは、Dev Container機能を使用することもできます：

1. VS Codeで「Remote - Containers」拡張機能をインストール
2. プロジェクトを開く
3. コマンドパレット（`Ctrl+Shift+P`）から「Remote-Containers: Reopen in Container」を選択

### Python仮想環境を使用する場合

Dockerを使用せずにPython仮想環境で実行することも可能です。詳細は`docs/developer-guide.md`を参照してください。

## サポート

問題が解決しない場合は、以下を確認してください：

- [トラブルシューティングガイド](TROUBLESHOOTING.md)
- [FAQ](docs/faq.md)
- [GitHubのIssue](https://github.com/your-username/shinouta-time/issues)

---

**環境構築が完了したら、開発を楽しんでください！** 🎵
