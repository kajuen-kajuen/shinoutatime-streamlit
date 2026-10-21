# archive — 古い文書

今の構成やデータの仕組みと合わなくなった文書を、読み物として残しています。**新しく書くときや、作業の手順を調べるときは、ここを見ない**でください。

- 今の構成: [`docs/architecture/overview.md`](../architecture/overview.md)
- データモデル v2 の正本: [`docs/specs/data-model.md`](../specs/data-model.md)
- データの取り込みの手順: [`docs/prompts/update-data.md`](../prompts/update-data.md)

## 2026-10-20 に移した文書

| 文書 | もとの場所 | 移した理由 |
|---|---|---|
| [`architecture/architecture.md`](architecture/architecture.md) | `docs/architecture/` | 2025年11月時点の v1 の構成図。v2(`data/v2/`・`src/ingest/`・`views`)が無い。今は `overview.md` |
| [`architecture/data-flow.md`](architecture/data-flow.md) | `docs/architecture/` | v1 の Excel → TSV → 画面の流れだけ。v2 の取り込みの流れが無い |
| [`architecture/error-handling.md`](architecture/error-handling.md) | `docs/architecture/` | v1 の例外の説明。v2 と CLI の扱いは `overview.md` の4章 |
| [`guides/developer-guide.md`](guides/developer-guide.md) | `docs/guides/` | ホストでの `pip install`・`streamlit run` など、今の決まり(Docker で動かす)と食い違う手順が多い。今は `CLAUDE.md`・`docs/prompts/_commands.md` |
| [`development/project-structure.md`](development/project-structure.md) | `docs/development/` | 2025年11月にファイルを整理したときの案。実施済み |
| [`development/FILE_ORGANIZATION_SUMMARY.md`](development/FILE_ORGANIZATION_SUMMARY.md) | `docs/development/` | 上の整理の記録 |
| [`testing/coverage_report_summary.md`](testing/coverage_report_summary.md) | `docs/testing/` | 2025年11月時点の v1 のカバレッジ。v2 のテストを含まない |

## 2026-10-22 に移した文書

2026-10-21 のフェーズ2で画面が v2(`data/v2/`)を読むようになり、v1 のデータの手順はもう使わないため。

| 文書 | もとの場所 | 移した理由 |
|---|---|---|
| [`data-management.md`](data-management.md) | `docs/` | v1 のデータ(`data/*.TSV`・`data.xlsx`)の形と更新の手順。今は `docs/specs/data-model.md`・`docs/prompts/update-data.md` |
| [`guides/excel-to-tsv-guide.md`](guides/excel-to-tsv-guide.md) | `docs/guides/` | v1 の Excel → TSV の変換ツールの使い方 |
| [`guides/artist-sort-correction-guide.md`](guides/artist-sort-correction-guide.md) | `docs/guides/` | v1 のアーティストの読みの直し方。v2 は `data set artists <id> sort_name <読み>` |
| [`testing/tests-guide-2025.md`](testing/tests-guide-2025.md) | `tests/README.md` | 2025年11月時点のテストガイド(v1 の部品が中心)。今は `docs/testing/README.md` |
| [`README-v1-sections.md`](README-v1-sections.md) | ルートの `README.md` | README の v1 のデータ・Excel の変換・アーティストの読み・X(Twitter)の埋め込みの節 |

## もとからある文書

| 文書 | 中身 |
|---|---|
| [`specs/`](specs/) | 以前の仕様(機能ごとの `requirements.md`・`design.md`・`tasks.md`) |
| [`steering/`](steering/) | 以前の書き方の決まり |
| `REORGANIZATION_SUMMARY.md`・`VERIFICATION_REPORT.md`・`TESTING_COMPLETE.md`・`test_results_summary.md` | 2025年11月のファイル整理とテストの記録 |
