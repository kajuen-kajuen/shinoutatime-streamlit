# データフロードキュメント

## 概要

本ドキュメントは、「しのうたタイム」アプリケーションにおけるデータの流れを詳細に説明します。データの読み込みから表示まで、各処理ステップとデータモデルの関係を図示し、システムの動作を理解しやすくします。

## データフロー全体像

```mermaid
graph TB
    subgraph "データソース層"
        TSV1[data/M_YT_LIVE.TSV<br/>配信情報]
        TSV2[data/M_YT_LIVE_TIMESTAMP.TSV<br/>楽曲タイムスタンプ情報]
        TSV3[data/V_SONG_LIST.TSV<br/>楽曲リスト情報]
    end
    
    subgraph "データ読み込み層"
        READ1[Pandas read_csv<br/>配信データ読み込み]
        READ2[Pandas read_csv<br/>楽曲データ読み込み]
        READ3[Pandas read_csv<br/>楽曲リスト読み込み]
    end
    
    subgraph "データ処理層"
        MERGE[データ結合<br/>LIVE_IDをキーとして結合]
        CONVERT[タイムスタンプ変換<br/>HH:MM:SS → 秒数]
        SORT[ソート処理<br/>配信日降順・タイムスタンプ昇順]
        URLGEN[URL生成<br/>タイムスタンプ付きYouTube URL]
        SONGNUM[曲目番号生成<br/>配信内での歌唱順序]
    end
    
    subgraph "検索・フィルタリング層"
        SEARCH[検索処理<br/>キーワードによるフィルタリング]
        FILTER[フィルタ条件適用<br/>曲名・アーティスト・配信タイトル]
    end
    
    subgraph "表示制御層"
        LIMIT[段階的表示<br/>25件ずつ表示]
        HTML[HTML変換<br/>リンク生成・スタイル適用]
    end
    
    subgraph "UI表示層"
        UI[Streamlit UI<br/>テーブル表示]
    end
    
    TSV1 --> READ1
    TSV2 --> READ2
    TSV3 --> READ3
    
    READ1 --> MERGE
    READ2 --> MERGE
    
    MERGE --> CONVERT
    CONVERT --> SORT
    SORT --> URLGEN
    URLGEN --> SONGNUM
    
    SONGNUM --> SEARCH
    SEARCH --> FILTER
    FILTER --> LIMIT
    LIMIT --> HTML
    HTML --> UI
    
    READ3 --> SORT
```

## メインページのデータフロー詳細

### 1. データ読み込みフェーズ

```mermaid
sequenceDiagram
    participant App as Home.py
    participant Pandas as Pandas
    participant File1 as M_YT_LIVE.TSV
    participant File2 as M_YT_LIVE_TIMESTAMP.TSV
    
    App->>Pandas: read_csv(M_YT_LIVE.TSV)
    Pandas->>File1: ファイル読み込み
    File1-->>Pandas: 配信データ
    Pandas-->>App: df_lives (DataFrame)
    
    App->>Pandas: read_csv(M_YT_LIVE_TIMESTAMP.TSV)
    Pandas->>File2: ファイル読み込み
    File2-->>Pandas: 楽曲データ
    Pandas-->>App: df_songs (DataFrame)
    
    Note over App: エラーハンドリング:<br/>FileNotFoundError<br/>Exception
```

**処理内容:**
- `data/M_YT_LIVE.TSV`から配信情報を読み込む
- `data/M_YT_LIVE_TIMESTAMP.TSV`から楽曲タイムスタンプ情報を読み込む
- エラー発生時は適切なメッセージを表示し、処理を継続

**要件:** 1.1, 1.2, 1.3, 1.4

### 2. データ結合フェーズ

```mermaid
graph LR
    A[df_songs<br/>楽曲データ] --> C[pd.merge]
    B[df_lives<br/>配信データ] --> C
    C --> D[df_merged<br/>結合データ]
    
    style C fill:#e1f5ff
```


