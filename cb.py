import streamlit as st
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(page_title="Private Portal", page_icon="🔒", layout="wide")

# Initialize Master Chat Storage to track multiple conversations
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}  
if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "Chat 1"
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False

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

# 5. Sidebar Navigation & Active Recent Chats Management
with st.sidebar:
    st.error("⚠️ **CRITICAL WARNING:** Exiting, refreshing, or closing this browser tab will permanently delete all chat history and active sessions!")
    st.markdown("---")
    
    st.title("🤖 Navigation")
    # Added the 3rd option right into your main control dropdown
    app_mode = st.selectbox("Choose Mode:", ["💬 Original Chatbot", "📝 Text Humanizer", "📊 Smart Summarizer"])
    
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

# Guarantee active key exists
if st.session_state.current_chat_title not in st.session_state.all_chats:
    st.session_state.current_chat_title = list(st.session_state.all_chats.keys())[0]
active_messages = st.session_state.all_chats[st.session_state.current_chat_title]

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
                response_stream = None
                for model_slug in free_models_to_try:
                    try:
                        client_kwargs = {
                            "model": model_slug,
                            "messages": [{"role": m["role"], "content": m["content"]} for m in active_messages],
                            "stream": True
                        }
                        response_stream = client.chat.completions.create(**client_kwargs)
                        break
                    except Exception:
                        continue
                
                if response_stream is not None:
                    try:
                        message_placeholder = st.empty()
                        full_response = ""
                        for chunk in response_stream:
                            if st.session_state.stop_generation:
                                full_response += "... [Generation Stopped by User]"
                                break
                            if chunk.choices[0].delta.content:
                                full_response += chunk.choices[0].delta.content
                                message_placeholder.markdown(full_response + "▌")
                        message_placeholder.markdown(full_response)
                        active_messages.append({"role": "assistant", "content": full_response})
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("All free models are currently busy. Please try again in a moment!")

# =====================================================================
# MODE 2: TEXT HUMANIZER
# =====================================================================
elif app_mode == "📝 Text Humanizer":
    st.title("📝 Anas Intelligence - Humanizer Mode")
    st.write("Paste long paragraphs below to rewrite them with a fluid, natural human flow.")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("### 📤 Input Paragraphs")
        user_paragraphs = st.text_area("Paste your text or essay here:", height=350, placeholder="Type or paste paragraphs here...", key="humanizer_area")
        submit_button = st.button("✨ Humanize Text", type="primary", use_container_width=True)

    with col2:
        st.markdown("### 📥 Humanized Output")
        output_placeholder = st.empty()
        output_placeholder.info("Your humanized text will stream here word-by-word...")

    if submit_button and user_paragraphs.strip():
        st.session_state.stop_generation = False
        with col2:
            with st.spinner("Analyzing text flow and rewriting..."):
                humanizer_instructions = (
                    "You are an expert human editor. Rewrite the user's text to make it sound completely natural, "
                    "fluid, and engaging. Vary sentence lengths, improve flow, and eliminate robotic patterns."
                )
                response_stream = None
                for model_slug in free_models_to_try:
                    try:
                        client_kwargs = {
                            "model": model_slug,
                            "messages": [
                                {"role": "system", "content": humanizer_instructions},
                                {"role": "user", "content": f"Humanize this text:\n\n{user_paragraphs}"}
                            ],
                            "stream": True
                        }
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
                                output_placeholder.markdown(full_response + "▌")
                        output_placeholder.markdown(full_response)
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("All free models are currently busy!")

# =====================================================================
# NEW MODE 3: SMART SUMMARIZER & EXTRACTOR
# =====================================================================
elif app_mode == "📊 Smart Summarizer":
    st.title("📊 Anas Intelligence - Smart Summarizer")
    st.write("Turn huge text documents, articles, or notes into scannable, key-point breakdowns.")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("### 📤 Input Document Text")
        heavy_text = st.text_area("Paste your long reading material here:", height=350, placeholder="Paste heavy articles or notes here...", key="summary_area")
        summarize_button = st.button("⚡ Extract Insights", type="primary", use_container_width=True)

    with col2:
        st.markdown("### 📥 Scannable Breakdown")
        summary_placeholder = st.empty()
        summary_placeholder.info("The summary dashboard will build out here word-by-word...")

    if summarize_button and heavy_text.strip():
        st.session_state.stop_generation = False
        with col2:
            with st.spinner("Processing document data..."):
                summarizer_instructions = (
                    "You are an elite data analyst. Process the user's heavy text and return a beautifully formatted "
                    "summary. Structure it exactly like this:\n"
                    "## 📋 Executive Summary\n(A brief 2-3 sentence overview)\n\n"
                    "## 🔑 Key Takeaways\n(A clean bulleted list of the most critical facts)\n\n"
                    "## 🧠 Core Terms & Concepts\n(Define any complex vocabulary or central ideas present)"
                )
                response_stream = None
                for model_slug in free_models_to_try:
                    try:
                        client_kwargs = {
                            "model": model_slug,
                            "messages": [
                                {"role": "system", "content": summarizer_instructions},
                                {"role": "user", "content": f"Summarize this text:\n\n{heavy_text}"}
                            ],
                            "stream": True
                        }
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
                                summary_placeholder.markdown(full_response + "▌")
                        summary_placeholder.markdown(full_response)
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("All free models are currently busy!")
