# プロジェクト構成整理案

## 現在の問題点

1. **ルートディレクトリが散らかっている**
   - バッチファイルが3つ
   - 手動テストファイルが2つ（test_repositories_manual.py, test_utils_manual.py）
   - 検証用ファイル（verify_utils.py）
   - ドキュメントファイルが複数

2. **ドキュメントが分散している**
   - ルートに複数のマークダウンファイル
   - docs/ フォルダにも複数のドキュメント

3. **一時ファイル・生成ファイルが混在**
   - htmlcov/ (カバレッジレポート)
   - .hypothesis/ (プロパティテストのキャッシュ)
   - __pycache__/ (Pythonキャッシュ)

## 整理後の理想的な構成

```
shinoutatime-streamlit/
├── .devcontainer/          # Dev Container設定
├── .github/                # GitHub設定
├── .kiro/                  # Kiro設定
│   ├── specs/             # 機能仕様書
│   └── steering/          # ステアリングルール
├── .streamlit/            # Streamlit設定
├── data/                  # データファイル
│   ├── backups/          # バックアップ
│   ├── data.xlsx         # 入力データ
│   └── *.TSV             # 生成されたTSVファイル
├── docs/                  # ドキュメント
│   ├── api/              # API仕様書
│   ├── guides/           # ガイド
│   │   ├── user-guide.md
│   │   ├── developer-guide.md
│   │   └── excel-to-tsv-guide.md
│   ├── architecture/     # アーキテクチャ
│   │   ├── architecture.md
│   │   ├── data-flow.md
│   │   └── error-handling.md
│   └── testing/          # テスト関連
├── logs/                  # ログファイル
├── pages/                 # Streamlitページ
├── scripts/               # 実行スクリプト（新規）
│   ├── excel_to_tsv_converter.bat
│   ├── excel_to_tsv_full.bat
│   ├── excel_to_tsv_dryrun.bat
│   ├── verify_environment.bat
│   └── verify_environment.sh
├── src/                   # ソースコード
│   ├── cli/              # CLIツール
│   ├── clients/          # 外部APIクライアント
│   ├── config/           # 設定
│   ├── core/             # コア機能
│   ├── exceptions/       # 例外定義
│   ├── models/           # データモデル
│   ├── repositories/     # データアクセス層
│   ├── services/         # ビジネスロジック
│   ├── ui/               # UI コンポーネント
│   └── utils/            # ユーティリティ
├── tests/                 # テスト
│   ├── fixtures/         # テストフィクスチャ
│   ├── integration/      # 統合テスト
│   ├── manual/           # 手動テスト
│   ├── property/         # プロパティベーステスト
│   └── unit/             # ユニットテスト
├── .coverage              # カバレッジデータ
├── .env.example           # 環境変数テンプレート
├── .gitignore             # Git除外設定
├── docker-compose.yml     # Docker Compose設定
├── Dockerfile             # Dockerイメージ定義
├── Home.py                # Streamlitメインページ
├── footer.py              # フッターコンポーネント
├── LICENSE                # ライセンス
├── README.md              # プロジェクト概要
├── requirements.txt       # Python依存関係
├── SETUP.md               # セットアップガイド
├── style.css              # スタイルシート
└── TROUBLESHOOTING.md     # トラブルシューティング
```

## 整理手順

### 1. scripts/ フォルダを作成してバッチファイルを移動

```bash
mkdir scripts
move excel_to_tsv_converter.bat scripts/
move excel_to_tsv_full.bat scripts/
move excel_to_tsv_dryrun.bat scripts/
move verify_environment.bat scripts/
move verify_environment.sh scripts/
```

### 2. 手動テストファイルを tests/manual/ に移動

```bash
move test_repositories_manual.py tests/manual/
move test_utils_manual.py tests/manual/
move verify_utils.py tests/manual/
```

### 3. ドキュメントを整理

```bash
# docs/guides/ を作成
mkdir docs\guides
move EXCEL_TO_TSV_README.md docs\guides\excel-to-tsv-guide.md

# docs/architecture/ を作成
mkdir docs\architecture
move docs\architecture.md docs\architecture\
move docs\data-flow.md docs\architecture\
move docs\error-handling.md docs\architecture\

# docs/guides/ にユーザーガイドを移動
move docs\user-guide.md docs\guides\
move docs\developer-guide.md docs\guides\
```

### 4. プロジェクトルートのドキュメントを整理

以下のファイルはルートに残す（重要度が高い）:
- README.md
- SETUP.md
- TROUBLESHOOTING.md
- LICENSE
- CONTRIBUTING.md
- CHANGELOG.md

以下のファイルは docs/ に移動:
- BRANCH_STRATEGY.md → docs/development/
- FILE_ORGANIZATION_SUMMARY.md → docs/development/

### 5. .gitignore を更新

生成ファイルとキャッシュを除外:
```
# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.coverage
htmlcov/

# Hypothesis
.hypothesis/

# Logs
logs/*.log
!logs/.gitkeep

# Data (except examples)
data/*.TSV
data/backups/*
!data/backups/.gitkeep

# IDE
.vscode/
.idea/

# Environment
.env
```

## 実装の優先順位

### 優先度: 高
1. scripts/ フォルダの作成とバッチファイルの移動
2. 手動テストファイルの移動
3. EXCEL_TO_TSV_README.md の移動

### 優先度: 中
4. docs/ の再構成
5. .gitignore の更新

### 優先度: 低
6. 古いドキュメントの整理
7. 不要なファイルの削除

## 移行後の利点

1. **ルートディレクトリがすっきり**
   - 重要なファイルのみが残る
   - プロジェクトの全体像が把握しやすい

2. **スクリプトが整理される**
   - scripts/ フォルダに集約
   - 用途別に分類しやすい

3. **ドキュメントが見つけやすい**
   - docs/ 配下で体系的に整理
   - ガイド、アーキテクチャ、テストで分類

4. **メンテナンスしやすい**
   - 関連ファイルが近くに配置
   - 新しいファイルの配置場所が明確

## 注意事項

- バッチファイルを移動した場合、実行時のパスを更新する必要があります
- README.md にスクリプトの新しい場所を記載する必要があります
- 既存のドキュメントのリンクを更新する必要があります
