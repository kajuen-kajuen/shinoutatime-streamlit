"""
HTML Validatorのプロパティベーステスト

普遍的な性質を多数のランダム入力で検証します。
"""

import pytest
from hypothesis import given, strategies as st, assume
from src.utils.html_validator import (
    validate_html_structure,
    validate_twitter_embed_code,
    get_validation_message,
    validate_and_report
)


# カスタム戦略: 有効なTwitter埋め込みHTMLを生成
@st.composite
def valid_twitter_html(draw):
    """
    有効なTwitter埋め込みHTMLを生成する戦略
    
    blockquoteタグとtwitter-tweetクラスを含むHTMLを生成します。
    """
    # ランダムなコンテンツを生成
    content = draw(st.text(min_size=0, max_size=200))
    # HTMLエスケープが必要な文字を除外
    content = content.replace("<", "&lt;").replace(">", "&gt;")
    
    # 追加のクラスをランダムに生成
    extra_classes = draw(st.lists(st.text(alphabet=st.characters(whitelist_categories=("L", "N")), min_size=1, max_size=10), max_size=3))
    classes = ["twitter-tweet"] + extra_classes
    class_attr = " ".join(classes)
    
    # 追加の属性をランダムに生成
    has_data_height = draw(st.booleans())
    extra_attrs = ""
    if has_data_height:
        height = draw(st.integers(min_value=100, max_value=1000))
        extra_attrs = f' data-height="{height}"'
    
    # HTMLを構築
    html = f'<blockquote class="{class_attr}"{extra_attrs}><p>{content}</p></blockquote>'
    
    return html


# カスタム戦略: 無効なTwitter埋め込みHTMLを生成（blockquote欠落）
@st.composite
def invalid_html_no_blockquote(draw):
    """
    blockquoteタグが欠落した無効なHTMLを生成する戦略
    """
    content = draw(st.text(min_size=0, max_size=200))
    content = content.replace("<", "&lt;").replace(">", "&gt;")
    
    # blockquote以外のタグを使用
    tag = draw(st.sampled_from(["div", "span", "section", "article"]))
    html = f'<{tag} class="twitter-tweet"><p>{content}</p></{tag}>'
    
    return html


# カスタム戦略: 無効なTwitter埋め込みHTMLを生成（twitter-tweetクラス欠落）
@st.composite
def invalid_html_no_class(draw):
    """
    twitter-tweetクラスが欠落した無効なHTMLを生成する戦略
    """
    content = draw(st.text(min_size=0, max_size=200))
    content = content.replace("<", "&lt;").replace(">", "&gt;")
    
    # twitter-tweet以外のクラスを使用（またはクラスなし）
    has_class = draw(st.booleans())
    if has_class:
        other_class = draw(st.text(alphabet=st.characters(whitelist_categories=("L", "N")), min_size=1, max_size=10))
        # twitter-tweetを含まないことを確認
        assume("twitter-tweet" not in other_class)
        html = f'<blockquote class="{other_class}"><p>{content}</p></blockquote>'
    else:
        html = f'<blockquote><p>{content}</p></blockquote>'
    
    return html


class TestValidHTMLProperties:
    """有効なHTML検証のプロパティテスト"""
    
    @given(valid_twitter_html())
    def test_property_6_valid_html_consistency(self, html):
        """
        Feature: test-coverage-improvement, Property 6: 有効なHTML検証の一貫性
        Validates: Requirements 3.1
        
        すべてのblockquoteタグとtwitter-tweetクラスを含むHTMLに対して、
        検証が成功する
        """
        is_valid, errors = validate_html_structure(html)
        assert is_valid is True, f"有効なHTMLが検証に失敗しました: {errors}"
        assert len(errors) == 0, f"エラーが返されました: {errors}"
    
    @given(valid_twitter_html())
    def test_valid_html_has_required_elements(self, html):
        """
        有効なHTMLは必須要素を含むこと
        
        blockquoteタグとtwitter-tweetクラスが含まれていることを確認
        """
        assert "<blockquote" in html
        assert "twitter-tweet" in html
        
        is_valid, errors = validate_html_structure(html)
        assert is_valid is True
    
    @given(valid_twitter_html(), st.text(min_size=0, max_size=100))
    def test_valid_html_with_additional_content(self, html, extra_content):
        """
        有効なHTMLに追加コンテンツがあっても検証が成功すること
        
        scriptタグなどの追加要素があっても基本構造が有効であれば成功する
        """
        # 追加コンテンツをエスケープ
        extra_content = extra_content.replace("<", "&lt;").replace(">", "&gt;")
        modified_html = html + extra_content
        
        is_valid, errors = validate_html_structure(modified_html)
        # 基本構造が有効なので検証は成功するはず
        assert is_valid is True


