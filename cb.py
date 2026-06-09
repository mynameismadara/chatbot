import streamlit as st
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(page_title="Secure Chatbot", page_icon="🔒")

# 2. Check for required secrets
try:
    api_key_from_secrets = st.secrets["OPENAI_API_KEY"]
    correct_password = st.secrets["APP_PASSWORD"]
except KeyError:
    st.error("Missing configuration! Please check your Streamlit Advanced Settings -> Secrets.")
    st.stop()

# 3. Simple Password Protection Interface
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Password Protected AI")
    user_password = st.text_input("Enter Passcode to Access AI:", type="password")
    
    if st.button("Unlock"):
        if user_password == correct_password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect passcode. Access Denied.")
    st.stop()  # Stops the script here so unauthorized users see nothing below

# =====================================================================
# EVERYTHING BELOW THIS LINE ONLY RUNS IF THE PASSWORD IS CORRECT
# =====================================================================

# 4. Title of your web app
st.title("💬 My Private AI Chatbot")
st.write("Welcome back! The secure connection is active.")

# 5. Initialize the client to talk to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key_from_secrets
)

# 6. Initialize the chat history if it doesn't exist yet
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Authorized user detected. How can I help you today?"}
    ]

# 7. Display all previous messages on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 8. Handle new user input
if user_input := st.chat_input("Type your message here..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            # Smart fallback list to handle rate limits
            free_models_to_try = [
                "meta-llama/llama-3.2-3b-instruct:free",
                "mistralai/mistral-7b-instruct:free",
                "openchat/openchat-7b:free",
                "openrouter/free"
            ]
            
            response_stream = None
            
            for model_slug in free_models_to_try:
                try:
                    response_stream = client.chat.completions.create(
                        model=model_slug,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True
                    )
                    break
                except Exception:
                    continue
            
            if response_stream is not None:
                try:
                    assistant_reply = st.write_stream(response_stream)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                except Exception as e:
                    st.error(f"Error displaying response: {e}")
            else:
                st.error("All free models are currently heavily loaded. Please wait a moment and try again!")
