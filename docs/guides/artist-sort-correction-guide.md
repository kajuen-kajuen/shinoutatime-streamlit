# アーティスト名ソート修正機能 使い方

## 概要

この機能は、V_SONG_LIST.TSVのアーティスト名（ソート用）が誤っている場合に修正できる仕組みを提供します。

自動生成されたソート名が誤っている場合や、特殊な読み方をするアーティスト名に対して、正しいソート名を手動で設定できます。

## 背景

現在、アーティスト名（ソート用）は`ArtistSortGenerator`クラスによって自動的にひらがなに変換されていますが、以下のような問題があります：

- 自動変換が誤った読み仮名を生成する場合がある
- 特殊な読み方をするアーティスト名に対応できない
- 一度生成されたソート名を手動で修正する手段がない

本機能により、これらの問題を解決できます。

---

## 修正マッピングファイルについて

### ファイルの場所

修正マッピングは以下のファイルに保存されます：

```
data/artist_sort_mapping.tsv
```

### ファイル形式

TSV（タブ区切り）形式で、UTF-8エンコーディングで保存されます。

**構造**:
```
アーティスト名	ソート名
Vaundy	Vaundy
米津玄師	よねづけんし
Official髭男dism	おふぃしゃるひげだんでぃずむ
```

**ルール**:
- 1行目はヘッダー行（`アーティスト名`と`ソート名`）
- 2行目以降がデータ行
- 各行はタブ文字で区切られた2つのフィールドを持つ
- 空行は無視される
- 重複したアーティスト名がある場合、最後のエントリが有効

---

## CLIコマンドの使い方

### 基本的な使い方

アーティスト名ソート修正機能は、コマンドラインから操作します。

```bash
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli <サブコマンド> [引数]
```

### サブコマンド一覧

#### 1. add - 修正マッピングを追加

新しい修正マッピングを追加します。既存のマッピングがある場合は更新されます。

**使い方**:
```bash
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli add "アーティスト名" "ソート名"
```

**例**:
```bash
# Vaundyのソート名を設定
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli add "Vaundy" "Vaundy"

# 米津玄師のソート名を設定
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli add "米津玄師" "よねづけんし"

# Official髭男dismのソート名を設定
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli add "Official髭男dism" "おふぃしゃるひげだんでぃずむ"
```

**出力例**:
```
修正マッピングを追加しました: Vaundy -> Vaundy
```

---

#### 2. list - 修正マッピングを一覧表示

現在登録されているすべての修正マッピングを表示します。

**使い方**:
```bash
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli list
```

**出力例**:
```
現在の修正マッピング:
Vaundy -> Vaundy
米津玄師 -> よねづけんし
Official髭男dism -> おふぃしゃるひげだんでぃずむ
```

マッピングが登録されていない場合:
```
修正マッピングは登録されていません。
```

---

#### 3. delete - 修正マッピングを削除

指定したアーティスト名の修正マッピングを削除します。

**使い方**:
```bash
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli delete "アーティスト名"
```

**例**:
```bash
# Vaundyのマッピングを削除
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli delete "Vaundy"
```

**出力例**:
```
修正マッピングを削除しました: Vaundy
```

存在しないマッピングを削除しようとした場合:
```
エラー: 'Vaundy' の修正マッピングは存在しません。
```

---

#### 4. update - 修正マッピングを更新

既存の修正マッピングを新しい値で更新します。（`add`コマンドと同じ動作）

**使い方**:
```bash
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli update "アーティスト名" "新しいソート名"
```

**例**:
```bash
# Vaundyのソート名を更新
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli update "Vaundy" "ばうんでぃ"
```

**出力例**:
```
修正マッピングを更新しました: Vaundy -> ばうんでぃ
```

---

## 使用例

### 例1: 英語アーティスト名のソート名を設定

英語のアーティスト名は、そのままソート名として使用したい場合があります。

```bash
# Vaundyはそのまま"Vaundy"でソート
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli add "Vaundy" "Vaundy"

# YOASOBIはそのまま"YOASOBI"でソート
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli add "YOASOBI" "YOASOBI"
```

### 例2: 特殊な読み方をするアーティスト名を修正

自動変換が誤った読み仮名を生成する場合に修正します。

```bash
# Official髭男dismの正しい読み方を設定
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli add "Official髭男dism" "おふぃしゃるひげだんでぃずむ"

# ずっと真夜中でいいのに。の正しい読み方を設定
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli add "ずっと真夜中でいいのに。" "ずっとまよなかでいいのに"
```

