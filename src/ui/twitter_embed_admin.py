"""
Twitter埋め込みコード管理画面

このモジュールは、Streamlitアプリケーション内でTwitter埋め込みコードを
管理するための管理画面を提供します。

主な機能:
- パスワード認証によるアクセス制御
- ツイートURL入力フォーム
- 埋め込みコード取得と保存
- プレビュー表示
- エラーハンドリング

要件: 4.1, 4.2, 4.3, 4.4, 4.5
"""

import os
import logging
import streamlit as st
import streamlit.components.v1 as components
from typing import List, Optional

from src.services.twitter_embed_service import TwitterEmbedService
from src.clients.twitter_api_client import TwitterAPIClient
from src.repositories.file_repository import FileRepository
from src.config.settings import TwitterEmbedConfig
from src.models.embed_result import MultipleEmbedCodeResult
from src.utils.html_validator import validate_twitter_embed_code

# ロガーの設定
logger = logging.getLogger(__name__)


def check_admin_auth() -> bool:
    """
    管理者認証をチェック
    
    セッション状態で認証状態を管理し、未認証の場合は
    パスワード入力フォームを表示します。
    
    Returns:
        bool: 認証済みの場合True
    
    要件: 4.5
    """
    # セッション状態の初期化
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # 既に認証済みの場合
    if st.session_state.authenticated:
        return True
    
    # 認証フォームを表示
    st.subheader("🔒 管理者認証")

    # 環境変数からパスワードを取得する。既定値は持たない(公開リポジトリなので、既定値は誰でも読める)。
    # 未設定のときはログインさせない
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_password:
        logger.warning("管理者認証: ADMIN_PASSWORD が未設定のためログインを受け付けない")
        st.error("管理者パスワード(ADMIN_PASSWORD)が設定されていないため、ログインできません。")
        return False

    st.info("この機能を使用するには管理者パスワードが必要です。")

    # パスワード入力
    password = st.text_input(
        "パスワード",
        type="password",
        key="admin_password_input"
    )
    
    # ログインボタン
    if st.button("ログイン", key="admin_login_button"):
        if password == admin_password:
            st.session_state.authenticated = True
            logger.info("管理者認証成功")
            st.success("認証に成功しました！")
            st.rerun()
        else:
            logger.warning("管理者認証失敗: 不正なパスワード")
            st.error("パスワードが正しくありません。")
    
    return False


def parse_tweet_urls(input_text: str) -> List[str]:
    """
    入力テキストからツイートURLのリストを抽出
    
    改行で区切られたURLを解析し、空行や空白を除去します。
    
    Args:
        input_text: 入力テキスト（複数行可）
    
    Returns:
        List[str]: ツイートURLのリスト
    """
    # 改行で分割し、前後の空白を除去
    urls = [line.strip() for line in input_text.split("\n")]
    # 空行を除去
    urls = [url for url in urls if url]
    return urls


def render_embed_preview(embed_code: str, height: int = 850) -> None:
    """
    埋め込みコードのプレビューを表示
    
    Args:
        embed_code: 埋め込みHTMLコード
        height: 表示高さ（ピクセル単位）
    
    要件: 4.3
    """
    st.subheader("📱 プレビュー")
    
    # 3カラムレイアウトで中央に表示
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if embed_code:
            components.html(
                embed_code,
                height=height,
                scrolling=True
            )
        else:
            st.info("プレビューする埋め込みコードがありません。")


def render_result_summary(result: MultipleEmbedCodeResult) -> None:
    """
    取得結果のサマリーを表示
    
    Args:
        result: 複数ツイート取得結果
    
    要件: 4.3
    """
    st.subheader("📊 取得結果")
    
    # 結果サマリーを3カラムで表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("総件数", result.total_count)
    
    with col2:
        st.metric("成功", result.success_count, delta_color="normal")
    
    with col3:
        st.metric("失敗", result.failure_count, delta_color="inverse")
    
    # 失敗したURLがある場合は表示
    if result.failed_urls:
        st.warning("⚠️ 以下のURLの取得に失敗しました:")
        for url in result.failed_urls:
            st.text(f"  • {url}")
    
    # 最大高さを表示
    if result.max_height:
        st.info(f"📏 表示高さ: {result.max_height}px")


