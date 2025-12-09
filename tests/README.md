# テストガイド

このディレクトリには、「しのうたタイム」アプリケーションの各種テストが含まれています。

## テストカバレッジ目標

本プロジェクトでは、コード品質を保証するために以下のカバレッジ目標を設定しています：

- **全体カバレッジ**: 70%以上
- **主要モジュールカバレッジ**: 60%以上
- **テスト実行時間**: 5秒以内

現在のカバレッジ状況は、カバレッジレポート（`htmlcov/index.html`）を参照してください。

## テストの種類

### ユニットテスト（tests/unit/）

個別の関数やクラスの動作を検証するテストです。特定の動作、エッジケース、エラーハンドリングをカバーします。

**テストファイル:**
- `test_twitter_api_client.py` - Twitter API Clientのテスト
- `test_file_repository.py` - File Repositoryのテスト
- `test_html_validator.py` - HTML Validatorのテスト
- `test_twitter_embed_service.py` - Twitter Embed Serviceのテスト
- `test_logging_config.py` - Logging Configのテスト
- `test_retry.py` - Retry Utilityのテスト
- `test_data_pipeline.py` - Data Pipelineのテスト
- `test_data_service.py` - Data Serviceのテスト
- `test_settings.py` - Settingsのテスト
- `test_validators.py` - Validatorsのテスト
- `test_edge_cases.py` - エッジケースのテスト

### プロパティベーステスト（tests/property/）

普遍的な性質を多数のランダム入力で検証するテストです。Hypothesisライブラリを使用して、最低100回の反復実行を行います。

**テストファイル:**
- `test_twitter_api_client_properties.py` - Twitter API Clientのプロパティテスト
- `test_file_repository_properties.py` - File Repositoryのプロパティテスト
- `test_html_validator_properties.py` - HTML Validatorのプロパティテスト
- `test_twitter_embed_service_properties.py` - Twitter Embed Serviceのプロパティテスト
- `test_logging_config_properties.py` - Logging Configのプロパティテスト
- `test_retry_properties.py` - Retry Utilityのプロパティテスト
- `test_data_pipeline_properties.py` - Data Pipelineのプロパティテスト
- `test_data_service_properties.py` - Data Serviceのプロパティテスト
- `test_settings_properties.py` - Settingsのプロパティテスト

### テストフィクスチャ（tests/fixtures/）

再利用可能なテストデータとヘルパー関数を提供します。

**フィクスチャファイル:**
- `sample_html.py` - サンプルHTML（Twitter埋め込みコード）
- `sample_data.py` - サンプルデータ（TSVデータ）
- `mock_responses.py` - モックレスポンス（API応答）

### 環境構築動作確認テスト

Docker Composeで構築した環境が正しく動作することを確認するテストです。

**検証内容:**
- アプリケーションが正常に起動すること（要件10.1）
- データ読み込みが正常に動作すること（要件10.2）
- 基本機能（検索、ページ遷移）が動作すること（要件10.3）
- データ整合性が保たれていること（要件10.4）
- 環境分離が正しく機能していること（要件2.4, 14.5）
- 本番環境との整合性（要件13.1〜13.5）

### その他のテスト

- `tests/unit/test_utils.py` - ユーティリティ関数のテスト
- `tests/unit/test_search_service.py` - 検索サービスのテスト
- `tests/unit/test_config.py` - 設定管理のテスト
- `tests/unit/test_errors.py` - エラーハンドリングのテスト
- `tests/unit/test_fixtures.py` - フィクスチャのテスト

## テストの実行方法

### Docker Compose環境でのテスト実行（推奨）

**重要**: すべてのPythonコマンドは、Dockerコンテナ内で実行してください。

1. **Dockerコンテナを起動**

```bash
docker-compose up -d
```

2. **全てのテストを実行**

```bash
docker-compose exec shinouta-time pytest tests/ -v
```

3. **ユニットテストのみ実行**

```bash
docker-compose exec shinouta-time pytest tests/unit/ -v
```

4. **プロパティベーステストのみ実行**

```bash
docker-compose exec shinouta-time pytest tests/property/ -v
```

5. **特定のテストファイルを実行**

```bash
# Twitter API Clientのユニットテスト
docker-compose exec shinouta-time pytest tests/unit/test_twitter_api_client.py -v

# File Repositoryのプロパティテスト
docker-compose exec shinouta-time pytest tests/property/test_file_repository_properties.py -v

# 環境構築動作確認テスト
docker-compose exec shinouta-time pytest tests/integration/test_environment_verification.py -v
```

6. **詳細なテスト結果を表示**

```bash
docker-compose exec shinouta-time pytest tests/ -v -s
```

7. **特定のテストクラスのみ実行**

