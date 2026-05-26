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

# 🎯 升級版句內生字提取（完美過濾所有縮寫詞）
def extract_sentence_vocab(sentence_text):
    # 💡 核心修改：切分單字時，先保留撇號 ' 以便識別縮寫詞，清除其他標點符號
    clean_text = re.sub(r"[^\w\s']", '', sentence_text)
    words = clean_text.split()
    
    # 基礎高頻虛詞過濾庫
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
        w_lower = word.lower()
        
        # 🚫 終極防禦：如果單字包含撇號 `'`（代表它是縮寫詞，如 they'd, don't, i'm），直接略過！
        if "'" in w_lower:
            continue
            
        # 排除過短字、高頻字、包含純數字以及重複出現的字
        if len(w_lower) < 3 or w_lower in ignore_words or not w_lower.isalpha() or w_lower in seen_words:
            continue
            
        seen_words.add(w_lower)
        
        # 翻譯核心生字
        chinese_meaning = translate_text(w_lower)
        
        # 避免無效翻譯干擾
        if chinese_meaning.lower() == w_lower:
            continue
            
        vocab_list.append({"word": w_lower, "meaning": chinese_meaning})
        
    return vocab_list


# --- 🚀 網頁精美視覺設計 (CSS) 🚀 ---
st.markdown("""
   <style>
   #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
   .stAppDeployButton {display: none !important;} div[data-testid="stDecoration"] {display: none !important;}
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
       background-color: #FFFFFF; padding: 24px; border-radius
