# トラブルシューティング

手元で「しのうたタイム」を動かすとき・テストや取り込みをするときに、このプロジェクトで起きやすいことと直し方です。環境の作り方は [SETUP.md](SETUP.md)、本番(Streamlit Community Cloud)のことは [docs/deployment.md](docs/deployment.md) にあります。

コマンドは Git Bash で、リポジトリの直下から打ちます。

## Docker

### `Cannot connect to the Docker daemon` などで、コマンドが通らない

Docker Desktop が起動していません。起動してから、もう一度打ちます。

### `port is already allocated`(ポート 8501 が使われている)

ほかの Streamlit や、前に起動したコンテナが 8501 番を使っています。

- `docker compose ps` と `docker ps` で動いているコンテナを確かめ、要らないものを止める(`docker compose down`)
- それでも空かないときは、`docker-compose.yml` の `ports` を `"127.0.0.1:8502:8501"` などにして、http://localhost:8502 で開く(この変更はコミットしない)

### イメージのビルドに失敗する

ネットワークを確かめてから、キャッシュを使わずに作り直します。

```bash
docker compose build --no-cache
docker compose up -d
```

## 画面

### `src/` を直したのに、画面が変わらない

起動中のアプリが古いモジュールを読み込んだままのことがあります(Windows・WSL のファイルの監視のため)。再起動します。

```bash
docker compose restart shinouta-time
```

### Home に「データの読み込みまたは処理中にエラーが発生しました。」と出る

その下に理由が出ています。ログにも詳しく残ります(`docker compose logs --tail=100 shinouta-time`)。

- 「データのディレクトリがありません」: `data/v2/` が無いか、`SHINOUTA_V2_DATA_DIR` の指定が違う
- TSV が読めない・列が足りない: `data/v2/*.tsv` を手で編集していないか確かめる(`git diff data/v2`)。検査は次のコマンドで流せます

```bash
docker compose exec shinouta-time python -m src.cli.data validate
```

楽曲リストの「楽曲リストを読み込めませんでした。」も、原因と確かめ方は同じです。

### データを直したのに、画面が古いまま

読み込みはキャッシュしていますが、データファイルと集計のコードの更新日時が変わると計算し直します。それでも古いときは、ブラウザを再読み込みするか、`docker compose restart shinouta-time` で確実に読み直します。

## テスト

- ホストで `pytest` を打たない。コンテナの中で流します(`docker compose exec shinouta-time pytest`)。ホストの Python とは版や依存が違うため、結果が合いません
- e2e(`tests/e2e`)は本物の `data/v2/` を読みます。データを取り込んだ直後に落ちたら、まず `data validate` を流します
- 性能のテスト(`tests/performance`)は `--runslow` を付けたときだけ動きます。付けないと skipped になるのは正常です

## データの取り込み(ingest)

### 「環境変数 YOUTUBE_API_KEY(または YOUTUBE_API_KEYS)が設定されていません」

`.env` に `YOUTUBE_API_KEY` を書き、コンテナを作り直して読み込ませます(`docker compose up -d`)。キーの作り方は `.env.example` のコメントにあります。

### 「すべての API キーで上限に達しました」

YouTube Data API の1日の上限です。`YOUTUBE_API_KEYS` にほかのキーがあれば、自動で次のキーへ切り替えます。すべて使い切ったら、上限が戻る日本時間の16〜17時以降に流し直します。

### メンバー限定の動画のコメントが取れない

API キーではメン限の動画のコメントを読めません(403)。取り込みはコメント0件で進むので、セットリストは X の告知などで確かめます(手順は [docs/prompts/update-data.md](docs/prompts/update-data.md))。

## Git

### コミットが止まる(check-rules の NG)

コミットの前に `sh tools/check-rules.sh` が流れ、NG があると止まります。出た NG(秘密の値・絶対パス・メールアドレス、`main`・`develop` でのコミット、エスケープしない HTML など)を直してから、もう一度コミットします。

### `.github/workflows/` を変えた push が断られる

GitHub の認証に `workflow` の権限がありません。直し方は [ブランチ戦略のトラブルシューティング](docs/development/BRANCH_STRATEGY.md#トラブルシューティング) にあります。

### PowerShell でコマンドが動かない

この文書とほかの文書のコマンドは Git Bash の書き方です(`cp`・`$VAR`・`/` の区切りなど)。Git Bash で打ちます。

## それでも解決しないとき

ログ(`docker compose logs --tail=100 shinouta-time`)と、打ったコマンド・出た文言を添えて、GitHub の [Issue](https://github.com/kajuen-kajuen/shinoutatime-streamlit/issues) でお知らせください。
