import streamlit as st


def display_footer():
    """
    Streamlitアプリケーションのフッターを表示する関数。
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
