import streamlit as st
import re

def render_quiz_page():
    # 讀取主頁面傳遞過來的生字封包
    sentence = st.session_state.get("quiz_target_sentence", "")
    translation = st.session_state.get("quiz_target_translation", "")
    vocabs = st.session_state.get("quiz_target_vocabs", [])
    
    # 🎨 獨立頁面的專屬精美外觀
    st.markdown("""
        <style>
        .quiz-title { font-size: 32px !important; font-weight: 800 !important; color: #1E3A8A !important; margin-bottom: 5px; }
        .back-btn button { background-color: #64748B !important; color: white !important; font-size: 16px !important; font-weight: bold !important; }
        .quiz-box { background-color: #F0Fdf4; border: 2px dashed #22C55E; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
        .quiz-prompt { font-size: 20px !important; font-weight: bold !important; color: #15803D !important; margin-bottom: 8px; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="quiz-title">📝 Interactive Cloze Quiz</p>', unsafe_allow_html=True)
    st.write("根據本句上下文語境，完成下方的生字挖空測試：")
    
    st.info(f"原句中文提示：{translation}")
    st.write("---")
    
    # 核心需求：有 N 個生字，就動態彈出 N 題測試！
    for idx, item in enumerate(vocabs):
        target_word = item["word"]
        target_meaning = item["meaning"]
        
        # 動態為當前題目做句子挖空
        pattern = re.compile(re.escape(target_word), re.IGNORECASE)
        blanked_sentence = pattern.sub("_______", sentence)
        
        st.markdown(f"""
        <div class="quiz-box">
            <div class="quiz-prompt">Question {idx + 1} / {len(vocabs)}</div>
            <div style="font-size: 20px; font-weight: 500; color: #1E293B;">{blanked_sentence}</div>
            <div style="font-size: 14px; color: #64748B; margin-top: 5px;">（提示目標單字意為：{target_meaning}）</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 建立 4 個高效干擾項
        options = [target_word]
        fallback = ["spoke", "party", "formal", "bench", "translate", "severe-looking", "future", "eyes", "think"]
        for fb in fallback:
            if len(options) < 4 and fb != target_word and fb not in options:
                options.append(fb)
        options = sorted(options)
        
        # 單選題控制
        user_choice = st.radio(
            f"請選擇正確的單字填入上方 Question {idx + 1} 的空格：",
            options,
            key=f"page_quiz_radio_{idx}"
        )
        
        if st.button(f"💡 驗證 Question {idx + 1} 答案", key=f"page_quiz_btn_{idx}"):
            if user_choice == target_word:
                st.success(f"🎉 太棒了！完全正確！這裡應該填入『{target_word}』。")
            else:
                st.error(f"❌ 答錯囉！正確答案是『{target_word}』。再仔細思考一下！")
        st.write("<br>", unsafe_allow_html=True)
        
    st.write("---")
    
    # 一鍵返回主頁按鈕
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ Back to Reading Lessons", use_container_width=True):
        st.session_state.current_page = "main"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
