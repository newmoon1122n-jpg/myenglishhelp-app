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
    
    /* 🎯 核心修改：將 MACAOMAMASUE 專屬簽名做成網頁 Logo，固定在左上角 */
    .author-logo {
        position: absolute;
        top: -15px;             /* 往上提，緊貼頂部 */
        left: 0px;              /* 靠最左邊 */
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #1E4ED8 !important;   /* 使用主題深藍色 */
        background-color: #EFF6FF;  /* 淡藍色底色 */
        padding: 5px 12px;
        border-radius: 8px;        /* 漂亮的現代感小圓角 */
        border: 2px solid #BFDBFE;  /* 藍色邊框 */
        font-family: sans-serif;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        z-index: 999;
    }
    
    /* 大標題設計：漸層色彩、陰影與生動圖示 */
    .app-header {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2);
        margin-bottom: 25px;
        text-align: center;
        position: relative; /* 讓左上角定位更精準 */
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
        font-size: 22px !important;
        font-weight: 900 !important;
        color: #000000 !important;
        margin-bottom: 12px !important;
        display: block;
    }

    /* 置頂紅色聲明的樣式 */
    .input-disclaimer {
        font-size: 15px !important;
        color: #EF4444 !important;    
        font-weight: 700 !important;   
        font-style: italic;           
        margin-bottom: 15px !important;
        display: block;
    }

    /* 輸入框：6 像素純黑超粗邊框 */
    .stTextArea textarea {
        border: 6px solid #000000 !important;  
        border-radius: 14px !important;       
        background-color: #FFFFFF !important;  
        font-size: 20px !important;
