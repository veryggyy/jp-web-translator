import streamlit as st
from deep_translator import GoogleTranslator
import pandas as pd
import re
import concurrent.futures

# 1. 頁面配置
st.set_page_config(page_title="小說譯閱 Pro - 高速版", page_icon="⚡", layout="centered")

# 2. 側邊欄控制面板
with st.sidebar:
    st.header("🎨 閱讀偏好設定")
    font_size = st.slider("字體大小 (px)", min_value=14, max_value=32, value=20)
    line_height = st.slider("行間距 (倍數)", min_value=1.5, max_value=3.5, value=2.1, step=0.1)
    st.divider()
    st.info("⚡ 已啟用多執行緒並行翻譯加速。")

# 3. 動態 CSS 注入
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F0F0F; color: #E0E0E0; }} 
    .novel-container {{
        max-width: 850px;
        margin: 30px auto;
        padding: 50px 40px;
        background-color: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 16px;
        box-shadow: 0 15px 45px rgba(0,0,0,0.7);
    }}
    .novel-header {{ text-align: center; border-bottom: 2px solid #2D2D2D; padding-bottom: 30px; margin-bottom: 45px; }}
    .novel-header h2 {{ color: #FFFFFF; font-family: "Noto Serif TC", serif; font-size: 2.2rem; }}
    .paragraph-block {{ margin-bottom: 35px; line-height: {line_height}; }}
    .zh-content {{
        font-size: {font_size}px;
        color: #D6D6D6;
        text-indent: 2em;
        font-family: "Microsoft JhengHei", "PingFang TC", sans-serif;
        text-align: justify;
    }}
    .jp-orig {{
        display: block;
        font-size: 0.85rem;
        color: #606060;
        margin-top: 10px;
        text-indent: 0;
        font-style: italic;
        border-left: 3px solid #4A90E2;
        padding-left: 15px;
    }}
    .stTextArea textarea {{ background-color: #262626 !important; color: #FFFFFF !important; border: 1px solid #444 !important; }}
    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# 4. 核心邏輯：加速翻譯與自動命名
def fetch_translation(text):
    """單條翻譯執行器"""
    if not text.strip(): return ""
    try:
        # 使用 GoogleTranslator 進行翻譯
        return GoogleTranslator(source='ja', target='zh-TW').translate(text)
    except Exception:
        return text

def translate_and_polish(raw_text):
    if not raw_text.strip(): return [], "", "空內容"
    
    lines = raw_text.split('\n')
    # 建立任務索引，僅處理有文字內容的行
    task_map = {i: line.strip() for i, line in enumerate(lines) if line.strip()}
    
    translated_dict = {}
    # 使用 ThreadPoolExecutor 同時發送請求（建議 max_workers 設為 10-15 避免被封鎖）
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_idx = {executor.submit(fetch_translation, text): idx for idx, text in task_map.items()}
        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            translated_dict[idx] = future.result()

    final_results = []
    full_translated_text = ""
    first_valid_line = ""
    
    for i, line in enumerate(lines):
        if not line.strip():
            final_results.append((None, None))
            full_translated_text += "\n"
        else:
            tran = translated_dict.get(i, line)
            # 檔名處理：取第一句翻譯，移除特殊字元
            if not first_valid_line and tran:
                first_valid_line = re.sub(r'[\\/*?:"<>|]', '', tran).strip()[:15]
            final_results.append((line, tran))
            full_translated_text += f"{tran}\n"
            
    return final_results, full_translated_text, first_valid_line

# 5. 主程式介面
st.markdown('<h1 style="text-align:center; color:#4A90E2; font-weight:300;">⚡ 小說譯閱｜並行加速版</h1>', unsafe_allow_html=True)

input_text = st.text_area("請貼上日文小說文字：", height=200, placeholder="貼上後點擊下方按鈕，系統將自動啟動並行翻譯...")

if st.button("🚀 啟動高速翻譯與專業排版", use_container_width=True):
    if input_text:
        with st.spinner("⚡ 多執行緒翻譯中，請稍候..."):
            results, full_zh, file_title = translate_and_polish(input_text)
            
            # --- 複製與下載區塊 ---
            st.divider()
            final_filename = f"{file_title}.txt" if file_title else "小說翻譯稿.txt"
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"📄 當前翻譯：{final_filename}")
            with col2:
                st.download_button(label="📥 下載檔案", data=full_zh, file_name=final_filename, mime="text/plain")
            
            st.text_area("繁體中文翻譯稿 (Ctrl+A 全選複製)", value=full_zh, height=150)
            
            # --- 閱讀呈現區塊 ---
            st.markdown('<div class="novel-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="novel-header"><h2>{file_title}</h2></div>', unsafe_allow_html=True)
            
            for orig, tran in results:
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
            st.toast(f"✅ 翻譯完成！檔案已命名為：{final_filename}")
    else:
        st.warning("⚠️ 請先貼上日文內容。")
