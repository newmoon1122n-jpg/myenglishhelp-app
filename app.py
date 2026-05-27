import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io
import random

# 🎯 Web Configuration
st.set_page_config(page_title="Smart Reading Buddy", layout="centered", initial_sidebar_state="collapsed")

# 🚀 翻譯核心
def translate_text(text, target_lang='zh-TW'):
   try:
       url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
       req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
       with urllib.request.urlopen(req) as response:
           data = json.loads(response.read().decode('utf-8'))
           return "".join([sentence[0] for sentence in data[0] if sentence[0]])
   except Exception: return "無法取得翻譯"

# 🎯 語境生字提取
def extract_fast_contextual_vocab(sentence_text, sentence_translation):
   clean_text = re.sub(r"[^\w\s'\-]", ' ', sentence_text)
   words = clean_text.split()
   ignore_words = {'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with', 'and', 'but', 'or', 'so', 'because', 'if', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'can', 'will', 'should', 'would', 'could', 'may', 'might', 'must', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him', 'them', 'us'}
   vocab_list = []
   seen_words = set()
   for word in words:
       w_lower = word.lower().strip('-')
       if "'" in w_lower or len(w_lower) < 3 or w_lower in ignore_words or w_lower in seen_words or not re.match(r'^[a-z\-]+$', w_lower): continue
       seen_words.add(w_lower)
       try:
           context_meaning = translate_text(w_lower)
           if context_meaning.lower() != w_lower: vocab_list.append({"word": w_lower, "meaning": context_meaning})
       except: continue
   return vocab_list

# 🧠 Gemini AI 智能出題
def generate_cloze_sentences_gemini(vocabs):
    target_words_str = ",".join([v["word"] for v in vocabs])
    if "GEMINI_API_KEY" not in st.secrets:
        return [{"target_word": v["word"], "new_sentence": "I need to learn how to _______ correctly.", "meaning": v["meaning"], "distractors": ["error", "fail", "wrong"]} for v in vocabs]
    
    api_key = st.secrets["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"For each word in [{target_words_str}], generate 1 unique simple English sentence replacing the word with '_______'. Provide 3 plausible distractors. Respond ONLY in raw JSON format like this: [{{\"target_word\":\"word\",\"new_sentence\":\"The _______ is clear.\",\"distractors\":[\"wrong1\",\"wrong2\",\"wrong3\"]}}]"
    
    try:
        req = urllib.request.Request(url, data=json.dumps({"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=12) as response:
            ai_reply = json.loads(response.read().decode('utf-8'))["candidates"][0]["content"]["parts"][0]["text"].strip()
            data = json.loads(ai_reply)
            for item in data:
                for v in vocabs:
                    if v["word"].lower() == item["target_word"].lower(): item["meaning"] = v["meaning"]
            return data
    except: return [{"target_word": v["word"], "new_sentence": "Always try to _______ new ideas.", "meaning": v["meaning"], "distractors": ["ignore", "forget", "avoid"]} for v in vocabs]

# --- 🎨 CSS 排版設置 ---
st.markdown("""
  <style>
  .author-logo { position: absolute; top: -15px; left: 0px; font-size: 12px; font-weight: 700; color: #1E4ED8; background-color: #EFF6FF; padding: 5px 12px; border-radius: 8px; border: 2px solid #BFDBFE; z-index: 999; }
  .app-header { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); padding: 30px; border-radius: 20px; text-align: center; color: white; margin-bottom: 25px; }
  .stTextArea textarea { border: 6px solid #000000 !important; border-radius: 14px !important; font-size: 20px !important; }
  .stButton button { background-color: #FF9800 !important; font-weight: 800 !important; font-size: 24px !important; color: white !important; padding: 14px 28px !important; border-radius: 12px !important; }
  .sentence-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px; }
  .vocab-box { background-color: #FFFDF5; border: 2px dashed #FFD54F; border-radius: 10px; padding: 12px; margin-top: 10px; }
  .vocab-tag { display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px; font-size: 15px; font-weight: bold; margin: 4px; border: 1px solid #FFE0B2; }
  .quiz-link-btn { display: block; text-align: center; padding: 12px; background-color: #10B981 !important; color: white !important; font-weight: bold; border-radius: 10px; text-decoration: none; margin-top: 10px; }
  .quiz-page-card { background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
  .explanation-page-box { background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 15px; border-radius: 4px; margin-top: 10px; }
  </style>
""", unsafe_allow_html=True)

query_params = st.query_params

# ================= 測驗頁 =================
if "quiz_vocabs" in query_params:
    incoming_vocabs = json.loads(urllib.parse.unquote(query_params["quiz_vocabs"]))
    st.markdown("## 📝 Contextual Cloze Quiz")
    if "session_quiz_data" not in st.session_state:
        with st.spinner("AI is generating questions..."): st.session_state.session_quiz_data = generate_cloze_sentences_gemini(incoming_vocabs)
    
    for idx, q in enumerate(st.session_state.session_quiz_data):
        st.markdown(f'<div class="quiz-page-card"><strong>Question {idx + 1}:</strong><br>{q["new_sentence"]}</div>', unsafe_allow_html=True)
        options = sorted(list(set([q["target_word"]] + q["distractors"])))
        state_key = f"submit_{idx}"
        if state_key not in st.session_state: st.session_state[state_key] = False
        choice = st.radio(f"Select option for Blank {idx + 1}:", options, key=f"radio_{idx}", disabled=st.session_state[state_key])
        
        if st.button(f"Verify Answer {idx + 1}", key=f"btn_{idx}", disabled=st.session_state[state_key]):
            st.session_state[state_key] = True
            st.rerun()
            
        if st.session_state[state_key]:
            if choice.lower() == q["target_word"].lower(): st.success("Correct!")
            else: st.error(f"Incorrect. The correct answer is: **{q['target_word']}**")
            
            # ✨ 新增：翻譯功能整合
            trans = translate_text(q["new_sentence"])
            st.markdown(f'''<div class="explanation-page-box">
                <strong>💡 Target Vocabulary Hint:</strong> {q["target_word"]} ({q["meaning"]})<br>
                <em>Context: {q["new_sentence"]}</em><br>
                <span style="color: #475569;"><strong>中文翻譯：</strong>{trans}</span>
            </div>''', unsafe_allow_html=True)
            st.write("<br><br>", unsafe_allow_html=True)

# ================= 主頁面 =================
else:
    st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-header"><h1>📱 Smart Reading</h1></div>', unsafe_allow_html=True)
    text_input = st.text_area("", height=180, placeholder="Enter English text here...")
    
    if st.button("🚀 Start Audio & Reading Analysis"): st.session_state.processed_text = text_input
    
    if "processed_text" in st.session_state:
        sentences = [s.strip() + "." for s in st.session_state.processed_text.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        for i, s in enumerate(sentences):
            trans = translate_text(s)
            vocabs = extract_fast_contextual_vocab(s, trans)
            st.markdown(f'<div class="sentence-card"><strong>Sentence {i+1}</strong><br>{s}<br><small style="color:gray;">💡 {trans}</small></div>', unsafe_allow_html=True)
            
            if vocabs:
                with st.expander("🔑 Vocabulary"):
                    st.markdown('<div class="vocab-box">' + "".join([f'<span class="vocab-tag">📌 {v["word"]} ： {v["meaning"]}</span>' for v in vocabs]) + '</div>', unsafe_allow_html=True)
                    encoded = urllib.parse.quote(json.dumps(vocabs))
                    st.markdown(f'<a href="?quiz_vocabs={encoded}" target="_blank" class="quiz-link-btn">📝 Take Cloze Quiz</a>', unsafe_allow_html=True)
