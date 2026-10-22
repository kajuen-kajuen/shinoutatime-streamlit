# デプロイメントガイド

「しのうたタイム」は Streamlit Community Cloud で公開しています。この文書は、公開の環境・スリープ防止・依存と Python の版・アプリの作り直し・反映の確認をまとめたものです。ブランチとリリースの手順は [ブランチ戦略](development/BRANCH_STRATEGY.md) にあります。

## 今の環境(2026-10)

| ブランチ | 環境 | URL |
|---|---|---|
| `main` | 本番 | https://shinoutatime.streamlit.app/ |
| `develop` | ステージング(stg) | https://stg-shinoutatime.streamlit.app/ |

- どちらも、ブランチに push すると自動で再デプロイされます(数分)。
- 開発の流れは「作業ブランチ(`feature/xxx` など)→ `develop`(stg で確認)→ `main`(本番)」です。`develop`・`main` への統合と push は、持ち主が手で行います。
- `.github/workflows/wake_up_streamlit.yml` が6時間ごとに本番をブラウザで開き、スリープを防いでいます(stg は対象外。テストの CI はありません)。

## スリープ防止(wake_up_streamlit.yml)

Community Cloud のアプリは、しばらくアクセスが無いとスリープします。スリープ中は HTML を取るだけでは起きず、画面の「Yes, get this app back up!」を押す必要があります。

- 日本時間 0・6・12・18 時に、GitHub Actions が `tools/wake_up_streamlit.py`(Playwright の Chromium)で本番を開きます。ボタンがあれば押し、見出し「しのうたタイム」が出るまで最大 3 分待ちます。
- 見出しが出なければ実行が失敗になり、GitHub から失敗の通知が届きます。そのときの画面は、実行の Artifacts の `wake-up-screenshots` で見られます。
- 公開リポジトリでは、60 日活動が無いと定期実行が自動で無効になります。これを防ぐため、毎回の最後に自分自身を有効にし直しています。
- それでも無効になったとき(Actions の画面に「This scheduled workflow is disabled」と出る)は、`gh workflow enable wake_up_streamlit.yml` か、Actions の画面の「Enable workflow」で戻します。
- 定期実行は `main` のワークフロー定義だけが使われます。変更を試すときは、作業ブランチを push して `gh workflow run wake_up_streamlit.yml --ref <ブランチ>` で手動実行します。

## 依存と Python の版

- Cloud が読むのは `requirements.txt` だけです。`requirements-tools.txt`(データの CLI)と `requirements-dev.txt`(テスト)は読みません。
- 版は `==` で固定し、ビルドのたびに版が変わらないよう、間接の依存(`numpy`・`pyarrow` など)まで固定しています。直接の依存を上げたときの取り直し方は、`requirements.txt` の中のコメントにあります。
- `pyarrow` は 24.0.0 に固定しています。Cloud は 26.0.0 を「落ちる不具合がある」(apache/arrow#50471)として 25 未満に差し替えるので、Cloud が実際に入れる版に合わせています。
- 依存を変えたら、先にコンテナでテストと画面を確かめ、stg に出してビルドのログを見てから本番に出します。
- Python は **3.14**(手元のコンテナは `python:3.14.8-slim-trixie`)。Cloud の Python の版は、アプリを作るときに「Advanced settings」で選び、**あとから変えられません**。変えるときは、次の手順でアプリを作り直します。

## アプリを作り直す(Python の版を上げるときなど)

1. 今の設定を控える: カスタムサブドメイン(`shinoutatime` / `stg-shinoutatime`)、リポジトリ、ブランチ、Main file path(`Home.py`)、Secrets(アプリは読まないが、入っていれば控える)
2. 新しい Python で `requirements.txt` が入り、テストが通ることを、コンテナ(`Dockerfile` の Python を同じ版にしたもの)で確かめる
3. Cloud のダッシュボードでアプリを削除する(削除すると、サブドメインはすぐに使い直せる)
4. 「New app」で作り直す: 同じリポジトリ・ブランチ(本番は `main`、stg は `develop`)・`Home.py` を選び、サブドメインを元と同じにし、「Advanced settings」で Python の版を選ぶ
5. 下の「反映の確認」をする。**stg で先に行い、問題がなければ本番**

## 反映の確認

push のあと、Cloud のダッシュボードの「Manage app」→ ログで、ビルドと起動を確かめます。

**`src/` を変えたリリースのあとは、「Manage app」→ 右上の「⋮」→「Reboot app」でアプリを起動し直します。** Cloud は push を受けると、動いているアプリを止めずにファイルだけを差し替えます。ページのファイルは読み直されますが、すでに読み込まれていた `src/` の部品は古い版のまま残るので、新しく足した関数を読むところで `ImportError` になることがあります(2026-10-22、本番の Information で起きた。stg はリリースのあとに起動したので出なかった)。データ(`data/`)だけのリリースでは要りません。

- 依存のインストールでエラーや、版の差し替えの警告が出ていない
- 起動後に例外が出ていない

画面では次を確かめます。

- [ ] Home の検索欄の上に「データは YYYY/MM/DD の配信まで(歌唱 N 件)」が出て、日付が出したデータに合っている
- [ ] キーワードを入れて Enter キーで検索でき、件数と表が出る
- [ ] リンク(「YouTubeへ👻」など)で、歌ったところが開く
- [ ] 楽曲リスト(Song List beta)が出て、「さらに25件表示」で増える
- [ ] Information の動画、今週のスケジュール(X の投稿)と、Wiki・X・公式サイトへのリンクが出る
- [ ] どのページにも見出し「しのうたタイム👻🫧」とフッターが出る

本番では、Reboot app のあとにブラウザの確認を流します(4ページが PC・スマホの幅で例外なく開く、検索とリンク、はみ出し。上のチェックの一部を自動で確かめる)。スリープしていると開けないので、先に起こします。

```bash
docker compose --profile browser run --rm browser sh -c "python tools/wake_up_streamlit.py https://shinoutatime.streamlit.app/ && pytest tests/browser --runbrowser --base-url https://shinoutatime.streamlit.app/"
```

stg はログインが要るので、ブラウザの確認は流せません。stg は上のチェックを目で確かめます。

## ログとエラーのとき

- ログは「Manage app」から見られ、ファイルに落とすこともできます。落としたログ(`logs-*.txt`)はリポジトリの直下に置いて読めますが、Git には入れません(`.gitignore` 済み)。
- 直すときは、手元で直して作業ブランチ → `develop`(stg で確認)→ `main` の順に出します。手元で起きるときの直し方は [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)。

## 秘密の値

- 今の画面は、Cloud の Secrets も環境変数も使いません(`SHINOUTA_*` の設定は既定のまま)。
- 取り込みの YouTube Data API のキーは手元の `.env` にだけ置き、Cloud には置きません(画面は外部の API を使わない)。
- 公開リポジトリなので、秘密の値をコミットしません(`sh tools/check-rules.sh` で確かめる)。

## データの反映

データ v2(`data/v2/`)は本番の画面が読むので、コードと同じく `develop` で確かめてから `main` に出します。取り込みは `update-data` ブランチで行います([ブランチ戦略](development/BRANCH_STRATEGY.md)・[取り込みの手順](prompts/update-data.md))。push すると Cloud が再デプロイし、新しいデータで読み込み直します。