**処理内容:**
```python
df_merged = pd.merge(
    df_songs,
    df_lives[["ID", "配信日", "タイトル", "URL"]],
    left_on="LIVE_ID",
    right_on="ID",
    how="left",
    suffixes=("_song", "_live")
)
```

- 楽曲データの`LIVE_ID`と配信データの`ID`をキーとして左結合
- 各楽曲がどの配信で歌われたかを紐付ける
- 重複する列名には接尾辞（`_song`, `_live`）を付与

**要件:** 1.5

### 3. タイムスタンプ変換フェーズ

```mermaid
graph TB
    A[タイムスタンプ文字列<br/>HH:MM:SS or MM:SS] --> B{形式判定}
    B -->|3要素| C[HH * 3600 + MM * 60 + SS]
    B -->|2要素| D[MM * 60 + SS]
    B -->|その他| E[None]
    C --> F[秒数]
    D --> F
    E --> F
    
    style B fill:#fff4e6
    style F fill:#e8f5e9
```

**処理内容:**
- `convert_timestamp_to_seconds()`関数を使用
- HH:MM:SS形式: 時間×3600 + 分×60 + 秒
- MM:SS形式: 分×60 + 秒
- 不正な形式の場合はNoneを返す

**要件:** 6.1


### 4. ソート処理フェーズ

```mermaid
graph TB
    A[df_merged] --> B[日付変換<br/>UNIXミリ秒 → datetime]
    B --> C[日付変換<br/>YYYY/MM/DD → datetime]
    C --> D[ソート実行]
    D --> E[ソート済みデータ]
    
    subgraph "ソート条件"
        S1[1. ライブ配信日_sortable<br/>降順 新しい順]
        S2[2. LIVE_ID<br/>昇順]
        S3[3. タイムスタンプ_秒<br/>昇順]
    end
    
    D -.適用.-> S1
    D -.適用.-> S2
    D -.適用.-> S3
    
    style D fill:#e1f5ff
```

**処理内容:**
1. 配信日をdatetime型に変換（UNIXミリ秒 → datetime）
2. 変換失敗した行はYYYY/MM/DD形式として再変換
3. 3つのキーでソート:
   - 配信日降順（新しい配信が上）
   - LIVE_ID昇順（同一日の配信順）
   - タイムスタンプ昇順（配信内の歌唱順）

**要件:** 4.3, 4.4, 4.5

### 5. URL生成フェーズ


```mermaid
graph LR
    A[元ライブURL] --> C{URL & 秒数<br/>存在確認}
    B[タイムスタンプ_秒] --> C
    C -->|両方存在| D[URL + &t= + 秒数 + s]
    C -->|いずれか欠損| E[空文字列]
    D --> F[YouTubeタイムスタンプ付きURL]
    E --> F
    
    style C fill:#fff4e6
    style F fill:#e8f5e9
```

**処理内容:**
```python
df_merged["YouTubeタイムスタンプ付きURL"] = df_merged.apply(
    lambda row: (
        f"{row['元ライブURL']}&t={int(row['タイムスタンプ_秒'])}s"
        if pd.notna(row["元ライブURL"]) and pd.notna(row["タイムスタンプ_秒"])
        else ""
    ),
    axis=1
)
```

- 配信URLにタイムスタンプパラメータ（`&t=秒数s`）を付加
- URLまたは秒数が欠損している場合は空文字列

**要件:** 6.2, 6.3

### 6. 曲目番号生成フェーズ

```mermaid
graph TB
    A[df_merged] --> B[各配信内で曲順を計算<br/>groupby LIVE_ID.cumcount]
    B --> C[同一日内の配信に番号を振る<br/>factorize LIVE_ID]
    C --> D{同一日の<br/>配信数}
    D -->|複数| E[配信番号-曲順曲目<br/>例: 1-3曲目]
    D -->|単一| F[曲順曲目<br/>例: 3曲目]
    E --> G[曲目列]
    F --> G
    
    style D fill:#fff4e6
    style G fill:#e8f5e9
```


