# 構成の概要

- 状態: 2026-10-21 時点のコードから書いた(本番の画面を v2 に切り替えた時点)
- 関連: [`docs/specs/data-model.md`](../specs/data-model.md)(v2 のデータの正本)、[`docs/prompts/update-data.md`](../prompts/update-data.md)(取り込みの手順)、`CLAUDE.md`(AI 向けの入口)

しのうたタイムは、Streamlit のマルチページのアプリです。データは `data/` の TSV で、DB は使いません。アプリ(画面)は外部の API を使いません。取り込みの CLI だけが YouTube Data API を使います。

以前の構成図・データフロー・エラー処理の文書は、2025年11月時点の v1 の内容で、[`docs/archive/`](../archive/) に移しました。

## 1. v1 と v2

データの仕組みが2つ並んでいます。画面が読むのは v2 です。

| | v1(参照用。フェーズ3で消す) | v2(正本。画面が読む) |
|---|---|---|
| データ | `data/M_YT_LIVE.TSV`(配信)・`M_YT_LIVE_TIMESTAMP.TSV`(歌唱)・`V_SONG_LIST.TSV`(生成物) | `data/v2/` の5つのテーブル(contents・artists・songs・performances・aliases) |
| 作り方 | `data.xlsx` を手で書き、`excel_to_tsv_cli` → `song_list_generator` | YouTube などから取り込み(`ingest`)。直すときは `data` の CLI |
| 読む画面 | なし(2026-10-21 のフェーズ2で、画面は v2 に切り替えた) | Home(`Home.py`)、Song List(`pages/99_Song_List_beta.py`) |
| 集計 | `DataPipeline`・`SongListService` | `src/core/views.py`(実行時に計算し、生成物を持たない) |

v1 のデータ・ツール・テストは、比べるための参照として残しています(フェーズ3で消す)。v1 の文書には【旧フロー】の注記を付けています。

## 2. 層

```
pages/・Home.py           画面の入口(Streamlit のページ)
  └ src/ui/               画面の部品(page_setup.py・components/・pages/home_page.py・v2_data.py・styles/style.css)
      └ src/core/         処理の中心(v2: views・validation・dataset_ops・text・links / v1: DataPipeline・utils)
          └ src/repositories/  ファイルの読み書き(v2: TableRepository / v1: Live・Timestamp・SongList など)
              └ src/models/    データの形(v2 のテーブル定義は schema.py)
      └ src/services/     v1 の業務の処理(DataService・SearchService・SongListService ほか。画面からは使わない)
src/config/               設定(Config。環境変数 SHINOUTA_*)とログ
src/exceptions/           例外(DataLoadError・DataProcessingError・DataSaveError ほか)
src/ingest/               v2 の取り込み(youtube_api・parser・staging・skips・capture)
src/cli/                  CLI(v2: ingest・data / v1: excel_to_tsv_cli・song_list_generator・artist_sort_cli / twitter_embed_cli)
```

- 上の層が下の層を呼びます。下の層は Streamlit を知りません(`st.*` を使うのは `pages/`・`Home.py`・`src/ui/` だけ)。
- 画面は `src/ui/v2_data.py` を通して、`TableRepository` と `views` を直接呼びます(services を通さない)。
- 取り込み(`src/ingest/`)は画面からは使わず、CLI(`src/cli/ingest.py`)からだけ使います。

## 3. データの流れ

```
取り込み(CLI):
  YouTube Data API / ブラウザ ─→ data/ingest/cache/(取得結果 JSON。Git 管理外)
    → ingest prepare ─→ data/ingest/staged/(下書き。Git 管理外)
    → 判断(人と Claude。docs/prompts/update-data.md)
    → ingest apply(検査を通ったときだけ)─→ data/v2/*.tsv
  曲の無いコンテンツ ─→ ingest skip ─→ data/ingest/skipped.tsv(Git 管理)

画面:
  data/v2/*.tsv → TableRepository.load() → views.build_performance_view(歌唱の一覧)─→ Home(検索・25件ずつ)
                                          → views.build_song_stats(曲ごとの集計)  ─→ Song List(25件ずつ)
  (src/ui/v2_data.py の load_performance_view・load_song_stats。キャッシュ付き)
```

- どのページも最初に `src/ui/page_setup.py` の `setup_page()` を呼びます(ページ設定・共通の `style.css`・見出し「しのうたタイム👻🫧」と、Home 以外は絵文字付きのページ名)。CSS をページの中に書かず、`style.css` だけを直します。
- `Home.py` は `setup_page()` のあと、返ってきた設定を渡して `HomePage(config).run()` を呼ぶだけです(設定の読み込みは1回)。検索欄は `st.form` で、Enter キーでも送信されます。検索は `home_page.filter_view`(検索語を `normalize_for_match` してから、一覧の検索用の列に部分一致)。検索欄の上に、データの時点(`home_page.data_as_of`。「データは YYYY/MM/DD の配信まで(歌唱 N 件)」)を出します。
- 書き込みは、必ず CLI(`ingest apply`・`data set` など)を通します。保存の前に `validation.validate_dataset` で検査し、`sort_table` で決まった順に並べます。手で TSV を編集しないのはこのためです。
- 並び順・No. の付け方・メン限を画面に出さない決まりなどは、`data-model.md` の 3.2〜3.3 にあります。

