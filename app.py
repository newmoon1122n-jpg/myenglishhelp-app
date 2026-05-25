import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request

# 設定網頁配置
st.set_page_config(
    page_title="Smart Reading Buddy",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 官方輕量翻譯函數
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "Translation temporarily unavailable, please try again!"

# --- 🚀 網頁精美視覺設計 (CSS) 🚀 ---
st.markdown("""
    <style>
    /* 全局背景優化 */
    .stApp {
        background-color: #F8FAFC;
    }

    /* 🎯 終極瞒天過海法：在右下角建立一塊與背景同色的「隱形防護罩」，徹底擋住頭像和皇冠 */
    .invisible-shield {
        position: fixed;
        bottom: 0px;
        right: 0px;
        width: 150px;             /* 寬度足夠蓋住頭像和皇冠 */
        height: 70px;             /* 高度足夠完全遮擋 */
        background-color: #F8FAFC; /* 使用和網頁底色完全一樣的淺灰色 */
        z-index: 999999 !important; /* 確保圖層在最最最上層，壓死官方圖標 */
        pointer-events: auto;     /* 攔截點擊，不讓學生誤點 */
    }
    
    /* 專屬商標：固定在左上角，名稱修正為 MACAOMAMASUE */
    .author-logo {
        position: absolute;
        top: -15px;             
        left: 0px;              
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #1E4ED8 !important;   
        background-color: #EFF6FF;  
        padding: 5px 12px;
        border-radius: 8px;        
        border: 2px solid #BFDBFE;  
        font-family: sans-serif;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        z-index: 999;
    }
    
    /* 大標題設計 */
    .app-header {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2);
        margin-bottom: 25px;
        text-align: center;
        position: relative; 
    }
    .main-title { 
        font-size: 34px !important; 
        font-weight: 800 !important; 
        color: #FFFFFF !important; 
        margin: 0px !important;
        letter-spacing: 1px;
    }
    .sub-title {
        font-size: 15px !important;
        color: #E0F2FE !important;
        margin-top: 8px !important;
        opacity: 0.9;
    }
    
    /* 提示文字樣式 */
    .input-label {
        font-size: 22px !important;
        font-weight: 900 !important;
        color: #000000 !important;
        margin-bottom: 12px !important;
        display: block;
    }

    /* 置頂紅色聲明 */
    .input-disclaimer {
        font-size: 15px !important;
        color: #EF4444 !important;    
        font-weight: 700 !important;   
        font-style: italic;           
        margin-bottom: 15px !important;
        display: block;
    }

    /* 輸入框：6 像素純黑超粗邊框 */
    .stTextArea textarea {
        border: 6px solid #000000 !important;  
        border-radius: 14px !important;       
        background-color: #FFFFFF !important;  
        font-size: 20px !important;            
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* START 按鈕外觀大幅放大加粗 */
    .stButton button {
        font-size: 24px !important;           
        font-weight: 800 !important;           
        padding: 14px 28px !important;         
        border-radius: 12px !important;        
        background-color: #FF9800 !important;  
        color: #FFFFFF !important;             
        border: none !important;
        box-shadow: 0 4px 6px rgba(255, 152, 0, 0.3) !important; 
    }
    
    /* 每一句英文卡片設計 */
    .sentence-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .english-text { 
        font-size: 26px !important; 
        font-weight: 600 !important; 
        color: #0F172A !important; 
    }
    .chinese-text { 
        font-size: 20px !important; 
        font-weight: 500 !important;
        color: #475569 !important; 
        background-color: #F1F5F9;
        padding: 10px 14px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 🎨 畫面正式渲染 🎨 ---

# 🎯 渲染右下角隱形防護罩，直接把官方小圖標壓在下面
st.markdown('<div class="invisible-shield"></div>', unsafe_allow_html=True)

# 在網頁最頂端渲染左上角專屬 Logo 標籤（並修正為 MACAOCMM）
st.markdown("""
    <div class="author-logo">
        🚀 AI Crafted by MACAOCMM
    </div>
""", unsafe_allow_html=True)

# 頂部精美招牌
st.markdown("""
    <div class="app-header">
        <p class="main-title">📱Smart Reading</p>
        <p class="sub-title">Break down text • Listen sentence by sentence</p>
    </div>
""", unsafe_allow_html=True)

# 置頂紅色免責聲明
st.markdown('<span class="input-disclaimer">Powered by Google Translate. Content is for reference only and may not be perfect.</span>', unsafe_allow_html=True)

# 輸入提示標題
st.markdown('<p class="input-label">✍️ Paste your English text below:</p>', unsafe_allow_html=True)

text_input = st.text_area("", height=180, placeholder="Once upon a time, there was a smart tool that helped students learn...")

st.write("") # 留白

# 啟動按鈕
if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
    if text_input.strip():
        sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        st.success(f"🎉 Awesome! We found {len(sentences)} sentences for you.")
        
        for i, sentence in enumerate(sentences):
            full_sentence = sentence + "."
            translated = translate_text(full_sentence)
            
            st.markdown(f"""
                <div class="sentence-card">
                    <div class="english-text">{full_sentence}</div>
                    <div class="chinese-text">💡 {translated}</div>
                </div>
            """, unsafe_allow_html=True)
            
            try:
                tts = gTTS(text=full_sentence, lang='en', slow=False)
                tts.save(f"sentence_{i}.mp3")
                st.audio(f"sentence_{i}.mp3", format="audio/mp3")
            except Exception:
                st.warning("Audio generation delayed...")
