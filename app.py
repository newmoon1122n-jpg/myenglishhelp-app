import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io

# 🎯 Web Configuration
st.set_page_config(
    page_title="Smart Reading Buddy",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 官方輕量翻譯函數（用於句子與單字/片語翻譯）
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "無法取得翻譯"

# 🎯 智慧型句內生字與片語提取函數（完美支援 set off, put down 等一體化識別）
def extract_sentence_vocab(sentence_text):
    # 切分單字時保留撇號，清理其他標點
    clean_text = re.sub(r"[^\w\s']", '', sentence_text)
    words = clean_text.split()
    
    # 常見動詞片語的後半部分（小品詞/介詞庫）
    phrasal_particles = {
        'off', 'down', 'up', 'on', 'out', 'in', 'away', 'back', 'over', 'after', 'for', 'into'
    }
    
    # 基礎高頻單字過濾庫
    ignore_words = {
        'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with', 'and', 'but', 
        'or', 'so', 'because', 'if', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 
        'these', 'those', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 
        'do', 'does', 'did', 'can', 'will', 'should', 'would', 'could', 'may', 'might', 'must',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him', 'them', 'us'
    }
    
    vocab_list = []
    seen_words = set()
    
    i = 0
    while i < len(words):
        w_lower = words[i].lower()
        
        # 1. 🚫 跳過縮寫詞
        if "'" in w_lower:
            i += 1
            continue
            
        # 2. 💡 核心邏輯：動態偵測動詞片語 (例如 set off, put down, look after)
        if i + 1 < len(words):
            next_w_lower = words[i+1].lower()
            # 如果下一個字屬於常見片語介詞（如 off, down），則嘗試將它們打包成片語
            if next_w_lower in phrasal_particles and w_lower.isalpha() and next_w_lower.isalpha():
                phrasal_verb = f"{w_lower} {next_w_lower}"
                
                if phrasal_verb not in seen_words:
                    seen_words.add(phrasal_verb)
                    meaning = translate_text(phrasal_verb)
                    
                    # 確保翻譯有效，且不是單純的英文字母重複
                    if meaning.lower() != phrasal_verb:
                        vocab_list.append({"word": phrasal_verb, "meaning": meaning})
                        
                seen_words.add(w_lower)       # 標記前字已被使用，防止單獨拆出
                seen_words.add(next_w_lower)  # 標記後字已被使用，防止單獨拆出
                i += 2  # 成功打包，直接跳過這兩個字
                continue
        
        # 3. 一般單字處理流程
        if len(w_lower) < 3 or w_lower in ignore_words or not w_lower.isalpha() or w_lower in seen_words:
            i += 1
            continue
            
        seen_words.add(w_lower)
        meaning = translate_text(w_lower)
        
        if meaning.lower() != w_lower:
            vocab_list.append({"word": w_lower, "meaning": meaning})
            
        i += 1
        
    return vocab_list


# --- 🚀 網頁精美視覺設計 (CSS) 🚀 ---
st.markdown("""
   <style>
   #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
   .stAppDeployButton {display: none !important;} div[data-testid="stDecoration"] {display: none !important;}
   .stApp { background-color: #F8FAFC; }
    
   .author-logo {
       position: absolute; top: -15px; left: 0px;              
       font-size: 12px !important; font-weight: 700 !important;
       color: #1E4ED8 !important; background-color: #EFF6FF;  
       padding: 5px 12px; border-radius: 8px; border: 2px solid #BFDBFE;  
       font-family: sans-serif; letter-spacing: 0.5px; z-index: 999;
   }
    
   .app-header {
       background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
       padding: 30px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2);
       margin-bottom: 25px; text-align: center; position: relative; 
   }
   .main-title { font-size: 38px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0px !important; letter-spacing: 1px; }
   .sub-title { font-size: 16px !important; color: #E0F2FE !important; margin-top: 8px !important; opacity: 0.9; }
   .input-label { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; margin-bottom: 12px !important; display: block; }
   .input-disclaimer { font-size: 15px !important; color: #EF4444 !important; font-weight: 700 !important; font-style: italic; margin-bottom: 15px !important; display: block; }
 
   .stTextArea textarea {
       border: 6px solid #000000 !important; border-radius: 14px !important;      
       background-color: #FFFFFF !important; font-size: 20px !important; color: #000000 !important; font-weight: 500 !important;
   }
   
   .stButton button {
       font-size: 24px !important; font-weight: 800 !important; padding: 14px 28px !important; border-radius: 12px !important;       
       background-color: #FF9800 !important; color: #FFFFFF !important; border: none !important;
       box-shadow: 0 4px 6px rgba(255, 152, 0, 0.3) !important;
   }
    
   .sentence-card {
       background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6;
       box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; margin-bottom: 5px;
   }
   .card-index { font-size: 14px !important; font-weight: bold !important; color: #3B82F6 !important; text-transform: uppercase; margin-bottom: 4px; }
   .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.4 !important; margin-bottom: 12px !important; }
   .chinese-text { font-size: 20px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; margin-bottom: 5px !important; }

   .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; margin-top: 5px; margin-bottom: 25px; }
   .vocab-title { font-size: 15px; font-weight: bold; color: #D84315; margin-bottom: 6px; }
   .vocab-tag {
       display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px;
       font-size: 15px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; border: 1px solid #FFE0B2;
   }
   </style>
""", unsafe_allow_html=True)
 
# --- 🎨 畫面正式渲染 🎨 ---
st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)
 
