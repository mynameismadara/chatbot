import streamlit as st
from openai import OpenAI

# 1. Page Configuration (Generic title to hide AI footprint)
st.set_page_config(page_title="Private Portal", page_icon="🔒", layout="wide")

# Initialize stop flag and temporary instant-message box
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False

# Chats are kept in a single temporary session list that wipes on refresh
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Secure connection established. System ready."}
    ]

# 2. Check for required secrets
try:
    api_key_from_secrets = st.secrets["OPENAI_API_KEY"]
    correct_password = st.secrets["APP_PASSWORD"]
except KeyError:
    st.error("System configuration missing. Access offline.")
    st.stop()

# 3. Disguised Secure Password Protection Interface (No mention of AI)
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

# 5. Sidebar Navigation Menu
with st.sidebar:
    st.title("🤖 Navigation")
    app_mode = st.selectbox("Choose Mode:", ["💬 Original Chatbot", "📝 Text Humanizer"])
    
    st.markdown("---")
    if st.button("🛑 Force Stop AI", use_container_width=True):
        st.session_state.stop_generation = True
        st.toast("Stopping generation...")
        
    st.markdown("---")
    st.caption("🔒 Incognito Active: Closing or refreshing this tab destroys all data permanently.")

# =====================================================================
# MODE 1: ORIGINAL CHATBOT (TEMPORARY INCIGNITO CHAT)
# =====================================================================
if app_mode == "💬 Original Chatbot":
    st.title("🤖 Anas Intelligence 👍")
    st.write("Welcome to your private, high-speed AI assistant.")

    # Display temporary session messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Handle new user chat input
    if user_input := st.chat_input("Ask Anas Intelligence something..."):
        st.session_state.stop_generation = False
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_stream = None
                for model_slug in free_models_to_try:
                    try:
                        client_kwargs = {
                            "model": model_slug,
                            "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
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
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
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
        user_paragraphs = st.text_area("Paste your text or essay here:", height=350, placeholder="Type or paste paragraphs here...")
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
                    "fluid, and engaging, as if written by an authentic human author. Vary sentence lengths, improve "
                    "flow, use natural transitions, and eliminate typical robotic patterns while keeping the exact original facts."
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
                    st.error("All free models are currently busy. Please try again in a moment!")
