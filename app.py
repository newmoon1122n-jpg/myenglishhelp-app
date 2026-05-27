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

# 🧠 AI 智能出題核心：修正了 JSON 解析邏輯
def generate_cloze_sentences_free(vocabs):
    target_words_str = ",".join([v["word"] for v in vocabs])
    prompt = f"For words [{target_words_str}], generate 1 new sentence each replacing the word with '_______'. Provide 3 distinct distractors. Return ONLY a JSON list of objects: [{{'target_word':'word','new_sentence':'...','distractors':['a','b','c']}}]. No extra text."
    
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as response:
            ai_reply = response.read().decode('utf-8').strip()
            # 關鍵修正：確保移除 markdown 符號，讓 json.loads 能順利執行
            clean_json_str = re.sub(r'^```json\s*|\s*```$', '', ai_reply, flags=re.MULTILINE).strip()
            return json.loads(clean_json_str)
    except:
        return [{"target_word": v["word"], "new_sentence": "The _______ is important.", "distractors": ["idea", "system", "change"]} for v in vocabs]

# --- CSS 視覺設計 ---
st.markdown("""<style>
    .quiz-page-card { background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    .stApp { background-color: #F8FAFC; }
    .quiz-link-btn { display: inline-block; text-align: center; width: 100%; padding: 12px; background-color: #10B981 !important; color: white !important; font-weight: bold !important; border-radius: 10px !important; text-decoration: none !important; }
</style>""", unsafe_allow_html=True)

# 🌐 獲取 URL 參數 (關鍵修正)
query_params = st.query_params

# ==========================================
# ─── 模式 A：獨立測驗分頁 ───
# ==========================================
if "quiz_vocabs" in query_params:
    st.title("📝 Contextual Cloze Quiz")
    
    # 讀取參數並解析
    try:
        vocabs_list = json.loads(urllib.parse.unquote(query_params["quiz_vocabs"]))
        
        # 使用 session_state 緩存生成的題目，避免刷新時重複請求 AI
        if "session_quiz_data" not in st.session_state:
            with st.spinner("AI 正在生成題目..."):
                st.session_state.session_quiz_data = generate_cloze_sentences_free(vocabs_list)
        
        for idx, item in enumerate(st.session_state.session_quiz_data):
            st.markdown(f'<div class="quiz-page-card"><strong>Q{idx+1}:</strong> {item["new_sentence"]}</div>', unsafe_allow_html=True)
            options = sorted([item["target_word"]] + item["distractors"])
            st.radio(f"Select option {idx+1}:", options, key=f"rad_{idx}")
        
        if st.button("完成練習"):
            st.success("練習完成！")
            
    except Exception as e:
        st.error("無法載入題目，請返回主頁。")
    st.stop() # 確保測驗頁不會執行下方的主頁邏輯

# ==========================================
# ─── 模式 B：主閱讀頁面 ───
# ==========================================
st.title("📱 Smart Reading")
text_input = st.text_area("Enter English text:", key="main_input")

if st.button("Start Analysis"):
    st.session_state.text = text_input

if "text" in st.session_state and st.session_state.text:
    sentences = [s.strip() + "." for s in st.session_state.text.replace('?', '.').split('.') if s.strip()]
    for i, s in enumerate(sentences):
        st.write(f"**Sentence {i+1}:** {s}")
        # 簡易範例：這裡你需要一個簡單的單字提取邏輯
        vocabs = [{"word": "example", "meaning": "範例"}] # 這裡是為了示範，你可以接回你原本的提取邏輯
        
        # 傳遞參數到 URL
        encoded = urllib.parse.quote(json.dumps(vocabs))
        st.markdown(f'<a href="?quiz_vocabs={encoded}" target="_blank" class="quiz-link-btn">📝 Open Quiz</a>', unsafe_allow_html=True)
