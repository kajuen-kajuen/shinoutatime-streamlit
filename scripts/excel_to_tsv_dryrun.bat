@echo off
chcp 65001 > nul
REM Excel to TSV変換ツール ドライラン実行バッチファイル
REM このバッチファイルは、実際のファイルを生成せずに処理内容を確認します

echo ============================================================
echo Excel to TSV変換ツール（ドライランモード）
echo ============================================================
echo このモードでは、実際のファイルを生成せずに処理内容を確認できます
echo ============================================================
echo.

REM Dockerコンテナが起動しているか確認
echo [1/3] Docker container status check...
docker-compose ps | findstr "shinouta-time" | findstr "Up" > nul
if %errorlevel% neq 0 (
    echo Dockerコンテナが起動していません。起動します...
    docker-compose up -d
    if %errorlevel% neq 0 (
        echo エラー: Dockerコンテナの起動に失敗しました
        pause
        exit /b 1
    )
    echo Dockerコンテナを起動しました
    echo 起動を待機しています...
    timeout /t 5 /nobreak > nul
) else (
    echo Dockerコンテナは既に起動しています
)
echo.

REM data.xlsxファイルの存在確認
echo [2/3] Input file check...
if not exist "data\data.xlsx" (
    echo エラー: data\data.xlsx が見つかりません
    echo data\data.xlsx を配置してから再度実行してください
    pause
    exit /b 1
)
echo 入力ファイル: data\data.xlsx
echo.

REM Excel to TSV変換をドライランモードで実行
echo [3/3] Running in dry-run mode...
echo (No files will be created)
echo.
docker-compose exec -T shinouta-time python -m src.cli.excel_to_tsv_cli --dry-run

echo.
echo ============================================================
echo ドライラン完了
echo ============================================================
echo.
echo To generate files, run:
echo   - excel_to_tsv_converter.bat (TSV files only)
echo   - excel_to_tsv_full.bat (TSV + V_SONG_LIST.TSV)
echo.

pause
