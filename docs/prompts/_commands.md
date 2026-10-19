# コマンド集(しのうたタイム)

**変えずにそのまま打つ**。リポジトリのルートで、Git Bash から打つ。Docker Desktop を起動しておく。

| 用途 | コマンド | 注意 |
|---|---|---|
| コンテナの起動 | `docker compose up -d` | 起動後 http://localhost:8501 でアプリを確認できる。コードはマウントされているので、保存すると Streamlit が再読み込みする |
| 起動の確認 | `docker compose ps` | `shinouta-time` が `running` |
| コードの変更を確実に反映 | `docker compose restart shinouta-time` | `src/` の変更が画面に反映されないことがある(起動中のアプリが古いモジュールを読み込んだまま。WSL のファイル監視のため)。`src/` を直して画面で確かめるときは再起動する |
| アプリのログ | `docker compose logs --tail=100 shinouta-time` | 例外のスタックトレースはここに出る |
| テスト(全部) | `docker compose exec shinouta-time pytest` | 作業の終わりに必ず。e2e は `data/` の本物の TSV を読む |
| テスト(一部) | `docker compose exec shinouta-time pytest tests/unit -q` | `tests/unit` を `tests/property`・`tests/integration`・`tests/e2e` やファイル名に替えてよい |
| カバレッジ | `docker compose exec shinouta-time pytest --cov=src --cov-report=term-missing` | |
| 絶対制約の確認 | `sh tools/check-rules.sh` | ホストで打つ(コンテナに git が無い)。NG が 0 になるまで直す |
| データ件数の確認 | `wc -l data/M_YT_LIVE.TSV data/M_YT_LIVE_TIMESTAMP.TSV data/V_SONG_LIST.TSV` | 1 行目はヘッダー。データを触る前後で比べる |
| 本番のデータ件数 | `git show origin/main:data/M_YT_LIVE.TSV \| wc -l` | ファイル名を替えて比べる。先に `git fetch origin` が要ることがある |
| 楽曲一覧の生成(確認だけ) | `docker compose exec shinouta-time python -m src.cli.song_list_generator --dry-run --verbose` | ファイルを書かない。件数と警告を見る |
| 楽曲一覧の生成 | `docker compose exec shinouta-time python -m src.cli.song_list_generator` | `V_SONG_LIST.TSV` を上書きする。**打つ前にユーザーへ確認** |
| Excel から TSV(確認だけ) | `docker compose exec shinouta-time python -m src.cli.excel_to_tsv_cli --dry-run` | ファイルを書かない |
| Excel から TSV | `docker compose exec shinouta-time python -m src.cli.excel_to_tsv_cli` | `M_YT_LIVE*.TSV` と `V_SONG_LIST.TSV` を上書きする。**打つ前にユーザーへ確認** |
| アーティストの読みの一覧 | `docker compose exec shinouta-time python -m src.cli.artist_sort_cli list` | 追加・削除(`add`・`delete`)は `ARTIST_SORT_MAPPING.TSV` を書き換えるので確認してから |
| データ v2 の検査 | `docker compose exec shinouta-time python -m src.cli.data validate` | `data/v2/` の主キー・外部キー・値の形・並び順 |
| データ v2 の表示 | `docker compose exec shinouta-time python -m src.cli.data show` | 歌唱の一覧と曲ごとの集計 |
| データ v2 の値の修正 | `docker compose exec shinouta-time python -m src.cli.data set <テーブル> <主キー> <列> <値>` | 検査を通ったときだけ保存する。TSV を手で編集しない |
| 投稿の一覧(読むだけ) | `docker compose exec shinouta-time python -m src.cli.ingest list --month 2025-04` | YouTube Data API(`.env` の `YOUTUBE_API_KEY`) |
| 月ごとの取得 | `docker compose exec shinouta-time python -m src.cli.ingest fetch --month 2025-04` | 取得済みは飛ばす。`--force` で取り直す |
| 曲なしの記録 | `docker compose exec shinouta-time python -m src.cli.ingest skip <content_id> "<理由>"` | `data/ingest/skipped.tsv` に記録する。ユーザーに確かめてから |
| 取り込みの状況 | `docker compose exec shinouta-time python -m src.cli.ingest status --month 2025-04` | 登録済み / 曲なし / 下書きあり / 未処理 |
| 取り込み(下書き → 追記) | `docker compose exec shinouta-time python -m src.cli.ingest prepare <content_id>` → 判断 → `… ingest apply <content_id> --dry-run` → `… ingest apply <content_id>` | 手順と判断の決まりは `docs/prompts/update-data.md` |
| コンテナの停止 | `docker compose down` | |
| 差分の確認 | `git status --short` / `git diff --stat` | コミットはユーザーの指示があったときだけ |

## 打ってはいけないコマンド

| コマンド | 理由 |
|---|---|
| `git push`(どのブランチも) | ユーザーの指示があるまで行わない。公開リポジトリなので push した時点で公開される(`settings.json` で deny) |
| `git checkout main` / `git checkout develop` / `git merge` / `git rebase` | `main`・`develop` は本番・stg に直結する。統合はユーザーが行う(`settings.json` で deny) |
| `git add .` / `git add -A` | 意図しないファイル(作業中の別の変更、ログなど)が入る。ファイルを名指しで add する |
| ホストでの `pip install` / `pytest` / `streamlit run` | 環境が本番(コンテナ)とずれる。コンテナの中で打つ |
| 生成ツールの `--dry-run` なしの実行 | `data/` の TSV を上書きする。件数を確かめ、ユーザーの承認を得てから |
