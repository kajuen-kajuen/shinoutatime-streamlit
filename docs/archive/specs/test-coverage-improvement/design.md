# 設計書

## 概要

本設計書は、「しのうたタイム」プロジェクトのテストカバレッジを38%から70%以上に向上させるための包括的なテスト戦略を定義します。現在カバレッジが低いモジュール（Twitter API Client、File Repository、HTML Validator、Logging Config、Retry Utility、Data Pipeline、Data Service、Settings）に対して、ユニットテストとプロパティベーステストを追加します。

## アーキテクチャ

### テスト構造

```
tests/
├── unit/                          # ユニットテスト
│   ├── test_twitter_api_client.py
│   ├── test_file_repository.py
│   ├── test_html_validator.py
│   ├── test_twitter_embed_service.py
│   ├── test_logging_config.py
│   ├── test_retry.py
│   ├── test_data_pipeline.py
│   ├── test_data_service.py
│   └── test_settings.py
├── property/                      # プロパティベーステスト
│   ├── test_twitter_api_client_properties.py
│   ├── test_file_repository_properties.py
│   ├── test_html_validator_properties.py
│   ├── test_twitter_embed_service_properties.py
│   ├── test_logging_config_properties.py
│   ├── test_retry_properties.py
│   ├── test_data_pipeline_properties.py
│   ├── test_data_service_properties.py
│   └── test_settings_properties.py
└── fixtures/                      # テストフィクスチャ
    ├── sample_html.py
    ├── sample_data.py
    └── mock_responses.py
```

### テスト戦略

1. **ユニットテスト**: 特定の動作、エッジケース、エラーハンドリングを検証
2. **プロパティベーステスト**: 普遍的な性質を多数のランダム入力で検証
3. **モックとスタブ**: 外部依存（API、ファイルシステム）を分離してテスト
4. **テストフィクスチャ**: 再利用可能なテストデータとヘルパー関数

## コンポーネントとインターフェース

### 1. Twitter API Clientテスト

**テスト対象**: `src/clients/twitter_api_client.py`

**主要なテストケース**:
- 有効なURLでのAPI呼び出し
- 無効なURLのエラーハンドリング
- レート制限の処理
- ネットワークエラーの処理
- タイムアウトの処理
- レート制限情報の更新

**モック戦略**:
- `requests.get`をモックしてAPIレスポンスをシミュレート
- 様々なHTTPステータスコード（200, 404, 429, 500）をテスト
- ネットワークエラー（ConnectionError, Timeout）をシミュレート

### 2. File Repositoryテスト

**テスト対象**: `src/repositories/file_repository.py`

**主要なテストケース**:
- ファイルの読み込み
- ファイルの書き込み
- 存在しないファイルの処理
- バックアップの作成
- 権限エラーの処理
- ディレクトリの自動作成

**テスト戦略**:
- 一時ディレクトリ（`tempfile.TemporaryDirectory`）を使用
- ファイル操作のラウンドトリップテスト
- 権限エラーのシミュレーション

### 3. HTML Validatorテスト

**テスト対象**: `src/utils/html_validator.py`

**主要なテストケース**:
- 有効なTwitter埋め込みHTMLの検証
- 無効なHTMLの検証
- 空のHTMLの処理
- タグの不一致検出
- 必須要素（blockquote、twitter-tweetクラス）の検証

**テスト戦略**:
- 様々なHTML構造パターンを生成
- 正常系と異常系の両方をカバー
- エラーメッセージの検証

### 4. Twitter Embed Serviceテスト

**テスト対象**: `src/services/twitter_embed_service.py`

**主要なテストケース**:
- 埋め込みコードの取得
- 埋め込みコードの保存
- 埋め込みコードの読み込み
- エラー処理
- バックアップの作成
- URL検証

**モック戦略**:
- `TwitterAPIClient`と`FileRepository`をモック
- 成功・失敗の両方のシナリオをテスト

### 5. Logging Configテスト

**テスト対象**: `src/config/logging_config.py`

**主要なテストケース**:
- ロガーの設定
- ファイルロギングの有効化
- ログローテーションの設定
- ログフォーマットの設定
- 複数ハンドラーの設定
- 環境変数からの設定読み込み

**テスト戦略**:
- 一時ログファイルを使用
- ログ出力の内容を検証
- ハンドラーの設定を検証

### 6. Retry Utilityテスト

**テスト対象**: `src/utils/retry.py`

**主要なテストケース**:
- リトライ回数の検証
- リトライ後の成功
- すべてのリトライ失敗
- 指数バックオフの検証
- 特定の例外のみリトライ

