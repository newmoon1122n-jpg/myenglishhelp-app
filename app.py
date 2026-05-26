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
    
    /* Grammar Analysis Box & Tags */
    .analysis-box {
        background-color: #FFFFFF; border: 3px solid #0EA5E9; padding: 22px; border-radius: 16px; margin-top: 15px;
    }
    .analysis-title { font-size: 20px !important; font-weight: 800 !important; margin-bottom: 12px; margin-top: 15px; }
    .title-noun { color: #0284C7 !important; }
    .title-verb { color: #15803D !important; }
    .title-adj { color: #EC4899 !important; }
    .title-adverb { color: #B45309 !important; }
    
    .tags-container { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; }
    .tag-noun { background-color: #E0F2FE; color: #0369A1; padding: 6px 12px; border-radius: 8px; font-weight: 600; font-size: 16px; border: 1px solid #BAE6FD; }
    .tag-verb { background-color: #DCFCE7; color: #15803D; padding: 6px 12px; border-radius: 8px; font-weight: 600; font-size: 16px; border: 1px solid #BBF7D0; }
    .tag-adj { background-color: #FCE7F3; color: #9D174D; padding: 6px 12px; border-radius: 8px; font-weight: 600; font-size: 16px; border: 1px solid #FBCFE8; }
    .tag-adverb { background-color: #FEF3C7; color: #92400E; padding: 6px 12px; border-radius: 8px; font-weight: 600; font-size: 16px; border: 1px solid #FDE68A; }
    </style>
""", unsafe_allow_html=True)

# --- 🎨 UI Layout Rendering 🎨 ---

st.markdown('<div class="author-logo">🚀 AI Crafted by MACAOCMM</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="app-header">
        <p class="main-title">📱 Smart Reading Buddy</p>
        <p class="sub-title">Bridge to Form 1 • Master English Textbooks Easily</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<span class="input-disclaimer">⚠️ Powered by Google Translate. Content is for reference only.</span>', unsafe_allow_html=True)
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
                tts = gTTS(text=full_sentence, lang='en', slow=False)
                tts.save(f"sentence_{i}.mp3")
                st.audio(f"sentence_{i}.mp3", format="audio/mp3")
            except Exception:
                st.text("Loading audio tool...")
        
        st.write("---")
        
        # 2. 🎯 Bottom Feature: Grammar Analysis (Fully English Controlled Expansion)
        st.markdown("### 🔍 Grammar Focus: Vocabulary Extractor")
        st.write("Ready for a bigger challenge? Click below to extract key vocabulary categorized by parts of speech.")
        
        with st.expander("✨ Click to Extract Nouns, Verbs, Adjectives & Adverbs", expanded=False):
            nouns, verbs, adjectives, adverbs = extract_pos_tags(text_input)
            
            st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
            
            # 🔵 Nouns List
            st.markdown('<div class="analysis-title title-noun">🔷 Core Nouns (名詞 - No Names)</div>', unsafe_allow_html=True)
            if nouns:
                st.markdown('<div class="tags-container">', unsafe_allow_html=True)
                for noun in nouns:
                    trans_n = translate_text(noun)
                    st.markdown(f'<span class="tag-noun">{noun} ({trans_n})</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("No major nouns detected.")
                
            # 🟢 Verbs List
            st.markdown('<div class="analysis-title title-verb">🟢 Action Verbs (動詞)</div>', unsafe_allow_html=True)
            if verbs:
                st.markdown('<div class="tags-container">', unsafe_allow_html=True)
                for verb in verbs:
                    trans_v = translate_text(verb)
                    st.markdown(f'<span class="tag-verb">{verb} ({trans_v})</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("No major verbs detected.")

            # 💗 Adjectives List
            st.markdown('<div class="analysis-title title-adj">🔮 Descriptive Adjectives (形容詞)</div>', unsafe_allow_html=True)
            if adjectives:
                st.markdown('<div class="tags-container">', unsafe_allow_html=True)
                for adj in adjectives:
                    trans_adj = translate_text(adj)
                    st.markdown(f'<span class="tag-adj">{adj} ({trans_adj})</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("No major adjectives detected.")
                
            # 🟡 Adverbs List
            st.markdown('<div class="analysis-title title-adverb">🔶 Useful Adverbs (副詞)</div>', unsafe_allow_html=True)
            if adverbs:
                st.markdown('<div class="tags-container">', unsafe_allow_html=True)
                for adverb in adverbs:
                    trans_a = translate_text(adverb)
                    st.markdown(f'<span class="tag-adverb">{adverb} ({trans_a})</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("No major adverbs detected.")
                
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        st.error("Please enter some English sentences first!")
