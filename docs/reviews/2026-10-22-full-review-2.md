# 全体 レビュー記録(2回目)

- 日付: 2026-10-22
- 種別: コードレビュー / データ確認
- 対象: 全体(`63ab27a` 時点)。前回の記録([`2026-10-22-full-review.md`](2026-10-22-full-review.md)、`ec92209` 時点)の後の `ec92209..63ab27a`(前回の指摘への対応と、2026-03-05 の配信の登録)。関連する仕様書は `docs/specs/data-model.md`
- レビューした人: 別のエージェント(モデル名は【要確認】)。指摘は Claude(Opus 5.5)がリポジトリで確かめ、影響の説明を直した

## 1. 範囲と観点

見たもの:
- 画面: `Home.py`・`src/ui/pages/home_page.py`・`pages/`(Information・About Us・Song List beta)・`src/ui/components/`・`src/ui/v2_data.py`
- v2 のデータの層: `src/models/schema.py`・`src/core/views.py`・`validation.py`・`dataset_ops.py`・`links.py`・`text.py`
- 取り込み: `src/cli/ingest.py`。X の埋め込み: `src/cli/twitter_embed_cli.py`・`src/ui/twitter_embed_admin.py`
- 公開と運用: `tools/check-rules.sh`・`.github/workflows/wake_up_streamlit.yml`・`requirements.txt`
- データ: `data/v2/*.tsv`(件数・検査・直近のコミット 99f674f で足した行)

観点: 公開リポジトリとしての安全、データの正しさ、障害時の振る舞い、表示の安全と使いやすさ、保守性(`docs/prompts/review.md` の順)。

見なかったこと:
- v1(フェーズ3で消す前提)、`src/ingest/` の解析の細部
- スマホの幅での表示、本番・stg の画面(ブラウザで見ていない)

## 2. 指摘事項

重要度「高」の指摘はなかった。

| # | 重要度 | 場所 | 内容 | 対応 | 状態 |
|---|---|---|---|---|---|
| 1 | 中 | `data/v2/performances.tsv`(`yt:wFnIyA1459M`) | 2026-03-05 の深夜定期の弾き語りの 11 曲のうち 8 曲(seq 20〜40・60〜100)の `start` が空。リンクが動画の先頭に飛ぶ。登録のコミット 99f674f に「時刻は3曲だけ。残りは後で入れる」とあり、分かっていて残したもの | 配信のアーカイブで時刻を確かめてから `data set performances yt:wFnIyA1459M,<seq> start <H:MM:SS>` で入れる | 未対応 |
| 2 | 低 | `data/v2/songs.tsv` の s0790(8.32) | `sort_title` が空。ほかの数字で始まる曲(1999・366日・3月9日など 8 曲)には読みがある。平仮名の読みで検索しても出ない。(元の指摘は「Song List で は行に並ばない」としていたが、Song List はアーティストの読み → 曲の読みの順で並べるので、並びへの影響は同じアーティストの中だけ。*Luna の曲の中では今も先頭のまま) | `data set songs s0790 sort_title はちてんさんに`(読みは【要確認】。公式の表記は見つからなかった。RAG Music の「は」から始まるボカロ曲のまとめには入っている)。データなのでブランチ `update-data` で直した | 対応済み |
| 3 | 低 | `src/ui/components/__init__.py` の `EMBED_AUTO_HEIGHT_SCRIPT` | X の埋め込みの高さを合わせるのに、Streamlit の DOM(`data-testid="stElementContainer"`)の flex と height を上書きしている。Streamlit の更新で属性が変わると伸び縮みが効かなくなる(そのときは渡した高さのまま、スクロールで見られる) | Streamlit の版を上げ、`st.components.v1.html` を `st.iframe` に置き換えるときに、合わせて見直す | 見送り |
| 4 | 低 | `src/cli/twitter_embed_cli.py` のヘルプ(epilog) | 案内先の `docs/twitter-embed-automation.md` が無い(`docs/archive/specs/twitter-embed-automation/` に移した) | 案内先を `docs/archive/specs/twitter-embed-automation/` に直した | 対応済み |
| 5 | 低 | `.github/workflows/wake_up_streamlit.yml` | actions をタグ(`@v7`)で指定していて、SHA で固定していない。前回の #12 と同じ | 前回と同じく、任意の対応のため見送り | 見送り |
| 6 | 低 | 作業のブランチ | レビューの時点で `develop` の上にいた(`check-rules.sh` が WARN)。push・コミットはしていない | 対応は作業ブランチ(`update-data`・`fix/review-2-followup`)で行った | 対応済み |
| 7 | 低 | `src/cli/__init__.py` | package の `__init__` が `twitter_embed_cli` を import している。`python -m src.cli.twitter_embed_cli` で RuntimeWarning が出て、`python -m src.cli.data` などでも `twitter_embed_cli` まで読み込む。CLAUDE.md の「`__init__.py` でまとめて import しない」に合わない(Claude が確かめるときに気づいた) | `__init__.py` の import を消す(`main` を package から使っている所が無いか確かめてから) | 未対応 |

