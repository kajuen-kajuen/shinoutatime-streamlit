# デプロイメントガイド

## 概要

本ドキュメントは、「しのうたタイム」アプリケーションをStreamlit Cloudにデプロイする手順を説明します。Streamlit Cloudは、Streamlitアプリケーションを無料でホスティングできるプラットフォームです。

## 前提条件

デプロイを開始する前に、以下の準備が必要です：

1. **GitHubアカウント**: リポジトリをホストするため
2. **Streamlit Cloudアカウント**: [https://streamlit.io/cloud](https://streamlit.io/cloud) から無料で作成可能
3. **リポジトリの準備**: アプリケーションコードがGitHubリポジトリにプッシュされていること

## デプロイ手順

### ステップ1: GitHubリポジトリの準備

#### 1.1 リポジトリの作成

GitHubで新しいリポジトリを作成するか、既存のリポジトリを使用します。

```bash
# 新規リポジトリの場合
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/your-repo-name.git
git push -u origin main
```

#### 1.2 必要なファイルの確認

リポジトリに以下のファイルが含まれていることを確認してください：

- `Home.py` - メインアプリケーションファイル
- `requirements.txt` - 依存パッケージリスト
- `pages/` - ページファイルのディレクトリ
- `data/` - データファイルのディレクトリ
- `footer.py` - フッターモジュール
- `style.css` - カスタムCSSファイル

#### 1.3 .gitignoreの設定

機密情報や不要なファイルをリポジトリに含めないよう、`.gitignore`ファイルを設定します：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Streamlit
.streamlit/secrets.toml

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# データファイル
# 注意: データファイルは通常リポジトリに含めますが、
# 機密情報が含まれる場合は除外してください
# data/sensitive_data.tsv
```

### ステップ2: Streamlit Cloudへのデプロイ

#### 2.1 Streamlit Cloudにログイン

1. [https://streamlit.io/cloud](https://streamlit.io/cloud) にアクセス
2. 「Sign up」または「Sign in」をクリック
3. GitHubアカウントで認証

#### 2.2 新しいアプリの作成

1. Streamlit Cloudダッシュボードで「New app」ボタンをクリック
2. 以下の情報を入力：
   - **Repository**: デプロイするGitHubリポジトリを選択
   - **Branch**: デプロイするブランチ（通常は`main`または`master`）
   - **Main file path**: `Home.py`
3. 「Advanced settings」をクリック（必要に応じて環境変数を設定）
4. 「Deploy!」ボタンをクリック

#### 2.3 デプロイの確認

- デプロイプロセスが開始され、ログがリアルタイムで表示されます
- 通常、数分でデプロイが完了します
- デプロイが成功すると、アプリのURLが表示されます（例: `https://your-app-name.streamlit.app`）

### ステップ3: デプロイ後の確認

#### 3.1 アプリの動作確認

デプロイされたアプリにアクセスし、以下の項目を確認してください：

- [ ] ホームページが正常に表示される
- [ ] 検索機能が動作する
- [ ] データが正しく読み込まれている
- [ ] YouTubeリンクが正常に機能する
- [ ] 各ページ（Information、About Us、Song List）が表示される
- [ ] CSSスタイルが適用されている
- [ ] フッターが表示されている

#### 3.2 エラーの確認

エラーが発生した場合：

1. Streamlit Cloudダッシュボードで「Manage app」をクリック
2. 「Logs」タブでエラーログを確認
3. エラー内容に基づいて修正を行い、GitHubにプッシュ
4. Streamlit Cloudが自動的に再デプロイを実行

## 環境変数の設定

### 環境変数が必要な場合

現在の「しのうたタイム」アプリケーションは環境変数を使用していませんが、将来的に以下のような情報を環境変数として管理する場合があります：

- API キー（YouTube Data API など）
- データベース接続情報
- 外部サービスの認証情報

### Streamlit Cloudでの環境変数設定方法

#### 方法1: Streamlit Cloud UI経由

1. Streamlit Cloudダッシュボードで対象アプリを選択
2. 「Settings」→「Secrets」をクリック
3. TOML形式で環境変数を入力：

```toml
# 例: API キーの設定
api_key = "your-api-key-here"
database_url = "your-database-url"

# セクション付きの設定
[database]
host = "localhost"
port = 5432
username = "user"
password = "password"
```

4. 「Save」をクリック

#### 方法2: ローカルでのテスト

ローカル環境でシークレットをテストする場合：

1. `.streamlit/secrets.toml` ファイルを作成（このファイルは`.gitignore`に含める）
2. 同じTOML形式で環境変数を記述
3. アプリケーション内で以下のようにアクセス：

```python
import streamlit as st

# シークレットへのアクセス
api_key = st.secrets["api_key"]

# セクション付きシークレットへのアクセス
db_host = st.secrets["database"]["host"]
```

### セキュリティのベストプラクティス

- **絶対にシークレットをGitHubにコミットしない**
- `.streamlit/secrets.toml` を `.gitignore` に追加
- API キーやパスワードは環境変数として管理
- 定期的にシークレットをローテーション

## デプロイ時の注意事項

### 1. リソース制限

Streamlit Cloudの無料プランには以下の制限があります：

- **メモリ**: 1GB
- **CPU**: 共有CPU
- **ストレージ**: リポジトリサイズに依存
- **同時実行**: 限定的

#### 対策

- データファイルのサイズを最適化
- `@st.cache_data` デコレータを活用してキャッシュを有効化
- 不要なデータの読み込みを避ける
- 大量データの場合は外部データベースの使用を検討

### 2. データファイルの管理

#### 2.1 データファイルのサイズ

- TSVファイルが大きい場合、リポジトリサイズが増大
- GitHubの推奨リポジトリサイズは1GB未満
- 大規模データの場合は外部ストレージ（S3、Google Cloud Storageなど）の使用を検討

#### 2.2 データの更新

データファイルを更新する場合：

1. ローカルでデータファイルを更新
2. GitHubにコミット＆プッシュ
3. Streamlit Cloudが自動的に再デプロイ
4. キャッシュがクリアされ、新しいデータが反映される

#### 2.3 データのバックアップ

- 定期的にデータファイルをバックアップ
- GitHubのバージョン管理を活用
- 重要なデータは複数の場所に保存

### 3. 自動デプロイ

Streamlit Cloudは、GitHubリポジトリの変更を検知して自動的に再デプロイします：

- **トリガー**: `main`ブランチへのプッシュ
- **デプロイ時間**: 通常2〜5分
- **ダウンタイム**: 最小限（数秒程度）

#### 自動デプロイの無効化

必要に応じて自動デプロイを無効化できます：

1. Streamlit Cloudダッシュボードで「Settings」をクリック
2. 「Auto-deploy」をオフに設定
3. 手動で「Reboot」ボタンをクリックしてデプロイ

### 4. カスタムドメインの設定

Streamlit Cloudでは、カスタムドメインの設定が可能です（有料プランで利用可能）：

1. ドメインを取得（例: `shinouta-time.com`）
2. Streamlit Cloudダッシュボードで「Settings」→「Custom domain」をクリック
3. ドメインプロバイダーでCNAMEレコードを設定
4. Streamlit Cloudで設定を完了

### 5. パフォーマンス最適化

#### 5.1 キャッシュの活用

```python
import streamlit as st
import pandas as pd

@st.cache_data
def load_data(file_path):
    """データを読み込み、キャッシュする"""
    return pd.read_csv(file_path, delimiter="\t")

# キャッシュされたデータの使用
df = load_data("data/M_YT_LIVE.TSV")
```

#### 5.2 遅延読み込み

- 必要なデータのみを読み込む
- ページごとにデータを分割
- 段階的表示機能を活用

#### 5.3 画像の最適化

- 画像ファイルを圧縮
- 適切なフォーマット（WebP、JPEG）を使用
- 不要な画像は削除

### 6. エラーハンドリング

デプロイ環境では、ローカル環境と異なるエラーが発生する可能性があります：

#### 6.1 ファイルパスの問題

```python
import os

# 相対パスを使用
data_path = os.path.join(os.path.dirname(__file__), "data", "M_YT_LIVE.TSV")

# または、カレントディレクトリからの相対パス
data_path = "data/M_YT_LIVE.TSV"
```

#### 6.2 エンコーディングの問題

```python
# UTF-8エンコーディングを明示的に指定
df = pd.read_csv("data/M_YT_LIVE.TSV", delimiter="\t", encoding="utf-8")
```

#### 6.3 依存関係の問題

- `requirements.txt` にすべての依存パッケージを記載
- バージョンを明示的に指定（推奨）

```txt
streamlit==1.28.0
pandas==2.1.0
```

### 7. モニタリングとログ

#### 7.1 アプリケーションログの確認

Streamlit Cloudダッシュボードで：

1. 対象アプリを選択
2. 「Manage app」→「Logs」をクリック
3. リアルタイムログを確認

#### 7.2 エラー通知

Streamlit Cloudは、アプリがクラッシュした場合にメール通知を送信します（設定で有効化可能）。

### 8. セキュリティ考慮事項

#### 8.1 認証の追加

公開アプリに認証を追加する場合：

```python
import streamlit as st

def check_password():
    """パスワード認証を実装"""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    # アプリのメインコンテンツ
    st.write("Welcome!")
```

#### 8.2 HTTPS

Streamlit Cloudは自動的にHTTPSを提供します。追加の設定は不要です。

#### 8.3 CORS設定

Streamlit Cloudは、デフォルトで適切なCORS設定を行います。

### 9. トラブルシューティング

#### 問題1: アプリが起動しない

**原因**:
- `requirements.txt` の依存関係の問題
- メインファイルのパスが間違っている
- Pythonバージョンの不一致

**解決策**:
1. ログを確認してエラーメッセージを特定
2. `requirements.txt` を確認
3. ローカル環境で動作確認
4. Pythonバージョンを指定（`.streamlit/config.toml` または `runtime.txt`）

#### 問題2: データが表示されない

**原因**:
- データファイルのパスが間違っている
- データファイルがリポジトリに含まれていない
- エンコーディングの問題

**解決策**:
1. ファイルパスを確認
2. GitHubリポジトリにデータファイルが含まれているか確認
3. エンコーディングを明示的に指定

#### 問題3: メモリ不足エラー

**原因**:
- データファイルが大きすぎる
- キャッシュが効いていない
- メモリリークの可能性

**解決策**:
1. `@st.cache_data` を使用してキャッシュを有効化
2. データを分割して読み込む
3. 不要なデータを削除
4. 有料プランへのアップグレードを検討

#### 問題4: CSSが適用されない

**原因**:
- `style.css` ファイルのパスが間違っている
- ファイルがリポジトリに含まれていない

**解決策**:
1. ファイルパスを確認
2. GitHubリポジトリに `style.css` が含まれているか確認
3. エンコーディングを確認（UTF-8）

## デプロイのベストプラクティス

### 1. 開発フロー

推奨される開発フローは以下の通りです：

1. **ローカル開発**: ローカル環境で機能を開発・テスト
2. **ブランチ作成**: 新機能用のブランチを作成
3. **コミット**: 変更をコミット
4. **プッシュ**: GitHubにプッシュ
5. **プルリクエスト**: `main` ブランチへのプルリクエストを作成
6. **レビュー**: コードレビューを実施
7. **マージ**: `main` ブランチにマージ
8. **自動デプロイ**: Streamlit Cloudが自動的にデプロイ

### 2. バージョン管理

- セマンティックバージョニングを使用（例: v1.0.0）
- タグを使用してリリースを管理
- CHANGELOGを維持

### 3. テスト

デプロイ前に以下のテストを実施：

- [ ] ローカル環境での動作確認
- [ ] すべてのページが正常に表示される
- [ ] 検索機能が動作する
- [ ] データが正しく読み込まれる
- [ ] エラーハンドリングが機能する
- [ ] レスポンシブデザインが機能する

### 4. ドキュメント

- README.mdを最新の状態に保つ
- デプロイ手順を文書化
- トラブルシューティング情報を追加

## まとめ

Streamlit Cloudへのデプロイは、以下の手順で簡単に実行できます：

1. GitHubリポジトリを準備
2. Streamlit Cloudでアカウントを作成
3. 「New app」からアプリをデプロイ
4. 環境変数を設定（必要に応じて）
5. デプロイ後の動作確認

デプロイ後は、GitHubへのプッシュで自動的に更新されるため、継続的なメンテナンスが容易です。

## 参考リンク

- [Streamlit Cloud公式ドキュメント](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
- [GitHub公式ドキュメント](https://docs.github.com/)
- [Streamlit Community Forum](https://discuss.streamlit.io/)

## サポート

デプロイに関する問題が発生した場合：

1. Streamlit Cloudのログを確認
2. [Streamlit Community Forum](https://discuss.streamlit.io/) で質問
3. GitHubのIssueを作成
4. プロジェクト管理者に連絡

---

**最終更新日**: 2025年11月18日  
**対象バージョン**: Streamlit Cloud (2025年11月時点)
