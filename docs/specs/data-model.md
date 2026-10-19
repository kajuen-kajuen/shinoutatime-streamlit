# データモデル v2 仕様書

- 状態: 下書き
- 作成日: 2026-10-19
- 関連: `docs/prompts/update-data.md`(取り込みの判断の決まり)、`src/models/schema.py`、`src/repositories/table_repository.py`、`src/core/views.py`、`src/ingest/`

## 1. 背景と目的

今のデータ(`data/M_YT_LIVE*.TSV`)は、歌唱1件ごとに曲名とアーティストを文字で持っています。表記の揺れ(「サカナクション」と「サクナクション」、「(1chorus)」付きの曲名など)があるため、曲ごとの歌唱回数を GROUP BY で正しく集計できません。集め方も Excel への手入力で、自動化の試みは表記の揺れで止まりました。

v2 では次のことをします。

- 曲・アーティストをマスタに分け、歌唱はその ID を参照します。こうすることで、集計を GROUP BY で正しく計算できます。
- データは移行せず、取り込みの仕組みで取り直します。
- ライブ配信のほか、動画・ショート・X・Z-aN も扱います。

## 2. 非目的(やらないこと)

- 今の `data/M_YT_LIVE*.TSV` からの移行(比べるための参照には使う)
- 保存の形式を TSV 以外にすること(性能の目安を超えたら見直す。4章)
- 曲の歌詞や音源そのものを保存すること

## 3. 仕様

### 3.1 テーブル

置き場所は `data/v2/` です。どのファイルも UTF-8、タブ区切り、改行は LF、1行目がヘッダーです。値はすべて文字列で、空は空文字です。

```
contents ┐                         artists
         │ 1:N                        │ 1:N
         └─< performances >── N:1 ─ songs ─< aliases
```

| ファイル | 1行が表すもの | キー |
|---|---|---|
| `contents.tsv` | 歌が含まれるコンテンツ(ライブ配信・動画・ショート・X の投稿・Z-aN のライブ) | 主キー `content_id` |
| `artists.tsv` | アーティスト | 主キー `artist_id` |
| `songs.tsv` | 曲 | 主キー `song_id`、外部キー `artist_id` |
| `performances.tsv` | 歌唱(集計の元) | 主キー (`content_id`, `seq`)、外部キー `content_id`・`song_id` |
| `aliases.tsv` | 表記の揺れの辞書(取り込み用) | 主キー (`raw_title`, `raw_artist`)、外部キー `song_id` |

**contents**

| 列 | 必須 | 値 |
|---|---|---|
| `content_id` | ○ | `<接頭辞>:<そのプラットフォームでの ID>`。接頭辞は youtube=`yt`、x=`x`、zan=`zan`。例: `yt:rPoEadXC5ck`、`zan:10889` |
| `platform` | ○ | `youtube` / `x` / `zan`(増やすときは `schema.py` と `links.py` に足す) |
| `type` | ○ | `live` / `video` / `short` / `post` |
| `url` | ○ | 元のコンテンツの URL。YouTube は `https://www.youtube.com/watch?v=<ID>`(共有用の `si` は付けない)。ショートは `https://www.youtube.com/shorts/<ID>` |
| `channel` | | 本人以外のチャンネルへの出演のときだけ、そのチャンネル名 |
| `date` | ○ | `YYYY-MM-DD`(日本時間)。ライブは開始日、それ以外は公開日 |
| `start_time` | | `HH:MM`(日本時間)。同じ日の並び順に使う |
| `title` | ○ | コンテンツのタイトル |
| `kind` | | 細かい種類。歌枠 / 縦型歌枠 / 雑談 / コラボ / イベント / 歌ってみた / オリジナルMV / 歌ショート / 切り抜き など |
| `default_style` | | そのコンテンツの基本の演奏の形。`音源` / `弾き語り` / `アカペラ`。空は不明 |
| `access` | | `public` / `members`(メンバー限定)/ `paid`(有料チケット)。空は public |
| `available_until` | | アーカイブの公開期限 `YYYY-MM-DD`(Z-aN の有料ライブなど) |

**artists**: `artist_id`(○、`a0001` 形式。連番で、消しても再利用しない)、`name`(○、表示名)、`sort_name`(読み)。

