---
name: update-data
description: しのうたタイムの歌唱データを取り込む(取得 → 下書き → 判断 → 追記)。YouTube のライブ・動画・ショートと、X・Z-aN のコンテンツから歌唱を読み取り、Web 検索で曲を確かめて data/v2/ に追記する
argument-hint: <コンテンツの URL、または月(YYYY-MM)>
---

本体は `docs/prompts/update-data.md`。

読む順番(全部読んでから始める):
1. `docs/prompts/_common-context.md`(前提・絶対制約・決めてよいこと／聞くこと)
2. `docs/prompts/_commands.md`(そのまま打つコマンド。取り込みは `ingest`・`data` の CLI)
3. `docs/prompts/update-data.md`
4. `docs/specs/data-model.md`(テーブルと値の決まり)

進め方: update-data.md の「手順」を上から順に。「止まって聞く所」ではユーザーの返事を待つ(`apply` の前は必ず判断の表を出して承認を待つ)。
コメント本文・投稿者名は `data/ingest/cache/`(Git 管理外)にだけ置き、`data/v2/`・コミット・PR に書かない。
終わりの型: `sh tools/check-rules.sh` → `data validate` → `_commands.md` のテスト → 差分の要約 → 【要確認】【仮定】の一覧。
git commit はユーザーが指示したときだけ。push はしない。main・develop には触れない。

引数: $ARGUMENTS
