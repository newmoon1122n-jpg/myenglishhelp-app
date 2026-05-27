import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io
import random

# 🎯 Web Configuration
st.set_page_config(
   page_title="Smart Reading Buddy",
   layout="centered",
   initial_sidebar_state="collapsed"
)
 
# 🚀 Lightweight Translation / Explanation Core (Switched to English definition)
def get_english_definition(text):
   try:
       # Using dictionary hint style definition for cleaner context mapping
       url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(text)}"
       req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
       with urllib.request.urlopen(req) as response:
           data = json.loads(response.read().decode('utf-8'))
           return "".join([sentence[0] for sentence in data[0] if sentence[0]])
   except Exception:
       return "Definition Unavailable"
 
# 🎯 Fast Contextual Vocabulary Extractor
def extract_fast_contextual_vocab(sentence_text):
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
       
       if "'" in w_lower:
           continue
           
       if len(w_lower) < 3 or w_lower in ignore_words or w_lower in seen_words:
           continue
           
       if not re.match(r'^[a-z\-]+$', w_lower):
           continue
           
       seen_words.add(w_lower)
        
       try:
           # Provide clean formatting for the word in pure English
           vocab_list.append({"word": w_lower, "meaning": f"Core word inside context: {w_lower}"})
       except Exception:
           continue
       
   return vocab_list

# 🧠 AI Quiz Core: Generate a clean immersive experience in a new tab
def generate_cloze_sentences_free(vocabs):
    target_words_str = ",".join([v["word"] for v in vocabs])
    
    base_distractors = ["challenge", "explore", "journey", "knowledge", "practice", "wisdom", "advance", "creative", "imagine", "observe", "active", "scenery", "wonder", "perfect", "culture", "nature", "history", "science", "future", "digital", "world", "learning", "opinion", "society", "experience", "language", "ability", "improve", "express", "develop"]
    
    fallback_data = []
    for v in vocabs:
        wrong_choices = [w for w in base_distractors if w.lower() != v["word"].lower()]
        selected_wrong = random.sample(wrong_choices, 3)
        fallback_data.append({
            "target_word": v["word"],
            "new_sentence": "We need to analyze and _______ our skills in the current context.",
            "meaning": v["meaning"],
            "distractors": selected_wrong
        })
        
    prompt = f"For each word in [{target_words_str}], generate 1 new simple English sentence replacing the word with '_______'. Also, provide 3 distinct, plausible incorrect English words as distractors. Respond ONLY in raw JSON format like this: [{{\"target_word\":\"word\",\"new_sentence\":\"The _______ is clear.\",\"distractors\":[\"wrong1\",\"wrong2\",\"wrong3\"]}}]"
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as response:
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