**songs**: `song_id`(○、`s0001` 形式)、`title`(○)、`sort_title`(曲名の読み)、`artist_id`(○)、`feat`(歌い手)、`kind`(`カバー` / `オリジナル` / `即興`)、`work`(作品・タイアップ。例: アニメ「〇〇」ED。後からの CM 起用なども含め、気づいたときに足す。複数は「、」で区切る)、`year`(4桁。曲の発売・投稿の年)。

- **feat. の扱い**: 「メル feat.IA」のような曲は、アーティストを作り手(メル)にまとめ、歌い手(IA)を `feat` に持つ。
  - 画面では「作り手 feat.歌い手」と組み立てて表示する(`views.display_artist`)。
  - アーティスト別の集計は、作り手でまとめて数える。
  - 下書きの段階で、`feat.`・`ft.`・`featuring` を自動で分ける(`parser.split_feat`)。
- **後から足した任意の列**(`feat` など)は、古いファイルに無くても空として読み、次の保存で列が加わる。必須の列とキーの列が無いときはエラーにする。

**performances**

| 列 | 必須 | 値 |
|---|---|---|
| `content_id` | ○ | |
| `seq` | ○ | コンテンツの中の曲順。**10 刻み**(10, 20, 30…)で振り、間に足せるようにする。画面の No. は順位から計算する |
| `start` | | 開始時刻 `H:MM:SS`。時刻を指定できないもの(Z-aN など)は空 |
| `song_id` | ○ | |
| `style` | | **基本(`default_style`)と違うときだけ**書く演奏の形。1つの配信で音源と弾き語りが混ざるときに使う |
| `part` | | 尺。空はフル。`1chorus` / `1phrase` / `short` / `1番のみ` |
| `note` | | リクエスト・役名など、自由に書く |

**aliases**: `raw_title`(○)、`raw_artist`、`song_id`(○)。取り込みのとき、職人さんの書いた表記と曲を結び付ける。

### 3.2 並び順

**ファイルの中**: 保存するたびに `TableRepository` が並べ直します。新しいものは、たいてい末尾に入ります。

| ファイル | 並び |
|---|---|
| contents | `date` → `start_time`(空は先)→ `content_id` |
| performances | contents の並び → `seq` |
| artists・songs | ID の数字の順 |
| aliases | `song_id` → `raw_title` → `raw_artist` |

**画面の初期の並び**: 利用者は、列見出しで並べ替えられます。

| 画面 | 並び |
|---|---|
| 歌唱の一覧(Home) | `date` の新しい順 → 同じ日の中は時刻の早い順(No. の枝番の順。今の Home と同じ)→ コンテンツの中は `seq` 順 |
| 曲の一覧(Song List) | アーティストの読み → 曲の読み |

**読みの並べ方**(`src/core/text.py` の `reading_sort_key`):
- カタカナはひらがなに、全角英数は半角にそろえる。大文字小文字は区別しない。
- 順は「記号・数字 → 英字 → かな → その他」。
- 読みが空なら表示名で並べる。

### 3.3 集計(`src/core/views.py`)

集計は実行時に計算し、生成物のファイルは持ちません。

- **歌唱の一覧**(`build_performance_view`):
  - 結合: performances に contents・songs・artists を結合する。
  - No.: コンテンツの中の順位。同じ日に複数の**ライブ配信**があるときは、`start_time` の早い順の枝番を付けて「枝番-順位」にする。**1曲だけのショート・動画・投稿の No. は空欄**(種類の列で見分けられる)。複数の曲が入ったもの(例: ボカロファンテスト)は曲順(1, 2, 3…)を付ける。ショート・動画には枝番を付けない(同じ日にあっても、ライブ配信の No. を変えない)。同じ日の中の並びは、種類を問わず時刻の早い順で、コンテンツの中は曲順。
  - 演奏の形: `style` があればそれ、無ければ `default_style`。
  - 種類(`type_label`): `type` の日本語表示(配信 / ショート / 動画 / 投稿。`views.CONTENT_TYPE_LABELS`)。画面では「配信日 / No. / 曲名 / アーティスト / 種類 / リンク」の順に並べる(Home だけ。Song List には出さない)。
  - リンク: `build_link(platform, url, start)` で組み立てる。YouTube は `t=秒`(0秒からのときは付けない)。X・Z-aN は url のまま。
  - 検索用の列: 曲名・アーティスト・タイトルを `normalize_for_match` でならし、改行で区切ってつないだもの。検索語も同じようにならしてから照合する。
