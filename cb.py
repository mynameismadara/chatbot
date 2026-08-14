import streamlit as st
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(page_title="Private Portal", page_icon="🔒", layout="wide")

# Initialize Session State Variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "menu"  # Options: 'menu', 'anas_intelligence'

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}  
if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "Chat 1"
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False

if "flashcard_content" not in st.session_state:
    st.session_state.flashcard_content = ""
if "show_answers" not in st.session_state:
    st.session_state.show_answers = False

# Ensure active chat exists in master storage
if st.session_state.current_chat_title not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat_title] = [
        {"role": "assistant", "content": "Secure connection established. System ready."}
    ]

# 2. Check Secrets
try:
    api_key_from_secrets = st.secrets["OPENAI_API_KEY"]
    correct_password = st.secrets["APP_PASSWORD"]
except KeyError:
    st.error("System configuration missing. Access offline.")
    st.stop()

# 3. Password Authentication
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
# EVERYTHING BELOW THIS LINE RUNS ONLY WHEN AUTHENTICATED
# =====================================================================

# 4. Shared API Client & Models
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key_from_secrets
)

free_models_to_try = [
    "meta-llama/llama-4-scout:free",     
    "openai/gpt-oss-20b:free",          
    "meta-llama/llama-3.2-3b-instruct:free",
    "openrouter/free"                    
]

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
# VIEW 1: CENTERED RADIANT MENU
# =====================================================================
if st.session_state.current_view == "menu":
    
    # Custom CSS for Centered Title, Footer, and Card Button Styling
    st.markdown("""
        <style>
        .menu-header {
            text-align: center;
            font-size: 32px;
            font-weight: 600;
            margin-top: 40px;
            margin-bottom: 40px;
            color: #FAFAFA;
            letter-spacing: 1.5px;
        }
        .footer-text {
            position: fixed;
            left: 0;
            bottom: 15px;
            width: 100%;
            text-align: center;
            font-size: 13px;
            color: #888888;
            z-index: 100;
        }
        /* Style Streamlit Button into a Centered Card */
        div.stButton > button {
            width: 100%;
            height: 220px;
            background-color: #1E1E2E;
            border: 1px solid #313244;
            border-radius: 20px;
            color: #CDD6F4;
            font-size: 20px;
            font-weight: 600;
            white-space: pre-wrap;
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            transition: all 0.25s ease-in-out;
            padding: 20px;
        }
        div.stButton > button:hover {
            transform: translateY(-5px);
            border-color: #89B4FA;
            background-color: #26263A;
            box-shadow: 0 10px 25px rgba(137, 180, 250, 0.15);
            color: #FFFFFF;
        }
        </style>
    """, unsafe_allow_html=True)

    # Top Middle Header
    st.markdown("<div class='menu-header'>Radiant</div>", unsafe_allow_html=True)

    # Centered Single Card Button
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        card_text = "🤖\n\nAnas Intelligence\n\nChatbot • Humanizer • Summarizer • Translator • Flashcards"
        if st.button(card_text, key="btn_anas_intelligence", use_container_width=True):
            st.session_state.current_view = "anas_intelligence"
            st.rerun()

    # Bottom Footer
    st.markdown("<div class='footer-text'>2026 made by ?</div>", unsafe_allow_html=True)

