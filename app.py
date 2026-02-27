import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import time

# 1. 頁面配置：夜間模式優先
st.set_page_config(page_title="小說譯閱 Pro - 夜間版", page_icon="🌙", layout="centered")

# 2. 進階 CSS：極致夜間沉浸式排版
st.markdown("""
    <style>
    /* 全域深色背景：低藍光深煤灰 */
    .stApp { 
        background-color: #0F0F0F; 
        color: #E0E0E0;
    } 
    
    /* 閱讀容器：深灰浮雕感 */
    .novel-container {
        max-width: 850px;
        margin: 20px auto;
        padding: 50px 40px;
        background-color: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 16px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
    }

    /* 標題：亮銀色對比 */
    .novel-title {
        font-family: "Noto Serif TC", serif;
        color: #FFFFFF;
        text-align: center;
        border-bottom: 2px solid #2D2D2D;
        padding-bottom: 30px;
        margin-bottom: 40px;
        font-size: 2.2rem;
        letter-spacing: 2px;
    }

    /* 段落區塊 */
    .paragraph-block {
        margin-bottom: 35px;
        line-height: 2.0;
    }

    /* 中文本文：柔和白（不刺眼） */
    .zh-content {
        font-size: 1.3rem;
        color: #D6D6D6;
        text-indent: 2.5em; /* 加大首行縮排，更有小說質感 */
        font-family: "Microsoft JhengHei", "PingFang TC", sans-serif;
    }

    /* 日文原文：幽靈灰（極低干擾，僅供比對） */
    .jp-orig {
        display: block;
        font-size: 0.95rem;
        color: #666666;
        margin-top: 10px;
        text-indent: 0;
        font-style: italic;
        border-left: 3px solid #4A90E2; /* 藍色導引線，方便對照 */
        padding-left: 15px;
    }

    /* 調整 Streamlit 輸入框與按鈕在夜間模式下的視覺 */
    .stTextInput input {
        background-color: #262626 !important;
        color: #FFFFFF !important;
        border: 1px solid #444 !important;
    }
    .stTextInput label { color: #888 !important; }
    
    /* 隱藏多餘雜訊 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. 核心翻譯邏輯 (內建贅詞剔除)
def translate_novel_content(text_list):
    if not text_list: return []
    
    # 自動取消所有導覽與廣告文字
    blacklist = [
        '下一頁', '下一一個', '前一頁', '次へ', '前へ', '目次', '導覽',
        '發生錯誤', '加入書籤', '廣告', '廣告贊助', 'Narou Cheers', '點此了解'
    ]
    
    cleaned_list = []
    for t in text_list:
        if not any(noise in t for noise in blacklist) and len(t) > 2:
            cleaned_list.append(t)
    
    if not cleaned_list: return []

    combined = "\n\n===SPLIT===\n\n".join(cleaned_list)
    try:
        translated = GoogleTranslator(source='ja', target='zh-TW').translate(combined)
        return cleaned_list, translated.split("\n\n===SPLIT===\n\n")
    except:
        res = [GoogleTranslator(source='ja', target='zh-TW').translate(t) for t in cleaned_list]
        return cleaned_list, res

# 4. 主程式介面
st.markdown('<h1 style="text-align:center; color:#4A90E2; font-weight:300;">🌙 小說譯閱｜夜間模式</h1>', unsafe_allow_html=True)
url = st.text_input("請輸入日文小說網址：", placeholder="https://ncode.syosetu.com...")

if url:
    try:
        with st.spinner("🌙 正在進入沈浸式翻譯環境..."):
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'lxml')

            # 定位主本文 (針對主流小說站點優化)
            main_content = soup.select_one('#novel_honbun, .novel_view, .episode-content, #story')
            if not main_content: main_content = soup

            # 章節標題處理
            raw_title = soup.title.string.split('「')[-1].split('」')[0] if soup.title else "章節內容"
            zh_title = GoogleTranslator(source='ja', target='zh-TW').translate(raw_title)

            # 渲染容器
            st.markdown(f'<div class="novel-container"><h2 class="novel-title">{zh_title}</h2>', unsafe_allow_html=True)

            paragraphs = [p.get_text().strip() for p in main_content.find_all(['p', 'h1', 'h2']) if p.get_text().strip()]
            
            # 分批翻譯 (提升效能)
            batch_size = 12
            for i in range(0, len(paragraphs), batch_size):
                batch = paragraphs[i:i+batch_size]
                orig_cleaned, trans_batch = translate_novel_content(batch)
                
                for orig, tran in zip(orig_cleaned, trans_batch):
                    st.markdown(f"""
                        <div class="paragraph-block">
                            <div class="zh-content">{tran}</div>
                            <div class="jp-orig">{orig}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.toast("✅ 翻譯已完成，請享受閱讀時間。")

    except Exception as e:
        st.error("連線或翻譯過程中斷，請確認網址是否受保護。")
