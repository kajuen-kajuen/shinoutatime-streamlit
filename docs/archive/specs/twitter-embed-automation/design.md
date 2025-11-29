# 設計書

## 概要

本ドキュメントは、「しのうたタイム」アプリケーションにおけるTwitter埋め込みコード自動取得システムの設計を定義します。このシステムは、Twitter（X）のツイートURLから埋め込みコードを自動的に取得し、`data/tweet_embed_code.html`ファイルに保存する機能を提供します。

### 設計目標

1. **自動化**: 手動でのコピー&ペースト作業を排除
2. **柔軟性**: コマンドライン実行とStreamlit UI実行の両方をサポート
3. **信頼性**: エラーハンドリングとリトライ機能による堅牢な実装
4. **セキュリティ**: API認証情報の安全な管理
5. **保守性**: モジュール化された設計による拡張性の確保
6. **シンプルさ**: ローカル環境専用の機能として、複雑さを最小限に抑える

### デプロイメント環境

本システムは**ローカル環境専用**として設計されています。

- ファイルシステムへの直接書き込みが可能
- `data/tweet_embed_code.html`への保存が可能
- バックアップファイルの作成が可能
- Dockerコンテナ内での実行をサポート

## アーキテクチャ

### システム構成図

```
┌─────────────────────────────────────────────────────────┐
│                    ユーザーインターフェース層                │
├─────────────────────────────────────────────────────────┤
│  - コマンドラインインターフェース (CLI)                      │
│  - Streamlit管理画面 (UI)                                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    サービス層                              │
├─────────────────────────────────────────────────────────┤
│  - TwitterEmbedService                                   │
│    - ツイートURL解析                                      │
│    - 埋め込みコード取得                                    │
│    - ファイル保存                                         │
│    - 履歴管理                                            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    データアクセス層                         │
├─────────────────────────────────────────────────────────┤
│  - TwitterAPIClient                                      │
│    - oEmbed API呼び出し                                  │
│    - レート制限管理                                       │
│    - リトライ処理                                         │
│  - FileRepository                                        │
│    - ファイル読み書き                                     │
│    - バックアップ管理                                     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    外部サービス                            │
├─────────────────────────────────────────────────────────┤
│  - Twitter oEmbed API                                    │
│  - ファイルシステム                                       │
└─────────────────────────────────────────────────────────┘
```

### レイヤー構成

#### 1. ユーザーインターフェース層

**責務**: ユーザーからの入力を受け取り、サービス層を呼び出し、結果を表示する

- **CLI (Command Line Interface)**
  - コマンドライン引数の解析
  - 進行状況の表示
  - エラーメッセージの表示
  
- **Streamlit管理画面**
  - フォーム入力の受付
  - プレビュー表示
  - 認証・権限チェック

#### 2. サービス層

**責務**: ビジネスロジックの実装、データアクセス層の調整

- **TwitterEmbedService**
  - ツイートURL解析とバリデーション
  - 埋め込みコード取得のオーケストレーション
  - 複数ツイートの処理
  - ファイル保存とバックアップ
  - 履歴ログの記録

#### 3. データアクセス層

**責務**: 外部サービスとの通信、ファイル操作

- **TwitterAPIClient**
  - Twitter oEmbed APIとの通信
  - レート制限の管理
  - リトライロジック
  - エラーハンドリング

- **FileRepository**
  - ファイルの読み書き
  - バックアップの作成と管理
  - ファイルシステムエラーの処理

## コンポーネントとインターフェース

### 1. TwitterEmbedService

メインのビジネスロジックを担当するサービスクラス。

