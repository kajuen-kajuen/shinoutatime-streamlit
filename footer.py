"""
footer.py - フッター表示モジュール

このモジュールは、しのうたタイムアプリケーションの全ページで共通して使用される
フッター表示機能を提供します。

主な機能:
- 区切り線の表示
- クレジット情報の表示
- 連絡先情報の表示

使用方法:
    from footer import display_footer
    
    # ページの最後でフッターを表示
    display_footer()

要件: 12.1, 12.2, 12.3
"""

import streamlit as st


def display_footer():
    """
    Streamlitアプリケーションのフッターを表示する関数。
    
    この関数は、アプリケーションの全ページで共通のフッターを表示します。
    フッターには以下の要素が含まれます：
    - 水平区切り線（---）
    - クレジット表示（「Streamlit アプリケーション by Gemini」）
    - 連絡先情報（質問・バグ報告先のTwitterアカウント）
    
    表示内容:
        - 区切り線: ページコンテンツとフッターを視覚的に分離
        - クレジット: アプリケーションの作成者情報
        - 連絡先: サイトに関する質問やバグ報告の連絡先（@kajuen_kajuen）
    
    使用方法:
        各ページファイル（Home.py、pages/*.py）の最後で呼び出します。
        
        例:
            import streamlit as st
            from footer import display_footer
            
            # ページのメインコンテンツ
            st.title("ページタイトル")
            st.write("ページの内容...")
            
            # フッターを表示
            display_footer()
    
    引数:
        なし
    
    戻り値:
        なし
    
    副作用:
        - Streamlitのマークダウンとキャプション要素をページに追加します
        - ページの表示状態を変更します
    
    注意事項:
        - この関数はStreamlit環境でのみ動作します
        - ページの最後で呼び出すことを推奨します
        - 複数回呼び出すと、フッターが複数回表示されます
    
    要件: 12.1, 12.2, 12.3
    """
    st.markdown("---")
    st.caption("Streamlit アプリケーション by Gemini")
    st.caption(
        "本サイトに関する質問・バグの報告などは[@kajuen_kajuen](https://x.com/kajuen_kajuen)までお願いします。"
    )


if __name__ == "__main__":
    # このファイルが直接実行された場合のテストコード
    st.set_page_config(
        page_title="フッターテスト",
        layout="centered",
    )
    st.title("フッターテストページ")
    st.write("このページはフッターモジュールのテスト用です。")
    display_footer()
