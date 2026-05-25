import streamlit as st
from googletrans import Translator
from gtts import gTTS
import re

# 設定網頁標題與大字體
st.set_page_config(page_title="英文點讀翻譯機", page_icon="📱")
st.title("📱 英文影相點讀翻譯機")
st.write("請在下方直接打字，或使用手機相機影相上傳。")

# 1. 建立左邊的輸入區
uploaded_file = st.file_uploader("👉 步驟一：手機點這裡「影相」或上傳圖片", type=["png", "jpg", "jpeg"])
input_text = st.text_area("或者直接在這裡輸入/貼上英文文字：", height=150)

# 如果是用戶影相上傳（這裡為了讓老人家好操作，簡化為純文字與語音處理，若要完整OCR需加裝對應工具）
text_to_process = ""
if uploaded_file is not None:
    st.info("圖片上傳成功！(提示：若需自動識別圖片文字，建議直接使用下方輸入框或配合手機複製功能)")
if input_text:
    text_to_process = input_text

# 2. 開始處理按鈕
if st.button("👉 步驟二：點我開始拆解和翻譯", type="primary"):
    if text_to_process:
        # 精準按標點符號拆分句子
        sentences = re.split(r'(?<=[.!?])\s+', text_to_process.strip())
        translator = Translator()
        
        st.subheader("📋 步驟三：逐句點讀列表")
        
        # 3. 逐句輸出英文、中文和聲音
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) == 0:
                continue
            
            # 翻譯成繁體中文
            try:
                translated = translator.translate(sentence, src='en', dest='zh-tw').text
            except:
                translated = "翻譯暫時出現波折"
                
            # 顯示一個漂亮乾淨的卡片
            with st.container():
                st.markdown(f"**【英文原文 {i+1}】**")
                st.info(sentence)
                st.markdown(f"**【中文翻譯】** {translated}")
                
                # 生成該句子的標準發音
                try:
                    tts = gTTS(text=sentence, lang='en')
                    audio_path = f"audio_{i}.mp3"
                    tts.save(audio_path)
                    # 顯示播放條
                    st.audio(audio_path, format="audio/mp3")
                except:
                    st.write("📢 語音加載失敗")
                st.write("---") # 畫一條分隔線，方便閱讀
    else:
        st.warning("請先輸入英文文字或上傳內容喔！")
