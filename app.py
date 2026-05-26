import streamlit as st
import urllib.parse
import json
import urllib.request
import re

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

# 官方輕量翻譯函數（僅用於單字與句子翻譯）
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
        position: absolute; top: -15px; left: 0px; font-size: 12px !important; font-weight: 70
