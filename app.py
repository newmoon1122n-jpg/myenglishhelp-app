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
   
   ignore_words = {
       'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with', 'and', 'but', 
       'or', 'so', 'because', 'if', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 
       'these', 'those', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 
       'do', 'does', 'did', 'can', 'will', 'should', 'would', 'could', 'may', 'might', 'must',
       'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him', 'them', 'us'
    }
   
   vocab_list = []
   seen_words = set()
   
   for word in words:
       w_lower = word.lower().strip('-')
       
       if "'" in w_lower:
           continue
           
       if len(w_lower) < 3 or w_lower in ignore_words or w_lower in seen_words:
           continue
           
       if not re.match(r'^[a-z\-]+$', w_lower):
           continue
           
       seen_words.add(w_lower)
       
       try:
           basic_meaning = translate_text(w_lower)
           context_meaning = basic_meaning
           
           if w_lower == "party":
                if "政黨" in sentence_translation: context_meaning = "政黨"
                elif "派對" in sentence_translation or "聚會" in sentence_translation: context_meaning = "派對/聚會"
           
           elif w_lower == "spoke":
                if "輻條" in sentence_translation or "輪輻" in sentence_translation: context_meaning = "輻條"
                elif "說" in sentence_translation or "談" in sentence_translation: context_meaning = "說話 (speak的過去式)"
           
           elif "-" in w_lower and context_meaning.lower() == w_lower:
                continue
                
           if context_meaning.lower() == w_lower:
                continue
                
           vocab_list.append({"word": w_lower, "meaning": context_meaning})
       except Exception:
           continue
      
   return vocab_list


# --- 🚀 網頁精美視覺設計 (CSS) 🚀 ---
st.markdown("""
  <style>
  #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
  .stAppDeployButton {display: none !important;}
  div[data-testid="stDecoration"] {display: none !important;}
  .stApp { background-color: #F8FAFC; }
   
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
  .main-title { font-size: 38px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0px !important; letter-spacing: 1px; }
  .sub-title { font-size: 16px !important; color: #E0F2FE !important; margin-top: 8px !important; opacity: 0.9; }
  .input-label { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; margin-bottom: 12px !important; display: block; }
  .input-disclaimer { font-size: 15px !important; color: #EF4444 !important; font-weight: 700 !important; font-style: italic; margin-bottom: 15px !important; display: block; }

  .stTextArea textarea {
      border: 6px solid #000000 !important; border-radius: 14px !important;      
      background-color: #FFFFFF !important; font-size: 20px !important; color: #000000 !important; font-weight: 500 !important;
   }
   
  .stButton button {
      font-size: 24px !important; font-weight: 800 !important; padding: 14px 28px !important; border-radius: 12px !important;       
      background-color: #FF9800 !important; color: #FFFFFF !important; border: none !important;
      box-shadow: 0 4px 6px rgba(255, 152, 0, 0.3) !important;
   }
   
  .sentence-card {
      background-color: #FFFFFF; padding: 24px; border-radius: 16px;
      border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; margin-bottom: 5px;
   }
  .card-index { font-size: 14px !important; font-weight: bold !important; color: #3B82F6 !important; text-transform: uppercase; margin-bottom: 4px; }
  .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.4 !important; margin-bottom: 12px !important; }
  .chinese-text { font-size: 20px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; margin-bottom: 5px !important; }

  .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; margin-top: 5px; margin-bottom: 10px; }
  .vocab-tag {
      display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px;
      font-size: 15px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; border: 1px solid #FFE0B2;
   }
   
  .stExpander { border: none !important; box-shadow: none !important; margin-bottom: 20px !important; }
  .stExp
