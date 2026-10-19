# 共通コンテキスト(しのうたタイム)

全プロンプト共通の前提と絶対制約。各スキルの実行前に必ず読み込むこと。

## プロジェクト前提

- **公開リポジトリ**。コミットしたものは push した時点で誰でも読める。秘密の値・ローカルの絶対パス・個人情報は書かない
- Streamlit のマルチページ構成。入口は `Home.py`(本体は `src/ui/pages/home_page.py` の `HomePage`)、ほかのページは `pages/NN_Name.py`(番号順にサイドバーへ並ぶ)。`pages/*_Admin.py` はローカル専用で Git 管理外
- 層: `src/repositories/`(TSV 読み込み) → `src/services/`(DataService ほか) → `src/core/data_pipeline.py`(結合・変換・ソート) → `src/ui/`。DI フレームワークは使わず、コンストラクタで依存を渡す
- エラー: リポジトリとサービスは失敗時に例外(`src/exceptions/errors.py` の `DataLoadError`・`DataProcessingError` ほか)を投げる。`None` を返したり、エラーを状態として持ったりしない(2026-05 のリファクタ dd4b385 で統一)。例外はページ側で捕まえて `st.error` で表示する
- キャッシュ: 読み込みは `@st.cache_data` の関数で行う。キャッシュ関数の中では `st.*` で表示しない(キャッシュが効いた実行では表示されなくなる)
- データ: `data/` の TSV は UTF-8・タブ区切り。配信日の形式は `YYYY/M/D`(時刻付き `YYYY/M/D HH:MM` が混ざることがある【要確認】)。`V_SONG_LIST.TSV` は `song_list_generator` の生成物なので手で直さない。アーティストの読みは `ARTIST_SORT_MAPPING.TSV`(`artist_sort_cli`)で補正する
- デプロイ: Streamlit Community Cloud がブランチを見て自動デプロイする(`main` → 本番、`develop` → stg)。`requirements.txt` がそのまま本番に入る
- 実行環境: Docker(`docker-compose.yml` のサービス名 `shinouta-time`、作業ディレクトリ `/app` にリポジトリをマウント)。コンテナには git が無いので、git と `tools/check-rules.sh` はホストの Git Bash で打つ
- 表示: 利用者の多くはスマホ。表は横に長くしすぎない。Streamlit の内部クラス名(`st-emotion-cache-*`)に依存した CSS は版を上げると壊れる

## 絶対制約

`sh tools/check-rules.sh` で 1・2 を確かめ、4・5 は WARN で知らせる(既知の違反を直したら NG に上げる)。

1. `main`・`develop` にコミット・マージ・push しない。作業ブランチで行い、push はユーザーの指示があったときだけ(`check-rules.sh` がブランチを確かめる。`settings.json` で push・merge・rebase を deny)
2. 秘密の値(`.env`・`secrets.toml`・トークン)、ローカルの絶対パス、メールアドレスをコミットしない(`check-rules.sh` が追跡中・未追跡のファイルを grep する)
3. `data/` の TSV と `data.xlsx` を、確認なしで上書き・削除しない。生成ツールはまず `--dry-run` で件数を見る。配信・歌唱の件数が減るときは必ず止まって報告する
4. データ由来の文字列(曲名・アーティスト・配信タイトル・URL)をエスケープせずに HTML へ埋め込まない(`to_html(escape=False)`・`unsafe_allow_html=True` を新しく足さない)
5. キャッシュ関数の中で `st.*` を表示しない。エラーは例外で上げてページ側で表示する

## 決めてよいこと・聞くこと

迷ったらこの表。「聞く」に当たるものは、案を出して止まり、ユーザーの返事を待つ。

| 決めてよい(進めてよい) | 聞く(止まる) |
|---|---|
| 命名、private 関数の分割、既存のパターンに沿ったファイルの分割 | `data/` の TSV・xlsx を書き換える、列や形式を変える |
| 純粋なロジック(パイプライン・検索・URL 生成・番号付け)へのテストの追加 | 依存(`requirements.txt`)を足す・消す・版を変える |
| ログの文言、コメント、docstring | ページを足す・消す・名前や順番を変える(URL が変わる) |
| 既存のパターンに沿った小さな UI の調整(文言・並び・余白) | 画面の構成を変える、表示する列・リンク先を変える |
| `docs/specs/` の「エッジケース」「確認結果」への追記 | 仕様書の「未決事項」を決める、ブランチ運用・デプロイ設定を変える |
| | 秘密の値・環境変数を足す、外部サービス(API・埋め込み)を足す |

## テスト規約

- 置き場所: 純粋なロジックは `tests/unit/`、性質(どんな入力でも成り立つこと)は `tests/property/`(hypothesis)、複数の層をまたぐものは `tests/integration/`、ページの起動・操作は `tests/e2e/`(`streamlit.testing.v1.AppTest`)
- テストの期待値は仕様(`_common-context.md`・`docs/specs/`)を根拠にする。今の実装の出力をそのまま期待値にしない
- テストのデータは `tests/fixtures/` か、テストの中で作る小さな DataFrame で。e2e 以外は `data/` の本物の TSV に頼らない
- ネットワークに出るテストを書かない(ツイート埋め込みなどはモックで)

## 表記規約(全プロンプト共通)

- 情報が不足している箇所を推測で埋めない。仕様が分岐する未確定事項は【要確認】として質問し、細部は妥当な仮定を置いて【仮定: 内容】と明記して先へ進む
- 成果物の末尾に【要確認】【仮定】の一覧を集約する(本文に埋もれさせない)
- やり取り・ドキュメント・コメントは日本語。コミットメッセージは `<type>: <日本語の件名>`
