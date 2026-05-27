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
   ignore_words = {'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with', 'and', 'but', 'or', 'so', 'because', 'if', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'can', 'will', 'should', 'would', 'could', 'may', 'might', 'must', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him', 'them', 'us'}
   vocab_list = []
   seen_words = set()
   for word in words:
       w_lower = word.lower().strip('-')
       if "'" in w_lower or len(w_lower) < 3 or w_lower in ignore_words or w_lower in seen_words or not re.match(r'^[a-z\-]+$', w_lower):
           continue
       seen_words.add(w_lower)
       try:
           basic_meaning = translate_text(w_lower)
           if basic_meaning.lower() != w_lower:
               vocab_list.append({"word": w_lower, "meaning": basic_meaning})
       except: continue
   return vocab_list

# 🧠 AI 智能出題核心 (免費 API)
def generate_cloze_sentences(vocabs):
    target_words_str = ",".join([v["word"] for v in vocabs])
    # 使用 Pollinations AI 生成新句子與選項
    prompt = f"For each word in [{target_words_str}], generate 1 new simple English sentence replacing the word with '_______'. Also provide 3 distractors. Respond ONLY in JSON: [{{\"target_word\":\"word\",\"new_sentence\":\"...\",\"distractors\":[\"a\",\"b\",\"c\"]}}]"
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        with urllib.request.urlopen(url, timeout=10) as response:
            ai_reply = response.read().decode('utf-8')
            clean_json = re.sub(r'^```json\s*|\s*```$', '', ai_reply, flags=re.MULTILINE).strip()
            return json.loads(clean_json)
    except:
        # 備援方案
        return [{"target_word": v["word"], "new_sentence": f"It is important to _______ every day.", "distractors": ["ignore", "forget", "stop"], "meaning": v["meaning"]} for v in vocabs]

# --- 🚀 網頁精美視覺設計 (CSS) ---
st.markdown("""
  <style>
  #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
  .stApp { background-color: #F8FAFC; }
  .author-logo { position: absolute; top: -15px; left: 0px; font-size: 12px; font-weight: 700; color: #1E4ED8; background-color: #EFF6FF; padding: 5px 12px; border-radius: 8px; border: 2px solid #BFDBFE; z-index: 999; }
  .app-header { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); padding: 30px; border-radius: 20px; text-align: center; color: white; margin-bottom: 25px; }
  .main-title { font-size: 38px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0px !important; }
  .stTextArea textarea { border: 6px solid #000000 !important; border-radius: 14px !important; font-size: 20px !important; }
  .stButton button { font-size: 24px !important; font-weight: 800 !important; padding: 14px 28px !important; border-radius: 12px !important; background-color: #FF9800 !important; color: white !important; }
  .sentence-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; }
  .chinese-text { font-size: 20px; color: #475569; background-color: #F1F5F9; padding: 10px; border-radius: 8px; }
  .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 16px; margin-top: 10px; }
  .vocab-tag { display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px; font-weight: bold; margin: 4px; border: 1px solid #FFE0B2; }
  
  /* 🟩 綠色按鈕樣式 */
  .quiz-link-btn {
      display: block; text-align: center; width: 100%; padding: 12px;
      background-color: #10B981 !important; color: white !important;
      font-size: 18px !important; font-weight: bold !important; border-radius: 10px !important;
      text-decoration: none !important; margin-top: 15px;
      box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
  }
  .quiz-link-btn:hover { background-color: #059669 !important; }
  
  .quiz-page-card { background-color: white; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
  </style>
""", unsafe_allow_html=True)

# 🌐 路由邏輯：判斷是否為測驗頁
query_params = st.query_params

# ==========================================
# ─── 🚪 【模式 A：獨立測驗分頁框】 ───
# ==========================================
if "quiz_vocabs" in query_params:
    st.markdown("<div style='text-align: center;'><h2>📝 Contextual Cloze Quiz</h2></div>", unsafe_allow_html=True)
    try:
        raw_vocabs = json.loads(urllib.parse.unquote(query_params["quiz_vocabs"]))
        if "quiz_data" not in st.session_state:
            with st.spinner("⚡ AI 正在為您生成全新題目..."):
                st.session_state.quiz_data = generate_cloze_sentences(raw_vocabs)
        
        for idx, item in enumerate(st.session_state.quiz_data):
            st.markdown(f'<div class="quiz-page-card"><strong>Question {idx+1}:</strong><br><span style="font-size:20px;">{item["new_sentence"]}</span></div>', unsafe_allow_html=True)
            options = sorted([item["target_word"]] + item["distractors"])
            st.radio(f"Select for Q{idx+1}:", options, key=f"quiz_{idx}")
        
        if st.button("Submit Quiz"): st.balloons()
    except:
        st.error("無法讀取單字數據，請返回主頁。")
    st.stop()

# ==========================================
# ─── 📖 【模式 B：閱讀主網頁】 ───
# ==========================================
st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)
st.markdown('<div class="app-header"><p class="main-title">📱Smart Reading</p></div>', unsafe_allow_html=True)
st.markdown('<span class="input-disclaimer">Powered by Google Translate. Content is for reference only.</span>', unsafe_allow_html=True)

text_input = st.text_area("", height=180, placeholder="Enter English text here...")

if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
   if text_input.strip():
      sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
      st.success(f"🎉 Awesome! We found {len(sentences)} sentences for you.")
      
      for i, sentence in enumerate(sentences):
          full_sentence = sentence + "."
          translated = translate_text(full_sentence)
          sentence_vocabs = extract_fast_contextual_vocab(full_sentence, translated)
          
          st.markdown(f'<div class="sentence-card"><div class="english-text">{full_sentence}</div><div class="chinese-text">💡 {translated}</div></div>', unsafe_allow_html=True)
          
          try:
              tts = gTTS(text=full_sentence, lang='en')
              fp = io.BytesIO()
              tts.write_to_fp(fp)
              fp.seek(0)
              st.audio(fp, format="audio/mp3")
          except: pass
          
          if sentence_vocabs:
              with st.expander("🔑 Vocabulary "):
                  vocab_html = '<div class="vocab-box">'
                  for item in sentence_vocabs:
                      vocab_html += f'<span class="vocab-tag">📌 {item["word"]}：{item["meaning"]}</span>'
                  vocab_html += '</div>'
                  st.markdown(vocab_html, unsafe_allow_html=True)
                  
                  # 🔗 生成綠色按鈕連結
                  vocabs_json = json.dumps(sentence_vocabs)
                  encoded_data = urllib.parse.quote(vocabs_json)
                  quiz_url = f"?quiz_vocabs={encoded_data}"
                  
                  st.markdown(f'<a href="{quiz_url}" target="_blank" class="quiz-link-btn">📝 Enter Cloze Quiz (New Tab)</a>', unsafe_allow_html=True)
   else:
      st.warning("Please enter some English sentences first!")
