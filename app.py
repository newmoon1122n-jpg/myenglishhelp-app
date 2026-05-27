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

# 🚀 輕量高效翻譯核心
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "無法取得翻譯"

# 🎯 高速語境生字提取函數
def extract_fast_contextual_vocab(sentence_text, sentence_translation):
    clean_text = re.sub(r"[^\w\s'\-]", ' ', sentence_text)
    words = clean_text.split()
    
    ignore_words = {
        'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with', 'and', 'but', 
        'or', 'so', 'because', 'if', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 
        'these', 'those', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 
        'do', 'does', 'did', 'can', 'will', 'should', 'would', 'could', 'may', 'might', 'must',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him', 'them', 'us'
    }
    
    vocab_list = []
    seen_words = set()
    
    for word in words:
        w_lower = word.lower().strip('-')
        if "'" in w_lower or len(w_lower) < 3 or w_lower in ignore_words or w_lower in seen_words:
            continue
        if not re.match(r'^[a-z\-]+$', w_lower):
            continue
            
        seen_words.add(w_lower)
        
        try:
            raw_meaning = translate_text(w_lower)
            if '(' in raw_meaning:
                context_meaning = raw_meaning.split('(')[0].strip()
            else:
                context_meaning = raw_meaning.strip()
            
            if w_lower == "party":
                if "政黨" in sentence_translation: context_meaning = "政黨"
                elif "派對" in sentence_translation or "聚會" in sentence_translation: context_meaning = "派對/聚會"
            elif w_lower == "spoke":
                if "輻條" in sentence_translation or "輪輻" in sentence_translation: context_meaning = "輻條"
                elif "說" in sentence_translation or "談" in sentence_translation: context_meaning = "說話 (speak的過去式)"
            
            if context_meaning.lower() == w_lower or not context_meaning:
                continue
                
            vocab_list.append({"word": w_lower, "meaning": context_meaning})
        except Exception:
            continue
        
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
       z-index: 999;
   }
   .app-header {
       background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
       padding: 30px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2);
       margin-bottom: 25px; text-align: center;
   }
   .main-title { font-size: 38px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0px !important; }
   .sub-title { font-size: 16px !important; color: #E0F2FE !important; margin-top: 8px !important; }
   .input-label { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; margin-bottom: 12px !important; display: block; }
   .input-disclaimer { font-size: 15px !important; color: #EF4444 !important; font-weight: 700 !important; margin-bottom: 15px !important; display: block; }
   .stTextArea textarea { border: 6px solid #000000 !important; border-radius: 14px !important; font-size: 20px !important; }
   .stButton button { font-size: 24px !important; font-weight: 800 !important; padding: 14px 28px !important; background-color: #FF9800 !important; color: #FFFFFF !important; }
   .sentence-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; }
   .card-index { font-size: 14px !important; font-weight: bold !important; color: #3B82F6 !important; text-transform: uppercase; }
   .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; }
   .chinese-text { font-size: 20px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; }
   .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; }
   .vocab-tag { display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px; font-size: 15px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; }
   .stExpander { border: none !important; box-shadow: none !important; margin-bottom: 10px !important; }
   .quiz-box { background-color: #F0Fdf4; border: 1px dashed #4ADE80; border-radius: 10px; padding: 16px; }
   .quiz-prompt { font-size: 18px !important; font-weight: bold !important; color: #166534 !important; margin-bottom: 10px; }
   </style>
""", unsafe_allow_html=True)
 
st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)
st.markdown("""
   <div class="app-header">
       <p class="main-title">📱 Smart Reading</p>
       <p class="sub-title">Break down text • Learn step by step</p>
   </div>
""", unsafe_allow_html=True)
st.markdown('<span class="input-disclaimer">Powered by Google Translate. Content is for reference only.</span>', unsafe_allow_html=True)
st.markdown('<p class="input-label">✍️ Paste your English text below:</p>', unsafe_allow_html=True)
 
text_input = st.text_area("", height=180, placeholder="Enter English text here...")
st.write("") 

# 🧠 核心記憶機制：初始化記憶庫
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None

# 當使用者按下分析按鈕，開始處理並存入大腦
if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
   if text_input.strip():
       clean_input = re.sub(r'^\d+\s+', '', text_input.strip())
       sentences = [s.strip() for s in clean_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
       
       results = []
       for i, sentence in enumerate(sentences):
           full_sentence = sentence + "."
           translated = translate_text(full_sentence)
           sentence_vocabs = extract_fast_contextual_vocab(full_sentence, translated)
           
           # 預先處理好測驗題目與干擾項，存進記憶
           quiz_info = None
           if sentence_vocabs:
               target_vocab = sentence_vocabs[0]
               pattern = re.compile(re.escape(target_vocab["word"]), re.IGNORECASE)
               blanked = pattern.sub("_______", full_sentence)
               
               options = [target_vocab["word"]]
               fallback = ["spoke", "party", "formal", "bench", "translate", "severe-looking"]
               for fb in fallback:
                   if len(options) < 4 and fb != target_vocab["word"] and fb not in options:
                       options.append(fb)
               options = sorted(options)
               
               quiz_info = {
                   "blanked": blanked,
                   "options": options,
                   "target_word": target_vocab["word"],
                   "target_meaning": target_vocab["meaning"]
               }
               
           results.append({
               "full_sentence": full_sentence,
               "translated": translated,
               "vocabs": sentence_vocabs,
               "quiz": quiz_info
           })
       
       # 寫入 st.session_state 大腦
       st.session_state.processed_data = results
   else:
       st.warning("Please enter some English sentences first!")

# 🎨 渲染區：只要大腦裡有資料，就一直畫在畫面上，不怕網頁重整！
if st.session_state.processed_data:
   st.success(f"🎉 Awesome! We managed the text successfully. Let's practice:")
   
   for i, data in enumerate(st.session_state.processed_data):
       # 1️⃣ 句子卡片
       st.markdown(f"""
            <div class="sentence-card">
                <div class="card-index">Sentence {i+1}</div>
                <div class="english-text">{data["full_sentence"]}</div>
                <div class="chinese-text">💡 {data["translated"]}</div>
            </div>
       """, unsafe_allow_html=True)
       
       # 2️⃣ 發音條
       try:
           tts = gTTS(text=data["full_sentence"], lang='en', slow=False)
           fp = io.BytesIO()
           tts.write_to_fp(fp)
           fp.seek(0)
           st.audio(fp, format="audio/mp3")
       except Exception:
           st.write("")
       
       # 3️⃣ 🔑 Vocabulary
       if data["vocabs"]:
           with st.expander("🔑 Vocabulary"):
               vocab_html = '<div class="vocab-box">'
               for item in data["vocabs"]:
                   vocab_html += f'<span class="vocab-tag">📌 {item["word"]}：{item["meaning"]}</span>'
               vocab_html += '</div>'
               st.markdown(vocab_html, unsafe_allow_html=True)
               
           # 4️⃣ 📝 Cloze Quiz
           if data["quiz"]:
               with st.expander("📝 Cloze Quiz"):
                   st.markdown(f"""
                   <div class="quiz-box">
                       <div class="quiz-prompt">🎯 句子挖空挑戰：</div>
                       <div style="font-size: 19px; font-weight: 500; color: #1e293b; margin-bottom: 6px;">{data["quiz"]["blanked"]}</div>
                   </div>
                   """, unsafe_allow_html=True)
                   
                   user_choice = st.radio(
                       "請選擇最適合填入空格的單字：",
                       data["quiz"]["options"],
                       key=f"radio_sentence_{i}"
                   )
                   
                   if st.button("️確認答案", key=f"btn_sentence_{i}"):
                       if user_choice == data["quiz"]["target_word"]:
                           st.success(f"🎉 太棒了！答對了！這裡使用的是『{data['quiz']['target_word']}』（意為：{data['quiz']['target_meaning']}）。")
                       else:
                           st.error(f"❌ 可惜不對唷！正確答案應該是『{data['quiz']['target_word']}』（意為：{data['quiz']['target_meaning']}）。再試一次！")
       st.markdown("<br>", unsafe_allow_html=True)
