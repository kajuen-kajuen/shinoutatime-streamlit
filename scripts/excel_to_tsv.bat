@echo off
chcp 65001 > nul
REM Excel to TSV変換統合ツール
REM 使用方法: excel_to_tsv.bat [mode]
REM   mode: full (デフォルト) - TSV変換 + song_list_generator
REM         tsv_only - TSV変換のみ
REM         dryrun - ドライラン（ファイル生成なし）

setlocal enabledelayedexpansion

set MODE=%1
if "%MODE%"=="" set MODE=full

if "%MODE%"=="full" goto mode_full
if "%MODE%"=="tsv_only" goto mode_tsv_only
if "%MODE%"=="dryrun" goto mode_dryrun
goto mode_invalid

:mode_full
set SCRIPT_TITLE=Excel to TSV変換ツール（完全版）
set SCRIPT_DESC=このツールは以下の処理を実行します:
set SCRIPT_DESC2=  1. data.xlsx から M_YT_LIVE.TSV と M_YT_LIVE_TIMESTAMP.TSV を生成
set SCRIPT_DESC3=  2. song_list_generator を実行して V_SONG_LIST.TSV を生成
set CLI_ARGS=
set OUTPUT_FILES=   - data\M_YT_LIVE.TSV
set OUTPUT_FILES2=   - data\M_YT_LIVE_TIMESTAMP.TSV
set OUTPUT_FILES3=   - data\V_SONG_LIST.TSV
goto mode_done

:mode_tsv_only
set SCRIPT_TITLE=Excel to TSV変換ツール（TSVのみ）
set SCRIPT_DESC=このツールは以下の処理を実行します:
set SCRIPT_DESC2=  1. data.xlsx から M_YT_LIVE.TSV と M_YT_LIVE_TIMESTAMP.TSV を生成
set CLI_ARGS=--skip-song-list
set OUTPUT_FILES=   - data\M_YT_LIVE.TSV
set OUTPUT_FILES2=   - data\M_YT_LIVE_TIMESTAMP.TSV
goto mode_done

:mode_dryrun
set SCRIPT_TITLE=Excel to TSV変換ツール（ドライランモード）
set SCRIPT_DESC=このモードでは、実際のファイルを生成せずに処理内容を確認できます
set SCRIPT_DESC2=
set SCRIPT_DESC3=
set CLI_ARGS=--dry-run
set DRYRUN_MSG= (No files will be created)
goto mode_done

:mode_invalid
echo エラー: 無効なモードが指定されました
echo 使用可能なモード: full, tsv_only, dryrun
pause
exit /b 1

:mode_done

echo ============================================================
echo !SCRIPT_TITLE!
echo ============================================================
if defined SCRIPT_DESC echo !SCRIPT_DESC!
if defined SCRIPT_DESC2 echo !SCRIPT_DESC2!
if defined SCRIPT_DESC3 echo !SCRIPT_DESC3!
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
if defined DRYRUN_MSG echo !DRYRUN_MSG!
echo.
docker-compose exec -T shinouta-time python -m src.cli.excel_to_tsv_cli %CLI_ARGS%

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo 変換が正常に完了しました！
    echo ============================================================
    echo.
    if defined OUTPUT_FILES echo 生成されたファイル:
    if defined OUTPUT_FILES echo !OUTPUT_FILES!
    if defined OUTPUT_FILES2 echo !OUTPUT_FILES2!
    if defined OUTPUT_FILES3 echo !OUTPUT_FILES3!
    echo.
    echo バックアップファイルは data\backups\ に保存されています
    echo.
) else (
    echo.
    echo ============================================================
    if "%MODE%"=="dryrun" (
        echo ドライラン完了
    ) else (
        echo エラー: 変換処理に失敗しました
    )
    echo ============================================================
    echo.
    if "%MODE%"=="dryrun" (
        echo To generate files, run:
        echo   - excel_to_tsv.bat tsv_only (TSV files only)
        echo   - excel_to_tsv.bat full (TSV + V_SONG_LIST.TSV)
    ) else (
        echo TSVファイルは生成されている可能性があります
        echo 詳細は上記のログを確認してください
    )
    echo.
)

pause