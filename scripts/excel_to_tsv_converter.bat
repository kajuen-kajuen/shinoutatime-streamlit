@echo off
chcp 65001 > nul
REM Excel to TSV変換ツール自動実行バッチファイル
REM このバッチファイルは、Dockerコンテナ内でExcel to TSV変換を実行します

echo ============================================================
echo Excel to TSV変換ツール
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

REM Excel to TSV変換を実行
echo [3/3] Running Excel to TSV conversion...
echo.
docker-compose exec -T shinouta-time python -m src.cli.excel_to_tsv_cli --skip-song-list

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo 変換が正常に完了しました！
    echo ============================================================
    echo.
    echo 生成されたファイル:
    echo   - data\M_YT_LIVE.TSV
    echo   - data\M_YT_LIVE_TIMESTAMP.TSV
    echo.
    echo バックアップファイルは data\backups\ に保存されています
    echo.
) else (
    echo.
    echo ============================================================
    echo エラー: 変換処理に失敗しました
    echo ============================================================
    echo.
    echo 詳細は上記のログを確認してください
    echo.
)

pause
