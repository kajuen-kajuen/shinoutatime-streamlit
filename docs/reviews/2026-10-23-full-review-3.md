# 全体 レビュー記録(3回目)

- 日付: 2026-10-23
- 種別: コードレビュー / データ確認 / セキュリティ確認(依存の既知の脆弱性)
- 対象: 全体(`9c5b25a` 時点)。前回の記録([`2026-10-22-full-review-2.md`](2026-10-22-full-review-2.md)、`63ab27a` 時点)の後の `63ab27a..9c5b25a`(データ1行・CLI のヘルプ・文書)。関連する仕様書は `docs/specs/data-model.md`
- レビューした人: 別のエージェント(モデル名は【要確認】)。指摘は Claude(Opus 5.5)が、レビューの後に本番に出た `195511f`(フェーズ3・ブラウザの確認)のリポジトリと PyPI の公開情報で確かめ、影響の説明を直した

## 1. 範囲と観点

見たもの:
- 画面: `Home.py`・`src/ui/pages/home_page.py`・`pages/`・`src/ui/components/`・`src/ui/v2_data.py`
- v2 のデータの層: `src/models/schema.py`・`src/core/views.py`・`validation.py`
- 取り込みと修正の CLI: `src/cli/ingest.py`・`src/cli/data.py`(カバレッジ)
- 公開と運用: `tools/check-rules.sh`・`requirements.txt`(`pip-audit`)・`Dockerfile`・`docker-compose.yml`・`.env.example`・`.github/`
- データ: `data/v2/*.tsv`(件数・検査・同じ配信の中で同じ曲が2回ある行)

観点: 公開リポジトリとしての安全、データの正しさ、障害時の振る舞い、表示の安全と使いやすさ、保守性(`docs/prompts/review.md` の順)。

見なかったこと:
- スマホの幅での表示、本番・stg の画面(レビューの環境でブラウザが使えなかった)
- 本来のコンテナ(`python:3.14.8-slim-trixie`)での実行。Docker が動かず、Python 3.13 の一時的な venv で流した

## 2. 指摘事項

重要度「高」の指摘はなかった。