**テスト戦略**:
- カウンターを使ってリトライ回数を追跡
- 時間測定で指数バックオフを検証
- 様々な例外タイプをテスト

### 7. Data Pipelineテスト

**テスト対象**: `src/core/data_pipeline.py`

**主要なテストケース**:
- キャッシュの使用
- キャッシュのクリア
- エラー処理
- 空のデータ処理
- データ変換の正確性

**モック戦略**:
- `DataService`をモック
- 様々なデータセットでテスト

### 8. Data Serviceテスト

**テスト対象**: `src/services/data_service.py`

**主要なテストケース**:
- データの読み込み
- データの結合
- エラー処理
- 欠損値の処理
- データ型の変換

**テスト戦略**:
- 一時TSVファイルを作成
- 様々なデータパターンをテスト

### 9. Settingsテスト

**テスト対象**: `src/config/settings.py`

**主要なテストケース**:
- 環境変数の読み込み
- デフォルト値の使用
- 無効な値の検証
- パスの解決
- 設定の更新

**テスト戦略**:
- 環境変数を一時的に設定
- 様々な設定値パターンをテスト

## データモデル

### テストフィクスチャ

```python
# sample_html.py
VALID_TWITTER_EMBED_HTML = """
<blockquote class="twitter-tweet">
  <p>Sample tweet</p>
  <a href="https://twitter.com/user/status/123"></a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js"></script>
"""

INVALID_HTML_MISSING_BLOCKQUOTE = """
<div class="twitter-tweet">
  <p>Sample tweet</p>
</div>
"""

# sample_data.py
SAMPLE_LIVES_DATA = {
    "ID": [1, 2],
    "配信日": ["2024/01/01", "2024/01/02"],
    "タイトル": ["配信1", "配信2"],
    "URL": ["https://youtube.com/watch?v=abc", "https://youtube.com/watch?v=def"]
}

SAMPLE_SONGS_DATA = {
    "ID": [1, 2, 3],
    "LIVE_ID": [1, 1, 2],
    "曲名": ["曲A", "曲B", "曲C"],
    "タイムスタンプ": ["00:10", "05:30", "02:15"]
}
```

## 正確性プロパティ

*プロパティとは、システムのすべての有効な実行において真であるべき特性や動作のことです。プロパティは、人間が読める仕様と機械で検証可能な正確性保証の橋渡しをします。*

### Twitter API Client

**プロパティ1: 有効なURL処理の一貫性**
*すべての*有効なツイートURLに対して、API呼び出しが成功した場合、返されるHTMLは空でなく、OEmbedResponse型である
**検証: 要件1.1**

**プロパティ2: 無効なURL拒否の一貫性**
*すべての*無効なツイートURLに対して、InvalidURLErrorまたはそれに相当するエラーが発生する
**検証: 要件1.2**

**プロパティ3: ネットワークエラーの適切な処理**
*すべての*ネットワークエラー（ConnectionError、Timeout）に対して、NetworkErrorまたはAPITimeoutErrorが発生する
**検証: 要件1.4**

### File Repository

**プロパティ4: ファイル読み書きのラウンドトリップ**
*すべての*文字列コンテンツに対して、書き込んでから読み込むと元の内容と一致する
**検証: 要件2.1, 2.2**

**プロパティ5: バックアップの一貫性**
*すべての*ファイル内容に対して、バックアップを作成すると元ファイルと同じ内容のバックアップファイルが作成される
**検証: 要件2.4**

### HTML Validator

**プロパティ6: 有効なHTML検証の一貫性**
*すべての*blockquoteタグとtwitter-tweetクラスを含むHTMLに対して、検証が成功する
**検証: 要件3.1**

**プロパティ7: 無効なHTML検証の一貫性**
*すべての*blockquoteタグまたはtwitter-tweetクラスを欠くHTMLに対して、検証が失敗し、適切なエラーメッセージが返される
**検証: 要件3.2**

### Twitter Embed Service

**プロパティ8: 埋め込みコード取得の一貫性**
*すべての*有効なツイートURLに対して、埋め込みコードの取得が成功した場合、EmbedCodeResultのsuccessフィールドがTrueであり、embed_codeが空でない
**検証: 要件4.1**

**プロパティ9: 埋め込みコード保存のラウンドトリップ**
*すべての*埋め込みコードに対して、保存してから読み込むと元の内容と一致する
**検証: 要件4.2, 4.3**

**プロパティ10: エラー処理の一貫性**
*すべての*エラー状況（無効なURL、ネットワークエラー）に対して、EmbedCodeResultのsuccessフィールドがFalseであり、error_messageが空でない
**検証: 要件4.4**

