# テストドキュメント

しのうたタイムのテストの置き場所・流し方・今の状態です。テストの書き方の詳細は [`tests/README.md`](../../tests/README.md)。

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
| `tests/unit/` | ユニットテスト(v1 のサービス・リポジトリ・CLI など) |
| `tests/unit/v2/` | データモデル v2 のテスト(文字列とリンク、読み書きと検査、操作と集計、取り込み・YouTube API) |
| `tests/property/` | hypothesis を使ったプロパティベーステスト(v1) |
| `tests/integration/` | 統合テスト(v1) |
| `tests/e2e/` | ページの起動(Streamlit の `AppTest`)。`data/` の本物の TSV を読む |
| `tests/performance/` | 性能テスト。架空の2万件で、読み込みから集計までを約0.5秒で終えることを確かめる(`--runslow`) |
| `tests/fixtures/` | テスト用のデータ |

## 今の状態(2026-10-20)

- 全体: **792 passed / 21 failed / 11 errors / 4 skipped**
- v2(`tests/unit/v2`): **146 passed**(失敗なし)
- 失敗しているのは v1 の古いテストだけです(既知の課題)。
  - テストファイルで `MagicMock` を import し忘れているもの(`tests/integration/test_environment_verification.py`)
  - 前提が今のコードと合わなくなったもの(`tests/unit/test_error_cases.py`・`tests/e2e/test_app_coverage.py` など)
  - `tests/property/test_file_repository_properties.py`: hypothesis が `"\r\n"` が `"\n"` に変わる食い違いを見つけ、`.hypothesis` に保存したので、以後は毎回失敗する(v1 の `FileRepository` の穴)
- 変更の前後で、**失敗が増えていない**ことを確かめます。v1 の古いテストは、本番の画面を v2 に切り替える(フェーズ2)ときに、まとめて見直す予定です。

## 古い記録

2025年11月時点の記録は `docs/archive/` に移しました。v2 のテストを含みません。

- [カバレッジレポートのサマリー](../archive/testing/coverage_report_summary.md)(84件、2025年11月)
- [`docs/archive/TESTING_COMPLETE.md`](../archive/TESTING_COMPLETE.md)(テスト完了報告)

## 関連ドキュメント

- [テストガイド](../../tests/README.md) - テストの書き方と拡張方法
- [構成の概要](../architecture/overview.md) - アプリの層とデータの流れ、既知の課題
