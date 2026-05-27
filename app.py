import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io
import random

# 🎯 網頁基礎配置
st.set_page_config(
    page_title="Smart Reading Buddy",
    layout="centered",
    initial_sidebar_state="expanded" # 預展開側邊欄，方便測驗顯示
)

# 🚀 輕量免費翻譯核心 (免金鑰)
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except:
        return "Translation Unavailable"

# 🧠 AI 智能出題核心：為生字暗中生成「全新語境句子」與「不一樣的四選一干擾項」
def generate_cloze_sentences_free(vocabs, sentence_text):
    target_words_str = ",".join([v["word"] for v in vocabs])
    
    # 🌟 動態干擾字基礎庫
    base_distractors = ["challenge", "explore", "journey", "knowledge", "practice", "wisdom", "advance", "creative", "imagine", "observe", "active", "scenery", "wonder", "perfect", "culture", "nature", "history", "science", "future", "digital", "world", "learning"]
    
    fallback_data = []
    for v in vocabs:
        pattern = re.compile(re.escape(v["word"]), re.IGNORECASE)
        blanked = pattern.sub("_______", sentence_text)
        wrong_choices = [w for w in base_distractors if w.lower() != v["word"].lower()]
        selected_wrong = random.sample(wrong_choices, 3)
        fallback_data.append({
            "target_word": v["word"],
            "new_sentence": blanked,
            "meaning": v["meaning"],
            "distractors": selected_wrong
        })
        
    prompt = f"For each word in [{target_words_str}], generate 1 new simple English sentence replacing the word with '_______'. Also, provide 3 distinct, plausible incorrect English words as distractors. Respond ONLY in raw JSON format like this: [{{\"target_word\":\"word\",\"new_sentence\":\"The _______ is clear.\",\"distractors\":[\"wrong1\",\"wrong2\",\"wrong3\"]}}]"
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            ai_reply = response.read().decode('utf-8').strip()
            clean_json_str = re.sub(r'^```json\s*|\s*```$', '', ai_reply)
            new_data = json.loads(clean_json_str)
            
            for item in new_data:
                tw = item["target_word"].lower()
                if "distractors" not in item or len(item["distractors"]) < 3:
                    wrong_choices = [w for w in base_distractors if w.lower() != tw]
                    item["distractors"] = random.sample(wrong_choices, 3)
                else:
                    item["distractors"] = [d for d in item["distractors"] if d.lower() != tw][:3]
                    while len(item["distractors"]) < 3:
                        extra = random.choice(base_distractors)
                        if extra.lower() != tw and extra not in item["distractors"]:
                            item["distractors"].append(extra)
                            
                for v in vocabs:
                    if v["word"].lower() == tw:
                        item["meaning"] = v["meaning"]
                        break
            return new_data
    except:
        return fallback_data

# 🎯 語境生字自動提取
def extract_vocab(sentence_text, sentence_translation):
    clean_text = re.sub(r"[^\w\s'\-]", ' ', sentence_text)
    words = clean_text.split()
    ignore = {'the','a','an','to','of','at','in','on','by','for','from','with','and','but','or','so','if','i','you','he','she','it','we','they','is','am','are','was','were','be','been','have','has','had','can','will','do','my','your','his','her','its','me','him','us','them'}
    vocab_list, seen = [], set()
    for word in words:
        w_lower = word.lower().strip('-')
        if "'" in w_lower or len(w_lower) < 3 or w_lower in ignore or w_lower in seen: continue
        if not re.match(r'^[a-z\-]+$', w_lower): continue
        seen.add(w_lower)
        try:
            raw = translate_text(w_lower)
            mean = raw.split('(')[0].strip() if '(' in raw else raw.strip()
            if w_lower == "party": mean = "政黨" if "政黨" in sentence_translation else "派對/聚會"
            elif w_lower == "spoke": mean = "輻條" if "輻條" in sentence_translation else "說話"
            if mean.lower() == w_lower or not mean: continue
            vocab_list.append({"word": w_lower, "meaning": mean})
        except: continue
    return vocab_list

