# しのうたタイム — 開発ガイド(AI エージェント向け)

## 最初に読むもの(この順で)

1. この節と「やってはいけないこと」
2. [`docs/prompts/_common-context.md`](docs/prompts/_common-context.md)(前提・絶対制約・決めてよいこと／聞くこと)
3. [`docs/prompts/_commands.md`](docs/prompts/_commands.md)(そのまま打つコマンド。Docker・テスト・データ生成)
4. 使うスキルの本体 `docs/prompts/<x>.md`(`/debug` `/feature` `/refactor` `/review` `/test`。入口は `.claude/skills/`)
5. 触る機能の `docs/specs/<機能>.md` だけ(全部は読まない。一覧は [`docs/README.md`](docs/README.md))

## やってはいけないこと

- `main`・`develop` にコミット・マージ・push しない(push されると Streamlit Cloud の本番・stg に自動で反映される)。作業は `feature/xxx` などの作業ブランチで行う
- 公開リポジトリなので、秘密の値・ローカルの絶対パス・メールアドレスなどの個人情報をコミットしない(`.env`・`.streamlit/secrets.toml`・`.claude/settings.local.json` は Git に入れない)
- `data/*.TSV`・`data/data.xlsx` を確認なしで上書き・削除しない(生成ツールはまず `--dry-run`。件数が大きく変わったら報告して止まる)
- データ由来の文字列をエスケープせずに HTML へ埋め込まない。キャッシュ関数(`@st.cache_data`)の中で `st.error` などを表示しない
- コマンドをホストで直接打たない(pip・pytest・streamlit は Docker のコンテナで。例外は `sh tools/check-rules.sh` と git)
- 作業の終わりに `sh tools/check-rules.sh` を流す。git commit は指示があったときだけ、push はしない

## 概要

VTuber「幽音しの」さんの配信で歌われた楽曲を検索し、YouTube の該当箇所へ直接飛べる**非公式ファンサイト**。Streamlit 製で、Streamlit Community Cloud に公開している。

- 本番: `main` → https://shinoutatime.streamlit.app/
- ステージング: `develop` → https://stg-shinoutatime.streamlit.app/
- データ更新: `update-data`(デプロイなし)。詳細は [`docs/development/BRANCH_STRATEGY.md`](docs/development/BRANCH_STRATEGY.md)
- `.github/workflows/wake_up_streamlit.yml` が 6 時間ごとに両環境へアクセスし、スリープを防いでいる(テストの CI は無い)

## 技術スタック

- Python 3.11(Docker イメージ `python:3.11-slim`)、Streamlit(マルチページ: `Home.py` と `pages/NN_Name.py`)、pandas
- データ: `data/` の TSV(UTF-8)。DB・外部 API は使わない
- テスト: pytest + hypothesis(`tests/unit`・`property`・`integration`・`e2e`。e2e は Streamlit の `AppTest`)
- オフラインのツール(CLI): pykakasi(読み)、python-Levenshtein(類似曲の検出)、openpyxl(Excel)

## 構成

```
Home.py                 入口。HomePage(src/ui/pages/home_page.py)を呼ぶ
pages/                  01_Information / 02_About_Us / 99_Song_List_beta(*_Admin.py はローカル専用・Git 管理外)
src/config/             設定(Config、環境変数 SHINOUTA_*)、ログ
src/repositories/       TSV の読み込み(失敗は DataLoadError を投げる)
src/services/           DataService・SearchService・SongListService ほか
src/core/               DataPipeline(読み込み → 結合 → 変換 → ソート)、utils
src/ui/                 コンポーネント、フッター、style.css
src/cli/                データ生成ツール(excel_to_tsv_cli・song_list_generator・artist_sort_cli・twitter_embed_cli)
data/                   M_YT_LIVE.TSV(配信)・M_YT_LIVE_TIMESTAMP.TSV(歌唱)・V_SONG_LIST.TSV(楽曲一覧、生成物)・ARTIST_SORT_MAPPING.TSV・data.xlsx
tests/                  unit / property / integration / e2e / fixtures
tools/check-rules.sh    絶対制約の機械的な確認(読み取り専用)
docs/                   仕様書・レビュー記録・プロンプト(一覧は docs/README.md)。古い仕様は docs/archive/
```

データの流れ: `data.xlsx` →(`excel_to_tsv_cli`)→ `M_YT_LIVE*.TSV` →(`song_list_generator`)→ `V_SONG_LIST.TSV` → アプリが読み込んで表示。

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
- [`docs/data-management.md`](docs/data-management.md)・[`docs/deployment.md`](docs/deployment.md)
- `.cursorrules`: Cursor 向けの同じ方針(日本語・Docker で実行)
