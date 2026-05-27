import streamlit as st
import urllib.parse
import json
import urllib.request
import re
import random

st.set_page_config(page_title="Smart Reading Buddy", layout="centered", initial_sidebar_state="collapsed")

# 🚀 輕量高效翻譯核心
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except: return "翻譯失敗"

# 🧠 AI 出題核心 (修正 JSON 解析問題)
def generate_cloze_sentences_free(vocabs):
    target_words_str = ",".join([v["word"] for v in vocabs])
    prompt = f"For words [{target_words_str}], generate 1 new sentence each replacing the word with '_______'. Provide 3 distinct distractors. Return ONLY a JSON list of objects: [{{'target_word':'word','new_sentence':'...','distractors':['a','b','c']}}]."
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        with urllib.request.urlopen(url, timeout=12) as response:
            ai_reply = response.read().decode('utf-8').strip()
            # 關鍵修正：確保移除所有非 JSON 的 Markdown 符號
            clean_json = re.sub(r'^```json\s*|\s*```$', '', ai_reply, flags=re.MULTILINE).strip()
            return json.loads(clean_json)
    except:
        return [{"target_word": v["word"], "new_sentence": "The _______ is important.", "distractors": ["demo", "test", "idea"]} for v in vocabs]

# --- 路由邏輯 ---
query_params = st.query_params

if "quiz_vocabs" in query_params:
    st.markdown("## 📝 Contextual Cloze Quiz")
    try:
        # 正確解碼網址參數
        vocabs = json.loads(urllib.parse.unquote(query_params["quiz_vocabs"]))
        
        # 使用唯一 key 確保每次進入此頁面都觸發 AI 生成
        if "quiz_data" not in st.session_state:
            with st.spinner("AI 正在生成全新題目..."):
                st.session_state.quiz_data = generate_cloze_sentences_free(vocabs)
        
        for i, q in enumerate(st.session_state.quiz_data):
            st.markdown(f'<div class="quiz-page-card"><strong>Q{i+1}:</strong> {q["new_sentence"]}</div>', unsafe_allow_html=True)
            st.radio(f"Select:", sorted([q["target_word"]] + q["distractors"]), key=f"r{i}")
    except:
        st.error("參數讀取失敗，請返回主頁。")
    st.stop() # 嚴格隔離主頁面與測驗頁

# --- 主程式頁面 ---
st.markdown('<div class="app-header"><h1>📱 Smart Reading</h1></div>', unsafe_allow_html=True)
text_input = st.text_area("Paste text here:", height=150)

if st.button("🚀 Start Analysis"):
    st.session_state.processed_text = text_input
    if "quiz_data" in st.session_state: del st.session_state.quiz_data # 清除舊題目

if "processed_text" in st.session_state:
    sentences = [s.strip() + "." for s in st.session_state.processed_text.replace('?', '.').split('.') if s.strip()]
    for i, s in enumerate(sentences):
        trans = translate_text(s)
        # 顯示句子與翻譯... (省略你的原有顯示邏輯)
        # 修正 URL 生成：使用 urllib.parse.quote 確保特殊字元不會炸掉連結
        encoded = urllib.parse.quote(json.dumps([{"word": "example"}])) # 請接回你的 vocabs
        st.markdown(f'<a href="?quiz_vocabs={encoded}" target="_blank" class="quiz-link-btn">📝 Open Quiz</a>', unsafe_allow_html=True)
