import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from duckduckgo_search import DDGS

# 1. Page Configuration
st.set_page_config(page_title="Private Portal", page_icon="🔒", layout="wide")

# Initialize Session State Variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "menu"  # Options: 'menu', 'anas_intelligence', 'search_engine'

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

# Initialize Tavily Client if key exists
tavily_api_key = st.secrets.get("TAVILY_API_KEY", None)

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

# Global System Instructions for Gemini-style clean formatting
GEMINI_FORMATTING_PROMPT = """
You are Anas Intelligence, an ultra-precise, highly factual, and articulate AI assistant.

CRITICAL FORMATTING RULES FOR ALL RESPONSES:
- **Zero Fluff:** Never start with generic filler sentences like "Sure, here is...", "As an AI...", or "Here is a breakdown...". Jump straight into the core content.
- **High Visual Hierarchy:** Divide long answers using clear Markdown subheaders (`### Section Title`).
- **Scannable Bolding:** Bold key terms, important numbers, and critical phrases (`**bold text**`) so the response can be skimmed in seconds.
- **Lists over Text Walls:** Use bullet points or numbered lists instead of dense paragraphs. Keep bullet points concise and punchy.
- **Tables for Comparisons:** Whenever comparing specs, features, dates, or items, always output standard Markdown tables.
- **Clean Code & Formulas:** Wrap code in Markdown blocks and format math using clean LaTeX syntax.
- **Strict Factual Accuracy:** Never invent hardware names, stats, or fake data.
"""

# 4. Shared API Client & High-Quality Free Models
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key_from_secrets
)

free_models_to_try = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "openai/gpt-oss-120b:free",
    "google/gemma-4-31b-it:free",
    "openai/gpt-oss-20b:free",
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

