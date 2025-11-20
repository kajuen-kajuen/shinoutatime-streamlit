"""
HTML Validatorのユニットテスト

HTML検証機能の正常系・異常系をテストします。
"""

import pytest
from src.utils.html_validator import (
    validate_html_structure,
    validate_twitter_embed_code,
    get_validation_message,
    validate_and_report,
    HTMLValidationError,
    TwitterEmbedHTMLParser
)
from tests.fixtures.sample_html import (
    VALID_TWITTER_EMBED_HTML,
    VALID_TWITTER_EMBED_HTML_WITH_HEIGHT,
    INVALID_HTML_MISSING_BLOCKQUOTE,
    INVALID_HTML_MISSING_CLASS,
    INVALID_HTML_EMPTY,
    INVALID_HTML_MISMATCHED_TAGS,
    MINIMAL_VALID_HTML,
    HTML_WITH_SPECIAL_CHARS
)


class TestHTMLStructureValidation:
    """HTML構造検証のテスト（要件3.1）"""
    
    def test_valid_html_structure(self):
        """有効なHTML構造の検証が成功すること"""
        is_valid, errors = validate_html_structure(VALID_TWITTER_EMBED_HTML)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_valid_html_with_height(self):
        """高さ情報付きの有効なHTMLの検証が成功すること"""
        is_valid, errors = validate_html_structure(VALID_TWITTER_EMBED_HTML_WITH_HEIGHT)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_minimal_valid_html(self):
        """最小限の有効なHTMLの検証が成功すること"""
        is_valid, errors = validate_html_structure(MINIMAL_VALID_HTML)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_html_with_special_chars(self):
        """特殊文字を含むHTMLの検証が成功すること"""
        is_valid, errors = validate_html_structure(HTML_WITH_SPECIAL_CHARS)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_blockquote_tag_validation(self):
        """blockquoteタグの検証が正しく動作すること"""
        html_with_blockquote = '<blockquote class="twitter-tweet"><p>Test</p></blockquote>'
        is_valid, errors = validate_html_structure(html_with_blockquote)
        assert is_valid is True
        
        html_without_blockquote = '<div class="twitter-tweet"><p>Test</p></div>'
        is_valid, errors = validate_html_structure(html_without_blockquote)
        assert is_valid is False
        assert any("blockquote" in error for error in errors)
    
    def test_twitter_tweet_class_validation(self):
        """twitter-tweetクラスの検証が正しく動作すること"""
        html_with_class = '<blockquote class="twitter-tweet"><p>Test</p></blockquote>'
        is_valid, errors = validate_html_structure(html_with_class)
        assert is_valid is True
        
        html_without_class = '<blockquote><p>Test</p></blockquote>'
        is_valid, errors = validate_html_structure(html_without_class)
        assert is_valid is False
        assert any("twitter-tweet" in error for error in errors)
    
    def test_twitter_tweet_class_with_multiple_classes(self):
        """複数のクラスを持つblockquoteタグの検証が成功すること"""
        html = '<blockquote class="twitter-tweet other-class"><p>Test</p></blockquote>'
        is_valid, errors = validate_html_structure(html)
        assert is_valid is True
        assert len(errors) == 0


class TestInvalidHTMLValidation:
    """無効なHTML検証のテスト（要件3.2, 3.3）"""
    
    def test_missing_blockquote_tag(self):
        """blockquoteタグが欠落している場合、検証が失敗すること"""
        is_valid, errors = validate_html_structure(INVALID_HTML_MISSING_BLOCKQUOTE)
        assert is_valid is False
        assert len(errors) > 0
        assert any("blockquote" in error for error in errors)
    
    def test_missing_twitter_tweet_class(self):
        """twitter-tweetクラスが欠落している場合、検証が失敗すること"""
        is_valid, errors = validate_html_structure(INVALID_HTML_MISSING_CLASS)
        assert is_valid is False
        assert len(errors) > 0
        assert any("twitter-tweet" in error for error in errors)
    
    def test_mismatched_tags(self):
        """タグの不一致がある場合、検証が失敗すること"""
        is_valid, errors = validate_html_structure(INVALID_HTML_MISMATCHED_TAGS)
        assert is_valid is False
        assert len(errors) > 0
        # タグの不一致エラーが含まれていることを確認
        assert any("不一致" in error or "閉じられていない" in error for error in errors)
    
    def test_empty_html(self):
        """空のHTMLの場合、検証が失敗すること"""
        is_valid, errors = validate_html_structure(INVALID_HTML_EMPTY)
        assert is_valid is False
        assert len(errors) > 0
        assert any("空" in error for error in errors)
    
    def test_whitespace_only_html(self):
        """空白のみのHTMLの場合、検証が失敗すること"""
        is_valid, errors = validate_html_structure("   \n\t  ")
        assert is_valid is False
        assert len(errors) > 0
        assert any("空" in error for error in errors)
    
    def test_unclosed_tags(self):
        """閉じられていないタグがある場合、検証が失敗すること"""
        html = '<blockquote class="twitter-tweet"><p>Test'
        is_valid, errors = validate_html_structure(html)
        assert is_valid is False
        assert any("閉じられていない" in error for error in errors)


