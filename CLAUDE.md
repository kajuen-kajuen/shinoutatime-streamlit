# しのうたタイム — 開発ガイド(AI エージェント向け)

## 最初に読むもの(この順で)

1. この節と「やってはいけないこと」
2. [`docs/prompts/_common-context.md`](docs/prompts/_common-context.md)(前提・絶対制約・決めてよいこと／聞くこと)
3. [`docs/prompts/_commands.md`](docs/prompts/_commands.md)(そのまま打つコマンド。Docker・テスト・データ生成)
4. 使うスキルの本体 `docs/prompts/<x>.md`(`/debug` `/feature` `/refactor` `/review` `/test` `/update-data`。入口は `.claude/skills/`)
5. 触る機能の `docs/specs/<機能>.md` だけ(全部は読まない。一覧は [`docs/README.md`](docs/README.md))

## やってはいけないこと

- `main` にコミット・マージ・push しない。`develop` には push しない(push は持ち主が行う。push されると Streamlit Cloud の本番・stg に自動で反映される)。作業は `feature/xxx` などの作業ブランチで行う。develop への切り替えと `git merge`(作業ブランチへの `origin/develop` の取り込み、読むだけの merge-tree・merge-base)は、毎回ユーザーの確認を取ってから
- 公開リポジトリなので、秘密の値・ローカルの絶対パス・メールアドレスなどの個人情報をコミットしない(`.env`・`.streamlit/secrets.toml`・`.claude/settings.local.json` は Git に入れない)
- `data/v2/*.tsv`・`data/ingest/skipped.tsv` を手で編集しない(`ingest`・`data` の CLI を通す。並びと検査がそろわなくなる)
- データ由来の文字列をエスケープせずに HTML へ埋め込まない。キャッシュ関数(`@st.cache_data`)の中で `st.error` などを表示しない
- コマンドをホストで直接打たない(pip・pytest・streamlit は Docker のコンテナで。例外は `sh tools/check-rules.sh` と git)
- 作業の終わりに `sh tools/check-rules.sh` を流す。git commit は指示があったときだけ、push はしない

## 概要

VTuber「幽音しの」さんの配信で歌われた楽曲を検索し、YouTube の該当箇所へ直接飛べる**非公式ファンサイト**。Streamlit 製で、Streamlit Community Cloud に公開している。

- 本番: `main` → https://shinoutatime.streamlit.app/
- ステージング: `develop` → https://stg-shinoutatime.streamlit.app/
- データ v2 の更新用のブランチ: `update-data`(デプロイなし。`origin/develop` から作り直して使い、develop → main で出す)。コードの作業ブランチは用件ごとに `origin/develop` から作る。詳細は [`docs/development/BRANCH_STRATEGY.md`](docs/development/BRANCH_STRATEGY.md)。データの取り込みの手順は `/update-data` スキル([`docs/prompts/update-data.md`](docs/prompts/update-data.md))
- `.github/workflows/wake_up_streamlit.yml` が 6 時間ごとに本番をブラウザ(Playwright。`tools/wake_up_streamlit.py`)で開き、スリープしていれば起こす(stg は対象外。テストの CI は無い。詳細は `docs/deployment.md`)

## 技術スタック

- Python 3.14(Docker イメージ `python:3.14.8-slim-trixie`)、Streamlit(マルチページ: `Home.py` と `pages/NN_Name.py`)、pandas
- 依存は `==` で固定し、3つに分ける: `requirements.txt`(本番。Streamlit Cloud はこれだけを読む)、`requirements-tools.txt`(取り込みの CLI)、`requirements-dev.txt`(テスト。コンテナはこれを入れる)
- データ: `data/` の TSV(UTF-8)。DB は使わない。アプリ(画面)は外部 API を使わない。取り込みの CLI だけが YouTube Data API を使う(キーは `.env` の `YOUTUBE_API_KEY`。複数のキーは `YOUTUBE_API_KEYS`)
- テスト: pytest + hypothesis(`tests/unit`・`property`・`integration`・`e2e`・`performance`。e2e は Streamlit の `AppTest`。性能テストは `--runslow` のときだけ)
- オフラインのツール(CLI): python-Levenshtein(類似曲の検出)は `requirements-tools.txt`。requests は Streamlit が要るので `requirements.txt` に入っている(取り込みの CLI・X の埋め込みの CLI も使う)
- パッケージの `__init__.py` でまとめて import しない(画面が使わない部品とその依存まで読み込むため)。使うモジュールは個別に import する

