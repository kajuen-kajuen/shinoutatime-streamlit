# 設計書

## 概要

V_SONG_LIST.TSV自動生成システムは、M_YT_LIVE.TSVとM_YT_LIVE_TIMESTAMP.TSVから曲ごとの最新歌唱情報を自動的に集計し、V_SONG_LIST.TSVを生成するPythonベースのコマンドラインツールです。本システムは、データの読み込み、結合、集計、ソート、出力の各処理を自動化し、データ品質チェック機能も提供します。

## アーキテクチャ

本システムは、レイヤードアーキテクチャを採用し、以下の層で構成されます：

```
┌─────────────────────────────────────┐
│   CLI Layer (コマンドライン)        │
│   - 引数解析                         │
│   - 実行制御                         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Service Layer (ビジネスロジック)  │
│   - データ結合・集計                 │
│   - 曲名正規化                       │
│   - 類似性チェック                   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Repository Layer (データアクセス)  │
│   - TSV読み込み                      │
│   - TSV書き込み                      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Model Layer (データモデル)         │
│   - LiveInfo                         │
│   - TimestampInfo                    │
│   - SongInfo                         │
└─────────────────────────────────────┘
```

## コンポーネントとインターフェース

### 1. CLIコンポーネント (`src/cli/song_list_generator.py`)

コマンドライン引数を解析し、処理を実行します。

**主要な機能:**
- 引数解析（入力ファイルパス、出力ファイルパス、オプション）
- ログレベル設定
- サービス層の呼び出し
- エラーハンドリング

**コマンドライン引数:**
```
python -m src.cli.song_list_generator [OPTIONS]

Options:
  --live-file PATH          M_YT_LIVE.TSVのパス (デフォルト: data/M_YT_LIVE.TSV)
  --timestamp-file PATH     M_YT_LIVE_TIMESTAMP.TSVのパス (デフォルト: data/M_YT_LIVE_TIMESTAMP.TSV)
  --output-file PATH        V_SONG_LIST.TSVの出力パス (デフォルト: data/V_SONG_LIST.TSV)
  --dry-run                 ドライランモード（ファイルを書き込まない）
  --similarity-threshold FLOAT  類似度チェックの閾値 (0.0-1.0, デフォルト: 0.85)
  --no-similarity-check     類似性チェックを無効化
  --verbose, -v             詳細ログを表示
  --help, -h                ヘルプメッセージを表示
  --version                 バージョン情報を表示
```

### 2. サービスコンポーネント (`src/services/song_list_service.py`)

ビジネスロジックを実装します。

**主要なクラス:**

```python
class SongListService:
    def __init__(self, live_repo: LiveRepository, timestamp_repo: TimestampRepository):
        """サービスの初期化"""
        
    def generate_song_list(self) -> List[SongInfo]:
        """曲リストを生成"""
        
    def normalize_song_name(self, song_name: str) -> Tuple[str, bool]:
        """曲名を正規化（バリエーション表記を除去）"""
        
    def check_similarity(self, songs: List[SongInfo], threshold: float) -> List[SimilarityWarning]:
        """類似性チェックを実行"""
        
    def compare_with_existing(self, new_songs: List[SongInfo], existing_file: str) -> DiffResult:
        """既存ファイルとの差分を検出"""
```

### 3. リポジトリコンポーネント

#### LiveRepository (`src/repositories/live_repository.py`)

M_YT_LIVE.TSVの読み込みを担当します。

```python
class LiveRepository:
    def __init__(self, file_path: str):
        """リポジトリの初期化"""
        
    def load_all(self) -> List[LiveInfo]:
        """すべての配信情報を読み込む"""
        
    def get_by_id(self, live_id: int) -> Optional[LiveInfo]:
        """IDで配信情報を取得"""
```

#### TimestampRepository (`src/repositories/timestamp_repository.py`)

M_YT_LIVE_TIMESTAMP.TSVの読み込みを担当します。

```python
class TimestampRepository:
    def __init__(self, file_path: str):
        """リポジトリの初期化"""
        
    def load_all(self) -> List[TimestampInfo]:
        """すべてのタイムスタンプ情報を読み込む"""
        
    def get_by_live_id(self, live_id: int) -> List[TimestampInfo]:
        """配信IDでタイムスタンプ情報を取得"""
```

#### SongListRepository (`src/repositories/song_list_repository.py`)

V_SONG_LIST.TSVの読み書きを担当します。

```python
class SongListRepository:
    def __init__(self, file_path: str):
        """リポジトリの初期化"""
        
    def load_all(self) -> List[SongInfo]:
        """既存の曲リストを読み込む"""
        
    def save_all(self, songs: List[SongInfo]) -> None:
        """曲リストを保存"""
```

### 4. モデルコンポーネント (`src/models/song_list_models.py`)

データ構造を定義します。

