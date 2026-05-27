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

# 🚀 核心功能：翻譯與生字提取
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception: 
        return "無法取得翻譯"

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
            meaning = translate_text(w_lower)
            if meaning.lower() != w_lower: 
                vocab_list.append({"word": w_lower, "meaning": meaning})
        except: 
            continue
    return vocab_list

# 🧠 AI 出題核心 (修正 JSON 清洗邏輯)
def generate_cloze_sentences_free(vocabs):
    target_words_str = ",".join([v["word"] for v in vocabs])
    base_distractors = ["challenge", "explore", "journey", "knowledge", "practice", "wisdom", "advance", "creative", "imagine", "observe"]
    prompt = f"For each word in [{target_words_str}], generate 1 new simple English sentence replacing the word with '_______'. Provide 3 distinct distractors. Respond ONLY in JSON: [{{\"target_word\":\"word\",\"new_sentence\":\"...\",\"distractors\":[\"a\",\"b\",\"c\"]}}]"
    
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        with urllib.request.urlopen(url, timeout=12) as response:
            raw_data = response.read().decode('utf-8')
            # 關鍵修正：確保移除所有 Markdown 標記，強制 JSON 格式
            clean_json = re.sub(r'^```json\s*|\s*```$', '', raw_data, flags=re.MULTILINE).strip()
            return json.loads(clean_json)
    except: 
        return [{"target_word": v["word"], "new_sentence": f"We need to _______ more.", "meaning": v.get("meaning", ""), "distractors": random.sample(base_distractors, 3)} for v in vocabs]

# --- 🎨 CSS 樣式 ---
st.markdown("""
<style>
.app-header { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); padding: 30px; border-radius: 20px; text-align: center; color: white; margin-bottom: 25px; }
.stButton button { background-color: #FF9800 !important; color: white !important; font-weight: 800 !important; border-radius: 12px !important; }
.sentence-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
.vocab-tag { display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px; font-weight: bold; margin: 4px; border: 1px solid #FFE0B2; }
.quiz-link-btn { display: block; text-align: center; padding: 12px; background-color: #10B981 !important; color: white !important; font-weight: bold; border-radius: 10px; text-decoration: none; }
.quiz-page-card { background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 路由邏輯 ---
query_params = st.query_params

# 📝 獨立測驗分頁
if "quiz_vocabs" in query_params:
    st.markdown("## 📝 Contextual Cloze Quiz")
    try:
        # 解碼參數
        vocabs = json.loads(urllib.parse.unquote(query_params["quiz_vocabs"]))
        # 每次打開網頁都觸發 AI 生成 (移除 session_state 限制以確保每次都是新的)
        quiz_data = generate_cloze_sentences_free(vocabs)
        
        for i, q in enumerate(quiz_data):
            st.markdown(f'<div class="quiz-page-card"><strong>Q{i+1}:</strong> {q["new_sentence"]}</div>', unsafe_allow_html=True)
            st.radio(f"Select:", sorted([q["target_word"]] + q["distractors"]), key=f"r{i}")
    except Exception as e:
        st.error(f"題目載入失敗: {e}")
    st.stop() # 強制停止，確保不顯示主程式頁面

# --- 主程式頁面 ---
st.markdown('<div class="app-header"><h1>📱 Smart Reading</h1></div>', unsafe_allow_html=True)
text_input = st.text_area("", height=180, placeholder="Enter English text here...")

if st.button("🚀 Start Audio & Reading Analysis"):
    st.session_state.processed_text = text_input

if "processed_text" in st.session_state:
    sentences = [s.strip() + "." for s in st.session_state.processed_text.replace('?', '.').replace('!', '.').split('.') if s.strip()]
    for i, s in enumerate(sentences):
        trans = translate_text(s)
        vocabs = extract_fast_contextual_vocab(s, trans)
        st.markdown(f'<div class="sentence-card"><strong>Sentence {i+1}</strong><br>{s}<br><small>💡 {trans}</small></div>', unsafe_allow_html=True)
        if vocabs:
            with st.expander("🔑 Vocabulary"):
                st.markdown("".join([f'<span class="vocab-tag">📌 {v["word"]}</span>' for v in vocabs]), unsafe_allow_html=True)
                encoded = urllib.parse.quote(json.dumps(vocabs))
                st.markdown(f'<a href="?quiz_vocabs={encoded}" target="_blank" class="quiz-link-btn">📝 Open Cloze Quiz</a>', unsafe_allow_html=True)
