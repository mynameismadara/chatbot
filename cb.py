import streamlit as st
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(page_title="Anas Intelligence", page_icon="🤖")

# Initialize stop flag in session state
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False

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
    st.stop()

# =====================================================================
# EVERYTHING BELOW THIS LINE ONLY RUNS IF THE PASSWORD IS CORRECT
# =====================================================================

# 4. Title of your web app
st.title("🤖 Anas Intelligence 👍")
st.write("Welcome to your private, high-speed AI assistant.")

# Create a sidebar button to reset or stop generation if needed
with st.sidebar:
    if st.button("🛑 Force Stop AI"):
        st.session_state.stop_generation = True
        st.toast("Stopping current generation...")

# 5. Initialize the client to talk to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key_from_secrets
)

# 6. Initialize the chat history if it doesn't exist yet
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Anas Intelligence is online and ready. How can I help you today?"}
    ]

# 7. Display all previous messages on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 8. Handle new user input
if user_input := st.chat_input("Ask Anas Intelligence something..."):
    # Reset the stop flag for a new prompt
    st.session_state.stop_generation = False
    
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            # Fast, low-latency free models
            free_models_to_try = [
                "meta-llama/llama-4-scout:free",     
                "openai/gpt-oss-20b:free",          
                "meta-llama/llama-3.2-3b-instruct:free",
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
                    # Create an empty placeholder to type into word-by-word
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Manual streaming loop so we can intercept and stop it
                    for chunk in response_stream:
                        # Check if user clicked the sidebar stop button
                        if st.session_state.stop_generation:
                            full_response += "... [Generation Stopped by User]"
                            break
                            
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                    
                    # Clean up the trailing cursor character
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    st.error(f"Error displaying response: {e}")
            else:
                st.error("All free models are currently heavily loaded. Please wait a moment and try again!")