```python
class TwitterEmbedService:
    """
    Twitter埋め込みコード取得サービス
    
    ツイートURLから埋め込みコードを取得し、ファイルに保存する
    """
    
    def __init__(
        self,
        api_client: TwitterAPIClient,
        file_repo: FileRepository,
        logger: logging.Logger
    ):
        """
        サービスを初期化
        
        Args:
            api_client: Twitter APIクライアント
            file_repo: ファイルリポジトリ
            logger: ロガー
        """
        pass
    
    def fetch_embed_code(
        self,
        tweet_url: str
    ) -> EmbedCodeResult:
        """
        単一のツイートの埋め込みコードを取得
        
        Args:
            tweet_url: ツイートURL
            
        Returns:
            取得結果（成功/失敗、埋め込みコード、エラーメッセージ）
        """
        pass
    
    def fetch_multiple_embed_codes(
        self,
        tweet_urls: List[str]
    ) -> MultipleEmbedCodeResult:
        """
        複数のツイートの埋め込みコードを取得
        
        Args:
            tweet_urls: ツイートURLのリスト
            
        Returns:
            取得結果（成功数、失敗数、埋め込みコード、失敗リスト）
        """
        pass
    
    def save_embed_code(
        self,
        embed_code: str,
        create_backup: bool = True
    ) -> bool:
        """
        埋め込みコードをファイルに保存
        
        Args:
            embed_code: 埋め込みHTMLコード
            create_backup: バックアップを作成するか
            
        Returns:
            保存成功の可否
        """
        pass
    
    def validate_tweet_url(
        self,
        url: str
    ) -> Tuple[bool, Optional[str]]:
        """
        ツイートURLの妥当性を検証
        
        Args:
            url: 検証するURL
            
        Returns:
            (妥当性, エラーメッセージ)
        """
        pass
    
    def extract_tweet_id(
        self,
        url: str
    ) -> Optional[str]:
        """
        ツイートURLからツイートIDを抽出
        
        Args:
            url: ツイートURL
            
        Returns:
            ツイートID（抽出失敗時はNone）
        """
        pass
```

### 2. TwitterAPIClient

Twitter oEmbed APIとの通信を担当するクライアントクラス。

```python
class TwitterAPIClient:
    """
    Twitter API クライアント
    
    Twitter oEmbed APIとの通信を管理
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        APIクライアントを初期化
        
        Args:
            api_key: API認証キー（oEmbed APIでは不要だが将来の拡張用）
            max_retries: 最大リトライ回数
            retry_delay: リトライ間隔（秒）
        """
        pass
    
    def get_oembed(
        self,
        tweet_url: str,
        max_width: Optional[int] = None,
        hide_media: bool = False,
        hide_thread: bool = False
    ) -> OEmbedResponse:
        """
        oEmbed APIを使用して埋め込みコードを取得
        
        Args:
            tweet_url: ツイートURL
            max_width: 最大幅（ピクセル）
            hide_media: メディアを非表示にするか
            hide_thread: スレッドを非表示にするか
            
        Returns:
            oEmbed APIレスポンス
        """
        pass
    
    def check_rate_limit(self) -> RateLimitInfo:
        """
        レート制限の状態を確認
        
        Returns:
            レート制限情報（残り回数、リセット時刻）
        """
        pass
```

### 3. FileRepository

ファイル操作を担当するリポジトリクラス。

```python
class FileRepository:
    """
    ファイルリポジトリ
    
    埋め込みコードファイルの読み書きとバックアップを管理
    """
    
    def __init__(
        self,
        embed_code_path: str,
        height_path: str,
        backup_dir: str = "data/backups"
    ):
        """
        リポジトリを初期化
        
        Args:
            embed_code_path: 埋め込みコードファイルのパス
            height_path: 高さ設定ファイルのパス
            backup_dir: バックアップディレクトリ
        """
        pass
    
    def read_embed_code(self) -> Optional[str]:
        """
        埋め込みコードを読み込む
        
        Returns:
            埋め込みコード（ファイルが存在しない場合はNone）
        """
        pass
    
    def write_embed_code(
        self,
        content: str
    ) -> bool:
        """
        埋め込みコードを書き込む
        
        Args:
            content: 書き込む内容
            
        Returns:
            書き込み成功の可否
        """
        pass
    
    def create_backup(self) -> Optional[str]:
        """
        現在のファイルのバックアップを作成
        
        Returns:
            バックアップファイルのパス（失敗時はNone）
        """
        pass
    
    def write_height(
        self,
        height: int
    ) -> bool:
        """
        表示高さを書き込む
        
        Args:
            height: 高さ（ピクセル）
            
        Returns:
            書き込み成功の可否
        """
        pass
    
    def read_height(
        self,
        default: int = 850
    ) -> int:
        """
        表示高さを読み込む
        
        Args:
            default: デフォルト値
            
        Returns:
            高さ（ピクセル）
        """
        pass
```

