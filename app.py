import streamlit as st
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

# 手機版顯示優化
st.set_page_config(page_title="日文翻譯助手", layout="centered")

st.title("🇯🇵 日文網頁轉繁中")
st.write("輸入日文網址，下方會自動顯示翻譯後的內容")

# 1. 網址輸入區
url = st.text_input("請貼上日文網頁網址：", placeholder="https://example.jp")

if url:
    try:
        # 2. 抓取內容
        res = requests.get(url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 3. 翻譯標題
        translator = Translator()
        st.subheader("翻譯結果：")
        title_trans = translator.translate(soup.title.string, src='ja', dest='zh-tw').text
        st.header(title_trans)
        
        # 4. 翻譯正文 (手機滑動模式)
        for p in soup.find_all('p'):
            if len(p.text) > 5:
                trans = translator.translate(p.text, src='ja', dest='zh-tw').text
                st.write(trans)
                st.divider()
    except:
        st.error("無法讀取此網址，請確認連結是否正確。")