**処理内容:**
1. **曲順の計算**: `groupby("LIVE_ID").cumcount() + 1`で各配信内の連番を生成
2. **ライブ番号の計算**: 同一日内の配信に`factorize`で番号を振る
3. **曲目表示形式の決定**:
   - 同一日に複数配信: `{ライブ番号}-{曲順}曲目`
   - 同一日に単一配信: `{曲順}曲目`

**要件:** 7.1, 7.2, 7.3, 7.4

## 検索処理のデータフロー

### 検索フロー全体

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant UI as Streamlit UI
    participant Session as セッション状態
    participant Filter as フィルタ処理
    
    User->>UI: キーワード入力
    User->>UI: チェックボックス選択
    User->>UI: 検索ボタンクリック
    
    UI->>Session: search_query保存
    UI->>Session: include_live_title保存
    UI->>Session: display_limit=25にリセット
    
    Session->>Filter: df_full取得
    Filter->>Filter: 曲名で部分一致検索
    Filter->>Filter: アーティストで部分一致検索
    
    alt ライブタイトル検索ON
        Filter->>Filter: ライブタイトルで部分一致検索
    end
    
    Filter->>Session: filtered_df保存
    Session->>UI: 検索結果表示
    UI->>User: 結果件数とテーブル表示
```


### 検索フィルタリング詳細

```mermaid
graph TB
    A[検索キーワード] --> B{キーワード<br/>存在?}
    B -->|No| C[全件表示]
    B -->|Yes| D[フィルタ条件構築]
    
    D --> E[曲名.str.contains<br/>case=False]
    D --> F[アーティスト.str.contains<br/>case=False]
    
    G{ライブタイトル<br/>検索ON?} -->|Yes| H[ライブタイトル.str.contains<br/>case=False]
    G -->|No| I[スキップ]
    
    E --> J[OR条件で結合]
    F --> J
    H --> J
    I --> J
    
    J --> K[フィルタ適用]
    K --> L[filtered_df]
    C --> L
    
    style B fill:#fff4e6
    style G fill:#fff4e6
    style L fill:#e8f5e9
```

**処理内容:**
```python
filter_condition = (
    df_full["曲名"].astype(str).str.contains(search_query, case=False, na=False) |
    df_full["アーティスト"].astype(str).str.contains(search_query, case=False, na=False)
)

if include_live_title:
    filter_condition = filter_condition | df_full["ライブタイトル"].astype(str).str.contains(
        search_query, case=False, na=False
    )

filtered_df = df_full[filter_condition].copy()
```

**特徴:**
- 部分一致検索（`str.contains`）
- 大文字小文字を区別しない（`case=False`）
- 欠損値を無視（`na=False`）
- OR条件で複数フィールドを検索

**要件:** 2.3, 2.4, 2.5, 2.6, 2.8, 3.2, 3.3


### セッション状態管理

```mermaid
stateDiagram-v2
    [*] --> 初期化: アプリ起動
    
    初期化 --> 全件表示: search_query=""
    全件表示 --> 検索実行: 検索ボタンクリック
    検索実行 --> 検索結果表示: filtered_df更新
    検索結果表示 --> 検索実行: 再検索
    検索結果表示 --> 段階的表示: さらに表示ボタン
    段階的表示 --> 検索結果表示: display_limit += 25
    
    state 初期化 {
        [*] --> search_query=""
        search_query="" --> filtered_df=df_full
        filtered_df=df_full --> include_live_title=True
        include_live_title=True --> display_limit=25
    }