st.markdown("""
   <div class="app-header">
       <p class="main-title">📱Smart Reading</p>
       <p class="sub-title">Break down text • Learn step by step</p>
   </div>
""", unsafe_allow_html=True)
 
st.markdown('<span class="input-disclaimer">Powered by Google Translate. Content is for reference only and may not be perfect.</span>', unsafe_allow_html=True)
st.markdown('<p class="input-label">✍️ Paste your English text below:</p>', unsafe_allow_html=True)
 
text_input = st.text_area("", height=180, placeholder="Once upon a time, they decided to set off early...")
st.write("") 
 
if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
   if text_input.strip():
       sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
       
       st.success(f"🎉 Awesome! We found {len(sentences)} sentences for you. Let's practice:")
       
       for i, sentence in enumerate(sentences):
           full_sentence = sentence + "."
           translated = translate_text(full_sentence)
           
           # 提取核心生字及一體化動詞片語
           sentence_vocabs = extract_sentence_vocab(full_sentence)
           
           # 1️⃣ 第一步：列句子卡片
           st.markdown(f"""
                <div class="sentence-card">
                    <div class="card-index">Sentence {i+1}</div>
                    <div class="english-text">{full_sentence}</div>
                    <div class="chinese-text">💡 {translated}</div>
                </div>
           """, unsafe_allow_html=True)
           
           # 2️⃣ 第二步：句子的發音條
           try:
               tts = gTTS(text=full_sentence, lang='en', slow=False)
               fp = io.BytesIO()
               tts.write_to_fp(fp)
               fp.seek(0)
               st.audio(fp, format="audio/mp3")
           except Exception:
               st.warning("Audio generation slightly delayed...")
           
           # 3️⃣ 第三步：最後呈現精確的生詞與片語清單
           if sentence_vocabs:
               vocab_html = '<div class="vocab-box"><div class="vocab-title">🔑 Vocabulary ：</div>'
               for item in sentence_vocabs:
                   vocab_html += f'<span class="vocab-tag">📌 {item["word"]}：{item["meaning"]}</span>'
               vocab_html += '</div>'
               st.markdown(vocab_html, unsafe_allow_html=True)
           else:
               st.write("")
           
   else:
       st.warning("Please enter some English sentences first!")
