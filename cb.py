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

# 3. Disguised Secure Password Protection Interface
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

# Shared Global Languages Array
global_languages_list = [
    "French", "Spanish", "German", "Chinese (Simplified)", "Chinese (Traditional)", "Arabic", 
    "Japanese", "Italian", "Portuguese", "Hindi", "Korean", "Russian", "Turkish", "Afrikaans", 
    "Albanian", "Amharic", "Armenian", "Azerbaijani", "Basque", "Belarusian", "Bengali", 
    "Bosnian", "Bulgarian", "Burmese", "Catalan", "Cebuano", "Chichewa", "Corsican", 
    "Croatian", "Czech", "Danish", "Dutch", "English", "Esperanto", "Estonian", 
    "Filipino (Tagalog)", "Finnish", "Frisian", "Galician", "Georgian", "Greek", 
    "Gujarati", "Haitian Creole", "Hausa", "Hawaiian", "Hebrew", "Hmong", "Hungarian", 
    "Icelandic", "Igbo", "Indonesian", "Irish", "Javanese", "Kannada", "Kazakh", 
    "Khmer", "Kinyarwanda", "Kurdish (Kurmanji)", "Kurdish (Sorani)", "Kyrgyz", "Lao", 
    "Latin", "Latvian", "Lithuanian", "Luxembourgish", "Macedonian", "Malagasy", "Malay", 
    "Malayalam", "Maltese", "Maori", "Marathi", "Mongolian", "Nepali", "Norwegian", 
    "Odia (Oriya)", "Pashto", "Persian", "Polish", "Punjabi", "Romanian", "Samoan", 
    "Scots Gaelic", "Serbian", "Sesotho", "Shona", "Sindhi", "Sinhala", "Slovak", 
    "Slovenian", "Somali", "Sundanese", "Swahili", "Swedish", "Tajik", "Tamil", 
    "Tatar", "Telugu", "Thai", "Turkmen", "Ukrainian", "Urdu", "Uyghur", "Uzbek", 
    "Vietnamese", "Welsh", "Xhosa", "Yiddish", "Yoruba", "Zulu"
]

# 5. Sidebar Navigation
with st.sidebar:
    st.error("⚠️ **CRITICAL WARNING:** Exiting, refreshing, or closing this browser tab will permanently delete all history!")
    st.markdown("---")
    
    st.title("🤖 Navigation")
    app_mode = st.selectbox(
        "Choose Mode:", 
        ["💬 Original Chatbot", "📝 Text Humanizer", "📊 Smart Summarizer", "🌐 AI Translator", "🧠 Flashcard Generator"]
    )
    
    st.markdown("---")
    
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
                
    if st.button("🛑 Force Stop AI", use_container_width=True):
        st.session_state.stop_generation = True
        st.toast("Stopping generation...")

# Current Chat Logic
if st.session_state.current_chat_title not in st.session_state.all_chats:
    st.session_state.current_chat_title = list(st.session_state.all_chats.keys())[0]
active_messages = st.session_state.all_chats[st.session_state.current_chat_title]

# Fixed AI Stream Function
def run_ai_stream(messages_payload, placeholder):
    global free_models_to_try
    response_stream = None
    for model_slug in free_models_to_try:
        try:
            client_kwargs = {"model": model_slug, "messages": messages_payload, "stream": True}
            # FIXED: Removed the space between 'com' and 'pletions'
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
        st.error("All free models are currently busy. Try again shortly!")
        return None

# =====================================================================
# MODES
# =====================================================================

if app_mode == "💬 Original Chatbot":
    st.title("🤖 Artificial Intelligence")
    st.caption(f"Room: **{st.session_state.current_chat_title}**")

    for message in active_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if user_input := st.chat_input("Ask Artificial Intelligence something..."):
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

