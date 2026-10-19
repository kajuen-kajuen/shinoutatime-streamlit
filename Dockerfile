FROM python:3.14.8-slim-trixie

WORKDIR /app

# 依存パッケージのインストール(ローカルではテストと CLI も使うので開発用を入れる)
COPY requirements.txt requirements-tools.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# アプリケーションファイルのコピー
COPY . .

# Streamlitのポートを公開
EXPOSE 8501

# Streamlitサーバーの起動
CMD ["streamlit", "run", "Home.py", "--server.address", "0.0.0.0"]
