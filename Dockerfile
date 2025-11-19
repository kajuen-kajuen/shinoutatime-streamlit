FROM python:3.11-slim

WORKDIR /app

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY . .

# Streamlitのポートを公開
EXPOSE 8501

# Streamlitサーバーの起動
CMD ["streamlit", "run", "Home.py", "--server.address", "0.0.0.0"]
