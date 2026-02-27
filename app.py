import streamlit as st
from deep_translator import GoogleTranslator
import time

# 1. 頁面配置：維持夜間純淨模式
st.set_page_config(page_title="小說譯閱 Pro - 專業翻譯", page_icon="📖", layout="centered")

# 2. 專業小說排版 CSS (夜間沉浸式)
st.markdown("""
    <style>
    /* 全域背景：低藍光深煤灰 */
    .stApp { background-color: #0F0F0F; color: #E0E0E0; } 
    
    /* 閱讀容器：深灰浮雕質感 */
    .novel-container {
        max-width: 850px;
        margin: 30px auto;
        padding: 50px 40px;
        background-color: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 16px;
        box-shadow: 0 15px 45px rgba(0,0,0,0.7);
    }

    /* 標題與裝飾 */
    .novel-header {
        text-align: center;
        border-bottom: 2px solid #2D2D2D;
        padding-bottom: 30px;
        margin-bottom: 45px;
    }
    .novel-header h2 { color: #FFFFFF; font-family: "Noto Serif TC", serif; font-size: 2.2rem; }

    /* 段落排版 */
    .paragraph-block { margin-bottom: 35px; line-height: 2.1; }

    /* 中文本文：柔和白、加大縮排 */
    .zh-content {
        font-size: 1.3rem;
        color: #D6D6D6;
        text-indent: 2.5em; /* 專業小說首行縮排 */
        font-family: "Microsoft JhengHei", "PingFang TC", sans-serif;
        text-align: justify; /* 兩端對齊 */
    }

    /* 日文原文：低干擾幽靈灰 */
    .jp-orig {
        display: block;
        font-size: 0.95rem;
        color: #606060;
        margin-top: 10px;
        text-indent: 0;
        font-style: italic;
        border-left: 3px solid #4A90E2; /* 導引線 */
        padding-left: 15px;
    }

    /* 輸入區塊美化 */
    .stTextArea textarea {
        background-color: #262626 !important;
        color: #FFFFFF !important;
        border: 1px solid #444 !important;
        font-size: 1rem;
    }
    
    /* 隱藏預設元件 */
    #MainMenu, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. 翻譯核心邏輯：處理空白、剔除贅詞、批次潤飾
def translate_and_polish(raw_text):
    if not raw_text.strip(): return []
    
    # 按照換行符分割段落
    lines = raw_text.split('\n')
    
    processed_list = []
    to_translate = []
    
    # 預處理：識別空白行與內容
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            processed_list.append("__EMPTY_LINE__")
        else:
            processed_list.append(clean_line)
            to_translate.append(clean_line)
            
    if not to_translate: return []

    # 執行翻譯 (模擬專業潤飾：繁體中文)
    try:
        # 使用批次翻譯減少請求次數，並確保語句連貫
        combined = "\n\n[SEP]\n\n".join(to_translate)
        translated_all = GoogleTranslator(source='ja', target='zh-TW').translate(combined)
        translated_parts = translated_all.split("\n\n[SEP]\n\n")
    except Exception as e:
        # 備援：逐行翻譯
        translated_parts = [GoogleTranslator(source='ja', target='zh-TW').translate(t) for t in to_translate]

    # 合併回最終清單
    final_results = []
    ti = 0
    for item in processed_list:
        if item == "__EMPTY_LINE__":
            final_results.append(None)
        else:
            # 填入翻譯結果，若翻譯索引超出則填入原文
            final_results.append(translated_parts[ti] if ti < len(translated_parts) else item)
            ti += 1
    return list(zip(processed_list, final_results))

# 4. 主程式介面
st.markdown('<h1 style="text-align:center; color:#4A90E2; font-weight:300;">🌙 小說譯閱｜手動翻譯模式</h1>', unsafe_allow_html=True)

# 使用 TextArea 讓使用者貼上大量文字
input_text = st.text_area("請貼上日文小說文字：", height=250, placeholder="將日文內容複製並貼到此處...")

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    start_btn = st.button("✨ 開始專業翻譯與排版", use_container_width=True)

if start_btn and input_text:
    try:
        with st.spinner("🌙 正在進行專業級繁體中文潤飾..."):
            results = translate_and_polish(input_text)
            
            st.markdown('<div class="novel-container">', unsafe_allow_html=True)
            st.markdown('<div class="novel-header"><h2>章節內容</h2></div>', unsafe_allow_html=True)
            
            for orig, tran in results:
                # 邏輯：空白處維持空白 (不顯示文字或符號)
                if tran is None or orig == "__EMPTY_LINE__":
                    st.markdown('<br>', unsafe_allow_html=True)
                else:
                    # 專業排版：上方中文潤飾，下方日文原稿
                    st.markdown(f"""
                        <div class="paragraph-block">
                            <div class="zh-content">{tran}</div>
                            <div class="jp-orig">{orig}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.success("✅ 翻譯完成！")
            st.toast("已套用專業小說排版樣式")

    except Exception as e:
        st.error(f"❌ 翻譯過程發生錯誤：{str(e)}")
elif start_btn and not input_text:
    st.warning("⚠️ 請先貼上一些文字再開始翻譯。")

