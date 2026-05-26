import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io

# 🚀 引入 NLTK 核心庫
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer

# 🎯 相容新版 Python 環境，完整下載所有必備大腦模型
@st.cache_resource
def initialize_nltk():
    required_packages = [
        'punkt', 'punkt_tab', 'averaged_perceptron_tagger', 
        'averaged_perceptron_tagger_eng', 'wordnet', 'omw-1.4'
    ]
    for package in required_packages:
        try:
            nltk.download(package, quiet=True)
        except Exception:
            pass

initialize_nltk()

# 🎯 Web Configuration
st.set_page_config(
    page_title="Smart Reading Buddy",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if "play_word_bytes" not in st.session_state:
    st.session_state.play_word_bytes = None
if "word_audio_cache" not in st.session_state:
    st.session_state.word_audio_cache = {}

# Official lightweight translation function
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "Translation temporarily unavailable..."

# 🎯 AI-Driven POS Classifier using NLTK
def advanced_extract_eight_pos(text):
    if not text.strip():
        return {k: [] for k in ["Noun", "Pronoun", "Verb", "Adjective", "Adverb", "Conjunction", "Interjection"]}, []

    phrase_patterns = r'\b(look after|look for|pick up|get up|run away|once upon a time|a lot of|depend on|laugh at|listen to|go to|set up|turn off|turn on|put on|take off)\b'
    phrases = sorted(list(set(re.findall(phrase_patterns, text.lower()))))
    
    tokens = word_tokenize(text)
    tagged_words = pos_tag(tokens)
    lemmatizer = WordNetLemmatizer()
    
    categories = {
        "Noun": set(), "Pronoun": set(), "Verb": set(), "Adjective": set(),
        "Adverb": set(), "Conjunction": set(), "Interjection": set()
    }
    ignore_words = {'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with'}

    for word, tag in tagged_words:
        w_lower = word.lower()
        if len(w_lower) < 2 or w_lower in ignore_words or not w_lower.isalpha():
            continue
            
        if tag.startswith('NN'):
            if tag == 'NNP' or tag == 'NNPS': continue
            categories["Noun"].add(lemmatizer.lemmatize(w_lower, pos='n'))
        elif tag.startswith('VB'):
            categories["Verb"].add(lemmatizer.lemmatize(w_lower, pos='v'))
        elif tag.startswith('JJ'):
            categories["Adjective"].add(lemmatizer.lemmatize(w_lower, pos='a'))
        elif tag.startswith('RB'):
            categories["Adverb"].add(lemmatizer.lemmatize(w_lower, pos='r'))
        elif tag in ['PRP', 'PRP$', 'WP', 'WP$']:
            categories["Pronoun"].add(w_lower)
        elif tag in ['CC', 'IN'] and w_lower in ['and', 'but', 'or', 'so', 'because', 'if', 'although', 'while', 'unless']:
            categories["Conjunction"].add(w_lower)
        elif tag == 'UH' or w_lower in ['oh', 'wow', 'oops', 'hey', 'hello', 'hi']:
            categories["Interjection"].add(w_lower)
            
    return {k: sorted(list(v)) for k, v in categories.items()}, phrases


# --- 🚀 UI/UX Precision CSS Design 🚀 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;} div[data-testid="stDecoration"] {display: none !important;}
    .stApp { background-color: #F8FAFC; }
    
    .author-logo {
        position: absolute; top: -15px; left: 0px; font-size: 12px !important; font-weight: 700 !important;
        color: #1E4ED8 !important; background-color: #EFF6FF; padding: 5px 12px; border-radius: 8px; border: 2px solid #BFDBFE; z-index: 999;
    }
    .app-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 30px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2); margin-bottom: 25px; text-align: center;
    }
    .main-title { font-size: 38px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0px !important;}
    .sub-title { font-size: 15px !important; color: #E0F2FE !important; margin-top: 8px !important; }
    .input-label { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; display: block; margin-bottom: 8px !important; }
    .input-disclaimer { font-size: 14px !important; color: #EF4444 !important; font-weight: 700 !important; font-style: italic; display: block; margin-bottom: 15px !important; }
    .stTextArea textarea { border: 6px solid #000000 !important; border-radius: 14px !important; font-size: 20px !important; color: #000000 !important; font-weight: 500 !important; }
    
    div[data-testid="stMainBlockContainer"] > div:nth-child(6) button {
        font-size: 24px !important; font-weight: 800 !important; padding: 14px 28px !important; border-radius: 12px !important; background-color: #FF9800 !important; color: #FFFFFF !important; border: none !important; box-shadow: 0 4px 6px rgba(255, 152, 0, 0.3) !important;
    }
    .sentence-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; margin-bottom: 10px; }
    .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.4 !important; }
    .chinese-text { font-size: 20px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; margin-top: 8px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)
st.markdown("""
    <div class="app-header">
        <p class="main-title">📱Smart Reading</p>
        <p class="sub-title">Break down text • Listen sentence by sentence</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<span class="input-disclaimer">Powered by Google Translate. Content is for reference only.</span>', unsafe_allow_html=True)
st.markdown('<p class="input-label">✍️ Paste your English textbook text below:</p>', unsafe_allow_html=True)

text_input = st.text_area("", height=180, placeholder="Type or paste paragraphs from your textbooks here...")
st.write("") 

if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
    st.session_state.processed_text = text_input
    # Clear old cache on new text input
    st.session_state.word_audio_cache = {}
    st.session_state.play_word_bytes = None

if "processed_text" in st.session_state and st.session_state.processed_text.strip():
    current_text = st.session_state.processed_text
    sentences = [s.strip() for s in current_text.replace('?', '.').replace('!', '.').split('.') if s.strip()]
    
    st.success(f"🎉 Analysis Complete! We prepared {len(sentences)} sentences for your training:")
    
    # 1. Display Sentences and Translations
    for i, sentence in enumerate(sentences):
        full_sentence = sentence + "."
        translated = translate_text(full_sentence)
        
        st.markdown(f"""
            <div class="sentence-card">
                <div style="font-size:13px; color:#3B82F6; font-weight:bold; text-transform:uppercase; margin-bottom:4px;">Sentence {i+1}</div>
                <div class="english-text">{full_sentence}</div>
                <div class="chinese-text">💡 {translated}</div>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            tts = gTTS(text=full_sentence, lang='en', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            st.audio(fp, format="audio/mp3")
        except Exception:
            st.text("Loading audio tool...")
    
    st.write("---")
    
    # 2. 🎯 Advanced 8-POS Grammar Explorer
    st.markdown("### 🔍 Grammar Focus: 8 Parts of Speech & Phrases")
    st.write("Click on any word category below to explore. **Click any word button to play its sound instantly!**")
    
    pos_lists, phrases = advanced_extract_eight_pos(current_text)
    
    # ✨ 核心優勢：在背景把所有生字的語音檔案「一次過存入內存（Byte級快取）」
    # 這樣一來，按鈕點下去不需要再等聯網下載，直接秒播！
    all_words_to_cache = []
    for words in pos_lists.values():
        all_words_to_cache.extend(words)
    all_words_to_cache.extend(phrases)
    all_words_to_cache = list(set(all_words_to_cache))

    # 用快取加快後續渲染
    for word in all_words_to_cache:
        if word not in st.session_state.word_audio_cache:
            try:
                w_tts = gTTS(text=word, lang='en', slow=False)
                w_fp = io.BytesIO()
                w_tts.write_to_fp(w_fp)
                st.session_state.word_audio_cache[word] = w_fp.getvalue()
            except Exception:
                pass

    # 隱藏的秒級播放組件
    if st.session_state.play_word_bytes:
        st.audio(st.session_state.play_word_bytes, format="audio/mp3", autoplay=True)
        st.session_state.play_word_bytes = None

    all_categories = [
        ("🔷 Noun", pos_lists["Noun"]), ("🟡 Pronoun", pos_lists["Pronoun"]),
        ("🟢 Verb", pos_lists["Verb"]), ("🔮 Adjective", pos_lists["Adjective"]),
        ("🔶 Adverb", pos_lists["Adverb"]), ("🚀 Phrase", phrases),
        ("🔗 Conjunction", pos_lists["Conjunction"]), ("📢 Interjection", pos_lists["Interjection"])
    ]
    
    for title, word_list in all_categories:
        with st.expander(f"{title} ({len(word_list)})", expanded=False):
            if word_list:
                cols = st.columns(3)
                for index, word in enumerate(word_list):
                    trans = translate_text(word)
                    button_label = f"🔊 {word} ({trans})"
                    
                    with cols[index % 3]:
                        if st.button(button_label, key=f"btn_{title}_{word}_{index}"):
                            # 點擊時直接抽內存中的語音數據，實現極速秒播！
                            if word in st.session_state.word_audio_cache:
                                st.session_state.play_word_bytes = st.session_state.word_audio_cache[word]
                                st.rerun()
            else:
                st.write("No vocabulary detected in this category.")
