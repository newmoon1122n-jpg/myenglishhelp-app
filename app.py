import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re

# 🎯 網頁基本配置
st.set_page_config(
    page_title="Smart Reading Buddy - Bridge to Form 1",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 輕量翻譯函數
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "Translation temporarily unavailable..."

# 🎯 簡單的高頻/學科核心詞彙庫（幫助小六生快速抓出重要單字）
def extract_key_vocab(text):
    # 清理標點符號，轉小寫
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower()) # 挑出5個字母以上的單字
    # 排除常見極簡單字
    stop_words = {'about', 'their', 'there', 'would', 'could', 'should', 'which', 'where', 'these', 'those'}
    unique_words = list(set(words) - stop_words)[:6] # 每次最多挑6個
    return unique_words

# --- 🚀 網頁美化視覺設計 (CSS) 🚀 ---
st.markdown("""
    <style>
    /* 隱藏官方冗餘元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}

    .stApp { background-color: #F8FAFC; }
    
    /* 左上角專屬商標 */
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
        z-index: 999;
    }
    
    /* 大標題 */
    .app-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2);
        margin-bottom: 25px;
        text-align: center;
    }
    .main-title { font-size: 34px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0px !important;}
    .sub-title { font-size: 15px !important; color: #E0F2FE !important; margin-top: 8px !important; }
    
    /* 標籤與提示 */
    .input-label { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; margin-bottom: 12px !important; }
    .input-disclaimer { font-size: 14px !important; color: #EF4444 !important; font-weight: 700 !important; font-style: italic; display: block; margin-bottom: 15px; }

    /* 輸入框：6像素純黑超粗邊框 */
    .stTextArea textarea {
        border: 6px solid #000000 !important;  
        border-radius: 14px !important;       
        background-color: #FFFFFF !important;  
        font-size: 20px !important;            
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* 按鈕樣式 */
    .stButton button {
        font-size: 22px !important; font-weight: 800 !important; padding: 12px 24px !important;
        border-radius: 12px !important; background-color: #FF9800 !important; color: #FFFFFF !important; border: none !important;
    }
    
    /* 句子卡片 */
    .sentence-card {
        background-color: #FFFFFF; padding: 20px; border-radius: 16px; border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 15px; margin-bottom: 5px;
    }
    .english-text { font-size: 24px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.5; }
    .chinese-text { font-size: 19px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 8px 12px; border-radius: 8px; margin-top: 8px; }
    
    /* 單字卡特製樣式 */
    .vocab-box {
        background-color: #FFFBEB; border: 2px dashed #F59E0B; padding: 15px; border-radius: 12px; margin-top: 20px;
    }
    .vocab-title { font-size: 18px !important; font-weight: 800 !important; color: #B45309 !important; margin-bottom: 8px; }
    .vocab-item { font-size: 16px !important; font-weight: 600 !important; color: #1E293B !important; }
    </style>
""", unsafe_allow_html=True)

# --- 🎨 畫面渲染 🎨 ---

st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOMAMASUE</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="app-header">
        <p class="main-title">📱 Smart Reading Buddy</p>
        <p class="sub-title">✏️ 中小銜接特訓版：聽力、詞彙、句子逐一擊破，輕鬆適應英文中學！</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<span class="input-disclaimer">⚠️ Powered by Google Translate. Content is for reference only.</span>', unsafe_allow_html=True)

# 🚀 貼心功能一：讓學生自行調配適合英文中學的語速
st.markdown("##### 🎧 聽力適應特訓 (Audio Speed)")
speed_option = st.radio(
    "明天升初一，建議先從「慢速」聽清發音，再挑戰「正常」語速適應全英授課：",
    ("🐢 慢速特訓 (Slow for practice)", "⚡ 正常語速 (Normal for English School)"),
    horizontal=True
)
is_slow = True if "🐢" in speed_option else False

st.write("")

st.markdown('<p class="input-label">✍️ Paste your English textbook text below:</p>', unsafe_allow_html=True)
text_input = st.text_area("", height=180, placeholder="Paste a paragraph from your Mathematics, Science, or English textbook here...")

st.write("")

if st.button("🚀 Start English School Training!", use_container_width=True):
    if text_input.strip():
        # 拆分句子
        sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        
        # 🚀 貼心功能二：自動抓出核心單字卡，幫學生擴充詞彙量
        key_words = extract_key_vocab(text_input)
        if key_words:
            st.markdown('<div class="vocab-box">', unsafe_allow_html=True)
            st.markdown('<div class="vocab-title">🔑 F.1 Textbook Core Vocabulary (課文核心詞彙解碼)</div>', unsafe_allow_html=True)
            for word in key_words:
                meaning = translate_text(word)
                st.markdown(f'<div class="vocab-item">📌 <b>{word}</b> : {meaning}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        st.subheader(f"📖 Sentence-by-Sentence Breakdown ({len(sentences)} sentences)")
        
        for i, sentence in enumerate(sentences):
            full_sentence = sentence + "."
            translated = translate_text(full_sentence)
            
            # 渲染精美句子卡
            st.markdown(f"""
                <div class="sentence-card">
                    <div style="font-size:12px; color:#3B82F6; font-weight:bold;">第 {i+1} 句</div>
                    <div class="english-text">{full_sentence}</div>
                    <div class="chinese-text">💡 中文翻譯：{translated}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # 播放音檔 (套用學生選擇的語速)
            try:
                tts = gTTS(text=full_sentence, lang='en', slow=is_slow)
                tts.save(f"sent_{i}.mp3")
                st.audio(f"sent_{i}.mp3", format="audio/mp3")
            except Exception:
                st.text("Audio loading...")
    else:
        st.warning("Please paste some text first!")
