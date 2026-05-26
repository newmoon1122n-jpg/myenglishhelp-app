import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re

# 🎯 設定網頁配置，隱藏 Streamlit 官方選單與標籤
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
        return "Translation temporarily unavailable..."

# 🎯 核心新功能：聰明提取名詞與動詞（排除人名與常見代名詞）
def extract_nouns_and_verbs(text):
    # 預自定義一些英文中最常見、不需要背的極簡單字（代名詞、助動詞等）
    stop_words = {
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'its', 'our', 'their', 'this', 'that', 'these', 'those',
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'can', 'could', 'will', 'would', 'shall', 'should', 'may', 'might', 'must',
        'the', 'and', 'but', 'not', 'for', 'with', 'from', 'about', 'into', 'there', 'here', 'thing', 'things'
    }
    
    # 1. 找出潛在的人名（非句首的大寫單字，例如 John, Mary）
    # 先把完整的句子切開，找出那些在句子中間卻大寫的字
    proper_nouns = set(re.findall(r'\b[A-Z][a-z]+\b', text))
    # 找出句首的字（句號後面第一個大寫字），句首的大寫通常不是人名，所以不排除
    sentence_starts = set(re.findall(r'(?:^|[.!?]\s+)([A-Z][a-z]+)', text))
    # 真正要排除的人名 = 在中間大寫，且不是句首的字
    names_to_exclude = {name.lower() for name in (proper_nouns - sentence_starts)}

    # 2. 清理文章，抓出所有長度大於等於3的純英文單字
    all_words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
    
    nouns = set()
    verbs = set()
    
    # 常見字尾規律判斷（輕量級詞性分析）
    verb_suffixes = ('ing', 'ed', 'ize', 'ify', 'ate', 'es')
    noun_suffixes = ('tion', 'sion', 'ment', 'ence', 'ance', 'ity', 'ness', 'ship
