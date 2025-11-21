# V_SONG_LIST.TSV 自動生成ツール

## 概要

V_SONG_LIST.TSV自動生成ツールは、M_YT_LIVE.TSVとM_YT_LIVE_TIMESTAMP.TSVから曲ごとの最新歌唱情報を自動的に集計し、V_SONG_LIST.TSVを生成するPythonベースのコマンドラインツールです。

## 主な機能

- **データ自動結合**: 配信情報とタイムスタンプ情報を自動的に結合
- **最新歌唱選択**: 同じ曲の複数レコードから最新の歌唱を自動選択
- **曲名正規化**: バリエーション表記（(1chorus)、(short ver)等）を自動処理
- **ソート用読み仮名生成**: 日本語アーティスト名から自動的にひらがな読み仮名を生成
- **タイムスタンプ付きURL生成**: YouTube配信の該当箇所へ直接ジャンプできるURLを生成
- **データ品質チェック**: 類似したアーティスト名・曲名を検出して警告
- **差分検出**: 既存ファイルとの差分を表示

## インストール

### 前提条件

- Python 3.11以上
- Docker（推奨）

### 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

主な依存ライブラリ：
- `pykakasi`: 日本語の読み仮名変換
- `python-Levenshtein`: 類似度計算
- `pytest`: テストフレームワーク
- `hypothesis`: プロパティベーステスト

## 使用方法

### 基本的な使い方

```bash
python -m src.cli.song_list_generator
```

デフォルトでは以下のファイルを使用します：
- 入力: `data/M_YT_LIVE.TSV`, `data/M_YT_LIVE_TIMESTAMP.TSV`
- 出力: `data/V_SONG_LIST.TSV`

### コマンドライン引数

```bash
python -m src.cli.song_list_generator [OPTIONS]
```

#### オプション一覧

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--live-file PATH` | M_YT_LIVE.TSVのパス | `data/M_YT_LIVE.TSV` |
| `--timestamp-file PATH` | M_YT_LIVE_TIMESTAMP.TSVのパス | `data/M_YT_LIVE_TIMESTAMP.TSV` |
| `--output-file PATH` | V_SONG_LIST.TSVの出力パス | `data/V_SONG_LIST.TSV` |
| `--dry-run` | ドライランモード（ファイルを書き込まない） | - |
| `--similarity-threshold FLOAT` | 類似度チェックの閾値（0.0-1.0） | `0.85` |
| `--no-similarity-check` | 類似性チェックを無効化 | - |
| `--verbose`, `-v` | 詳細ログを表示 | - |
| `--help`, `-h` | ヘルプメッセージを表示 | - |
| `--version` | バージョン情報を表示 | - |

### 使用例

#### 例1: 基本的な実行

```bash
python -m src.cli.song_list_generator
```

#### 例2: カスタムファイルパスを指定

```bash
python -m src.cli.song_list_generator \
  --live-file data/custom_live.tsv \
  --timestamp-file data/custom_timestamp.tsv \
  --output-file data/custom_output.tsv
