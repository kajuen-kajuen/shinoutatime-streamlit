# テストガイド

このディレクトリには、「しのうたタイム」アプリケーションの各種テストが含まれています。

## テストの種類

### 1. 環境構築動作確認テスト（test_environment_verification.py）

Docker Composeで構築した環境が正しく動作することを確認するテストです。

**検証内容:**
- アプリケーションが正常に起動すること（要件10.1）
- データ読み込みが正常に動作すること（要件10.2）
- 基本機能（検索、ページ遷移）が動作すること（要件10.3）
- データ整合性が保たれていること（要件10.4）
- 環境分離が正しく機能していること（要件2.4, 14.5）
- 本番環境との整合性（要件13.1〜13.5）

### 2. ユーティリティ関数テスト（test_utils.py）

データ変換・処理関数の正確性を確認するテストです。

**検証内容:**
- タイムスタンプ文字列の秒数変換
- YouTubeタイムスタンプ付きURL生成
- 曲目番号の生成ロジック
- 日付文字列の変換

### 3. 検索サービステスト（test_search_service.py）

検索機能とフィルタリング機能の動作を確認するテストです。

**検証内容:**
- キーワード検索（単一/複数フィールド）
- 大文字小文字の区別/非区別
- 部分一致検索
- 日本語文字検索
- 複数条件フィルタリング
- エッジケース（空データ、NaN値など）

### 4. 設定管理テスト（test_config.py）

アプリケーション設定の読み込みと検証を確認するテストです。

**検証内容:**
- デフォルト値の設定
- 環境変数からの読み込み
- ブール値の解析
- 設定値のバリデーション
- 無効な設定値のエラー処理

### 5. エラーハンドリングテスト（test_errors.py）

カスタム例外クラスとエラーログの動作を確認するテストです。

**検証内容:**
- カスタム例外クラスの動作
- 例外の継承関係
- エラーログの記録
- コンテキスト情報付きログ
- 実際のエラーシナリオ

## テストの実行方法

### Docker Compose環境でのテスト実行

1. **Dockerコンテナを起動**

```bash
docker-compose up -d
```

2. **全てのテストを実行**

```bash
docker-compose exec shinouta-time pytest tests/ -v
```

3. **特定のテストファイルを実行**

```bash
# 環境構築動作確認テスト
docker-compose exec shinouta-time pytest tests/test_environment_verification.py -v

# ユーティリティ関数テスト
docker-compose exec shinouta-time pytest tests/test_utils.py -v

# 検索サービステスト
docker-compose exec shinouta-time pytest tests/test_search_service.py -v

# 設定管理テスト
docker-compose exec shinouta-time pytest tests/test_config.py -v

# エラーハンドリングテスト
docker-compose exec shinouta-time pytest tests/test_errors.py -v
```

4. **詳細なテスト結果を表示**

```bash
docker-compose exec shinouta-time pytest tests/ -v -s
```

5. **特定のテストクラスのみ実行**

```bash
# 環境構築動作確認テストのみ
docker-compose exec shinouta-time pytest tests/test_environment_verification.py::TestEnvironmentVerification -v

# ユーティリティ関数のタイムスタンプ変換テストのみ
docker-compose exec shinouta-time pytest tests/test_utils.py::TestConvertTimestampToSeconds -v

# 検索サービステストのみ
docker-compose exec shinouta-time pytest tests/test_search_service.py::TestSearchService -v
```

6. **特定のテストメソッドのみ実行**

```bash
docker-compose exec shinouta-time pytest tests/test_environment_verification.py::TestEnvironmentVerification::test_search_functionality -v
```

7. **カバレッジレポート付きで実行（オプション）**

```bash
docker-compose exec shinouta-time pytest tests/ --cov=src --cov-report=html
```

### ローカル環境（Python仮想環境）でのテスト実行

1. **仮想環境をアクティベート**

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

2. **pytestをインストール（未インストールの場合）**

