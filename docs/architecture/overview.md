# 構成の概要

- 状態: 2026-10-20 時点のコードから書いた
- 関連: [`docs/specs/data-model.md`](../specs/data-model.md)(v2 のデータの正本)、[`docs/prompts/update-data.md`](../prompts/update-data.md)(取り込みの手順)、`CLAUDE.md`(AI 向けの入口)

しのうたタイムは、Streamlit のマルチページのアプリです。データは `data/` の TSV で、DB は使いません。アプリ(画面)は外部の API を使いません。取り込みの CLI だけが YouTube Data API を使います。

以前の構成図・データフロー・エラー処理の文書は、2025年11月時点の v1 の内容で、[`docs/archive/`](../archive/) に移しました。

## 1. v1 と v2

データの仕組みが2つ並んでいます。

| | v1(今の画面が読む) | v2(今後の正本) |
|---|---|---|
| データ | `data/M_YT_LIVE.TSV`(配信)・`M_YT_LIVE_TIMESTAMP.TSV`(歌唱)・`V_SONG_LIST.TSV`(生成物) | `data/v2/` の5つのテーブル(contents・artists・songs・performances・aliases) |
| 作り方 | `data.xlsx` を手で書き、`excel_to_tsv_cli` → `song_list_generator` | YouTube などから取り込み(`ingest`)。直すときは `data` の CLI |
| 読む画面 | Home(`Home.py`)、Song List(`pages/99_Song_List_beta.py`) | 確認用ページ `pages/9x_V2_*_Preview.py`(ローカル専用・Git 管理外) |
| 集計 | `DataPipeline`・`SongListService` | `src/core/views.py`(実行時に計算し、生成物を持たない) |

本番の画面を v2 に切り替えるのは、これからです(フェーズ2)。v1 の文書には【旧フロー】の注記を付けています。

## 2. 層

```
pages/・Home.py           画面の入口(Streamlit のページ)
  └ src/ui/               画面の部品(components/・pages/home_page.py・styles/style.css)
      └ src/services/     業務の処理(v1: DataService・SearchService・SongListService ほか)
      └ src/core/         処理の中心(v1: DataPipeline・utils / v2: views・validation・dataset_ops・text・links)
          └ src/repositories/  ファイルの読み書き(v1: Live・Timestamp・SongList など / v2: TableRepository)
              └ src/models/    データの形(v2 のテーブル定義は schema.py)
src/config/               設定(Config。環境変数 SHINOUTA_*)とログ
src/exceptions/           例外(DataLoadError・DataProcessingError・DataSaveError ほか)
src/ingest/               v2 の取り込み(youtube_api・parser・staging・skips・capture)
src/cli/                  CLI(v2: ingest・data / v1: excel_to_tsv_cli・song_list_generator・artist_sort_cli / twitter_embed_cli)
```

- 上の層が下の層を呼びます。下の層は Streamlit を知りません(`st.*` を使うのは `pages/`・`Home.py`・`src/ui/` だけ)。
- v2 の画面は、ページから `TableRepository` と `views` を直接呼びます(services を通さない)。
- 取り込み(`src/ingest/`)は画面からは使わず、CLI(`src/cli/ingest.py`)からだけ使います。

## 3. データの流れ

### v1(今の Home)

```
data/M_YT_LIVE.TSV ─┐
                    ├ LiveRepository・TimestampRepository(読み込み)
data/M_YT_LIVE_TIMESTAMP.TSV ┘
  → DataService(結合)
  → DataPipeline.execute(): 読み込み → 結合 → 変換(曲目番号・YouTube の時刻つきリンク)→ 並べ替え
  → HomePage(検索・25件ずつの表示)
```

- `Home.py` は設定を読み、`HomePage().run()` を呼ぶだけです。
- 読み込みと処理は `home_page.load_and_process_data()`(`@st.cache_data(ttl=3600)`)にまとまっています。

### v2(確認用ページ)

```
取り込み(CLI):
  YouTube Data API / ブラウザ ─→ data/ingest/cache/(取得結果 JSON。Git 管理外)
    → ingest prepare ─→ data/ingest/staged/(下書き。Git 管理外)
    → 判断(人と Claude。docs/prompts/update-data.md)
    → ingest apply(検査を通ったときだけ)─→ data/v2/*.tsv
  曲の無いコンテンツ ─→ ingest skip ─→ data/ingest/skipped.tsv(Git 管理)

画面:
  data/v2/*.tsv → TableRepository.load() → views.build_performance_view(歌唱の一覧)
                                          → views.build_song_stats(曲ごとの集計)
```

