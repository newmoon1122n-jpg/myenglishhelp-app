import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re

# 🎯 設定網頁配置，隱藏 Streamlit 官方選單與標籤
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
        return "Translation temporarily unavailable..."

# 🎯 核心新功能：聰明提取名詞與動詞（排除人名與常見代名詞）
def extract_nouns_and_verbs(text):
    # 預自定義一些英文中最常見、不需要背的極簡單字（代名詞、助動詞等）
    stop_words = {
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'its', 'our', 'their', 'this', 'that', 'these', 'those',
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'can', 'could', 'will', 'would', 'shall', 'should', 'may', 'might', 'must',
        'the', 'and', 'but', 'not', 'for', 'with', 'from', 'about', 'into', 'there', 'here', 'thing', 'things'
    }
    
    # 1. 找出潛在的人名（非句首的大寫單字，例如 John, Mary）
    # 先把完整的句子切開，找出那些在句子中間卻大寫的字
    proper_nouns = set(re.findall(r'\b[A-Z][a-z]+\b', text))
    # 找出句首的字（句號後面第一個大寫字），句首的大寫通常不是人名，所以不排除
    sentence_starts = set(re.findall(r'(?:^|[.!?]\s+)([A-Z][a-z]+)', text))
    # 真正要排除的人名 = 在中間大寫，且不是句首的字
    names_to_exclude = {name.lower() for name in (proper_nouns - sentence_starts)}

    # 2. 清理文章，抓出所有長度大於等於3的純英文單字
    all_words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
    
    nouns = set()
    verbs = set()
    
    # 常見字尾規律判斷（輕量級詞性分析）
    verb_suffixes = ('ing', 'ed', 'ize', 'ify', 'ate', 'es')
    noun_suffixes = ('tion', 'sion', 'ment', 'ence', 'ance', 'ity', 'ness', 'ship', 'ism', 'ist', 'logy')

    for word in all_words:
        w_lower = word.lower()
        # 排除簡單字、排除人名
        if w_lower in stop_words or w_lower in names_to_exclude:
            continue
            
        # 根據字尾做初步智慧分類
        if w_lower.endswith(verb_suffixes):
            verbs.add(w_lower)
        elif w_lower.endswith(noun_suffixes):
            nouns.add(w_lower)
        else:
            # 剩餘無法精準靠字尾判斷的單字，根據常見語法習慣暫時歸類（優先歸類為名詞供學生背誦）
            if len(w_lower) >= 4:
                nouns.add(w_lower)

    return sorted(list(nouns)), sorted(list(verbs))


