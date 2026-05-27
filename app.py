import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io

# 🎯 Web 基礎配置
st.set_page_config(page_title="Smart Reading Buddy", layout="centered")

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
    vocab_list, seen_words = [], set()
    for word in words:
        w_lower = word.lower().strip('-')
        if "'" in w_lower or len(w_lower) < 3 or w_lower in ignore_words or w_lower in seen_words:
            continue
        if not re.match(r'^[a-z\-]+$', w_lower):
            continue
        seen_words.add(w_lower)
        try:
            raw_meaning = translate_text(w_lower)
            context_meaning = raw_meaning.split('(')[0].strip() if '(' in raw_meaning else raw_meaning.strip()
            
            if w_lower == "party":
                context_meaning = "政黨" if "政黨" in sentence_translation else "派對/聚會"
            elif w_lower == "spoke":
                context_meaning = "輻條" if "輻條" in sentence_translation else "說話 (speak的過去式)"
            
            if context_meaning.lower() == w_lower or not context_meaning:
                continue
            vocab_list.append({"word": w_lower, "meaning": context_meaning})
        except Exception:
            continue
    return vocab_list

# --- 🚀 CSS 視覺美化 ---
st.markdown("""
   <style>
   #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
   .stAppDeployButton {display: none !important;} div[data-testid="stDecoration"] {display: none !important;}
   .stApp { background-color: #F8FAFC; }
   .author-logo { position: absolute; top: -15px; left: 0px; font-size: 12px !important; font-weight: 700 !important; color: #1E4ED8 !important; background-color: #EFF6FF; padding: 5px 12px; border-radius: 8px; border: 2px solid #BFDBFE; z-index: 999; }
   .app-header { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); padding: 30px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2); margin-bottom: 25px; text-align: center; }
   .main-title { font-size: 38px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0px !important; }
   .sub-title { font-size: 16px !important; color: #E0F2FE !important; margin-top: 8px !important; }
   .input-label { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; margin-bottom: 12px !important; display: block; }
   .input-disclaimer { font-size: 15px !important; color: #EF4444 !important; font-weight: 700 !important; margin-bottom: 15px !important; display: block; }
   .stTextArea textarea { border: 6px solid #000000 !important; border-radius: 14px !important; font-size: 20px !important; }
   
   /* 專屬：抽屜內測試跳轉按鈕樣式 */
   .quiz-nav-btn button { background-color: #10B981 !important; color: white !important; font-size: 18px !important; font-weight: 700 !important; border-radius: 8px !important; width: 100% !important; border: none !important; margin-top: 10px; }
   
   .sentence-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; }
   .card-index { font-size: 14px !important; font-weight: bold !important; color: #3B82F6 !important; text-transform: uppercase; }
   .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; }
   .chinese-text { font-size: 20px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; }
   .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; }
   .vocab-tag { display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px; font-size: 15px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; }
   .stExpander { border: none !important; box-shadow: none !important; margin-bottom: 10px !important; }
   </style>
""", unsafe_allow_html=True)

# --- 🚀 多頁面路由管理核心 ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

# ─── 【頁面 A：閱讀主界面】 ───
if st.session_state.current_page == "main":
    st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-header"><p class="main-title">📱 Smart Reading</p><p class="sub-title">Break down text • Learn step by step</p></div>', unsafe_allow_html=True)
    st.markdown('<span class="input-disclaimer">Powered by Google Translate. Content is for reference only.</span>', unsafe_allow_html=True)
    st.markdown('<p class="input-label">✍️ Paste your English text below:</p>', unsafe_allow_html=True)
    
    # 利用 session_state 保持文字輸入框的內容
    if "input_text_val" not in st.session_state:
        st.session_state.input_text_val = ""
    text_input = st.text_area("", value=st.session_state.input_text_val, height=180, placeholder="Enter English text here...")
    st.session_state.input_text_val = text_input
    
    if "main_processed_data" not in st.session_state:
        st.session_state.main_processed_data = None

    if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
        if text_input.strip():
            clean_input = re.sub(r'^\d+\s+', '', text_input.strip())
            sentences = [s.strip() for s in clean_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
            
            results = []
            for i, sentence in enumerate(sentences):
                full_sentence = sentence + "."
                translated = translate_text(full_sentence)
                sentence_vocabs = extract_fast_contextual_vocab(full_sentence, translated)
                results.append({
                    "full_sentence": full_sentence,
                    "translated": translated,
                    "vocabs": sentence_vocabs
                })
            st.session_state.main_processed_data = results
        else:
            st.warning("Please enter some English sentences first!")

    if st.session_state.main_processed_data:
        st.success(f"🎉 Analysis completed successfully! Let's practice:")
        for i, data in enumerate(st.session_state.main_processed_data):
            st.markdown(f'<div class="sentence-card"><div class="card-index">Sentence {i+1}</div><div class="english-text">{data["full_sentence"]}</div><div class="chinese-text">💡 {data["translated"]}</div></div>', unsafe_allow_html=True)
            
            try:
                tts = gTTS(text=data["full_sentence"], lang='en', slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                st.audio(fp, format="audio/mp3")
            except Exception:
                pass
            
            if data["vocabs"]:
                with st.expander("🔑 Vocabulary"):
                    vocab_html = '<div class="vocab-box">'
                    for item in data["vocabs"]:
                        vocab_html += f'<span class="vocab-tag">📌 {item["word"]}：{item["meaning"]}</span>'
                    vocab_html += '</div>'
                    st.markdown(vocab_html, unsafe_allow_html=True)
                    
                    # 💡 重點新功能：將測驗按鈕安置在 Vocabulary 內部
                    st.markdown('<div class="quiz-nav-btn">', unsafe_allow_html=True)
                    if st.button(f"📝 Go to Cloze Quiz ({len(data['vocabs'])} Questions)", key=f"go_quiz_{i}"):
                        # 儲存此句資訊發送到測試頁
                        st.session_state.quiz_target_sentence = data["full_sentence"]
                        st.session_state.quiz_target_translation = data["translated"]
                        st.session_state.quiz_target_vocabs = data["vocabs"]
                        st.session_state.current_page = "quiz"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

# ─── 【頁面 B：獨立專屬測驗頁】 ───
elif st.session_state.current_page == "quiz":
    # 引入外部測驗腳本渲染
    import quiz
    quiz.render_quiz_page()
