import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request

# Official lightweight translation function
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "Translation temporarily unavailable, please try again!"

# --- 🚀 網頁精美視覺設計 (CSS) 🚀 ---
st.markdown("""
    <style>
    /* 全局背景與字體優化 */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 大標題設計：漸層色彩、陰影與生動圖示 */
    .app-header {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2);
        margin-bottom: 30px;
        text-align: center;
    }
    .main-title { 
        font-size: 38px !important; 
        font-weight: 800 !important; 
        color: #FFFFFF !important; 
        margin: 0px !important;
        letter-spacing: 1px;
    }
    .sub-title {
        font-size: 16px !important;
        color: #E0F2FE !important;
        margin-top: 8px !important;
        opacity: 0.9;
    }
    
    /* 提示文字樣式 */
    .input-label {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        margin-bottom: 10px;
    }

    /* 🎯 核心修改：把 Streamlit 預設的輸入框強行改成黑粗框 */
    .stTextArea textarea {
        border: 3px solid #000000 !important;  /* 3像素純黑超粗邊框 */
        border-radius: 12px !important;       /* 保持漂亮的圓角 */
        background-color: #FFFFFF !important;  /* 保持背景純白 */
        font-size: 18px !important;            /* 裡面打字的字體加大 */
        color: #000000 !important;
    }
    
    /* 當學生用滑鼠點擊輸入框時，邊框變色並加強發光，提醒效果
