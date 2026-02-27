import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import time

# 1. 頁面配置
st.set_page_config(page_title="小說譯閱 Pro - 夜間純淨版", page_icon="🌙", layout="centered")

# 2. 夜間模式 CSS
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

# 3. 優化後的翻譯引擎：支援批次處理且保留空白
def batch_translate_safe(text_list):
    if not text_list: return []
    
    # 過濾贅詞
    blacklist = ['下一頁', '下一一個', '前一頁', '次へ', '前へ', '目次', '加入書籤', '發生錯誤']
    
    # 預處理：標記空白處，合併有效文字
    processed_list = []
    to_translate = []
    
    for t in text_list:
        clean_t = t.strip()
        # 如果是空白或是黑名單字眼，標記為特殊符號跳過翻譯
        if not clean_t or any(noise in clean_t for noise in blacklist):
            processed_list.append("__EMPTY_LINE__")
        else:
            processed_list.append(clean_t)
            to_translate.append(clean_t)
            
    if not to_translate:
        return [" " for _ in processed_list]

    # 批次翻譯有效文字 (使用分隔符號減少請求次數)
    try:
        combined = "\n\n###\n\n".join(to_translate)
        translated_all = GoogleTranslator(source='ja', target='zh-TW').translate(combined)
        translated_parts = translated_all.split("\n\n###\n\n")
    except:
        # 備援：若批次失敗則單筆翻譯
        translated_parts = [GoogleTranslator(source='ja', target='zh-TW').translate(t) for t in to_translate]

    # 將翻譯好的文字填回對應位置，空白處維持空白
    final_results = []
    ti = 0
    for item in processed_list:
        if item == "__EMPTY_LINE__":
            final_results.append(None) # None 代表空白
        else:
            final_results.append(translated_parts[ti] if ti < len(translated_parts) else item)
            ti += 1
    return final_results

# 4. 主程式介面
st.markdown('<h1 style="text-align:center; color:#4A90E2;">🌙 小說譯閱｜純淨夜間模式</h1>', unsafe_allow_html=True)
url = st.text_input("請輸入日文小說網址：", placeholder="https://ncode.syosetu.com...")

if url:
    try:
        with st.spinner("🌙 正在繞過偵測並解析內容..."):
            # 強化 Header 偽裝成真實用戶
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
            }
            res = requests.get(url, headers=headers, timeout=20)
            res.raise_for_status() # 如果 403 或 404 會報錯
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'lxml')

            # 定位小說主體
            main_content = soup.select_one('#novel_honbun, .novel_view, .episode-content, #story')
            if not main_content:
                st.warning("⚠️ 找不到標準小說區塊，嘗試解析全文。")
                main_content = soup

            # 章節標題
            raw_title = soup.title.string.replace(' - 小説家になろう', '').strip() if soup.title else "章節內容"
            zh_title = GoogleTranslator(source='ja', target='zh-TW').translate(raw_title)

            st.markdown(f'<div class="novel-container"><h2 class="novel-title">{zh_title}</h2>', unsafe_allow_html=True)

            # 獲取所有段落
            raw_paragraphs = [p.get_text() for p in main_content.find_all(['p', 'h1', 'h2'])]
            
            # 分批處理（每 15 段一組），平衡速度與成功率
            batch_size = 15
            for i in range(0, len(raw_paragraphs), batch_size):
                batch = raw_paragraphs[i:i+batch_size]
                translated_batch = batch_translate_safe(batch)
                
                for orig, tran in zip(batch, translated_batch):
                    if tran is None: # 空白處
                        st.markdown('<br>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="paragraph-block">
                                <div class="zh-content">{tran}</div>
                                <div class="jp-orig">{orig}</div>
                            </div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.toast("✅ 翻譯已安全完成。")

    except Exception as e:
        st.error(f"❌ 解析失敗。原因：{str(e)}")
        st.info("提示：如果出現 403 錯誤，代表該網站暫時封鎖了您的連線，請過幾分鐘再試。")
