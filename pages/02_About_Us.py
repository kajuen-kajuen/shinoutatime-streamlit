import streamlit as st
from PIL import Image

# 各ページでページ設定を行うのが良いでしょう
st.set_page_config(
    page_title="このサイトについて - しのうたタイム",
    page_icon="👻",
    layout="wide",
)

st.title("このサイトについて")

st.markdown(
    """
    ---
    このウェブサイトは、VTuber **「幽音しの」** さんの配信活動を応援するために、ファンが非公式に作成・運営しています。
    歌枠配信で歌われた楽曲の情報をまとめて、より多くのファンが楽しめるようにすることを目指しています。

    #### データの正確性について
    このサイトのデータは、有志のファンによる手作業での情報収集と入力に基づいています。
    そのため、一部情報に誤りがある可能性や、最新の情報が反映されていない場合があります。
    公式情報とは異なる点があることをご承知おきください。

    #### 注意事項
    本サイトは非公式ファンサイトであり、幽音しのさんご本人および所属事務所とは一切関係ありません。
    """
)

# ここからスペシャルサンクスを追加します
st.markdown(
    """
    ---
    ### スペシャルサンクス
    このサイトの作成にあたり、以下の皆様や情報を参考にさせていただきました。
    
    ##### 幽音しのさん
    素晴らしい歌声と配信をいつもありがとうございます。
    [公式サイト](https://www.774.ai/talent/shino-kasukane)・[YouTube](https://www.youtube.com/@Shino_Kasukane)・
    [X(旧Twitter)](https://x.com/Shino_Kasukane_)

    ##### タイムスタンプ職人さん
    データの参考とさせていただいております。ありがとうございます。
    
    ##### [りんのうた](https://reneuta.net/)さん
    サイト構成や情報の整理方法を参考にさせていただきました。ありがとうございます。
    
    ##### [裏ラジアーカイブス](https://uraradi-archives.streamlit.app/)さん
    技術基盤を参考にさせていただきました。BIG KANSYA🦉
    
    ##### [電脳図書室いんでっくす](https://owl-index.vercel.app/)さん
    一部、サイトのレイアウトを参考にさせていただきました。BIG KANSYA🦉
    
    ##### [ななしいんく 非公式Wiki](https://wikiwiki.jp/774inc/)さん
    [各種ファンサイト](https://wikiwiki.jp/774inc/%E4%BE%BF%E5%88%A9%E3%83%84%E3%83%BC%E3%83%AB#w3a76369)の情報収集に活用させていただきました。ありがとうございます。
    """
)
# ここまでスペシャルサンクス

st.markdown("---")
st.caption("Streamlit アプリケーション by Gemini")
st.caption(
    "本サイトに関する質問・バグの報告などは[@kajuen_kajuen](https://x.com/kajuen_kajuen)までお願いします。"
)
