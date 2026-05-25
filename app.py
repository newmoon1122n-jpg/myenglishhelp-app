import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request

# 官方免安裝的輕量翻譯函數
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "翻譯暫時出現小碎步，請再試一次！"

# 網頁大字體與樣式設計
st.markdown("""
    <style>
    .big-title { font-size:40px !important; font-weight: bold; color: #1E88E5; text-align: center; }
    .english-box { font-size:26px !important; font-weight: 500; color: #2C3E50; margin-bottom: 2px; }
    .chinese-box { font-size:22px !important; color: #7F8C8D; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">📱 英文文章點讀翻譯機</p>', unsafe_allow_html=True)

# 讓使用者輸入或貼上文章
text_input = st.text_area("請在下方輸入或貼上英文文章：", height=200, placeholder="Once upon a time...")

if st.button("🚀 開始拆解和點讀", use_container_width=True):
    if text_input.strip():
        # 按句號、問號、感嘆號拆分句子
        sentences = [s.strip() for s in text_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        
        st.success(f"成功拆解出 {len(sentences)} 個句子，準備點讀：")
        st.write("---")
        
        for i, sentence in enumerate(sentences):
            full_sentence = sentence + "."
            # 翻譯
            translated = translate_text(full_sentence)
            
            # 顯示大字體英文與中文
            st.markdown(f'<p class="english-box">{i+1}. {full_sentence}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="chinese-box">💡 {translated}</p>', unsafe_allow_html=True)
            
            # 產生語音播放條
            try:
                tts = gTTS(text=full_sentence, lang='en', slow=False)
                tts.save(f"sentence_{i}.mp3")
                st.audio(f"sentence_{i}.mp3", format="audio/mp3")
            except Exception:
                st.warning("語音生成稍有延遲")
            
            st.write("---")
    else:
        st.warning("請先輸入一些英文內容喔！")