```bash
# Twitter API Clientのテストクラス
docker-compose exec shinouta-time pytest tests/unit/test_twitter_api_client.py::TestTwitterAPIClient -v

# File Repositoryのプロパティテストクラス
docker-compose exec shinouta-time pytest tests/property/test_file_repository_properties.py::TestFileRepositoryProperties -v
```

8. **特定のテストメソッドのみ実行**

```bash
docker-compose exec shinouta-time pytest tests/unit/test_twitter_api_client.py::TestTwitterAPIClient::test_get_oembed_success -v
```

9. **カバレッジレポート付きで実行**

```bash
# ターミナルに表示
docker-compose exec shinouta-time pytest tests/ --cov=src --cov-report=term-missing -v

# HTML形式のレポートを生成
docker-compose exec shinouta-time pytest tests/ --cov=src --cov-report=html -v
```

10. **カバレッジレポートの確認**

HTML形式のカバレッジレポートは `htmlcov/index.html` に生成されます。ブラウザで開いて確認してください。

```bash
# Windowsの場合
start htmlcov/index.html

# macOS/Linuxの場合
open htmlcov/index.html
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
pytest tests/integration/test_environment_verification.py -v
```

## テスト結果の見方

### 成功例

```
tests/integration/test_environment_verification.py::TestEnvironmentVerification::test_data_files_exist PASSED
tests/integration/test_environment_verification.py::TestEnvironmentVerification::test_python_version PASSED
tests/integration/test_environment_verification.py::TestEnvironmentVerification::test_load_lives_data PASSED
...
```

全てのテストが`PASSED`と表示されれば、環境構築は成功です。

### 失敗例

```
tests/integration/test_environment_verification.py::TestEnvironmentVerification::test_data_files_exist FAILED
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

### カバレッジレポートの見方

カバレッジレポート（`htmlcov/index.html`）では、以下の情報を確認できます：

- **全体カバレッジ**: プロジェクト全体のカバレッジ率
- **モジュール別カバレッジ**: 各Pythonファイルのカバレッジ率
- **未カバー行**: テストされていないコード行
- **カバー行**: テストされているコード行

**カバレッジの色分け:**
- 緑色: カバーされている行
- 赤色: カバーされていない行
- 黄色: 部分的にカバーされている行（分岐の一部のみ）

### 最新のテスト結果

詳細は `docs/testing/test_results_summary.md` を参照してください。

## 主要モジュールのテスト詳細

### Twitter API Client（要件1）

**ユニットテスト（tests/unit/test_twitter_api_client.py）:**
- 有効なURLでのAPI呼び出し
- 無効なURLのエラーハンドリング
- レート制限の処理
- ネットワークエラーの処理
- タイムアウトの処理

**プロパティテスト（tests/property/test_twitter_api_client_properties.py）:**
- プロパティ1: 有効なURL処理の一貫性
- プロパティ2: 無効なURL拒否の一貫性
- プロパティ3: ネットワークエラーの適切な処理

### File Repository（要件2）

**ユニットテスト（tests/unit/test_file_repository.py）:**
- ファイルの読み込み
- ファイルの書き込み
- 存在しないファイルの処理
- バックアップの作成
- 権限エラーの処理

**プロパティテスト（tests/property/test_file_repository_properties.py）:**
- プロパティ4: ファイル読み書きのラウンドトリップ
- プロパティ5: バックアップの一貫性

### HTML Validator（要件3）

**ユニットテスト（tests/unit/test_html_validator.py）:**
- 有効なTwitter埋め込みHTMLの検証
- 無効なHTMLの検証
- 空のHTMLの処理
- タグの不一致検出

**プロパティテスト（tests/property/test_html_validator_properties.py）:**
- プロパティ6: 有効なHTML検証の一貫性
- プロパティ7: 無効なHTML検証の一貫性

### Twitter Embed Service（要件4）

**ユニットテスト（tests/unit/test_twitter_embed_service.py）:**
- 埋め込みコードの取得
- 埋め込みコードの保存
- 埋め込みコードの読み込み
- エラー処理

**プロパティテスト（tests/property/test_twitter_embed_service_properties.py）:**
- プロパティ8: 埋め込みコード取得の一貫性
- プロパティ9: 埋め込みコード保存のラウンドトリップ
- プロパティ10: エラー処理の一貫性

### Logging Config（要件5）

**ユニットテスト（tests/unit/test_logging_config.py）:**
- ロガーの設定
- ファイルロギングの有効化
- ログローテーションの設定
- ログフォーマットの設定

**プロパティテスト（tests/property/test_logging_config_properties.py）:**
- プロパティ11: ログレベル設定の一貫性
- プロパティ12: ログフォーマットの一貫性

### Retry Utility（要件6）

**ユニットテスト（tests/unit/test_retry.py）:**
- リトライ回数の検証
- リトライ後の成功
- すべてのリトライ失敗
- 指数バックオフの検証

**プロパティテスト（tests/property/test_retry_properties.py）:**
- プロパティ13: リトライ回数の一貫性
- プロパティ14: 指数バックオフの一貫性
- プロパティ15: 例外フィルタリングの一貫性

### Data Pipeline（要件7）

**ユニットテスト（tests/unit/test_data_pipeline.py）:**
- パイプライン実行
- キャッシュ機能
- エラー処理

**プロパティテスト（tests/property/test_data_pipeline_properties.py）:**
- プロパティ16: エラー処理の一貫性

### Data Service（要件8）

**ユニットテスト（tests/unit/test_data_service.py）:**
- データの読み込み
- データの結合
- エラー処理

**プロパティテスト（tests/property/test_data_service_properties.py）:**
- プロパティ17: データ読み込みの一貫性
- プロパティ18: データ結合の一貫性
- プロパティ19: エラー処理の一貫性
- プロパティ20: 欠損値処理の一貫性

### Settings（要件9）

**ユニットテスト（tests/unit/test_settings.py）:**
- 環境変数の読み込み
- デフォルト値の使用
- 無効な値の検証
- パスの解決

**プロパティテスト（tests/property/test_settings_properties.py）:**
- プロパティ21: 環境変数読み込みの一貫性
- プロパティ22: 無効な値検証の一貫性
- プロパティ23: パス解決の一貫性
- プロパティ24: 設定更新の一貫性

## 継続的な動作確認

環境構築後、以下のタイミングでテストを実行することを推奨します：

1. **初回環境構築後**: 全てのテストを実行して環境が正しく構築されたことを確認
2. **依存パッケージ更新後**: requirements.txt更新後にテストを実行
3. **データファイル更新後**: data/ディレクトリのTSVファイル更新後にテストを実行
4. **コード変更後**: 主要な機能を変更した後にテストを実行
5. **プルリクエスト作成前**: 全てのテストが成功することを確認
6. **カバレッジ確認**: 定期的にカバレッジレポートを確認し、70%以上を維持

## テストの拡張

新しい機能を追加した場合、対応するテストを追加してください：

### 1. ユニットテストの追加

適切なテストファイル（`tests/unit/`）に新しいテストメソッドを追加します：

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

### 2. プロパティベーステストの追加

普遍的な性質を検証する場合は、プロパティテスト（`tests/property/`）を追加します：

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_property_new_feature(content):
    """
    Feature: feature-name, Property X: プロパティの説明
    
    すべての有効な入力に対して、特定の性質が保たれることを確認
    """
    result = function_to_test(content)
    assert property_holds(result), "プロパティ違反"
```

