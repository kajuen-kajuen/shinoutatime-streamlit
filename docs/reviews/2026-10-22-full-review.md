# 全体 レビュー記録

- 日付: 2026-10-22
- 種別: コードレビュー / データ確認 / セキュリティ確認
- 対象: 全体(`ec92209` 時点。フェーズ2で画面を v2 に切り替えた直後)。関連する仕様書は `docs/specs/data-model.md`
- レビューした人: Claude(Opus 5.5)

## 1. 範囲と観点

見たもの:
- 画面: `Home.py`・`src/ui/pages/home_page.py`・`pages/`(Information・About Us・Song List beta)・`src/ui/components/`・`src/ui/page_setup.py`・`src/ui/v2_data.py`
- v2 のデータの層: `src/models/schema.py`・`src/repositories/table_repository.py`・`src/core/views.py`・`validation.py`・`dataset_ops.py`・`links.py`・`text.py`
- 取り込み: `src/cli/ingest.py`・`src/cli/data.py`・`src/ingest/youtube_api.py`・`staging.py`・`skips.py`
- X の埋め込み: `src/cli/twitter_embed_cli.py`・`data/tweet_embed_code.html`
- 公開と運用: `.gitignore`・`git ls-files`・`.env.example`・`.claude/settings.json`・`.github/workflows/wake_up_streamlit.yml`・`Dockerfile`・`docker-compose.yml`・`requirements*.txt`
- データ: `data/v2/*.tsv`(件数・検査・読みの空・kind の空)

観点: 公開リポジトリとしての安全、データの正しさ、障害時の振る舞い、表示の安全と使いやすさ、保守性、性能(`docs/prompts/review.md` の順)。

見なかったこと:
- v1(`src/services/`・`src/core/data_pipeline.py`・v1 の CLI)の個別の不具合。フェーズ3で消す前提なので、「残っていることの影響」だけを見た
- `src/ingest/parser.py`・`capture.py` の細部(コメントの解析の精度)
- スマホの幅での表示(ブラウザでは見ていない。コードと CSS を読んだだけ)

## 2. 指摘事項

重要度「高」(秘密の漏えい・データの欠落や誤表示・ページが落ちる)の指摘はなかった。

