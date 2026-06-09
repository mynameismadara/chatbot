import streamlit as st
from openai import OpenAI

# 1. Set up the page title and styling
st.set_page_config(page_title="My OpenAI Chatbot", page_icon="🤖")
st.title("💬 My AI Chatbot")
st.write("Ask me anything!")

# 2. Initialize the OpenAI client
# Security Tip: Replace "your-api-key-here" with your actual OpenAI API key.
# Or leave it empty and set it up in Streamlit Cloud's "Secrets" panel later.
API_KEY = "your-api-key-here"
client = OpenAI(api_key=API_KEY)

# 3. Initialize chat history in the session state if it doesn't exist yet
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]

# 4. Display past chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. React to user input
if user_input := st.chat_input("Type your message here..."):

    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(user_input)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate a response from OpenAI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Call the OpenAI API using the recommended chat model
            response = client.chat.completions.create(
                model="gpt-4o-mini", # Fast, smart, and cheap model
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True, # This makes the text type out live!
            )

            # Stream the response chunk by chunk
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.write(full_response + "▌")

            message_placeholder.write(full_response)

        except Exception as e:
            st.error(f"Error: {e}")
            full_response = "Sorry, I ran into an error connecting to OpenAI. Please check your API key."
            message_placeholder.write(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
