import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io
import random

# 🎯 Web Configuration
st.set_page_config(page_title="Smart Reading Buddy", layout="centered")

# --- 核心工具 ---
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except: return "無法取得翻譯"

def extract_fast_contextual_vocab(sentence_text, sentence_translation):
    clean_text = re.sub(r"[^\w\s'\-]", ' ', sentence_text)
    words = [w.lower().strip('-') for w in clean_text.split() if len(w) > 3]
    ignore_words = {'the', 'and', 'that', 'this', 'with', 'from', 'they', 'would', 'could', 'should'}
    vocab_list = []
    seen = set()
    for w in words:
        if w not in seen and w not in ignore_words and re.match(r'^[a-z]+$', w):
            seen.add(w)
            meaning = translate_text(w)
            vocab_list.append({"word": w, "meaning": meaning})
            if len(vocab_list) >= 5: break
    return vocab_list

def generate_cloze_sentences_free(vocabs):
    # 使用 Pollinations AI 進行出題
    target_words = ",".join([v["word"] for v in vocabs])
    prompt = f"Generate 1 simple English sentence for each of these words: {target_words}. Replace the word with '_______'. Provide 3 distinct distractors for each. Return ONLY JSON: [{{\"target_word\":\"word\",\"new_sentence\":\"...\",\"distractors\":[\"a\",\"b\",\"c\"]}}]"
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(re.sub(r'^```json\s*|\s*```$', '', response.read().decode('utf-8')))
    except:
        return [{"target_word": v["word"], "new_sentence": f"The _______ is important.", "distractors": ["test", "word", "idea"]} for v in vocabs]

# --- CSS ---
st.markdown("<style>.quiz-page-card{background:#FFF;padding:20px;border:2px solid #E2E8F0;border-radius:12px;margin-bottom:15px;}</style>", unsafe_allow_html=True)

# --- 路由邏輯 (關鍵修正) ---
query_params = st.query_params

if "quiz_vocabs" in query_params:
    st.title("📝 Contextual Cloze Quiz")
    vocabs_data = json.loads(urllib.parse.unquote(query_params["quiz_vocabs"]))
    
    # 初始化測驗資料
    if "quiz_questions" not in st.session_state:
        with st.spinner("AI 正在生成題目..."):
            st.session_state.quiz_questions = generate_cloze_sentences_free(vocabs_data)
    
    for i, q in enumerate(st.session_state.quiz_questions):
        st.markdown(f'<div class="quiz-page-card"><strong>Q{i+1}:</strong> {q["new_sentence"]}</div>', unsafe_allow_html=True)
        options = sorted([q["target_word"]] + q["distractors"])
        st.radio(f"Select option for blank {i+1}:", options, key=f"ans_{i}")
    
    if st.button("Submit Answers"):
        st.success("Check your understanding!")
    st.stop() # 停止執行主程式，僅顯示測驗頁

# --- 主程式區 ---
st.header("📱 Smart Reading")
text_input = st.text_area("Paste English text:", height=150)

if st.button("Start Analysis"):
    st.session_state.text = text_input

if "text" in st.session_state:
    sentences = [s.strip() + "." for s in st.session_state.text.replace('?', '.').split('.') if s.strip()]
    for i, s in enumerate(sentences):
        st.write(f"**Sentence {i+1}:** {s}")
        vocabs = extract_fast_contextual_vocab(s, "")
        if vocabs:
            encoded = urllib.parse.quote(json.dumps(vocabs))
            st.markdown(f'<a href="?quiz_vocabs={encoded}" target="_blank" style="padding:10px; background:#10B981; color:white; text-decoration:none; border-radius:8px;">📝 Open Quiz</a>', unsafe_allow_html=True)
