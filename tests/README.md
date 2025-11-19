# テストガイド

このディレクトリには、「しのうたタイム」アプリケーションの動作確認テストが含まれています。

## テストの種類

### 環境構築動作確認テスト（test_environment_verification.py）

Docker Composeで構築した環境が正しく動作することを確認するテストです。

**検証内容:**
- アプリケーションが正常に起動すること（要件10.1）
- データ読み込みが正常に動作すること（要件10.2）
- 基本機能（検索、ページ遷移）が動作すること（要件10.3）
- データ整合性が保たれていること（要件10.4）
- 環境分離が正しく機能していること（要件2.4, 14.5）
- 本番環境との整合性（要件13.1〜13.5）

## テストの実行方法

### Docker Compose環境でのテスト実行

1. **Dockerコンテナを起動**

```bash
docker-compose up -d
```

2. **コンテナ内でテストを実行**

```bash
docker-compose exec shinouta-time pytest tests/test_environment_verification.py -v
```

3. **詳細なテスト結果を表示**

```bash
docker-compose exec shinouta-time pytest tests/test_environment_verification.py -v -s
```

4. **特定のテストクラスのみ実行**

```bash
# 環境構築動作確認テストのみ
docker-compose exec shinouta-time pytest tests/test_environment_verification.py::TestEnvironmentVerification -v

# 環境分離確認テストのみ
docker-compose exec shinouta-time pytest tests/test_environment_verification.py::TestEnvironmentIsolation -v

# 本番環境整合性確認テストのみ
docker-compose exec shinouta-time pytest tests/test_environment_verification.py::TestProductionParity -v
```

5. **特定のテストメソッドのみ実行**

```bash
docker-compose exec shinouta-time pytest tests/test_environment_verification.py::TestEnvironmentVerification::test_search_functionality -v
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

## 継続的な動作確認

環境構築後、以下のタイミングでテストを実行することを推奨します：

1. **初回環境構築後**: 全てのテストを実行して環境が正しく構築されたことを確認
2. **依存パッケージ更新後**: requirements.txt更新後にテストを実行
3. **データファイル更新後**: data/ディレクトリのTSVファイル更新後にテストを実行
4. **コード変更後**: 主要な機能を変更した後にテストを実行

## テストの拡張

新しい機能を追加した場合、対応するテストを追加してください：

1. `tests/test_environment_verification.py`に新しいテストメソッドを追加
2. テストメソッド名は`test_`で始める
3. docstringで検証内容と要件番号を記載
4. assertを使用して期待値を検証

例:
```python
def test_new_feature(self, data_pipeline):
    """
    新機能が正常に動作することを確認
    
    要件XX.X: 新機能の動作確認
    """
    # テストコード
    assert expected == actual, "エラーメッセージ"
```
