import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request

# Official lightweight translation function (Translates English input to Traditional Chinese for explanation)
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "Translation temporarily unavailable, please try again!"

# UI Big Font and Style Design
st.markdown("""
    <style>
    .big-title { font-size:40px !important; font-weight: bold; color: #1E88E5; text-align: center; }
    .english-box { font-size:26px !important; font-weight: 500; color: #2C3E50; margin-bottom: 2px; }
    .chinese-box { font-size:22px !important; color: #7F8C8D; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# App Title (Changed to English)
st.markdown('<p class="big-title">📱 English Reading & Audio Player</p>', unsafe_allow_html=True)

# User Input Area (Changed to English)
text_input = st.text_area("Please paste your English article below:", height=200, placeholder="Once upon a time...")

# Button (Changed to English)
if st.button("🚀 Start Analysis and Reading", use_container_width=True):
    if text_input.strip():
        # Split sentences by period, question mark, and exclamation mark
        sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        
        st.success(f"Successfully split into {len(sentences)} sentences. Ready to read:")
        st.write("---")
        
        for i, sentence in enumerate(sentences):
            full_sentence = sentence + "."
            # Translate to Chinese for the student's reference
            translated = translate_text(full_sentence)
            
            # Display Big Font English and Chinese Translation
            st.markdown(f'<p class="english-box">{i+1}. {full_sentence}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="chinese-box">💡 {translated}</p>', unsafe_allow_html=True)
            
            # Generate Audio Player
            try:
                tts = gTTS(text=full_sentence, lang='en', slow=False)
                tts.save(f"sentence_{i}.mp3")
                st.audio(f"sentence_{i}.mp3", format="audio/mp3")
            except Exception:
                st.warning("Audio generation slightly delayed...")
            
            st.write("---")
    else:
        st.warning("Please enter some English content first!")
