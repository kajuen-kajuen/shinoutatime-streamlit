"""Excel to TSV変換のデータモデル

このモジュールは、Excel to TSV変換処理で使用されるデータモデルを定義します。
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ValidationWarning:
    """データ検証の警告
    
    Attributes:
        sheet_name: シート名
        row_number: 行番号
        field_name: フィールド名
        message: 警告メッセージ
        severity: 重要度 ('warning' または 'error')
    """
    sheet_name: str
    row_number: int
    field_name: str
    message: str
    severity: str  # 'warning' or 'error'


@dataclass
class SheetMapping:
    """シートマッピング情報
    
    ExcelシートとTSVファイルのマッピング情報を保持します。
    
    Attributes:
        sheet_name: Excelシート名
        output_file: 出力TSVファイル名
        headers: ヘッダー行のフィールド名リスト
        required_fields: 必須フィールド名リスト
    """
    sheet_name: str
    output_file: str
    headers: List[str]
    required_fields: List[str]


@dataclass
class ConversionResult:
    """変換処理の結果
    
    Excel to TSV変換処理の結果を保持します。
    
    Attributes:
        success: 変換が成功したかどうか
        files_created: 作成されたファイルのパスリスト
        warnings: データ検証の警告リスト
        errors: エラーメッセージリスト
        backup_files: 作成されたバックアップファイルのパスリスト
    """
    success: bool
    files_created: List[str]
    warnings: List[ValidationWarning]
    errors: List[str]
    backup_files: List[str]