**プロパティテストの設定:**
- 最低100回の反復実行（`@settings(max_examples=100)`）
- タイムアウト: 各テスト5秒以内
- 設計書の正確性プロパティを参照してテストを作成

### 3. 新しいテストファイルを作成する場合

新しいモジュールをテストする場合は、新しいテストファイルを作成します：

**ユニットテスト（tests/unit/test_new_module.py）:**
```python
"""
新モジュールのユニットテスト

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

**プロパティテスト（tests/property/test_new_module_properties.py）:**
```python
"""
新モジュールのプロパティベーステスト

src/path/to/new_module.pyの普遍的な性質を検証するテストです。
"""

from hypothesis import given, strategies as st, settings
from src.path.to.new_module import NewClass


class TestNewClassProperties:
    """NewClassのプロパティテスト"""
    
    @given(st.text())
    @settings(max_examples=100)
    def test_property_consistency(self, input_data):
        """
        Feature: feature-name, Property 1: 一貫性の検証
        
        すべての入力に対して、一貫した動作をすることを確認
        """
        instance = NewClass()
        result = instance.method(input_data)
        assert result is not None
```

### 4. テストのベストプラクティス

**ユニットテスト:**
- **明確なテスト名**: テストメソッド名は何をテストしているか明確にする
- **1テスト1検証**: 各テストメソッドは1つの機能を検証する
- **独立性**: テストは他のテストに依存しない
- **再現性**: 同じ入力で常に同じ結果を返す
- **高速**: テストは可能な限り高速に実行される
- **日本語docstring**: 検証内容を日本語で記述する
- **要件参照**: docstringに要件番号を記載する

**プロパティベーステスト:**
- **普遍的な性質**: すべての入力に対して成り立つ性質を検証する
- **最低100回反復**: `@settings(max_examples=100)`を設定する
- **Feature参照**: docstringに`Feature: feature-name, Property X:`を記載する
- **適切なジェネレータ**: 入力ドメインを正しく制約する
- **明確なプロパティ**: 何を検証しているか明確にする

### 5. テストフィクスチャの追加

再利用可能なテストデータは、`tests/fixtures/`に追加します：

```python
# tests/fixtures/sample_new_data.py
"""新しいテストデータのフィクスチャ"""

SAMPLE_NEW_DATA = {
    "key1": "value1",
    "key2": "value2",
}
```