### Logging Config

**プロパティ11: ログレベル設定の一貫性**
*すべての*有効なログレベル（DEBUG、INFO、WARNING、ERROR）に対して、ロガーのレベルが正しく設定される
**検証: 要件5.1**

**プロパティ12: ログフォーマットの一貫性**
*すべての*ログメッセージに対して、出力されるログは指定されたフォーマット（タイムスタンプ、レベル、メッセージ）を含む
**検証: 要件5.4**

### Retry Utility

**プロパティ13: リトライ回数の一貫性**
*すべての*リトライ回数設定に対して、失敗した処理は指定された回数だけリトライされる
**検証: 要件6.1**

**プロパティ14: 指数バックオフの一貫性**
*すべての*リトライ試行に対して、待機時間は指数的に増加する（base_delay * exponential_base^attempt）
**検証: 要件6.4**

**プロパティ15: 例外フィルタリングの一貫性**
*すべての*例外タイプに対して、指定された例外のみがリトライされ、それ以外の例外は即座に再送出される
**検証: 要件6.5**

### Data Pipeline

**プロパティ16: エラー処理の一貫性**
*すべての*エラー状況（ファイル読み込み失敗、データ変換エラー）に対して、Noneが返され、適切なエラーログが記録される
**検証: 要件7.3**

### Data Service

**プロパティ17: データ読み込みの一貫性**
*すべての*有効なTSVファイルに対して、読み込みが成功した場合、DataFrameが返され、error_messageがNoneである
**検証: 要件8.1**

**プロパティ18: データ結合の一貫性**
*すべての*配信データと楽曲データのペアに対して、結合後のデータ件数は楽曲データの件数と一致する（左結合）
**検証: 要件8.2**

**プロパティ19: エラー処理の一貫性**
*すべての*エラー状況（ファイル不存在、読み込みエラー）に対して、Noneが返され、error_messageが空でない
**検証: 要件8.3**

**プロパティ20: 欠損値処理の一貫性**
*すべての*欠損値を含むデータに対して、適切なデフォルト値が設定され、処理が継続される
**検証: 要件8.4**

### Settings

**プロパティ21: 環境変数読み込みの一貫性**
*すべての*環境変数設定に対して、設定値が正しく読み込まれ、型変換が正しく行われる
**検証: 要件9.1**

**プロパティ22: 無効な値検証の一貫性**
*すべての*無効な設定値（負の数、空文字列など）に対して、適切なバリデーションエラーが発生する
**検証: 要件9.3**

**プロパティ23: パス解決の一貫性**
*すべての*相対パスに対して、正しい絶対パスが返される
**検証: 要件9.4**

**プロパティ24: 設定更新の一貫性**
*すべての*設定値に対して、更新後の値が正しく反映され、取得できる
**検証: 要件9.5**

## エラーハンドリング

### エラー処理戦略

1. **例外の分類**:
   - ネットワークエラー: `NetworkError`, `APITimeoutError`, `RateLimitError`
   - ファイルエラー: `FileWriteError`, `FileNotFoundError`
   - データエラー: `DataLoadError`, `DataProcessingError`
   - バリデーションエラー: `InvalidURLError`, `HTMLValidationError`

2. **エラーログ**:
   - すべてのエラーは適切なログレベルで記録
   - スタックトレースを含む詳細情報を記録
   - コンテキスト情報（URL、ファイルパスなど）を含める

3. **エラーリカバリ**:
   - リトライ可能なエラーは自動的にリトライ
   - リトライ不可能なエラーは即座に失敗
   - 部分的な成功を許容（複数ツイート取得など）

### テストでのエラーハンドリング

- すべてのエラーケースをテスト
- エラーメッセージの内容を検証
- エラーログの記録を検証
- エラー後の状態を検証（リソースのクリーンアップなど）

## テスト戦略

### ユニットテスト戦略

**目的**: 特定の動作、エッジケース、エラーハンドリングを検証

**アプローチ**:
1. 各関数・メソッドに対して最低1つのテストケース
2. 正常系と異常系の両方をカバー
3. エッジケース（空文字列、None、境界値）をテスト
4. モックを使用して外部依存を分離

**カバレッジ目標**:
- 各モジュール: 60%以上
- 全体: 70%以上

### プロパティベーステスト戦略

**目的**: 普遍的な性質を多数のランダム入力で検証

**使用ライブラリ**: `hypothesis`（Pythonの標準的なプロパティベーステストライブラリ）

