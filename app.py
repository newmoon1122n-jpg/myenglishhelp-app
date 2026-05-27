import streamlit as st
import urllib.parse
import json
import urllib.request
import re

# 🎯 設定頁面 (確保沒有斷行)
st.set_page_config(page_title="Smart Reading Buddy", layout="centered", initial_sidebar_state="collapsed")

# --- 核心出題函數 ---
def generate_cloze_sentences_free(vocabs):
    # 確保每個單字都生成全新的語境
    target_words = ",".join([v["word"] for v in vocabs])
    prompt = f"Generate 1 unique English sentence for: {target_words}. Replace the word with '_______'. Provide 3 distractors. Output JSON: [{{'target_word':'word','new_sentence':'...','distractors':['a','b','c']}}]"
    
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        with urllib.request.urlopen(url, timeout=10) as response:
            res = response.read().decode('utf-8')
            clean = re.sub(r'^```json\s*|\s*```$', '', res, flags=re.MULTILINE).strip()
            return json.loads(clean)
    except:
        return [{"target_word": v["word"], "new_sentence": "This is a test for _______.", "distractors": ["a", "b", "c"]} for v in vocabs]

# --- 路由邏輯：這裡是最重要的 ---
query_params = st.query_params

# 如果網址有參數，強制顯示測驗頁，不顯示主頁
if "quiz_vocabs" in query_params:
    st.title("📝 Cloze Quiz")
    try:
        # 強制解碼
        raw_val = query_params["quiz_vocabs"]
        vocabs = json.loads(urllib.parse.unquote(raw_val))
        
        # 強制重新產生題目，不依賴過往狀態
        data = generate_cloze_sentences_free(vocabs)
        
        for i, q in enumerate(data):
            st.write(f"**Q{i+1}:** {q['new_sentence']}")
            options = sorted([q["target_word"]] + q["distractors"])
            st.radio(f"Select option {i+1}:", options, key=f"q{i}")
    except Exception as e:
        st.error(f"題目讀取失敗: {e}")
    
    st.stop() # 關鍵：這行會切斷後續主頁代碼執行，確保頁面乾淨

# --- 主頁代碼 ---
st.title("📱 Smart Reading")
text = st.text_area("Enter text:")
if st.button("Start"):
    st.session_state.text = text

if "text" in st.session_state:
    # 假設這就是你的單字列表邏輯
    vocabs = [{"word": "apple"}, {"word": "banana"}]
    # 產生連結時，確保參數是編碼過的
    encoded = urllib.parse.quote(json.dumps(vocabs))
    st.markdown(f'<a href="?quiz_vocabs={encoded}" target="_blank">點擊開啟測驗</a>', unsafe_allow_html=True)
