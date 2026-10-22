---
name: review
description: しのうたタイムの全体レビューと改善提案。公開リポジトリの安全とデータの正しさを優先し、コードは直さず docs/reviews/ に記録する
argument-hint: <重点観点(任意)>
---

本体は `docs/prompts/review.md`。

読む順番(全部読んでから始める。specs は触る機能のものだけ):
1. `docs/prompts/_common-context.md`(前提・絶対制約・決めてよいこと／聞くこと)
2. `docs/prompts/_commands.md`(そのまま打つコマンド)
3. `docs/prompts/review.md`
4. `docs/specs/`(全体のとき)と `docs/README.md` の「レビュー記録」

進め方: review.md の「手順」を上から順に。「止まって聞く所」ではユーザーの返事を待つ(Plan Mode の計画は承認を待つ)。
終わりの型: `sh tools/check-rules.sh` → `_commands.md` のテスト → 差分の要約 → 【要確認】【仮定】の一覧。
git commit はユーザーが指示したときだけ。push はしない。main には触れない。develop への切り替えと git merge はユーザーの確認を取ってから。

引数: $ARGUMENTS
