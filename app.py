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
       
       if "'" in w_lower:
           continue
           
       if len(w_lower) < 3 or w_lower in ignore_words or w_lower in seen_words:
           continue
           
       if not re.match(r'^[a-z\-]+$', w_lower):
           continue
           
       seen_words.add(w_lower)
        
       try:
           basic_meaning = translate_text(w_lower)
           context_meaning = basic_meaning
           
           if w_lower == "party":
                if "政黨" in sentence_translation: context_meaning = "政黨"
                elif "派對" in sentence_translation or "聚會" in sentence_translation: context_meaning = "派對/聚會"
           
           elif w_lower == "spoke":
                if "輻條" in sentence_translation or "輪輻" in sentence_translation: context_meaning = "輻條"
                elif "說" in sentence_translation or "談" in sentence_translation: context_meaning = "說話 (speak的過去式)"
           
           elif "-" in w_lower and context_meaning.lower() == w_lower:
                continue
                
           if context_meaning.lower() == w_lower:
                continue
                
           vocab_list.append({"word": w_lower, "meaning": context_meaning})
       except Exception:
           continue
       
   return vocab_list

# 🧠 AI 智能出題核心：在新分頁中為每個生字獨立打造全新語境句子與「完全不同」的四選一選項
def generate_cloze_sentences_free(vocabs):
    target_words_str = ",".join([v["word"] for v in vocabs])
    
    # 🌟 豐富的動態干擾字庫，確保往下拉時每題選項絕對不重複
    base_distractors = ["challenge", "explore", "journey", "knowledge", "practice", "wisdom", "advance", "creative", "imagine", "observe", "active", "scenery", "wonder", "perfect", "culture", "nature", "history", "science", "future", "digital", "world", "learning", "opinion", "society", "experience", "language", "ability", "improve", "express", "develop"]
    
    fallback_data = []
    for v in vocabs:
        wrong_choices = [w for w in base_distractors if w.lower() != v["word"].lower()]
        selected_wrong = random.sample(wrong_choices, 3)
        fallback_data.append({
            "target_word": v["word"],
            "new_sentence": f"We need to _______ our skills in the digital world.",
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
 
  .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; margin-top: 5px; margin-bottom: 10px; }
  .vocab-tag {
      display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px;
      font-size: 15px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; border: 1px solid #FFE0B2;
   }
   
  .stExpander { border: none !important; box-shadow: none !important; margin-bottom: 20px !important; }
  .stExpander summary { font-size: 16px !important; font-weight: bold !important; color: #D84315 !important; background-color: #FFFDE5 !important; border-radius: 8px !important; padding: 10px !important; }
  
  /* 🟩 老師專屬：經典鮮綠色開新網頁分頁按鍵樣式 */
  .quiz-link-btn {
      display: inline-block; text-align: center; width: 100%; padding: 12px;
      background-color: #10B981 !important; color: white !important;
      font-size: 18px !important; font-weight: bold !important; border-radius: 10px !important;
      text-decoration: none !important; box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2) !important;
      margin-top: 10px; margin-bottom: 10px;
  }
  .quiz-link-btn:hover { background-color: #059669 !important; text-decoration: none !important; }
  
  /* 📝 新網頁測驗卡片外觀 */
  .quiz-page-card { background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
  .quiz-page-prompt { font-size: 16px !important; font-weight: bold !important; color: #1E3A8A !important; margin-bottom: 8px; }
  .explanation-page-box { background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px 16px; border-radius: 4px; margin-top: 10px; font-size: 16px; color: #1E40AF; }
  </style>
""", unsafe_allow_html=True)

# 🌐 讀取網址參數，判斷是否為「新開啟的獨立測驗分頁」
query_params = st.query_params

# ==========================================
# ─── 🚪 【模式 A：全新網頁分頁框 (獨立小測驗)】 ───
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
            <p style='color: #64748B; font-size: 16px;'>提升英文應用能力：請根據 AI 全新生成的語境情境選擇最佳單字</p>
        </div>
    """, unsafe_allow_html=True)
    st.write("---")
    
    if incoming_vocabs:
        # 100% 獨立觸發 AI 針對傳過來的生字庫生成全新句子與隨機選項
        if "session_quiz_data" not in st.session_state:
            with st.spinner("⚡ Gemini AI 正在為您暗中打造全新的應用題型與選項..."):
                st.session_state.session_quiz_data = generate_cloze_sentences_free(incoming_vocabs)
        
        for idx, quiz_item in enumerate(st.session_state.session_quiz_data):
            target_word = quiz_item.get("target_word", "error")
            meaning = quiz_item.get("meaning", "")
            new_sentence = quiz_item.get("new_sentence", "_______")
            distractors = quiz_item.get("distractors", ["wordA", "wordB", "wordC"])
            
            st.markdown(f"""
            <div class="quiz-page-card">
                <div class="quiz-page-prompt">Question {idx + 1}</div>
                <div style="font-size: 22px; font-weight: 600; color: #0F172A; line-height: 1.4;">{new_sentence}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 💥 結合動態干擾字，打散排序，確保每一道題目的四個選項完完全全不一樣！
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
                    st.success(f"🎉 太棒了！ '{user_choice}' 完全正確。")
                else:
                    st.error(f"❌ 不夠準確。正確答案應該是: **{target_word}**")
                
                st.markdown(f"""
                    <div class="explanation-page-box">
                        <strong>💡 應用能力提升提示：</strong><br>
                        核心單字：<strong>{target_word}</strong>（中文意思：{meaning}）<br>
                        全新應用句翻譯：{translate_text(new_sentence, target_lang='zh-TW')}
                    </div>
                """, unsafe_allow_html=True)
                
            st.write("<br><br>", unsafe_allow_html=True)
    else:
        st.warning("未偵測到生字數據，請返回主頁重新分析。")
        
    st.write("---")
    st.info("💡 練習完畢！您可以直接關閉此網頁分頁，返回原文章閱讀面板。")

# ==========================================
# ─── 📖 【模式 B：文章閱讀主網頁 (完美保留所有視覺)】 ───
# ==========================================
else:
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
     
    text_input = st.text_area("", height=180, placeholder="Enter English text here...", key="main_text_input")
    st.write("") 
     
    if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True, key="start_analysis_btn"):
       if text_input.strip():
          st.session_state.processed_text = text_input.strip()
       else:
          st.warning("Please enter some English sentences first!")

    if "processed_text" in st.session_state:
          sentences = [s.strip() for s in st.session_state.processed_text.replace('?', '.').replace('!', '.').split('.') if s.strip()]
          st.success(f"🎉 Awesome! We found {len(sentences)} sentences for you. Let's practice:")
          
          for i, sentence in enumerate(sentences):
              full_sentence = sentence + "."
              translated = translate_text(full_sentence)
              sentence_vocabs = extract_fast_contextual_vocab(full_sentence, translated)
              
              # 1️⃣ 第一步：列句子卡片 (藍條樣式)
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
                   st.audio(fp, format="audio/mp3", key=f"audio_player_{i}")
              except Exception:
                   st.warning("Audio generation slightly delayed...")
              
              # 3️⃣ 第三步：將生字本包進摺疊抽屜中 (溫潤橙金色)
              if sentence_vocabs:
                   with st.expander("🔑 Vocabulary "):
                       vocab_html = '<div class="vocab-box">'
                       for item in sentence_vocabs:
                           vocab_html += f'<span class="vocab-tag">📌 {item["word"]}：{item["meaning"]}</span>'
                       vocab_html += '</div>'
                       st.markdown(vocab_html, unsafe_allow_html=True)
                       
                       # 4️⃣ 第四步：綠色按鍵 ── 點擊開啟獨立的新網頁分頁框
                       vocabs_json = json.dumps(sentence_vocabs)
                       encoded_vocabs = urllib.parse.quote(vocabs_json)
                       # 利用 target="_blank" 確保點擊時在全新分頁開啟測驗，絕不干擾主頁面
                       quiz_target_url = f"?quiz_vocabs={encoded_vocabs}"
                       
                       st.markdown(f"""
                            <a href="{quiz_target_url}" target="_blank" class="quiz-link-btn">
                                📝 Open Cloze Quiz (Sentence {i+1} • New Context)
                            </a>
                       """, unsafe_allow_html=True)
              else:
                   st.write("")
              st.markdown("<br>", unsafe_allow_html=True)