```

#### 例3: ドライランモードで差分確認

```bash
python -m src.cli.song_list_generator --dry-run
```

ファイルを実際に書き込まずに、変更内容のみを表示します。

#### 例4: 詳細ログを表示

```bash
python -m src.cli.song_list_generator --verbose
```

処理の各ステップの詳細情報を表示します。

#### 例5: 類似性チェックの閾値を変更

```bash
python -m src.cli.song_list_generator --similarity-threshold 0.9
```

類似度が90%以上のペアのみを警告として表示します。

#### 例6: 類似性チェックを無効化

```bash
python -m src.cli.song_list_generator --no-similarity-check
```

類似性チェックをスキップして処理を高速化します。

## 出力形式

生成されるV_SONG_LIST.TSVは以下の形式です：

```
アーティスト	アーティスト(ソート用)	曲名	最近の歌唱
Vaundy	Vaundy	怪獣の花唄	https://www.youtube.com/live/xxxxx?si=xxxxx&t=123s
米津玄師	よねづけんし	Lemon	https://www.youtube.com/live/xxxxx?si=xxxxx&t=456s
```

- **アーティスト**: アーティスト名（元の表記）
- **アーティスト(ソート用)**: ソート用の読み仮名（ひらがな）
- **曲名**: 曲名
- **最近の歌唱**: タイムスタンプ付きYouTube URL

## データ処理ルール

### 最新歌唱の選択

同じアーティストと曲名の組み合わせが複数存在する場合：
1. 配信日が最も新しいレコードを選択
2. 配信日が同じ場合は、配信IDが大きい方を選択

### 曲名の正規化

以下のバリエーション表記を検出して処理します：
- `(1chorus)`, `(2chorus)` 等
- `(short ver)`, `(long ver)` 等
- `(1phrase)` 等

正規版（バリエーション表記なし）が存在する場合は、正規版を優先します。

### ソート順

1. ソート用アーティスト名の昇順
2. 同じアーティストの場合は、曲名の昇順

### エラーハンドリング

以下の場合は警告を表示して該当レコードをスキップします：
- タイムスタンプ情報に対応する配信情報が存在しない
- 曲名またはアーティスト名が空白
- タイムスタンプの形式が不正

## ログ出力

### 通常モード

```
INFO: M_YT_LIVE.TSVを読み込んでいます...
INFO: 110件の配信情報を読み込みました
INFO: M_YT_LIVE_TIMESTAMP.TSVを読み込んでいます...
INFO: 813件のタイムスタンプ情報を読み込みました
INFO: データを結合しています...
INFO: 曲リストを生成しました（442件）
INFO: V_SONG_LIST.TSVに出力しました
```

### 詳細モード（--verbose）

```
DEBUG: 配信ID 1: 2025/4/27 - 【初配信】おばけじゃないから...
DEBUG: タイムスタンプID 1: LIVE_ID=1, 0:01:47, かすかなおと, 幽音しの
DEBUG: ソート用アーティスト名を生成: 幽音しの -> ゆうねしの
DEBUG: タイムスタンプ付きURL生成: https://www.youtube.com/live/xxxxx&t=107s
```

### 警告メッセージ

```
WARNING: タイムスタンプID 39に対応する配信情報が見つかりません（LIVE_ID=999）
WARNING: タイムスタンプID 40の曲名が空白です
WARNING: 類似したアーティスト名を検出: "米津玄師" と "米津 玄師" (類似度: 0.95)
```

### 差分情報

```
INFO: 既存ファイルとの差分:
  追加: 5件
  削除: 2件
  更新: 3件

追加された曲:
  - Vaundy / 新曲1
  - YOASOBI / 新曲2

削除された曲:
  - 旧アーティスト / 旧曲1

更新された曲:
  - Ado / 曲名 (URL変更)
```

## トラブルシューティング

### エラー: ファイルが見つかりません

```
ERROR: ファイルが見つかりません: data/M_YT_LIVE.TSV
```

**解決方法**: ファイルパスが正しいか確認してください。相対パスはカレントディレクトリからの相対パスです。

### エラー: ファイル形式が不正

```
ERROR: ファイル形式が不正です: ヘッダーが一致しません
```

**解決方法**: TSVファイルのヘッダー行が正しいか確認してください。

### 警告: 読み仮名の自動生成が失敗

```
WARNING: 読み仮名の自動生成が失敗しました: アーティスト名
```

**解決方法**: 元のアーティスト名がソート用アーティスト名として使用されます。特殊な文字が含まれている可能性があります。

### パフォーマンスが遅い

類似性チェックは計算量が多いため、大規模データセットでは時間がかかる場合があります。

**解決方法**:
- `--no-similarity-check` オプションで類似性チェックを無効化
- `--similarity-threshold` オプションで閾値を上げる（例: 0.95）

## テスト

### ユニットテストの実行

```bash
pytest tests/unit/
```

### プロパティベーステストの実行

```bash
pytest tests/property/
```

### すべてのテストの実行

```bash
pytest
```

### カバレッジレポートの生成

```bash
pytest --cov=src --cov-report=html
```

## 開発

### プロジェクト構造

```
src/
├── cli/
│   └── song_list_generator.py  # CLIエントリーポイント
├── models/
│   └── song_list_models.py     # データモデル
├── repositories/
│   ├── live_repository.py      # 配信情報リポジトリ
│   ├── timestamp_repository.py # タイムスタンプ情報リポジトリ
│   └── song_list_repository.py # 曲リストリポジトリ
├── services/
│   └── song_list_service.py    # ビジネスロジック
└── utils/
    ├── artist_sort_generator.py # ソート用読み仮名生成
    ├── url_generator.py         # URL生成
    └── similarity_checker.py    # 類似度計算
```

### コーディング規約

- PEP 8に準拠
- 型ヒントを使用
- docstringを記述（日本語）
- テストカバレッジ80%以上を目標

## ライセンス

このプロジェクトのライセンスについては、LICENSEファイルを参照してください。

## 貢献

バグ報告や機能要望は、GitHubのIssueで受け付けています。

## 変更履歴

### v1.0.0 (2025-XX-XX)
- 初回リリース
- 基本機能の実装
  - データ読み込み・結合
  - 最新歌唱選択
  - 曲名正規化
  - ソート用読み仮名生成
  - タイムスタンプ付きURL生成
  - 類似性チェック
  - 差分検出