# Inject Global Custom CSS for Clean UI Elements
st.markdown("""
    <style>
    /* Input Boxes & TextAreas Styling */
    .stTextArea textarea, .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #313244 !important;
        background-color: #181825 !important;
        color: #CDD6F4 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #89B4FA !important;
        box-shadow: 0 0 8px rgba(137, 180, 250, 0.2) !important;
    }

    /* Clean Card Container Styling */
    [data-testid="stForm"], div[data-testid="stExpander"], div.stContainer {
        border-radius: 14px;
    }

    /* Chat Messages Styling */
    .stChatMessage {
        border-radius: 14px !important;
        padding: 1rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Header Polish */
    h1, h2, h3 {
        letter-spacing: -0.5px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# VIEW 1: ABSOLUTE CENTERED RADIANT MENU (SIDE-BY-SIDE BUTTONS)
# =====================================================================
if st.session_state.current_view == "menu":
    
    st.markdown("""
        <style>
        .main .block-container {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            min-height: 85vh !important;
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            max-width: 900px !important;
        }

        .menu-header {
            text-align: center;
            font-size: 52px;
            font-weight: 800;
            margin-bottom: 30px;
            color: #FAFAFA;
            letter-spacing: 3px;
            text-transform: uppercase;
            width: 100%;
        }

        /* Pull layout columns close together */
        div[data-testid="stHorizontalBlock"] {
            gap: 12px !important;
            justify-content: center !important;
        }

        div[data-testid="stColumn"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            flex: 1 1 0px !important;
        }

        div.stButton {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
        }

        /* Style Menu Card Buttons */
        div.stButton > button {
            width: 100% !important;
            max-width: 380px !important;
            height: 270px !important;
            background-color: #1E1E2E !important;
            border: 1px solid #313244 !important;
            border-radius: 24px !important;
            color: #CDD6F4 !important;
            font-size: 22px !important;
            font-weight: 700 !important;
            white-space: pre-wrap !important;
            box-shadow: 0 8px 28px rgba(0,0,0,0.4) !important;
            transition: all 0.25s ease-in-out !important;
            padding: 24px !important;
            line-height: 1.4 !important;
            margin: 0 auto !important;
        }

        div.stButton > button:hover {
            transform: translateY(-6px) !important;
            border-color: #89B4FA !important;
            background-color: #26263A !important;
            box-shadow: 0 12px 30px rgba(137, 180, 250, 0.2) !important;
            color: #FFFFFF !important;
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
        </style>
    """, unsafe_allow_html=True)

    # 1. Header Title
    st.markdown("<div class='menu-header'>Radiant</div>", unsafe_allow_html=True)

    # 2. Side-by-Side Menu Buttons (Tightly Aligned)
    col1, col2 = st.columns(2)
    
    with col1:
        card_text_1 = "🤖\n\nAnas Intelligence\n\n💬 Chatbot • 📝 Humanizer\n📊 Summarizer • 🌐 Translator\n🧠 Flashcards"
        if st.button(card_text_1, key="btn_anas_intelligence", use_container_width=True):
            st.session_state.current_view = "anas_intelligence"
            st.rerun()

    with col2:
        card_text_2 = "🔍\n\nSearch Engine\n\n🔎 DuckDuckGo • ⚡ Tavily AI\n🌐 Web Proxy • 📖 Reader"
        if st.button(card_text_2, key="btn_search_engine", use_container_width=True):
            st.session_state.current_view = "search_engine"
            st.rerun()

    st.markdown("<div class='footer-text'>2026 made by ?</div>", unsafe_allow_html=True)

# =====================================================================
# VIEW 2: FULL-PAGE UNBLOCKED SEARCH ENGINE
# =====================================================================
elif st.session_state.current_view == "search_engine":

    # Full page wide layout setup
    st.markdown("<style>.main .block-container { padding-top: 1.5rem !important; max-width: 95% !important; }</style>", unsafe_allow_html=True)

    top_col1, top_col2 = st.columns([1, 10])
    with top_col1:
        if st.button("🔙 Menu", use_container_width=True):
            st.session_state.current_view = "menu"
            st.rerun()

    st.title("🔍 Cloud Search Engine")
    st.caption("Bypass network restrictions to query live web answers, read articles, or proxy web pages.")

    search_mode = st.radio("Choose Search Tool:", ["🔎 DuckDuckGo Native", "⚡ Tavily AI Search", "🌐 Unblocked Web Proxy", "📖 Cloud Article Reader"], horizontal=True)

    st.markdown("---")

    # TOOL 1: DUCKDUCKGO NATIVE SEARCH
    if search_mode == "🔎 DuckDuckGo Native":
        with st.form(key="ddg_search_form"):
            ddg_query = st.text_input("Enter Search Query:", placeholder="e.g. Python programming or global news", key="ddg_input")
            ddg_submit = st.form_submit_button(label="Search Web", type="primary")

        if ddg_submit and ddg_query.strip():
            with st.spinner("Fetching DuckDuckGo search results..."):
                try:
                    results = list(DDGS().text(ddg_query, max_results=10))

                    if results:
                        st.subheader(f"Results for: '{ddg_query}'")
                        for item in results:
                            st.markdown(f"### [{item['title']}]({item['href']})")
                            st.write(item['body'])
                            st.caption(f"Source: {item['href']}")
                            st.write("")
                    else:
                        st.warning("No results found. Try a different search term.")
                except Exception as e:
                    st.error(f"Search error: {str(e)}")

    # TOOL 2: AI LIVE WEB SEARCH (TAVILY)
    elif search_mode == "⚡ Tavily AI Search":
        if not tavily_api_key:
            st.warning("⚠️ `TAVILY_API_KEY` missing in Streamlit Secrets. Please add it to enable live cloud searches.")
        else:
            from tavily import TavilyClient
            tavily_client = TavilyClient(api_key=tavily_api_key)

            search_query = st.text_input("Enter Topic, Question, or News Query:", placeholder="e.g., What are the latest developments in quantum computing?", key="tavily_query")
            
            col_search, col_depth = st.columns([4, 1])
            with col_search:
                run_search = st.button("🚀 Search Web", type="primary", use_container_width=True)
            with col_depth:
                depth_val = st.selectbox("Depth:", ["basic", "advanced"], key="search_depth_select")

            if run_search and search_query.strip():
                st.session_state.stop_generation = False
                with st.spinner("Fetching live web data via cloud..."):
                    try:
                        res = tavily_client.search(query=search_query, search_depth=depth_val, max_results=6)
                        
                        web_snippets = ""
                        for item in res.get("results", []):
                            web_snippets += f"• **Title:** {item['title']}\n  **URL:** {item['url']}\n  **Snippet:** {item['content']}\n\n"

                        st.markdown("### 📋 AI Summarized Answer")
                        ans_container = st.container(border=True)
                        with ans_container:
                            placeholder = st.empty()
                            
                            system_prompt = (
                                f"{GEMINI_FORMATTING_PROMPT}\n\n"
                                "You are a world-class web researcher. Use the provided real-time search context "
                                "to write an accurate, highly structured, and readable answer. Cite source URLs where applicable."
                            )
                            user_prompt = f"User Question: {search_query}\n\nLive Search Data:\n{web_snippets}"
                            
                            payload = [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ]
                            run_ai_stream(payload, placeholder)

                        with st.expander("🔗 Source Links Found"):
                            for item in res.get("results", []):
                                st.markdown(f"- **[{item['title']}]({item['url']})**")
                    except Exception as e:
                        st.error(f"Search failed: {e}")

    # TOOL 3: UNBLOCKED WEB PROXY
    elif search_mode == "🌐 Unblocked Web Proxy":
        st.write("Enter any website URL below to fetch and render its HTML content server-side.")
        
        target_url = st.text_input("Enter Web Address (URL):", placeholder="https://en.wikipedia.org/wiki/Main_Page", key="proxy_url_input")
        load_proxy_btn = st.button("🚀 Load Unblocked Page", type="primary")

        if load_proxy_btn and target_url.strip():
            if not target_url.startswith(("http://", "https://")):
                target_url = "https://" + target_url

            with st.spinner("Fetching page on cloud server..."):
                try:
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    response = requests.get(target_url, headers=headers, timeout=12)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        
                        # Fix relative links and images
                        for img in soup.find_all("img", src=True):
                            img["src"] = urljoin(target_url, img["src"])
                        for a in soup.find_all("a", href=True):
                            a["href"] = urljoin(target_url, a["href"])

                        # Strip script tags for clean sandbox execution
                        for script in soup(["script"]):
                            script.decompose()

                        st.markdown("---")
                        # Full-width component frame
                        st.components.v1.html(str(soup), height=800, scrolling=True)
                    else:
                        st.error(f"Could not load page. Server returned status code: {response.status_code}")
                except Exception as e:
                    st.error(f"Proxy Connection Error: {e}")

    # TOOL 4: CLOUD ARTICLE READER
    elif search_mode == "📖 Cloud Article Reader":
        if not tavily_api_key:
            st.warning("⚠️ `TAVILY_API_KEY` missing in Streamlit Secrets. Please add it to enable article extraction.")
        else:
            from tavily import TavilyClient
            tavily_client = TavilyClient(api_key=tavily_api_key)

            article_url = st.text_input("Paste Article / Webpage URL:", placeholder="https://en.wikipedia.org/wiki/Computer_science", key="extract_url_input")
            extract_btn = st.button("📖 Extract Full Article", type="primary")

            if extract_btn and article_url.strip():
                with st.spinner("Extracting content from cloud..."):
                    try:
                        ext_res = tavily_client.extract(urls=[article_url])
                        if ext_res.get("results"):
                            raw_text = ext_res["results"][0]["raw_content"]
                            st.markdown("---")
                            with st.container(border=True):
                                st.markdown(raw_text[:15000])
                        else:
                            st.warning("Could not extract clean text from this link.")
                    except Exception as e:
                        st.error(f"Extraction Error: {e}")

# =====================================================================
# VIEW 3: FULL ANAS INTELLIGENCE SUITE
# =====================================================================
elif st.session_state.current_view == "anas_intelligence":

    st.markdown("<style>.main .block-container { padding-top: 2rem !important; max-width: 1200px !important; }</style>", unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
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
                    {"role": "assistant", "content": "Secure connection established. How can I help you today?"}
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

    # MODE 1: ORIGINAL CHATBOT
    if app_mode == "💬 Original Chatbot":
        st.title("🤖 Anas Intelligence")
        st.caption(f"Active Session: **{st.session_state.current_chat_title}**")

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
                    payload = [{"role": "system", "content": GEMINI_FORMATTING_PROMPT}] + [
                        {"role": m["role"], "content": m["content"]} for m in active_messages
                    ]
                    reply = run_ai_stream(payload, st.empty())
                    if reply:
                        active_messages.append({"role": "assistant", "content": reply})

    # MODE 2: TEXT HUMANIZER
    elif app_mode == "📝 Text Humanizer":
        st.title("📝 Text Humanizer")
        st.caption("Rewrite text into fluid, natural human prose with zero robotic phrasing.")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            user_paragraphs = st.text_area("Source Text:", height=300, placeholder="Paste your essay or text here...", key="humanizer_area")
            humanizer_style = st.selectbox("Style Profile:", ["Formal", "Chill", "Student"])
            submit_button = st.button("✨ Humanize Text", type="primary", use_container_width=True)

        with col2:
            st.markdown("### 📄 Humanized Output")
            with st.container(border=True):
                output_placeholder = st.empty()
                output_placeholder.info("Your humanized text will stream here...")

        if submit_button and user_paragraphs.strip():
            st.session_state.stop_generation = False
            with col2:
                with st.spinner("Rewriting..."):
                    if humanizer_style == "Formal":
                        style_instruction = "Rewrite to sound highly professional, academic, and fluid. Eliminate repetitive sentence structures."
                    elif humanizer_style == "Chill":
                        style_instruction = "Rewrite to sound completely casual, relaxed, and conversational, like explaining to a close friend."
                    else:
                        style_instruction = "Rewrite from the perspective of an intelligent high school or college student. Straightforward and authentic."
                        
                    instr = f"{GEMINI_FORMATTING_PROMPT}\n\nYou are an expert human editor. {style_instruction} Preserve all key facts and details."
                    payload = [{"role": "system", "content": instr}, {"role": "user", "content": user_paragraphs}]
                    run_ai_stream(payload, output_placeholder)

    # MODE 3: SMART SUMMARIZER
    elif app_mode == "📊 Smart Summarizer":
        st.title("📊 Smart Summarizer")
        st.caption("Extract structured takeaways and core insights from long documents.")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            heavy_text = st.text_area("Source Material:", height=350, placeholder="Paste long documents or study notes here...", key="summary_area")
            summarize_button = st.button("⚡ Extract Insights", type="primary", use_container_width=True)

        with col2:
            st.markdown("### 📋 Executive Summary")
            with st.container(border=True):
                summary_placeholder = st.empty()
                summary_placeholder.info("The summary breakdown will generate here...")

        if summarize_button and heavy_text.strip():
            st.session_state.stop_generation = False
            with col2:
                with st.spinner("Analyzing data..."):
                    instr = f"{GEMINI_FORMATTING_PROMPT}\n\nProcess the text into three formatted sections:\n### 📋 Executive Summary\n### 🔑 Key Takeaways (bullet points with bold keywords)\n### 🧠 Core Terms & Definitions"
                    payload = [{"role": "system", "content": instr}, {"role": "user", "content": heavy_text}]
                    run_ai_stream(payload, summary_placeholder)

    # MODE 4: AI TRANSLATOR
    elif app_mode == "🌐 AI Translator":
        st.title("🌐 AI Universal Translator")
        st.caption("Translate source text seamlessly across global languages.")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            src_text = st.text_area("Source Text:", height=250, placeholder="Type or paste text to translate...", key="trans_area")
            
            lang_col, style_col = st.columns(2)
            with lang_col:
                target_lang = st.selectbox("Target Language:", global_languages_list, index=0)
            with style_col:
                translation_style = st.selectbox("Tone Profile:", ["Literal/Exact", "Natural/Casual", "Formal/Business"])
                
            translate_button = st.button("🚀 Translate Text", type="primary", use_container_width=True)

        with col2:
            st.markdown(f"### 🌐 Translation ({target_lang})")
            with st.container(border=True):
                trans_placeholder = st.empty()
                trans_placeholder.info("Your AI translation will stream here...")

        if translate_button and src_text.strip():
            st.session_state.stop_generation = False
            with col2:
                with st.spinner("Translating text..."):
                    instr = f"{GEMINI_FORMATTING_PROMPT}\n\nTranslate the input text into {target_lang} using a '{translation_style}' stylistic profile."
                    payload = [{"role": "system", "content": instr}, {"role": "user", "content": src_text}]
                    run_ai_stream(payload, trans_placeholder)

    # MODE 5: FLASHCARD GENERATOR
    elif app_mode == "🧠 Flashcard Generator":
        st.title("🧠 Flashcard Engine")
        st.caption("Generate structured, multi-lingual study decks instantly from your notes.")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            raw_notes = st.text_area("Study Material (English):", height=240, placeholder="Paste topics or notes here...", key="flash_area")
            
            f_lang_col, f_num_col = st.columns(2)
            with f_lang_col:
                study_lang = st.selectbox("Deck Language:", global_languages_list, index=0, key="flash_lang_select")
            with f_num_col:
                num_cards = st.slider("Number of cards:", min_value=1, max_value=50, value=5)
                
            generate_cards_btn = st.button("🃏 Forge Study Flashcards", type="primary", use_container_width=True)
            
        with col2:
            st.markdown("### 🗂️ Study Deck")
            
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                if st.button("👁️ Show Answers", use_container_width=True):
                    st.session_state.show_answers = True
            with t_col2:
                if st.button("🙈 Hide Answers", use_container_width=True):
                    st.session_state.show_answers = False

            st.markdown("---")
            with st.container(border=True):
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
                    cards_display_placeholder.info("Your flashcard deck will build here...")

        if generate_cards_btn and raw_notes.strip():
            st.session_state.stop_generation = False
            st.session_state.show_answers = False
            with col2:
                with st.spinner(f"Forging {num_cards} cards in {study_lang}..."):
                    instr = (
                        f"{GEMINI_FORMATTING_PROMPT}\n\n"
                        f"Read the user's material and create exactly {num_cards} flashcards in {study_lang}.\n"
                        f"Use this clean structure for every single card:\n\n"
                        f"### 🃏 CARD X\n"
                        f"**QUESTION:** (Question in {study_lang})\n"
                        f"**ANSWER:** (Answer in {study_lang})\n\n"
                        f"Output ONLY the cards without intro or outro chatter."
                    )
                    payload = [{"role": "system", "content": instr}, {"role": "user", "content": raw_notes}]
                    
                    final_deck = run_ai_stream(payload, cards_display_placeholder)
                    if final_deck:
                        st.session_state.flashcard_content = final_deck
                        st.rerun()