- **曲ごとの集計**(`build_song_stats`、GROUP BY song_id): 次の値を出す。
  - 歌唱回数(`count`)・初歌唱日・最終歌唱日・最新の歌唱へのリンク
  - ライブでの回数・歌ってみた動画の有無・ショートの有無
  - 弾き語りの回数
  - **`kind=切り抜き` のコンテンツは数えない**(元の配信と二重になるため)。
- **メンバー限定(`access=members`)のコンテンツは画面に出さない**: データには登録するが、歌唱の一覧にも曲ごとの集計にも入れない。同じ日の枝番にも数えない(`views.HIDDEN_ACCESS`)。

### 3.4 後から足す・直すとき

| ケース | 扱い |
|---|---|
| 過去のコンテンツを足す | 日付の位置に入る。ほかの行の ID は変わらない |
| セットリストの途中に曲を足す | 間の `seq` を使う(20 と 30 の間なら 25)。詰まったら `data renumber <content_id>` |
| 同じ曲・アーティストが2つあった | `data merge-song <残す> <消す>` / `data merge-artist`。消した ID は再利用しない。元の表記は aliases に残る |
| 値の修正 | `data set <テーブル> <主キー> <列> <値>` で直す(例: `data set songs s0001 work "…"`。主キーが複数の列なら `yt:xxx,20` のようにカンマで区切る)。キーは変わらない。主キーの列は直せない |

### 3.5 取り込み(`src/ingest/`、`python -m src.cli.ingest`)

```
1. 取得   取得結果 JSON を data/ingest/cache/ に保存する(Git 管理外)
          ブラウザ(Claude が操作)/ YouTube Data API(from-api)/ yt-dlp の JSON(from-ytdlp)
2. 下書き prepare: 職人さんのコメントを選び、時刻の行を「曲名/アーティスト/作品/年」に分け、
          aliases・songs と照合する → data/ingest/staged/(Git 管理外)
3. 判断   Claude が下書きを確かめて直す(docs/prompts/update-data.md)
4. 追記   apply: 検査を通してから data/v2/ に追記する(--dry-run あり)
```

**取得結果 JSON**(`src/ingest/capture.py` の `Capture`):

| 項目 | 内容 |
|---|---|
| 識別 | `content_id`・`platform`・`type`・`url`・`title` |
| 日時 | `published_at`(ISO 8601、日本時間) |
| 取得の情報 | `captured_by`(browser / api / ytdlp / manual)・`captured_at` |
| 任意 | `description`・`channel`・`duration_seconds`・`comments`(`text`・`author`・`likes`) |

- 投稿者名はキャッシュの中でだけ使い、`data/v2/` には入れません。

**YouTube の取得**(`ingest list` / `fetch --month YYYY-MM` / `from-api`):
- チャンネル(`@Shino_Kasukane`)のアップロードの一覧から、月ごとにまとめて取得する。取得済みのものは飛ばす(`--force` で取り直す)。
- 種類の判定:
  - ライブのアーカイブは `live`。
  - それ以外は `https://www.youtube.com/shorts/<ID>` がリダイレクトされなければ `short`、されれば `video`。
- **動画・ショートの下書き**: セットリストらしいコメント(見出しがある、または曲名とアーティストに分けられる行がある)が無ければ、**タイトルから1行**を作る(`start=0:00:00`)。
  - 「【アカペラ】曲名/アーティスト …」の形から曲を、【アカペラ】【弾き語り】【歌ってみた】の印から演奏の形(アカペラ / 弾き語り / 音源)の候補を取る。
  - 「0:20 の歌い方が好き」のような感想は、セットリストとして選ばない。

**本人のチャンネル以外**: 本人が出演したコンテンツ(コラボ相手のチャンネルの配信、公式チャンネルの動画)は対象にし、`channel` にチャンネル名を入れる。**ファンが作った動画(切り抜き・ファンの歌ってみたなど)は対象外**で、登録も記録もしない。

