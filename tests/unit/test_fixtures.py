"""
フィクスチャの動作確認テスト

作成したテストフィクスチャが正しく動作することを確認します。
"""

import pytest
import tempfile
import os
from pathlib import Path

from tests.fixtures import (
    VALID_TWITTER_EMBED_HTML,
    VALID_TWITTER_EMBED_HTML_WITH_HEIGHT,
    INVALID_HTML_MISSING_BLOCKQUOTE,
    INVALID_HTML_MISSING_CLASS,
    INVALID_HTML_EMPTY,
    SAMPLE_LIVES_DATA,
    SAMPLE_SONGS_DATA,
    SAMPLE_SONG_LIST_DATA,
    create_sample_tsv_file,
    create_mock_oembed_response,
    create_mock_rate_limit_headers,
    create_mock_error_response,
    create_mock_success_response,
)


class TestHTMLFixtures:
    """HTMLフィクスチャのテスト"""
    
    def test_valid_html_not_empty(self):
        """有効なHTMLが空でないことを確認"""
        assert len(VALID_TWITTER_EMBED_HTML) > 0
        assert "blockquote" in VALID_TWITTER_EMBED_HTML
        assert "twitter-tweet" in VALID_TWITTER_EMBED_HTML
    
    def test_valid_html_with_height_contains_height(self):
        """高さ情報付きHTMLに高さ属性が含まれることを確認"""
        assert "data-height" in VALID_TWITTER_EMBED_HTML_WITH_HEIGHT
    
    def test_invalid_html_missing_blockquote(self):
        """blockquote欠落HTMLにblockquoteタグがないことを確認"""
        # <blockquote>タグではなく<div>タグを使用していることを確認
        assert "<blockquote" not in INVALID_HTML_MISSING_BLOCKQUOTE
        assert "<div" in INVALID_HTML_MISSING_BLOCKQUOTE
    
    def test_invalid_html_missing_class(self):
        """クラス欠落HTMLにtwitter-tweetクラスがないことを確認"""
        # class="twitter-tweet"属性がないことを確認
        assert 'class="twitter-tweet"' not in INVALID_HTML_MISSING_CLASS
        assert "<blockquote>" in INVALID_HTML_MISSING_CLASS
    
    def test_invalid_html_empty(self):
        """空のHTMLが実際に空であることを確認"""
        assert INVALID_HTML_EMPTY == ""


class TestDataFixtures:
    """データフィクスチャのテスト"""
    
    def test_sample_lives_data_structure(self):
        """配信データの構造が正しいことを確認"""
        assert "ID" in SAMPLE_LIVES_DATA
        assert "配信日" in SAMPLE_LIVES_DATA
        assert "タイトル" in SAMPLE_LIVES_DATA
        assert "URL" in SAMPLE_LIVES_DATA
        
        # すべてのキーが同じ長さであることを確認
        lengths = [len(v) for v in SAMPLE_LIVES_DATA.values()]
        assert len(set(lengths)) == 1
    
    def test_sample_songs_data_structure(self):
        """楽曲データの構造が正しいことを確認"""
        assert "ID" in SAMPLE_SONGS_DATA
        assert "LIVE_ID" in SAMPLE_SONGS_DATA
        assert "曲名" in SAMPLE_SONGS_DATA
        assert "タイムスタンプ" in SAMPLE_SONGS_DATA
        
        # すべてのキーが同じ長さであることを確認
        lengths = [len(v) for v in SAMPLE_SONGS_DATA.values()]
        assert len(set(lengths)) == 1
    
    def test_sample_song_list_data_structure(self):
        """楽曲リストデータの構造が正しいことを確認"""
        assert "ID" in SAMPLE_SONG_LIST_DATA
        assert "曲名" in SAMPLE_SONG_LIST_DATA
        assert "アーティスト" in SAMPLE_SONG_LIST_DATA
        assert "ジャンル" in SAMPLE_SONG_LIST_DATA
        
        # すべてのキーが同じ長さであることを確認
        lengths = [len(v) for v in SAMPLE_SONG_LIST_DATA.values()]
        assert len(set(lengths)) == 1
    
    def test_create_sample_tsv_file(self):
        """TSVファイル作成関数が正しく動作することを確認"""
        # 一時ファイルを作成
        file_path = create_sample_tsv_file(SAMPLE_LIVES_DATA)
        
        try:
            # ファイルが存在することを確認
            assert os.path.exists(file_path)
            
            # ファイルの内容を確認
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "ID\t配信日\tタイトル\tURL" in content
                assert "新年最初の配信" in content
        finally:
            # クリーンアップ
            if os.path.exists(file_path):
                os.remove(file_path)


