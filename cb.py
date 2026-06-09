import streamlit as st
from openai import OpenAI

# 1. Page Configuration (Disguised title to protect privacy on the outside)
st.set_page_config(page_title="Private Portal", page_icon="🔒", layout="wide")

# Initialize Master Chat Storage to track multiple conversations
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}  
if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "Chat 1"
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False

# Flashcard structural tracking state
if "flashcard_content" not in st.session_state:
    st.session_state.flashcard_content = ""
if "show_answers" not in st.session_state:
    st.session_state.show_answers = False

# Make sure our active chat exists in our master storage
if st.session_state.current_chat_title not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat_title] = [
        {"role": "assistant", "content": "Secure connection established. System ready."}
    ]

# 2. Check for required secrets
try:
    api_key_from_secrets = st.secrets["OPENAI_API_KEY"]
    correct_password = st.secrets["APP_PASSWORD"]
except KeyError:
    st.error("System configuration missing. Access offline.")
    st.stop()

# 3. Disguised Secure Password Protection Interface (No mention of AI or names)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Secure Portal Connection")
    st.write("Authorization required to access this node.")
    user_password = st.text_input("Enter Passcode:", type="password")
    
    if st.button("Authenticate"):
        if user_password == correct_password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Authentication failed. Access Denied.")
    st.stop()

# =====================================================================
# EVERYTHING BELOW THIS LINE ONLY RUNS IF THE PASSWORD IS CORRECT
# =====================================================================

# 4. Shared API Client Setup
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key_from_secrets
)

# Shared ultra-fast free models list
free_models_to_try = [
    "meta-llama/llama-4-scout:free",     
    "openai/gpt-oss-20b:free",          
    "meta-llama/llama-3.2-3b-instruct:free",
    "openrouter/free"                   
]

# 5. Sidebar Navigation & Active Recent Chats Management
with st.sidebar:
    st.error("⚠️ **CRITICAL WARNING:** Exiting, refreshing, or closing this browser tab will permanently delete all chat history and active sessions!")
    st.markdown("---")
    
    st.title("🤖 Navigation")
    app_mode = st.selectbox(
        "Choose Mode:", 
        ["💬 Original Chatbot", "📝 Text Humanizer", "📊 Smart Summarizer", "🌐 AI Translator", "🧠 Flashcard Generator"]
    )
    
    st.markdown("---")
    
    # CHATBOT TOOLS AND SAVED CHATS LIST
    if app_mode == "💬 Original Chatbot":
        st.subheader("📚 Recent Chats")
        
        if st.button("➕ New Chat", use_container_width=True):
            new_chat_num = len(st.session_state.all_chats) + 1
            new_title = f"Chat {new_chat_num}"
            while new_title in st.session_state.all_chats:  
                new_chat_num += 1
                new_title = f"Chat {new_chat_num}"
                
            st.session_state.all_chats[new_title] = [
                {"role": "assistant", "content": "Hello! Started a brand new chat. What's on your mind?"}
            ]
            st.session_state.current_chat_title = new_title
            st.rerun()
            
        st.write("") 
        
        for chat_title in list(st.session_state.all_chats.keys()):
            is_current = (chat_title == st.session_state.current_chat_title)
            button_label = f"💬 {chat_title}" if not is_current else f"👉 {chat_title}"
            
            if st.button(button_label, key=f"select_{chat_title}", use_container_width=True, type="secondary" if not is_current else "primary"):
                st.session_state.current_chat_title = chat_title
                st.rerun()
                
        st.markdown("---")
        
        st.subheader("⚙️ Chat Options")
        new_name = st.text_input("Rename current chat:", value=st.session_state.current_chat_title, key="rename_input")
        if st.button("✏️ Confirm Rename", use_container_width=True):
            if new_name.strip() and new_name != st.session_state.current_chat_title:
                if new_name in st.session_state.all_chats:
                    st.error("A chat room with that name already exists!")
                else:
                    st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(st.session_state.current_chat_title)
                    st.session_state.current_chat_title = new_name
                    st.rerun()
                    
        if st.button("🗑️ Delete Current Chat", use_container_width=True, type="secondary"):
            if len(st.session_state.all_chats) > 1:
                old_title = st.session_state.current_chat_title
                st.session_state.all_chats.pop(old_title)
                st.session_state.current_chat_title = list(st.session_state.all_chats.keys())[0]
                st.rerun()
            else:
                st.warning("⚠️ You can't delete your last open chat room!")
                
        st.markdown("---")
        
    if st.button("🛑 Force Stop AI", use_container_width=True):
        st.session_state.stop_generation = True
        st.toast("Stopping generation...")

# Guarantee active key exists to prevent edge-case crashing
if st.session_state.current_chat_title not in st.session_state.all_chats:
    st.session_state.current_chat_title = list(st.session_state.all_chats.keys())[0]
active_messages = st.session_state.all_chats[st.session_state.current_chat_title]

# Shared processing function to execute global API streams dynamically
def run_ai_stream(messages_payload, placeholder):
    global free_models_to_try
    response_stream = None
    for model_slug in free_models_to_try:
        try:
            client_kwargs = {"model": model_slug, "messages": messages_payload, "stream": True}
            response_stream = client.chat.completions.create(**client_kwargs)
            break
        except Exception:
            continue
    if response_stream is not None:
        try:
            full_response = ""
            for chunk in response_stream:
                if st.session_state.stop_generation:
                    full_response += "\n\n[Generation Stopped by User]"
                    break
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            return full_response
        except Exception as e:
            st.error(f"Streaming Error: {e}")
            return None
    else:
        st.error("All free models are currently heavily loaded. Try again shortly!")
        return None