## 構成

```
Home.py                 入口。HomePage(src/ui/pages/home_page.py)を呼ぶ
pages/                  01_Information / 02_About_Us / 99_Song_List_beta
                        (*_Admin.py・*_Preview.py はローカル専用・Git 管理外)
src/config/             設定(Config、環境変数 SHINOUTA_*)、ログ
src/repositories/       table_repository.py(v2 の5テーブルの読み書き。失敗は DataLoadError を投げる)、file_repository.py(X の埋め込みコードの保存)
src/models/schema.py    v2 のテーブルの定義(列・主キー・値の形)
src/services/・clients/ X の埋め込みコードの取得(twitter_embed_service・twitter_api_client)
src/core/               views.py(v2 の歌唱の一覧・曲ごとの集計)、validation・dataset_ops・text・links
src/ingest/             取り込み(YouTube API・コメントの解析・下書き・曲なしの記録)
src/ui/                 コンポーネント、フッター、style.css、v2_data.py(画面が読む v2 のデータ。キャッシュ付き)
src/cli/                ingest・data(v2 の取り込みと修正)、twitter_embed_cli(今週のスケジュールの埋め込みコード)
data/                   tweet_embed_code.html・tweet_height.txt(Information の今週のスケジュール)
data/v2/                v2: contents・artists・songs・performances・aliases(仕様は docs/specs/data-model.md)
data/ingest/            skipped.tsv(曲なしの記録。Git 管理)。cache/・staged/ は取得結果と下書き(Git 管理外)
tests/                  unit(v2 は unit/v2)/ property / integration / e2e / performance / fixtures
tools/check-rules.sh    絶対制約の機械的な確認(読み取り専用)
docs/                   仕様書・レビュー記録・プロンプト(一覧は docs/README.md)。古い仕様は docs/archive/
```

データの流れ: YouTube の取得 →(`ingest`: 下書き → 判断 → 追記)→ `data/v2/*.tsv` →(`src/core/views.py` で集計。`src/ui/v2_data.py` がキャッシュ)→ Home・Song List。2026-10-21 のフェーズ2で v2 に切り替え、2026-10-23 のフェーズ3で v1(`data.xlsx` → `M_YT_LIVE*.TSV` → `V_SONG_LIST.TSV`)のコード・データ・テストを消した(Git の履歴に残る)

## 書き方

- やり取り・ドキュメント・コメント・docstring は日本語。識別子は英語
- コミットメッセージは `<type>: <日本語の件名>`(type: feat / fix / data / docs / style / refactor / test / chore)。詳細は `CONTRIBUTING.md`
- 未確定のことは推測で埋めない。【要確認】【仮定: 内容】を付け、成果物の末尾に一覧にする
- テストが通っていない状態で「完了」と報告しない。テスト結果は実際の出力を貼る
- 複数ファイルにまたがる変更は、Plan Mode で計画を出して承認を得てから実装する

## 関連ドキュメント

- [`README.md`](README.md): 利用者・開発者向けの全体説明
- [`CONTRIBUTING.md`](CONTRIBUTING.md): コーディング規約・コミット規約
- [`docs/architecture/overview.md`](docs/architecture/overview.md): 構成の概要(層・データの流れ・エラー・キャッシュ)。古い構成の文書は `docs/archive/`
- [`docs/specs/data-model.md`](docs/specs/data-model.md): データモデル v2 の正本
- [`docs/deployment.md`](docs/deployment.md): デプロイと反映の確認。v1 の資料は `docs/archive/`(参照用)
- `.cursorrules`: Cursor 向けの同じ方針(日本語・Docker で実行。この CLAUDE.md を読む)
