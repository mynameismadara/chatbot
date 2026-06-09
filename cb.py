import streamlit as st
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(page_title="Anas Intelligence - Humanizer", page_icon="📝", layout="wide")

# Initialize stop flag
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

# 4. App Headers
st.title("🤖 Anas Intelligence 👍")
st.subheader("⚡ Professional Paragraph Humanizer")
st.write("Paste your paragraphs below to rewrite them with a natural, human-like flow and tone.")

# 5. Initialize the client to talk to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key_from_secrets
)

# 6. Setup Layout Columns (Input on Left, Output on Right)
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 📤 Input Paragraphs")
    # A text area is perfect for long, multi-line blocks of text
    user_paragraphs = st.text_area(
        label="Paste your long text here:", 
        height=350, 
        placeholder="Paste your text or essay here..."
    )
    
    # Action buttons arranged horizontally
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        submit_button = st.button("✨ Humanize Text", type="primary", use_container_width=True)
    with btn_col2:
        stop_button = st.button("🛑 Stop Generation", type="secondary", use_container_width=True)
        if stop_button:
            st.session_state.stop_generation = True

with col2:
    st.markdown("### 📥 Humanized Output")
    output_placeholder = st.empty()
    # Provide a static box style before generation starts
    output_placeholder.info("Your humanized text will stream here word-by-word...")

# 7. Process Text When Button is Clicked
if submit_button and user_paragraphs.strip():
    st.session_state.stop_generation = False
    
    with col2:
        with st.spinner("Analyzing text flow and rewriting..."):
            
            # The secret sauce: engineering the system instructions for humanization
            humanizer_instructions = (
                "You are an expert human editor. Rewrite the user's text to make it sound completely natural, "
                "fluid, and engaging, as if written by an authentic human author. Vary sentence lengths, improve "
                "flow, use idiomatic phrasing and creative transitions where appropriate, and eliminate typical robotic "
                "or repetitive patterns. Maintain the original core facts, message, and meaning perfectly."
            )
            
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
                            {"role": "system", "content": humanizer_instructions},
                            {"role": "user", "content": f"Humanize this text:\n\n{user_paragraphs}"}
                        ],
                        stream=True
                    )
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
                            # Live update the text area box on the right side
                            output_placeholder.markdown(full_response + "▌")
                    
                    # Finalize output text box
                    output_placeholder.markdown(full_response)
                    
                except Exception as e:
                    st.error(f"Error processing stream: {e}")
            else:
                st.error("All free models are currently heavily loaded. Please wait a moment and try again!")
