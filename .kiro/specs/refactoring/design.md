# リファクタリング設計書

## 概要

本ドキュメントは、「しのうたタイム」アプリケーションのリファクタリング設計を定義します。現在のコードベースは機能的には動作していますが、以下の課題があります：

- **コードの重複**: 各ページで似たようなデータ読み込み処理が繰り返されている
- **責務の分離不足**: Home.pyに多くのロジックが集中している（約500行）
- **テスト可能性の低さ**: ビジネスロジックがUIコードと密結合している
- **保守性の課題**: 長い関数、複雑なデータ処理ロジック

リファクタリングの目標は、コードの保守性、テスト可能性、拡張性を向上させることです。

## アーキテクチャ

### 現在のアーキテクチャ

```
しのうたタイム（現在）
├── Home.py（約500行、多くのロジックが集中）
├── pages/
│   ├── 01_Information.py
│   ├── 02_About_Us.py
│   └── 99_Song_List_beta.py
├── footer.py
├── style.css
└── data/
    ├── M_YT_LIVE.TSV
    ├── M_YT_LIVE_TIMESTAMP.TSV
    └── V_SONG_LIST.TSV
```

### リファクタリング後のアーキテクチャ

```
しのうたタイム（リファクタリング後）
├── src/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py      # データ読み込みサービス
│   │   └── search_service.py    # 検索サービス
│   ├── core/
│   │   ├── __init__.py
│   │   ├── data_pipeline.py     # データ処理パイプライン
│   │   └── utils.py             # ユーティリティ関数
│   ├── ui/
│   │   ├── __init__.py
│   │   └── components.py        # UIコンポーネント
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # 設定管理
│   └── exceptions/
│       ├── __init__.py
│       └── errors.py            # カスタム例外
├── Home.py（簡潔化、約100行）
├── pages/
│   ├── 01_Information.py（簡潔化）
│   ├── 02_About_Us.py
│   └── 99_Song_List_beta.py（簡潔化）
├── footer.py
├── style.css
├── tests/
│   ├── __init__.py
│   ├── test_data_service.py
│   ├── test_search_service.py
│   ├── test_utils.py
│   └── test_data_pipeline.py
└── data/
    ├── M_YT_LIVE.TSV
    ├── M_YT_LIVE_TIMESTAMP.TSV
    └── V_SONG_LIST.TSV
```

### レイヤー構造

```
┌─────────────────────────────────────┐
│   プレゼンテーション層（UI）         │
│   - Home.py                         │
│   - pages/*.py                      │
│   - ui/components.py                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   ビジネスロジック層                 │
│   - services/data_service.py        │
│   - services/search_service.py      │
│   - core/data_pipeline.py           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   ユーティリティ層                   │
│   - core/utils.py                   │
│   - config/settings.py              │
│   - exceptions/errors.py            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   データ層                           │
│   - data/*.TSV                      │
└─────────────────────────────────────┘
```

## コンポーネントとインターフェース

### 1. DataService（services/data_service.py）

#### 責務
- TSVファイルからのデータ読み込み
- データの基本的な検証
- エラーハンドリング

#### インターフェース

```python
class DataService:
    """データ読み込みサービス"""
    
    def __init__(self, config: Config):
        """
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.error_message = None
    
    def load_lives_data(self) -> Optional[pd.DataFrame]:
        """
        配信データを読み込む
        
        Returns:
            配信データのDataFrame、エラー時はNone
        """
        pass
    
    def load_songs_data(self) -> Optional[pd.DataFrame]:
        """
        楽曲データを読み込む
        
        Returns:
            楽曲データのDataFrame、エラー時はNone
        """
        pass
    
    def load_song_list_data(self) -> Optional[pd.DataFrame]:
        """
        楽曲リストデータを読み込む
        
        Returns:
            楽曲リストデータのDataFrame、エラー時はNone
        """
        pass
    
    def merge_data(
        self, 
        lives_df: pd.DataFrame, 
        songs_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        配信データと楽曲データを結合する
        
        Args:
            lives_df: 配信データ
            songs_df: 楽曲データ
        
        Returns:
            結合されたDataFrame
        """
        pass
    
    def get_last_error(self) -> Optional[str]:
        """
        最後に発生したエラーメッセージを取得
        
        Returns:
            エラーメッセージ、エラーがない場合はNone
        """
        return self.error_message
```