| # | 重要度 | 場所 | 内容 | 対応 | 状態 |
|---|---|---|---|---|---|
| 1 | 中 | `src/core/dataset_ops.py` の `next_id`・`merge_song`・`merge_artist` | ID は「最大値+1」で振るので、`merge-song`・`merge-artist` でいちばん大きい ID を消すと、次に足した曲・アーティストに同じ ID が使われる。仕様(「消しても再利用しない」)と食い違う。`drop-artist` は運用で避けている(docstring)が、merge には歯止めがない。merge の前に作った下書き(`staged/*.tsv` の song_id)を後で apply すると、別の曲に黙って付くことがある。修正案: 最大の ID を消そうとしたら止める(または最後に振った ID を別に持つ)。テストを足す | | 未対応 |
| 2 | 中 | `src/cli/ingest.py` の `cmd_apply` | `apply` は `skipped.tsv` を見ない。曲なしに記録したものを unskip せずに apply すると、登録済みと曲なしの両方になる(`skip` は登録済みを拒むが、逆向きの確認がない)。`status` の表示と次の取り込みの判断がずれる。修正案: apply の前に skips を見て、記録があれば止めて unskip を促す | | 未対応 |
| 3 | 中 | `src/repositories/__init__.py`・`src/services/__init__.py` | 画面は v2 だけを読むのに、`table_repository` を import すると package の `__init__` が v1 のリポジトリ(Excel など)まで読み込む。そのため本番の `requirements.txt` から `requests`・`openpyxl` を外せない(requirements.txt のコメントに明記済み)。起動が重くなり、依存の面も広い。修正案: フェーズ3の最初に `__init__` の一括 import をやめる | | 未対応 |
| 4 | 低 | `src/ui/pages/home_page.py` の `_handle_error` | 読み込みの失敗時に、例外のメッセージ(サーバー上のファイルパスを含む)と「データファイル(TSV)の形式や存在を確認してください」を、公開の画面にそのまま出す。利用者には意味のない開発者向けの文言。修正案: 画面は短い案内だけにし、詳細はログへ(Song List と同じ形にそろえる) | | 未対応 |
| 5 | 低 | `pages/99_Song_List_beta.py` の読み込み失敗時 | `st.error`「楽曲リストを読み込めませんでした。」と、else の `st.warning`「楽曲データが読み込めませんでした。」が二重に出る。修正案: 失敗時は warning を出さない(空のときと分ける) | | 未対応 |
| 6 | 低 | `src/core/views.py` の `build_song_stats`(曲と集計の inner merge) | 切り抜き(`kind=切り抜き`)でしか歌っていない曲は、Home には出るが Song List には出ない。仕様は「数えない」だけで、一覧から消すかは書いていない。2026-10-22 のデータでは該当 0 件。【要確認】一覧に残すか、今のままか。決めたら仕様に書く | | 未対応 |
| 7 | 低 | `data/v2/contents.tsv` | `kind` が空のライブ配信が 6 件(2025-10-17・2025-11-04・2026-02-20・02-21・02-27・02-28)。画面には出ないが、切り抜きの除外などの判断に使う列。修正案: `data set contents <id> kind <値>` で埋める | | 未対応 |
| 8 | 低 | `data/v2/artists.tsv` | どの曲からも参照されていないアーティストが 3 人(a0268 作者不明・a0286 Sharp Hawks・a0314 はなまるおばけ。`data validate` の warning)。どれも最大の ID(a0337)ではないので、`drop-artist` で消せる | | 未対応 |
| 9 | 低 | `src/ui/v2_data.py` の `_load` | `@st.cache_data` に `max_entries` が無い。鍵(更新日時)が変わるたびに古い結果がメモリに残る(Cloud は再デプロイで再起動するので実害は小さい)。修正案: `max_entries=1` | | 未対応 |
| 10 | 低 | `src/ui/twitter_embed_admin.py`・`src/config/settings.py` の `enable_admin_page` | 管理画面のコード(ページは無い)が残り、パスワードを `==` で比べ、`enable_admin_page` の既定が True。今はページが無いので実害なし。修正案: フェーズ3で消す(残すなら `hmac.compare_digest`・既定 False) | | 未対応 |
| 11 | 低 | `pages/02_About_Us.py` | 使っていない `from PIL import Image` | | 未対応 |
| 12 | 低 | `.github/workflows/wake_up_streamlit.yml` | actions をタグ(`@v7`)で指定していて、SHA で固定していない(公開リポジトリの一般的な注意。任意) | | 未対応 |
| 13 | 低 | `src/ui/pages/home_page.py` の検索結果の件数の表示 | 検索語を `st.write` の Markdown にそのまま入れるので、`**` や `[x](…)` が書式として効く。入力した本人の画面だけで、表示が崩れる程度。修正案: Markdown の記号をエスケープする | | 未対応 |
| 14 | 低 | `tests/unit/test_error_cases.py`(2件)・`tests/unit/test_excel_to_tsv_service.py`(1件) | 常にスキップされるテストが 3 件(無い関数・クラスを前提にしている)。v1 のテストで、フェーズ3で消すか、残すなら直す | | 未対応 |

重要度の目安: **高**=秘密・個人情報の漏えい、データの欠落・誤表示、ページが落ちる、**中**=特定の条件で誤動作する・スマホで使いにくい、**低**=見た目・読みやすさ・将来の課題。

### 次にやるべきこと Top 5

1. #1 ID の再利用の歯止め: 仕様違反で、気づかないうちに歌唱が別の曲に付く唯一の経路。小さな修正とテストで閉じられる
2. #2 apply で skipped を確かめる: 取り込みの記録の整合性。数行で済む
3. #4・#5 エラー表示をそろえる: 公開の画面に開発者向けの文言とパスが出ている。Home と Song List を同じ形に
4. #3 フェーズ3の第一歩として `__init__` の一括 import をやめる: 本番の依存(requests・openpyxl)を外せるようになる
5. #6 切り抜きだけの曲の扱いを決めて仕様に書く(あわせて #7・#8 のデータを整える)

## 3. 確認の結果

2026-10-22、ローカルの Docker のコンテナ(`python:3.14.8-slim-trixie`)で確認した。

絶対制約のチェックリスト:

| # | 制約 | 結果 | 根拠 |
|---|---|---|---|
| 1 | main・develop に触れない | OK | `sh tools/check-rules.sh`「作業ブランチ: main-local」。`.claude/settings.json` で push・merge・rebase・main/develop への切り替えを deny |
| 2 | 秘密・個人情報をコミットしない | OK | check-rules の「公開リポジトリ」の項目がすべて OK。`.gitignore` に `.env`・`secrets.toml`・`settings.local.json`・`data/ingest/cache/`・`staged/`。`git ls-files` にも無い。`.env.example` は値なし。YouTube API のキーは、例外のメッセージに URL を入れない形で守っている |
| 3 | データを確認なしで書き換えない | OK | `data` の書き込みは検査を通ったときだけ保存する。`ingest apply` に `--dry-run` がある。v2 の保存はバックアップを取らない(Git で戻せる前提) |
| 4 | エスケープしない HTML を足さない | OK | `escape=False` なし。`unsafe_allow_html=True` は CSS の読み込み・Home の表・Song List の表だけで、データ由来の文字列はどれもエスケープしている |
| 5 | キャッシュ関数の中で表示しない | OK | check-rules で OK。`v2_data._load` は例外を投げるだけで、検査の error はログに書くだけ |

