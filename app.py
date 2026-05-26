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

# 🎯 自動下載必備的語法大腦模型（加入快取，避免重複下載變慢）
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

# 官方輕量翻譯函數
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "無法取得翻譯"

# 🎯 專業級 NLTK 句內詞性精確過濾
def extract_sentence_vocab(sentence_text):
    if not sentence_text.strip():
        return []
        
    # 1. 使用 NLTK 進行標準分詞與上下文詞性標註
    tokens = word_tokenize(sentence_text)
    tagged_words = pos_tag(tokens)
    lemmatizer = WordNetLemmatizer()
    
    # 排除基礎高頻虛詞
    ignore_words = {
        'the', 'a', 'an', 'to', 'of', 'at', 'in', 'on', 'by', 'for', 'from', 'with', 'and', 'but', 
        'or', 'so', 'because', 'if', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 
        'these', 'those', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'
    }
    
    vocab_list = []
    seen_words = set()
    
    for word, tag in tagged_words:
        w_lower = word.lower()
        
        # 基本過濾
        if len(w_lower) < 2 or w_lower in ignore_words or not w_lower.isalpha() or w_lower in seen_words:
            continue
            
        # 💡 NLTK 精確標籤對應與原型還原 (Lemmatization)
        pos = None
        if tag.startswith('NN'):        # 名詞 Noun (NN, NNS, NNP, NNPS)
            pos = "n."
            base_word = lemmatizer.lemmatize(w_lower, pos='n')
        elif tag.startswith('VB'):      # 動詞 Verb (VB, VBD, VBG, VBN, VBP, VBZ)
            pos = "v."
            base_word = lemmatizer.lemmatize(w_lower, pos='v')
        elif tag.startswith('JJ'):      # 形容詞 Adjective (JJ, JJR, JJS)
            pos = "adj."
            base_word = lemmatizer.lemmatize(w_lower, pos='a')
        elif tag.startswith('RB'):      # 副詞 Adverb (RB, RBR, RBS)
            pos = "adv."
            base_word = lemmatizer.lemmatize(w_lower, pos='r')
            
        # 🚫 如果不是四大實詞，直接無情排除
        if not pos:
            continue
            
        # 避免原型還原後重複
        if base_word in seen_words:
            continue
        seen_words.add(base_word)
        
        # 翻譯核心生字（使用還原後的主幹單字，查字典更精準）
        chinese_meaning = translate_text(
