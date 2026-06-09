import streamlit as st
from openai import OpenAI

# 1. Title of your web app
st.title("💬 My OpenRouter AI Chatbot")
st.write("Running completely free with high-speed Llama streaming!")

# 2. Securely get the API key from Streamlit's Secrets manager
try:
    api_key_from_secrets = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("Missing API Key! Please add OPENAI_API_KEY to your Streamlit Advanced Settings -> Secrets.")
    st.stop()

# 3. Initialize the client to talk to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",  # Redirects to OpenRouter's free servers
    api_key=api_key_from_secrets
)

# 4. Initialize the chat history if it doesn't exist yet
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]

# 5. Display all previous messages on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Handle new user input
if user_input := st.chat_input("Type your message here..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Ask OpenRouter to stream from a reliable, permanent free model
                response_stream = client.chat.completions.create(
                    model="meta-llama/llama-3.3-70b-instruct:free",  # High-speed open source free model
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True  # Stream words instantly as they are generated
                )
                
                # Use Streamlit's typewriter effect to display words instantly
                assistant_reply = st.write_stream(response_stream)
                
                # Save the final completed message to history
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                
            except Exception as e:
                st.error(f"Something went wrong: {e}")