### 4. CLIインターフェース

コマンドライン実行用のインターフェース。

```python
def main():
    """
    CLIのメインエントリーポイント
    """
    parser = argparse.ArgumentParser(
        description="Twitter埋め込みコード自動取得ツール"
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="ツイートURL（複数指定可能）"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="data/tweet_embed_code.html",
        help="出力ファイルパス"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="バックアップを作成しない"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="詳細ログを表示"
    )
    
    args = parser.parse_args()
    
    # サービスの初期化と実行
    # ...
```

### 5. Streamlit管理画面

Streamlitアプリケーション内の管理画面（ローカル環境専用）。

```python
def render_twitter_embed_admin():
    """
    Twitter埋め込みコード管理画面を表示
    """
    st.header("Twitter埋め込みコード管理")
    
    # 認証チェック
    if not check_admin_auth():
        st.error("管理者権限が必要です")
        return
    
    # URL入力フォーム
    with st.form("tweet_url_form"):
        tweet_urls = st.text_area(
            "ツイートURL（1行に1つ）",
            height=150,
            help="複数のツイートを指定する場合は、1行に1つずつ入力してください"
        )
        
        create_backup = st.checkbox(
            "バックアップを作成",
            value=True
        )
        
        submitted = st.form_submit_button("取得")
    
    if submitted:
        # ローカルファイルに直接書き込み
        update_local_file(tweet_urls, create_backup)
```

## データモデル

### EmbedCodeResult

単一のツイート取得結果を表すデータクラス。

```python
@dataclass
class EmbedCodeResult:
    """埋め込みコード取得結果"""
    success: bool
    tweet_url: str
    embed_code: Optional[str] = None
    height: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
```

### MultipleEmbedCodeResult

複数のツイート取得結果を表すデータクラス。

```python
@dataclass
class MultipleEmbedCodeResult:
    """複数の埋め込みコード取得結果"""
    total_count: int
    success_count: int
    failure_count: int
    combined_embed_code: str
    max_height: int
    results: List[EmbedCodeResult]
    failed_urls: List[str]
```

### OEmbedResponse

Twitter oEmbed APIのレスポンスを表すデータクラス。

```python
@dataclass
class OEmbedResponse:
    """oEmbed APIレスポンス"""
    html: str
    width: Optional[int] = None
    height: Optional[int] = None
    type: str = "rich"
    version: str = "1.0"
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    provider_name: str = "Twitter"
    provider_url: str = "https://twitter.com"
    cache_age: Optional[int] = None
```

### RateLimitInfo

APIレート制限情報を表すデータクラス。

```python
@dataclass
class RateLimitInfo:
    """レート制限情報"""
    limit: int
    remaining: int
    reset_time: datetime
```

## 正確性プロパティ

*プロパティとは、システムの全ての有効な実行において真であるべき特性や動作のことです。プロパティは、人間が読める仕様と機械で検証可能な正確性保証の橋渡しとなります。*

### プロパティ1: ツイートID抽出の一貫性

*任意の*有効なツイートURL（twitter.com、x.com、モバイル版など）に対して、システムはツイートIDを正しく抽出できる

**検証要件: 1.1**

### プロパティ2: ファイル保存のラウンドトリップ

*任意の*有効な埋め込みHTMLコードに対して、ファイルに保存した後に読み込むと、元のコードと同じ内容が得られる

**検証要件: 1.3**

### プロパティ3: エラー時のファイル不変性

*任意の*エラー状況において、既存のファイルは変更されない

**検証要件: 1.4**

### プロパティ4: 無効URL拒否の完全性

*任意の*無効なツイートURL（空文字列、不正な形式、他サイトのURLなど）に対して、システムは検証エラーを返す

**検証要件: 1.5**

### プロパティ5: 複数URL処理の完全性

*任意の*ツイートURLのリストに対して、システムは全てのURLを処理する

**検証要件: 2.1**

### プロパティ6: 埋め込みコード連結の完全性

*任意の*埋め込みコードのリストに対して、連結後のファイルには全てのコードが含まれる

**検証要件: 2.2**