```

**セッション状態変数:**
- `df_full`: 全データ（フィルタリング前）
- `filtered_df`: フィルタリング後のデータ
- `search_query`: 検索キーワード
- `include_live_title`: ライブタイトル検索フラグ
- `display_limit`: 表示件数制限

**要件:** 2.1, 2.2, 2.7, 5.1, 5.2, 5.3

## 表示処理のデータフロー

### 段階的表示フロー

```mermaid
graph TB
    A[filtered_df] --> B[表示用列の選択]
    B --> C[YouTubeリンクHTML生成]
    C --> D[アーティスト列スタイル適用]
    D --> E[不要列の削除]
    E --> F{display_limit<br/>< 総件数?}
    F -->|Yes| G[head display_limit]
    F -->|No| H[全件表示]
    G --> I[HTMLテーブル生成]
    H --> I
    I --> J[カスタムヘッダー適用]
    J --> K[スクロール可能div追加]
    K --> L[UI表示]
    
    M[さらに表示ボタン] -->|クリック| N[display_limit += 25]
    N --> O[ページ再読み込み]
    O --> A
    
    style F fill:#fff4e6
    style L fill:#e8f5e9
```


**処理内容:**
1. **列の選択**: 表示に必要な列のみを抽出
2. **HTMLリンク生成**: YouTubeタイムスタンプ付きURLをHTMLリンクに変換
3. **スタイル適用**: アーティスト列に`artist-cell`クラスを適用
4. **件数制限**: `head(display_limit)`で表示件数を制限
5. **HTML変換**: `to_html(escape=False)`でHTMLテーブルを生成
6. **カスタマイズ**: ヘッダーを短縮形に置き換え
7. **スクロール対応**: divタグで囲んで横スクロールを有効化

**要件:** 4.1, 4.2, 4.6, 5.1, 5.2, 5.3, 5.4, 6.4, 6.5

### HTML生成詳細

```mermaid
graph LR
    A[DataFrame] --> B[to_html]
    B --> C[HTMLテーブル]
    
    subgraph "オプション"
        O1[escape=False<br/>HTMLタグ有効]
        O2[index=False<br/>行番号非表示]
        O3[justify=left<br/>左寄せ]
        O4[classes=dataframe<br/>CSSクラス適用]
    end
    
    B -.設定.-> O1
    B -.設定.-> O2
    B -.設定.-> O3
    B -.設定.-> O4
    
    C --> D[ヘッダー置き換え]
    D --> E[スクロールdiv追加]
    E --> F[st.write<br/>unsafe_allow_html=True]
    
    style F fill:#e8f5e9
```

**生成されるHTML構造:**
```html
<div style="overflow-x: auto; max-width: 100%;">
    <table class="dataframe">
        <thead>
            <tr>
                <th>配信日</th>
                <th>No.</th>
                <th>曲名</th>
                <th>アーティスト</th>
                <th>リンク</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>2024/01/01</td>
                <td>1曲目</td>
                <td>曲名例</td>
                <td><div class="artist-cell">アーティスト名</div></td>
                <td><a href="..." target="_blank">YouTubeへ👻</a></td>
            </tr>
        </tbody>
    </table>
</div>
```

**要件:** 4.1, 4.2, 6.4, 6.5


## 楽曲リストページのデータフロー

### 楽曲リスト表示フロー

```mermaid
graph TB
    A[data/V_SONG_LIST.TSV] --> B[@st.cache_data<br/>load_data]
    B --> C[df_original]
    C --> D[ソート処理<br/>アーティスト ソート用]
    D --> E[df_sorted]
    E --> F[YouTubeリンク生成]
    F --> G[アーティスト列スタイル適用]
    G --> H[表示列選択]
    H --> I[HTMLテーブル生成]
    I --> J[UI表示]
    
    style B fill:#e1f5ff
    style J fill:#e8f5e9
