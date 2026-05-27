import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io

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

# 🎯 高速語境生字提取
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
            meaning = translate_text(w_lower)
            if meaning.lower() != w_lower: vocab_list.append({"word": w_lower, "meaning": meaning})
        except: continue
    return vocab_list

# 🧠 Gemini AI 出題函數
def generate_cloze_quiz(vocabs):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return None
    
    target_words = ",".join([v["word"] for v in vocabs[:3]]) # 取前三個單字出題
    prompt = f"Create 3 simple English cloze test questions using these words: {target_words}. Each question should replace the target word with '_______'. Provide 3 wrong distractors for each. Return ONLY valid JSON format: [{{\"q\": \"The sentence with _______\", \"ans\": \"correct_word\", \"options\": [\"opt1\", \"opt2\", \"opt3\", \"opt4\"]}}]"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    req = urllib.request.Request(url, data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        # 清理 markdown 標記
        text = re.sub(r'```json|```', '', text).strip()
        return json.loads(text)

# --- 🎨 CSS ---
st.markdown("""
    <style>
    .app-header { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); padding: 30px; border-radius: 20px; text-align: center; color: white; margin-bottom: 25px; }
    .stButton button { background-color: #FF9800 !important; color: white !important; font-weight: 800 !important; }
    .green-btn { background-color: #10B981 !important; color: white !important; border-radius: 10px !important; padding: 10px !important; width: 100%; border: none !important; font-weight: bold !important; }
    .quiz-card { background: #F0FDF4; border: 2px solid #10B981; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 渲染 ---
st.markdown('<div class="app-header"><h1>📱 Smart Reading</h1></div>', unsafe_allow_html=True)
text_input = st.text_area("", height=180, placeholder="Enter English text here...")

if st.button("🚀 Start Audio & Reading Analysis"):
    sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
    for i, s in enumerate(sentences):
        full = s + "."
        trans = translate_text(full)
        vocabs = extract_fast_contextual_vocab(full, trans)
        
        st.markdown(f'<div class="sentence-card"><strong>{full}</strong><br><small>{trans}</small></div>', unsafe_allow_html=True)
        
        # 綠色 Cloze Quiz 按鈕
        if vocabs:
            quiz_key = f"quiz_{i}"
            if st.button("📝 Open Cloze Quiz", key=quiz_key):
                st.session_state[quiz_key] = generate_cloze_quiz(vocabs)
            
            if quiz_key in st.session_state and st.session_state[quiz_key]:
                for q in st.session_state[quiz_key]:
                    st.markdown(f'<div class="quiz-card">{q["q"]}</div>', unsafe_allow_html=True)
                    st.radio("Select:", q["options"], key=q["q"])