### プロパティ7: 部分的失敗時の正確性

*任意の*成功と失敗が混在するケースにおいて、成功したツイートのみが保存され、失敗リストが正確である

**検証要件: 2.3**

### プロパティ8: コマンドライン引数解析の正確性

*任意の*有効なコマンドライン引数パターンに対して、システムは正しく解析する

**検証要件: 3.1**

### プロパティ9: 進行状況出力の一貫性

*任意の*処理実行において、進行状況がコンソールに出力される

**検証要件: 3.3**

### プロパティ10: 成功時の終了コード

*任意の*成功ケースにおいて、システムは終了コード0を返す

**検証要件: 3.4**

### プロパティ11: 失敗時の終了コード

*任意の*失敗ケースにおいて、システムは非ゼロの終了コードを返す

**検証要件: 3.5**

### プロパティ12: 認証情報のアクセス制御

*任意の*アクセスにおいて、システムは認証と権限チェックを実施する

**検証要件: 4.5**

### プロパティ13: 環境変数からの認証情報読み込み

*任意の*APIアクセスにおいて、システムは環境変数から認証情報を読み込む

**検証要件: 5.1**

### プロパティ14: 認証情報のログ非出力

*任意の*ログ出力において、認証情報は含まれない

**検証要件: 5.4**

### プロパティ15: HTML検証の実行

*任意の*埋め込みコード取得において、システムはHTMLコードの基本的な検証を実行する

**検証要件: 6.1**

### プロパティ16: 不正HTML検出の完全性

*任意の*不正なHTMLコードに対して、システムは警告メッセージを表示する

**検証要件: 6.2**

### プロパティ17: バックアップ作成の一貫性

*任意の*保存操作において、システムは既存ファイルのバックアップを作成する

**検証要件: 6.3**

### プロパティ18: 取得操作のログ記録

*任意の*埋め込みコード取得操作において、取得日時、ツイートURL、成功/失敗がログに記録される

**検証要件: 7.1**

### プロパティ19: 代替手段使用のログ記録

*任意の*代替手段使用時において、使用した方法がログに記録される

**検証要件: 8.2**

### プロパティ20: 表示高さ取得の一貫性

*任意の*埋め込みコード取得において、システムはツイートの推奨表示高さを取得する

**検証要件: 9.1**

### プロパティ21: 表示高さ保存のラウンドトリップ

*任意の*表示高さ値に対して、ファイルに保存した後に読み込むと、元の値と同じ値が得られる

**検証要件: 9.2**

### プロパティ22: 最大高さ選択の正確性

*任意の*複数の高さ値のリストに対して、システムは最大値を選択する

**検証要件: 9.4**

### プロパティ23: ネットワークエラーのリトライ

*任意の*ネットワークエラーにおいて、システムはリトライを実行する

**検証要件: 10.1**

### プロパティ24: ファイルエラーの適切な処理

*任意の*ファイルシステムエラーにおいて、システムは適切に処理する

**検証要件: 10.3**

### プロパティ25: 予期しないエラーのログ記録

*任意の*予期しないエラーにおいて、詳細なエラー情報がログに記録され、ユーザーには分かりやすいメッセージが表示される

**検証要件: 10.4**

### プロパティ26: 全エラーのログ記録

*任意の*エラーにおいて、適切にログに記録される

**検証要件: 10.5**



## エラーハンドリング

### エラー分類

システムは以下のエラーカテゴリを定義します：

#### 1. 入力検証エラー

- **InvalidURLError**: 無効なツイートURL形式
- **EmptyURLError**: 空のURL入力
- **InvalidTweetIDError**: ツイートIDの抽出失敗

**処理方針**: ユーザーに分かりやすいエラーメッセージを表示し、処理を中断

#### 2. API通信エラー

- **NetworkError**: ネットワーク接続エラー
- **APITimeoutError**: APIタイムアウト
- **RateLimitError**: APIレート制限超過
- **APIResponseError**: API応答エラー

**処理方針**: リトライ機能を提供し、最大リトライ回数に達したら失敗として処理

#### 3. ファイルシステムエラー

- **FileNotFoundError**: ファイルが見つからない
- **FilePermissionError**: ファイルアクセス権限エラー
- **DiskFullError**: ディスク容量不足
- **FileWriteError**: ファイル書き込みエラー