# =====================================================================
# MODE 1: ORIGINAL CHATBOT
# =====================================================================
if app_mode == "💬 Original Chatbot":
    st.title("🤖 Anas Intelligence 👍")
    st.caption(f"Currently Viewing Room: **{st.session_state.current_chat_title}**")

    for message in active_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if user_input := st.chat_input("Ask Anas Intelligence something..."):
        st.session_state.stop_generation = False
        active_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                payload = [{"role": m["role"], "content": m["content"]} for m in active_messages]
                reply = run_ai_stream(payload, st.empty())
                if reply:
                    active_messages.append({"role": "assistant", "content": reply})

# =====================================================================
# MODE 2: TEXT HUMANIZER
# =====================================================================
elif app_mode == "📝 Text Humanizer":
    st.title("📝 Anas Intelligence - Humanizer Mode")
    st.write("Paste paragraphs below to rewrite them with a fluid, natural human flow.")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        user_paragraphs = st.text_area("Paste text or essay here:", height=350, placeholder="Paste text here...", key="humanizer_area")
        submit_button = st.button("✨ Humanize Text", type="primary", use_container_width=True)

    with col2:
        output_placeholder = st.empty()
        output_placeholder.info("Your humanized text will stream here...")

    if submit_button and user_paragraphs.strip():
        st.session_state.stop_generation = False
        with col2, st.spinner("Rewriting..."):
            instr = "You are an expert human editor. Rewrite the text to make it sound completely natural, fluid, and engaging. Vary sentence lengths, eliminate typical robotic phrasing while protecting facts."
            payload = [{"role": "system", "content": instr}, {"role": "user", "content": user_paragraphs}]
            run_ai_stream(payload, output_placeholder)

# =====================================================================
# MODE 3: SMART SUMMARIZER
# =====================================================================
elif app_mode == "📊 Smart Summarizer":
    st.title("📊 Anas Intelligence - Smart Summarizer")
    st.write("Turn huge documents or notes into scannable key points.")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        heavy_text = st.text_area("Paste material here:", height=350, placeholder="Paste details here...", key="summary_area")
        summarize_button = st.button("⚡ Extract Insights", type="primary", use_container_width=True)

    with col2:
        summary_placeholder = st.empty()
        summary_placeholder.info("The summary breakdown will generate here...")

    if summarize_button and heavy_text.strip():
        st.session_state.stop_generation = False
        with col2, st.spinner("Analyzing data..."):
            instr = "You are an elite analyst. Process the text and return a summary formatted exactly with sections: ## 📋 Executive Summary, ## 🔑 Key Takeaways, and ## 🧠 Core Terms & Concepts."
            payload = [{"role": "system", "content": instr}, {"role": "user", "content": heavy_text}]
            run_ai_stream(payload, summary_placeholder)

# =====================================================================
# MODE 4: AI TRANSLATOR (100+ GLOBAL & REGIONAL LANGUAGES)
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

# =====================================================================
# MODE 5: FLASHCARD GENERATOR
# =====================================================================
elif app_mode == "🧠 Flashcard Generator":
    st.title("🧠 Anas Intelligence - Smart Flashcard Engine")
    st.write("Paste your raw study notes, definitions, or textbook materials below to forge structured study cards.")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        raw_notes = st.text_area("Paste Study Material/Notes:", height=280, placeholder="Paste definitions, raw class notes, or text details...", key="flash_area")
        num_cards = st.slider("Number of flashcards to forge:", min_value=3, max_value=12, value=5)
        generate_cards_btn = st.button("🃏 Forge Study Flashcards", type="primary", use_container_width=True)
        
    with col2:
        st.markdown("### 🗂️ Study Deck Display")
        
        # Action toggles for hidden/visible answers
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            if st.button("👁️ Show All Answers", use_container_width=True):
                st.session_state.show_answers = True
        with t_col2:
            if st.button("🙈 Hide All Answers", use_container_width=True):
                st.session_state.show_answers = False

        st.markdown("---")
        cards_display_placeholder = st.empty()
        
        # Render current generation cache out of storage state safely
        if st.session_state.flashcard_content:
            if st.session_state.show_answers:
                cards_display_placeholder.markdown(st.session_state.flashcard_content)
            else:
                # Mask answer blocks using markdown spoiler syntax
                masked_content = st.session_state.flashcard_content.replace("ANSWER:", "||**ANSWER:**").replace("\n\n#", "||\n\n#")
                if "||" in masked_content and not masked_content.endswith("||"):
                    masked_content += "||"
                cards_display_placeholder.markdown(masked_content)
        else:
            cards_display_placeholder.info("Your flashcards deck will print here. Click answers to reveal them individually or use toggle switches above!")

    if generate_cards_btn and raw_notes.strip():
        st.session_state.stop_generation = False
        st.session_state.show_answers = False
        with col2:
            with st.spinner("Extracting definitions and forging cards..."):
                instr = (
                    f"You are an academic flashcard generator. Extract the absolute core concepts from the user's material "
                    f"and create exactly {num_cards} flashcards. Follow this strict formatting rule for every card:\n\n"
                    f"### 🃏 FLASHCARD X\n"
                    f"**QUESTION:** (Clear concept question here)\n"
                    f"**ANSWER:** (Precise concept answer here)\n\n"
                    f"Do not add any introductory text, match the pattern perfectly."
                )
                payload = [{"role": "system", "content": instr}, {"role": "user", "content": raw_notes}]
                
                final_deck = run_ai_stream(payload, cards_display_placeholder)
                if final_deck:
                    st.session_state.flashcard_content = final_deck
                    st.rerun()
