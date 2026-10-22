# しのうたタイム - ローカル環境構築ガイド

手元で「しのうたタイム」を動かし、テストを流せるようにするまでの手順です。開発・テスト・データの取り込みは、すべて Docker のコンテナで行います。

## 前提

- **Docker Desktop**(Windows・Mac)または Docker Engine(Linux)。`docker compose version` で確かめます
- **Git**
- Windows では、コマンドを **Git Bash** で打ちます(この文書とほかの文書のコマンドは、Git Bash の書き方です)

## 1. 取得

```bash
git clone https://github.com/kajuen-kajuen/shinoutatime-streamlit.git
cd shinoutatime-streamlit
```

作業は、用件ごとに `origin/develop` から作業ブランチを作って行います(`main`・`develop` では作業しません)。手順は [ブランチ戦略](docs/development/BRANCH_STRATEGY.md) にあります。

```bash
git switch -c feature/xxx origin/develop
```

## 2. 環境変数(任意)

`.env.example` を `.env` にコピーし、必要な値だけ書きます。`.env` は Git に入れません(公開リポジトリなので、値をコミットしない)。

```bash
cp .env.example .env
```

`docker-compose.yml` がコンテナに渡すのは、次の変数です。

| 変数 | 用途 | 既定 |
|---|---|---|
| `SHINOUTA_LOG_LEVEL` | ログの細かさ(DEBUG・INFO・WARNING・ERROR) | INFO |
| `SHINOUTA_ENABLE_FILE_LOGGING` | ログをファイルにも書く(10MB で回し、5世代残す) | false |
| `SHINOUTA_LOG_FILE` | ログファイルの場所 | `logs/shinouta.log` |
| `YOUTUBE_API_KEY` | 取り込み(`ingest`)が使う YouTube Data API v3 のキー。画面だけなら不要 | なし |
| `YOUTUBE_API_KEYS` | 複数のキー(カンマ区切り)。上限に達したら次のキーへ切り替える | なし |
| `SHINOUTA_TRUSTED_COMMENTERS` | セットリストのコメントを優先する職人さんの表示名(カンマ区切り) | なし |

画面の設定(`SHINOUTA_V2_DATA_DIR`・`SHINOUTA_INITIAL_DISPLAY_LIMIT`・`SHINOUTA_DISPLAY_INCREMENT` など。`src/config/settings.py`)は既定のままで動きます。変えるときは `docker-compose.yml` の `environment` にも足します。

## 3. 起動

```bash
docker compose up -d                      # 初回はイメージのビルドで数分かかる
docker compose ps                         # shinouta-time が running なら起動済み
docker compose logs -f shinouta-time      # ログを見る(Ctrl+C で抜ける)
```

ブラウザで http://localhost:8501 を開きます。

## 4. 確かめる

```bash
docker compose exec shinouta-time pytest tests/e2e -q   # 本物の data/v2/ で、ページの起動・検索・さらに表示を確かめる
docker compose exec shinouta-time pytest                # 全部(作業の終わりに)
```

画面でも次を見ます。

- Home の検索欄の上に「データは YYYY/MM/DD の配信まで(歌唱 N 件)」が出る
- キーワードを入れて Enter キーで検索でき、件数と表が出る
- リンク(「YouTubeへ👻」など)で、歌ったところが開く
- サイドバーで Information・About Us・Song List beta に移れる

ほかのコマンド(テストの一部だけ・カバレッジ・データの検査・取り込み)は [コマンド集](docs/prompts/_commands.md) にあります。

## 5. コードを変えたとき

`docker-compose.yml` がリポジトリをコンテナの `/app` にマウントしているので、保存すると Streamlit が読み込み直します。`src/` の変更が画面に出ないときは、コンテナを再起動します。

```bash
docker compose restart shinouta-time
```

依存(`requirements*.txt`)を変えたときは、イメージを作り直します(`docker compose up -d --build`)。

## 6. 止める

```bash
docker compose down
```

## 補足

- **Dev Container**: VS Code の拡張機能「Dev Containers」で `.devcontainer/` を開いて使うこともできます。ただし `docker-compose.yml` とは別のイメージで、`.env` の変数も渡りません。テストや取り込みは上の Docker Compose で行います。
- **Python の仮想環境**: Python 3.14 で `pip install -r requirements-dev.txt` → `streamlit run Home.py` とすれば画面は見られます。ただし、このリポジトリの開発・テスト・取り込みは Docker で行う決まりです([CONTRIBUTING.md](CONTRIBUTING.md))。

困ったときは [TROUBLESHOOTING.md](TROUBLESHOOTING.md) を見てください。