**処理方針**: 詳細なエラー情報をログに記録し、ユーザーには対処方法を含むメッセージを表示

#### 4. 認証エラー

- **MissingCredentialsError**: 認証情報が設定されていない
- **InvalidCredentialsError**: 認証情報が無効
- **AuthenticationError**: 認証失敗

**処理方針**: セキュリティを考慮し、詳細な情報は表示せず、設定方法を案内

#### 5. データ検証エラー

- **InvalidHTMLError**: 不正なHTML形式
- **EmptyResponseError**: 空のAPI応答
- **MalformedResponseError**: 不正なAPI応答形式

**処理方針**: 警告メッセージを表示し、可能であれば処理を継続

### エラーハンドリング戦略

#### リトライロジック

```python
class RetryStrategy:
    """リトライ戦略"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        """
        リトライ戦略を初期化
        
        Args:
            max_retries: 最大リトライ回数
            base_delay: 基本遅延時間（秒）
            max_delay: 最大遅延時間（秒）
            exponential_base: 指数バックオフの基数
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def calculate_delay(self, attempt: int) -> float:
        """
        リトライ遅延時間を計算（指数バックオフ）
        
        Args:
            attempt: 試行回数（0から開始）
            
        Returns:
            遅延時間（秒）
        """
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)
```

#### エラーログ記録

全てのエラーは以下の情報と共にログに記録されます：

- タイムスタンプ
- エラータイプ
- エラーメッセージ
- スタックトレース（予期しないエラーの場合）
- コンテキスト情報（ツイートURL、処理ステップなど）

```python
def log_error(
    error: Exception,
    context: Dict[str, Any],
    logger: logging.Logger
) -> None:
    """
    エラーをログに記録
    
    Args:
        error: 発生したエラー
        context: コンテキスト情報
        logger: ロガー
    """
    logger.error(
        f"エラーが発生しました: {type(error).__name__}",
        extra={
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        },
        exc_info=True
    )
```

## テスト戦略

### テストアプローチ

本システムは、ユニットテストとプロパティベーステストの両方を使用して包括的なテストカバレッジを実現します。

#### ユニットテスト

**目的**: 個別のコンポーネントの正しい動作を検証

**対象**:
- URL解析ロジック
- ファイル読み書き操作
- エラーハンドリング
- 設定読み込み

**ツール**: pytest

**例**:
```python
def test_extract_tweet_id_from_standard_url():
    """標準的なツイートURLからIDを抽出できることを確認"""
    service = TwitterEmbedService(...)
    url = "https://twitter.com/user/status/1234567890"
    tweet_id = service.extract_tweet_id(url)
    assert tweet_id == "1234567890"

def test_save_embed_code_creates_backup():
    """埋め込みコード保存時にバックアップが作成されることを確認"""
    file_repo = FileRepository(...)
    embed_code = "<blockquote>...</blockquote>"
    result = file_repo.write_embed_code(embed_code)
    assert result is True
    assert os.path.exists("data/backups/tweet_embed_code_*.html")
```

#### プロパティベーステスト

**目的**: 全ての入力に対してプロパティが成り立つことを検証

**対象**:
- URL解析の一貫性
- ファイル操作のラウンドトリップ
- エラー時の不変性
- 複数データ処理の完全性

**ツール**: Hypothesis（Pythonのプロパティベーステストライブラリ）

**設定**: 各プロパティテストは最低100回の反復を実行

**例**:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_property_file_save_roundtrip(embed_code: str):
    """
    プロパティ2: ファイル保存のラウンドトリップ
    
    Feature: twitter-embed-automation, Property 2: ファイル保存のラウンドトリップ
    """
    file_repo = FileRepository(...)
    
    # 保存
    file_repo.write_embed_code(embed_code)
    
    # 読み込み
    loaded_code = file_repo.read_embed_code()
    
    # 元のコードと同じであることを確認
    assert loaded_code == embed_code

