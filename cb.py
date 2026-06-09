import streamlit as st
from openai import OpenAI

# 1. Title of your web app
st.title("💬 My Smart Free AI Chatbot")
st.write("Equipped with auto-fallback to dodge rate limits!")

# 2. Securely get the API key from Streamlit's Secrets manager
try:
    api_key_from_secrets = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("Missing API Key! Please add OPENAI_API_KEY to your Streamlit Advanced Settings -> Secrets.")
    st.stop()

# 3. Initialize the client to talk to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
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
            
            # A list of completely free models to try in order if one is rate-limited
            free_models_to_try = [
                "meta-llama/llama-3.2-3b-instruct:free",
                "mistralai/mistral-7b-instruct:free",
                "openchat/openchat-7b:free",
                "openrouter/free"  # Final backup catch-all
            ]
            
            response_stream = None
            
            # Loop through our models until one successfully answers
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
                    # If it succeeded, break out of the loop!
                    break
                except Exception as model_error:
                    # If this model failed/rate-limited, ignore it and try the next one
                    continue
            
            # Try to output the stream if we found a working model
            if response_stream is not None:
                try:
                    # Use Streamlit's typewriter effect to display words instantly
                    assistant_reply = st.write_stream(response_stream)
                    # Save the final completed message to history
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                except Exception as e:
                    st.error(f"Error displaying response: {e}")
            else:
                st.error("All free models are currently heavily loaded. Please wait a moment and try sending your message again!")