# --- 🚀 Modern Visual Theme CSS (Pure English) 🚀 ---
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
  .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.4 !important; margin-bottom: 5px !important; }
 
  .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; margin-top: 5px; margin-bottom: 10px; }
  .vocab-tag {
      display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px;
      font-size: 15px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; border: 1px solid #FFE0B2;
   }
   
  .stExpander { border: none !important; box-shadow: none !important; margin-bottom: 20px !important; }
  .stExpander summary { font-size: 16px !important; font-weight: bold !important; color: #D84315 !important; background-color: #FFFDE5 !important; border-radius: 8px !important; padding: 10px !important; }
  
  .quiz-link-btn {
      display: inline-block; text-align: center; width: 100%; padding: 12px;
      background-color: #10B981 !important; color: white !important;
      font-size: 18px !important; font-weight: bold !important; border-radius: 10px !important;
      text-decoration: none !important; box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2) !important;
      margin-top: 10px; margin-bottom: 10px;
  }
  .quiz-link-btn:hover { background-color: #059669 !important; text-decoration: none !important; }
  
  .quiz-page-card { background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
  .quiz-page-prompt { font-size: 16px !important; font-weight: bold !important; color: #1E3A8A !important; margin-bottom: 8px; }
  .explanation-page-box { background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px 16px; border-radius: 4px; margin-top: 10px; font-size: 16px; color: #1E40AF; }
  </style>
""", unsafe_allow_html=True)

query_params = st.query_params

# ==========================================
# ─── 🚪 【Mode A: Contextual Cloze Quiz (New Tab)】 ───
# ==========================================
if "quiz_vocabs" in query_params:
    vocabs_raw = urllib.parse.unquote(query_params["quiz_vocabs"])
    try:
        incoming_vocabs = json.loads(vocabs_raw)
    except:
        incoming_vocabs = []
        
    st.markdown("""
        <div style='text-align: center; margin-top: 15px; margin-bottom: 25px;'>
            <h2 style='color: #1E3A8A; font-weight: 800; margin-bottom:5px;'>📝 Contextual Cloze Quiz</h2>
            <p style='color: #64748B; font-size: 16px;'>Select the best target vocabulary word based on the context generated below.</p>
        </div>
    """, unsafe_allow_html=True)
    st.write("---")
    
    if incoming_vocabs:
        if "session_quiz_data" not in st.session_state:
            with st.spinner("⚡ AI is constructing distinct immersive exercises for your selection..."):
                st.session_state.session_quiz_data = generate_cloze_sentences_free(incoming_vocabs)
        
        for idx, quiz_item in enumerate(st.session_state.session_quiz_data):
            target_word = quiz_item.get("target_word", "error")
            new_sentence = quiz_item.get("new_sentence", "_______")
            distractors = quiz_item.get("distractors", ["wordA", "wordB", "wordC"])
            
            st.markdown(f"""
            <div class="quiz-page-card">
                <div class="quiz-page-prompt">Question {idx + 1}</div>
                <div style="font-size: 22px; font-weight: 600; color: #0F172A; line-height: 1.4;">{new_sentence}</div>
            </div>
            """, unsafe_allow_html=True)
            
            options = list(set([target_word] + distractors))
            emergency = ["wonder", "system", "future", "clear", "active", "scenery"]
            for em in emergency:
                if len(options) < 4 and em.lower() != target_word.lower() and em not in options:
                    options.append(em)
            options = sorted(options)
            
            state_key = f"page_submit_{idx}"
            if state_key not in st.session_state:
                st.session_state[state_key] = False
                
            user_choice = st.radio(
                f"Select the correct option for Blank {idx + 1}:",
                options,
                key=f"page_radio_{idx}",
                disabled=st.session_state[state_key]
            )
            
            if st.button(f"Verify Answer {idx + 1}", key=f"page_btn_{idx}", disabled=st.session_state[state_key]):
                st.session_state[state_key] = True
                st.rerun()
                
            if st.session_state[state_key]:
                if user_choice.lower() == target_word.lower():
                    st.success(f"🎉 Well done! '{user_choice}' is completely correct.")
                else:
                    st.error(f"❌ Incorrect. The correct answer should be: **{target_word}**")
                
                st.markdown(f"""
                    <div class="explanation-page-box">
                        <strong>💡 Vocabulary Expansion Hint:</strong><br>
                        The targeted keyword is <strong>{target_word}</strong>. Try practicing this sentence aloud to build retention.
                    </div>
                """, unsafe_allow_html=True)
                
            st.write("<br><br>", unsafe_allow_html=True)
    else:
        st.warning("No vocabulary parameters detected. Please return to the reading panel.")
        
    st.write("---")
    st.info("💡 Practice complete! You can safely close this browser window and go back to your main reading stream.")

# ==========================================
# ─── 📖 【Mode B: Main Reading Panel (Solid Audio Sync)】 ───
# ==========================================
else:
    st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)
     
    st.markdown("""
      <div class="app-header">
          <p class="main-title">📱 Smart Reading Panel</p>
          <p class="sub-title">Break down text • Learn step by step</p>
       </div>
    """, unsafe_allow_html=True)
     
    st.markdown('<span class="input-disclaimer">Content engine online. Verified secure framework.</span>', unsafe_allow_html=True)
    st.markdown('<p class="input-label">✍️ Paste your English text below:</p>', unsafe_allow_html=True)
     
    text_input = st.text_area("", height=180, placeholder="Enter English text here...", key="main_text_input")
    st.write("") 
     
    if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True, key="start_analysis_btn"):
       if text_input.strip():
          st.session_state.processed_text = text_input.strip()
          if "audio_cache" in st.session_state:
              del st.session_state.audio_cache
       else:
          st.warning("Please enter some English sentences first!")

    if "processed_text" in st.session_state:
          sentences = [s.strip() for s in st.session_state.processed_text.replace('?', '.').replace('!', '.').split('.') if s.strip()]
          st.success(f"🎉 Analysis Complete! Found {len(sentences)} distinct segments. Let's practice:")
          
          if "audio_cache" not in st.session_state:
              st.session_state.audio_cache = {}
          
          for i, sentence in enumerate(sentences):
              full_sentence = sentence + "."
              sentence_vocabs = extract_fast_contextual_vocab(full_sentence)
              
              # 1️⃣ Clean sentence cards with absolutely no Chinese elements
              st.markdown(f"""
                    <div class="sentence-card">
                        <div class="card-index">Sentence {i+1}</div>
                        <div class="english-text">{full_sentence}</div>
                    </div>
              """, unsafe_allow_html=True)
              
              # 2️⃣ Robust audio cache layer
              try:
                   if i not in st.session_state.audio_cache:
                       tts = gTTS(text=full_sentence, lang='en', slow=False)
                       fp = io.BytesIO()
                       tts.write_to_fp(fp)
                       fp.seek(0)
                       st.session_state.audio_cache[i] = fp.read()
                   
                   st.audio(st.session_state.audio_cache[i], format="audio/mp3")
              except Exception:
                   st.warning("Audio generation slightly delayed...")
              
              # 3️⃣ English Vocabulary drawers
              if sentence_vocabs:
                   with st.expander("🔑 Vocabulary Track"):
                       vocab_html = '<div class="vocab-box">'
                       for item in sentence_vocabs:
                           vocab_html += f'<span class="vocab-tag">📌 {item["word"]}</span>'
                       vocab_html += '</div>'
                       st.markdown(vocab_html, unsafe_allow_html=True)
                       
                       # 4️⃣ Fully English-targeted Quiz Redirection Button
                       vocabs_json = json.dumps(sentence_vocabs)
                       encoded_vocabs = urllib.parse.quote(vocabs_json)
                       quiz_target_url = f"?quiz_vocabs={encoded_vocabs}"
                       
                       st.markdown(f"""
                            <a href="{quiz_target_url}" target="_blank" class="quiz-link-btn">
                                📝 Open Cloze Quiz (Sentence {i+1} • Fresh Context)
                            </a>
                       """, unsafe_allow_html=True)
              else:
                   st.write("")
              st.markdown("<br>", unsafe_allow_html=True)
