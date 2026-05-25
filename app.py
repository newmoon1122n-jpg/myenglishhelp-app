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
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        margin-bottom: 10px;
    }
    
    /* 每一句英文卡片的精美設計 */
    .sentence-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-top: 20px;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .sentence-card:hover {
        transform: translateY(-2px);
    }
    
    /* 卡片內文字樣式：特大字體與清晰行距 */
    .card-index {
        font-size: 14px !important;
        font-weight: bold !important;
        color: #3B82F6 !important;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .english-text { 
        font-size: 26px !important; 
        font-weight: 600 !important; 
        color:
