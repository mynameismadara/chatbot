# =====================================================================
# MODE 4: AI TRANSLATOR (EXPANDED TO 100+ LANGUAGES)
# =====================================================================
elif app_mode == "🌐 AI Translator":
    st.title("🌐 Anas Intelligence - Universal AI Translator")
    st.write("Translate source text into any global language using specific style profiles.")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        src_text = st.text_area("Text to Translate:", height=250, placeholder="Type or paste text here...", key="trans_area")
        
        lang_col, style_col = st.columns(2)
        with lang_col:
            target_lang = st.selectbox(
                "Target Language:", 
                [
                    "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Azerbaijani", 
                    "Basque", "Belarusian", "Bengali", "Bosnian", "Bulgarian", "Burmese", 
                    "Catalan", "Cebuano", "Chichewa", "Chinese (Simplified)", "Chinese (Traditional)", 
                    "Corsican", "Croatian", "Czech", "Danish", "Dutch", "English", "Esperanto", 
                    "Estonian", "Filipino (Tagalog)", "Finnish", "French", "Frisian", "Galician", 
                    "Georgian", "German", "Greek", "Gujarati", "Haitian Creole", "Hausa", 
                    "Hawaiian", "Hebrew", "Hindi", "Hmong", "Hungarian", "Icelandic", 
                    "Igbo", "Indonesian", "Irish", "Italian", "Japanese", "Javanese", 
                    "Kannada", "Kazakh", "Khmer", "Kinyarwanda", "Korean", "Kurdish (Kurmanji)", 
                    "Kurdish (Sorani)", "Kyrgyz", "Lao", "Latin", "Latvian", "Lithuanian", 
                    "Luxembourgish", "Macedonian", "Malagasy", "Malay", "Malayalam", "Maltese", 
                    "Maori", "Marathi", "Mongolian", "Nepali", "Norwegian", "Odia (Oriya)", 
                    "Pashto", "Persian", "Polish", "Portuguese", "Punjabi", "Romanian", 
                    "Russian", "Samoan", "Scots Gaelic", "Serbian", "Sesotho", "Shona", 
                    "Sindhi", "Sinhala", "Slovak", "Slovenian", "Somali", "Spanish", 
                    "Sundanese", "Swahili", "Swedish", "Tajik", "Tamil", "Tatar", 
                    "Telugu", "Thai", "Turkish", "Turkmen", "Ukrainian", "Urdu", 
                    "Uyghur", "Uzbek", "Vietnamese", "Welsh", "Xhosa", "Yiddish", 
                    "Yoruba", "Zulu"
                ]
            )
        with style_col:
            translation_style = st.selectbox("Tone/Style Profile:", ["Literal/Exact", "Natural/Casual", "Formal/Business"])
            
        translate_button = st.button("🚀 Translate Text", type="primary", use_container_width=True)

    with col2:
        trans_placeholder = st.empty()
        trans_placeholder.info("Your AI translation will stream here...")

    if translate_button and src_text.strip():
        st.session_state.stop_generation = False
        with col2, st.spinner("Translating text..."):
            instr = f"You are a professional multilingual translator. Translate the user's text into {target_lang}. Adjust your vocabulary selection and grammatical phrasing to match a '{translation_style}' stylistic profile."
            payload = [{"role": "system", "content": instr}, {"role": "user", "content": src_text}]
            run_ai_stream(payload, trans_placeholder)