class TestMockResponseHelpers:
    """モックレスポンスヘルパーのテスト"""
    
    def test_create_mock_oembed_response(self):
        """oEmbedレスポンス作成関数が正しく動作することを確認"""
        response = create_mock_oembed_response()
        
        assert "author_name" in response
        assert "html" in response
        assert "type" in response
        assert response["type"] == "rich"
        assert "blockquote" in response["html"]
        
        # urlを指定した場合はレスポンスに含まれる
        response_with_url = create_mock_oembed_response(url="https://twitter.com/user/status/123")
        assert "url" in response_with_url
        assert response_with_url["url"] == "https://twitter.com/user/status/123"
    
    def test_create_mock_oembed_response_with_custom_html(self):
        """カスタムHTML付きoEmbedレスポンスが正しく作成されることを確認"""
        custom_html = "<blockquote class='twitter-tweet'>カスタムHTML</blockquote>"
        response = create_mock_oembed_response(html=custom_html)
        
        assert response["html"] == custom_html
    
    def test_create_mock_rate_limit_headers(self):
        """レート制限ヘッダー作成関数が正しく動作することを確認"""
        headers = create_mock_rate_limit_headers()
        
        assert "x-rate-limit-limit" in headers
        assert "x-rate-limit-remaining" in headers
        assert "x-rate-limit-reset" in headers
        
        # 値が文字列であることを確認
        assert isinstance(headers["x-rate-limit-limit"], str)
        assert isinstance(headers["x-rate-limit-remaining"], str)
        assert isinstance(headers["x-rate-limit-reset"], str)
    
    def test_create_mock_error_response_404(self):
        """404エラーレスポンスが正しく作成されることを確認"""
        response = create_mock_error_response(404)
        
        assert response.status_code == 404
        assert response.ok is False
        assert "errors" in response.json()
    
    def test_create_mock_error_response_429(self):
        """429エラーレスポンス（レート制限）が正しく作成されることを確認"""
        response = create_mock_error_response(429)
        
        assert response.status_code == 429
        assert response.ok is False
        assert "x-rate-limit-remaining" in response.headers
        assert response.headers["x-rate-limit-remaining"] == "0"
    
    def test_create_mock_success_response(self):
        """成功レスポンスが正しく作成されることを確認"""
        data = {"test": "data"}
        response = create_mock_success_response(data)
        
        assert response.status_code == 200
        assert response.ok is True
        assert response.json() == data
        assert "x-rate-limit-limit" in response.headers


class TestFixturesIntegration:
    """フィクスチャの統合テスト"""
    
    def test_html_and_mock_response_integration(self):
        """HTMLフィクスチャとモックレスポンスの統合"""
        # HTMLフィクスチャを使用してモックレスポンスを作成
        response = create_mock_oembed_response(html=VALID_TWITTER_EMBED_HTML)
        
        assert response["html"] == VALID_TWITTER_EMBED_HTML
        assert "blockquote" in response["html"]
        assert "twitter-tweet" in response["html"]
    
    def test_data_and_tsv_file_integration(self):
        """データフィクスチャとTSVファイル作成の統合"""
        import pandas as pd
        
        # TSVファイルを作成
        file_path = create_sample_tsv_file(SAMPLE_LIVES_DATA)
        
        try:
            # ファイルを読み込んでデータを確認
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
            
            assert len(df) == len(SAMPLE_LIVES_DATA["ID"])
            assert list(df.columns) == list(SAMPLE_LIVES_DATA.keys())
            assert df["タイトル"].tolist() == SAMPLE_LIVES_DATA["タイトル"]
        finally:
            # クリーンアップ
            if os.path.exists(file_path):
                os.remove(file_path)