def render_twitter_embed_admin(enable_admin_features: bool = True) -> None:
    """
    Twitter埋め込みコード管理画面を表示
    
    認証、URL入力フォーム、取得処理、結果表示、プレビューを含む
    完全な管理画面を提供します。
    
    Args:
        enable_admin_features: 管理機能を有効にするか（デフォルト: True）
                              Falseの場合、閲覧のみ可能
    
    要件: 4.1, 4.2, 4.3, 4.4, 4.5
    """
    st.header("🐦 Twitter埋め込みコード管理")
    
    # 本番・ステージング環境では管理機能を無効化
    if not enable_admin_features:
        st.warning("⚠️ この環境では管理機能は無効化されています。")
        st.info("""
        **閲覧モード**
        
        現在、本番環境またはステージング環境で実行されているため、
        Twitter埋め込みコードの取得・保存機能は無効化されています。
        
        管理機能を使用するには、ローカル環境で実行してください。
        """)
        
        # 現在の埋め込みコードを表示（閲覧のみ）
        st.markdown("---")
        st.subheader("📄 現在の埋め込みコード")
        
        try:
            config = TwitterEmbedConfig.from_env()
            file_repo = FileRepository(
                embed_code_path=config.embed_code_path,
                height_path=config.height_path,
                backup_dir=config.backup_dir
            )
            
            current_code = file_repo.read_embed_code()
            current_height = file_repo.read_height()
            
            if current_code:
                st.success(f"✅ 埋め込みコードが設定されています（高さ: {current_height}px）")
                
                # プレビューを表示
                with st.expander("プレビューを表示", expanded=False):
                    render_embed_preview(current_code, current_height)
                
                # コードを表示
                with st.expander("HTMLコードを表示", expanded=False):
                    st.code(current_code, language="html")
            else:
                st.info("埋め込みコードが設定されていません。")
        
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {str(e)}")
            logger.error(f"埋め込みコード読み込みエラー: {str(e)}", exc_info=True)
        
        return
    
    # 認証チェック（ローカル環境のみ）
    if not check_admin_auth():
        return
    
    # 認証済みの場合、管理画面を表示
    st.success("✅ 認証済み")
    
    # ログアウトボタン
    if st.button("ログアウト", key="admin_logout_button"):
        st.session_state.authenticated = False
        logger.info("管理者ログアウト")
        st.rerun()
    
    st.markdown("---")
    
    # 説明
    st.markdown("""
    この画面では、TwitterのツイートURLから埋め込みコードを自動取得し、
    `data/tweet_embed_code.html`ファイルに保存できます。
    
    **使い方:**
    1. 下のテキストエリアにツイートURLを入力（複数の場合は1行に1つ）
    2. 必要に応じてオプションを設定
    3. 「取得」ボタンをクリック
    4. プレビューを確認
    5. 「保存」ボタンで確定
    """)
    
    # URL入力フォーム
    st.subheader("📝 ツイートURL入力")
    
    with st.form("tweet_url_form", clear_on_submit=False):
        tweet_urls_input = st.text_area(
            "ツイートURL（1行に1つ）",
            height=150,
            placeholder="https://twitter.com/username/status/1234567890\nhttps://x.com/username/status/0987654321",
            help="複数のツイートを指定する場合は、1行に1つずつ入力してください。"
        )
        
        # オプション設定
        col1, col2 = st.columns(2)
        
        with col1:
            create_backup = st.checkbox(
                "バックアップを作成",
                value=True,
                help="既存のファイルをバックアップしてから保存します。"
            )
        
        with col2:
            auto_save = st.checkbox(
                "取得後に自動保存",
                value=False,
                help="取得成功後、確認なしで自動的にファイルに保存します。"
            )
        
        # 取得ボタン
        submitted = st.form_submit_button(
            "🔍 取得",
            use_container_width=True,
            type="primary"
        )
    
    # フォームが送信された場合
    if submitted:
        if not tweet_urls_input.strip():
            st.error("❌ ツイートURLを入力してください。")
            return
        
        # URLリストを解析
        tweet_urls = parse_tweet_urls(tweet_urls_input)
        
        if not tweet_urls:
            st.error("❌ 有効なツイートURLが見つかりませんでした。")
            return
        
        st.info(f"🔄 {len(tweet_urls)}件のツイートを処理中...")
        
        # 設定を読み込み
        config = TwitterEmbedConfig.from_env()
        
        # サービスを初期化
        api_client = TwitterAPIClient(
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )
        file_repo = FileRepository(
            embed_code_path=config.embed_code_path,
            height_path=config.height_path,
            backup_dir=config.backup_dir
        )
        service = TwitterEmbedService(
            api_client=api_client,
            file_repo=file_repo,
            logger=logger
        )
        
        # 埋め込みコードを取得
        try:
            with st.spinner("取得中..."):
                result = service.fetch_multiple_embed_codes(tweet_urls)
            
            # セッション状態に結果を保存
            st.session_state.fetch_result = result
            st.session_state.create_backup = create_backup
            
            # 結果サマリーを表示
            render_result_summary(result)
            
            # 成功した場合
            if result.success_count > 0:
                st.success(f"✅ {result.success_count}件のツイートの取得に成功しました！")
                
                # HTML検証を実行して結果を表示（要件6.1, 6.2）
                if result.combined_embed_code:
                    is_valid, validation_messages = validate_twitter_embed_code(
                        result.combined_embed_code
                    )
                    
                    if is_valid and validation_messages:
                        # 警告がある場合
                        with st.expander("⚠️ HTML検証警告", expanded=False):
                            for warning in validation_messages:
                                st.warning(warning)
                    elif not is_valid:
                        # エラーがある場合
                        with st.expander("❌ HTML検証エラー", expanded=True):
                            for error in validation_messages:
                                st.error(error)
                    else:
                        # 検証成功
                        st.info("✅ HTML検証: 成功")
                
                # プレビューを表示
                render_embed_preview(
                    result.combined_embed_code,
                    result.max_height
                )
                
                # 自動保存が有効な場合
                if auto_save:
                    st.info("💾 自動保存を実行中...")
                    save_success = service.save_embed_code(
                        result.combined_embed_code,
                        create_backup=create_backup
                    )
                    
                    if save_success:
                        # 高さも保存
                        file_repo.write_height(result.max_height)
                        st.success("✅ ファイルへの保存が完了しました！")
                        logger.info(
                            f"埋め込みコード自動保存成功: "
                            f"{result.success_count}件, 高さ={result.max_height}px"
                        )
                    else:
                        st.error("❌ ファイルへの保存に失敗しました。")
                        logger.error("埋め込みコード自動保存失敗")
            else:
                st.error("❌ 全てのツイートの取得に失敗しました。")
                logger.error(f"全ツイート取得失敗: {len(tweet_urls)}件")
        
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {str(e)}")
            logger.error(f"埋め込みコード取得エラー: {str(e)}", exc_info=True)
    
    # 取得結果がセッション状態にある場合、保存ボタンを表示
    if "fetch_result" in st.session_state:
        result = st.session_state.fetch_result
        create_backup = st.session_state.get("create_backup", True)
        
        if result.success_count > 0:
            st.markdown("---")
            st.subheader("💾 保存")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info(
                    f"取得した埋め込みコード（{result.success_count}件）を "
                    f"`{TwitterEmbedConfig.from_env().embed_code_path}` に保存します。"
                )
            
            with col2:
                if st.button(
                    "💾 保存",
                    use_container_width=True,
                    type="primary",
                    key="save_button"
                ):
                    # 設定を読み込み
                    config = TwitterEmbedConfig.from_env()
                    
                    # サービスを初期化
                    api_client = TwitterAPIClient(
                        max_retries=config.max_retries,
                        retry_delay=config.retry_delay
                    )
                    file_repo = FileRepository(
                        embed_code_path=config.embed_code_path,
                        height_path=config.height_path,
                        backup_dir=config.backup_dir
                    )
                    service = TwitterEmbedService(
                        api_client=api_client,
                        file_repo=file_repo,
                        logger=logger
                    )
                    
                    # 保存実行
                    with st.spinner("保存中..."):
                        save_success = service.save_embed_code(
                            result.combined_embed_code,
                            create_backup=create_backup
                        )
                    
                    if save_success:
                        # 高さも保存
                        file_repo.write_height(result.max_height)
                        st.success("✅ ファイルへの保存が完了しました！")
                        logger.info(
                            f"埋め込みコード保存成功: "
                            f"{result.success_count}件, 高さ={result.max_height}px"
                        )
                        
                        # セッション状態をクリア
                        del st.session_state.fetch_result
                        if "create_backup" in st.session_state:
                            del st.session_state.create_backup
                    else:
                        st.error("❌ ファイルへの保存に失敗しました。")
                        logger.error("埋め込みコード保存失敗")


# メイン実行（テスト用）
if __name__ == "__main__":
    st.set_page_config(
        page_title="Twitter埋め込みコード管理",
        page_icon="🐦",
        layout="wide"
    )
    render_twitter_embed_admin()
