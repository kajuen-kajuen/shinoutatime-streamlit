---
name: feature
description: しのうたタイムの新機能を Plan Mode で設計し、承認後に実装する。層(repositories→services→core→ui)とキャッシュの決まりを守り、スマホ幅でも崩さない
argument-hint: <機能要件>
---

本体は `docs/prompts/feature.md`。

読む順番(全部読んでから始める。specs は触る機能のものだけ):
1. `docs/prompts/_common-context.md`(前提・絶対制約・決めてよいこと／聞くこと)
2. `docs/prompts/_commands.md`(そのまま打つコマンド)
3. `docs/prompts/feature.md`
4. 関係する `docs/specs/<機能>.md`(一覧は `docs/README.md`)

進め方: feature.md の「手順」を上から順に。「止まって聞く所」ではユーザーの返事を待つ(Plan Mode の計画は承認を待つ)。
終わりの型: `sh tools/check-rules.sh` → `_commands.md` のテスト → 差分の要約 → 【要確認】【仮定】の一覧。
git commit はユーザーが指示したときだけ。push はしない。main・develop には触れない。

引数: $ARGUMENTS
