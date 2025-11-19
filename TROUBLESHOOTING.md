# トラブルシューティングガイド

このドキュメントでは、「しのうたタイム」アプリケーションのローカル環境構築時によく発生する問題と、その解決方法をまとめています。

## 目次

1. [Docker関連の問題](#docker関連の問題)
2. [ポート関連の問題](#ポート関連の問題)
3. [データファイル関連の問題](#データファイル関連の問題)
4. [Python環境関連の問題](#python環境関連の問題)
5. [パッケージインストール関連の問題](#パッケージインストール関連の問題)
6. [文字エンコーディング関連の問題](#文字エンコーディング関連の問題)
7. [テスト関連の問題](#テスト関連の問題)

---

## Docker関連の問題

### 問題1: Dockerがインストールされていない

**症状**:
```
'docker' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

**原因**: Dockerがシステムにインストールされていません。

**解決方法**:

1. **Windows/Mac**: Docker Desktopをインストール
   - [Docker Desktop公式サイト](https://www.docker.com/products/docker-desktop)からダウンロード
   - インストーラーを実行してインストール
   - インストール後、システムを再起動

2. **Linux**: Docker Engineをインストール
   ```bash
   # Ubuntu/Debianの場合
   sudo apt-get update
   sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
   ```

3. インストール確認
   ```bash
   docker --version
   docker-compose --version
   ```

### 問題2: Dockerが起動していない

**症状**:
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
Is the docker daemon running?
```

**原因**: Dockerデーモンが起動していません。

**解決方法**:

- **Windows/Mac**: Docker Desktopを起動
  - タスクバー/メニューバーからDocker Desktopアイコンをクリック
  - 「Docker Desktop is running」と表示されるまで待つ

- **Linux**: Dockerサービスを起動
  ```bash
  sudo systemctl start docker
  sudo systemctl enable docker  # 自動起動を有効化
  ```

### 問題3: Dockerコンテナのビルドに失敗する

**症状**:
```
ERROR: failed to solve: failed to compute cache key
```

**原因**: ネットワーク接続の問題、またはDockerfileの記述エラー。

**解決方法**:

1. ネットワーク接続を確認
   ```bash
   ping google.com
   ```

2. Dockerのキャッシュをクリア
   ```bash
   docker-compose down
   docker system prune -a
   docker-compose build --no-cache
   ```

3. Dockerfileの構文を確認
   - Dockerfileに記述エラーがないか確認
   - 特にCOPY、RUN命令の記述を確認

### 問題4: コンテナが起動しない

**症状**:
```
Error response from daemon: driver failed programming external connectivity
```

**原因**: ポートの競合、またはリソース不足。

**解決方法**:

1. 既存のコンテナを停止
   ```bash
   docker-compose down
   docker ps -a  # 全てのコンテナを確認
   docker rm -f <container_id>  # 不要なコンテナを削除
   ```

2. Dockerのリソース設定を確認
   - Docker Desktop > Settings > Resources
   - メモリを4GB以上に設定することを推奨

---

## ポート関連の問題

### 問題5: ポート8501が既に使用されている

**症状**:
```
Error starting userland proxy: listen tcp4 0.0.0.0:8501: bind: address already in use
```

**原因**: ポート8501が他のプロセスで使用されています。

**解決方法**:

**方法1: 使用中のプロセスを停止**

- **Windows**:
  ```cmd
  netstat -ano | findstr :8501
  taskkill /PID <PID番号> /F
  ```

- **Mac/Linux**:
  ```bash
  lsof -i :8501
  kill -9 <PID番号>
  ```

**方法2: 別のポートを使用**

docker-compose.ymlを編集:
```yaml
services:
  shinouta-time:
    ports:
      - "8502:8501"  # ホスト側のポートを8502に変更
```

変更後、`http://localhost:8502`でアクセス

### 問題6: ポートにアクセスできない

**症状**: ブラウザで`http://localhost:8501`にアクセスしても接続できない。

**原因**: ファイアウォールの設定、またはコンテナが正常に起動していない。

**解決方法**:

1. コンテナの状態を確認
   ```bash
   docker-compose ps
   docker-compose logs
   ```

2. ファイアウォールの設定を確認
   - **Windows**: Windows Defenderファイアウォールでポート8501を許可
   - **Mac**: システム環境設定 > セキュリティとプライバシー > ファイアウォール

3. コンテナを再起動
   ```bash
   docker-compose restart
   ```

---

## データファイル関連の問題

### 問題7: データファイルが見つからない

**症状**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/M_YT_LIVE.TSV'
```

**原因**: 必要なデータファイルが存在しません。

**解決方法**:

1. dataディレクトリの存在を確認
   ```bash
   ls -la data/
   ```

2. 必須ファイルの確認
   - `data/M_YT_LIVE.TSV`
   - `data/M_YT_LIVE_TIMESTAMP.TSV`
   - `data/V_SONG_LIST.TSV`

3. ファイルが存在しない場合
   - Gitリポジトリを再クローン
   ```bash
   cd ..
   git clone https://github.com/your-repo/shinouta-time.git
   cd shinouta-time
   ```

4. ボリュームマウントの確認（Docker使用時）
   - docker-compose.ymlのvolumes設定を確認
   ```yaml
   volumes:
     - .:/app  # カレントディレクトリを/appにマウント
   ```

### 問題8: データファイルの読み込みエラー

**症状**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**原因**: データファイルの文字エンコーディングが正しくありません。

**解決方法**:

1. ファイルのエンコーディングを確認
   ```bash
   file -i data/M_YT_LIVE.TSV
   ```

2. UTF-8に変換（必要な場合）
   - テキストエディタで開いて「UTF-8で保存」
   - またはコマンドで変換:
   ```bash
   iconv -f SHIFT-JIS -t UTF-8 data/M_YT_LIVE.TSV > data/M_YT_LIVE_UTF8.TSV
   mv data/M_YT_LIVE_UTF8.TSV data/M_YT_LIVE.TSV
   ```

3. Pythonコードでエンコーディングを指定
   ```python
   df = pd.read_csv('data/M_YT_LIVE.TSV', sep='\t', encoding='utf-8')
   ```

---

## Python環境関連の問題

### 問題9: Pythonのバージョンが古い

**症状**:
```
Python 3.9.x
```

**原因**: Python 3.11が必要ですが、古いバージョンがインストールされています。

**解決方法**:

1. **推奨**: Docker Composeを使用
   - Dockerを使用すれば、ローカルのPythonバージョンに依存しません
   ```bash
   docker-compose up
   ```

2. Python 3.11をインストール

   - **Windows**:
     - [Python公式サイト](https://www.python.org/downloads/)からPython 3.11をダウンロード
     - インストール時に「Add Python to PATH」をチェック

   - **Mac** (Homebrewを使用):
     ```bash
     brew install python@3.11
     ```

   - **Linux** (Ubuntu/Debian):
     ```bash
     sudo apt-get update
     sudo apt-get install python3.11 python3.11-venv
     ```

3. バージョン確認
   ```bash
   python3.11 --version
   ```

### 問題10: 仮想環境のアクティベートに失敗

**症状** (Windows):
```
このシステムではスクリプトの実行が無効になっているため、
ファイル venv\Scripts\Activate.ps1 を読み込むことができません。
```

**原因**: PowerShellの実行ポリシーが制限されています。

**解決方法**:

1. PowerShellを管理者として実行

2. 実行ポリシーを変更
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. 仮想環境を再度アクティベート
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. または、コマンドプロンプト（cmd）を使用
   ```cmd
   venv\Scripts\activate.bat
   ```

---

## パッケージインストール関連の問題

### 問題11: pipのインストールに失敗

**症状**:
```
ERROR: Could not install packages due to an OSError
```

**原因**: ネットワーク接続の問題、権限の問題、またはキャッシュの破損。

**解決方法**:

1. pipをアップグレード
   ```bash
   python -m pip install --upgrade pip
   ```

2. キャッシュをクリア
   ```bash
   pip cache purge
   pip install -r requirements.txt --no-cache-dir
   ```

3. プロキシ設定（企業ネットワーク内の場合）
   ```bash
   pip install -r requirements.txt --proxy=http://proxy.example.com:8080
   ```

4. タイムアウトを延長
   ```bash
   pip install -r requirements.txt --timeout=100
   ```

### 問題12: 特定のパッケージのインストールに失敗

**症状**:
```
ERROR: Could not find a version that satisfies the requirement <package>
```

**原因**: パッケージ名の誤り、またはPythonバージョンの非互換性。

**解決方法**:

1. パッケージ名を確認
   - requirements.txtのスペルミスを確認

2. Pythonバージョンを確認
   ```bash
   python --version
   ```
   - Python 3.11を使用していることを確認

3. パッケージを個別にインストール
   ```bash
   pip install streamlit
   pip install pandas
   ```

4. 依存関係の問題を解決
   ```bash
   pip install -r requirements.txt --use-deprecated=legacy-resolver
   ```

---

## 文字エンコーディング関連の問題

### 問題13: 日本語が文字化けする

**症状**: アプリケーション内で日本語が正しく表示されない。

**原因**: 文字エンコーディングの設定が正しくありません。

**解決方法**:

1. ファイルをUTF-8で保存
   - すべての.pyファイルと.mdファイルをUTF-8で保存

2. Pythonファイルの先頭にエンコーディング宣言を追加
   ```python
   # -*- coding: utf-8 -*-
   ```

3. データファイルの読み込み時にエンコーディングを指定
   ```python
   df = pd.read_csv('data/M_YT_LIVE.TSV', sep='\t', encoding='utf-8')
   ```

4. 環境変数を設定（Windows）
   ```cmd
   set PYTHONIOENCODING=utf-8
   ```

### 問題14: コンソール出力が文字化けする

**症状** (Windows): コマンドプロンプトで日本語が文字化けする。

**原因**: コンソールの文字コードがUTF-8ではありません。

**解決方法**:

1. コマンドプロンプトの文字コードを変更
   ```cmd
   chcp 65001
   ```

2. PowerShellを使用
   - PowerShellはデフォルトでUTF-8をサポート

3. Windows Terminalを使用
   - [Microsoft Store](https://aka.ms/terminal)からインストール
   - UTF-8を標準でサポート

---

## テスト関連の問題

### 問題17: pytestが見つからない

**症状**:
```
bash: pytest: command not found
```

**原因**: pytestがインストールされていません。

**解決方法**:

1. **Docker環境の場合**: コンテナを再ビルド
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **ローカル環境の場合**: pytestをインストール
   ```bash
   pip install pytest
   ```

3. インストール確認
   ```bash
   pytest --version
   ```

### 問題18: テストが失敗する - データファイルが見つからない

**症状**:
```
AssertionError: 配信データファイルが見つかりません: data/M_YT_LIVE.TSV
```

**原因**: 必須データファイルが存在しません。

**解決方法**:

1. dataディレクトリの存在を確認
   ```bash
   docker-compose exec shinouta-time ls -la data/
   ```

2. 必須ファイルの確認
   - `data/M_YT_LIVE.TSV`
   - `data/M_YT_LIVE_TIMESTAMP.TSV`
   - `data/V_SONG_LIST.TSV`

3. ファイルが存在しない場合、リポジトリを再クローン
   ```bash
   git pull origin main
   ```

4. ボリュームマウントの確認
   - docker-compose.ymlのvolumes設定を確認
   ```yaml
   volumes:
     - .:/app
   ```

### 問題19: テストが失敗する - Pythonバージョンが一致しない

**症状**:
```
AssertionError: Pythonマイナーバージョンが11ではありません（本番環境と一致しません）
```

**原因**: Python 3.11以外のバージョンが使用されています。

**解決方法**:

1. **Docker環境の場合**: Dockerfileを確認
   ```dockerfile
   FROM python:3.11-slim
   ```

2. コンテナを再ビルド
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. Pythonバージョンを確認
   ```bash
   docker-compose exec shinouta-time python --version
   ```

4. **ローカル環境の場合**: Python 3.11をインストール
   - [問題9: Pythonのバージョンが古い](#問題9-pythonのバージョンが古い)を参照

### 問題20: テストが失敗する - モジュールが見つからない

**症状**:
```
ModuleNotFoundError: No module named 'streamlit'
```

**原因**: 必要なパッケージがインストールされていません。

**解決方法**:

1. **Docker環境の場合**: コンテナを再ビルド
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **ローカル環境の場合**: パッケージをインストール
   ```bash
   pip install -r requirements.txt
   ```

3. インストール確認
   ```bash
   pip list | grep streamlit
   pip list | grep pandas
   pip list | grep pytest
   ```

### 問題21: テストが失敗する - 検索結果が空

**症状**:
```
AssertionError: 検索結果に検索キーワードが含まれていません
```

**原因**: データファイルの内容が空、または検索機能に問題があります。

**解決方法**:

1. データファイルの内容を確認
   ```bash
   docker-compose exec shinouta-time head -n 5 data/M_YT_LIVE.TSV
   docker-compose exec shinouta-time head -n 5 data/M_YT_LIVE_TIMESTAMP.TSV
   ```

2. データファイルが空の場合、正しいデータファイルを配置

3. 検索機能のログを確認
   ```bash
   docker-compose logs shinouta-time
   ```

4. 特定のテストのみ実行して詳細を確認
   ```bash
   docker-compose exec shinouta-time pytest tests/test_environment_verification.py::TestEnvironmentVerification::test_search_functionality -v -s
   ```

### 問題22: テスト実行時にコンテナが起動していない

**症状**:
```
Error: No such container: shinouta-time
```

**原因**: Docker Composeでコンテナが起動していません。

**解決方法**:

1. コンテナの状態を確認
   ```bash
   docker-compose ps
   ```

2. コンテナを起動
   ```bash
   docker-compose up -d
   ```

3. コンテナが起動するまで待つ（数秒）
   ```bash
   docker-compose logs -f
   ```

4. テストを再実行
   ```bash
   docker-compose exec shinouta-time pytest tests/test_environment_verification.py -v
   ```

### 問題23: テストの実行が遅い

**症状**: テストの実行に時間がかかりすぎる。

**原因**: データファイルが大きい、またはシステムリソースが不足。

**解決方法**:

1. 特定のテストクラスのみ実行
   ```bash
   # 基本動作確認のみ
   docker-compose exec shinouta-time pytest tests/test_environment_verification.py::TestEnvironmentVerification -v
   ```

2. Dockerのリソース設定を増やす
   - Docker Desktop > Settings > Resources
   - CPUとメモリを増やす

3. キャッシュを有効化
   - 設定ファイルで`SHINOUTA_ENABLE_CACHE=true`を設定

4. 並列実行（pytest-xdistを使用）
   ```bash
   pip install pytest-xdist
   pytest tests/test_environment_verification.py -n auto
   ```

---

## その他の問題

### 問題15: Streamlitアプリケーションが自動的にリロードされない

**症状**: コードを変更しても、ブラウザに反映されない。

**原因**: Streamlitの自動リロード機能が無効、またはファイル監視の問題。

**解決方法**:

1. ブラウザを手動でリロード（F5キー）

2. Streamlitの設定を確認
   - `.streamlit/config.toml`を作成
   ```toml
   [server]
   runOnSave = true
   ```

3. Dockerの場合、ボリュームマウントを確認
   ```yaml
   volumes:
     - .:/app  # 正しくマウントされているか確認
   ```

4. Streamlitサーバーを再起動
   ```bash
   # Ctrl+C で停止
   streamlit run Home.py
   ```

### 問題16: メモリ不足エラー

**症状**:
```
MemoryError: Unable to allocate array
```

**原因**: データファイルが大きすぎる、またはシステムメモリが不足。

**解決方法**:

1. Dockerのメモリ設定を増やす
   - Docker Desktop > Settings > Resources
   - メモリを8GB以上に設定

2. データを分割して読み込む
   ```python
   # チャンク単位で読み込み
   for chunk in pd.read_csv('data/M_YT_LIVE.TSV', sep='\t', chunksize=1000):
       process(chunk)
   ```

3. 不要なデータをフィルタリング
   ```python
   # 必要な列のみ読み込み
   df = pd.read_csv('data/M_YT_LIVE.TSV', sep='\t', usecols=['col1', 'col2'])
   ```

---

## サポート

上記の解決方法で問題が解決しない場合は、以下の情報を含めてGitHubのIssueを作成してください：

1. 発生した問題の詳細な説明
2. エラーメッセージの全文
3. 使用している環境（OS、Pythonバージョン、Dockerバージョン）
4. 実行したコマンドと結果
5. 試した解決方法

GitHubリポジトリ: [your-repo-url]

---

## 関連ドキュメント

- [環境構築手順（SETUP.md）](SETUP.md)
- [README.md](README.md)
- [開発者ガイド（docs/developer-guide.md）](docs/developer-guide.md)