@given(st.lists(st.integers(min_value=100, max_value=2000), min_size=1))
def test_property_max_height_selection(heights: List[int]):
    """
    プロパティ22: 最大高さ選択の正確性
    
    Feature: twitter-embed-automation, Property 22: 最大高さ選択の正確性
    """
    service = TwitterEmbedService(...)
    
    # 複数の高さから最大値を選択
    selected_height = service.select_max_height(heights)
    
    # 選択された高さがリストの最大値であることを確認
    assert selected_height == max(heights)
```

### テストカバレッジ目標

- **コードカバレッジ**: 80%以上
- **プロパティカバレッジ**: 全ての正確性プロパティに対応するテストを実装
- **エッジケースカバレッジ**: 主要なエラーケースをカバー

### テスト実行環境

#### ローカル環境

```bash
# 全テストを実行
pytest tests/

# プロパティテストのみ実行
pytest tests/ -m property

# カバレッジレポート付きで実行
pytest tests/ --cov=src --cov-report=html
```

#### CI/CD環境

- GitHub Actionsを使用した自動テスト実行
- プルリクエスト時に全テストを実行
- テストが失敗した場合はマージをブロック

### モックとスタブ

外部依存関係（Twitter API、ファイルシステム）に対してはモックを使用します：

```python
from unittest.mock import Mock, patch