class TestTwitterEmbedCodeValidation:
    """Twitter埋め込みコード検証のテスト"""
    
    def test_valid_twitter_embed_code(self):
        """有効なTwitter埋め込みコードの検証が成功すること"""
        is_valid, messages = validate_twitter_embed_code(VALID_TWITTER_EMBED_HTML)
        assert is_valid is True
        # 警告メッセージがないことを確認
        assert len(messages) == 0
    
    def test_valid_code_without_script_tag(self):
        """scriptタグがない場合、警告が返されること"""
        html = '<blockquote class="twitter-tweet"><p>Test</p></blockquote>'
        is_valid, messages = validate_twitter_embed_code(html)
        assert is_valid is True
        assert len(messages) > 0
        assert any("script" in msg.lower() for msg in messages)
    
    def test_valid_code_without_platform_js(self):
        """platform.jsがない場合、警告が返されること"""
        html = '<blockquote class="twitter-tweet"><p>Test</p></blockquote><script src="other.js"></script>'
        is_valid, messages = validate_twitter_embed_code(html)
        assert is_valid is True
        assert len(messages) > 0
        # scriptタグはあるがplatform.twitter.comがないため、警告が返される
        assert any("platform" in msg.lower() or "twitter" in msg.lower() for msg in messages)
    
    def test_invalid_twitter_embed_code(self):
        """無効なTwitter埋め込みコードの検証が失敗すること"""
        is_valid, messages = validate_twitter_embed_code(INVALID_HTML_MISSING_BLOCKQUOTE)
        assert is_valid is False
        assert len(messages) > 0


class TestValidationMessage:
    """検証メッセージ生成のテスト"""
    
    def test_success_message_without_warnings(self):
        """警告なしの成功メッセージが正しく生成されること"""
        message = get_validation_message(True, [])
        assert "成功" in message
        assert "警告" not in message
        assert "失敗" not in message
    
    def test_success_message_with_warnings(self):
        """警告ありの成功メッセージが正しく生成されること"""
        warnings = ["警告: scriptタグが見つかりません"]
        message = get_validation_message(True, warnings)
        assert "成功" in message
        assert "警告" in message
        assert "scriptタグ" in message
    
    def test_failure_message(self):
        """失敗メッセージが正しく生成されること"""
        errors = ["blockquoteタグが見つかりません", "twitter-tweetクラスが見つかりません"]
        message = get_validation_message(False, errors)
        assert "失敗" in message
        assert "blockquote" in message
        assert "twitter-tweet" in message
    
    def test_message_formatting(self):
        """メッセージのフォーマットが正しいこと"""
        errors = ["エラー1", "エラー2"]
        message = get_validation_message(False, errors)
        # 各エラーが箇条書きで表示されることを確認
        assert "  - エラー1" in message
        assert "  - エラー2" in message


class TestValidateAndReport:
    """検証とレポート生成のテスト"""
    
    def test_validate_and_report_success(self):
        """有効なHTMLの検証とレポート生成が正しく動作すること"""
        is_valid, report = validate_and_report(VALID_TWITTER_EMBED_HTML)
        assert is_valid is True
        assert "成功" in report
    
    def test_validate_and_report_failure(self):
        """無効なHTMLの検証とレポート生成が正しく動作すること"""
        is_valid, report = validate_and_report(INVALID_HTML_MISSING_BLOCKQUOTE)
        assert is_valid is False
        assert "失敗" in report
        assert "blockquote" in report
    
    def test_validate_and_report_with_warnings(self):
        """警告ありのHTMLの検証とレポート生成が正しく動作すること"""
        html = '<blockquote class="twitter-tweet"><p>Test</p></blockquote>'
        is_valid, report = validate_and_report(html)
        assert is_valid is True
        assert "警告" in report


class TestTwitterEmbedHTMLParser:
    """TwitterEmbedHTMLParserのテスト"""
    
    def test_parser_detects_blockquote(self):
        """パーサーがblockquoteタグを検出すること"""
        parser = TwitterEmbedHTMLParser()
        parser.feed('<blockquote class="twitter-tweet"><p>Test</p></blockquote>')
        assert parser.has_blockquote is True
    
    def test_parser_detects_twitter_tweet_class(self):
        """パーサーがtwitter-tweetクラスを検出すること"""
        parser = TwitterEmbedHTMLParser()
        parser.feed('<blockquote class="twitter-tweet"><p>Test</p></blockquote>')
        assert parser.has_twitter_tweet_class is True
    
    def test_parser_detects_tag_mismatch(self):
        """パーサーがタグの不一致を検出すること"""
        parser = TwitterEmbedHTMLParser()
        parser.feed('<blockquote><p>Test</blockquote></p>')
        assert len(parser.errors) > 0
        assert any("不一致" in error for error in parser.errors)
    
    def test_parser_detects_unexpected_closing_tag(self):
        """パーサーが予期しない終了タグを検出すること"""
        parser = TwitterEmbedHTMLParser()
        parser.feed('</div>')
        assert len(parser.errors) > 0
        assert any("予期しない" in error for error in parser.errors)
    
    def test_parser_tracks_unclosed_tags(self):
        """パーサーが閉じられていないタグを追跡すること"""
        parser = TwitterEmbedHTMLParser()
        parser.feed('<blockquote class="twitter-tweet"><p>Test')
        assert len(parser.tags) > 0