class TestInvalidHTMLProperties:
    """無効なHTML検証のプロパティテスト"""
    
    @given(invalid_html_no_blockquote())
    def test_property_7_invalid_html_no_blockquote_consistency(self, html):
        """
        Feature: test-coverage-improvement, Property 7: 無効なHTML検証の一貫性
        Validates: Requirements 3.2
        
        すべてのblockquoteタグを欠くHTMLに対して、
        検証が失敗し、適切なエラーメッセージが返される
        """
        is_valid, errors = validate_html_structure(html)
        assert is_valid is False, "blockquoteタグがないHTMLが検証に成功してしまいました"
        assert len(errors) > 0, "エラーメッセージが返されませんでした"
        assert any("blockquote" in error for error in errors), \
            f"blockquoteに関するエラーメッセージが含まれていません: {errors}"
    
    @given(invalid_html_no_class())
    def test_property_7_invalid_html_no_class_consistency(self, html):
        """
        Feature: test-coverage-improvement, Property 7: 無効なHTML検証の一貫性
        Validates: Requirements 3.2
        
        すべてのtwitter-tweetクラスを欠くHTMLに対して、
        検証が失敗し、適切なエラーメッセージが返される
        """
        is_valid, errors = validate_html_structure(html)
        assert is_valid is False, "twitter-tweetクラスがないHTMLが検証に成功してしまいました"
        assert len(errors) > 0, "エラーメッセージが返されませんでした"
        assert any("twitter-tweet" in error for error in errors), \
            f"twitter-tweetに関するエラーメッセージが含まれていません: {errors}"
    
    @given(st.text(max_size=0))
    def test_empty_html_always_fails(self, html):
        """
        空のHTMLは常に検証が失敗すること
        """
        is_valid, errors = validate_html_structure(html)
        assert is_valid is False
        assert len(errors) > 0
        assert any("空" in error for error in errors)
    
    @given(st.text(alphabet=st.characters(whitelist_categories=("Zs",)), min_size=1, max_size=50))
    def test_whitespace_only_html_always_fails(self, html):
        """
        空白のみのHTMLは常に検証が失敗すること
        """
        is_valid, errors = validate_html_structure(html)
        assert is_valid is False
        assert len(errors) > 0


class TestValidationMessageProperties:
    """検証メッセージ生成のプロパティテスト"""
    
    @given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10))
    def test_failure_message_contains_all_errors(self, errors):
        """
        失敗メッセージにはすべてのエラーが含まれること
        """
        message = get_validation_message(False, errors)
        assert "失敗" in message
        for error in errors:
            assert error in message
    
    @given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10))
    def test_success_message_with_warnings_contains_all_warnings(self, warnings):
        """
        警告ありの成功メッセージにはすべての警告が含まれること
        """
        message = get_validation_message(True, warnings)
        assert "成功" in message
        assert "警告" in message
        for warning in warnings:
            assert warning in message
    
    @given(st.booleans(), st.lists(st.text(min_size=1, max_size=100), max_size=10))
    def test_message_format_consistency(self, is_valid, messages):
        """
        メッセージフォーマットの一貫性
        
        すべての検証結果に対して、適切なフォーマットのメッセージが生成される
        """
        message = get_validation_message(is_valid, messages)
        assert isinstance(message, str)
        assert len(message) > 0
        
        # 成功または失敗のいずれかが含まれる
        assert "成功" in message or "失敗" in message


class TestTwitterEmbedCodeValidationProperties:
    """Twitter埋め込みコード検証のプロパティテスト"""
    
    @given(valid_twitter_html())
    def test_valid_embed_code_validation(self, html):
        """
        有効な埋め込みコードの検証が一貫していること
        
        基本構造が有効であれば、検証は成功する（警告はあるかもしれない）
        """
        is_valid, messages = validate_twitter_embed_code(html)
        assert is_valid is True
        # messagesは警告を含む可能性がある
        assert isinstance(messages, list)
    
    @given(invalid_html_no_blockquote())
    def test_invalid_embed_code_validation_no_blockquote(self, html):
        """
        blockquoteがない埋め込みコードの検証が失敗すること
        """
        is_valid, messages = validate_twitter_embed_code(html)
        assert is_valid is False
        assert len(messages) > 0
    
    @given(invalid_html_no_class())
    def test_invalid_embed_code_validation_no_class(self, html):
        """
        twitter-tweetクラスがない埋め込みコードの検証が失敗すること
        """
        is_valid, messages = validate_twitter_embed_code(html)
        assert is_valid is False
        assert len(messages) > 0


class TestValidateAndReportProperties:
    """検証とレポート生成のプロパティテスト"""
    
    @given(valid_twitter_html())
    def test_validate_and_report_consistency(self, html):
        """
        検証とレポート生成の一貫性
        
        有効なHTMLに対して、検証が成功し、適切なレポートが生成される
        """
        is_valid, report = validate_and_report(html)
        assert is_valid is True
        assert isinstance(report, str)
        assert len(report) > 0
        assert "成功" in report
    
    @given(st.one_of(invalid_html_no_blockquote(), invalid_html_no_class()))
    def test_validate_and_report_failure_consistency(self, html):
        """
        無効なHTMLに対して、検証が失敗し、適切なレポートが生成される
        """
        is_valid, report = validate_and_report(html)
        assert is_valid is False
        assert isinstance(report, str)
        assert len(report) > 0
        assert "失敗" in report