テスト(`docker compose exec shinouta-time pytest -q`):

```
873 passed, 4 skipped in 105.76s (0:01:45)
```

スキップの内訳: `--runslow` のときだけの性能テスト 1 件と、#14 の 3 件。

データの検査(`python -m src.cli.data validate`):

```
[warning] artists: どの曲からも参照されていないアーティストがいます: a0268, a0286, a0314
```

error は 0 件。`data/v2/` の件数は origin/main と同じ(ヘッダーを除いて contents 393・artists 336・songs 787・performances 2318・aliases 859)。ライブ配信の歌唱で時刻が空のものは 0 件。Home にあって Song List に無い曲(#6)は 0 件。

確認できなかったこと: スマホの幅での表示(ブラウザで見ていない)。本番・stg の画面。

## 4. 良かった点

- 画面の表のエスケープが `build_table`・`build_results_table_html`・Song List の `_cell` にまとまっていて、HTML を組み立てる場所が少ない
- キャッシュの鍵にデータとコードの更新日時を入れている(`views.cache_key`)ので、起動したままでも古い集計が返らない
- YouTube API のキーを例外・ログに出さない設計(`YouTubeApiError` に URL を入れない。キーの切り替えは番号だけ表示)
- `data` CLI が「検査を通ったときだけ保存」で、手で TSV を触らなくて済む
- e2e で全ページの起動・読み込み失敗・データが空のときを押さえている

## 5. 結論

修正後に採用(本番はこのままで問題なく動く。中の 3 件は、データの取り込みとフェーズ3の前に直すとよい)。各指摘を直すか見送るかは、この後に決めて「6. 追記」に書く。

## 6. 追記

### 2026-10-22 指摘への対応(ブランチ `fix/review-2026-10-22`)

| # | 状態 | 対応 |
|---|---|---|
| 1 | 対応済み | `dataset_ops._refuse_max_id` を足し、`merge_song`・`merge_artist`・`drop_artist` でいちばん大きい ID を消そうとすると止める(データの形は変えない)。仕様 3.4 にも書いた |
| 2 | 対応済み | `ingest apply` は、`skipped.tsv` に記録があれば止めて unskip を促す(dry-run でも) |
| 3 | 対応済み | `src/repositories`・`src/services`・`src/core` の `__init__.py` のまとめての import をやめた。openpyxl・et_xmlfile・chardet を `requirements-tools.txt` に移した。requests は Streamlit が要るので、本番の間接の依存として残した。新しい venv に `requirements.txt` だけを入れて、4ページが AppTest で起動することを確かめた |
| 4 | 対応済み | Home と Song List の読み込み失敗の表示を、短い案内「時間をおいて、ページを開き直してください。」にそろえた。例外のメッセージとサーバー上のパスは出さない(ログには出る) |
| 5 | 対応済み | Song List の失敗のときに、warning を重ねて出さないようにした |
| 6 | 決定 | 出さない(今のまま)。`docs/specs/data-model.md` 3.3 に書いた |
| 7 | 対応済み | kind に「ゲーム」(ゲーム・運動などの配信)を足し(仕様・`update-data.md`)、6件を `data set` で直した |
| 8 | 対応済み | a0268・a0286・a0314 を `data drop-artist` で消した |
| 9 | 対応済み | `v2_data._load` に `max_entries=1` |
| 10 | 対応済み | パスワードを `hmac.compare_digest` で比べるようにした。`enable_admin_page` の既定を False にした。コードを消すのはフェーズ3 |
| 11 | 対応済み | `from PIL import Image` を消した |
| 12 | 見送り | 任意の対応のため、今回は見送り |
| 13 | 対応済み | 「「…」で検索した結果」で、検索語の Markdown の記号をエスケープする(`home_page.escape_markdown`) |
| 14 | 対応済み | 中身の無い2件は消した。`test_run_song_list_generator_success` は skip を外すと通ったので残した |

確認: `pytest` が `888 passed, 1 skipped`(skip は `--runslow` の性能テストだけ)、`pytest --runslow tests/performance` が `1 passed`、`data validate` が「問題はありません」、`check-rules.sh` が「問題なし」。データの件数は artists が 336 → 333 で、ほかは同じ。

新しく気づいたこと(この記録の対象外): Streamlit 1.66 が `st.components.v1.html`(Information の今週のスケジュールの埋め込みで使う)について「2026-06-01 以降に消す。`st.iframe` に置き換える」と警告を出している。Streamlit の版を上げる前に置き換える。
