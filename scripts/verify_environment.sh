#!/bin/bash
# しのうたタイム - 環境構築動作確認スクリプト
# 
# このスクリプトは、Docker Compose環境が正しく構築されたことを確認します。
# 
# 使用方法:
#   bash verify_environment.sh
#
# または:
#   chmod +x verify_environment.sh
#   ./verify_environment.sh

set -e  # エラーが発生したら即座に終了

echo "=========================================="
echo "しのうたタイム - 環境構築動作確認"
echo "=========================================="
echo ""

# 色の定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Dockerの確認
echo "1. Dockerの確認..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker がインストールされています"
    docker --version
else
    echo -e "${RED}✗${NC} Docker がインストールされていません"
    echo "   Docker Desktop をインストールしてください: https://www.docker.com/get-started"
    exit 1
fi
echo ""

# 2. Docker Composeの確認
echo "2. Docker Compose の確認..."
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose がインストールされています"
    docker-compose --version
else
    echo -e "${RED}✗${NC} Docker Compose がインストールされていません"
    echo "   Docker Compose をインストールしてください"
    exit 1
fi
echo ""

# 3. コンテナの起動確認
echo "3. コンテナの起動確認..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} コンテナが起動しています"
    docker-compose ps
else
    echo -e "${YELLOW}!${NC} コンテナが起動していません"
    echo "   コンテナを起動します..."
    docker-compose up -d
    echo "   起動完了を待っています（10秒）..."
    sleep 10
fi
echo ""

# 4. データファイルの確認
echo "4. データファイルの確認..."
if docker-compose exec -T shinouta-time test -f data/M_YT_LIVE.TSV; then
    echo -e "${GREEN}✓${NC} M_YT_LIVE.TSV が存在します"
else
    echo -e "${RED}✗${NC} M_YT_LIVE.TSV が見つかりません"
    exit 1
fi

if docker-compose exec -T shinouta-time test -f data/M_YT_LIVE_TIMESTAMP.TSV; then
    echo -e "${GREEN}✓${NC} M_YT_LIVE_TIMESTAMP.TSV が存在します"
else
    echo -e "${RED}✗${NC} M_YT_LIVE_TIMESTAMP.TSV が見つかりません"
    exit 1
fi

if docker-compose exec -T shinouta-time test -f data/V_SONG_LIST.TSV; then
    echo -e "${GREEN}✓${NC} V_SONG_LIST.TSV が存在します"
else
    echo -e "${RED}✗${NC} V_SONG_LIST.TSV が見つかりません"
    exit 1
fi
echo ""

# 5. Pythonバージョンの確認
echo "5. Python バージョンの確認..."
PYTHON_VERSION=$(docker-compose exec -T shinouta-time python --version)
echo "   ${PYTHON_VERSION}"
if echo "$PYTHON_VERSION" | grep -q "Python 3.11"; then
    echo -e "${GREEN}✓${NC} Python 3.11 が使用されています（本番環境と一致）"
else
    echo -e "${YELLOW}!${NC} Python 3.11 ではありません（本番環境と異なる可能性があります）"
fi
echo ""

# 6. 必須パッケージの確認
echo "6. 必須パッケージの確認..."
if docker-compose exec -T shinouta-time python -c "import streamlit" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Streamlit がインストールされています"
else
    echo -e "${RED}✗${NC} Streamlit がインストールされていません"
    exit 1
fi

if docker-compose exec -T shinouta-time python -c "import pandas" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Pandas がインストールされています"
else
    echo -e "${RED}✗${NC} Pandas がインストールされていません"
    exit 1
fi

if docker-compose exec -T shinouta-time python -c "import pytest" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} pytest がインストールされています"
else
    echo -e "${RED}✗${NC} pytest がインストールされていません"
    exit 1
fi
echo ""

# 7. 自動テストの実行
echo "7. 自動テストの実行..."
echo "   テストを実行しています（数秒かかります）..."
echo ""

if docker-compose exec -T shinouta-time pytest tests/test_environment_verification.py -v; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✓ 全てのテストが成功しました！"
    echo "==========================================${NC}"
    echo ""
    echo "環境構築が正常に完了しました。"
    echo ""
    echo "次のステップ:"
    echo "  1. ブラウザで http://localhost:8501 にアクセス"
    echo "  2. アプリケーションの動作を確認"
    echo ""
else
    echo ""
    echo -e "${RED}=========================================="
    echo "✗ テストが失敗しました"
    echo "==========================================${NC}"
    echo ""
    echo "トラブルシューティング:"
    echo "  1. TROUBLESHOOTING.md を参照"
    echo "  2. docker-compose logs でログを確認"
    echo "  3. docker-compose down && docker-compose up -d で再起動"
    echo ""
    exit 1
fi
