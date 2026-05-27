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

# 🚀 輕量免費翻譯核心 (免金鑰)
def translate_text(text, target_lang='zh-TW'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in data[0] if sentence[0]])
    except Exception:
        return "Translation Unavailable"

# 🧠 免金鑰 AI 智能出題核心 (修復語法漏洞，暗中生成新句子)
def generate_cloze_sentences_free(vocabs, sentence_text):
    target_words_str = ",".join([v["word"] for v in vocabs])
    
    # 【安全保障機制】如果 AI 接口超時，自動降級使用原句挖空，確保課堂教學不中斷
    fallback_data = []
    for v in vocabs:
        pattern = re.compile(re.escape(v["word"]), re.IGNORECASE)
        blanked = pattern.sub("_______", sentence_text)
        fallback_data.append({
            "target_word": v["word"],
            "new_sentence": blanked,
            "meaning": v["meaning"]
        })
        
    # 呼叫公共免金鑰 AI 出題通道，命令其用生字生成全新的英文句子
    prompt = f"Generate 1 new, distinct simple English sentence for each word in [{target_words_str}]. Replace the word with '_______'. Respond ONLY in raw JSON format like this: [{{\"target_word\":\"word\",\"new_sentence\":\"The _______ is here.\"}}]"
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            ai_reply = response.read().decode('utf-8').strip()
            clean_json_str = re.sub(r'^```json\s*|\s*```$', '', ai_reply)
            new_data = json.loads(clean_json_str)
            
            # 將原本提取的中文意思對齊補入新數據
            for item in new_data:
                tw = item["target_word"].lower()
                for v in vocabs:
                    if v["word"].lower() == tw:
                        item["meaning"] = v["meaning"]
                        break
            return new_data
    except:
        return fallback_data

# 🎯 語境生字自動提取
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

# --- 🚀 視覺外觀設計 (CSS) ---
st.markdown("""
   <style>
   #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
   .stAppDeployButton {display: none !important;} div[data-testid="stDecoration"] {display: none !important;}
   .stApp { background-color: #F8FAFC; }
   
   /* 🏷️ 保留 MACAOCMM 頂部標籤 */
   .macaocmm-badge { display: inline-block; background-color: #E0F2FE; color: #0369A1; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; border: 1px solid #BAE6FD; margin-bottom: 8px; }

   /* 💙 完美保留首頁深藍色大橫幅 */
   .header-banner { background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); padding: 35px 20px; border-radius: 18px; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2); }
   .header-banner h1 { color: white !important; margin: 0 !important; font-weight: 800 !important; font-size: 40px !important; letter-spacing: -0.5px; }
   .header-banner p { color: #E0F2FE !important; opacity: 0.95 !important; font-size: 16px !important; margin-top: 8px !important; font-weight: 500; }

   /* ✍️ 保留黑框輸入框設置 */
   .stTextArea textarea { border: 3px solid #000000 !important; border-radius: 12px !important; padding: 15px !important; font-size: 18px !important; }
   
   /* 🧡 配色完美回歸：溫潤橙金色 Vocabulary 抽屜外觀 */
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

   /* 句子卡片與單字樣式 */
   .sentence-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-top: 20px; }
   .english-text { font-size: 26px !important; font-weight: 600 !important; color: #0F172A !important; line-height: 1.4 !important; }
   .chinese-text { font-size: 19px !important; font-weight: 500 !important; color: #475569 !important; background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; margin-top: 10px; }
   .vocab-box { background-color: #FFFDF5; border: 1px dashed #FFD54F; border-radius: 10px; padding: 12px 16px; margin-top: 5px; }
   .vocab-tag { display: inline-block; background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 6px; font
