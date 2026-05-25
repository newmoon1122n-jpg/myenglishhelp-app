import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request

# Official lightweight translation function
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
    /* 全局背景與字體優化 */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 大標題設計：漸層色彩、陰影與生動圖示 */
    .app-header {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2);
        margin-bottom: 30px;
        text-align: center;
    }
    .main-title { 
        font-size: 38px !important; 
        font-weight: 800 !important; 
        color: #FFFFFF !important; 
        margin: 0px !important;
        letter-spacing: 1px;
    }
    .sub-title {
        font-size: 16px !important;
        color: #E0F2FE !important;
        margin-top: 8px !important;
        opacity: 0.9;
    }
    
    /* 提示文字樣式：字體再加粗 */
    .input-label {
        font-size: 22px !important;
        font-weight: 900 !important;
        color: #000000 !important;
        margin-bottom: 12px;
    }

    /* 🎯 輸入框：6 像素純黑超粗邊框 */
    .stTextArea textarea {
        border: 6px solid #000000 !important;  
        border-radius: 14px !important;       
        background-color: #FFFFFF !important;  
        font-size: 20px !important;            
        color: #000000 !important;
        font-weight: 500 !important;
    }
    .stTextArea textarea:focus {
        border-color: #1D4ED8 !important;     
        box-shadow: 0 0 0 4px rgba(29, 78, 216, 0.4) !important;
    }
    
    /* 🎯 核心修改：把 START 按鈕的字體和外觀大幅放大加粗 */
    .stButton button {
        font-size: 50px !important;           /* 字體加大到 50px */
        font-weight: 800 !important;           /* 字體超級加粗 */
        padding: 14px 28px !important;         /* 增加按鈕內襯，讓按鈕變大顆 */
        border-radius: 12px !important;        /* 圓角設計 */
        background-color: #FF9800 !important;  /* 改成活力亮橘色，更吸引學生 */
        color: #FFFFFF !important;             /* 白色文字 */
        border: none !important;
        box-shadow: 0 4px 6px rgba(255, 152, 0, 0.3) !important; /* 橘色發光陰影 */
        transition: all 0.2s ease;
    }
    
    /* 滑鼠移到按鈕上時的特殊動態效果 */
    .stButton button:hover {
        background-color: #F57C00 !important;  /* 顏色變深一點點 */
        transform: translateY(-2px) !important; /* 微微向上浮起 */
        box-shadow: 0 6px 12px rgba(255, 152, 0, 0.4) !important;
    }
    
    /* 每一句英文卡片的精美設計 */
    .sentence-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-top: 20px;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .sentence-card:hover {
        transform: translateY(-2px);
    }
    
    /* 卡片內文字樣式 */
    .card-index {
        font-size: 14px !important;
        font-weight: bold !important;
        color: #3B82F6 !important;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .english-text { 
        font-size: 26px !important; 
        font-weight: 600 !important; 
        color: #0F172A !important; 
        line-height: 1.4 !important;
        margin-bottom: 12px !important; 
    }
    .chinese-text { 
        font-size: 20px !important; 
        font-weight: 500 !important;
        color: #475569 !important; 
        background-color: #F1F5F9;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 15px !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- 🎨 畫面正式渲染 🎨 ---

# 頂部精美招牌
st.markdown("""
    <div class="app-header">
        <p class="main-title">📱 Smart Reading Buddy</p>
        <p class="sub-title">🤖 Break down text • Listen sentence by sentence • Master English easily!</p>
    </div>
""", unsafe_allow_html=True)

# 輸入區引導
st.markdown('<p class="input-label">✍️ Paste your English text below:</p>', unsafe_allow_html=True)
text_input = st.text_area("", height=180, placeholder="Once upon a time, there was a smart tool that helped students learn...")

st.write("") # 留白

# 啟動按鈕
if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
    if text_input.strip():
        # 按句號、問號、感嘆號拆分句子
        sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        
        st.success(f"🎉 Awesome! We found {len(sentences)} sentences for you. Let's practice:")
        
        for i, sentence in enumerate(sentences):
            full_sentence = sentence + "."
            # 翻譯
            translated = translate_text(full_sentence)
            
            # 用精美的卡片包裹英文與中文
            st.markdown(f"""
                <div class="sentence-card">
                    <div class="card-index">Sentence {i+1}</div>
                    <div class="english-text">{full_sentence}</div>
                    <div class="chinese-text">💡 {translated}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # 語音播放條緊跟在卡片下方
            try:
                tts = gTTS(text=full_sentence, lang='en', slow=False)
                tts.save(f"sentence_{i}.mp3")
                st.audio(f"sentence_{i}.mp3", format="audio/mp3")
            except Exception:
                st.warning("Audio generation slightly delayed...")
            
    else:
        st.warning("Please enter some English sentences first!")
