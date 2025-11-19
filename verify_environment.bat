@echo off
REM しのうたタイム - 環境構築動作確認スクリプト (Windows)
REM 
REM このスクリプトは、Docker Compose環境が正しく構築されたことを確認します。
REM 
REM 使用方法:
REM   verify_environment.bat

setlocal enabledelayedexpansion

echo ==========================================
echo しのうたタイム - 環境構築動作確認
echo ==========================================
echo.

REM 1. Dockerの確認
echo 1. Dockerの確認...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker がインストールされています
    docker --version
) else (
    echo [ERROR] Docker がインストールされていません
    echo    Docker Desktop をインストールしてください: https://www.docker.com/get-started
    exit /b 1
)
echo.

REM 2. Docker Composeの確認
echo 2. Docker Compose の確認...
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker Compose がインストールされています
    docker-compose --version
) else (
    echo [ERROR] Docker Compose がインストールされていません
    echo    Docker Compose をインストールしてください
    exit /b 1
)
echo.

REM 3. コンテナの起動確認
echo 3. コンテナの起動確認...
docker-compose ps | findstr "Up" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] コンテナが起動しています
    docker-compose ps
) else (
    echo [WARNING] コンテナが起動していません
    echo    コンテナを起動します...
    docker-compose up -d
    echo    起動完了を待っています（10秒）...
    timeout /t 10 /nobreak >nul
)
echo.

REM 4. データファイルの確認
echo 4. データファイルの確認...
docker-compose exec -T shinouta-time test -f data/M_YT_LIVE.TSV >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] M_YT_LIVE.TSV が存在します
) else (
    echo [ERROR] M_YT_LIVE.TSV が見つかりません
    exit /b 1
)

docker-compose exec -T shinouta-time test -f data/M_YT_LIVE_TIMESTAMP.TSV >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] M_YT_LIVE_TIMESTAMP.TSV が存在します
) else (
    echo [ERROR] M_YT_LIVE_TIMESTAMP.TSV が見つかりません
    exit /b 1
)

docker-compose exec -T shinouta-time test -f data/V_SONG_LIST.TSV >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] V_SONG_LIST.TSV が存在します
) else (
    echo [ERROR] V_SONG_LIST.TSV が見つかりません
    exit /b 1
)
echo.

REM 5. Pythonバージョンの確認
echo 5. Python バージョンの確認...
for /f "tokens=*" %%i in ('docker-compose exec -T shinouta-time python --version') do set PYTHON_VERSION=%%i
echo    %PYTHON_VERSION%
echo %PYTHON_VERSION% | findstr "Python 3.11" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python 3.11 が使用されています（本番環境と一致）
) else (
    echo [WARNING] Python 3.11 ではありません（本番環境と異なる可能性があります）
)
echo.

REM 6. 必須パッケージの確認
echo 6. 必須パッケージの確認...
docker-compose exec -T shinouta-time python -c "import streamlit" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Streamlit がインストールされています
) else (
    echo [ERROR] Streamlit がインストールされていません
    exit /b 1
)

docker-compose exec -T shinouta-time python -c "import pandas" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Pandas がインストールされています
) else (
    echo [ERROR] Pandas がインストールされていません
    exit /b 1
)

docker-compose exec -T shinouta-time python -c "import pytest" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] pytest がインストールされています
) else (
    echo [ERROR] pytest がインストールされていません
    exit /b 1
)
echo.

REM 7. 自動テストの実行
echo 7. 自動テストの実行...
echo    テストを実行しています（数秒かかります）...
echo.

docker-compose exec -T shinouta-time pytest tests/test_environment_verification.py -v
if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo [OK] 全てのテストが成功しました！
    echo ==========================================
    echo.
    echo 環境構築が正常に完了しました。
    echo.
    echo 次のステップ:
    echo   1. ブラウザで http://localhost:8501 にアクセス
    echo   2. アプリケーションの動作を確認
    echo.
) else (
    echo.
    echo ==========================================
    echo [ERROR] テストが失敗しました
    echo ==========================================
    echo.
    echo トラブルシューティング:
    echo   1. TROUBLESHOOTING.md を参照
    echo   2. docker-compose logs でログを確認
    echo   3. docker-compose down ^&^& docker-compose up -d で再起動
    echo.
    exit /b 1
)

endlocal
