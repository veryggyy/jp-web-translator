import streamlit as st
from deep_translator import GoogleTranslator
import pandas as pd

# 1. 頁面配置
st.set_page_config(page_title="小說譯閱 Pro - 專業自定義", page_icon="📖", layout="centered")

# 2. 側邊欄控制面板
with st.sidebar:
    st.header("🎨 閱讀偏好設定")
    font_size = st.slider("字體大小 (px)", min_value=14, max_value=32, value=20)
    line_height = st.slider("行間距 (倍數)", min_value=1.5, max_value=3.5, value=2.1, step=0.1)
    st.divider()
    st.info("調整後，下方閱讀區會即時更新排版。")

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

    .novel-header {{
        text-align: center;
        border-bottom: 2px solid #2D2D2D;
        padding-bottom: 30px;
        margin-bottom: 45px;
    }}
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

    .stTextArea textarea {{
        background-color: #262626 !important;
        color: #FFFFFF !important;
        border: 1px solid #444 !important;
    }}
    
    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# 4. 翻譯與格式處理邏輯
def translate_and_polish(raw_text):
    if not raw_text.strip(): return []
    lines = raw_text.split('\n')
    processed_list = []
    to_translate = []
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            processed_list.append("__EMPTY_LINE__")
        else:
            processed_list.append(clean_line)
            to_translate.append(clean_line)
            
    if not to_translate: return []

    try:
        combined = "\n\n[SEP]\n\n".join(to_translate)
        translated_all = GoogleTranslator(source='ja', target='zh-TW').translate(combined)
        translated_parts = translated_all.split("\n\n[SEP]\n\n")
    except:
        translated_parts = [GoogleTranslator(source='ja', target='zh-TW').translate(t) for t in to_translate]

    final_results = []
    ti = 0
    full_translated_text = "" # 用於一鍵複製
    
    for item in processed_list:
        if item == "__EMPTY_LINE__":
            final_results.append((None, None))
            full_translated_text += "\n" # 保持空行
        else:
            tran = translated_parts[ti] if ti < len(translated_parts) else item
            final_results.append((item, tran))
            full_translated_text += f"{tran}\n"
            ti += 1
            
    return final_results, full_translated_text

# 5. 主程式介面
st.markdown('<h1 style="text-align:center; color:#4A90E2; font-weight:300;">🌙 小說譯閱｜自定義夜間模式</h1>', unsafe_allow_html=True)

input_text = st.text_area("請貼上日文小說文字：", height=200, placeholder="將內容複製並貼到此處...")

if st.button("✨ 開始專業翻譯與排版", use_container_width=True):
    if input_text:
        with st.spinner("🌙 正在進行專業級繁體中文潤飾..."):
            results, full_zh = translate_and_polish(input_text)
            
            # --- 複製功能區塊 ---
            st.divider()
            st.subheader("📋 翻譯結果操作")
            st.text_area("繁體中文翻譯稿 (可直接複製)", value=full_zh, height=150, help="此區塊已保留所有原始段落格式")
            st.download_button(label="📥 下載為 .txt 檔案", data=full_zh, file_name="小說翻譯稿.txt", mime="text/plain")
            
            # --- 閱讀呈現區塊 ---
            st.markdown('<div class="novel-container">', unsafe_allow_html=True)
            st.markdown('<div class="novel-header"><h2>章節內容</h2></div>', unsafe_allow_html=True)
            
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
            st.toast("✅ 翻譯與排版已根據設定完成更新！")
    else:
        st.warning("⚠️ 請先貼上文字再開始。")