## 4. エラーの扱い

- **読み込みは例外を投げる**: リポジトリは、ファイルが無い・形が違うときに `DataLoadError` を投げます(v2 の `TableRepository.load_table` は、TSV が読めない・必須の列が無い・知らない列があるとき。`v2_data` はデータのディレクトリが無いとき)。保存の失敗は `DataSaveError` です。
- **表示はページで行う**: Home は `HomePage.run()`、Song List はページの中で例外を受け止め、`st.error` などで表示し、ログにも残します。
- **データの検査の error**: 画面の読み込み(`v2_data`)ではログにだけ書き、公開の画面には出しません(データは取り込みのときに検査している)。
- **CLI**: `ValueError`・`FileNotFoundError`・`YouTubeApiError` を受け止め、「エラー: …」を出して終了コード 1 で終わります。`YouTubeApiError` のメッセージには URL(API キー)を入れません。

## 5. キャッシュ

- 重い読み込みと集計は `@st.cache_data` の関数にまとめます(`src/ui/v2_data.py` の `_load`)。
- **キャッシュ関数の中で `st.error` などを表示しない**(キャッシュが効くと、2回目から表示されなくなるため)。例外を投げ、表示はページで行います。`tools/check-rules.sh` が NG で知らせます。
- キャッシュの鍵に `views.cache_key(データのディレクトリ)` を渡します。データファイルと、集計・読み込みのコード(views・schema・table_repository・links・text)の更新日時を鍵にするので、起動したままでも、どちらかが変われば計算し直します。

## 6. 画面に出す HTML

- 表は HTML で組み立てて出しています(リンクと CSS のクラスを効かせるため。`st.dataframe` は使わない)。
- Home の表は `src/ui/components` の `render_results_table` がセルと見出しをエスケープします。リンクやアーティストのように呼び出す側で HTML に組み立てる列だけ `html_columns` で渡し、その中のデータ由来の文字列は呼び出す側で `html.escape` します。Song List はページの `build_table_html` でエスケープします。
- `to_html(escape=False)` は使いません(`tools/check-rules.sh` が NG で知らせる)。

## 7. ページ

| ページ | 中身 | データ |
|---|---|---|
| `Home.py` | 歌唱の検索(曲名・アーティスト・読み、配信タイトルも)と一覧 | v2(歌唱の一覧) |
| `pages/01_Information.py` | 予定表置き場(本人のフリーチャットの枠)、今週のスケジュール(X の投稿の埋め込み。`data/tweet_*`)、お知らせ・活動の記録の案内(非公式 Wiki・X・公式サイトへのリンク) | — |
| `pages/02_About_Us.py` | サイトの説明 | — |
| `pages/99_Song_List_beta.py` | 曲の一覧(β。アーティストの読み → 曲名の読みの順) | v2(曲ごとの集計) |

`pages/*_Admin.py`・`pages/*_Preview.py` はローカル専用で Git 管理外です(今は置いていない)。

## 8. 設定と秘密の値

- 画面の設定は `src/config/settings.py` の `Config` で、環境変数 `SHINOUTA_*` で上書きできます(v2 のデータのディレクトリ `SHINOUTA_V2_DATA_DIR`、表示の件数など)。
- 取り込みの API キー `YOUTUBE_API_KEY`(複数のキーは `YOUTUBE_API_KEYS`。上限に達したら次のキーへ切り替える)、職人さんの指定 `SHINOUTA_TRUSTED_COMMENTERS` は `.env` に置きます(Git 管理外。`docker-compose.yml` がコンテナに渡す)。`ADMIN_PASSWORD` は X の埋め込みの管理画面のためのもので、今は使うページがありません。
- 公開リポジトリなので、秘密の値・コメント本文・ローカルの絶対パスはコミットしません。`tools/check-rules.sh` で確かめます。

## 9. 既知の課題(2026-10-21 時点)

- v1 のコード・データ・テスト・CLI が残っている(画面からは使わない)。`src/repositories/__init__.py` が `ExcelRepository`(openpyxl)を、`src/services/__init__.py` が `TwitterEmbedService`(requests)をまとめて import するので、openpyxl・requests を本番の requirements から外せない。フェーズ3で片付ける。
- X の埋め込みの管理画面(`src/ui/twitter_embed_admin.py`)は、ページを消してあり、どこからも使っていない。フェーズ3で片付けるか決める。取得の部品(`src/cli/twitter_embed_cli.py`・`src/services/twitter_embed_service.py`・`src/clients/twitter_api_client.py`)と `data/tweet_*` は、Information の今週のスケジュールで使う(2026-10-22 から。毎週の更新は `docs/prompts/update-data.md`)。
- `style.css` の `.block-container` は Streamlit の内部のクラス名に頼っている(data-testid の指定に置き換えるかは未定)。