```

**処理内容:**
1. **キャッシュ付き読み込み**: `@st.cache_data`デコレータで再読み込みを防ぐ
2. **ソート**: `アーティスト(ソート用)`列で大文字小文字を区別せずソート
3. **リンク生成**: 最近の歌唱URLをHTMLリンクに変換
4. **スタイル適用**: アーティスト列に改行許可のスタイルを適用
5. **表示**: 全件をHTMLテーブルで表示

**要件:** 8.1, 8.2, 8.3, 8.4, 8.5

### ソート処理詳細

```mermaid
graph TB
    A[df_original] --> B[sort_values]
    
    subgraph "ソート設定"
        S1[by=アーティスト ソート用]
        S2[na_position=last<br/>欠損値は最後]
        S3[key=lambda col: col.str.lower<br/>大文字小文字無視]
        S4[kind=mergesort<br/>安定ソート]
    end
    
    B -.設定.-> S1
    B -.設定.-> S2
    B -.設定.-> S3
    B -.設定.-> S4
    
    B --> C[df_sorted]
    
    style B fill:#e1f5ff
    style C fill:#e8f5e9
```

**ソート仕様:**
- `アーティスト(ソート用)`列を使用
- 大文字小文字を区別しない（`key=lambda col: col.str.lower()`）
- 欠損値は最後に配置（`na_position='last'`）
- 安定ソート（`kind='mergesort'`）で同一アーティスト内の曲順を維持

**β版の制約:**
- 漢字のソート順は完全ではない可能性があります

**要件:** 8.2, 8.3


## データモデルの関係

### エンティティ関係図（ER図）

```mermaid
erDiagram
    M_YT_LIVE ||--o{ M_YT_LIVE_TIMESTAMP : "1対多"
    M_YT_LIVE {
        int ID PK "配信ID"
        string 配信日 "配信日（UNIXミリ秒またはYYYY/MM/DD）"
        string タイトル "配信タイトル"
        string URL "YouTube配信URL"
    }
    
    M_YT_LIVE_TIMESTAMP {
        int ID PK "楽曲レコードID"
        int LIVE_ID FK "配信ID（外部キー）"
        string 曲名 "楽曲名"
        string アーティスト "アーティスト名"
        string タイムスタンプ "歌唱開始時刻（HH:MM:SSまたはMM:SS）"
    }
    
    V_SONG_LIST {
        string アーティスト "アーティスト名（表示用）"
        string アーティスト_ソート用 "アーティスト名（ソート用）"
        string 曲名 "楽曲名"
        string 最近の歌唱 "最近の歌唱へのYouTube URL"
    }
```

**関係性:**
- `M_YT_LIVE`（配信情報）と`M_YT_LIVE_TIMESTAMP`（楽曲情報）は1対多の関係
- 1つの配信に複数の楽曲が紐付く
- `LIVE_ID`が外部キーとして機能
- `V_SONG_LIST`は独立したビューで、他のテーブルとは直接の関係なし

**要件:** 1.1, 1.2, 1.5

### 結合後のデータモデル

```mermaid
classDiagram
    class df_merged {
        +int 楽曲ID
        +int LIVE_ID
        +string 曲名
        +string アーティスト
        +string タイムスタンプ
        +string ライブ配信日
        +datetime ライブ配信日_sortable
        +string ライブタイトル
        +string 元ライブURL
        +int タイムスタンプ_秒
        +string YouTubeタイムスタンプ付きURL
        +int 曲順
        +int ライブ番号
        +string 曲目
        +string YouTubeリンク
    }
    
    class df_full {
        <<session_state>>
        +DataFrame 全データ
    }
    
    class filtered_df {
        <<session_state>>
        +DataFrame フィルタリング後データ
    }
    
    df_merged --> df_full : 保存
    df_full --> filtered_df : 検索フィルタ適用
```


**派生カラム:**
- `楽曲ID`: 元の`ID_song`
- `ライブ配信日_sortable`: ソート用のdatetime型配信日
- `タイムスタンプ_秒`: タイムスタンプ文字列を秒数に変換
- `YouTubeタイムスタンプ付きURL`: 配信URL + タイムスタンプパラメータ
- `曲順`: 配信内での歌唱順序（1から始まる連番）
- `ライブ番号`: 同一日内の配信番号
- `曲目`: 表示用の曲目番号（例: "1-3曲目" または "3曲目"）
- `YouTubeリンク`: HTMLリンクタグ

## データ変換パイプライン

### 変換ステップの詳細

```mermaid
graph TB
    subgraph "入力データ"
        I1[配信日<br/>UNIXミリ秒 or YYYY/MM/DD]
        I2[タイムスタンプ<br/>HH:MM:SS or MM:SS]
        I3[配信URL]
    end
    
    subgraph "変換処理"
        T1[pd.to_datetime<br/>unit=ms]
        T2[pd.to_datetime<br/>errors=coerce]
        T3[convert_timestamp_to_seconds]
        T4[URL + &t= + 秒数 + s]
    end
    
    subgraph "出力データ"
        O1[ライブ配信日_sortable<br/>datetime]
        O2[タイムスタンプ_秒<br/>int]
        O3[YouTubeタイムスタンプ付きURL<br/>string]
    end
    
    I1 --> T1
    T1 -->|失敗時| T2
    T1 -->|成功時| O1
    T2 --> O1
    
    I2 --> T3
    T3 --> O2
    
    I3 --> T4
    O2 --> T4
    T4 --> O3
    
    style T1 fill:#e1f5ff
    style T2 fill:#e1f5ff
    style T3 fill:#e1f5ff
    style T4 fill:#e1f5ff
```

**変換ルール:**

1. **配信日変換:**
   - まずUNIXミリ秒として変換を試みる
   - 失敗した場合はYYYY/MM/DD形式として再変換
   - 両方失敗した場合はNaT（Not a Time）

2. **タイムスタンプ変換:**
   - コロン区切りで分割
   - 3要素（HH:MM:SS）: 時間×3600 + 分×60 + 秒
   - 2要素（MM:SS）: 分×60 + 秒
   - その他: None

3. **URL生成:**
   - 元URL + `&t=` + 秒数 + `s`
   - URLまたは秒数が欠損している場合は空文字列

**要件:** 1.5, 4.3, 6.1, 6.2, 6.3


## エラーハンドリングフロー

### ファイル読み込みエラー処理

```mermaid
graph TB
    A[ファイル読み込み試行] --> B{成功?}
    B -->|Yes| C[データ処理継続]
    B -->|No| D{エラー種類}
    
    D -->|FileNotFoundError| E[st.error<br/>ファイルが見つかりません]
    D -->|Exception| F[st.error<br/>読み込み中にエラー]
    
    E --> G[st.info<br/>対処方法を表示]
    F --> G
    
    G --> H[処理継続<br/>他のデータで動作]
    
    style D fill:#fff4e6
    style E fill:#ffebee
    style F fill:#ffebee
```

**エラーハンドリング戦略:**
- ファイルが見つからない場合: エラーメッセージと対処方法を表示
- その他のエラー: エラー内容を表示
- アプリケーションは停止せず、可能な範囲で動作を継続

**要件:** 1.3, 1.4, 13.1, 13.2, 13.4

### データ変換エラー処理

```mermaid
graph TB
    A[データ変換試行] --> B{成功?}
    B -->|Yes| C[変換済みデータ]
    B -->|No| D[st.warning<br/>変換エラー]
    
    D --> E[デフォルト値設定<br/>NaT or None]
    E --> F[処理継続]
    
    style D fill:#fff9c4
```

**変換エラー対応:**
- 日付変換失敗: NaT（Not a Time）を設定
- タイムスタンプ変換失敗: Noneを設定
- 警告メッセージを表示し、処理は継続

**要件:** 13.3, 13.4, 13.5

## パフォーマンス最適化

### キャッシュ戦略

```mermaid
graph TB
    A[load_data呼び出し] --> B{キャッシュ<br/>存在?}
    B -->|Yes| C[キャッシュから返却<br/>ファイルI/Oなし]
    B -->|No| D[ファイル読み込み]
    D --> E[キャッシュに保存]
    E --> F[データ返却]
    
    G[ファイル変更] --> H[キャッシュ無効化]
    H --> B
    
    style B fill:#fff4e6
    style C fill:#e8f5e9
```

**キャッシュ効果:**
- 初回読み込み後、ファイルI/Oが不要
- ページ再読み込み時の高速化
- サーバーリソースの節約

**要件:** 8.1


### 段階的表示による最適化

```mermaid
graph LR
    A[検索結果<br/>1000件] --> B[初期表示<br/>25件]
    B --> C{ユーザー<br/>アクション}
    C -->|さらに表示| D[表示件数<br/>+25件]
    D --> E[50件表示]
    E --> C
    C -->|満足| F[終了]
    
    style B fill:#e8f5e9
    style F fill:#e8f5e9
```

**最適化効果:**
- 初期表示速度の向上
- メモリ使用量の削減
- ユーザー体験の向上（必要な分だけ表示）

**要件:** 4.6, 5.1, 5.2, 5.3, 5.4

## データフロー実行例

### 具体的な実行例

**入力データ:**

`M_YT_LIVE.TSV`:
```
ID	配信日	タイトル	URL
1	2024/01/01	新年歌枠	https://youtube.com/watch?v=abc123
2	2024/01/01	深夜歌枠	https://youtube.com/watch?v=def456
```

`M_YT_LIVE_TIMESTAMP.TSV`:
```
ID	LIVE_ID	曲名	アーティスト	タイムスタンプ
1	1	曲A	アーティストX	0:05:30
2	1	曲B	アーティストY	0:15:45
3	2	曲C	アーティストZ	0:10:20
```

**処理フロー:**

1. **データ読み込み:**
   - `df_lives`: 2行（配信2件）
   - `df_songs`: 3行（楽曲3件）

2. **データ結合:**
   - `LIVE_ID`をキーとして結合
   - 結果: 3行（各楽曲に配信情報が紐付く）

3. **タイムスタンプ変換:**
   - `0:05:30` → 330秒
   - `0:15:45` → 945秒
   - `0:10:20` → 620秒

4. **ソート:**
   - 配信日: 2024/01/01（同一）
   - LIVE_ID: 1, 1, 2の順
   - タイムスタンプ: 330, 945, 620の順

5. **曲目番号生成:**
   - 同一日に2配信あり
   - 配信1: 1-1曲目, 1-2曲目
   - 配信2: 2-1曲目

6. **URL生成:**
   - `https://youtube.com/watch?v=abc123&t=330s`
   - `https://youtube.com/watch?v=abc123&t=945s`
   - `https://youtube.com/watch?v=def456&t=620s`

**最終出力:**
```
配信日      | No.    | 曲名 | アーティスト | リンク
2024/01/01 | 1-1曲目 | 曲A  | アーティストX | YouTubeへ👻
2024/01/01 | 1-2曲目 | 曲B  | アーティストY | YouTubeへ👻
2024/01/01 | 2-1曲目 | 曲C  | アーティストZ | YouTubeへ👻
```

## まとめ

本ドキュメントでは、「しのうたタイム」アプリケーションのデータフローを詳細に説明しました。

**主要なデータフロー:**
1. **データ読み込み**: TSVファイルからPandas DataFrameへ
2. **データ結合**: 配信情報と楽曲情報の紐付け
3. **データ変換**: タイムスタンプ、日付、URLの変換
4. **ソート**: 配信日・LIVE_ID・タイムスタンプによる並び替え
5. **検索**: キーワードによるフィルタリング
6. **表示**: 段階的表示とHTML生成

**データモデルの関係:**
- `M_YT_LIVE`と`M_YT_LIVE_TIMESTAMP`は1対多の関係
- `LIVE_ID`が外部キーとして機能
- 結合後のデータに派生カラムを追加

**最適化手法:**
- キャッシュによる再読み込み防止
- 段階的表示による初期表示速度向上
- セッション状態による検索結果の保持

このデータフローに基づいて、アプリケーションは効率的かつ安定的に動作します。
