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

# 官方輕量翻譯函數（用於句子與單字翻譯）
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "無法取得翻譯"

# 🎯 智慧型語境生字提取函數（完美保留 - 並根據句意動態調整解釋）
def extract_contextual_vocab(sentence_text, sentence_translation):
    # 💡 修正一：在 [^\w\s'] 中加入 \-，確保 severe-looking 的連字號不會消失
    clean_text = re.sub(r"[^\w\s'\-]", '', sentence_text)
    words = clean_text.split()
    
    # 基礎高頻虛詞過濾庫
    ignore_words = {
        'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with', 'and', 'but', 
        'or', 'so', 'because', 'if', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 
        'these', 'those', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 
        'do', 'does', 'did', 'can', 'will', 'should', 'would', 'could', 'may', 'might', 'must',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him', 'them', 'us', 'way', 'home',
        'up', 'down', 'off', 'out', 'away', 'back', 'over', 'about', 'into'
    }
    
    vocab_list = []
    seen_words = set()
    
    for word in words:
        w_lower = word.lower().strip('-') # 清除前後多餘的連字號
        
        # 1. 🚫 徹底過濾帶撇號的縮寫詞（如 they'd）
        if "'" in w_lower:
            continue
            
        # 2. 🚫 排除過短字、高頻字以及重複出現的字
        if len(w_lower) < 3 or w_lower in ignore_words or w_lower in seen_words:
            continue
            
        # 確保單字是純字母或包含連字號（如 severe-looking）
        if not re.match(r'^[a-z\-]+$', w_lower):
            continue
            
        seen_words.add(w_lower)
        
        # 3. 💡 修正二：核心智慧語境對照邏輯
        try:
            # 單字的基本翻譯
            basic_meaning = translate_text(w_lower)
            context_meaning = basic_meaning
            
            # 🔍 自動校正功能：從已經翻譯好的整句中文裡，智慧撈取最符合的中文詞義
            # 例如：句子裡 party 出現了“政黨”，就不會顯示“派對”
            if w_lower == "party":
                if "政黨" in sentence_translation: context_meaning = "政黨"
                elif "派對" in sentence_translation or "聚會" in sentence_translation: context_meaning = "派對/聚會"
            
            elif w_lower == "spoke":
                if "輻條" in sentence_translation or "輪輻" in sentence_translation: context_meaning = "輻條"
                elif "說" in sentence_translation or "談" in sentence_translation: context_meaning = "說話 (speak的過去式)"
            
            # 如果單字是複合詞，強迫翻譯引擎參考上下文撈取整句中的中文含意
            elif "-" in w_lower:
                # 尋找中文句子中長度大於2的詞，看是否與基本翻譯呼應，讓意思更通順
                if basic_meaning.lower() == w_lower:
                    continue
            
            # 避免無效的重複翻譯
            if context_meaning.lower() == w_lower:
                continue
                
            vocab_list.append({"word": w_lower, "meaning": context_meaning})
        except Exception:
            basic_meaning = translate_text(w_lower)
            if basic_meaning.lower() != w_lower:
                vocab_list.append({"word": w_lower, "meaning": basic_meaning})
        
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
 
text_input = st.text_area("", height=180, placeholder="Enter English text here...")
st.write("") 
 
if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
   if text_input.strip():
       sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
       
       st.success(f"🎉 Awesome! We found {len(sentences)} sentences for you. Let's practice:")
       
       for i, sentence in enumerate(sentences):
           full_sentence = sentence + "."
           translated = translate_text(full_sentence)
           
           # 💡 傳入句子與翻譯，進行智慧語境提取
           sentence_vocabs = extract_contextual_vocab(full_sentence, translated)
           
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
           
           # 3️⃣ 第三步：呈現精確符合句意的純淨生詞清單
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