| # | 重要度 | 場所 | 内容 | 対応 | 状態 |
|---|---|---|---|---|---|
| 1 | 中 | `requirements.txt`(pillow・certifi) | `pip-audit` が pillow 12.3.0 に 35 件(すべて 13.0.0 で修正)、certifi 2026.10.18 に 1 件の既知の脆弱性を報告。画面は画像を開かない(`st.image`・PIL を使っていない)ので、実際の危険は小さい。(Claude が確かめて直したこと: レビューは「`streamlit==1.66.0` が `pillow<13` なので上げられない」としていたが、2026-10-21 の Streamlit 1.66.1 が `pillow<14` を許すので上げられる。certifi の報告(GHSA-6q48-6c7w-9gw2)の本文では、危ないのは emSign ECC Root CA - G3 を含む「2026.10.18 より前」の版。2026.10.18 は emSign のルートをすべて外した版で、2026.10.19 は影響の無いものを戻した版。今の版に実害は無い) | streamlit 1.66.1・pillow 13.0.0・certifi 2026.10.19 に上げる。間接の依存はコンテナで取り直す | 未対応 |
| 2 | 中 | `data/v2/performances.tsv`(`yt:wFnIyA1459M`) | 2026-03-05 の深夜定期の 8 曲の `start` が空で、リンクが動画の先頭に飛ぶ(前回の #1 と同じ) | 配信のアーカイブで時刻を確かめてから `data set` で入れる(持ち主が調べる) | 未対応 |
| 3 | 低 | `src/models/schema.py` の `CONTENTS.patterns` | `contents.url` の値の形を検査していない。Home と Song List は `html.escape` してから `href` に入れるが、`javascript:` などは escape では止まらない。今のデータ(394 件)はすべて `https://` | `url` に `^https://` の検査を足す | 未対応 |
| 4 | 低 | `src/cli/ingest.py`(50%)・`src/cli/data.py`(68%) | データを書く CLI だけカバレッジが低い(画面側の `views`・`validation`・`home_page` は 96〜100%)。(Claude が確かめて足したこと: 今のテストは断る道が中心で、「検査で落ちたら保存しない」「`--dry-run`」「`set` の成功と不正値」が `main()` を通して確かめられていない) | 書き込みの前後の検査に絞ってテストを足す(振る舞いは変えない) | 未対応 |
| 5 | 低 | `.env.example` の「キャッシュ」 | `SHINOUTA_ENABLE_CACHE`・`SHINOUTA_CACHE_TTL` を書いているが、画面のキャッシュ(`v2_data._load`)は使っていないので、設定しても効かない | `.env.example` から消す。`Config` のコードとテストは、使っていないコードを残すという 2026-10-23 の判断のまま残す | 未対応 |
| 6 | 低 | `Dockerfile`・`docker-compose.yml` | `.dockerignore` が無く、`COPY . .` で `.env`(API キー)と `.git` が手元のイメージに入る(イメージは push しないので外には出ない)。ポートが `0.0.0.0` に開いていて、同じ LAN から手元のアプリが見える | `.dockerignore` を足し、ポートを `127.0.0.1:8501:8501` にする | 未対応 |
| 7 | 低 | `src/cli/__init__.py` | `twitter_embed_cli` を import している(前回の #7) | (Claude が確かめたこと: レビューの後、フェーズ3(`3719a57`)で import を消した。今は docstring だけ) | 対応済み |
| 8 | 低 | `.github/CODEOWNERS` | `* @streamlit/community-cloud` は最初のコミットのひな形のままで、Streamlit 社側のチームを指している | 消す(PR の運用は未定で、持ち主は1人) | 未対応 |

前回から変わらない既知の項目(どれも前回の判断のまま): X の埋め込みの高さ合わせが Streamlit の DOM に頼っていること(前回の #3)、GitHub Actions を SHA で固定していないこと(前回の #5)。レビューの挙げた「v1 の残り」は、フェーズ3で消した。

重要度の目安: **高**=秘密・個人情報の漏えい、データの欠落・誤表示、ページが落ちる、**中**=特定の条件で誤動作する・スマホで使いにくい、**低**=見た目・読みやすさ・将来の課題。

## 3. 確認の結果

レビューの時点(`9c5b25a`、Python 3.13 の一時的な venv):
- テスト: `888 passed, 1 skipped in 74.36s`(v1 のテストを含む。フェーズ3の後は 561 件)
- データの検査(`python -m src.cli.data validate`): 「問題はありません」。件数(ヘッダーを除く): contents 394・artists 333・songs 788・performances 2329・aliases 859
- `check-rules.sh`: `main` の上にいたことの WARN のほかは OK(コミット・push はしていない)

絶対制約のチェックリスト:

| # | 制約 | 結果 | 根拠 |
|---|---|---|---|
| 1 | main・develop に触れない | WARN(レビューの時点) | レビュー用のクローンが `main` の上にいた(コミット・push なし)。対応は作業ブランチ `fix/review-3-followup` で行う |
| 2 | 秘密・個人情報をコミットしない | OK | check-rules の「公開リポジトリ」の項目がすべて OK |
| 3 | データを確認なしで書き換えない | OK | TSV は読んだだけ |
| 4 | エスケープしない HTML を足さない | OK | `escape=False` なし。`unsafe_allow_html` は表の3か所で、データ由来の文字列は `html.escape` 済み |
| 5 | キャッシュ関数の中で表示しない | OK | check-rules で OK |

Claude の確認(2026-10-23、`195511f`): PyPI の JSON(`vulnerabilities`・`requires_dist`)で #1 の件数・修正版・Streamlit 1.66.1 の要件を確かめた。#3・#5・#6・#8 はファイルを読んで確かめた。

## 4. 良かった点

- データの質が高く、検査は「問題なし」
- 表の HTML に入るデータ由来の文字列は、すべて `html.escape` を通っている

## 5. 結論

修正後に採用(本番は今のままでも問題なく動く)。#1・#3・#4・#5・#6・#8 を作業ブランチ `fix/review-3-followup` で直す。#2 は持ち主が時刻を調べてから。

## 6. 追記

(レビュー後の対応や再確認の結果を、日付つきで追記する。本文は書き換えない)