### 例3: 修正マッピングの確認と削除

```bash
# 現在のマッピングを確認
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli list

# 不要なマッピングを削除
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli delete "Vaundy"

# 削除後の確認
docker exec shinoutatime-streamlit-shinouta-time-1 python -m src.cli.artist_sort_cli list
```

---

## 修正マッピングの適用

修正マッピングは、曲リスト生成時に自動的に適用されます。

### 適用の優先順位

1. **修正マッピングファイルに登録されているソート名**（最優先）
2. 自動生成されたソート名（修正マッピングがない場合）

### 曲リスト生成時の動作

`SongListService`が曲リストを生成する際、以下の流れでソート名が決定されます：

1. アーティスト名を取得
2. 修正マッピングファイルを確認
3. マッピングが存在する場合：
   - 修正マッピングのソート名を使用
   - ログに「修正マッピングを適用しました」と記録
4. マッピングが存在しない場合：
   - 自動変換でソート名を生成
   - ログに「自動生成されたソート名を使用しました」と記録

---

## ファイルを直接編集する場合

CLIコマンドを使わずに、修正マッピングファイルを直接編集することもできます。

### 手順

1. `data/artist_sort_mapping.tsv`をテキストエディタで開く
2. 以下の形式で行を追加：
   ```
   アーティスト名[TAB]ソート名
   ```
3. ファイルを保存（UTF-8エンコーディング）

### 注意事項

- タブ文字で区切る（スペースではない）
- UTF-8エンコーディングで保存する
- ヘッダー行（1行目）は削除しない
- 重複したアーティスト名がある場合、最後のエントリが有効

---

## トラブルシューティング

### エラー: 修正マッピングファイルの形式が不正です

**原因**: TSV形式が正しくない、またはカラム数が不足している

**解決方法**:
1. ファイルがタブ区切りになっているか確認
2. 各行に2つのフィールド（アーティスト名とソート名）があるか確認
3. ヘッダー行が存在するか確認

---

### エラー: 修正マッピングファイルへの書き込みに失敗しました

**原因**: ファイルへの書き込み権限がない、またはディスク容量不足

**解決方法**:
1. ファイルのアクセス権限を確認
2. ディスク容量を確認
3. ファイルが他のプログラムで開かれていないか確認

---

### エラー: 修正マッピングファイルのエンコーディングが不正です

**原因**: UTF-8以外のエンコーディングでファイルが保存されている

**解決方法**:
1. ファイルをUTF-8エンコーディングで保存し直す
2. テキストエディタの設定を確認

---

### 修正マッピングが適用されない

**原因**: ファイルパスが間違っている、またはファイルが読み込まれていない

**解決方法**:
1. `data/artist_sort_mapping.tsv`が存在するか確認
2. ファイルの内容が正しいか確認
3. ログを確認して、マッピングが読み込まれているか確認

---

## よくある質問

### Q: 修正マッピングはいつ適用されますか？

A: 曲リスト生成時（`SongListService.generate_song_list()`実行時）に自動的に適用されます。

### Q: 修正マッピングを追加した後、すぐに反映されますか？

A: はい。次回の曲リスト生成時から反映されます。

### Q: 既存の曲リストは自動的に更新されますか？

A: いいえ。修正マッピングを追加した後、曲リスト生成を再実行する必要があります。

### Q: 修正マッピングファイルを削除するとどうなりますか？

A: すべてのアーティスト名が自動変換されるようになります。修正マッピングは失われます。

### Q: 複数のアーティスト名を一度に追加できますか？

A: CLIコマンドでは1つずつ追加する必要があります。複数追加する場合は、ファイルを直接編集するか、CLIコマンドを複数回実行してください。

### Q: 修正マッピングファイルのバックアップは作成されますか？

A: 現在、自動バックアップ機能はありません。重要な変更を行う前に、手動でファイルをバックアップすることをお勧めします。

---

## サポート

問題が発生した場合は、以下の情報を確認してください:
- Docker コンテナが起動しているか
- `data/artist_sort_mapping.tsv`が存在するか（存在しない場合は自動作成されます）
- ファイルのエンコーディングがUTF-8か
- ファイルの形式が正しいか（タブ区切り、2カラム）

それでも解決しない場合は、ログの内容を確認してください。

---

## 関連ドキュメント

- [Excel to TSV変換ツール 使い方](./excel-to-tsv-guide.md)
- [開発者ガイド](./developer-guide.md)
- [ユーザーガイド](./user-guide.md)
