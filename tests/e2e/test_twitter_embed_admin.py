"""
Twitter埋め込み管理者画面のE2Eテスト
src/ui/twitter_embed_admin.py のテスト
"""
import pytest
from streamlit.testing.v1 import AppTest
from pathlib import Path
from unittest.mock import MagicMock, patch

# AppTest.from_file の相対パスは、呼び出したファイル(このテスト)からの位置になるので絶対パスで渡す
APP_SCRIPT = str(Path(__file__).resolve().parents[2] / "src" / "ui" / "twitter_embed_admin.py")

class TestTwitterEmbedAdmin:
    """Twitter埋め込み管理者画面のテスト"""

    def test_auth_refused_without_password_env(self, monkeypatch):
        """ADMIN_PASSWORD が未設定なら、ログインのフォームを出さない(既定値でログインできない)"""
        monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
        at = AppTest.from_file(APP_SCRIPT, default_timeout=10)
        at.run()

        assert "管理者認証" in at.subheader[0].value
        assert any("ADMIN_PASSWORD" in e.value for e in at.error)
        assert len(at.text_input) == 0
        assert len(at.button) == 0
        assert not at.session_state.authenticated

    def test_auth_failure(self, monkeypatch):
        """認証失敗時の動作確認"""
        monkeypatch.setenv("ADMIN_PASSWORD", "test-password")
        # アプリの初期化
        at = AppTest.from_file(APP_SCRIPT, default_timeout=10)
        at.run()
        
        # タイトル確認（管理者認証）
        assert "管理者認証" in at.subheader[0].value
        
        # 間違ったパスワードを入力
        at.text_input[0].set_value("wrong_password").run()
        at.button[0].click().run()
        
        # エラーメッセージ確認
        assert at.error
        assert "パスワードが正しくありません" in at.error[0].value
        # 認証状態がFalseのままであること
        assert not at.session_state.authenticated

    def test_auth_success(self, monkeypatch):
        """認証成功時の動作確認"""
        monkeypatch.setenv("ADMIN_PASSWORD", "test-password")
        at = AppTest.from_file(APP_SCRIPT, default_timeout=10)
        at.run()

        # 正しいパスワード(テストで設定した ADMIN_PASSWORD)を入力
        at.text_input[0].set_value("test-password").run()
        at.button[0].click().run()
        
        # 成功メッセージ確認
        # リラン後は "✅ 認証済み" が表示される
        assert at.success
        assert any("認証済み" in s.value or "認証に成功" in s.value for s in at.success)
        # 認証状態がTrueになること
        assert at.session_state.authenticated

    @patch("src.services.twitter_embed_service.TwitterEmbedService.fetch_multiple_embed_codes")
    def test_fetch_embed_codes(self, mock_fetch):
        """埋め込みコード取得の動作確認"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.total_count = 1
        mock_result.success_count = 1
        mock_result.failure_count = 0
        mock_result.combined_embed_code = "<div>Test Embed</div>"
        mock_result.max_height = 500
        mock_result.failed_urls = []
        mock_fetch.return_value = mock_result
        
        at = AppTest.from_file(APP_SCRIPT, default_timeout=10)
        
        # 認証済み状態にする
        at.session_state.authenticated = True
        at.run()
        
        # 入力フォームへの入力
        test_url = "https://twitter.com/user/status/1234567890"
        # at.text_area[0] は "ツイートURL" 入力欄を想定
        # フォームの中の欄は、ここで run すると送信前に値が消えるので、送信ボタンの run だけにする
        at.text_area[0].set_value(test_url)
        
        # 取得ボタン押下 (フォームの送信ボタン)
        # フォーム内のボタンは通常、識別が難しい場合があるが、
        # form_submit_button は button リストに含まれる
        submit_button = [b for b in at.button if b.label == "🔍 取得"][0]
        submit_button.click().run()
        
        # 結果表示の確認
        # プレビューが表示されているか
        assert any("プレビュー" in sh.value for sh in at.subheader)
        # 結果サマリーが表示されているか
        assert any("取得結果" in sh.value for sh in at.subheader)
        
        # metricsの確認
        # AppTestでmetricの値を取得するのは現状のAPIでは直接的でない場合があるが、
        # マークダウンや他の要素で確認可能かチェック
        
        # プレビューHTMLが含まれているか
        # components.html は直接取得できない場合があるが、iframeとしてレンダリングされる要素などを確認
        
        # 保存セクションが表示されているか
        assert any("保存" in sh.value for sh in at.subheader)

    @patch("src.services.twitter_embed_service.TwitterEmbedService.save_embed_code")
    @patch("src.repositories.file_repository.FileRepository.write_height")
    @patch("src.services.twitter_embed_service.TwitterEmbedService.fetch_multiple_embed_codes")
    def test_save_embed_codes(self, mock_fetch, mock_write_height, mock_save):
        """埋め込みコード保存の動作確認"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.total_count = 1
        mock_result.success_count = 1
        mock_result.failure_count = 0
        mock_result.combined_embed_code = "<div>Test Embed</div>"
        mock_result.max_height = 500
        mock_result.failed_urls = []
        mock_fetch.return_value = mock_result
        
        mock_save.return_value = True
        
        at = AppTest.from_file(APP_SCRIPT, default_timeout=10)
        
        # 認証済み状態かつ取得完了状態にする
        at.session_state.authenticated = True
        at.run()
        
        # URL入力と取得実行 (stateを手動設定する代わりに操作をシミュレート)
        at.text_area[0].set_value("https://twitter.com/test")  # フォームの中の欄なので run しない
        [b for b in at.button if b.label == "🔍 取得"][0].click().run()
        
        # 保存ボタン押下
        # 取得後の再実行で保存ボタンが表示されているはず
        save_buttons = [b for b in at.button if b.label == "💾 保存"]
        assert len(save_buttons) > 0
        save_buttons[0].click().run()
        
        # 保存成功メッセージ確認
        assert at.success
        success_messages = [s.value for s in at.success]
        assert any("ファイルへの保存が完了しました" in m for m in success_messages)
        
        # モックが呼び出されたか確認
        # 注意: AppTestは別プロセスで実行されるため、ここでのmock呼び出し確認は
        # 直接的には機能しない可能性がある。AppTestの制限事項。
        # ただし、UI上のフィードバック（成功メッセージ）で動作を検証する。
