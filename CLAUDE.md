# しのうたタイム — 開発ガイド(AI エージェント向け)

## 最初に読むもの(この順で)

1. この節と「やってはいけないこと」
2. [`docs/prompts/_common-context.md`](docs/prompts/_common-context.md)(前提・絶対制約・決めてよいこと／聞くこと)
3. [`docs/prompts/_commands.md`](docs/prompts/_commands.md)(そのまま打つコマンド。Docker・テスト・データ生成)
4. 使うスキルの本体 `docs/prompts/<x>.md`(`/debug` `/feature` `/refactor` `/review` `/test` `/update-data`。入口は `.claude/skills/`)
5. 触る機能の `docs/specs/<機能>.md` だけ(全部は読まない。一覧は [`docs/README.md`](docs/README.md))

## やってはいけないこと

- `main`・`develop` にコミット・マージ・push しない(push されると Streamlit Cloud の本番・stg に自動で反映される)。作業は `feature/xxx` などの作業ブランチで行う
- 公開リポジトリなので、秘密の値・ローカルの絶対パス・メールアドレスなどの個人情報をコミットしない(`.env`・`.streamlit/secrets.toml`・`.claude/settings.local.json` は Git に入れない)
- `data/*.TSV`・`data/data.xlsx` を確認なしで上書き・削除しない(生成ツールはまず `--dry-run`。件数が大きく変わったら報告して止まる)
- `data/v2/*.tsv`・`data/ingest/skipped.tsv` を手で編集しない(`ingest`・`data` の CLI を通す。並びと検査がそろわなくなる)
- データ由来の文字列をエスケープせずに HTML へ埋め込まない。キャッシュ関数(`@st.cache_data`)の中で `st.error` などを表示しない
- コマンドをホストで直接打たない(pip・pytest・streamlit は Docker のコンテナで。例外は `sh tools/check-rules.sh` と git)
- 作業の終わりに `sh tools/check-rules.sh` を流す。git commit は指示があったときだけ、push はしない

## 概要

VTuber「幽音しの」さんの配信で歌われた楽曲を検索し、YouTube の該当箇所へ直接飛べる**非公式ファンサイト**。Streamlit 製で、Streamlit Community Cloud に公開している。

- 本番: `main` → https://shinoutatime.streamlit.app/
- ステージング: `develop` → https://stg-shinoutatime.streamlit.app/
- データ更新用のブランチ: `update-data`(デプロイなし)。詳細は [`docs/development/BRANCH_STRATEGY.md`](docs/development/BRANCH_STRATEGY.md)。データの取り込みの手順は `/update-data` スキル([`docs/prompts/update-data.md`](docs/prompts/update-data.md))
- `.github/workflows/wake_up_streamlit.yml` が 6 時間ごとに両環境へアクセスし、スリープを防いでいる(テストの CI は無い)

## 技術スタック

- Python 3.14(Docker イメージ `python:3.14.8-slim-trixie`)、Streamlit(マルチページ: `Home.py` と `pages/NN_Name.py`)、pandas
- 依存は `==` で固定し、3つに分ける: `requirements.txt`(本番。Streamlit Cloud はこれだけを読む)、`requirements-tools.txt`(データ生成の CLI)、`requirements-dev.txt`(テスト。コンテナはこれを入れる)
- データ: `data/` の TSV(UTF-8)。DB は使わない。アプリ(画面)は外部 API を使わない。取り込みの CLI だけが YouTube Data API を使う(キーは `.env` の `YOUTUBE_API_KEY`)
- テスト: pytest + hypothesis(`tests/unit`・`property`・`integration`・`e2e`・`performance`。e2e は Streamlit の `AppTest`。性能テストは `--runslow` のときだけ)
- オフラインのツール(CLI): pykakasi(読み)、python-Levenshtein(類似曲の検出)は `requirements-tools.txt`。openpyxl(Excel)と requests は `requirements.txt` に入っている

## 構成

```
Home.py                 入口。HomePage(src/ui/pages/home_page.py)を呼ぶ
pages/                  01_Information / 02_About_Us / 99_Song_List_beta
                        (*_Admin.py・*_Preview.py はローカル専用・Git 管理外。9x_V2_*_Preview.py は v2 の確認用ページ)
src/config/             設定(Config、環境変数 SHINOUTA_*)、ログ
src/repositories/       TSV の読み込み(失敗は DataLoadError を投げる)。table_repository.py は v2 の5テーブル
src/models/schema.py    v2 のテーブルの定義(列・主キー・値の形)
src/services/           DataService・SearchService・SongListService ほか(v1)
src/core/               DataPipeline(v1)、views.py(v2 の歌唱の一覧・曲ごとの集計)、validation・dataset_ops・text・links
src/ingest/             取り込み(YouTube API・コメントの解析・下書き・曲なしの記録)
src/ui/                 コンポーネント、フッター、style.css
src/cli/                ingest・data(v2 の取り込みと修正)、excel_to_tsv_cli・song_list_generator・artist_sort_cli(v1)、twitter_embed_cli
data/                   v1: M_YT_LIVE.TSV(配信)・M_YT_LIVE_TIMESTAMP.TSV(歌唱)・V_SONG_LIST.TSV(生成物)・ARTIST_SORT_MAPPING.TSV・data.xlsx
data/v2/                v2: contents・artists・songs・performances・aliases(仕様は docs/specs/data-model.md)
data/ingest/            skipped.tsv(曲なしの記録。Git 管理)。cache/・staged/ は取得結果と下書き(Git 管理外)
tests/                  unit(v2 は unit/v2)/ property / integration / e2e / performance / fixtures
tools/check-rules.sh    絶対制約の機械的な確認(読み取り専用)
docs/                   仕様書・レビュー記録・プロンプト(一覧は docs/README.md)。古い仕様は docs/archive/
```

データの流れ(2つが並んでいる):
- **v1(今の画面が読む)**: `data.xlsx` →(`excel_to_tsv_cli`)→ `M_YT_LIVE*.TSV` →(`song_list_generator`)→ `V_SONG_LIST.TSV` → アプリが読み込んで表示
- **v2(今後の正本)**: YouTube の取得 →(`ingest`: 下書き → 判断 → 追記)→ `data/v2/*.tsv` →(`src/core/views.py` で集計)→ 画面。本番の画面を v2 に切り替えるのはこれから(フェーズ2)。今は確認用ページだけが v2 を読む

## 書き方

- やり取り・ドキュメント・コメント・docstring は日本語。識別子は英語
- コミットメッセージは `<type>: <日本語の件名>`(type: feat / fix / data / docs / style / refactor / test / chore)。詳細は `CONTRIBUTING.md`
- 未確定のことは推測で埋めない。【要確認】【仮定: 内容】を付け、成果物の末尾に一覧にする
- テストが通っていない状態で「完了」と報告しない。テスト結果は実際の出力を貼る
- 複数ファイルにまたがる変更は、Plan Mode で計画を出して承認を得てから実装する

## 関連ドキュメント

- [`README.md`](README.md): 利用者・開発者向けの全体説明
- [`CONTRIBUTING.md`](CONTRIBUTING.md): コーディング規約・コミット規約
- [`docs/architecture/`](docs/architecture/): アーキテクチャ・データフロー・エラー処理
- [`docs/specs/data-model.md`](docs/specs/data-model.md): データモデル v2 の正本
- [`docs/data-management.md`](docs/data-management.md)(v1 のデータ)・[`docs/deployment.md`](docs/deployment.md)
- `.cursorrules`: Cursor 向けの同じ方針(日本語・Docker で実行。この CLAUDE.md を読む)