elif app_mode == "📝 Text Humanizer":
    st.title("📝 Artificial Intelligence - Humanizer Mode")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        user_paragraphs = st.text_area("Paste text here:", height=300, key="humanizer_area")
        humanizer_style = st.selectbox("Style Mode:", ["Formal", "Chill", "Student"])
        submit_button = st.button("✨ Humanize Text", type="primary", use_container_width=True)

    with col2:
        output_placeholder = st.empty()
        if submit_button and user_paragraphs.strip():
            st.session_state.stop_generation = False
            with st.spinner("Rewriting..."):
                if humanizer_style == "Formal":
                    style_instruction = "highly professional, sophisticated, and fluid."
                elif humanizer_style == "Chill":
                    style_instruction = "conversational, relaxed, and natural."
                else:
                    style_instruction = "intelligent student perspective, clear and straightforward."
                
                instr = f"You are a human editor. Rewrite this to be {style_instruction} Preserve all facts."
                payload = [{"role": "system", "content": instr}, {"role": "user", "content": user_paragraphs}]
                run_ai_stream(payload, output_placeholder)

elif app_mode == "📊 Smart Summarizer":
    st.title("📊 Artificial Intelligence - Smart Summarizer")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        heavy_text = st.text_area("Paste material:", height=350, key="summary_area")
        summarize_button = st.button("⚡ Extract Insights", type="primary", use_container_width=True)

    with col2:
        summary_placeholder = st.empty()
        if summarize_button and heavy_text.strip():
            st.session_state.stop_generation = False
            with st.spinner("Analyzing..."):
                instr = "Process text and return: ## 📋 Executive Summary, ## 🔑 Key Takeaways, ## 🧠 Core Terms."
                payload = [{"role": "system", "content": instr}, {"role": "user", "content": heavy_text}]
                run_ai_stream(payload, summary_placeholder)

elif app_mode == "🌐 AI Translator":
    st.title("🌐 Artificial Intelligence - Universal AI Translator")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        src_text = st.text_area("Translate this:", height=250, key="trans_area")
        target_lang = st.selectbox("Target Language:", global_languages_list)
        translation_style = st.selectbox("Tone:", ["Literal/Exact", "Natural/Casual", "Formal/Business"])
        translate_button = st.button("🚀 Translate Text", type="primary", use_container_width=True)

    with col2:
        trans_placeholder = st.empty()
        if translate_button and src_text.strip():
            st.session_state.stop_generation = False
            with st.spinner("Translating..."):
                instr = f"Translate to {target_lang} in a {translation_style} style."
                payload = [{"role": "system", "content": instr}, {"role": "user", "content": src_text}]
                run_ai_stream(payload, trans_placeholder)

elif app_mode == "🧠 Flashcard Generator":
    st.title("🧠 Artificial Intelligence - Smart Flashcard Engine")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        raw_notes = st.text_area("English Notes:", height=240, key="flash_area")
        study_lang = st.selectbox("Flashcard Language:", global_languages_list, key="f_lang")
        num_cards = st.slider("Number of cards:", 1, 100, 5)
        generate_cards_btn = st.button("🃏 Forge Cards", type="primary", use_container_width=True)
        
    with col2:
        st.markdown("### 🗂️ Study Deck")
        t_col1, t_col2 = st.columns(2)
        if t_col1.button("👁️ Show All"): st.session_state.show_answers = True
        if t_col2.button("🙈 Hide All"): st.session_state.show_answers = False

        st.markdown("---")
        cards_display = st.empty()
        
        if st.session_state.flashcard_content:
            content = st.session_state.flashcard_content
            if not st.session_state.show_answers:
                content = content.replace("ANSWER:", "||**ANSWER:**").replace("\n\n#", "||\n\n#")
            cards_display.markdown(content)

    if generate_cards_btn and raw_notes.strip():
        st.session_state.stop_generation = False
        with st.spinner("Generating..."):
            instr = f"Generate {num_cards} cards in {study_lang}. Format: ### 🃏 FLASHCARD X, **QUESTION:**, **ANSWER:**"
            payload = [{"role": "system", "content": instr}, {"role": "user", "content": raw_notes}]
            final_deck = run_ai_stream(payload, cards_display)
            if final_deck:
                st.session_state.flashcard_content = final_deck
                st.rerun()
