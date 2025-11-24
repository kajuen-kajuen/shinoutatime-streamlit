# Excel to TSV変換ツール 使い方

## 概要

このツールは、`data.xlsx`ファイルから2つのTSVファイル（`M_YT_LIVE.TSV`と`M_YT_LIVE_TIMESTAMP.TSV`）を自動生成します。

## バッチファイル一覧

### 1. excel_to_tsv_converter.bat（推奨）

**用途**: TSVファイルのみを生成

**実行内容**:
- `data.xlsx` を読み込み
- `M_YT_LIVE.TSV` を生成（配信情報）
- `M_YT_LIVE_TIMESTAMP.TSV` を生成（タイムスタンプ情報）
- 既存ファイルを自動バックアップ

**使い方**:
1. `data.xlsx` を `data/` フォルダに配置
2. `excel_to_tsv_converter.bat` をダブルクリック
3. 処理完了を待つ

**生成されるファイル**:
- `data/M_YT_LIVE.TSV`
- `data/M_YT_LIVE_TIMESTAMP.TSV`
- `data/backups/M_YT_LIVE_YYYYMMDD_HHMMSS.TSV`（バックアップ）
- `data/backups/M_YT_LIVE_TIMESTAMP_YYYYMMDD_HHMMSS.TSV`（バックアップ）

---

### 2. excel_to_tsv_full.bat

**用途**: TSVファイルとV_SONG_LIST.TSVを生成

**実行内容**:
- `excel_to_tsv_converter.bat` と同じ処理
- さらに `song_list_generator` を実行して `V_SONG_LIST.TSV` を生成

**使い方**:
1. `data.xlsx` を `data/` フォルダに配置
2. `excel_to_tsv_full.bat` をダブルクリック
3. 処理完了を待つ

**生成されるファイル**:
- `data/M_YT_LIVE.TSV`
- `data/M_YT_LIVE_TIMESTAMP.TSV`
- `data/V_SONG_LIST.TSV`
- バックアップファイル

**注意**: `song_list_generator` が失敗する場合がありますが、TSVファイルは正常に生成されます。

---

### 3. excel_to_tsv_dryrun.bat

**用途**: 処理内容の確認（ファイルを生成しない）

**実行内容**:
- 実際のファイルを生成せずに、処理内容を確認
- データの検証結果を表示

**使い方**:
1. `data.xlsx` を `data/` フォルダに配置
2. `excel_to_tsv_dryrun.bat` をダブルクリック
3. ログを確認

**用途**:
- 初めて使用する前の動作確認
- データの検証エラーを事前に確認
- 処理時間の見積もり

---

## 必要な環境

- Docker Desktop がインストールされていること
- Docker コンテナが起動可能であること
- `data/data.xlsx` ファイルが存在すること

## Excelファイルの形式

### M_YT_LIVEシート

必要な列（順不同、ヘッダー名で判定）:
- ID
- 配信日
- タイトル
- URL

### M_YT_LIVE_TIMESTAMPシート

必要な列（順不同、ヘッダー名で判定）:
- ID
- LIVE_ID
- タイムスタンプ
- 曲名
- アーティスト

**注意**: Excelファイルに追加の列があっても問題ありません。必要な列のみが抽出されます。

---

## トラブルシューティング

### エラー: Dockerコンテナの起動に失敗しました

**原因**: Docker Desktop が起動していない

**解決方法**:
1. Docker Desktop を起動
2. 数秒待ってから再度バッチファイルを実行

---

### エラー: data\data.xlsx が見つかりません

**原因**: 入力ファイルが存在しない

**解決方法**:
1. `data.xlsx` を `data/` フォルダに配置
2. ファイル名が正確に `data.xlsx` であることを確認

---

### 警告: フィールド数が不正です

**原因**: データの一部に空のフィールドがある

**影響**: 警告ですが、ファイルは生成されます

**解決方法**:
- Excelファイルのデータを確認して、空のセルを埋める
- または、警告を無視して続行

---

### song_list_generatorの実行に失敗しました

**原因**: 日付形式の問題など

**影響**: V_SONG_LIST.TSVは生成されませんが、M_YT_LIVE.TSVとM_YT_LIVE_TIMESTAMP.TSVは正常に生成されます

**解決方法**:
- `excel_to_tsv_converter.bat` を使用してTSVファイルのみを生成
- 必要に応じて、song_list_generatorを別途実行

---

## コマンドラインから実行する場合

### 基本的な実行

```bash
docker-compose exec shinouta-time python -m src.cli.excel_to_tsv_cli --skip-song-list
```

### ドライランモード

```bash
docker-compose exec shinouta-time python -m src.cli.excel_to_tsv_cli --dry-run
```

### 詳細ログ付き

```bash
docker-compose exec shinouta-time python -m src.cli.excel_to_tsv_cli --skip-song-list --verbose
```

### ヘルプを表示

```bash
docker-compose exec shinouta-time python -m src.cli.excel_to_tsv_cli --help
```

---

## よくある質問

### Q: バックアップファイルは削除しても良いですか？

A: はい。バックアップファイルは `data/backups/` フォルダに保存されており、必要に応じて削除できます。

### Q: 処理にどのくらい時間がかかりますか？

A: データ量にもよりますが、通常は1秒未満で完了します。

### Q: 既存のTSVファイルは上書きされますか？

A: はい。ただし、上書き前に自動的にバックアップが作成されます。

### Q: Excelファイルに追加の列があっても大丈夫ですか？

A: はい。必要な列（ID、配信日、タイトル、URL など）のみが抽出されます。

---

## サポート

問題が発生した場合は、以下の情報を確認してください:
- Docker Desktop が起動しているか
- `data/data.xlsx` が存在するか
- Excelファイルに必要なシート（M_YT_LIVE、M_YT_LIVE_TIMESTAMP）が存在するか

それでも解決しない場合は、ログの内容を確認してください。
