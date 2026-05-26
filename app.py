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

# 🎯 Smart Part-of-Speech Extractor (Nouns, Verbs, Adjectives, Adverbs)
def extract_pos_tags(text):
    # Common functional stop words to exclude from study list
    stop_words = {
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'its', 'our', 'their', 'this', 'that', 'these', 'those',
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'can', 'could', 'will', 'would', 'shall', 'should', 'may', 'might', 'must',
        'the', 'and', 'but', 'not', 'for', 'with', 'from', 'about', 'into', 'there', 'here', 'thing', 'things',
        'when', 'where', 'why', 'how', 'who', 'which'
    }
    
    # 1. Detect and exclude proper nouns (names like John, Mary)
    proper_nouns = set(re.findall(r'\b[A-Z][a-z]+\b', text))
    sentence_starts = set(re.findall(r'(?:^|[.!?]\s+)([A-Z][a-z]+)', text))
    names_to_exclude = {name.lower() for name in (proper_nouns - sentence_starts)}

    # Find all words with length >= 3
    all_words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
    
    nouns = set()
    verbs = set()
    adjectives = set()
    adverbs = set()
    
    # Advanced word suffix rules for classification
    noun_suffixes = ('tion', 'sion', 'ment', 'ence', 'ance', 'ity', 'ness', 'ship', 'ism', 'ist', 'logy', 'ture', 'dom')
    verb_suffixes = ('ing', 'ed', 'ize', 'ify', 'ate', 'es')
    adj_suffixes = ('ful', 'less', 'able', 'ible', 'ive', 'ous', 'ish', 'ant', 'ent', 'ary', 'ic', 'al')

    for word in all_words:
        w_lower = word.lower()
        if w_lower in stop_words or w_lower in names_to_exclude:
            continue
            
        # 🔶 Classify Adverbs
        if w_lower.endswith('ly'):
            adverbs.add(w_lower)
        # 🔴 Classify Adjectives
        elif w_lower.endswith(adj_suffixes):
            adjectives.add(w_lower)
        # 🟢 Classify Verbs
        elif w_lower.endswith(verb_suffixes):
            verbs.add(w_lower)
        # 🔵 Classify Nouns
        elif w_lower.endswith(noun_suffixes):
            nouns.add(w_lower)
        else:
            # Default fallback for shorter or unclassified words (Prioritize as nouns for learning)
            if len(w_lower) >= 4:
                nouns.add(w_lower)

    return sorted(list(nouns)), sorted(list(verbs)), sorted(list(adjectives)), sorted(list(adverbs))


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
    .sub-title { font-size: 16px !important; color: #E0F2FE !important; margin-top: 8px !important; }
    
    /* Input Labels and Disclaimers */
    .input-label { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; display: block; margin-bottom: 8px !important; }
    .input-disclaimer { font-size: 14px !important; color: #EF4444 !important; font-weight: 700 !important; font-style: italic; display: block; margin-bottom: 15px !important;
