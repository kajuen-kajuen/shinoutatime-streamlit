# テストドキュメント

しのうたタイムのテストの流し方・置き場所・書き方の要点・今の状態です。

## 流し方

コマンドはすべて Docker のコンテナで流します(ホストで `pytest` を打たない)。先に `docker compose up -d` でコンテナを起動しておきます。

```bash
# 全部
docker compose exec shinouta-time pytest

# 一部(ディレクトリやファイル名に替えてよい)
docker compose exec shinouta-time pytest tests/unit/v2 -q

# 性能のテストも(時間がかかるので、--runslow のときだけ動く)
docker compose exec shinouta-time pytest --runslow

# カバレッジ
docker compose exec shinouta-time pytest --cov=src --cov-report=term-missing
```

ほかのコマンドは [`docs/prompts/_commands.md`](../prompts/_commands.md)。

## 置き場所

| ディレクトリ | 中身 |
|---|---|
| `tests/unit/v2/` | データモデル v2 のテスト(文字列とリンク、読み書きと検査、操作と集計、取り込み・YouTube API) |
| `tests/unit/ui/` | 画面の部品のテスト(ページの準備 `page_setup`、Home の絞り込み・表の組み立て・データの時点) |
| `tests/unit/` | 設定・ログ・例外と、X の埋め込み(取得・保存・HTML の検査)のテスト |
| `tests/property/` | hypothesis を使ったプロパティベーステスト(設定・ログ・X の埋め込み) |
| `tests/integration/` | 統合テスト(画面の部品・v2 の読み込みのキャッシュ) |
| `tests/e2e/` | ページの起動・検索・さらに表示(Streamlit の `AppTest`)。本物の `data/v2/` を読むので、件数は「1件以上」などで確かめる |
| `tests/performance/` | 性能テスト。架空の2万件で、読み込みから集計までを約0.5秒で終えることを確かめる(`--runslow`) |
| `tests/fixtures/` | テスト用のデータ |

## 書き方の要点

- 期待値は仕様(`docs/prompts/_common-context.md`・`docs/specs/`)を根拠にします。今の実装の出力をそのまま期待値にしません。
- v2 のテストのデータは、`tests/unit/v2/conftest.py` の `make_dataset`・`content` でテストの中に小さく作ります(すべて架空のデータ)。e2e 以外は `data/` の本物のデータに頼りません。
- e2e の検索フォーム(`st.form`)は、入力欄に `set_value` したあと `.run()` を挟まずに「検索」ボタンを `click().run()` します(フォームの中の値は、送信したときにまとめて渡るため)。
- ネットワークに出るテストは書きません(YouTube API などはモックで)。

## 今の状態(2026-10-23)

- 全体: **561 passed / 1 skipped**(失敗なし。skip は `--runslow` の性能テスト)
- v1 の部品のテストは、2026-10-23 のフェーズ3で v1 のコードと一緒に消した。
- 変更の前後で、**失敗が増えていない**ことを確かめます。

## 古い記録

2025年11月時点の記録は `docs/archive/` に移しました。v2 のテストを含みません。

- [古いテストガイド](../archive/testing/tests-guide-2025.md)(v1 の部品が中心、2025年11月)
- [カバレッジレポートのサマリー](../archive/testing/coverage_report_summary.md)(84件、2025年11月)
- [`docs/archive/TESTING_COMPLETE.md`](../archive/TESTING_COMPLETE.md)(テスト完了報告)

## 関連ドキュメント

- [構成の概要](../architecture/overview.md) - アプリの層とデータの流れ、既知の課題
