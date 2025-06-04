import streamlit as st

st.set_page_config(
    page_title="Info - しのうたタイム",
    page_icon="👻",
    layout="wide",
)

st.title("Information")

# YouTube動画のURLを指定
youtube_url = "https://www.youtube.com/watch?v=LRowhAcHngc"  # 例：Rick Astley - Never Gonna Give You Up

st.write("---")  # 区切り線
st.subheader("ふりちゃという名の予定表置き場")
st.video(youtube_url)