# --- 🚀 前端樣式集中管理 (CSS) ---
st.markdown("""
   <style>
   #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
   .stAppDeployButton {display: none !important;} div[data-testid="stDecoration"] {display: none !important;}
   .stApp { background-color: #F8FAFC; }
   
   /* 🏷️ 頂部標籤 */
   .macaocmm-badge { display: inline-block; background-color: #E0F2FE; color: #0369A1; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; border: 1px solid #BAE6FD; margin-bottom: 8px; }

   /* 💙 深藍色大橫幅 */
   .header-banner { background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); padding: 35px 20px; border-radius: 18px; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2); }
   .header-banner h1 { color: white !important; margin: 0 !important; font-weight: 800 !important; font-size: 40px !important; }
   .header-banner p { color: #E0F2FE !important; font-size: 16px !important; margin-top: 8px !important; }

   /* ✍️ 輸入框粗黑框 */
   .stTextArea textarea { border: 3px solid #000000 !important; border-radius: 12px !important; padding: 15px !important; font-size: 18px !important; }
   
   /* 🚀 亮橙色分析按鈕 */
   div.stButton > button:first-child {
       background-color: #FF9800 !important;
       color: white !important;
       font-size: 18px !important;
       font-weight: bold !important;
       border-radius: 10px !important;
       padding: 12px 24px !important;
       border: none !important;
   }
   div.stButton > button:first-child:hover { background-color: #F57C00 !important; }

   /* 🧡 溫潤橙金色 Vocabulary 抽屜外觀 */
   .stExpander { border: none !important; box-shadow: none !important; margin-bottom: 10px !important; }
   .stExpander summary { 
       background-color: #FFF8E1 !important; 
       color: #FF8F00 !important; 
       border-radius: 10px !important; 
       padding: 12px !important; 
       font-weight: bold !important;
       font-size: 18px !important;
       border: 1px solid #FFE082 !important;
   }

   /* 句子卡片樣式 */
   .sentence-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); margin-top: 20px; }
   .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.4 !important; }
   .chinese-text { font-size: 19px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; margin-top: 10px; }
   .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; margin-top: 5px; }
   .vocab-tag { display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px; font-size: 15px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; }
   
   /* 🟩 綠色測驗按鈕樣式 */
   .stButton > button[key^="quiz_trigger_"] {
       background-color: #10B981 !important;
       color: white !important;
       font-size: 16px !important;
       font-weight: bold !important;
       border-radius: 8px !important;
       padding: 10px 20px !important;
       border: none !important;
       margin-top: 10px !important;
   }
   
   /* 📝 側邊欄測驗盒外觀 */
   .quiz-box { background-color: #FFFFFF; border: 2px solid #3B82F6; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
   .quiz-prompt { font-size: 14px !important; font-weight: bold !important; color: #1E3A8A !important; margin-bottom: 5px; }
   .explanation-box { background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 15px; color: #1E40AF; }
   </style>
""", unsafe_allow_html=True)


# ==========================================
# ─── 📖 【主頁面工作區 (完美保留老師所有設置)】 ───
# ==========================================
st.markdown('<div class="macaocmm-badge">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)
st.markdown('<div class="header-banner"><h1>📱 Smart Reading</h1><p>Break down text • Learn step by step</p></div>', unsafe_allow_html=True)

st.markdown('<p style="color: #FF0000; font-size: 14px; font-weight: bold; margin-bottom: 15px;">Powered by Google Translate. Content is for reference only and may not be perfect.</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:22px; font-weight:800; color:#000000; margin-bottom: 5px;">✍️ Paste your English text below:</p>', unsafe_allow_html=True)

text_input = st.text_area("", height=150, placeholder="Enter English text here...", key="main_text_input")
st.write("") 

# 用於儲存點擊狀態與小測數據的 Session State
if "current_quiz_data" not in st.session_state:
    st.session_state.current_quiz_data = None
if "current_quiz_title" not in st.session_state:
    st.session_state.current_quiz_title = ""

if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True, key="analyse_btn"):
    if text_input.strip():
        st.session_state.clean_input = re.sub(r'^\d+\s+', '', text_input.strip())
    else:
        st.warning("Please enter some English sentences first!")

# 如果有分析數據，渲染卡片
if "clean_input" in st.session_state:
    sentences = [s.strip() for s in st.session_state.clean_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
    st.success(f"🎉 Analysis Complete! Found {len(sentences)} sentences. Let's practice:")
    
    for i, sent in enumerate(sentences):
        full_sent = sent + "."
        trans = translate_text(full_sent)
        vocabs = extract_vocab(full_sent, trans)
        
        # 藍條卡片
        st.markdown(f"""
            <div class="sentence-card">
                <div style="font-size:14px; font-weight:bold; color:#3B82F6; margin-bottom:4px;">SENTENCE {i+1}</div>
                <div class="english-text">{full_sent}</div>
                <div class="chinese-text">💡 {trans}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # 發音條
        try:
            tts = gTTS(text=full_sent, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            st.audio(fp, format="audio/mp3", key=f"audio_{i}")
        except:
            pass
        
        # 🧡 溫潤橙金色 Vocabulary 抽屜
        if vocabs:
            with st.expander("🔑 Vocabulary", expanded=False):
                v_html = '<div class="vocab-box">'
                for v in vocabs:
                    v_html += f'<span class="vocab-tag">📌 {v["word"]}：{v["meaning"]}</span>'
                v_html += '</div>'
                st.markdown(v_html, unsafe_allow_html=True)
                
                # 🟩 綠色測驗按鈕 (直接點擊，右側滑出專屬全新題目)
                if st.button(f"📝 Open Cloze Quiz (Sentence {i+1})", key=f"quiz_trigger_{i}", use_container_width=True):
                    with st.spinner(f"⚡ AI is crafting brand NEW contextual sentences for Sentence {i+1}..."):
                        # 100% 呼叫 AI 針對這個句子生成全新的英文題目數據
                        st.session_state.current_quiz_data