# =====================================================================
# VIEW 2: FULL ANAS INTELLIGENCE SUITE
# =====================================================================
elif st.session_state.current_view == "anas_intelligence":

    # 5. Sidebar Navigation
    with st.sidebar:
        # Exit to Menu Button added directly above the critical warning
        if st.button("🔙 Exit to Menu", use_container_width=True):
            st.session_state.current_view = "menu"
            st.rerun()

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
                    {"role": "assistant", "content": "Secure connection established. System ready."}
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

    # Guarantee active key exists
    if st.session_state.current_chat_title not in st.session_state.all_chats:
        st.session_state.current_chat_title = list(st.session_state.all_chats.keys())[0]
    active_messages = st.session_state.all_chats[st.session_state.current_chat_title]

    # MODE 1: ORIGINAL CHATBOT (WITH GEMINI-STYLE SYSTEM PROMPT)
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
                    # Gemini Formatting System Instructions
                    gemini_system_prompt = {
                        "role": "system",
                        "content": (
                            "You are Anas Intelligence, a precise, helpful AI assistant.\n\n"
                            "RESPONSE FORMATTING RULES:\n"
                            "- **Get Straight to the Point:** Do not start responses with generic fluff like 'Sure!', 'Here is a breakdown...', or 'I'd be happy to help'.\n"
                            "- **High Visual Hierarchy:** Use clear Markdown headers (`###`) to separate distinct sections.\n"
                            "- **Bold for Emphasis:** Use bold text (`**key concepts**`) generously to make responses easy to scan.\n"
                            "- **Prefer Lists over Text Walls:** Use bulleted or numbered lists instead of dense paragraphs.\n"
                            "- **Use Tables for Comparisons:** Whenever comparing items or listing specs, present the data in Markdown tables.\n"
                            "- **Clean Code & Formulas:** Format math using LaTeX (`$E=mc^2$`) and wrap code in clean markdown code blocks."
                        )
                    }
                    
                    payload = [gemini_system_prompt] + [{"role": m["role"], "content": m["content"]} for m in active_messages]
                    reply = run_ai_stream(payload, st.empty())
                    if reply:
                        active_messages.append({"role": "assistant", "content": reply})

    # MODE 2: TEXT HUMANIZER
    elif app_mode == "📝 Text Humanizer":
        st.title("📝 Anas Intelligence - Humanizer Mode")
        st.write("Paste paragraphs below to rewrite them with a fluid, natural human flow.")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            user_paragraphs = st.text_area("Paste text or essay here:", height=300, placeholder="Paste text here...", key="humanizer_area")
            humanizer_style = st.selectbox("Choose Style Mode:", ["Formal", "Chill", "Student"])
            submit_button = st.button("✨ Humanize Text", type="primary", use_container_width=True)

        with col2:
            output_placeholder = st.empty()
            output_placeholder.info("Your humanized text will stream here...")

        if submit_button and user_paragraphs.strip():
            st.session_state.stop_generation = False
            with col2, st.spinner("Rewriting..."):
                if humanizer_style == "Formal":
                    style_instruction = (
                        "Rewrite the text to make it sound highly professional, sophisticated, and fluid. "
                        "Use precise and academic vocabulary, eliminate awkward phrasing or robotic patterns, "
                        "and maintain a structured, authoritative, yet completely natural tone."
                    )
                elif humanizer_style == "Chill":
                    style_instruction = (
                        "Rewrite the text to sound completely casual, conversational, and relaxed. "
                        "Use simple vocabulary, blend varied sentence structures naturally, and phrase items "
                        "exactly like a real human would explain something to a close friend in a relaxed chat, "
                        "without using stiff or artificial textbook speech."
                    )
                else: # Student
                    style_instruction = (
                        "Rewrite the text from the perspective of an intelligent high school or university student. "
                        "Keep it clear, straightforward, and readable. Avoid overly complex, archaic words that sound like AI, "
                        "but don't make it unprofessional either. Make it sound like an authentic student assignment or response."
                    )
                    
                instr = f"You are an expert human editor. {style_instruction} Make sure to preserve all key factual data accurately."
                payload = [{"role": "system", "content": instr}, {"role": "user", "content": user_paragraphs}]
                run_ai_stream(payload, output_placeholder)

    # MODE 3: SMART SUMMARIZER
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

    # MODE 4: AI TRANSLATOR
    elif app_mode == "🌐 AI Translator":
        st.title("🌐 Anas Intelligence - Universal AI Translator")
        st.write("Translate source text into any global language using specific style profiles.")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            src_text = st.text_area("Text to Translate:", height=250, placeholder="Type or paste text here...", key="trans_area")
            
            lang_col, style_col = st.columns(2)
            with lang_col:
                target_lang = st.selectbox("Target Language:", global_languages_list, index=0)
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

    # MODE 5: FLASHCARD GENERATOR
    elif app_mode == "🧠 Flashcard Generator":
        st.title("🧠 Anas Intelligence - Smart Flashcard Engine")
        st.write("Input your raw material in English, select your targets, and forge custom multi-language flashcards.")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            raw_notes = st.text_area("Paste Study Material/Prompts (in English):", height=240, placeholder="Type topic ideas or paste English notes here...", key="flash_area")
            
            f_lang_col, f_num_col = st.columns(2)
            with f_lang_col:
                study_lang = st.selectbox("Flashcard Language:", global_languages_list, index=0, key="flash_lang_select")
            with f_num_col:
                num_cards = st.slider("Number of flashcards to forge:", min_value=1, max_value=100, value=5)
                
            generate_cards_btn = st.button("🃏 Forge Study Flashcards", type="primary", use_container_width=True)
            
        with col2:
            st.markdown("### 🗂️ Study Deck Display")
            
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                if st.button("👁️ Show All Answers", use_container_width=True):
                    st.session_state.show_answers = True
            with t_col2:
                if st.button("🙈 Hide All Answers", use_container_width=True):
                    st.session_state.show_answers = False

            st.markdown("---")
            cards_display_placeholder = st.empty()
            
            if st.session_state.flashcard_content:
                if st.session_state.show_answers:
                    cards_display_placeholder.markdown(st.session_state.flashcard_content)
                else:
                    masked_content = st.session_state.flashcard_content.replace("ANSWER:", "||**ANSWER:**").replace("\n\n#", "||\n\n#")
                    if "||" in masked_content and not masked_content.endswith("||"):
                        masked_content += "||"
                    cards_display_placeholder.markdown(masked_content)
            else:
                cards_display_placeholder.info("Your translated study deck will build here. Click individual answers to reveal them or use the toggles!")

        if generate_cards_btn and raw_notes.strip():
            st.session_state.stop_generation = False
            st.session_state.show_answers = False
            with col2:
                with st.spinner(f"Processing English material and translation to {study_lang}..."):
                    instr = (
                        f"You are an elite academic flashcard generator and language expert. Read the user's English material "
                        f"and generate exactly {num_cards} distinct flashcards to help study. "
                        f"CRITICAL: The entire content of the flashcards (both questions and answers) MUST be written completely in {study_lang}. "
                        f"Translate the underlying English context seamlessly.\n\n"
                        f"Follow this strict layout formatting for every single card:\n\n"
                        f"### 🃏 FLASHCARD X\n"
                        f"**QUESTION:** (Write question here in {study_lang})\n"
                        f"**ANSWER:** (Write answer here in {study_lang})\n\n"
                        f"Do not include any greeting or conversational fluff, return only the formatted cards."
                    )
                    payload = [{"role": "system", "content": instr}, {"role": "user", "content": raw_notes}]
                    
                    final_deck = run_ai_stream(payload, cards_display_placeholder)
                    if final_deck:
                        st.session_state.flashcard_content = final_deck
                        st.rerun()
