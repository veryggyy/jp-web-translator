import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import time
import random

# 1. 頁面配置：維持夜間純淨模式
st.set_page_config(page_title="小說譯閱 Pro - 防封鎖版", page_icon="🌙", layout="centered")

# 2. CSS：夜間沉浸式排版
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
    .paragraph-block { margin-bottom: 30px; line-height: 2.0; }
    .zh-content { font-size: 1.25rem; color: #D6D6D6; text-indent: 2.5em; font-family: "Microsoft JhengHei", sans-serif; }
    .jp-orig { display: block; font-size: 0.9rem; color: #666666; margin-top: 8px; border-left: 3px solid #4A90E2; padding-left: 15px; font-style: italic; }
    #MainMenu, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. 翻譯核心：空白預留與批次處理
def batch_translate_safe(text_list):
    if not text_list: return []
    
    # 贅詞黑名單
    blacklist = ['下一頁', '下一一個', '前一頁', '次へ', '前へ', '目次', '加入書籤']
    
    processed_list = []
    to_translate = []
    
    for t in text_list:
        clean_t = t.strip()
        # 邏輯：空白或黑名單文字，標記為跳過
        if not clean_t or any(noise in clean_t for noise in blacklist):
            processed_list.append("__EMPTY_LINE__")
        else:
            processed_list.append(clean_t)
            to_translate.append(clean_t)
            
    if not to_translate:
        return [None for _ in processed_list]

    try:
        combined = "\n\n###\n\n".join(to_translate)
        translated_all = GoogleTranslator(source='ja', target='zh-TW').translate(combined)
        translated_parts = translated_all.split("\n\n###\n\n")
    except:
        translated_parts = [GoogleTranslator(source='ja', target='zh-TW').translate(t) for t in to_translate]

    final_results = []
    ti = 0
    for item in processed_list:
        if item == "__EMPTY_LINE__":
            final_results.append(None)
        else:
            final_results.append(translated_parts[ti] if ti < len(translated_parts) else item)
            ti += 1
    return final_results

# 4. 主程式介面
st.markdown('<h1 style="text-align:center; color:#4A90E2;">🌙 小說譯閱｜純淨夜間模式</h1>', unsafe_allow_html=True)
url = st.text_input("請貼上日文小說網址：", placeholder="https://ncode.syosetu.com...")

if url:
    try:
        with st.spinner("🌙 正在嘗試繞過伺服器檢測..."):
            # 模擬真實瀏覽器的 Header 組合
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ja,zh-TW;q=0.9,zh;q=0.8',
                'Referer': 'https://ncode.syosetu.com',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive'
            }
            
            # 加入隨機延遲 1-2 秒，防止被秒封
            time.sleep(random.uniform(1, 2))
            
            # 使用 Session 保持連線狀態
            session = requests.Session()
            res = session.get(url, headers=headers, timeout=20)
            res.raise_for_status()
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'lxml')

            # 定位本文
            main_content = soup.select_one('#novel_honbun, .novel_view, .episode-content')
            if not main_content: main_content = soup

            # 標題翻譯
            raw_title = soup.title.string.split('「')[-1].split('」')[0] if soup.title else "章節內容"
            zh_title = GoogleTranslator(source='ja', target='zh-TW').translate(raw_title)

            st.markdown(f'<div class="novel-container"><h2 class="novel-title">{zh_title}</h2>', unsafe_allow_html=True)

            # 抓取段落
            paragraphs = [p.get_text() for p in main_content.find_all(['p', 'h1', 'h2'])]
            
            batch_size = 15
            for i in range(0, len(paragraphs), batch_size):
                batch = paragraphs[i:i+batch_size]
                translated_batch = batch_translate_safe(batch)
                
                for orig, tran in zip(batch, translated_batch):
                    if tran is None:
                        st.markdown('<br>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="paragraph-block">
                                <div class="zh-content">{tran}</div>
                                <div class="jp-orig">{orig}</div>
                            </div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.toast("✅ 內容抓取成功並已翻譯完成。")

    except requests.exceptions.HTTPError as e:
        if "403" in str(e):
            st.error("❌ 存取遭拒 (403)。Syosetu 暫時封鎖了連線。")
            st.info("請嘗試更換 IP (使用 VPN) 或是過幾分鐘後再重新執行。")
        else:
            st.error(f"❌ 發生錯誤：{str(e)}")
    except Exception as e:
        st.error(f"❌ 系統錯誤：{str(e)}")
