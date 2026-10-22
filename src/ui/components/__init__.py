"""
UIコンポーネント

再利用可能なStreamlit UIコンポーネントを提供します。
各コンポーネントは独立して動作し、パラメータでカスタマイズ可能です。
"""

import html
import logging
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict, Collection, Optional

# ロガーの設定
logger = logging.getLogger(__name__)


def render_search_form(
    default_query: str = "",
    include_live_title: bool = True
) -> Tuple[str, bool, bool]:
    """
    検索フォームを表示する

    テキスト入力、チェックボックス、検索ボタンを含む検索フォームを表示します。
    st.form の中に置くので、入力欄で Enter キーを押しても検索ボタンと同じく送信される。
    入力欄とチェックボックスの値は、送信したときにまとめて反映される。

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

    # フォームの枠線は出さない(見た目は今までの入力欄・チェックボックス・ボタンのまま)
    with st.form("search_form", border=False):
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

        # 検索ボタン(Enter キーでも押される)
        search_button = st.form_submit_button("検索")

    if search_button:
        logger.info(f"検索が実行されました: クエリ='{current_input}', ライブタイトル検索={current_checkbox_value}")

    return current_input, current_checkbox_value, search_button



def build_results_table_html(
    df: pd.DataFrame,
    columns: List[str],
    column_headers: Dict[str, str],
    html_columns: Collection[str] = (),
) -> str:
    """
    結果テーブルの HTML を組み立てる

    html_columns 以外のセルと見出しはエスケープする。欠損は空。
    クラス名と見出しの左寄せは、以前の DataFrame.to_html(justify="left", classes="dataframe") と同じ。
    """
    def cell(value, raw: bool) -> str:
        if pd.isna(value):
            return ""
        return str(value) if raw else html.escape(str(value))

    header = "".join(
        f"<th>{html.escape(column_headers.get(col, col))}</th>" for col in columns
    )
    raw_flags = [col in html_columns for col in columns]
    rows = [
        "<tr>" + "".join(
            f"<td>{cell(value, raw)}</td>" for value, raw in zip(values, raw_flags)
        ) + "</tr>"
        for values in df[columns].itertuples(index=False, name=None)
    ]
    return (
        '<table border="1" class="dataframe">'
        f'<thead><tr style="text-align: left;">{header}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def render_results_table(
    df: pd.DataFrame,
    columns: List[str],
    column_headers: Dict[str, str],
    html_columns: Collection[str] = (),
) -> None:
    """
    結果テーブルを表示する

    DataFrameをHTMLテーブルとして表示します。
    カスタムヘッダーに対応し、スクロール可能なテーブルを生成します。

    Args:
        df: 表示するDataFrame
        columns: 表示する列のリスト
        column_headers: 列名のマッピング（元の列名 -> 表示用ヘッダー名）
        html_columns: 呼び出し側で組み立て済みの HTML の列(リンクなど)。
            中のデータ由来の文字列は、呼び出し側でエスケープしておく

    Examples:
        >>> df = pd.DataFrame({'曲名': ['曲A', '曲B'], 'アーティスト': ['歌手A', '歌手B']})
        >>> columns = ['曲名', 'アーティスト']
        >>> headers = {'曲名': '曲名', 'アーティスト': 'アーティスト'}
        >>> render_results_table(df, columns, headers)

    Notes:
        - html_columns の列だけそのまま出し、ほかの列と見出しはエスケープします
          (データ中の < や & で表が壊れないように)。欠損は空にします
        - テーブルは横スクロール可能です
    """
    logger.debug(f"結果テーブルを表示中: {len(df)}件、列={columns}")

    html_table = build_results_table_html(df, columns, column_headers, html_columns)

    # テーブルをスクロール可能なdivで囲む
    scrollable_html = f"""
    <div style="overflow-x: auto; max-width: 100%;">
        {html_table}
    </div>
    """
    
    # 生成したHTMLをStreamlitで表示
    st.write(scrollable_html, unsafe_allow_html=True)
    
    logger.debug("結果テーブルの表示が完了しました")



def _show_more(state_key: str, increment: int) -> None:
    """「さらに表示」ボタンの on_click: 表示件数を増やす(この後の1回の作り直しで、増えた件数で表が出る)"""
    st.session_state[state_key] += increment
    logger.info(f"「さらに表示」ボタンがクリックされました: 新しい表示件数={st.session_state[state_key]}")


def render_pagination(
    total_count: int,
    state_key: str,
    increment: int = 25
) -> None:
    """
    ページネーションを表示する

    「さらに表示」ボタンと件数表示を提供します。
    全件表示済みの場合は情報メッセージを表示します。
    ボタンの on_click で session_state の表示件数を増やすので、押したあとの作り直しは1回で済む
    (ボタンの戻り値を見て st.rerun() すると、1回の操作で2回作り直すことになる)。

    Args:
        total_count: 総件数
        state_key: 表示件数を持つ session_state のキー(Home は "display_limit"、楽曲リストは "song_list_limit")
        increment: 増分（デフォルト: 25）

    Examples:
        >>> # 表は st.session_state.display_limit 件まで出し、その下でボタンを出す
        >>> render_pagination(total_count=len(view), state_key="display_limit")

    Notes:
        - 表示件数が総件数より少ない場合のみボタンを表示します
        - 全件表示済みの場合は情報メッセージを表示します
    """
    current_limit = st.session_state[state_key]
    logger.debug(f"ページネーションを表示中: 総件数={total_count}, 現在の表示件数={current_limit}")

    if current_limit < total_count:
        # まだ表示していないデータがある場合
        displayed_count = min(current_limit, total_count)
        button_text = f"さらに{increment}件表示（現在の表示: {displayed_count}/{total_count}件）"
        st.button(button_text, on_click=_show_more, args=(state_key, increment))
    else:
        # 全件表示済みの場合
        st.info(f"全ての{total_count}件が表示されています。")
        logger.debug("全件表示済み")



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


def load_twitter_embed(embed_path: Path, height_path: Path) -> Optional[Tuple[str, int]]:
    """
    保存してある X の埋め込みコードと表示の高さを読む

    埋め込みコードは src.cli.twitter_embed_cli が X の oEmbed から取って保存したもの
    (保存の前に検査している)。画面の中で呼ぶので、ここでは表示をせず、ログだけ残す。

    Args:
        embed_path: 埋め込みコードのファイル(data/tweet_embed_code.html)
        height_path: 表示の高さ(ピクセル)のファイル(data/tweet_height.txt)

    Returns:
        (埋め込みコード, 高さ)。ファイルが無い・読めない・空・高さが正の整数でないときは None
    """
    try:
        embed_code = embed_path.read_text(encoding="utf-8").strip()
        height = int(height_path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError) as e:
        logger.warning(f"X の埋め込みを読めませんでした: {e}")
        return None
    if not embed_code or height <= 0:
        logger.warning(f"X の埋め込みが空か、高さが正しくありません: 高さ={height}")
        return None
    return embed_code, height
