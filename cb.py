import streamlit as st
from openai import OpenAI

# 1. Title of your web app
st.title("💬 My AI Chatbot")
st.write("Welcome! Ask me anything.")

# 2. Securely get the API key from Streamlit's Secrets manager
# This prevents the "Incorrect API key" error by pulling directly from your settings box.
try:
    api_key_from_secrets = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("Missing API Key! Please add OPENAI_API_KEY to your Streamlit Advanced Settings -> Secrets.")
    st.stop()

# 3. Initialize the OpenAI client
client = OpenAI(api_key=api_key_from_secrets)

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
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # Fast, smart, and efficient model
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                )
                assistant_reply = response.choices[0].message.content
                st.write(assistant_reply)
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            except Exception as e:
                st.error(f"Something went wrong: {e}")
