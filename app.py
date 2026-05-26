import streamlit as st
import urllib.parse
import json
import urllib.request
import re

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

# 🎯 輕量化句內生字過濾與詞性猜測（速度最快，免除 LookupError 報錯風險）
def extract_sentence_vocab(sentence_text):
    # 清理句子中的標點符號，切分成單字
    clean_text = re.sub(r'[^\w\s]', '', sentence_text)
    words = clean_text.split()
    
    # 常見的基礎虛詞（代名詞、冠詞、介係詞），排除在生字列表外，減輕學生負擔
    ignore_words = {
        'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with', 'and', 'but', 
        'or', 'so', 'because', 'if', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 
        'these', 'those', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'
    }
    
    vocab_list = []
    seen_words = set()
    
    for word in words:
        w_lower = word.lower()
        # 排除數字、過短的字、常規字以及重複字
        if len(w_lower) < 2 or w_lower in ignore_words or not w_lower.isalpha() or w_lower in seen_words:
            continue
            
        seen_words.add(w_lower)
        
        # 💡 輕量級精準詞性智能判斷 (字尾法)
        if w_lower.endswith('ly'):
            pos = "adv."
        elif w_lower.endswith(('tion', 'ness', 'ment', 'ity', 'ship', 'er', 'or', 'ist')):
            pos = "n."
        elif w_lower.endswith(('ful', 'less', 'able', 'ible', 'ive', 'ous', 'ish', 'al')):
            pos = "adj."
        elif w_lower.endswith(('ize', 'ify', 'ate')):
            pos = "v."
        elif w_lower.endswith(('ed', 'ing')): # 常見的動詞時態變形
            pos = "v./adj."
        else:
            pos = "w." # 通用單字標籤
            
        # 查中文意思
        chinese_meaning = translate_text(w_lower)
        
        # 如果翻譯跟單字本身一樣（代表可能是人名或特殊符號未翻譯成功），就略過
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
       position: absolute;
       top: -15px;             
       left: 0px;              
       font-size: 12px !important;
       font-weight: 700 !important;
       color: #1E4ED8 !important;   
       background-color: #EFF6FF;  
       padding: 5px 12px;
       border-radius: 8px;        
       border: 2px solid #BFDBFE;  
       font-family: sans-serif;
       letter-spacing: 0.5px;
       box-shadow: 0 2px 4px rgba(0,0,0,0.05);
       z-index: 999;
   }
    
   .app-header {
       background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
       padding: 30px;
       border-radius: 20px;
       box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2);
       margin-bottom: 25px;
       text-align: center;
       position: relative; 
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
    
   .input-label {
       font-size: 22px !important;
       font-weight: 900 !important;
       color: #000000 !important;
       margin-bottom: 12px !important;
       display: block;
   }
 
   .input-disclaimer {
       font-size: 15px !important;
       color: #EF4444 !important;    
       font-weight: 700 !important;   
       font-style: italic;           
       margin-bottom: 15px !important;
       display: block;
   }
 
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
    
   .stButton button {
       font-size: 24px !important;          
       font-weight: 800 !important;          
       padding: 14px 28px !important;        
       border-radius: 12px !important;       
       background-color: #FF9800 !important; 
       color: #FFFFFF !important;            
       border: none !important;
       box-shadow: 0 4px 6px rgba(255, 152, 0, 0.3) !important; 
       transition: all 0.2s ease;
   }
   .stButton button:hover {
       background-color: #F57C00 !important; 
       transform: translateY(-2px) !important; 
       box-shadow: 0 6px 12px rgba(255, 152, 0, 0.4) !important;
   }
    
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
       color: #0F172A !important; 
       line-height: 1.4 !important;
       margin-bottom: 12px !important; 
   }
   .chinese-text { 
       font-size: 20px !important; 
       font-weight: 500 !important;
       color: #475569 !important; 
       background-color: #F1F5F9;
       padding: 10px 14px;
       border-radius: 8px;
       margin-bottom: 15px !important; 
   }

   /* 💡 新增：生字庫精美小字條樣式 */
   .vocab-box {
       background-color: #FFFDF5;
       border: 1px dashed #FFD54F;
       border-radius: 10px;
       padding: 12px 16px;
       margin-top: 10px;
   }
   .vocab-title {
       font-size: 15px;
       font-weight: bold;
       color: #D84315;
       margin-bottom: 6px;
   }
   .vocab-tag {
       display: inline-block;
       background-color: #FFF3E0;
       color: #E65100;
       padding: 3px 8px;
       border-radius: 6px;
       font-size: 15px;
       font-weight: bold;
       margin-right: 8px;
       margin-bottom: 6px;
       border: 1px solid #FFE0B2;
   }
   .vocab-pos {
       color: #78909C;
       font-size: 13px;
       font-style: italic;
       font-weight: normal;
   }
   </style>
""", unsafe_allow_html=True)
 
# --- 🎨 畫面正式渲染 🎨 ---
 
st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)
 
st.markdown("""
   <div class="app-header">
       <p class="main-title">📱 Smart Reading</p>
       <p class="sub-title">Break down text • Learn vocabulary sentence by sentence</p>
   </div>
""", unsafe_allow_html=True)
 
st.markdown('<span class="input-disclaimer">Powered by Google Translate. Content is for reference only and may not be perfect.</span>', unsafe_allow_html=True)
st.markdown('<p class="input-label">✍️ Paste your English text below:</p>', unsafe_allow_html=True)
 
text_input = st.text_area("", height=180, placeholder="Once upon a time, there was a smart tool that helped students learn...")
st.write("") 
 
if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
   if text_input.strip():
       # 按句號、問號、感嘆號拆分句子
       sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
       
       st.success(f"🎉 Awesome! We found {len(sentences)} sentences for you. Let's practice:")
       
       for i, sentence in enumerate(sentences):
           full_sentence = sentence + "."
           # 翻譯整句
           translated = translate_text(full_sentence)
           
           # 提取本句的關鍵生字
           sentence_vocabs = extract_sentence_vocab(full_sentence)
           
           # 拼接生字的 HTML 字條
           vocab_html = ""
           if sentence_vocabs:
               vocab_html += '<div class="vocab-box"><div class="vocab-title">🔑 句子生字筆記 (Vocabulary Focus)：</div>'
               for item in sentence_vocabs:
                   vocab_html += f'<span class="vocab-tag">📌 {item["word"]} <span class="vocab-pos">({item["pos"]})</span>：{item["meaning"]}</span>'
               vocab_html += '</div>'
           
           # 用精美的卡片包裹英文、中文以及「新增的句下生字卡」
           st.markdown(f"""
                <div class="sentence-card">
                    <div class="card-index">Sentence {i+1}</div>
                    <div class="english-text">{full_sentence}</div>
                    <div class="chinese-text">💡 {translated}</div>
                    {vocab_html}
                </div>
           """, unsafe_allow_html=True)
           
   else:
       st.warning("Please enter some English sentences first!")