**アプローチ**:
1. 各正確性プロパティに対して1つのプロパティテスト
2. 最低100回の反復実行
3. ランダムな入力を生成（文字列、数値、データ構造）
4. プロパティ違反を検出した場合、最小の反例を報告

**プロパティテストの例**:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_file_write_read_roundtrip(content):
    """
    Feature: test-coverage-improvement, Property 4: ファイル読み書きのラウンドトリップ
    """
    repo = FileRepository("test.html", "test_height.txt")
    repo.write_embed_code(content)
    read_content = repo.read_embed_code()
    assert read_content == content
```

**プロパティテストの設定**:
- 各テストは最低100回実行
- タイムアウト: 各テスト5秒以内
- シード値を記録して再現可能にする

### テスト実行戦略

**実行環境**: Dockerコンテナ内

**実行コマンド**:
```bash
# すべてのテストを実行
docker-compose exec -T shinouta-time pytest tests/ -v

# カバレッジレポート付きで実行
docker-compose exec -T shinouta-time pytest --cov=src --cov-report=term-missing --cov-report=html tests/

# プロパティテストのみ実行
docker-compose exec -T shinouta-time pytest tests/property/ -v

# ユニットテストのみ実行
docker-compose exec -T shinouta-time pytest tests/unit/ -v
```

**継続的インテグレーション**:
- プルリクエスト作成時に自動実行
- カバレッジが70%未満の場合は警告
- すべてのテストが成功することを確認

### テストデータ管理

**フィクスチャの使用**:
- `pytest.fixture`を使用して再利用可能なテストデータを定義
- 一時ファイル・ディレクトリは自動的にクリーンアップ
- モックオブジェクトは各テストで独立して作成

**テストデータの分離**:
- 本番データを使用しない
- テスト用の小規模なデータセットを作成
- 一時ディレクトリを使用してファイルシステムを汚染しない

## パフォーマンス考慮事項

### テスト実行時間

**目標**: すべてのテストが5秒以内に完了

**最適化戦略**:
1. モックを使用してネットワーク呼び出しを回避
2. 小規模なテストデータを使用
3. 並列実行を検討（`pytest-xdist`）
4. 遅いテストにマーカーを付けて選択的に実行

### カバレッジ測定のオーバーヘッド

- カバレッジ測定は開発時のみ有効化
- 本番環境では無効化
- カバレッジレポートはHTML形式で保存

## セキュリティ考慮事項

### テストでのセキュリティ

1. **機密情報の保護**:
   - APIキーやトークンをテストコードに含めない
   - 環境変数を使用する場合はテスト用の値を使用
   - モックを使用して実際のAPIを呼び出さない

2. **ファイルシステムの保護**:
   - 一時ディレクトリのみを使用
   - テスト後は必ずクリーンアップ
   - 本番ファイルを上書きしない

3. **インジェクション攻撃の防止**:
   - ユーザー入力のバリデーションをテスト
   - SQLインジェクション、XSSなどの脆弱性をテスト

## 実装の優先順位

### フェーズ1: 基礎テストの追加（優先度: 高）

1. Twitter API Clientのユニットテスト
2. File Repositoryのユニットテスト
3. HTML Validatorのユニットテスト
4. Retry Utilityのユニットテスト

**目標カバレッジ**: 50%

### フェーズ2: サービス層のテスト追加（優先度: 中）

1. Twitter Embed Serviceのユニットテスト
2. Data Serviceのユニットテスト
3. Data Pipelineのユニットテスト
4. Settingsのユニットテスト

**目標カバレッジ**: 65%

### フェーズ3: プロパティベーステストの追加（優先度: 中）

1. 主要なプロパティテストの実装
2. エッジケースの追加テスト
3. Logging Configのテスト

**目標カバレッジ**: 70%以上

### フェーズ4: 統合テストとドキュメント（優先度: 低）

1. 統合テストの追加（オプション）
2. テストドキュメントの更新
3. CI/CDパイプラインへの統合

## 成功基準

1. **カバレッジ目標達成**:
   - 全体カバレッジ: 70%以上
   - 主要モジュールカバレッジ: 60%以上

2. **テスト品質**:
   - すべてのテストが成功
   - テスト実行時間: 5秒以内
   - プロパティテスト: 最低100回反復

3. **コード品質**:
   - すべてのエラーケースがテストされている
   - エッジケースがカバーされている
   - テストコードが読みやすく保守しやすい

4. **ドキュメント**:
   - テストの目的と範囲が明確
   - 実行方法が文書化されている
   - カバレッジレポートが生成されている
