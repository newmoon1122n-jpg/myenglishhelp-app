import streamlit as st
from gtts import gTTS
import urllib.parse
import json
import urllib.request
import re
import io

# 🎯 網頁基礎配置
st.set_page_config(
    page_title="Smart Reading Buddy",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🚀 輕量翻譯核心 (Google API)
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "Translation Unavailable"

# 🎯 語境生字提取
def extract_vocab(sentence_text, sentence_translation):
    clean_text = re.sub(r"[^\w\s'\-]", ' ', sentence_text)
    words = clean_text.split()
    ignore = {'the','a','an','to','of','at','in','on','by','for','from','with','and','but','or','so','if','i','you','he','she','it','we','they','is','am','are','was','were','be','been','have','has','had','can','will','do','my','your','his','her','its','me','him','us','them'}
    vocab_list, seen = [], set()
    for word in words:
        w_lower = word.lower().strip('-')
        if "'" in w_lower or len(w_lower) < 3 or w_lower in ignore or w_lower in seen: continue
        if not re.match(r'^[a-z\-]+$', w_lower): continue
        seen.add(w_lower)
        try:
            raw = translate_text(w_lower)
            mean = raw.split('(')[0].strip() if '(' in raw else raw.strip()
            if w_lower == "party": mean = "政黨" if "政黨" in sentence_translation else "派對/聚會"
            elif w_lower == "spoke": mean = "輻條" if "輻條" in sentence_translation else "說話"
            if mean.lower() == w_lower or not mean: continue
            vocab_list.append({"word": w_lower, "meaning": mean})
        except: continue
    return vocab_list

# --- 🚀 視覺外觀視覺設計 (CSS) ---
st.markdown("""
   <style>
   #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
   .stAppDeployButton {display: none !important;} div[data-testid="stDecoration"] {display: none !important;}
   .stApp { background-color: #F8FAFC; }
   
   /* 🧡 橙色 Vocabulary 抽屜標題外觀 */
   .stExpander { border: none !important; box-shadow: none !important; margin-bottom: 10px !important; }
   .stExpander summary { 
       background-color: #FFF8E1 !important; 
       color: #FF8F00 !important; 
       border-radius: 10px !important; 
       padding: 12px !important; 
       font-weight: bold !important;
       font-size: 18px !important;
       border: 1px solid #FFE082 !important;
   }

   .sentence-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; }
   .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.4 !important; }
   .chinese-text { font-size: 19px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; margin-top: 10px; }
   .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; margin-top: 5px; }
   .vocab-tag { display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px; font-size: 15px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; }
   
   /* 🟩 綠色開新分頁按鈕 */
   .quiz-btn { display: inline-block; text-align: center; width: 100%; padding: 14px; background-color: #10B981; color: white !important; font-size: 18px; font-weight: bold; border-radius: 8px; text-decoration: none; margin-top: 12px; box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2); }
   .quiz-btn:hover { background-color: #059669; text-decoration: none; }
   
   /* 📝 測驗區塊外觀 */
   .quiz-box { background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
   .quiz-prompt { font-size: 16px !important; font-weight: bold !important; color: #1E3A8A !important; margin-bottom: 8px; }
   
   /* 解析區塊樣式 */
   .explanation-box { background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px 16px; border-radius: 4px; margin-top: 10px; font-size: 16px; color: #1E40AF; }
   </style>
""", unsafe_allow_html=True)

# 🌐 智慧雙模式路由判斷
query_params = st.query_params

# ==========================================
# ─── 🚪 【模式 A：獨立互動測驗頁 (盲測 + 即時反饋鎖定)】 ───
# ==========================================
if "sentence" in query_params:
    sentence_raw = urllib.parse.unquote(query_params["sentence"])
    words_raw = urllib.parse.unquote(query_params["words"])
    meanings_raw = urllib.parse.unquote(query_params["meanings"])
    
    target_words = [w.strip() for w in words_raw.split(",") if w.strip()]
    word_meanings = [m.strip() for m in meanings_raw.split(",") if m.strip()]
    
    st.markdown("""
        <div style='text-align: center; margin-top: 10px; margin-bottom: 25px;'>
            <h2 style='color: #1E3A8A; font-weight: 800; margin-bottom:5px;'>📝 Interactive Cloze Quiz</h2>
            <p style='color: #64748B; font-size: 16px;'>Complete the blanks based purely on the sentence context.</p>
        </div>
    """, unsafe_allow_html=True)
    st.write("---")
    
    # 遍歷所有傳過來的生字，動態生成 N 題完全不同的題目！
    for idx, target_word in enumerate(target_words):
        current_meaning = word_meanings[idx] if idx < len(word_meanings) else "未知"
        
        # 動態正則表達式挖空
        pattern = re.compile(re.escape(target_word), re.IGNORECASE)
        blanked_sentence = pattern.sub("_______", sentence_raw)
        
        st.markdown(f"""
        <div class="quiz-box">
            <div class="quiz-prompt">Question {idx + 1} of {len(target_words)}</div>
            <div style="font-size: 22px; font-weight: 600; color: #0F172A; line-height: 1.4;">{blanked_sentence}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 建立專屬干擾選項組
        options = [target_word]
        fallback = ["spoke", "party", "formal", "bench", "translate", "future", "system", "lessons", "think", "eyes", "clear"]
        for fb in fallback:
            if len(options) < 4 and fb.lower() != target_word.lower() and fb not in options:
                options.append(fb)
        options = sorted(options)
        
        # 使用 Session State 記錄每一題的提交狀態，確保只能「校對一次」
        state_key = f"submitted_{sentence_raw}_{target_word}_{idx}"
        if state_key not in st.session_state:
            st.session_state[state_key] = False
            
        # 如果已經提交過，單選鈕就會變灰鎖定（disabled=True）
        user_choice = st.radio(
            f"Select the correct option for Blank {idx + 1}:",
            options,
            key=f"radio_{idx}",
            disabled=st.session_state[state_key]
        )
        
        # 校對按鈕：如果提交過，按鈕也會變灰鎖定
        if st.button(f"Verify Answer {idx + 1}", key=f"btn_{idx}", disabled=st.session_state[state_key]):
            st.session_state[state_key] = True
            st.rerun()  # 觸發刷新以立即鎖定介面並顯示結果
            
        # 顯示當下校對結果與原因解析
        if st.session_state[state_key]:
            if user_choice.lower() == target_word.lower():
                st.success(f"🎉 Excellent! Your answer '{user_choice}' is CORRECT.")
            else:
                st.error(f"❌ Incorrect. Your answer was '{user_choice}'. The correct answer is: **{target_word}**")
            
            # 💡 當下彈出中文原因解析區塊
            st.markdown(f"""
                <div class="explanation-box">
                    <strong>💡 語境解析與單字提示：</strong><br>
                    在本句中，空格處的正確單字應該填入 <strong>{target_word}</strong>（中文意思：{current_meaning}）。<br>
                    請引導學生結合上下文句意、詞性（Noun/Verb/Adj）以及前後搭配詞，重新體會該單字在英語真實語境中的用法。
                </div>
            """, unsafe_allow_html=True)
            
        st.write("<br><br>", unsafe_allow_html=True)
        
    st.write("---")
    st.info("💡 All questions completed! You can safely close this web tab to return to the main reading board.")

# ==========================================
# ─── 📖 【模式 B：閱讀主頁面工作區】 ───
# ==========================================
else:
    st.markdown("""
       <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 25px;">
           <h1 style="color: white; margin: 0; font-weight: 800; font-size: 38px;">📱 Smart Reading</h1>
           <p style="color: #E0F2FE; opacity: 0.9; font-size: 16px;">Break down text • Learn step by step</p>
       </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p style="font-size:20px; font-weight:900; color:#000;">✍️ Paste your English text below:</p>', unsafe_allow_html=True)
    text_input = st.text_area("", height=150, placeholder="Enter English text here...")
    st.write("") 
    
    if st.button("🚀 Start Audio & Reading Analysis", use_container_width=True):
        if text_input.strip():
            # 移除行首數字編號
            clean_input = re.sub(r'^\d+\s+', '', text_input.strip())
            sentences = [s.strip() for s in clean_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
            st.success(f"🎉 Analysis Complete! Found {len(sentences)} sentences. Let's practice:")
            
            for i, sent in enumerate(sentences):
                full_sent = sent + "."
                trans = translate_text(full_sent)
                vocabs = extract_vocab(full_sent, trans)
                
                # 英文句子與中文翻譯卡片
                st.markdown(f"""
                    <div class="sentence-card">
                        <div style="font-size:14px; font-weight:bold; color:#3B82F6; margin-bottom:4px;">SENTENCE {i+1}</div>
                        <div class="english-text">{full_sent}</div>
                        <div class="chinese-text">💡 {trans}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # TTS 自然語音播放
                try:
                    tts = gTTS(text=full_sent, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    st.audio(fp, format="audio/mp3")
                except:
                    pass
                
                # 🧡 橙金色 Vocabulary 抽屜
                if vocabs:
                    with st.expander("🔑 Vocabulary"):
                        v_html = '<div class="vocab-box">'
                        for v in vocabs:
                            v_html += f'<span class="vocab-tag">📌 {v["word"]}：{v["meaning"]}</span>'
                        v_html += '</div>'
                        st.markdown(v_html, unsafe_allow_html=True)
                        
                        # 🔄 【核心修正】將這句句子的所有生字與意思打包進行網址安全編碼
                        words_param = ",".join([x["word"] for x in vocabs])
                        meanings_param = ",".join([x["meaning"] for x in vocabs])
                        
                        encoded_sentence = urllib.parse.quote(full_sent)
                        encoded_words = urllib.parse.quote(words_param)
                        encoded_meanings = urllib.parse.quote(meanings_param)
                        
                        # 生成智慧跳轉超連結連結
                        quiz_url = f"?sentence={encoded_sentence}&words={encoded_words}&meanings={encoded_meanings}"
                        
                        st.markdown(f'<a href="{quiz_url}" target="_blank" class="quiz-btn">📝 Open Cloze Quiz ({len(vocabs)} Distinct Questions) in New Tab</a>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("Please enter some English sentences first!")