### 2. SearchService（services/search_service.py）

#### 責務
- キーワード検索
- フィルタリング
- 検索結果の管理

#### インターフェース

```python
class SearchService:
    """検索サービス"""
    
    def __init__(self):
        """検索サービスの初期化"""
        pass
    
    def search(
        self,
        df: pd.DataFrame,
        query: str,
        fields: List[str],
        case_sensitive: bool = False
    ) -> pd.DataFrame:
        """
        データフレームを検索する
        
        Args:
            df: 検索対象のDataFrame
            query: 検索クエリ
            fields: 検索対象フィールドのリスト
            case_sensitive: 大文字小文字を区別するか
        
        Returns:
            フィルタリングされたDataFrame
        """
        pass
    
    def filter_by_multiple_conditions(
        self,
        df: pd.DataFrame,
        conditions: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        複数条件でフィルタリングする
        
        Args:
            df: フィルタリング対象のDataFrame
            conditions: フィールド名と値の辞書
        
        Returns:
            フィルタリングされたDataFrame
        """
        pass
```

### 3. Utils（core/utils.py）

#### 責務
- タイムスタンプ変換
- URL生成
- 曲目番号生成
- 日付変換

#### インターフェース

```python
def convert_timestamp_to_seconds(timestamp_str: str) -> Optional[int]:
    """
    タイムスタンプ文字列を秒数に変換する
    
    Args:
        timestamp_str: タイムスタンプ文字列（HH:MM:SS または MM:SS）
    
    Returns:
        秒数、変換失敗時はNone
    """
    pass

def generate_youtube_url(base_url: str, timestamp_seconds: int) -> str:
    """
    YouTubeタイムスタンプ付きURLを生成する
    
    Args:
        base_url: 基本URL
        timestamp_seconds: タイムスタンプ（秒）
    
    Returns:
        タイムスタンプ付きURL
    """
    pass

def generate_song_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """
    曲目番号を生成する
    
    Args:
        df: 楽曲データのDataFrame
    
    Returns:
        曲目番号が追加されたDataFrame
    """
    pass

def convert_date_string(date_str: str) -> Optional[datetime]:
    """
    日付文字列をdatetime型に変換する
    
    Args:
        date_str: 日付文字列（UNIXミリ秒またはYYYY/MM/DD形式）
    
    Returns:
        datetime型、変換失敗時はNone
    """
    pass
```

### 4. DataPipeline（core/data_pipeline.py）

#### 責務
- データ処理の全体フロー管理
- 各処理ステップの実行
- キャッシング
- エラーハンドリング

#### インターフェース

```python
class DataPipeline:
    """データ処理パイプライン"""
    
    def __init__(self, data_service: DataService, config: Config):
        """
        Args:
            data_service: データサービス
            config: 設定オブジェクト
        """
        self.data_service = data_service
        self.config = config
        self._cache = {}
    
    def execute(self) -> Optional[pd.DataFrame]:
        """
        パイプライン全体を実行する
        
        Returns:
            処理済みDataFrame、エラー時はNone
        """
        pass
    
    def _load_data(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """データ読み込みステップ"""
        pass
    
    def _merge_data(
        self, 
        lives_df: pd.DataFrame, 
        songs_df: pd.DataFrame
    ) -> pd.DataFrame:
        """データ結合ステップ"""
        pass
    
    def _transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """データ変換ステップ"""
        pass
    
    def _sort_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """データソートステップ"""
        pass
    
    def _validate_step_result(self, df: pd.DataFrame, step_name: str) -> bool:
        """
        ステップ結果を検証する
        
        Args:
            df: 検証対象のDataFrame
            step_name: ステップ名
        
        Returns:
            検証成功時True
        """
        pass
    
    def clear_cache(self):
        """キャッシュをクリアする"""
        self._cache.clear()
```

### 5. UIComponents（ui/components.py）

#### 責務
- 再利用可能なUIコンポーネントの提供
- UIロジックの分離

