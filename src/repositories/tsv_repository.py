"""TSVファイルの書き込みを管理するリポジトリ"""

import os
from pathlib import Path
from typing import List, Any
import logging

logger = logging.getLogger(__name__)


class TsvRepository:
    """TSVファイルの書き込みを管理するリポジトリクラス"""
    
    def __init__(self, output_dir: str):
        """
        リポジトリを初期化
        
        Args:
            output_dir: 出力ディレクトリのパス
        """
        self.output_dir = Path(output_dir)
        logger.info(f"TsvRepository initialized with output_dir: {output_dir}")
    
    def save_tsv(
        self,
        file_name: str,
        headers: List[str],
        rows: List[List[Any]]
    ) -> None:
        """
        TSVファイルを保存
        
        Args:
            file_name: 出力ファイル名
            headers: ヘッダー行のリスト
            rows: データ行のリスト（各行はフィールドのリスト）
        
        Raises:
            IOError: ファイルの書き込みに失敗した場合
            PermissionError: 書き込み権限がない場合
        """
        file_path = self.output_dir / file_name
        
        # 出力ディレクトリが存在しない場合は作成
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                # ヘッダー行を書き込む
                header_line = self._format_row(headers)
                f.write(header_line + '\n')
                
                # データ行を書き込む
                for row in rows:
                    row_line = self._format_row(row)
                    f.write(row_line + '\n')
            
            logger.info(f"TSV file saved: {file_path} ({len(rows)} rows)")
        
        except PermissionError as e:
            logger.error(f"Permission denied when writing to {file_path}: {e}")
            raise
        except IOError as e:
            logger.error(f"IO error when writing to {file_path}: {e}")
            raise
    
    def file_exists(self, file_name: str) -> bool:
        """
        ファイルが存在するか確認
        
        Args:
            file_name: 確認するファイル名
        
        Returns:
            ファイルが存在する場合True、存在しない場合False
        """
        file_path = self.output_dir / file_name
        exists = file_path.exists()
        logger.debug(f"File exists check for {file_path}: {exists}")
        return exists
    
    def _format_row(self, row: List[Any]) -> str:
        """
        行をTSV形式にフォーマット
        
        Args:
            row: フィールドのリスト
        
        Returns:
            タブ区切りの文字列
        """
        formatted_fields = []
        
        for field in row:
            # Noneや空の値を空文字列に変換
            if field is None:
                field_str = ""
            else:
                field_str = str(field)
            
            # 改行文字を削除（要件3.3）
            field_str = field_str.replace('\n', ' ').replace('\r', ' ')
            
            # タブ文字をスペースに置換（要件3.4）
            field_str = field_str.replace('\t', ' ')
            
            formatted_fields.append(field_str)
        
        # タブ文字で区切る（要件3.1）
        return '\t'.join(formatted_fields)
