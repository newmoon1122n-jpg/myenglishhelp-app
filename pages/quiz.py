import streamlit as st
import urllib.parse
import re

st.set_page_config(page_title="Interactive Quiz", layout="centered")

st.markdown("""
   <style>
   #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
   .stAppDeployButton {display: none !important;} div[data-testid="stDecoration"] {display: none !important;}
   .stApp { background-color: #F8FAFC; }
   .quiz-box { background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
   .quiz-prompt { font-size: 18px !important; font-weight: bold !important; color: #1E3A8A !important; margin-bottom: 10px; }
   </style>
""", unsafe_allow_html=True)

query_params = st.query_params

if "sentence" in query_params and "words" in query_params:
    sentence_raw = urllib.parse.unquote(query_params["sentence"])
    words_raw = urllib.parse.unquote(query_params["words"])
    target_words = [w.strip() for w in words_raw.split(",") if w.strip()]
    
    st.markdown("""
        <div style='text-align: center; margin-top: 10px; margin-bottom: 25px;'>
            <h2 style='color: #1E3A8A; font-weight: 800;'>📝 Interactive Cloze Quiz</h2>
            <p style='color: #64748B; font-size: 16px;'>Complete the blanks based purely on the sentence context.</p>
        </div>
    """, unsafe_allow_html=True)
    st.write("---")
    
    # Generate N questions for N vocab terms dynamically
    for idx, target_word in enumerate(target_words):
        pattern = re.compile(re.escape(target_word), re.IGNORECASE)
        blanked_sentence = pattern.sub("_______", sentence_raw)
        
        # Displaying the question box with NO hint text
        st.markdown(f"""
        <div class="quiz-box">
            <div class="quiz-prompt">Question {idx + 1} of {len(target_words)}</div>
            <div style="font-size: 22px; font-weight: 600; color: #0F172A; line-height: 1.4;">{blanked_sentence}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Options Generator
        options = [target_word]
        fallback = ["spoke", "party", "formal", "bench", "translate", "severe-looking", "future", "system", "lessons", "think", "eyes"]
        for fb in fallback:
            if len(options) < 4 and fb.lower() != target_word.lower() and fb not in options:
                options.append(fb)
        options = sorted(options)
        
        user_choice = st.radio(
            f"Select the correct option for Question {idx + 1}:",
            options,
            key=f"independent_radio_{idx}"
        )
        
        if st.button(f"Verify Answer {idx + 1}", key=f"independent_btn_{idx}"):
            if user_choice.lower() == target_word.lower():
                st.success(f"🎉 Excellent! '{target_word}' is correct.")
            else:
                st.error(f"❌ Incorrect. Review the sentence structure and try again!")
        st.write("<br>", unsafe_allow_html=True)
        
    st.write("---")
    st.info("💡 Review complete. You can safely close this tab to return to your reading page.")
else:
    st.warning("No active quiz session found. Please launch a quiz from the main lesson reading workspace.")
