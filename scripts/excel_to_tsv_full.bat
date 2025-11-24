@echo off
chcp 65001 > nul
REM Excel to TSV変換ツール自動実行バッチファイル（完全版）
REM このバッチファイルは、Excel to TSV変換とsong_list_generatorを実行します

echo ============================================================
echo Excel to TSV変換ツール（完全版）
echo ============================================================
echo このツールは以下の処理を実行します:
echo   1. data.xlsx から M_YT_LIVE.TSV と M_YT_LIVE_TIMESTAMP.TSV を生成
echo   2. song_list_generator を実行して V_SONG_LIST.TSV を生成
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

REM Excel to TSV変換を実行（song_list_generatorも含む）
echo [3/3] Running Excel to TSV conversion (with song_list_generator)...
echo.
docker-compose exec -T shinouta-time python -m src.cli.excel_to_tsv_cli

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo 変換が正常に完了しました！
    echo ============================================================
    echo.
    echo 生成されたファイル:
    echo   - data\M_YT_LIVE.TSV
    echo   - data\M_YT_LIVE_TIMESTAMP.TSV
    echo   - data\V_SONG_LIST.TSV
    echo.
    echo バックアップファイルは data\backups\ に保存されています
    echo.
) else (
    echo.
    echo ============================================================
    echo 警告: 一部の処理に失敗しました
    echo ============================================================
    echo.
    echo TSVファイルは生成されている可能性があります
    echo 詳細は上記のログを確認してください
    echo.
)

pause
