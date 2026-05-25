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
    
    /* 提示文字樣式：字體再加粗 */
    .input-label {
        font-size: 22px !important;
        font-weight: 900 !important;
        color: #000000 !important;
        margin-bottom: 5px !important;
    }

    /* 🎯 專屬修改：放在輸入框下方的聲明樣式 */
    .input-disclaimer {
        font-size: 14px !important;
        color: #64748B !important;    /* 優雅的灰藍色，既清晰又不會太刺眼 */
        font-style: italic;          /* 斜體設計，增加提示感 */
        margin-bottom: 12px !important;
        display: block;
    }

    /* 輸入框：6 像素純黑超粗邊框 */
    .stTextArea textarea {
        border: 6px solid #000000 !important;  
        border-radius: 14px !important;       
        background-color: #FFFFFF !important;  
        font-size: 20px !important;            
        color: #000000 !important;
        font-weight: 500 !important;
    }
    .stTextArea textarea:focus {
        border-color: #1D4ED8 !important;     
        box-shadow: 0 0 0 4px rgba(29, 78, 216, 0.4) !important;
    }
    
    /* START 按鈕的字體和外觀大幅放大加粗 */
    .stButton button {
        font-size: 24px !important;           
        font-weight: 800 !important;           
        padding: 14px 28px !important;         
        border-radius: 12px !important;        
        background-color: #FF9800 !important;  
        color: #FFFFFF !important;             
        border
