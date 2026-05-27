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

# 🧠 AI 出題核心
def generate_cloze_sentences(vocabs):
    target_words_str = ",".join([v["word"] for v in vocabs])
    prompt = f"For each word in [{target_words_str}], generate 1 new simple English sentence replacing the word with '_______'. Provide 3 distractors. Respond ONLY in JSON: [{{\"target_word\":\"word\",\"new_sentence\":\"...\",\"distractors\":[\"a\",\"b\",\"c\"]}}]"
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(re.sub(r'^```json\s*|\s*```$', '', response.read().decode('utf-8'), flags=re.MULTILINE).strip())
    except:
        return [{"target_word": v["word"], "new_sentence": f"We need to _______ more.", "distractors": ["try", "work", "learn"], "meaning": v["meaning"]} for v in vocabs]

# --- 🎨 CSS 樣式 (保留您的橙色設計) ---
st.markdown("""
  <style>
  #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
  .stApp { background-color: #F8FAFC; }
  .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; margin-top: 5px; margin-bottom: 10px; }
  .vocab-tag { display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px; font-size: 15px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; border: 1px solid #FFE0B2; }
  .stExpander summary { font-size: 16px !important; font-weight: bold !important; color: #D84315 !important; background-color: #FFFDE5 !important; border-radius: 8px !important; padding: 10px !important; }
  
  /* 🟩 新增的綠色測驗按鈕樣式 */
  .quiz-link-btn { display: block; text-align: center; padding: 12px; background-color: #10B981 !important; color: white !important; font-weight: bold; border-radius: 10px; text-decoration
