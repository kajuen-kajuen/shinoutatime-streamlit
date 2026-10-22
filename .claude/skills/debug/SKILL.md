---
name: debug
description: しのうたタイムの不具合(表示・検索・データ読み込み・リンク)を仮説検証型で調査する。原因の説明が完成するまで修正禁止、データは直さず報告、最小修正で締める
argument-hint: <症状と発生条件>
---

本体は `docs/prompts/debug.md`。

読む順番(全部読んでから始める。specs は触る機能のものだけ):
1. `docs/prompts/_common-context.md`(前提・絶対制約・決めてよいこと／聞くこと)
2. `docs/prompts/_commands.md`(そのまま打つコマンド)
3. `docs/prompts/debug.md`
4. 関係する `docs/specs/<機能>.md`(一覧は `docs/README.md`)

進め方: debug.md の「手順」を上から順に。「止まって聞く所」ではユーザーの返事を待つ(Plan Mode の計画は承認を待つ)。
終わりの型: `sh tools/check-rules.sh` → `_commands.md` のテスト → 差分の要約 → 【要確認】【仮定】の一覧。
git commit はユーザーが指示したときだけ。push はしない。main には触れない。develop への切り替えと git merge はユーザーの確認を取ってから。

引数: $ARGUMENTS
