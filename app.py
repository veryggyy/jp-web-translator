import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import time

# 1. 頁面配置：維持極致夜間沈浸模式
st.set_page_config(page_title="小說譯閱 Pro - 夜間版", page_icon="🌙", layout="centered")

# 2. CSS：維持夜間沉浸式排版
st.markdown("""
    <style>
    .stApp { background-color: #0F0F0F; color: #E0E0E0; } 
    .novel-container {
        max-width: 850px;
        margin: 20px auto;
        padding: 50px 40px;
        background-color: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 16px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
    }
    .novel-title {
        font-family: "Noto Serif TC", serif;
        color: #FFFFFF;
        text-align: center;
        border-bottom: 2px solid #2D2D2D;
        padding-bottom: 30px;
        margin-bottom: 40px;
        font-size: 2.2rem;
    }
    .paragraph-block { margin-bottom: 35px; line-height: 2.0; }
    .zh-content {
        font-size: 1.3rem;
        color: #D6D6D6;
        text-indent: 2.5em; 
        font-family: "Microsoft JhengHei", sans-serif;
    }
    .jp-orig {
        display: block;
        font-size: 0.95rem;
        color: #666666;
        margin-top: 10px;
        text-indent: 0;
        font-style: italic;
        border-left: 3px solid #4A90E2;
        padding-left: 15px;
    }
    .stTextInput input { background-color: #262626 !important; color: #FFFFFF !important; }
    #MainMenu, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. 核心邏輯：優化空白處理與贅詞剔除
def translate_novel_content(text_list):
    if not text_list: return []
    
    # 贅詞清單
    blacklist = ['下一頁', '下一一個', '前一頁', '次へ', '前へ', '目次', '發生錯誤', '加入書籤', '廣告']
    
    cleaned_list = []
    for t in text_list:
        # 邏輯 A：如果是純空白（含全形、半形、換行），直接保留原始空白不翻譯
        if not t.strip():
            cleaned_list.append(t)
            continue
        # 邏輯 B：剔除黑名單贅詞
        if any(noise in t for noise in blacklist):
            continue
        cleaned_list.append(t)
    
    if not cleaned_list: return []

    # 批次翻譯，但跳過純空白的段落
    translated_results = []
    for t in cleaned_list:
        if not t.strip():
            translated_results.append("&nbsp;") # 直接用 HTML 空格代表空白處
        else:
            try:
                # 翻譯單一有效段落，確保不會把空白處轉成符號
                res = GoogleTranslator(source='ja', target='zh-TW').translate(t)
                translated_results.append(res)
            except:
                translated_results.append(t)
                
    return cleaned_list, translated_results

# 4. 主程式介面
st.markdown('<h1 style="text-align:center; color:#4A90E2;">🌙 小說譯閱｜純淨夜間模式</h1>', unsafe_allow_html=True)
url = st.text_input("請輸入日文小說網址：", placeholder="https://ncode.syosetu.com...")

if url:
    try:
        with st.spinner("🌙 正在處理純淨排版中..."):
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'lxml')

            main_content = soup.select_one('#novel_honbun, .novel_view, .episode-content, #story')
            if not main_content: main_content = soup

            raw_title = soup.title.string.split('「')[-1].split('」')[0] if soup.title else "章節內容"
            zh_title = GoogleTranslator(source='ja', target='zh-TW').translate(raw_title)

            st.markdown(f'<div class="novel-container"><h2 class="novel-title">{zh_title}</h2>', unsafe_allow_html=True)

            # 抓取所有段落與空行
            paragraphs = [p.get_text() for p in main_content.find_all(['p', 'h1', 'h2'])]
            
            orig_cleaned, trans_list = translate_novel_content(paragraphs)
            
            for orig, tran in zip(orig_cleaned, trans_list):
                # 如果是空白處，則渲染成空行
                if not orig.strip():
                    st.markdown('<br>', unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="paragraph-block">
                            <div class="zh-content">{tran}</div>
                            <div class="jp-orig">{orig}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.toast("✅ 純淨排版已完成。")

    except Exception as e:
        st.error("解析失敗，請檢查網址或稍後再試。")