# --- 🚀 網頁精美視覺設計 (CSS) 🚀 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}

    .stApp { background-color: #F8FAFC; }
    
    /* 專屬商標 */
    .author-logo {
        position: absolute; top: -15px; left: 0px;              
        font-size: 12px !important; font-weight: 700 !important;
        color: #1E4ED8 !important; background-color: #EFF6FF;  
        padding: 5px 12px; border-radius: 8px; border: 2px solid #BFDBFE;  
        font-family: sans-serif; letter-spacing: 0.5px; z-index: 999;
    }
    
    /* 大標題設計 */
    .app-header {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        padding: 30px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2);
        margin-bottom: 25px; text-align: center; position: relative; 
    }
    .main-title { font-size: 38px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0px !important;}
    .sub-title { font-size: 16px !important; color: #E0F2FE !important; margin-top: 8px !important; }
    
    /* 提示與標籤 */
    .input-label { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; display: block; }
    .input-disclaimer { font-size: 15px !important; color: #EF4444 !important; font-weight: 700 !important; font-style: italic; display: block; margin-bottom: 15px !important; }

    /* 輸入框：6 像素純黑超粗邊框 */
    .stTextArea textarea {
        border: 6px solid #000000 !important; border-radius: 14px !important;       
        background-color: #FFFFFF !important; font-size: 20px !important; color: #000000 !important; font-weight: 500 !important;
    }
    
    /* 大橘色 START 按鈕 */
    .stButton button {
        font-size: 24px !important; font-weight: 800 !important; padding: 14px 28px !important;         
        border-radius: 12px !important; background-color: #FF9800 !important; color: #FFFFFF !important; border: none !important;
    }
    
    /* 提煉單字專用的藍色副按鈕 */
    div[data-testid="stMainBlockContainer"] .vocab-btn button {
        background-color: #0EA5E9 !important; font-size: 20px !important; padding: 10px 20px !important; margin-top: 20px;
    }

    /* 英文卡片 */
    .sentence-card {
        background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; margin-bottom: 10px;
    }
    .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.4 !important; }
    .chinese-text { font-size: 20px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; }
    
    /* 詞性分類結果外觀 */
    .analysis-box {
        background-color: #FFFFFF; border: 3px solid #0EA5E9; padding: 20px; border-radius: 16px; margin-top: 20px;
    }
    .analysis-title { font-size: 22px !important; font-weight: 800 !important; color: #0284C7 !important; margin-bottom: 15px; }
    .tags-container { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; }
    .tag-noun { background-color: #E0F2FE; color: #0369A1; padding: 6px 12px; border-radius: 8px; font-weight: 600; font-size: 16px; border: 1px solid #BAE6FD; }
    .tag-verb { background-color: #DCFCE7; color: #15803D; padding: 6px 12px; border-radius: 8px; font-weight: 600; font-size: 16px; border: 1px solid #BBF7D0; }
    </style>
""", unsafe_allow_html=True)

# --- 🎨 畫面正式渲染 🎨 ---

st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="app-header">
        <p class="main-title">📱 Smart Reading</p>
        <p class="sub-title">Break down text • Listen sentence by sentence</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<span class="input-disclaimer">Powered by Google Translate. Content is for reference only and may not be perfect.</span>', unsafe_allow_html=True)
st.markdown('<p class="input-label">✍️ Paste your English text below:</p>', unsafe_allow_html=True)

text_input = st.text_area("", height=180, placeholder="Once upon a time, there was a smart tool that helped students learn...")

st.write("") 

# 啟動按鈕
if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
    if text_input.strip():
        sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        st.success(f"🎉 Awesome! We found {len(sentences)} sentences for you. Let's practice:")
        
        # 1. 正常渲染每一句的翻譯和聽力播放條
        for i, sentence in enumerate(sentences):
            full_sentence = sentence + "."
            translated = translate_text(full_sentence)
            
            st.markdown(f"""
                <div class="sentence-card">
                    <div class="card-index">Sentence {i+1}</div>
                    <div class="english-text">{full_sentence}</div>
                    <div class="chinese-text">💡 {translated}</div>
                </div>
            """, unsafe_allow_html=True)
            
            try:
                tts = gTTS(text=full_sentence, lang='en', slow=False)
                tts.save(f"sentence_{i}.mp3")
                st.audio(f"sentence_{i}.mp3", format="audio/mp3")
            except Exception:
                st.warning("Audio generation slightly delayed...")
        
        st.write("---") # 分隔線
        
        # 2. 🎯 學生看完聽完後，最下方的「智慧提煉按鈕」
        st.markdown("### 🔍 Vocabulary Deep Dive (課文詞彙深挖)")
        st.write("聽讀完成後，點擊下方按鈕，一鍵提煉文章中的核心名詞與動詞，方便背誦！")
        
        # 這裡做一個獨立的展開功能（按下去才顯示效果）
        with st.expander("✨ Click to Extract Nouns & Verbs (一鍵提煉名詞與動詞)", expanded=False):
            nouns, verbs = extract_nouns_and_verbs(text_input)
            
            st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
            
            # 渲染名詞結果
            st.markdown('<div class="analysis-title">📝 Core Nouns (文章中的核心名詞)</div>', unsafe_allow_html=True)
            if nouns:
                st.markdown('<div class="tags-container">', unsafe_allow_html=True)
                for noun in nouns:
                    trans_n = translate_text(noun)
                    st.markdown(f'<span class="tag-noun">🔷 {noun} ({trans_n})</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("No major nouns found.")
                
            st.write("") # 留空
            
            # 渲染動詞結果
            st.markdown('<div class="analysis-title">🎬 Action Verbs (文章中的行為動詞)</div>', unsafe_allow_html=True)
            if verbs:
                st.markdown('<div class="tags-container">', unsafe_allow_html=True)
                for verb in verbs:
                    trans_v = translate_text(verb)
                    st.markdown(f'<span class="tag-verb">🟢 {verb} ({trans_v})</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("No major verbs found.")
                
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        st.warning("Please enter some English sentences first!")
