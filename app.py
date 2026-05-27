import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io

# 🎯 網頁基礎配置
st.set_page_config(
    page_title="Smart Reading Buddy",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🚀 輕量免費翻譯核心
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "Translation Unavailable"

# 🧠 免金鑰 AI 智能出題核心（暗中生成全新句子）
def generate_cloze_sentences_free(vocabs, sentence_text):
    target_words_str = ",".join([v["word"] for v in vocabs])
    
    # 備用安全降級機制
    fallback_data = []
    for v in vocabs:
        pattern = re.compile(re.escape(v["word"]), re.IGNORECASE)
        blanked = pattern.sub("_______", sentence_text)
        fallback_data.append({
            "target_word": v["word"],
            "new_sentence": blanked,
            "meaning": v["meaning"]
        })
        
    prompt = f"Generate 1 new, distinct simple English sentence for each word in [{target_words_str}]. Replace the word with '_______'. Respond ONLY in raw JSON format like this: [{{\"target_word\":\"word\",\"new_sentence\":\"The _______ is here.\"}}]"
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            ai_reply = response.read().decode('utf-8').strip()
            clean_json_str = re.sub(r'^```json\s*|\s*```$', '', ai_reply)
            new_data = json.loads(clean_json_str)
            
            for item in new_data:
                tw = item["target_word"].lower()
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

# --- 🚀 視覺外觀設計 (CSS) ---
st.markdown("""
   <style>
   #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
   .stAppDeployButton {display: none !important;} div[data-testid="stDecoration"] {display: none !important;}
   .stApp { background-color: #F8FAFC; }
   
   /* 🏷️ MACAOCMM 頂部標籤 */
   .macaocmm-badge { display: inline-block; background-color: #E0F2FE; color: #0369A1; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; border: 1px solid #BAE6FD; margin-bottom: 8px; }

   /* 💙 深藍色大橫幅 */
   .header-banner { background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); padding: 35px 20px; border-radius: 18px; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2); }
   .header-banner h1 { color: white !important; margin: 0 !important; font-weight: 800 !important; font-size: 40px !important; letter-spacing: -0.5px; }
   .header-banner p { color: #E0F2FE !important; opacity: 0.95 !important; font-size: 16px !important; margin-top: 8px !important; font-weight: 500; }

   /* ✍️ 黑框輸入框設置 */
   .stTextArea textarea { border: 3px solid #000000 !important; border-radius: 12px !important; padding: 15px !important; font-size: 18px !important; }
   
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

   /* 句子卡片與單字外觀 */
   .sentence-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; }
   .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.4 !important; }
   .chinese-text { font-size: 19px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; margin-top: 10px; }
   .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; margin-top: 5px; }
   .vocab-tag { display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px; font-size: 15px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; }
   
   /* 🟩 綠色開新分頁按鈕 */
   .quiz-btn { display: inline-block; text-align: center; width: 100%; padding: 14px; background-color: #10B981; color: white !important; font-size: 18px; font-weight: bold; border-radius: 8px; text-decoration: none; margin-top: 12px; box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2); }
   .quiz-btn:hover { background-color: #059669; text-decoration: none; }
   
   /* 📝 測驗頁面外觀 */
   .quiz-box { background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
   .quiz-prompt { font-size: 16px !important; font-weight: bold !important; color: #1E3A8A !important; margin-bottom: 8px; }
   .explanation-box { background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px 16px; border-radius: 4px; margin-top: 10px; font-size: 16px; color: #1E40AF; }
   </style>
""", unsafe_allow_html=True)

# 🌐 智慧路由判斷
query_params = st.query_params

# ==========================================
# ─── 🚪 【模式 A：獨立互動測驗頁 (AI 智能出題盲測)】 ───
# ==========================================
if "cloze_json" in query_params:
    cloze_json_raw = urllib.parse.unquote(query_params["cloze_json"])
    try:
        all_quiz_data = json.loads(cloze_json_raw)
    except:
        all_quiz_data = []
    
    st.markdown("""
        <div style='text-align: center; margin-top: 10px; margin-bottom: 25px;'>
            <h2 style='color: #1E3A8A; font-weight: 800; margin-bottom:5px;'>📝 Contextual Cloze Quiz</h2>
            <p style='color: #64748B; font-size: 16px;'>Complete the blanks based purely on the new sentence context.</p>
        </div>
    """, unsafe_allow_html=True)
    st.write("---")
    
    for idx, quiz_item in enumerate(all_quiz_data):
        target_word = quiz_item.get("target_word", "error")
        meaning = quiz_item.get("meaning", "")
        new_sentence = quiz_item.get("new_sentence", "_______")
        
        st.markdown(f"""
        <div class="quiz-box">
            <div class="quiz-prompt">Question {idx + 1} of {len(all_quiz_data)}</div>
            <div style="font-size: 22px; font-weight: 600; color: #0F172A; line-height: 1.4;">{new_sentence}</div>
        </div>
        """, unsafe_allow_html=True)
        
        options = [target_word]
        fallback = ["spoke", "party", "formal", "bench", "translate", "future", "system", "lessons", "think", "eyes", "clear"]
        for fb in fallback:
            if len(options) < 4 and fb.lower() != target_word.lower() and fb not in options:
                options.append(fb)
        options = sorted(options)
        
        state_key = f"q_submitted_{idx}"
        if state_key not in st.session_state:
            st.session_state[state_key] = False
            
        user_choice = st.radio(
            f"Select the correct option for Blank {idx + 1}:",
            options,
            key=f"radio_{idx}",
            disabled=st.session_state[state_key]
        )
        
        if st.button(f"Verify Answer {idx + 1}", key=f"btn_{idx}", disabled=st.session_state[state_key]):
            st.session_state[state_key] = True
            st.rerun()
            
        if st.session_state[state_key]:
            if user_choice.lower() == target_word.lower():
                st.success(f"🎉 Excellent! '{user_choice}' is CORRECT.")
            else:
                st.error(f"❌ Incorrect. The correct answer is: **{target_word}**")
            
            st.markdown(f"""
                <div class="explanation-box">
                    <strong>💡 語境解析與單字提示：</strong><br>
                    本題正確答案為 <strong>{target_word}</strong>（中文意為：{meaning}）。<br>
                    本句測驗大意為：{translate_text(new_sentence, target_lang='zh-TW')}
                </div>
            """, unsafe_allow_html=True)
            
        st.write("<br><br>", unsafe_allow_html=True)
        
    st.write("---")
    st.info("💡 Review complete! Close this browser tab to return to the reading board.")

# ==========================================
# ─── 📖 【模式 B：閱讀主頁面工作區 (完美保留所有設置)】 ───
# ==========================================
else:
    # 頂部標籤
    st.markdown('<div class="macaocmm-badge">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)
    
    # 深藍色 Header
    st.markdown("""
       <div class="header-banner">
           <h1>📱 Smart Reading</h1>
