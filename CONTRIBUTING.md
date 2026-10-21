# コントリビューションガイド

「しのうたタイム」に関心を持っていただき、ありがとうございます。

このリポジトリは、ファン有志1人(持ち主)が AI(Claude Code など)と一緒に運営している、**非公式ファンサイト**のものです。外部からのプルリクエストは前提にしていませんが、データの誤りや不具合の報告は歓迎します(下の「外部の方へ」)。

AI エージェントは、まず [`CLAUDE.md`](CLAUDE.md) を読んでください。この文書は、その要点を人向けにまとめたものです。

## 外部の方へ

- **データの誤り・不具合・要望**: GitHub の Issue で知らせてください。次のことが書かれていると助かります。
  - 該当する配信やショート(タイトルか URL)と、時刻
  - 今の表示と、正しいと思う内容
  - 情報源(配信のコメント、公式の告知など)
- **書かないでほしいもの**: パスワードや API キーなどの秘密の値、ご自身や他人の個人情報(メールアドレスなど)。このリポジトリは公開されています。
- 本サイトは幽音しのさんご本人・所属事務所とは関係ありません。公式の情報は、公式のチャンネルや X を見てください。

## 運用の形

- 持ち主が方針を決め、AI が調査・実装・データの取り込みを手伝います。AI の作業の手順は [`docs/prompts/`](docs/prompts/)(スキルの本体)にあります。
- 変更は、作業ブランチで行います。`main`・`develop` への統合と push は、持ち主が手で行います(下の「ブランチ」)。
- 複数のファイルにまたがる変更は、先に計画を出して、持ち主の承認を得てから実装します。

## 開発環境

**Docker で動かします。** ホストで直接 `pip install`・`pytest`・`streamlit run` を打たないでください(本番のコンテナと環境がずれるため)。

```bash
docker compose up -d                                   # 起動(http://localhost:8501)
docker compose exec shinouta-time pytest               # テスト
sh tools/check-rules.sh                                # 絶対制約の確認(ホストの Git Bash で)
```

ほかのコマンド(データの取り込み・修正、ログ、性能テストなど)は [`docs/prompts/_commands.md`](docs/prompts/_commands.md) にまとめています。

- Python 3.14(Docker イメージ `python:3.14.8-slim-trixie`)
- 依存は `==` で固定し、3つに分けています: `requirements.txt`(本番。Streamlit Community Cloud はこれだけを読む)、`requirements-tools.txt`(データの CLI)、`requirements-dev.txt`(テスト。コンテナはこれを入れる)
- 秘密の値(`YOUTUBE_API_KEY`・`YOUTUBE_API_KEYS`・`ADMIN_PASSWORD` など)は `.env` に書きます。`.env` は Git に入れません。書き方は `.env.example`。

## ブランチ

| ブランチ | 環境 | 扱い |
|---|---|---|
| `main` | 本番(https://shinoutatime.streamlit.app/) | push すると自動で反映される。持ち主だけが統合・push する |
| `develop` | ステージング(https://stg-shinoutatime.streamlit.app/) | 同上 |
| `feature/xxx`・`fix/xxx` など | なし | ここで作業する。用件ごとに `origin/develop` から作り、develop に出したら消す |
| `update-data` | なし | データ v2 の更新(取り込み)用。使うたびに `origin/develop` から作り直し、develop → main で出す |

詳しくは [`docs/development/BRANCH_STRATEGY.md`](docs/development/BRANCH_STRATEGY.md)。

## コミット

- 形式は `<type>: <日本語の件名>`。本文は任意で、変えた理由や中身を箇条書きにします。
- type は次のどれか:

| type | 使うとき |
|---|---|
| `feat` | 機能の追加 |
| `fix` | 不具合の修正 |
| `data` | データ(`data/`)の追加・修正 |
| `docs` | 文書だけの変更 |
| `style` | 見た目(CSS など)、または意味の変わらない書式の変更 |
| `refactor` | 振る舞いを変えない内部の整理 |
| `test` | テストの追加・修正 |
| `chore` | 依存・設定・ツールなど |

- **コードと文書の変更と、データの変更は、別々のコミットにします**(`feat:`/`docs:` と `data:`)。
- 例:
  - `feat: YouTube Data API のキーを複数使えるようにし、上限で次のキーへ切り替える`
  - `data: 2025年10月分(22本)を取り込み data/v2 に登録`
  - `docs: 旧フローの文書に置き換え中と書き、README を今の構成に合わせる`
- コミットの前に `sh tools/check-rules.sh` を流します(AI の環境では、コミットのたびに自動で流れる)。

## データ

データは2つの仕組みが並んでいます(詳しくは [`docs/architecture/overview.md`](docs/architecture/overview.md))。

- **v2(正本。画面が読む)**: `data/v2/` の5つのテーブル。
  - **TSV を手で編集しません。** 追加は取り込みの CLI(`python -m src.cli.ingest`)、修正は `python -m src.cli.data` を通します(保存の前に検査し、決まった順に並べるため)。
  - 取り込みの手順と判断の決まりは [`docs/prompts/update-data.md`](docs/prompts/update-data.md)、データの形は [`docs/specs/data-model.md`](docs/specs/data-model.md)。
  - 配信のコメント本文や投稿者名は `data/ingest/cache/`(Git 管理外)にだけ置き、コミットしません。
- **v1(参照用。画面はもう読まない)**: `data/data.xlsx` から生成する `data/*.TSV`。フェーズ3で消す予定です(【旧フロー】。[`docs/data-management.md`](docs/data-management.md))。
  - 生成ツールは、まず `--dry-run` で件数を確かめ、持ち主の確認を得てから上書きします。

## 書き方

- やり取り・文書・コメント・docstring は日本語、識別子は英語。
- 分からないことは推測で埋めず、【要確認】【仮定: 内容】の印を付けます。
- 画面に出す HTML に、データ由来の文字列をエスケープせずに入れません。
- Streamlit のキャッシュ関数(`@st.cache_data`)の中で `st.error` などを表示しません(例外を投げるか、値として返し、ページで表示する)。
- テストが通っていない状態で「完了」としません。

## テスト

- `docker compose exec shinouta-time pytest` で全部を流します。v2 のテストは `tests/unit/v2/`、性能のテストは `--runslow` のときだけ動きます。
- v1 の古いテストの一部は、今も失敗します(既知の課題。[`docs/architecture/overview.md`](docs/architecture/overview.md) の「既知の課題」)。変更の前後で、失敗が増えていないことを確かめます。
- 詳しくは [`docs/testing/README.md`](docs/testing/README.md)。

## ライセンス

[Apache License 2.0](LICENSE) です。