重要度の目安: **高**=秘密・個人情報の漏えい、データの欠落・誤表示、ページが落ちる、**中**=特定の条件で誤動作する・スマホで使いにくい、**低**=見た目・読みやすさ・将来の課題。

## 3. 確認の結果

2026-10-22、ローカルの Docker のコンテナ(`python:3.14.8-slim-trixie`)で確認した。

絶対制約のチェックリスト:

| # | 制約 | 結果 | 根拠 |
|---|---|---|---|
| 1 | main・develop に触れない | WARN(レビューの時点) | `develop` の上にいた(push・コミットなし)。対応は作業ブランチで行い、`check-rules.sh` は OK |
| 2 | 秘密・個人情報をコミットしない | OK | check-rules の「公開リポジトリ」の項目がすべて OK |
| 3 | データを確認なしで書き換えない | OK | `data` の書き込みは検査を通ったときだけ保存する。`ingest apply` に `--dry-run` と曲なしの記録の確認がある |
| 4 | エスケープしない HTML を足さない | OK | `escape=False` なし。検索語の Markdown の記号もエスケープしている(`escape_markdown`) |
| 5 | キャッシュ関数の中で表示しない | OK | check-rules で OK。`v2_data._load` は例外を投げ、ページ側で案内を出す |

レビューの時点(`63ab27a`):
- テスト(`docker compose exec shinouta-time pytest -q`): `888 passed, 1 skipped in 98.36s`(skip は `--runslow` の性能テストだけ)
- データの検査(`python -m src.cli.data validate`): 「問題はありません」
- `data/v2/` の件数(ヘッダーを除く): contents 394・artists 333・songs 788・performances 2329・aliases 859。`data/ingest/skipped.tsv` 332

対応のあと:
- `fix/review-2-followup`: `pytest -q` が `888 passed, 1 skipped in 95.43s`。`python -m src.cli.twitter_embed_cli --help` の最後が「docs/archive/specs/twitter-embed-automation/ を参照してください」
- `update-data`: `data validate` が「問題はありません」。差分は `songs.tsv` の1行だけ。`build_song_stats` の `search` に「はちてんさんに」が入り、検索で s0790 が出ることを確かめた
- `check-rules.sh` は両方のブランチで「問題なし」

## 4. 良かった点

- 前回の 14 件のうち 13 件が対応済みで、記録の「6. 追記」に対応と確認の結果がそろっている
- 時刻の無い歌唱を、コミットのメッセージに「残りは後で入れる」と書いて残していて、後から経緯を追える

## 5. 結論

そのまま採用(本番はこのままで問題なく動く)。残った課題: #1 の時刻(配信のアーカイブで確かめてから入れる)、#7 の `src/cli/__init__.py`、#3 は Streamlit の版を上げるとき。

## 6. 追記

(レビュー後の対応や再確認の結果を、日付つきで追記する。本文は書き換えない)