def test_api_call_with_mock():
    """モックを使用したAPIテスト"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "html": "<blockquote>...</blockquote>",
        "height": 850
    }
    
    with patch("requests.get", return_value=mock_response):
        client = TwitterAPIClient()
        result = client.get_oembed("https://twitter.com/user/status/123")
        assert result.html == "<blockquote>...</blockquote>"
```

## 実装の詳細

### Twitter oEmbed API仕様

#### エンドポイント

```
GET https://publish.twitter.com/oembed
```

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| url | string | ✓ | ツイートURL |
| maxwidth | integer | - | 最大幅（ピクセル） |
| hide_media | boolean | - | メディアを非表示 |
| hide_thread | boolean | - | スレッドを非表示 |
| omit_script | boolean | - | スクリプトタグを省略 |
| align | string | - | 配置（left, right, center, none） |
| related | string | - | 関連アカウント |
| lang | string | - | 言語コード |
| theme | string | - | テーマ（light, dark） |
| link_color | string | - | リンク色（16進数） |
| widget_type | string | - | ウィジェットタイプ |

#### レスポンス例

```json
{
  "url": "https://twitter.com/user/status/1234567890",
  "author_name": "User Name",
  "author_url": "https://twitter.com/user",
  "html": "<blockquote class=\"twitter-tweet\">...</blockquote>",
  "width": 550,
  "height": 850,
  "type": "rich",
  "cache_age": "3153600000",
  "provider_name": "Twitter",
  "provider_url": "https://twitter.com",
  "version": "1.0"
}
```

### URL解析パターン

システムは以下のURL形式をサポートします：

```python
TWEET_URL_PATTERNS = [
    r"https?://(?:www\.)?twitter\.com/\w+/status/(\d+)",
    r"https?://(?:www\.)?x\.com/\w+/status/(\d+)",
    r"https?://mobile\.twitter\.com/\w+/status/(\d+)",
    r"https?://(?:www\.)?twitter\.com/i/web/status/(\d+)",
]
```

### ファイル構造

```
src/
├── services/
│   └── twitter_embed_service.py    # メインサービス
├── clients/
│   └── twitter_api_client.py       # APIクライアント
├── repositories/
│   └── file_repository.py          # ファイルリポジトリ
├── models/
│   ├── embed_result.py             # データモデル
│   └── oembed_response.py          # oEmbedレスポンス
├── cli/
│   └── main.py                     # CLIエントリーポイント
├── ui/
│   └── admin_page.py               # Streamlit管理画面
└── utils/
    ├── validators.py               # バリデーター
    └── retry.py                    # リトライロジック

tests/
├── unit/
│   ├── test_twitter_embed_service.py
│   ├── test_twitter_api_client.py
│   └── test_file_repository.py
├── property/
│   ├── test_url_parsing_properties.py
│   ├── test_file_operations_properties.py
│   └── test_error_handling_properties.py
└── integration/
    └── test_end_to_end.py

data/
├── tweet_embed_code.html           # 埋め込みコード
├── tweet_height.txt                # 表示高さ
└── backups/                        # バックアップディレクトリ
    └── tweet_embed_code_*.html     # バックアップファイル

logs/
└── twitter_embed.log               # ログファイル
```

### 設定管理

#### 環境変数

```bash
# Twitter API認証（将来の拡張用）
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret

# ファイルパス
TWITTER_EMBED_CODE_PATH=data/tweet_embed_code.html
TWITTER_HEIGHT_PATH=data/tweet_height.txt
TWITTER_BACKUP_DIR=data/backups

# ログ設定
TWITTER_EMBED_LOG_LEVEL=INFO
TWITTER_EMBED_LOG_FILE=logs/twitter_embed.log

# リトライ設定
TWITTER_API_MAX_RETRIES=3
TWITTER_API_RETRY_DELAY=1.0

# 管理画面認証
ADMIN_PASSWORD=your_admin_password
```

#### 設定ファイル（config.yaml）

```yaml
twitter_embed:
  api:
    endpoint: "https://publish.twitter.com/oembed"
    timeout: 30
    max_retries: 3
    retry_delay: 1.0
  
  files:
    embed_code_path: "data/tweet_embed_code.html"
    height_path: "data/tweet_height.txt"
    backup_dir: "data/backups"
  
  logging:
    level: "INFO"
    file: "logs/twitter_embed.log"
    max_size: 10485760  # 10MB
    backup_count: 5
  
  validation:
    allowed_domains:
      - "twitter.com"
      - "x.com"
    max_url_length: 2048
  
  defaults:
    height: 850
    max_width: 550
```

## セキュリティ考慮事項

### 1. 認証情報の保護

- 環境変数を使用した認証情報の管理
- `.env`ファイルを`.gitignore`に追加
- ログやエラーメッセージに認証情報を含めない

### 2. 入力検証

- ツイートURLの厳密な検証
- SQLインジェクション対策（該当する場合）
- XSS対策（HTMLコードの検証）

### 3. ファイルシステムセキュリティ

- ファイルパスのサニタイゼーション
- ディレクトリトラバーサル攻撃の防止
- 適切なファイルパーミッションの設定

### 4. API通信のセキュリティ

- HTTPS通信の強制
- SSL証明書の検証
- タイムアウトの設定

### 5. アクセス制御

- Streamlit管理画面への認証機能
- 権限ベースのアクセス制御
- セッション管理

## パフォーマンス考慮事項

### 1. API呼び出しの最適化

- レート制限の遵守
- バッチ処理による効率化
- キャッシング戦略（将来の拡張）

### 2. ファイル操作の最適化

- バッファリングを使用した効率的な読み書き
- 大きなファイルの処理時のメモリ管理
- 非同期I/O（必要に応じて）

### 3. 並行処理

- 複数ツイートの並行取得（API制限を考慮）
- スレッドプールまたは非同期処理の使用

## 運用とメンテナンス

### 1. ログ管理

- ログローテーション（10MB、5世代）
- ログレベルの適切な設定
- エラーログの監視

### 2. バックアップ管理

- 自動バックアップの作成
- バックアップの保持期間（30日間）
- バックアップからの復元手順

### 3. モニタリング

- API呼び出し成功率の監視
- エラー発生率の監視
- ファイルシステムの容量監視

### 4. アップデート手順

1. 新しいバージョンのデプロイ
2. 設定ファイルの更新
3. データベースマイグレーション（該当する場合）
4. 動作確認テストの実行
5. ロールバック手順の準備

## 今後の拡張可能性

### 1. 追加機能

- スケジュール実行機能（定期的な更新）
- 複数アカウントのサポート
- カスタムテーマの適用
- プレビュー機能の強化

### 2. 他のSNSへの対応

- Instagram埋め込み
- Facebook埋め込み
- YouTube埋め込み

### 3. 高度な機能

- 埋め込みコードのカスタマイズ
- A/Bテスト機能
- アナリティクス統合

### 4. クラウド対応（将来の拡張）

- GitHub Actions経由の自動更新
- Webhook経由の自動更新
- Streamlit Cloud対応（GitHub API経由のファイル更新）

## 参考資料

- [Twitter oEmbed API Documentation](https://developer.twitter.com/en/docs/twitter-for-websites/oembed-api)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
