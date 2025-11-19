"""
HTML検証ユーティリティ

Twitter埋め込みコードのHTML検証機能を提供します。
"""

import re
from typing import Tuple, List, Optional
from html.parser import HTMLParser


class HTMLValidationError(Exception):
    """HTML検証エラー"""
    pass


class TwitterEmbedHTMLParser(HTMLParser):
    """
    Twitter埋め込みHTML用のパーサー
    
    HTMLの構造を検証し、不正な形式を検出します。
    """
    
    def __init__(self):
        super().__init__()
        self.errors: List[str] = []
        self.tags: List[str] = []
        self.has_blockquote = False
        self.has_twitter_tweet_class = False
    
    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        """開始タグを処理"""
        self.tags.append(tag)
        
        # blockquoteタグをチェック
        if tag == "blockquote":
            self.has_blockquote = True
            # twitter-tweetクラスをチェック
            for attr_name, attr_value in attrs:
                if attr_name == "class" and attr_value and "twitter-tweet" in attr_value:
                    self.has_twitter_tweet_class = True
    
    def handle_endtag(self, tag: str) -> None:
        """終了タグを処理"""
        if not self.tags:
            self.errors.append(f"予期しない終了タグ: </{tag}>")
            return
        
        # タグの対応をチェック
        if self.tags[-1] != tag:
            self.errors.append(
                f"タグの不一致: <{self.tags[-1]}>に対して</{tag}>が閉じられています"
            )
        else:
            self.tags.pop()
    
    def error(self, message: str) -> None:
        """パースエラーを処理"""
        self.errors.append(f"パースエラー: {message}")


def validate_html_structure(html: str) -> Tuple[bool, List[str]]:
    """
    HTMLの基本的な構造を検証
    
    Args:
        html: 検証するHTML文字列
        
    Returns:
        (検証成功, エラーメッセージのリスト)
    """
    if not html or not html.strip():
        return False, ["HTMLコードが空です"]
    
    parser = TwitterEmbedHTMLParser()
    errors = []
    
    try:
        parser.feed(html)
    except Exception as e:
        errors.append(f"HTML解析エラー: {str(e)}")
        return False, errors
    
    # パーサーで検出されたエラーを追加
    errors.extend(parser.errors)
    
    # 閉じられていないタグをチェック
    if parser.tags:
        errors.append(f"閉じられていないタグ: {', '.join(parser.tags)}")
    
    # Twitter埋め込みコードの基本要素をチェック
    if not parser.has_blockquote:
        errors.append("blockquoteタグが見つかりません")
    
    if not parser.has_twitter_tweet_class:
        errors.append("twitter-tweetクラスが見つかりません")
    
    return len(errors) == 0, errors


def validate_twitter_embed_code(html: str) -> Tuple[bool, List[str]]:
    """
    Twitter埋め込みコードを検証
    
    基本的なHTML構造とTwitter埋め込みコードの必須要素を検証します。
    
    Args:
        html: 検証するHTML文字列
        
    Returns:
        (検証成功, エラーメッセージのリスト)
    """
    warnings = []
    
    # 基本的なHTML構造を検証
    is_valid, errors = validate_html_structure(html)
    
    if not is_valid:
        return False, errors
    
    # scriptタグの存在をチェック（警告レベル）
    if "<script" not in html.lower():
        warnings.append("警告: scriptタグが見つかりません。埋め込みコードが正しく動作しない可能性があります")
    
    # Twitter platform.jsスクリプトの存在をチェック（警告レベル）
    if "platform.twitter.com" not in html:
        warnings.append("警告: Twitter platform.jsスクリプトが見つかりません")
    
    # aタグ（リンク）の存在をチェック（警告レベル）
    if "<a" not in html.lower():
        warnings.append("警告: リンクタグが見つかりません")
    
    return True, warnings


def get_validation_message(is_valid: bool, messages: List[str]) -> str:
    """
    検証結果のメッセージを生成
    
    Args:
        is_valid: 検証成功かどうか
        messages: エラーまたは警告メッセージのリスト
        
    Returns:
        フォーマットされたメッセージ
    """
    if is_valid and not messages:
        return "HTML検証: 成功"
    
    if is_valid and messages:
        # 警告がある場合
        header = "HTML検証: 成功（警告あり）"
        formatted_messages = "\n".join(f"  - {msg}" for msg in messages)
        return f"{header}\n{formatted_messages}"
    
    # エラーがある場合
    header = "HTML検証: 失敗"
    formatted_messages = "\n".join(f"  - {msg}" for msg in messages)
    return f"{header}\n{formatted_messages}"


def validate_and_report(html: str) -> Tuple[bool, str]:
    """
    HTML検証を実行し、結果をレポート
    
    Args:
        html: 検証するHTML文字列
        
    Returns:
        (検証成功, レポートメッセージ)
    """
    is_valid, messages = validate_twitter_embed_code(html)
    report = get_validation_message(is_valid, messages)
    return is_valid, report
