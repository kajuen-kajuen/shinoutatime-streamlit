---
name: test
description: しのうたタイムのテストの穴を埋める。データの読み込み・結合・表示用の加工・検索・ページ起動を、仕様を根拠に利用者への影響が大きい順に守る
argument-hint: <対象(任意)>
---

本体は `docs/prompts/test.md`。

読む順番(全部読んでから始める。specs は触る機能のものだけ):
1. `docs/prompts/_common-context.md`(前提・絶対制約・決めてよいこと／聞くこと)
2. `docs/prompts/_commands.md`(そのまま打つコマンド)
3. `docs/prompts/test.md`
4. 対象の機能の `docs/specs/<機能>.md`

進め方: test.md の「手順」を上から順に。「止まって聞く所」ではユーザーの返事を待つ(Plan Mode の計画は承認を待つ)。
終わりの型: `sh tools/check-rules.sh` → `_commands.md` のテスト → 差分の要約 → 【要確認】【仮定】の一覧。
git commit はユーザーが指示したときだけ。push はしない。main には触れない。develop への切り替えと git merge はユーザーの確認を取ってから。

引数: $ARGUMENTS
