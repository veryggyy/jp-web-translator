import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import time

# 1. 頁面配置優化：打造沈浸式小說閱讀感
st.set_page_config(page_title="小說譯閱 Pro", page_icon="📖", layout="narrow")

# 進階 CSS 樣式：模擬電子書排版，移除雜訊與裝飾
st.markdown("""
    <style>
    /* 全域背景與字型 */
    .stApp { background-color: #fdfdfd; }
    
    /* 標題區域 */
    .novel-header {
        text-align: center;
        margin-bottom: 50px;
        color: #1a1a1a;
        font-family: "Noto Serif TC", serif;
    }
    
    /* 小說本文樣式：直向排版間距優化 */
    .novel-body {
        max-width: 700px;
        margin: 0 auto;
        font-family: "Georgia", "Microsoft JhengHei", serif;
        line-height: 1.8;
        color: #2c3e50;
        letter-spacing: 0.05em;
    }
    
    /* 段落美化 */
    .novel-paragraph {
        margin-bottom: 24px;
        text-indent: 2em; /* 首行縮排，符合小說習慣 */
        font-size: 1.15rem;
    }

    /* 原文對照樣式：極簡淡化 */
    .orig-text {
        display: block;
        color: #999;
        font-size: 0.85rem;
        margin-top: 4px;
        text-indent: 0;
        font-style: italic;
    }

    /* 隱藏 Streamlit 預設元件以提升美感 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. 核心功能：翻譯引擎 (移除多餘字眼)
def clean_and_translate(text_list):
    if not text_list: return []
    # 過濾小說網站常見的廣告與導覽字眼
    noise_words = ['次へ', '前へ', '目次', '下一頁', '下一一個', '發生錯誤']
    cleaned_list = [t for t in text_list if not any(noise in t for noise in noise_words)]
    
    if not cleaned_list: return []
    
    combined_text = "\n\n---NEXT---\n\n".join(cleaned_list)
    try:
        translated = GoogleTranslator(source='ja', target='zh-TW').translate(combined_text)
        return cleaned_list, translated.split("\n\n---NEXT---\n\n")
    except:
        # 備援機制
        return cleaned_list, [GoogleTranslator(source='ja', target='zh-TW').translate(t) for t in cleaned_list]

# 3. 介面呈現
st.markdown('<div class="novel-header"><h1>📖 小說譯閱專業版</h1><p>極簡純淨的小說翻譯空間</p></div>', unsafe_allow_html=True)

url = st.text_input("輸入日文小說網址：", placeholder="https://ncode.syosetu.com...")

if url:
    try:
        start_time = time.time()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'lxml')

        # 精準定位小說內容（針對常見平台如 Syosetu, Kakuyomu）
        content_div = soup.select_one('#novel_honbun, .novel_view, .episode-content, .entry-content')
        
        if content_div:
            # 只取段落 p 標籤，這通常能有效過濾掉導覽按鈕
            paragraphs = [p.get_text().strip() for p in content_div.find_all('p') if p.get_text().strip()]
        else:
            # 備援：抓取所有 p
            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 5]

        # 頁面標題翻譯
        page_title = soup.title.string.split('「')[-1].split('」')[0] if soup.title else "未命名章節"
        zh_title = GoogleTranslator(source='ja', target='zh-TW').translate(page_title)
        
        st.markdown(f"<h2 style='text-align:center;'>{zh_title}</h2>", unsafe_allow_html=True)
        st.caption(f"✨ 深度潤飾完成 | 耗時 {round(time.time() - start_time, 2)} 秒")
        st.divider()

        # 分批翻譯與排版呈現
        batch_size = 8
        for i in range(0, len(paragraphs), batch_size):
            batch = paragraphs[i:i + batch_size]
            orig_cleaned, trans_batch = clean_and_translate(batch)
            
            for orig, tran in zip(orig_cleaned, trans_batch):
                st.markdown(f"""
                    <div class="novel-body">
                        <div class="novel-paragraph">
                            {tran}
                            <span class="orig-text">{orig}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error("解析失敗，請確認網址是否正確或該網站是否有存取限制。")