```bash
pip install pytest
```

3. **テストを実行**

```bash
pytest tests/test_environment_verification.py -v
```

## テスト結果の見方

### 成功例

```
tests/test_environment_verification.py::TestEnvironmentVerification::test_data_files_exist PASSED
tests/test_environment_verification.py::TestEnvironmentVerification::test_python_version PASSED
tests/test_environment_verification.py::TestEnvironmentVerification::test_load_lives_data PASSED
...
```

全てのテストが`PASSED`と表示されれば、環境構築は成功です。

### 失敗例

```
tests/test_environment_verification.py::TestEnvironmentVerification::test_data_files_exist FAILED
...
AssertionError: 配信データファイルが見つかりません: data/M_YT_LIVE.TSV
```

`FAILED`と表示された場合、エラーメッセージを確認して問題を解決してください。

## トラブルシューティング

### pytestが見つからない

**エラー:**
```
bash: pytest: command not found
```

**解決方法:**
```bash
pip install pytest
```

### データファイルが見つからない

**エラー:**
```
AssertionError: 配信データファイルが見つかりません: data/M_YT_LIVE.TSV
```

**解決方法:**
- `data/`ディレクトリに必須TSVファイルが存在することを確認
- Gitリポジトリを正しくクローンしたか確認

### Pythonバージョンが一致しない

**エラー:**
```
AssertionError: Pythonマイナーバージョンが11ではありません（本番環境と一致しません）
```

**解決方法:**
- Docker Compose環境を使用している場合、Dockerfileが正しくビルドされているか確認
- ローカル環境の場合、Python 3.11をインストール

### モジュールが見つからない

**エラー:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**解決方法:**
```bash
pip install -r requirements.txt
```

## テスト結果の確認

### 最新のテスト結果

- **総テスト件数**: 84件
- **成功**: 84件
- **失敗**: 0件
- **実行時間**: 約2秒

詳細は `test_results_summary.md` を参照してください。

## 継続的な動作確認

環境構築後、以下のタイミングでテストを実行することを推奨します：

1. **初回環境構築後**: 全てのテストを実行して環境が正しく構築されたことを確認
2. **依存パッケージ更新後**: requirements.txt更新後にテストを実行
3. **データファイル更新後**: data/ディレクトリのTSVファイル更新後にテストを実行
4. **コード変更後**: 主要な機能を変更した後にテストを実行
5. **プルリクエスト作成前**: 全てのテストが成功することを確認

## テストの拡張

新しい機能を追加した場合、対応するテストを追加してください：

### 1. 既存のテストファイルに追加する場合

適切なテストファイルに新しいテストメソッドを追加します：

```python
def test_new_feature(self, fixture_name):
    """
    新機能が正常に動作することを確認
    
    要件XX.X: 新機能の動作確認
    """
    # テストコード
    result = function_to_test(input_data)
    assert result == expected_value, "エラーメッセージ"
```

### 2. 新しいテストファイルを作成する場合

新しいモジュールをテストする場合は、新しいテストファイルを作成します：

```python
"""
新モジュールのテスト

src/path/to/new_module.pyが正しく動作することを確認するテストです。
"""

import pytest
from src.path.to.new_module import NewClass


class TestNewClass:
    """NewClassのテスト"""
    
    @pytest.fixture
    def instance(self):
        """テスト用のインスタンスを提供"""
        return NewClass()
    
    def test_basic_functionality(self, instance):
        """基本機能が動作することを確認"""
        result = instance.method()
        assert result is not None
```

### 3. テストのベストプラクティス

- **明確なテスト名**: テストメソッド名は何をテストしているか明確にする
- **1テスト1検証**: 各テストメソッドは1つの機能を検証する
- **独立性**: テストは他のテストに依存しない
- **再現性**: 同じ入力で常に同じ結果を返す
- **高速**: テストは可能な限り高速に実行される
- **日本語docstring**: 検証内容を日本語で記述する
