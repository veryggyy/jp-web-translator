import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import time

# 1. 頁面配置優化
st.set_page_config(page_title="JP 日文助手 PRO", page_icon="🇯🇵", layout="wide")

# 加入更專業的 CSS 樣式
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput>div>div>input { background-color: #262730; color: white; }
    .trans-card { 
        background-color: #1e1e1e; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 6px solid #00d4ff;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .orig-text { color: #888; font-size: 0.85rem; margin-top: 8px; font-style: italic; }
    .zh-text { color: #ffffff; font-size: 1.1rem; line-height: 1.6; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 JP 日文網頁專業翻譯 (加速版)")
st.caption("採用批次翻譯技術，大幅提升讀取速度與繁中精準度")

# 2. 核心功能：批次翻譯引擎
def batch_translate(text_list):
    if not text_list: return []
    # 將多個段落用特殊的換行符號連接，一次送出（減少網路請求次數）
    combined_text = "\n\n---NEXT---\n\n".join(text_list)
    try:
        translated = GoogleTranslator(source='ja', target='zh-TW').translate(combined_text)
        return translated.split("\n\n---NEXT---\n\n")
    except:
        return [GoogleTranslator(source='ja', target='zh-TW').translate(t) for t in text_list]

# 3. 輸入區
url = st.text_input("請貼上日文網址：", placeholder="https://ncode.syosetu.com...")

if url:
    try:
        start_time = time.time()
        with st.status("正在進行深度解析與批次翻譯...", expanded=True) as status:
            # 抓取網頁 (模擬真實瀏覽器防止被擋)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            res = requests.get(url, headers=headers, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'lxml')
            
            # 針對小說網站（如 syosetu）的特殊優化：抓取主體內容
            # 如果是小說，通常在 .novel_view 或 #novel_honbun
            main_content = soup.find_all(['p', 'h1', 'h2'])
            
            raw_paragraphs = []
            for p in main_content:
                text = p.get_text().strip()
                if len(text) > 2: # 過濾掉空白行
                    raw_paragraphs.append(text)

            # 顯示標題
            page_title = soup.title.string if soup.title else "日文網頁"
            st.header(GoogleTranslator(source='ja', target='zh-TW').translate(page_title))
            st.write(f"⏱️ 解析耗時: {round(time.time() - start_time, 2)} 秒")
            st.divider()

            # 執行分批翻譯（每 10 段一組，平衡速度與穩定性）
            batch_size = 10
            for i in range(0, len(raw_paragraphs), batch_size):
                batch = raw_paragraphs[i:i + batch_size]
                translated_batch = batch_translate(batch)
                
                for orig, tran in zip(batch, translated_batch):
                    st.markdown(f"""
                        <div class="trans-card">
                            <div class="zh-text">{tran}</div>
                            <div class="orig-text">{orig}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            status.update(label="✅ 翻譯完成！", state="complete")

    except Exception as e:
        st.error(f"發生錯誤：{str(e)}。這可能是因為網站設有防爬蟲機制。")
