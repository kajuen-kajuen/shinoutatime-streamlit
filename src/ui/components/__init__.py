"""
UIコンポーネント

再利用可能なStreamlit UIコンポーネントを提供します。
各コンポーネントは独立して動作し、パラメータでカスタマイズ可能です。
"""

import logging
import streamlit as st
import pandas as pd
from typing import Tuple, List, Dict, Optional

# ロガーの設定
logger = logging.getLogger(__name__)


def render_search_form(
    default_query: str = "",
    include_live_title: bool = True
) -> Tuple[str, bool, bool]:
    """
    検索フォームを表示する
    
    テキスト入力、チェックボックス、検索ボタンを含む検索フォームを表示します。
    
    Args:
        default_query: デフォルトの検索クエリ
        include_live_title: ライブタイトル検索のデフォルト値
    
    Returns:
        Tuple[str, bool, bool]: (検索クエリ, ライブタイトル検索フラグ, 検索ボタンクリック)
            - 検索クエリ: ユーザーが入力した検索キーワード
            - ライブタイトル検索フラグ: 配信タイトルを検索対象に含めるかどうか
            - 検索ボタンクリック: 検索ボタンがクリックされたかどうか
    
    Examples:
        >>> query, include_title, clicked = render_search_form()
        >>> if clicked:
        ...     # 検索処理を実行
        ...     pass
    """
    logger.debug("検索フォームを表示中")
    
    # テキスト入力ボックス
    current_input = st.text_input(
        "キーワード検索（曲名、アーティスト）",
        value=default_query,
        key="search_input_box",
        placeholder="ここにキーワードを入力",
    )
    
    # チェックボックス
    current_checkbox_value = st.checkbox(
        "検索対象にライブ配信タイトルを含める",
        value=include_live_title,
        key="include_live_title_checkbox",
    )
    
    # 検索ボタン
    search_button = st.button("検索")
    
    if search_button:
        logger.info(f"検索ボタンがクリックされました: クエリ='{current_input}', ライブタイトル検索={current_checkbox_value}")
    
    return current_input, current_checkbox_value, search_button



def render_results_table(
    df: pd.DataFrame,
    columns: List[str],
    column_headers: Dict[str, str]
) -> None:
    """
    結果テーブルを表示する
    
    DataFrameをHTMLテーブルとして表示します。
    カスタムヘッダーに対応し、スクロール可能なテーブルを生成します。
    
    Args:
        df: 表示するDataFrame
        columns: 表示する列のリスト
        column_headers: 列名のマッピング（元の列名 -> 表示用ヘッダー名）
    
    Examples:
        >>> df = pd.DataFrame({'曲名': ['曲A', '曲B'], 'アーティスト': ['歌手A', '歌手B']})
        >>> columns = ['曲名', 'アーティスト']
        >>> headers = {'曲名': '曲名', 'アーティスト': 'アーティスト'}
        >>> render_results_table(df, columns, headers)
    
    Notes:
        - HTMLタグを含む列（リンクなど）はそのまま表示されます
        - テーブルは横スクロール可能です
        - アーティスト列には自動的にartist-cellクラスが適用されます
    """
    logger.debug(f"結果テーブルを表示中: {len(df)}件、列={columns}")
    
    # 表示する列のみを選択
    df_display = df[columns].copy()
    
    # DataFrameをHTMLテーブルに変換
    # escape=False: HTMLタグをそのまま表示（リンクとCSSクラスを有効化）
    # index=False: 行番号を非表示
    html_table = df_display.to_html(
        escape=False, 
        index=False, 
        justify="left", 
        classes="dataframe"
    )
    
    # テーブルヘッダーをカスタムヘッダーに置き換え
    for original, custom in column_headers.items():
        html_table = html_table.replace(
            f"<th>{original}</th>", 
            f"<th>{custom}</th>"
        )
    
    # テーブルをスクロール可能なdivで囲む
    scrollable_html = f"""
    <div style="overflow-x: auto; max-width: 100%;">
        {html_table}
    </div>
    """
    
    # 生成したHTMLをStreamlitで表示
    st.write(scrollable_html, unsafe_allow_html=True)
    
    logger.debug("結果テーブルの表示が完了しました")



def render_pagination(
    total_count: int,
    current_limit: int,
    increment: int = 25
) -> Optional[int]:
    """
    ページネーションを表示する
    
    「さらに表示」ボタンと件数表示を提供します。
    全件表示済みの場合は情報メッセージを表示します。
    
    Args:
        total_count: 総件数
        current_limit: 現在の表示件数
        increment: 増分（デフォルト: 25）
    
    Returns:
        Optional[int]: 新しい表示件数。変更がない場合はNone
            - ボタンがクリックされた場合: current_limit + increment
            - ボタンがクリックされなかった場合: None
    
    Examples:
        >>> new_limit = render_pagination(total_count=100, current_limit=25)
        >>> if new_limit:
        ...     # 表示件数を更新
        ...     st.session_state.display_limit = new_limit
        ...     st.rerun()
    
    Notes:
        - 表示件数が総件数より少ない場合のみボタンを表示します
        - 全件表示済みの場合は情報メッセージを表示します
    """
    logger.debug(f"ページネーションを表示中: 総件数={total_count}, 現在の表示件数={current_limit}")
    
    if current_limit < total_count:
        # まだ表示していないデータがある場合
        displayed_count = min(current_limit, total_count)
        button_text = f"さらに{increment}件表示（現在の表示: {displayed_count}/{total_count}件）"
        
        if st.button(button_text):
            # ボタンがクリックされたら新しい表示件数を返す
            new_limit = current_limit + increment
            logger.info(f"「さらに表示」ボタンがクリックされました: 新しい表示件数={new_limit}")
            return new_limit
    else:
        # 全件表示済みの場合
        st.info(f"全ての{total_count}件が表示されています。")
        logger.debug("全件表示済み")
    
    return None



def render_twitter_embed(
    embed_code: str,
    height: int,
) -> None:
    """
    Twitter埋め込みを表示する
    
    Twitterの埋め込みコードと高さを受け取り、中央カラムに表示します。
    
    Args:
        embed_code: 埋め込みHTMLコード
        height: 高さ（ピクセル単位）
    
    Examples:
        >>> render_twitter_embed(
        ...     '<blockquote class="twitter-tweet">...</blockquote>',
        ...     850
        ... )
    
    Notes:
        - 埋め込みコードが空の場合は情報メッセージを表示します
        - 画面レイアウトは3カラム [1, 2, 1] で中央に表示されます
        - スクロール可能なコンポーネントとして表示されます
    """
    import streamlit.components.v1 as components
    
    logger.debug(f"Twitter埋め込みを表示中: 高さ={height}px")
    
    # 画面レイアウトを3つのカラムに分割し、中央にコンテンツを配置
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if embed_code:
            # Streamlitのcomponents.htmlを使用してTwitter埋め込みコードを表示
            components.html(
                embed_code,
                height=height,
                scrolling=True,
            )
            logger.info("Twitter埋め込みの表示が完了しました")
        else:
            # 埋め込みコードが空だった場合の情報メッセージ
            logger.warning("埋め込みコードが空です")
            st.info("Twitterの埋め込み情報が読み込まれませんでした。")
