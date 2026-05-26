import streamlit as st
from gtts import gTTS
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

# Lightweight Translation Function (For text and vocabulary translation only)
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "Translation temporarily unavailable..."

# 🎯 Advanced 8-Category Part-of-Speech & Phrase Extractor
def extract_eight_pos(text):
    # Prepare text cleaning
    cleaned_text = re.sub(r'[.,!?";:()\]\[]', ' ', text)
    words_raw = cleaned_text.split()
    
    # 1. Extract Phrases (Basic 2-3 word combinations)
    # Looking for common patterns like: verb+prep, adj+noun, prep+noun
    phrase_matches = re.findall(r'\b(?:look after|look for|pick up|get up|run away|once upon a time|a lot of|depend on|laugh at|listen to|go to|set up|turn off|turn on|put on|take off)\b', text.lower())
    phrases = sorted(list(set(phrase_matches)))
    
    # Remove phrase words from regular word list to avoid duplicate marking
    phrase_blobs = " ".join(phrases)
    
    # Detect and exclude proper nouns (names like John, Mary)
    proper_nouns = set(re.findall(r'\b[A-Z][a-z]+\b', text))
    sentence_starts = set(re.findall(r'(?:^|[.!?]\s+)([A-Z][a-z]+)', text))
    names_to_exclude = {name.lower() for name in (proper_nouns - sentence_starts)}
    
    # Distinct categorization sets
    categories = {
        "Noun": set(), "Pronoun": set(), "Verb": set(), "Adjective": set(),
        "Adverb": set(), "Conjunction": set(), "Interjection": set()
    }
    
    # Grammar Rules Database
    pronouns = {'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'this', 'that', 'these', 'those', 'who', 'whom', 'which', 'what'}
    conjunctions = {'and', 'but', 'or', 'so', 'because', 'although', 'if', 'unless', 'since', 'until', 'while', 'as', 'than', 'yet', 'nor'}
    interjections = {'oh', 'wow', 'oops', 'hey', 'alas', 'hurrah', 'ah', 'hello', 'hi', 'yuck', 'ouch'}
    
    noun_suffixes = ('tion', 'sion', 'ment', 'ence', 'ance', 'ity', 'ness', 'ship', 'ism', 'ist', 'logy', 'ture', 'dom')
    verb_suffixes = ('ing', 'ed', 'ize', 'ify', 'ate', 'es')
    adj_suffixes = ('ful', 'less', 'able', 'ible', 'ive', 'ous', 'ish', 'ant', 'ent', 'ary', 'ic', 'al')

    for word in words_raw:
        w_lower = word.lower()
        if len(w_lower) < 2 or w_lower in names_to_exclude or w_lower in phrase_blobs:
            continue
            
        if w_lower in pronouns:
            categories["Pronoun"].add(w_lower)
        elif w_lower in conjunctions:
            categories["Conjunction"].add(w_lower)
        elif w_lower in interjections:
            categories["Interjection"].add(w_lower)
        elif w_lower.endswith('ly'):
            categories["Adverb"].add(w_lower)
        elif w_lower.endswith(adj_suffixes):
            categories["Adjective"].add(w_lower)
        elif w_lower.endswith(verb_suffixes):
            categories["Verb"].add(w_lower)
        elif w_lower.endswith(noun_suffixes):
            categories["Noun"].add(w_lower)
        else:
            # Fallback optimization for remaining general words
            if len(w_lower) >= 4:
                categories["Noun"].add(w_lower)
                
    return {k: sorted(list(v)) for k, v in categories.items()}, phrases

# 🎯 JavaScript Click-to-Speech Engine
def inject_speech_script():
    st.markdown("""
        <script>
        function speakWord(word) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel(); // Stop ongoing speech
                var utterance = new SpeechSynthesisUtterance(word);
                utterance.lang = 'en-US';
                utterance.rate = 0.9; // Slightly slower for better learning clarity
                window.speechSynthesis.speak(utterance);
            } else {
                alert('Audio playback not supported on this browser.');
            }
        }
        </script>
    """, unsafe_allow_html=True)

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
    
    /* Giant Vibrant Orange Action Button */
    .stButton button {
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
    
    /* Styled HTML Clickable Vocabulary Audio Cards */
    .audio-word-btn {
        display: inline-block;
        background-color: #FFFFFF;
        color: #1E293B;
        border: 2px solid #E2E8F0;
        padding: 8px 16px;
        margin: 5px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .audio-word-btn:hover {
        background-color: #EFF6FF;
        border-color: #3B82F6;
        color: #2563EB;
        transform: scale(1.05);
    }
    .audio-word-btn:active {
        transform: scale(0.95);
    }
    </style>
""", unsafe_allow_html=True)

# --- 🎨 UI Layout Rendering 🎨 ---

# Inject Javascript Speak System
inject_speech_script()

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
    if text_input.strip():
        sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
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
                tts = gTTS(text=
