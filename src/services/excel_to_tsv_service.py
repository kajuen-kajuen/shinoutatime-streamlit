"""
Excel to TSV変換サービスモジュール

ExcelファイルからTSVファイルへの変換処理を管理します。
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import Any, List, Optional

from src.models.excel_to_tsv_models import (
    ConversionResult,
    SheetMapping,
    ValidationWarning,
)
from src.repositories.excel_repository import ExcelRepository
from src.repositories.tsv_repository import TsvRepository
from src.repositories.backup_repository import BackupRepository
from src.exceptions.errors import DataLoadError, DataSaveError


# デフォルトのシートマッピング設定
DEFAULT_SHEET_MAPPINGS = [
    SheetMapping(
        sheet_name="M_YT_LIVE",
        output_file="M_YT_LIVE.TSV",
        headers=["ID", "配信日", "タイトル", "URL"],
        required_fields=["ID", "配信日", "タイトル", "URL"]
    ),
    SheetMapping(
        sheet_name="M_YT_LIVE_TIMESTAMP",
        output_file="M_YT_LIVE_TIMESTAMP.TSV",
        headers=["ID", "LIVE_ID", "タイムスタンプ", "曲名", "アーティスト"],
        required_fields=["ID", "LIVE_ID", "タイムスタンプ", "曲名", "アーティスト"]
    )
]


class ExcelToTsvService:
    """
    Excel to TSV変換サービス
    
    ExcelファイルからTSVファイルへの変換処理を管理します。
    """
    
    def __init__(
        self,
        excel_repo: ExcelRepository,
        tsv_repo: TsvRepository,
        backup_repo: BackupRepository
    ):
        """
        サービスを初期化
        
        Args:
            excel_repo: Excelリポジトリ
            tsv_repo: TSVリポジトリ
            backup_repo: バックアップリポジトリ
        """
        self.excel_repo = excel_repo
        self.tsv_repo = tsv_repo
        self.backup_repo = backup_repo
        self.logger = logging.getLogger(__name__)
        self.sheet_mappings = DEFAULT_SHEET_MAPPINGS
    
    def convert_excel_to_tsv(
        self,
        input_file: str,
        output_dir: str,
        dry_run: bool = False
    ) -> ConversionResult:
        """
        ExcelファイルをTSVファイルに変換
        
        Args:
            input_file: 入力Excelファイルのパス
            output_dir: 出力ディレクトリのパス
            dry_run: ドライランモード（ファイルを書き込まない）
            
        Returns:
            変換処理の結果
        """
        self.logger.info(f"変換処理を開始します: {input_file}")
        
        files_created = []
        warnings = []
        errors = []
        backup_files = []
        
        try:
            # Excelファイルの存在確認（要件1.3）
            input_path = Path(input_file)
            if not input_path.exists():
                error_msg = f"ファイルが存在しません: {input_file}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return ConversionResult(
                    success=False,
                    files_created=[],
                    warnings=[],
                    errors=errors,
                    backup_files=[]
                )
            
            # 出力ディレクトリの作成（要件1.4）
            output_path = Path(output_dir)
            if not dry_run:
                output_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"出力ディレクトリ: {output_dir}")
            
            # 全ての必要なシートが存在するか確認（要件2.5）
            missing_sheets = []
            for mapping in self.sheet_mappings:
                if not self.excel_repo.sheet_exists(mapping.sheet_name):
                    missing_sheets.append(mapping.sheet_name)
            
            if missing_sheets:
                error_msg = f"必要なシートが存在しません: {', '.join(missing_sheets)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return ConversionResult(
                    success=False,
                    files_created=[],
                    warnings=[],
                    errors=errors,
                    backup_files=[]
                )
            
            # 各シートを変換
            for mapping in self.sheet_mappings:
                try:
                    self.logger.info(f"シート '{mapping.sheet_name}' の変換を開始します")
                    
                    # シートデータを読み込む
                    rows = self.excel_repo.load_sheet(mapping.sheet_name)
                    
                    # 空のシートをスキップ（要件8.5）
                    if not rows or len(rows) <= 1:  # ヘッダーのみまたは空
                        warning_msg = f"シート '{mapping.sheet_name}' が空です。スキップします。"
                        self.logger.warning(warning_msg)
                        warnings.append(ValidationWarning(
                            sheet_name=mapping.sheet_name,
                            row_number=0,
                            field_name="",
                            message=warning_msg,
                            severity="warning"
                        ))
                        continue
                    
                    # ヘッダー行とデータ行を分離
                    header_row = rows[0]
                    data_rows = rows[1:]
                    
                    self.logger.info(
                        f"シート '{mapping.sheet_name}': {len(data_rows)}行のデータ"
                    )
                    
                    # データ検証
                    validation_warnings = self.validate_sheet_data(
                        mapping.sheet_name,
                        data_rows,
                        len(mapping.required_fields)
                    )
                    warnings.extend(validation_warnings)
                    
                    # ドライランモードでない場合のみファイルを書き込む
                    if not dry_run:
                        # 既存ファイルのバックアップ（要件1.5, 7.1）
                        output_file_path = output_path / mapping.output_file
                        if output_file_path.exists():
                            try:
                                backup_path = self.backup_repo.create_backup(
                                    str(output_file_path)
                                )
                                backup_files.append(backup_path)
                                self.logger.info(
                                    f"バックアップを作成しました: {backup_path}"
                                )
                            except DataSaveError as e:
                                # バックアップ失敗時は処理を中断（要件7.4）
                                error_msg = f"バックアップの作成に失敗しました: {e.message}"
                                self.logger.error(error_msg)
                                errors.append(error_msg)
                                return ConversionResult(
                                    success=False,
                                    files_created=files_created,
                                    warnings=warnings,
                                    errors=errors,
                                    backup_files=backup_files
                                )
                        
                        # TSVファイルを保存
                        self.tsv_repo.save_tsv(
                            mapping.output_file,
                            mapping.headers,
                            data_rows
                        )
                        
                        files_created.append(str(output_file_path))
                        self.logger.info(
                            f"TSVファイルを生成しました: {output_file_path} "
                            f"({len(data_rows)}行)"
                        )
                    else:
                        self.logger.info(
                            f"[ドライラン] TSVファイル: {mapping.output_file} "
                            f"({len(data_rows)}行)"
                        )
                
                except DataLoadError as e:
                    # シートの読み込みエラー（要件2.3）
                    error_msg = f"シート '{mapping.sheet_name}' の読み込みに失敗しました: {e.message}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
                    # 他のシートの処理は継続
                    continue
                
                except Exception as e:
                    # その他のエラー
                    error_msg = f"シート '{mapping.sheet_name}' の変換中にエラーが発生しました: {e}"
                    self.logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
                    # 他のシートの処理は継続
                    continue
            
            # 結果を返す
            # ドライランモードの場合はエラーがなければ成功
            if dry_run:
                success = len(errors) == 0
            else:
                success = len(files_created) > 0 and len(errors) == 0
            
            if success:
                if dry_run:
                    self.logger.info("変換処理（ドライラン）が完了しました")
                else:
                    self.logger.info(
                        f"変換処理が完了しました: {len(files_created)}ファイル生成"
                    )
            else:
                self.logger.warning(
                    f"変換処理が完了しましたが、エラーがあります: "
                    f"{len(errors)}個のエラー"
                )
            
            return ConversionResult(
                success=success,
                files_created=files_created,
                warnings=warnings,
                errors=errors,
                backup_files=backup_files
            )
        
        except Exception as e:
            # 予期しないエラー
            error_msg = f"変換処理中に予期しないエラーが発生しました: {e}"
            self.logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            return ConversionResult(
                success=False,
                files_created=files_created,
                warnings=warnings,
                errors=errors,
                backup_files=backup_files
            )
        
        finally:
            # リソースのクリーンアップ
            self.excel_repo.close()

    def validate_sheet_data(
        self,
        sheet_name: str,
        rows: List[List[Any]],
        expected_field_count: int = None
    ) -> List[ValidationWarning]:
        """
        シートデータを検証
        
        Args:
            sheet_name: シート名
            rows: データ行のリスト
            expected_field_count: 期待されるフィールド数（Noneの場合は検証しない）
            
        Returns:
            検証警告のリスト
        """
        warnings = []
        
        for row_idx, row in enumerate(rows, start=2):  # 行番号は2から（ヘッダーが1行目）
            # フィールド数の検証（要件4.1, 4.2）
            if expected_field_count is not None:
                actual_field_count = len(row)
                if actual_field_count != expected_field_count:
                    warnings.append(ValidationWarning(
                        sheet_name=sheet_name,
                        row_number=row_idx,
                        field_name="",
                        message=f"フィールド数が不正です（期待: {expected_field_count}, 実際: {actual_field_count}）",
                        severity="warning"
                    ))
            
            # 各フィールドの検証
            for field_idx, field_value in enumerate(row):
                # 必須フィールドが空かチェック（要件4.3）
                if field_value is None or str(field_value).strip() == "":
                    warnings.append(ValidationWarning(
                        sheet_name=sheet_name,
                        row_number=row_idx,
                        field_name=f"フィールド{field_idx + 1}",
                        message="必須フィールドが空です",
                        severity="warning"
                    ))
                
                # IDフィールドが数値かチェック（要件4.5）
                # 最初のフィールドがIDと仮定
                if field_idx == 0 and field_value is not None:
                    try:
                        # 数値に変換できるかチェック
                        float(str(field_value))
                    except (ValueError, TypeError):
                        warnings.append(ValidationWarning(
                            sheet_name=sheet_name,
                            row_number=row_idx,
                            field_name="ID",
                            message=f"IDフィールドが数値ではありません: {field_value}",
                            severity="error"
                        ))
                
                # URLフィールドの検証（要件4.4）
                # M_YT_LIVEシートの4番目のフィールドがURL
                if sheet_name.upper() == "M_YT_LIVE" and field_idx == 3:
                    if field_value and not self._is_valid_url(str(field_value)):
                        warnings.append(ValidationWarning(
                            sheet_name=sheet_name,
                            row_number=row_idx,
                            field_name="URL",
                            message=f"URL形式が不正です: {field_value}",
                            severity="warning"
                        ))
        
        return warnings
    
    def _is_valid_url(self, url: str) -> bool:
        """
        URL形式が有効かチェック
        
        Args:
            url: チェックするURL文字列
            
        Returns:
            有効なURL形式の場合True
        """
        # 簡易的なURL検証（http/httpsで始まるか）
        url_pattern = re.compile(
            r'^https?://'  # http:// または https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # ドメイン
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IPアドレス
            r'(?::\d+)?'  # ポート番号（オプション）
            r'(?:/?|[/?]\S+)$',  # パス
            re.IGNORECASE
        )
        return bool(url_pattern.match(url.strip()))
    
    def run_song_list_generator(
        self,
        live_file: str,
        timestamp_file: str,
        output_file: str
    ) -> bool:
        """
        song_list_generatorを実行
        
        Args:
            live_file: M_YT_LIVE.TSVファイルのパス
            timestamp_file: M_YT_LIVE_TIMESTAMP.TSVファイルのパス
            output_file: V_SONG_LIST.TSVファイルのパス
            
        Returns:
            実行が成功した場合True
        """
        try:
            self.logger.info("song_list_generatorを実行します")
            
            # song_list_generatorコマンドを実行（要件9.1, 9.2）
            # Pythonモジュールとして実行
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "src.cli.song_list_generator",
                    "--live-file",
                    live_file,
                    "--timestamp-file",
                    timestamp_file,
                    "--output-file",
                    output_file
                ],
                capture_output=True,
                text=True,
                timeout=300  # 5分のタイムアウト
            )
            
            # 実行結果をログに記録
            if result.stdout:
                self.logger.info(f"song_list_generator出力:\n{result.stdout}")
            
            if result.returncode == 0:
                self.logger.info(
                    f"song_list_generatorが正常に完了しました: {output_file}"
                )
                return True
            else:
                # エラーメッセージをログに記録（要件9.4）
                error_msg = f"song_list_generatorの実行に失敗しました（終了コード: {result.returncode}）"
                if result.stderr:
                    error_msg += f"\n{result.stderr}"
                self.logger.error(error_msg)
                return False
        
        except subprocess.TimeoutExpired:
            self.logger.error("song_list_generatorの実行がタイムアウトしました")
            return False
        
        except FileNotFoundError:
            self.logger.error(
                "song_list_generatorが見つかりません。"
                "Pythonモジュールが正しくインストールされているか確認してください。"
            )
            return False
        
        except Exception as e:
            self.logger.error(
                f"song_list_generatorの実行中にエラーが発生しました: {e}",
                exc_info=True
            )
            return False