```python
@dataclass
class LiveInfo:
    """配信情報"""
    id: int
    date: datetime
    title: str
    url: str

@dataclass
class TimestampInfo:
    """タイムスタンプ情報"""
    id: int
    live_id: int
    timestamp: str
    song_name: str
    artist: str

@dataclass
class SongInfo:
    """曲情報"""
    artist: str
    artist_sort: str
    song_name: str
    latest_url: str
    
@dataclass
class SimilarityWarning:
    """類似性警告"""
    type: str  # 'artist' or 'song'
    item1: str
    item2: str
    similarity: float

@dataclass
class DiffResult:
    """差分結果"""
    added: List[SongInfo]
    removed: List[SongInfo]
    updated: List[Tuple[SongInfo, SongInfo]]  # (old, new)
```

### 5. ユーティリティコンポーネント

#### ArtistSortGenerator (`src/utils/artist_sort_generator.py`)

アーティスト名からソート用読み仮名を生成します。

```python
class ArtistSortGenerator:
    def generate(self, artist_name: str) -> str:
        """ソート用アーティスト名を生成"""
```

**実装方針:**
- 英数字のみの場合はそのまま返す
- 日本語が含まれる場合は`pykakasi`ライブラリを使用してひらがなに変換
- 特殊文字は適切に処理

#### URLGenerator (`src/utils/url_generator.py`)

タイムスタンプ付きURLを生成します。

```python
class URLGenerator:
    def generate_timestamped_url(self, base_url: str, timestamp: str) -> str:
        """タイムスタンプ付きURLを生成"""
        
    def parse_timestamp(self, timestamp: str) -> int:
        """タイムスタンプを秒数に変換"""
```

#### SimilarityChecker (`src/utils/similarity_checker.py`)

文字列の類似度を計算します。

```python
class SimilarityChecker:
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """レーベンシュタイン距離ベースの類似度を計算（0.0-1.0）"""
        
    def find_similar_pairs(self, strings: List[str], threshold: float) -> List[Tuple[str, str, float]]:
        """類似度が閾値以上のペアを検出"""
```

**実装方針:**
- `python-Levenshtein`ライブラリを使用
- 類似度 = 1.0 - (レーベンシュタイン距離 / max(len(str1), len(str2)))

## データモデル

### データフロー

```
M_YT_LIVE.TSV → LiveInfo[]
                    ↓
M_YT_LIVE_TIMESTAMP.TSV → TimestampInfo[]
                    ↓
            [データ結合・集計]
                    ↓
                SongInfo[]
                    ↓
            [ソート・正規化]
                    ↓
            V_SONG_LIST.TSV
```

### データ変換ルール

1. **配信日のパース**: "YYYY/M/D" 形式を`datetime`オブジェクトに変換
2. **タイムスタンプのパース**: "H:MM:SS" または "MM:SS" 形式を秒数に変換
3. **曲名の正規化**: 
   - `(1chorus)`, `(short ver)`, `(1phrase)` などのパターンを検出
   - 正規表現: `r'\([^)]*(?:chorus|ver|phrase)[^)]*\)'`
4. **ソート順**: ソート用アーティスト名の昇順 → 曲名の昇順

## 正確性プロパティ

*プロパティとは、システムのすべての有効な実行において真であるべき特性や振る舞いのことです。プロパティは、人間が読める仕様と機械で検証可能な正確性保証の橋渡しをします。*

### プロパティ1: TSVファイル読み込みの完全性

*任意の* 有効なTSVファイル（M_YT_LIVE.TSVまたはM_YT_LIVE_TIMESTAMP.TSV）に対して、読み込まれたレコード数は、ファイルのデータ行数（ヘッダーを除く）と一致する
**検証: 要件1.1, 1.2**

### プロパティ2: データ結合の完全性

*任意の* 有効なM_YT_LIVE.TSVとM_YT_LIVE_TIMESTAMP.TSVに対して、生成されるV_SONG_LIST.TSVのすべてのレコードは、元のタイムスタンプ情報に対応する配信情報が存在する
**検証: 要件2.1, 2.4**

### プロパティ3: 最新歌唱の正確性

*任意の* アーティストと曲名の組み合わせに対して、選択される最新歌唱は、そのアーティストと曲名を持つすべてのレコードの中で配信日が最も新しい（配信日が同じ場合は配信IDが最大）
**検証: 要件2.2, 2.3**

### プロパティ4: バリエーション表記の優先順位

*任意の* 同じアーティストと曲名（正規化後）の組み合わせに対して、バリエーション表記のない曲が存在する場合、それが選択される。バリエーション表記のみの場合は、最新の配信日のものが選択される
**検証: 要件2.6, 2.7**

### プロパティ5: 曲名正規化の冪等性

*任意の* 曲名に対して、正規化処理を2回適用した結果は、1回適用した結果と同じである
**検証: 要件2.6, 2.7**

### プロパティ6: ソート用アーティスト名の生成

*任意の* 英数字のみで構成されるアーティスト名に対して、ソート用アーティスト名は元のアーティスト名と同じである
**検証: 要件3.1**

### プロパティ7: タイムスタンプ変換のラウンドトリップ

