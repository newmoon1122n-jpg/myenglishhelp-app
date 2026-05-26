import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import os

# 🚀 引入 NLTK 核心庫
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer

# 🎯 在本地或伺服器首次執行時，自動下載 NLTK 必要的大腦模型
@st.cache_resource
def initialize_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('taggers/averaged_perceptron_tagger')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('wordnet')
        nltk.download('omw-1.4')

initialize_nltk()

# 🎯 Web Configuration
st.set_page_config(
    page_title="Smart Reading Buddy",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize Session State for word audio triggering
if "play_word" not in st.session_state:
    st.session_state.play_word = None

# Official lightweight translation function (Only for text and vocabulary)
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "Translation temporarily unavailable..."

# 🎯 AI-Driven POS Classifier using NLTK (With Context Awareness & Lemmatization)
def advanced_extract_eight_pos(text):
    if not text.strip():
        return {k: [] for k in ["Noun", "Pronoun", "Verb", "Adjective", "Adverb", "Conjunction", "Interjection"]}, []

    # 1. Extract Common Educational Phrases First
    phrase_patterns = r'\b(look after|look for|pick up|get up|run away|once upon a time|a lot of|depend on|laugh at|listen to|go to|set up|turn off|turn on|put on|take off)\b'
    phrases = sorted(list(set(re.findall(phrase_patterns, text.lower()))))
    
    # 2. Tokenize and Tag parts of speech based on Context
    tokens = word_tokenize(text)
    tagged_words = pos_tag(tokens)
    
    # Initialize Lemmatizer to restore words to their base form (e.g., running -> run)
    lemmatizer = WordNetLemmatizer()
    
    categories = {
        "Noun": set(), "Pronoun": set(), "Verb": set(), "Adjective": set(),
        "Adverb": set(), "Conjunction": set(), "Interjection": set()
    }
    
    # Filter list for common stop words that don't need vocabulary testing
    ignore_words = {'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with'}

    for word, tag in tagged_words:
        w_lower = word.lower()
        
        # Skip punctuation, short noise, numbers, or specific stop words
        if len(w_lower) < 2 or w_lower in ignore_words or not w_lower.isalpha():
            continue
            
        # NLTK Rules Chart Conversion
        if tag.startswith('NN'): # Nouns
            # Filter out Proper Nouns (Names) if they are capitalized in mid-sentence
            if tag == 'NNP' or tag == 'NNPS':
                continue
            base_word = lemmatizer.lemmatize(w_lower, pos='n')
            categories["Noun"].add(base_word)
            
        elif tag.startswith('VB'): # Verbs
            base_word = lemmatizer.lemmatize(w_lower, pos='v')
            categories["Verb"].add(base_word)
            
        elif tag.startswith('JJ'): # Adjectives
            base_word = lemmatizer.lemmatize(w_lower, pos='a')
            categories["Adjective"].add(base_word)
            
        elif tag.startswith('RB'): # Adverbs
            base_word = lemmatizer.lemmatize(w_lower, pos='r')
            categories["Adverb"].add(base_word)
            
        elif tag in ['PRP', 'PRP$', 'WP', 'WP$']: # Pronouns
            categories["Pronoun"].add(w_lower)
            
        elif tag in ['CC', 'IN'] and w_lower in ['and', 'but', 'or', 'so', 'because', 'if', 'although', 'while', 'unless']: # Conjunctions
            categories["Conjunction"].add(w_lower)
            
        elif tag == 'UH' or w_lower in ['oh', 'wow', 'oops', 'hey', 'hello', 'hi']: # Interjections
            categories["Interjection"].add(w_lower)
            
    # Format and sort outputs neatly
    return {k: sorted(list(v)) for k, v in categories.items()}, phrases


# --- 🚀 UI/UX Precision CSS Design 🚀 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}

    .stApp { background-color: #F8FAFC; }
    
    /* Top Left Logo Custom Badge */
    .author-logo {
        position: absolute; top: -15px; left: 0px;              
        font-size: 12px !important; font-weight: 700 !important;
        color: #1E4ED8 !important; background-color: #EFF6FF;  
        padding: 5px 12px; border-radius: 8px; border: 2px solid #BFDBFE;  
        font-family: sans-serif; letter-spacing: 0.5px; z-index: 999;
    }
    
    /* Main Top Header Banner */
    .app-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 30px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(59, 131, 246, 0.2);
        margin-bottom: 25px; text-align: center; position: relative; 
    }
    .main-title { font-size: 38px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0px !important;}
    .sub-title { font-size: 15px !important; color: #E0F2FE !important; margin-top: 8px !important; }
    
    /* Input Labels and Disclaimers */
    .input-label { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; display: block; margin-bottom: 8px !important; }
    .input-disclaimer { font-size: 14px !important; color: #EF4444 !important; font-weight: 700 !important; font-style: italic; display: block; margin-bottom: 15px !important; }

    /* Ultra-bold 6px Black Textarea Border */
    .stTextArea textarea {
        border: 6px solid #000000 !important; border-radius: 14px !important;       
        background-color: #FFFFFF !important; font-size: 20px !important; color: #000000 !important; font-weight: 500 !important;
    }
    
    /* Giant Vibrant Orange Action Button Layout Pinpointing */
    div[data-testid="stMainBlockContainer"] > div:nth-child(6) button {
        font-size: 24px !important; font-weight: 800 !important; padding: 14px 28px !important;         
        border-radius: 12px !important; background-color: #FF9800 !important; color: #FFFFFF !important; border: none !important;
        box-shadow: 0 4px 6px rgba(255, 152, 0, 0.3) !important;
    }

    /* Core Reading Cards */
    .sentence-card {
        background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; margin-bottom: 10px;
    }
    .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.4 !important; }
    .chinese-text { font-size: 20px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; margin-top: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 🎨 UI Layout Rendering 🎨 ---

st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="app-header">
        <p class="main-title">📱Smart Reading</p>
        <p class="sub-title">Break down text • Listen sentence by sentence • Vocabulary</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<span class="input-disclaimer">Powered by Google Translate. Content is for reference only.</span>', unsafe_allow_html=True)
st.markdown('<p class="input-label">✍️ Paste your English textbook text below:</p>', unsafe_allow_html=True)

text_input = st.text_area("", height=180, placeholder="Type or paste paragraphs from your Math, Science, or English textbooks here...")

st.write("") 

# Main Process Button
if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
    st.session_state.processed_text = text_input

# Check if text has been processed and saved in memory
if "processed_text" in st.session_state and st.session_state.processed_text.strip():
    current_text = st.session_state.processed_text
    sentences = [s.strip() for s in current_text.replace('?', '.').replace('!', '.').split('.') if s.strip()]
    
    st.success(f"🎉 Analysis Complete! We prepared {len(sentences)} sentences for your training:")
    
    # 1. Display Sentences, Translations, and Audio Player
    for i, sentence in enumerate(sentences):
        full_sentence = sentence + "."
        translated = translate_text(full_sentence)
        
        st.markdown(f"""
            <div class="sentence-card">
                <div style="font-size:13px; color:#3B82F6; font-weight:bold; text-transform:uppercase; margin-bottom:4px;">Sentence {i+1}</div>
                <div class="english-text">{full_sentence}</div>
                <div class="chinese-text">💡 中文翻譯：{translated}</div>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            tts = gTTS(text=full_sentence, lang='en', slow=False)
            filename = f"sentence_{i}.mp3"
            tts.save(filename)
            st.audio(filename, format="audio/mp3")
        except Exception:
            st.text("Loading audio tool...")
    
    st.write("---")
    
    # 2. 🎯 Bottom Feature: Advanced 8-POS Grammar Explorer
    st.markdown("### 🔍 Grammar Focus: 8 Parts of Speech & Phrases")
    st.write("Click on any word category below to explore. **Click any word button to play its sound instantly!**")
    
    # Hidden audio player trigger section (Guarantees 100% sound playback)
    if st.session_state.play_word:
        try:
            word_tts = gTTS(text=st.session_state.play_word, lang='en', slow=False)
            word_tts.save("temp_word.mp3")
            st.audio("temp_word.mp3", format="audio/mp3", autoplay=True)
            # Reset after playing to prevent loop restarts
            st.session_state.play_word = None
        except Exception:
            pass

    # Extract high-precision lists using NLTK AI Engine
    pos_lists, phrases = advanced_extract_eight_pos(current_text)
    
    # Define 8 Categories Linked to Icons
    all_categories = [
        ("🔷 Noun", pos_lists["Noun"]),
        ("🟡 Pronoun", pos_lists["Pronoun"]),
        ("🟢 Verb", pos_lists["Verb"]),
        ("🔮 Adjective", pos_lists["Adjective"]),
        ("🔶 Adverb", pos_lists["Adverb"]),
        ("🚀 Phrase", phrases),
        ("🔗 Conjunction", pos_lists["Conjunction"]),
        ("📢 Interjection", pos_lists["Interjection"])
    ]
    
    # Render the 8 category expanders sequentially with Streamlit Native Buttons
    for title, word_list in all_categories:
        with st.expander(f"{title} ({len(word_list)})", expanded=False):
            if word_list:
                # Layout tags neatly in a 3-column structural layout
                cols = st.columns(3)
                for index, word in enumerate(word_list):
                    trans = translate_text(word)
                    button_label = f"🔊 {word} ({trans})"
                    
                    with cols[index % 3]:
                        if st.button(button_label, key=f"btn_{title}_{word}_{index}"):
                            st.session_state.play_word = word
                            st.rerun()
            else:
                st.write("No vocabulary detected in this category.")
