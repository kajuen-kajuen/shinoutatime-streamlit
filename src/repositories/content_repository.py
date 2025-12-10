"""
コンテンツリポジトリ

静的コンテンツファイルの読み込みを担当します。
"""

import logging
import os
from typing import Optional

# ロガーの設定
logger = logging.getLogger(__name__)


class ContentRepository:
    """
    コンテンツリポジトリ
    
    テキストファイルやHTMLファイルなどの静的コンテンツを読み込みます。
    """
    
    def read_text_file(self, file_path: str) -> Optional[str]:
        """
        テキストファイルを読み込む
        
        Args:
            file_path: ファイルパス
            
        Returns:
            読み込んだテキスト内容。ファイルが見つからないかエラーの場合はNone
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"ファイルが見つかりません: {file_path}")
                return None
                
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                return content
        except Exception as e:
            logger.error(f"ファイルの読み込み中にエラーが発生しました ({file_path}): {e}")
            return None
    
    def read_text_file_with_default(self, file_path: str, default: str) -> str:
        """
        デフォルト値付きでテキストファイルを読み込む
        
        Args:
            file_path: ファイルパス
            default: ファイルが読めない場合のデフォルト値
            
        Returns:
            読み込んだテキスト内容またはデフォルト値
        """
        content = self.read_text_file(file_path)
        return content if content is not None else default