*任意の* 有効なタイムスタンプ文字列（"HH:MM:SS"、"H:MM:SS"、"MM:SS"形式）に対して、それを秒数に変換し、再度タイムスタンプ文字列に変換すると、同じ時間を表す
**検証: 要件4.1, 4.2, 4.3, 4.4**

### プロパティ8: URL生成の正確性

*任意の* ベースURLとタイムスタンプに対して、生成されたタイムスタンプ付きURLは、ベースURLを含み、かつタイムスタンプパラメータ（&t=秒数）を含む
**検証: 要件4.1, 4.5**

### プロパティ9: ソート順の正確性

*任意の* 生成されたV_SONG_LIST.TSVに対して、すべての連続するレコードのペア(i, i+1)について、レコードiのソート用アーティスト名 ≤ レコードi+1のソート用アーティスト名、かつソート用アーティスト名が同じ場合は曲名i ≤ 曲名i+1
**検証: 要件5.3, 5.4**

### プロパティ10: 空データの除外

*任意の* 生成されたV_SONG_LIST.TSVに対して、すべてのレコードのアーティスト名と曲名は空白でない
**検証: 要件2.5**

### プロパティ11: ファイルエンコーディングの一貫性

*任意の* 生成されたV_SONG_LIST.TSVに対して、ファイルをUTF-8として読み込み、再度UTF-8として書き込んだ結果は、元のファイルと同じ内容である
**検証: 要件1.5, 5.5**

### プロパティ12: 類似性チェックの対称性

*任意の* 2つの文字列str1とstr2に対して、similarity(str1, str2) = similarity(str2, str1)
**検証: 要件9.3**

### プロパティ13: 類似性検出の正確性

*任意の* アーティスト名または曲名のリストに対して、類似度が指定された閾値以上のすべてのペアが検出される
**検証: 要件9.1, 9.2, 9.4**

## エラーハンドリング

### エラーの分類

1. **致命的エラー（処理を中断）**:
   - 入力ファイルが存在しない
   - ファイル形式が不正（ヘッダーが不一致）
   - 出力ファイルへの書き込み権限がない

2. **警告（処理を継続）**:
   - タイムスタンプ情報に対応する配信情報が存在しない
   - 曲名またはアーティスト名が空白
   - 類似したアーティスト名・曲名が検出された
   - 読み仮名の自動生成が失敗

### エラーメッセージの形式

```
[ERROR] <エラーの種類>: <詳細メッセージ>
  ファイル: <ファイルパス>
  行番号: <行番号>（該当する場合）
  
[WARNING] <警告の種類>: <詳細メッセージ>
  詳細: <追加情報>
```

### ログレベル

- **ERROR**: 致命的エラー
- **WARNING**: 警告
- **INFO**: 処理の進捗情報
- **DEBUG**: 詳細なデバッグ情報（--verboseオプション時のみ）

## テスト戦略

### ユニットテスト

各コンポーネントの個別機能をテストします：

- **リポジトリ層**: TSVファイルの読み書き
- **サービス層**: データ結合、集計、正規化ロジック
- **ユーティリティ**: URL生成、類似度計算、読み仮名生成

### プロパティベーステスト

`hypothesis`ライブラリを使用して、正確性プロパティを検証します：

- ランダムなデータを生成して各プロパティが成立することを確認
- 最低100回の反復テストを実行
- エッジケース（空文字列、特殊文字、境界値）を含む

### 統合テスト

実際のデータファイルを使用してエンドツーエンドの動作を検証します：

- サンプルデータでの正常系テスト
- 異常データでのエラーハンドリングテスト
- 既存ファイルとの差分検出テスト

### テストデータ

テスト用のサンプルTSVファイルを`tests/fixtures/`に配置します：

- `sample_live.tsv`: 10件程度の配信情報
- `sample_timestamp.tsv`: 50件程度のタイムスタンプ情報
- `sample_song_list.tsv`: 期待される出力結果
- `invalid_*.tsv`: 異常系テスト用データ

## 依存ライブラリ

- **pykakasi**: 日本語の読み仮名変換（ソート用アーティスト名生成）
- **python-Levenshtein**: レーベンシュタイン距離計算（類似性チェック）
- **hypothesis**: プロパティベーステスト
- **pytest**: ユニットテスト・統合テストフレームワーク

## パフォーマンス考慮事項

- **メモリ使用量**: すべてのデータをメモリに読み込むため、大規模データセット（10万件以上）では注意が必要
- **類似性チェック**: O(n²)の計算量のため、曲数が多い場合は時間がかかる可能性がある
  - 対策: 閾値を調整するか、`--no-similarity-check`オプションで無効化
- **ファイルI/O**: TSVファイルの読み書きは逐次処理のため、SSDの使用を推奨

## 将来の拡張性

1. **データベース対応**: TSVファイルの代わりにSQLiteやPostgreSQLを使用
2. **並列処理**: 類似性チェックを並列化してパフォーマンス向上
3. **Web UI**: Streamlitを使用したGUIの提供
4. **自動実行**: GitHub Actionsやcronでの定期実行
5. **差分更新**: 変更があった部分のみを更新する増分処理