- 書き込みは、必ず CLI(`ingest apply`・`data set` など)を通します。保存の前に `validation.validate_dataset` で検査し、`sort_table` で決まった順に並べます。手で TSV を編集しないのはこのためです。
- 並び順・No. の付け方・メン限を画面に出さない決まりなどは、`data-model.md` の 3.2〜3.3 にあります。

## 4. エラーの扱い

- **読み込みは例外を投げる**: リポジトリは、ファイルが無い・形が違うときに `DataLoadError` を投げます(v2 の `TableRepository.load_table` は、TSV が読めない・必須の列が無い・知らない列があるとき)。保存の失敗は `DataSaveError` です。
- **処理の失敗**: `DataPipeline` の各段は、失敗すると `DataProcessingError(段の名前, …)` を投げます。
- **表示はページで行う**: Home は `HomePage.run()` で例外を受け止め、`st.error` などで表示し、ログにも残します。v2 の確認用ページは、検査の結果をキャッシュ関数から返し、ページの側で `st.error` に出します。
- **CLI**: `ValueError`・`FileNotFoundError`・`YouTubeApiError` を受け止め、「エラー: …」を出して終了コード 1 で終わります。`YouTubeApiError` のメッセージには URL(API キー)を入れません。

## 5. キャッシュ

- 重い読み込みと集計は `@st.cache_data` の関数にまとめます。
- **キャッシュ関数の中で `st.error` などを表示しない**(キャッシュが効くと、2回目から表示されなくなるため)。例外を投げるか、エラーを値として返し、表示はページで行います。`tools/check-rules.sh` が WARN で知らせます。
- v2 は、キャッシュの鍵に `views.cache_key(データのディレクトリ)` を渡します。データファイルと、集計・読み込みのコード(views・schema・table_repository・links・text)の更新日時を鍵にするので、起動したままでも、どちらかが変われば計算し直します。
- v1 の Home は `ttl=3600`(1時間)で計算し直します。

## 6. 画面に出す HTML

- 表は pandas の `to_html(escape=False)` で HTML にして出しています(リンクと CSS のクラスを効かせるため)。
- **データ由来の文字列は、呼び出す側でエスケープしてから渡します**(v2 の確認用ページは `html.escape` を通している)。v1 の Home の表(`src/ui/components` の `render_results_table`)と Song List はまだエスケープしていないので、`check-rules.sh` が WARN を出します。フェーズ2で直す予定です。

## 7. ページ

| ページ | 中身 | データ |
|---|---|---|
| `Home.py` | 歌唱の検索(曲名・アーティスト、配信タイトルも)と一覧 | v1 |
| `pages/01_Information.py` | お知らせ。X の埋め込みはページのコードに直接書いている | — |
| `pages/02_About_Us.py` | サイトの説明 | — |
| `pages/99_Song_List_beta.py` | 曲の一覧(β) | v1(`V_SONG_LIST.TSV`) |
| `pages/9x_V2_*_Preview.py` | v2 の歌唱の一覧・曲の一覧の確認用 | v2(ローカル専用・Git 管理外) |
| `pages/*_Admin.py` | X の埋め込みの管理 | ローカル専用・Git 管理外 |

## 8. 設定と秘密の値

- 画面の設定は `src/config/settings.py` の `Config` で、環境変数 `SHINOUTA_*` で上書きできます(ファイルのパス、表示の件数、キャッシュなど)。
- 取り込みの API キー `YOUTUBE_API_KEY`、職人さんの指定 `SHINOUTA_TRUSTED_COMMENTERS`、管理ページの `ADMIN_PASSWORD` は `.env` に置きます(Git 管理外。`docker-compose.yml` がコンテナに渡す)。
- 公開リポジトリなので、秘密の値・コメント本文・ローカルの絶対パスはコミットしません。`tools/check-rules.sh` で確かめます。

## 9. 既知の課題(2026-10-20 時点)

- `pages/99_Song_List_beta.py` のキャッシュ関数の中で `st.error` を出している。また、削除済みの `get_last_error()` を呼ぶ箇所が残っている。
- v1 の古いテストの一部が失敗する(`tests/` の 21 failed / 11 errors。v2 のテスト `tests/unit/v2` は通る)。
- 内部のクラス名(`st-emotion-cache-*`)に頼る CSS が `style.css` に残っている(Streamlit の版を上げると崩れるおそれ)。

いずれも `tools/check-rules.sh` の WARN か、メモで追っています。フェーズ2(本番の画面を v2 に切り替える)で、まとめて片付ける予定です。