**曲の無いコンテンツ**: ティザーや曲の無い雑談の配信は `data/v2/` に入れず、`ingest skip <content_id> "<理由>"` で `data/ingest/skipped.tsv`(Git で管理。`content_id`・`reason`・`date` だけ)に記録する。X の投稿で YouTube と同じ動画も、二重に数えないよう登録せずにここへ記録する。`ingest status` は「登録済み / 曲なし / 下書きあり / 未処理」を表示する。
- 職人さんのコメントは、時刻の行が最も多いコメントを候補にします。環境変数 `SHINOUTA_TRUSTED_COMMENTERS`(投稿者名のカンマ区切り)で決め打ちにできます。

### 3.6 エッジケース

- **時刻が無い歌唱**(Z-aN など): `start` は空にし、`seq` だけで順を持ちます。
- **時刻の書式**: `MM:SS`・`HH:MM:SS` は `H:MM:SS` にそろえます。時刻があるときは、`seq` の順と時刻の順が合っていなければなりません(検査で確かめる)。
- **曲名の注記**: 曲名の末尾の `(1chorus)` などは `part` に、先頭か末尾の `(リクエスト)` などは `note` に移します。
- **アーティストの無い行**: 下書きに印を付け、判断で埋めるか除外します。
- **同じコンテンツの取り直し**: `apply --replace` で置き換えます(曲・アーティスト・aliases は残る)。

## 4. 実装メモ

- **主なファイル**:
  - スキーマ: `src/models/schema.py`
  - 読み書き: `src/repositories/table_repository.py`
  - 検査: `src/core/validation.py`
  - 操作: `src/core/dataset_ops.py`
  - 集計: `src/core/views.py`
  - 文字列と読み: `src/core/text.py`
  - リンク: `src/core/links.py`
  - CLI: `src/cli/data.py`・`src/cli/ingest.py`
- **性能**: 架空の 2万件(今のペースで約12年分)で、読み込みから集計までを約0.5秒で終えることを `tests/performance/` で確かめています(`--runslow`)。
  - 集計で `lambda` を使ったり、Arrow の文字列のまま min・max を取ったりすると、グループごとに遅くなります(2万件で約6秒だった)。NumPy の列にしてから集計します。
  - 保存の形式を見直す目安: 歌唱が数十万件を超えるか、読み込みが1秒を超えたとき(Parquet や DuckDB を検討する)。
- **公開リポジトリ**: API キー・職人さんの指定・コメント本文はコミットしません。`check-rules.sh` で検出します。

## 5. テストと検証

- **自動テスト**: `tests/unit/v2/`(文字列とリンク、読み書きと検査、操作と集計、取り込み)、`tests/performance/`(slow)。
- **コマンドでの確認**: `python -m src.cli.data validate`、`python -m src.cli.data show`。

## 6. 未決事項

- 切り抜きのショートを、歌唱回数に数えるか(今は数えない)
- Z-aN の複数タレントのライブで、どこまで登録するか。ユニット曲の扱い
- `kind`・`style` の言葉の一覧

## 7. 変更履歴

| 日付 | 変更内容 |
|---|---|
| 2026-10-19 | 初版(下書き) |
| 2026-10-19 | 歌唱の一覧で、同じ日の複数のコンテンツは時刻の早い順に並べると決めた(今の Home と同じ)。検索の対象に読み(sort_title・sort_name)を加えた |
| 2026-10-19 | songs に feat(歌い手)を足し、feat. 付きのアーティストは作り手にまとめると決めた。任意の列が無い古いファイルも読めるようにした |
| 2026-10-19 | work には後からの CM 起用なども含め、気づいたときに足すと決めた。値の修正コマンド `data set` を足した |
| 2026-10-19 | 月ごとの取得(list・fetch)、種類の自動判定、動画・ショートのタイトルからの下書き、曲の無いコンテンツの記録(skipped.tsv)を足した。同じ日の枝番はライブ配信どうしだけにした。0秒からのリンクには t を付けない |
| 2026-10-20 | 歌唱の一覧に「種類」(type の日本語表示)を足した。位置はリンクの左。Home だけ。1曲だけのショート・動画・投稿の No. は空欄にした(複数曲なら曲順)。画面のキャッシュの鍵にコードの更新日時も入れた(`views.cache_key`) |
| 2026-10-20 | 本人のチャンネル以外は、本人が出演したものだけを対象にし、ファンが作った動画は対象外と決めた |
| 2026-10-20 | メンバー限定の配信(`access=members`)は、データには登録するが画面には出さないと決めた |