#### インターフェース

```python
def render_search_form(
    default_query: str = "",
    include_live_title: bool = True
) -> Tuple[str, bool, bool]:
    """
    検索フォームを表示する
    
    Args:
        default_query: デフォルトの検索クエリ
        include_live_title: ライブタイトル検索のデフォルト値
    
    Returns:
        (検索クエリ, ライブタイトル検索フラグ, 検索ボタンクリック)
    """
    pass

def render_results_table(
    df: pd.DataFrame,
    columns: List[str],
    column_headers: Dict[str, str]
) -> None:
    """
    結果テーブルを表示する
    
    Args:
        df: 表示するDataFrame
        columns: 表示する列のリスト
        column_headers: 列名のマッピング
    """
    pass

def render_pagination(
    total_count: int,
    current_limit: int,
    increment: int = 25
) -> Optional[int]:
    """
    ページネーションを表示する
    
    Args:
        total_count: 総件数
        current_limit: 現在の表示件数
        increment: 増分
    
    Returns:
        新しい表示件数、変更がない場合はNone
    """
    pass

def render_twitter_embed(
    embed_code_path: str,
    height_path: str,
    default_height: int = 850
) -> None:
    """
    Twitter埋め込みを表示する
    
    Args:
        embed_code_path: 埋め込みコードファイルのパス
        height_path: 高さ設定ファイルのパス
        default_height: デフォルトの高さ
    """
    pass
```

### 6. Config（config/settings.py）

#### 責務
- アプリケーション設定の一元管理
- 環境変数からの設定読み込み
- デフォルト値の提供

#### インターフェース

```python
@dataclass
class Config:
    """アプリケーション設定"""
    
    # ファイルパス
    lives_file_path: str = "data/M_YT_LIVE.TSV"
    songs_file_path: str = "data/M_YT_LIVE_TIMESTAMP.TSV"
    song_list_file_path: str = "data/V_SONG_LIST.TSV"
    tweet_embed_code_path: str = "data/tweet_embed_code.html"
    tweet_height_path: str = "data/tweet_height.txt"
    css_file_path: str = "style.css"
    
    # 表示設定
    initial_display_limit: int = 25
    display_increment: int = 25
    
    # ページ設定
    page_title: str = "しのうたタイム"
    page_icon: str = "👻"
    layout: str = "wide"
    
    # パフォーマンス設定
    enable_cache: bool = True
    cache_ttl: int = 3600  # 秒
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        環境変数から設定を読み込む
        
        Returns:
            設定オブジェクト
        """
        pass
    
    def validate(self) -> bool:
        """
        設定値を検証する
        
        Returns:
            検証成功時True
        
        Raises:
            ConfigurationError: 設定値が不正な場合
        """
        pass
```

### 7. Exceptions（exceptions/errors.py）

#### 責務
- カスタム例外の定義
- エラーログ機能

#### インターフェース

```python
class ShinoutaTimeError(Exception):
    """基底例外クラス"""
    pass

class DataLoadError(ShinoutaTimeError):
    """データ読み込みエラー"""
    
    def __init__(self, file_path: str, message: str):
        self.file_path = file_path
        self.message = message
        super().__init__(f"データ読み込みエラー ({file_path}): {message}")

class DataProcessingError(ShinoutaTimeError):
    """データ処理エラー"""
    
    def __init__(self, step: str, message: str):
        self.step = step
        self.message = message
        super().__init__(f"データ処理エラー ({step}): {message}")

class ConfigurationError(ShinoutaTimeError):
    """設定エラー"""
    
    def __init__(self, setting: str, message: str):
        self.setting = setting
        self.message = message
        super().__init__(f"設定エラー ({setting}): {message}")

def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """
    エラーをログに記録する
    
    Args:
        error: 例外オブジェクト
        context: 追加のコンテキスト情報
    """
    pass
```

## データモデル

リファクタリング後もデータモデルは変更しません。既存のTSVファイル形式を維持します。

## 正確性プロパティ

*プロパティとは、システムの全ての有効な実行において真であるべき特性や動作のことです。プロパティは、人間が読める仕様と機械で検証可能な正確性保証の橋渡しとなります。*

