# Excel to TSV変換ツール 使い方

## 概要

このツールは、`data.xlsx`ファイルから2つのTSVファイル（`M_YT_LIVE.TSV`と`M_YT_LIVE_TIMESTAMP.TSV`）を自動生成します。

## 使い方

1. `data/data.xlsx` を `data/` フォルダに配置します。
2. `scripts/excel_to_tsv.bat` を実行します。

### 実行モード

バッチファイルは、引数に応じて3つのモードで動作します。

#### 1. `full` モード (デフォルト)
- **コマンド**: `excel_to_tsv.bat full` または `excel_to_tsv.bat`
- **処理内容**:
    - `M_YT_LIVE.TSV` と `M_YT_LIVE_TIMESTAMP.TSV` を生成します。
    - `song_list_generator` を実行して `V_SONG_LIST.TSV` を生成します。
- **用途**: 全てのデータファイルを一度に更新する場合に使用します。

#### 2. `tsv_only` モード
- **コマンド**: `excel_to_tsv.bat tsv_only`
- **処理内容**:
    - `M_YT_LIVE.TSV` と `M_YT_LIVE_TIMESTAMP.TSV` のみを生成します。
- **用途**: `V_SONG_LIST.TSV` の更新が不要な場合や、手動で `song_list_generator` を実行したい場合に使用します。

#### 3. `dryrun` モード
- **コマンド**: `excel_to_tsv.bat dryrun`
- **処理内容**:
    - 実際のファイル生成は行わず、処理内容の検証のみを実行します。
- **用途**:
    - 実行前のデータ検証
    - エラーの事前確認

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
