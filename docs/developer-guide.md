# 開発者ガイド

## 目次

1. [はじめに](#はじめに)
2. [プロジェクト構造](#プロジェクト構造)
3. [開発環境のセットアップ](#開発環境のセットアップ)
4. [各ファイルの役割](#各ファイルの役割)
5. [コーディング規約](#コーディング規約)
6. [ロギング機能](#ロギング機能)
7. [データファイルの管理](#データファイルの管理)
8. [開発ワークフロー](#開発ワークフロー)
9. [トラブルシューティング](#トラブルシューティング)

---

## はじめに

本ドキュメントは、「しのうたタイム」アプリケーションの開発者向けガイドです。
プロジェクトの構造、開発環境のセットアップ方法、コーディング規約などを説明します。

### プロジェクトの概要

「しのうたタイム」は、VTuber「幽音しの」さんの配信で歌唱された楽曲を検索・閲覧できる
非公式ファンサイトです。Streamlitフレームワークを使用したPython製Webアプリケーションです。

### 対象読者

- プロジェクトに新規参加する開発者
- コードのメンテナンスを行う開発者
- 機能追加や改善を行う開発者

---

## プロジェクト構造

```
shinouta-time-app/
├── .devcontainer/              # Dev Container設定
│   └── devcontainer.json       # VS Code Dev Container設定ファイル
├── .github/                    # GitHub関連設定
├── .kiro/                      # Kiro AI関連設定
│   ├── specs/                  # 仕様書・設計書
│   └── steering/               # プロジェクト言語設定など
├── .streamlit/                 # Streamlit設定
│   └── config.toml             # Streamlit設定ファイル
├── data/                       # データファイル
│   ├── M_YT_LIVE.TSV          # 配信情報データ
│   ├── M_YT_LIVE_TIMESTAMP.TSV # 楽曲タイムスタンプデータ
│   ├── V_SONG_LIST.TSV        # 楽曲リストデータ
│   ├── tweet_embed_code.html  # Twitter埋め込みコード
│   └── tweet_height.txt       # Twitter埋め込み高さ設定
├── docs/                       # ドキュメント
│   ├── architecture.md         # アーキテクチャドキュメント
│   ├── data-flow.md           # データフロードキュメント
│   └── developer-guide.md     # 本ドキュメント
├── pages/                      # Streamlitページ
│   ├── 01_Information.py      # 情報ページ
│   ├── 02_About_Us.py         # About Usページ
│   └── 99_Song_List_beta.py   # 楽曲リストページ（β版）
├── Home.py                     # メインページ（エントリーポイント）
├── footer.py                   # フッター表示モジュール
├── style.css                   # カスタムCSSスタイル
├── requirements.txt            # Python依存パッケージ
├── README.md                   # プロジェクト概要
└── LICENSE                     # ライセンス情報
```

### ディレクトリの役割

#### ルートディレクトリ

- **Home.py**: アプリケーションのエントリーポイント。メインページの実装。
- **footer.py**: 全ページで共通のフッター表示機能を提供。
- **style.css**: アプリケーション全体のカスタムCSSスタイル。
- **requirements.txt**: Python依存パッケージのリスト。

#### data/

TSVファイルとTwitter埋め込み関連ファイルを格納。

- **M_YT_LIVE.TSV**: 配信情報（配信日、タイトル、URL）
- **M_YT_LIVE_TIMESTAMP.TSV**: 楽曲タイムスタンプ情報（曲名、アーティスト、タイムスタンプ）
- **V_SONG_LIST.TSV**: 楽曲リスト（アーティスト順）
- **tweet_embed_code.html**: Twitter埋め込みHTMLコード
- **tweet_height.txt**: Twitter埋め込み表示高さ設定

#### pages/

Streamlitのマルチページ機能を使用したサブページ。

- **01_Information.py**: 配信スケジュールとお知らせ情報
- **02_About_Us.py**: サイトの目的と注意事項
- **99_Song_List_beta.py**: 楽曲リスト表示（β版）

#### docs/

プロジェクトのドキュメント。

- **architecture.md**: システムアーキテクチャの説明
- **data-flow.md**: データフローの説明
- **developer-guide.md**: 本ドキュメント

#### .streamlit/

Streamlitの設定ファイル。

- **config.toml**: テーマ設定、サーバー設定など

---

## 開発環境のセットアップ

### 必要な環境

- **Python**: 3.8以上（推奨: 3.10以上）
- **pip**: Pythonパッケージマネージャー
- **Git**: バージョン管理システム

### セットアップ手順

#### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd shinouta-time-app
```

#### 2. 仮想環境の作成（推奨）

```bash
# Windowsの場合
python -m venv venv
venv\Scripts\activate

# macOS/Linuxの場合
python3 -m venv venv
source venv/bin/activate
```

#### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

#### 4. アプリケーションの起動

```bash
streamlit run Home.py
```

ブラウザが自動的に開き、`http://localhost:8501` でアプリケーションが表示されます。

### Dev Container（オプション）

VS Codeを使用している場合、Dev Containerを利用できます。

1. VS Codeで「Remote - Containers」拡張機能をインストール
2. プロジェクトを開く
3. コマンドパレット（Ctrl+Shift+P）から「Remote-Containers: Reopen in Container」を選択

---

## 各ファイルの役割

### Home.py（メインページ）

**役割**: アプリケーションのエントリーポイント。楽曲検索機能を提供。

**主要機能**:
- TSVファイルからのデータ読み込み
- 配信データと楽曲データの結合
- キーワード検索（曲名、アーティスト、配信タイトル）
- YouTubeタイムスタンプ付きURL生成
- 段階的表示（25件ずつ）
- 曲目番号の自動生成

**重要な関数**:
- `convert_timestamp_to_seconds(timestamp_str)`: タイムスタンプを秒数に変換

**セッション状態**:
- `df_full`: 全データ
- `filtered_df`: フィルタリング後のデータ
- `search_query`: 検索キーワード
- `include_live_title`: 配信タイトル検索フラグ
- `display_limit`: 表示件数制限

### footer.py（フッターモジュール）

**役割**: 全ページで共通のフッター表示機能を提供。

**主要機能**:
- 区切り線の表示
- クレジット情報の表示
- 連絡先情報の表示

**重要な関数**:
- `display_footer()`: フッターを表示

**使用方法**:
```python
from footer import display_footer

# ページの最後で呼び出す
display_footer()
```

### pages/01_Information.py（情報ページ）

**役割**: 配信スケジュールとお知らせ情報を表示。

**主要機能**:
- YouTube動画の埋め込み表示
- Twitter投稿の埋め込み表示
- 過去のお知らせの展開可能な表示

**重要な関数**:
- `display_embedded_tweet(embed_code_path, height_path, default_height)`: Twitter埋め込み表示

### pages/02_About_Us.py（About Usページ）

**役割**: サイトの目的、注意事項、スペシャルサンクスを表示。

**主要機能**:
- サイトの目的説明
- 非公式サイトである旨の注意事項
- データの正確性に関する免責事項
- スペシャルサンクスセクション

### pages/99_Song_List_beta.py（楽曲リストページ）

**役割**: 全楽曲リストをアーティスト順で表示。

**主要機能**:
- V_SONG_LIST.TSVからのデータ読み込み
- アーティスト名によるソート
- YouTubeリンクの生成

**重要な関数**:
- `load_data(path)`: TSVファイルを読み込み（キャッシュ付き）

**β版の制約**:
- 漢字のソート順が完全ではない
- 一部楽曲の重複表示の可能性

### style.css（カスタムスタイル）

**役割**: アプリケーション全体のスタイリング。

**主要スタイル**:
- `.block-container`: メインコンテンツエリアの幅とマージン
- `table.dataframe`: テーブルのスタイリング
- `.artist-cell`: アーティスト列の改行許可

---

## コーディング規約

### 言語設定

本プロジェクトは**日本語を標準言語**とします。

#### 日本語で記述すべきもの

1. **ドキュメント**: すべてのマークダウンファイル
2. **コードコメント**: Pythonファイル内のコメント、docstring
3. **ユーザー向けメッセージ**: エラーメッセージ、警告、情報メッセージ

#### 英語で記述すべきもの

1. **プログラミング要素**: 変数名、関数名、クラス名、モジュール名
2. **ファイル名**: Pythonファイル、設定ファイル

### Python コーディングスタイル

#### 基本方針

- **PEP 8**: Pythonの標準コーディング規約に準拠
- **可読性重視**: コードは読みやすさを最優先

#### 命名規則

```python
# 変数名: スネークケース（小文字 + アンダースコア）
df_merged = pd.merge(...)
search_query = ""
display_limit = 25

# 関数名: スネークケース
def convert_timestamp_to_seconds(timestamp_str):
    pass

def display_footer():
    pass

# 定数: 大文字 + アンダースコア
CUSTOM_CSS = """..."""
DEFAULT_HEIGHT = 850

# クラス名: パスカルケース（使用する場合）
class DataProcessor:
    pass
```

#### インデント

- **4スペース**を使用（タブは使用しない）

```python
def example_function():
    if condition:
        # 4スペースのインデント
        do_something()
```

#### コメント規則

##### モジュールdocstring

各Pythonファイルの冒頭に、モジュールの目的と機能を説明するdocstringを記述。

```python
"""
モジュール名

このモジュールの目的と概要を記述します。

主な機能:
- 機能1の説明
- 機能2の説明
- 機能3の説明

データソース（該当する場合）:
- data/ファイル名.TSV: データの説明

要件: X.X-X.X
"""
```

##### 関数docstring

すべての関数に、引数、戻り値、例外を説明するdocstringを記述。

```python
def convert_timestamp_to_seconds(timestamp_str):
    """
    タイムスタンプ文字列を秒数に変換する
    
    YouTubeのタイムスタンプ付きURL生成のために、
    HH:MM:SS形式またはMM:SS形式の時間文字列を秒数に変換します。
    
    Args:
        timestamp_str (str): タイムスタンプ文字列
            - HH:MM:SS形式（例: "1:23:45"）
            - MM:SS形式（例: "12:34"）
    
    Returns:
        int: 変換された秒数。変換に失敗した場合はNone
            - HH:MM:SS形式の場合: 時間*3600 + 分*60 + 秒
            - MM:SS形式の場合: 分*60 + 秒
    
    Examples:
        >>> convert_timestamp_to_seconds("1:23:45")
        5025
        >>> convert_timestamp_to_seconds("12:34")
        754
        >>> convert_timestamp_to_seconds(None)
        None
    
    Notes:
        - 入力がNoneまたは文字列でない場合はNoneを返す
        - コロン区切りが3つでも2つでもない場合はNoneを返す
    """
    # 実装...
```

##### インラインコメント

コードの意図や処理内容を説明するコメントを適切に配置。

```python
# ===== データ結合処理 =====
# 配信情報（df_lives）と楽曲情報（df_songs）をLIVE_IDをキーとして結合
# 左結合（left join）により、楽曲データを基準として配信情報を紐付ける
df_merged = pd.merge(
    df_songs,
    df_lives[["ID", "配信日", "タイトル", "URL"]],
    left_on="LIVE_ID",  # 楽曲データのLIVE_IDカラム
    right_on="ID",      # 配信データのIDカラム
    how="left",         # 左結合: 楽曲データを基準とする
    suffixes=("_song", "_live"),  # 重複する列名に接尾辞を付与
)
```

#### エラーハンドリング

すべてのファイル読み込みとデータ処理にエラーハンドリングを実装。

```python
try:
    df = pd.read_csv(file_path, delimiter="\t")
except FileNotFoundError:
    st.error(f'エラー: ファイル "{file_path}" が見つかりません。')
    st.info(f"`{file_path}` が正しく配置されているか確認してください。")
except Exception as e:
    st.error(f'ファイル "{file_path}" の読み込み中にエラー: {e}')
```

### Streamlit 固有の規約

#### ページ設定

各ページファイルの冒頭で`st.set_page_config()`を呼び出す。

```python
st.set_page_config(
    page_title="ページタイトル - しのうたタイム",
    page_icon="👻",
    layout="wide",
)
```

#### セッション状態の管理

セッション状態を使用する場合は、初期化を明示的に行う。

```python
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
```

#### キャッシュの使用

データ読み込み関数には`@st.cache_data`デコレータを使用。

```python
@st.cache_data
def load_data(path):
    """データ読み込み処理"""
    return pd.read_csv(path, delimiter="\t")
```

---

## ロギング機能

### 概要

アプリケーションは統一されたロギング機能を提供します。ログレベル、フォーマット、ファイル出力、ローテーション設定を環境変数で制御できます。

### ロギング設定

#### 環境変数

| 環境変数名 | 説明 | デフォルト値 | 設定例 |
|-----------|------|------------|--------|
| `SHINOUTA_LOG_LEVEL` | ログレベル | INFO | DEBUG, INFO, WARNING, ERROR |
| `SHINOUTA_ENABLE_FILE_LOGGING` | ファイルログ出力 | false | true, false |
| `SHINOUTA_LOG_FILE` | ログファイルパス | logs/shinouta.log | logs/app.log |

#### ログレベルの説明

- **DEBUG**: 詳細なデバッグ情報（開発時のみ推奨）
  - データ読み込みの詳細
  - 検索条件の詳細
  - UIコンポーネントの表示状態
  
- **INFO**: 一般的な情報メッセージ（本番環境推奨）
  - データ読み込み完了
  - 検索実行と結果件数
  - パフォーマンス情報
  
- **WARNING**: 警告メッセージ
  - ファイルが見つからない
  - データ変換の失敗
  - 設定値の不正
  
- **ERROR**: エラーメッセージ
  - データ読み込みエラー
  - データ処理エラー
  - 予期しない例外

### 開発環境での使用

#### 基本的な使用方法

```bash
# DEBUGレベルでログを出力
export SHINOUTA_LOG_LEVEL=DEBUG
streamlit run Home.py
```

#### ファイルログの有効化

```bash
# ファイルログを有効化
export SHINOUTA_ENABLE_FILE_LOGGING=true
export SHINOUTA_LOG_FILE=logs/development.log
streamlit run Home.py
```

#### .envファイルの使用

`.env.example`を`.env`にコピーして編集：

```bash
cp .env.example .env
```

`.env`ファイルの内容：

```bash
SHINOUTA_LOG_LEVEL=DEBUG
SHINOUTA_ENABLE_FILE_LOGGING=true
SHINOUTA_LOG_FILE=logs/development.log
```

### 本番環境での使用

本番環境では、INFOレベル以上のログのみを出力することを推奨します。

```bash
export SHINOUTA_LOG_LEVEL=INFO
export SHINOUTA_ENABLE_FILE_LOGGING=true
export SHINOUTA_LOG_FILE=logs/production.log
streamlit run Home.py
```

### ログファイルのローテーション

ファイルログが有効な場合、以下の設定で自動的にローテーションされます：

- **最大ファイルサイズ**: 10MB
- **保持するバックアップ数**: 5個
- **ファイル名形式**: 
  - `shinouta.log` (現在のログ)
  - `shinouta.log.1` (1世代前)
  - `shinouta.log.2` (2世代前)
  - ...
  - `shinouta.log.5` (5世代前)

ファイルサイズが10MBを超えると、自動的に`shinouta.log.1`にローテーションされ、新しい`shinouta.log`が作成されます。

### コード内でのロギング使用方法

#### モジュールでのロガー取得

```python
import logging

# モジュールレベルでロガーを取得
logger = logging.getLogger(__name__)

# ログ出力
logger.debug("デバッグメッセージ")
logger.info("情報メッセージ")
logger.warning("警告メッセージ")
logger.error("エラーメッセージ")
```

#### データ読み込み時のログ

```python
def load_data(file_path):
    """データを読み込む"""
    logger.info(f"データを読み込み中: {file_path}")
    
    try:
        df = pd.read_csv(file_path, delimiter="\t")
        logger.info(f"データを読み込みました: {len(df)}件")
        return df
    except FileNotFoundError:
        logger.error(f"ファイルが見つかりません: {file_path}")
        return None
    except Exception as e:
        logger.error(f"データ読み込み中にエラーが発生しました: {e}", exc_info=True)
        return None
```

#### パフォーマンス情報のログ

```python
import time

def process_data(df):
    """データを処理する"""
    start_time = time.time()
    logger.info("データ処理を開始")
    
    # 処理...
    
    elapsed_time = time.time() - start_time
    logger.info(f"データ処理が完了しました: 処理時間={elapsed_time:.2f}秒")
```

#### エラー時の詳細ログ

```python
try:
    # 処理...
except Exception as e:
    # exc_info=Trueでスタックトレースも記録
    logger.error(f"エラーが発生しました: {e}", exc_info=True)
```

### ログの確認方法

#### コンソールログの確認

アプリケーション実行中、コンソールにログが出力されます：

```
2024-01-01 12:00:00 - src.services.data_service - INFO - データを読み込み中: data/M_YT_LIVE.TSV
2024-01-01 12:00:01 - src.services.data_service - INFO - データを読み込みました: 100件
2024-01-01 12:00:02 - src.core.data_pipeline - INFO - データパイプライン実行完了: 500件、処理時間: 1.23秒
```

#### ファイルログの確認

```bash
# ログファイルの内容を表示
cat logs/shinouta.log

# ログファイルをリアルタイムで監視
tail -f logs/shinouta.log

# エラーログのみを抽出
grep ERROR logs/shinouta.log
```

### ログのフォーマット

ログは以下のフォーマットで出力されます：

```
<タイムスタンプ> - <モジュール名> - <ログレベル> - <メッセージ>
```

例：
```
2024-01-01 12:00:00 - src.services.data_service - INFO - データを読み込みました: 100件
```

---

## データファイルの管理

### TSVファイルの形式

すべてのデータファイルはタブ区切り（TSV）形式。

#### M_YT_LIVE.TSV（配信情報）

```
ID	配信日	タイトル	URL
1	2024/01/01	配信タイトル	https://www.youtube.com/watch?v=...
```

**カラム**:
- `ID`: 配信の一意識別子（整数）
- `配信日`: 配信日（UNIXミリ秒またはYYYY/MM/DD形式）
- `タイトル`: 配信タイトル（文字列）
- `URL`: YouTube配信URL（文字列）

#### M_YT_LIVE_TIMESTAMP.TSV（楽曲タイムスタンプ）

```
ID	LIVE_ID	曲名	アーティスト	タイムスタンプ
1	1	曲名	アーティスト名	1:23:45
```

**カラム**:
- `ID`: 楽曲レコードの一意識別子（整数）
- `LIVE_ID`: 配信IDへの外部キー（整数）
- `曲名`: 楽曲名（文字列）
- `アーティスト`: アーティスト名（文字列）
- `タイムスタンプ`: 歌唱開始時刻（HH:MM:SSまたはMM:SS形式）

#### V_SONG_LIST.TSV（楽曲リスト）

```
アーティスト	アーティスト(ソート用)	曲名	最近の歌唱
アーティスト名	artist_name	曲名	https://www.youtube.com/watch?v=...
```

**カラム**:
- `アーティスト`: アーティスト名（表示用、文字列）
- `アーティスト(ソート用)`: アーティスト名（ソート用、文字列）
- `曲名`: 楽曲名（文字列）
- `最近の歌唱`: 最近の歌唱へのYouTube URL（文字列）

### データ更新の手順

1. TSVファイルをテキストエディタで開く
2. タブ区切りを維持しながらデータを追加・編集
3. ファイルを保存
4. アプリケーションを再起動（キャッシュクリア）

**注意事項**:
- タブ区切りを維持すること（スペースに変換しない）
- 文字エンコーディングはUTF-8を使用
- 改行コードはLF（Unix形式）を推奨

---

## 開発ワークフロー

### 1. 機能追加の流れ

1. **要件定義**: `.kiro/specs/shinouta-time-app/requirements.md`を更新
2. **設計**: `.kiro/specs/shinouta-time-app/design.md`を更新
3. **実装**: コードを記述
4. **テスト**: ローカル環境で動作確認
5. **ドキュメント更新**: 必要に応じてドキュメントを更新
6. **コミット**: Gitでコミット

### 2. ブランチ戦略

- **main**: 本番環境用の安定版
- **develop**: 開発用ブランチ
- **feature/機能名**: 機能追加用ブランチ
- **fix/バグ名**: バグ修正用ブランチ

### 3. コミットメッセージ

```
[種別] 簡潔な説明

詳細な説明（必要に応じて）
```

**種別**:
- `feat`: 新機能追加
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `style`: コードスタイル修正（機能変更なし）
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: その他の変更

**例**:
```
feat: 楽曲検索機能に配信タイトル検索を追加

チェックボックスで配信タイトルを検索対象に含めるかどうかを
選択できるようにしました。
```

### 4. コードレビュー

プルリクエストを作成する際は、以下を確認：

- [ ] コーディング規約に準拠しているか
- [ ] docstringとコメントが適切に記述されているか
- [ ] エラーハンドリングが実装されているか
- [ ] ローカル環境で動作確認済みか
- [ ] 関連ドキュメントが更新されているか

---

## トラブルシューティング

### よくある問題と解決方法

#### 1. アプリケーションが起動しない

**症状**: `streamlit run Home.py`を実行してもエラーが発生する

**解決方法**:
- 仮想環境がアクティブになっているか確認
- 依存パッケージが正しくインストールされているか確認
  ```bash
  pip install -r requirements.txt
  ```
- Pythonのバージョンを確認（3.8以上が必要）
  ```bash
  python --version
  ```

#### 2. TSVファイルが読み込めない

**症状**: 「ファイルが見つかりません」エラーが表示される

**解決方法**:
- `data/`ディレクトリにTSVファイルが存在するか確認
- ファイル名が正しいか確認（大文字小文字を区別）
- ファイルパスが正しいか確認

#### 3. CSSが適用されない

**症状**: スタイルが反映されない

**解決方法**:
- `style.css`ファイルがルートディレクトリに存在するか確認
- ブラウザのキャッシュをクリア
- Streamlitのキャッシュをクリア
  ```bash
  streamlit cache clear
  ```

#### 4. セッション状態がリセットされる

**症状**: 検索結果が保持されない

**解決方法**:
- `st.session_state`の初期化が正しく行われているか確認
- `st.rerun()`の使用箇所を確認

#### 5. データのソート順がおかしい

**症状**: 楽曲リストの並び順が期待と異なる

**解決方法**:
- `アーティスト(ソート用)`列のデータを確認
- 漢字のソートはβ版では完全に対応していないことを確認
- 必要に応じて手動でソート用データを調整

### デバッグ方法

#### Streamlitのデバッグ機能

```python
# データの内容を確認
st.write(df)

# 変数の値を確認
st.write(f"変数の値: {variable}")

# セッション状態を確認
st.write(st.session_state)
```

#### ログ出力

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("デバッグメッセージ")
logger.info("情報メッセージ")
logger.warning("警告メッセージ")
logger.error("エラーメッセージ")
```

---

## 参考資料

### 公式ドキュメント

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Python Documentation](https://docs.python.org/3/)

### プロジェクト内ドキュメント

- [README.md](../README.md): プロジェクト概要
- [architecture.md](architecture.md): アーキテクチャドキュメント
- [data-flow.md](data-flow.md): データフロードキュメント
- [requirements.md](../.kiro/specs/shinouta-time-app/requirements.md): 要件定義書
- [design.md](../.kiro/specs/shinouta-time-app/design.md): 設計書

---

## 連絡先

本プロジェクトに関する質問やバグ報告は、[@kajuen_kajuen](https://x.com/kajuen_kajuen)までお願いします。

---

**最終更新日**: 2025年11月17日
