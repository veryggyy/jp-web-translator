import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import time
import re

# 1. 頁面配置：修正 layout 為官方支援的 "centered" 以建立閱讀感
st.set_page_config(page_title="小說譯閱 Pro", page_icon="📖", layout="centered")

# 2. 市售小說風格 CSS 樣式
st.markdown("""
    <style>
    /* 仿紙質書背景與字體 */
    .stApp { background-color: #f4f1ea; } 
    
    .novel-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 40px 20px;
        background-color: #ffffff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-radius: 8px;
    }

    .novel-title {
        font-family: "Noto Serif TC", serif;
        color: #1a1a1a;
        text-align: center;
        border-bottom: 2px solid #eee;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }

    .paragraph-block {
        margin-bottom: 28px;
        line-height: 1.9;
    }

    .zh-content {
        font-size: 1.2rem;
        color: #2c3e50;
        text-indent: 2em; /* 標準小說首行縮排 */
        font-family: "Microsoft JhengHei", sans-serif;
        font-weight: 400;
    }

    .jp-orig {
        display: block;
        font-size: 0.85rem;
        color: #999;
        margin-top: 6px;
        text-indent: 0;
        font-style: italic;
        border-left: 3px solid #eee;
        padding-left: 10px;
    }

    /* 隱藏多餘 UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. 核心邏輯：過濾贅詞與翻譯
def translate_novel_content(text_list):
    if not text_list: return []
    
    # 贅詞清單：自動取消導覽與系統字眼
    blacklist = [
        '下一頁', '下一一個', '前一頁', '次へ', '前へ', '目次', 
        '發生錯誤', '加入書籤', '廣告', '點此了解詳情', 'Narou Cheers'
    ]
    
    # 過濾邏輯
    cleaned_list = []
    for text in text_list:
        if not any(noise in text for noise in blacklist) and len(text) > 1:
            cleaned_list.append(text)
    
    if not cleaned_list: return []

    # 批次翻譯以提升速度
    combined = "\n\n===SPLIT===\n\n".join(cleaned_list)
    try:
        translated = GoogleTranslator(source='ja', target='zh-TW').translate(combined)
        return cleaned_list, translated.split("\n\n===SPLIT===\n\n")
    except:
        # 若批次失敗則單筆翻譯
        res = [GoogleTranslator(source='ja', target='zh-TW').translate(t) for t in cleaned_list]
        return cleaned_list, res

# 4. 主程式介面
st.markdown('<h1 style="text-align:center;">📖 小說譯閱專業版</h1>', unsafe_allow_html=True)
url = st.text_input("請貼上日文小說網址：", placeholder="https://ncode.syosetu.com...")

if url:
    try:
        with st.spinner("正在進行深度翻譯與排版中..."):
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'lxml')

            # 抓取小說主體（自動過濾側欄與廣告）
            main_content = soup.select_one('#novel_honbun, .novel_view, .episode-content')
            if not main_content:
                main_content = soup # 備援方案

            # 抓取標題
            raw_title = soup.title.string.split('「')[-1].split('」')[0] if soup.title else "章節內容"
            zh_title = GoogleTranslator(source='ja', target='zh-TW').translate(raw_title)

            st.markdown(f'<div class="novel-container"><h2 class="novel-title">{zh_title}</h2>', unsafe_allow_html=True)

            # 抓取段落
            paragraphs = [p.get_text().strip() for p in main_content.find_all(['p', 'h1', 'h2']) if p.get_text().strip()]
            
            # 分批處理
            batch_size = 10
            for i in range(0, len(paragraphs), batch_size):
                batch = paragraphs[i:i+batch_size]
                orig_cleaned, trans_batch = translate_novel_content(batch)
                
                for orig, tran in zip(orig_cleaned, trans_batch):
                    # 呈現排版
                    st.markdown(f"""
                        <div class="paragraph-block">
                            <div class="zh-content">{tran}</div>
                            <div class="jp-orig">{orig}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.success("✅ 翻譯完成！已套用專業小說排版。")

    except Exception as e:
        st.error(f"連線或解析時發生錯誤，請確認網址格式。")
