import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

# 1. 專業 App 頁面設定
st.set_page_config(page_title="日文閱讀助手", page_icon="🇯🇵", layout="centered")

# 介面美化 CSS
st.markdown("""
    <style>
    .trans-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 20px; }
    .orig-text { color: #666; font-size: 0.85rem; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇯🇵 日文網頁專業翻譯")
st.write("專為手機設計，輸入網址即可輕鬆閱讀繁體中文")

# 2. 輸入區
target_url = st.text_input("請貼上日文網址：", placeholder="https://news.yahoo.co.jp...")

if target_url:
    try:
        with st.spinner('🚀 正在讀取並翻譯中...'):
            # 抓取網頁
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(target_url, headers=headers, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 翻譯標題
            raw_title = soup.title.string if soup.title else "無標題網頁"
            translated_title = GoogleTranslator(source='ja', target='zh-TW').translate(raw_title)
            
            st.header(f"📖 {translated_title}")
            st.divider()
            
            # 3. 抓取段落並翻譯
            paragraphs = soup.find_all(['p', 'h2', 'h3'])
            
            for p in paragraphs:
                original = p.get_text().strip()
                if len(original) > 10:  # 過濾雜訊
                    # 執行翻譯
                    translated = GoogleTranslator(source='ja', target='zh-TW').translate(original)
                    
                    # 專業美化顯示
                    st.markdown(f"""
                        <div class="trans-box">
                            <strong>{translated}</strong>
                            <div class="orig-text">{original}</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.success("✅ 全部翻譯完成！您可以直接將此頁面分享給好友。")
            
    except Exception as e:
        st.error(f"讀取網頁時發生錯誤，請確認網址是否正確。")
