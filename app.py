import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io

# 🎯 Web Configuration
st.set_page_config(
    page_title="Smart Reading Buddy",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 官方輕量翻譯函數（用於句子與單字翻譯）
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "無法取得翻譯"

# 🎯 輕量化句內生字過濾與詞性猜測
def extract_sentence_vocab(sentence_text):
    clean_text = re.sub(r'[^\w\s]', '', sentence_text)
    words = clean_text.split()
    
    # 排除常見基礎字
    ignore_words = {
        'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with', 'and', 'but', 
        'or', 'so', 'because', 'if', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 
        'these', 'those', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'
    }
    
    vocab_list = []
    seen_words = set()
    
    for word in words:
        w_lower = word.lower()
        if len(w_lower) < 2 or w_lower in ignore_words or not w_lower.isalpha() or w_lower in seen_words:
            continue
            
        seen_words.add(w_lower)
        
        # 詞性智能判斷
        if w_lower.endswith('ly'):
            pos = "adv."
        elif w_lower.endswith(('tion', 'ness', 'ment', 'ity', 'ship', 'er', 'or', 'ist')):
            pos = "n."
        elif w_lower.endswith(('ful', 'less', 'able', 'ible', 'ive', 'ous', 'ish', 'al')):
            pos = "adj."
        elif w_lower.endswith(('ize', 'ify', 'ate')):
            pos = "v."
        elif w_lower.endswith(('ed', 'ing')):
            pos = "v./adj."
        else:
            pos = "w."
            
        chinese_meaning = translate_text(w_lower)
        if chinese_meaning.lower() == w_lower:
            continue
            
        vocab_list.append({"word": w_lower, "pos": pos, "meaning": chinese_meaning})
        
    return vocab_list


# --- 🚀 網頁精美視覺設計 (CSS) 🚀 ---
st.markdown("""
   <style>
   #MainMenu {visibility: hidden;}
   footer {visibility: hidden;}
   header {visibility: hidden;}
   .stAppDeployButton {display: none !important;}
   div[data-testid="stDecoration"] {display: none !important;}
 
   .stApp {
       background-color: #F8FAFC;
   }
    
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
   .main-title { font-size: 38
