# Twitter API認証情報管理

## 概要

Twitter埋め込みコード取得システムの認証情報管理機能について説明します。

## 認証情報の設定

### 環境変数

以下の環境変数を設定することで、Twitter API認証情報を管理できます：

```bash
# Twitter API認証情報（将来の拡張用）
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
```

### .envファイル

`.env`ファイルに認証情報を記載することで、環境変数として読み込まれます：

```bash
# .envファイルの例
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
```

**重要**: `.env`ファイルは`.gitignore`に含まれており、Gitリポジトリにコミットされません。

## 使用方法

### 基本的な使用

```python
from src.config.settings import TwitterAPICredentials, TwitterEmbedConfig

# 認証情報を読み込む
credentials = TwitterAPICredentials.from_env()

# 認証情報が設定されているか確認
if credentials.is_configured():
    print("認証情報が設定されています")
else:
    print("認証情報が設定されていません")

# Twitter埋め込み設定を読み込む（認証情報を含む）
config = TwitterEmbedConfig.from_env()
```

### 認証情報の検証

```python
from src.config.settings import TwitterAPICredentials
from src.exceptions.errors import ConfigurationError

credentials = TwitterAPICredentials.from_env()

try:
    # 認証情報を必須としない検証
    credentials.validate(require_credentials=False)
    print("検証成功")
except ConfigurationError as e:
    print(f"検証失敗: {e}")

try:
    # 認証情報を必須とする検証
    credentials.validate(require_credentials=True)
    print("認証情報が正しく設定されています")
except ConfigurationError as e:
    print(f"認証情報が設定されていません: {e}")
```

## セキュリティ機能

### 1. ログ非出力

認証情報は、ログやエラーメッセージに出力されません：

```python
credentials = TwitterAPICredentials.from_env()

# 文字列表現では認証情報がマスクされる
print(credentials)  # 出力: TwitterAPICredentials(api_key=***, api_secret=***)
print(str(credentials))  # 出力: TwitterAPICredentials(api_key=***, api_secret=***)
print(repr(credentials))  # 出力: TwitterAPICredentials(api_key=***, api_secret=***)

# マスクされた認証情報を取得
masked = credentials.mask_credentials()
print(masked)  # 出力: {'api_key': '***', 'api_secret': '***', 'is_configured': True}
```

### 2. 環境変数からの読み込み

認証情報はハードコーディングされず、環境変数から読み込まれます。

### 3. .gitignoreによる保護

`.env`ファイルは`.gitignore`に含まれており、誤ってコミットされることを防ぎます。

## エラーハンドリング

### 認証情報が設定されていない場合

```python
from src.config.settings import TwitterAPICredentials
from src.exceptions.errors import ConfigurationError

credentials = TwitterAPICredentials.from_env()

try:
    # 認証情報を必須とする検証
    credentials.validate(require_credentials=True)
except ConfigurationError as e:
    print(f"エラー: {e}")
    # 出力例: エラー: 設定エラー (TWITTER_API_KEY): Twitter API認証キーが設定されていません。環境変数TWITTER_API_KEYを設定してください。
```

### 認証情報の形式が不正な場合

```python
import os
from src.config.settings import TwitterAPICredentials
from src.exceptions.errors import ConfigurationError

# 空文字列を設定
os.environ["TWITTER_API_KEY"] = "   "
os.environ["TWITTER_API_SECRET"] = "valid_secret"

credentials = TwitterAPICredentials.from_env()

try:
    credentials.validate(require_credentials=False)
except ConfigurationError as e:
    print(f"エラー: {e}")
    # 出力例: エラー: 設定エラー (TWITTER_API_KEY): Twitter API認証キーの形式が不正です
```

## Twitter oEmbed APIについて

**注意**: 現在使用しているTwitter oEmbed APIは認証不要です。認証情報の管理機能は、将来の拡張（認証が必要なAPIの使用など）のために実装されています。

認証情報が設定されていない場合でも、警告メッセージが表示されるのみで、処理は継続されます。

## 設定クラス

### TwitterAPICredentials

Twitter API認証情報を管理するクラス。

**属性**:
- `api_key`: APIキー（オプション）
- `api_secret`: APIシークレット（オプション）

**メソッド**:
- `from_env()`: 環境変数から認証情報を読み込む
- `validate(require_credentials=False)`: 認証情報を検証する
- `is_configured()`: 認証情報が設定されているか確認
- `mask_credentials()`: マスクされた認証情報を取得

### TwitterEmbedConfig

Twitter埋め込みコード取得システムの設定を管理するクラス。

**属性**:
- `embed_code_path`: 埋め込みコードファイルのパス
- `height_path`: 高さ設定ファイルのパス
- `backup_dir`: バックアップディレクトリ
- `log_level`: ログレベル
- `log_file`: ログファイルのパス
- `max_retries`: 最大リトライ回数
- `retry_delay`: リトライ遅延時間
- `api_timeout`: APIタイムアウト
- `default_height`: デフォルト高さ
- `credentials`: 認証情報（TwitterAPICredentials）

**メソッド**:
- `from_env()`: 環境変数から設定を読み込む
- `validate(require_credentials=False)`: 設定を検証する

## 関連ファイル

- `src/config/settings.py`: 認証情報管理の実装
- `.env.example`: 環境変数の設定例
- `src/exceptions/errors.py`: エラークラスの定義

## 要件との対応

- **要件5.1**: 環境変数からの認証情報読み込み ✓
- **要件5.2**: 認証情報未設定時のエラーメッセージ ✓
- **要件5.3**: .envファイルを使用した認証情報管理 ✓
- **要件5.4**: 認証情報のログ非出力 ✓
- **要件5.5**: 認証情報のハードコーディング禁止 ✓
