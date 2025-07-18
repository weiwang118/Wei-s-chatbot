import streamlit as st
import requests
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"
WS_BASE_URL = "ws://localhost:8000/ws"

# Page configuration
st.set_page_config(
    page_title="CHAI Social Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* Import beautiful fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

/* Global styling */
* {
    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Stunning gradient background */
.main {
    padding-top: 0.5rem;
    background: linear-gradient(135deg, 
        #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
    min-height: 100vh;
    position: relative;
}

.main::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(120, 200, 255, 0.2) 0%, transparent 50%);
    pointer-events: none;
    z-index: -1;
}

/* Glassmorphism header */
.chat-header {
    background: rgba(255, 255, 255, 0.25);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 2rem;
    border-radius: 24px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.4);
    position: relative;
    overflow: hidden;
}

.chat-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* Enhanced premium sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.15) 0%, 
        rgba(118, 75, 162, 0.15) 25%,
        rgba(240, 147, 251, 0.15) 50%,
        rgba(245, 87, 108, 0.15) 75%,
        rgba(79, 172, 254, 0.15) 100%) !important;
    backdrop-filter: blur(25px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(25px) saturate(180%) !important;
    border-right: 2px solid rgba(255, 255, 255, 0.4) !important;
    box-shadow: 2px 0 20px rgba(102, 126, 234, 0.1), inset -1px 0 0 rgba(255, 255, 255, 0.3) !important;
}

section[data-testid="stSidebar"] * {
    color: #262626 !important;
}

/* Stunning chat messages */
.stChatMessage {
    border-radius: 20px;
    margin: 1rem 0;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stChatMessage:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
}

.stChatMessage[data-testid="user"] {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.9) 0%, 
        rgba(118, 75, 162, 0.9) 100%);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.stChatMessage[data-testid="assistant"] {
    background: linear-gradient(135deg, 
        rgba(240, 147, 251, 0.9) 0%, 
        rgba(245, 87, 108, 0.9) 100%);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.stChatMessage .stMarkdown {
    color: white;
    font-weight: 500;
}

/* Button styling */
.stButton > button {
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.25) 0%, 
        rgba(255, 255, 255, 0.1) 100%);
    backdrop-filter: blur(10px);
    color: white;
    font-weight: 600;
    padding: 12px 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.35) 0%, 
        rgba(255, 255, 255, 0.2) 100%);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%);
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    border: none;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #ff8787 0%, #fed330 50%, #0abde3 100%);
    box-shadow: 0 12px 35px rgba(255, 107, 107, 0.6);
}

.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.4) 0%, 
        rgba(255, 255, 255, 0.3) 100%) !important;
    color: #1a1a1a !important;
    border: 2px solid rgba(255, 255, 255, 0.6) !important;
    backdrop-filter: blur(15px) !important;
    font-weight: 700 !important;
    text-shadow: none !important;
    box-shadow: 
        0 4px 15px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.6) 0%, 
        rgba(255, 255, 255, 0.5) 100%) !important;
    border-color: rgba(255, 255, 255, 0.8) !important;
    transform: translateY(-2px) !important;
    color: #0a0a0a !important;
    box-shadow: 
        0 6px 20px rgba(0, 0, 0, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.7) !important;
}

/* Input styling */
.stTextInput > div > div > input {
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    color: white;
    transition: all 0.3s ease;
    padding: 12px 16px;
    font-weight: 500;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(255, 255, 255, 0.7);
}

.stTextInput > div > div > input:focus {
    border-color: rgba(255, 255, 255, 0.6);
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.25);
}

/* Selectbox styling */
.stSelectbox > div > div {
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #262626;
}

/* Welcome screen */
.welcome-container {
    text-align: center;
    padding: 3rem;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    margin: 1rem 0;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    position: relative;
    overflow: hidden;
}

/* Personality badges */
.personality-badge {
    display: inline-block;
    padding: 8px 16px;
    background: linear-gradient(135deg, 
        rgba(255, 107, 107, 0.9) 0%, 
        rgba(254, 202, 87, 0.9) 100%);
    color: white;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    margin: 0.2rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Premium chat input with glassmorphism */
.stChatInputContainer,
div[data-testid="stChatInputContainer"] {
    border-radius: 30px !important;
    border: 3px solid rgba(255, 255, 255, 0.5) !important;
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.3) 0%, 
        rgba(255, 255, 255, 0.15) 50%,
        rgba(255, 255, 255, 0.3) 100%) !important;
    backdrop-filter: blur(30px) saturate(200%) brightness(1.1) !important;
    -webkit-backdrop-filter: blur(30px) saturate(200%) brightness(1.1) !important;
    box-shadow: 
        0 12px 40px rgba(0, 0, 0, 0.15),
        0 4px 15px rgba(102, 126, 234, 0.1),
        inset 0 2px 0 rgba(255, 255, 255, 0.6) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stChatInputContainer > div,
div[data-testid="stChatInputContainer"] > div {
    background: transparent !important;
}

/* Chat input text fields */
.stChatInputContainer input[type="text"],
.stChatInputContainer textarea,
div[data-testid="stChatInputContainer"] input[type="text"],
div[data-testid="stChatInputContainer"] textarea {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.25) 0%, 
        rgba(255, 255, 255, 0.15) 100%) !important;
    backdrop-filter: blur(15px) saturate(150%) !important;
    border: 2px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 25px !important;
    color: black !important;
    padding: 12px 20px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    max-width: 60% !important;
    resize: none !important;
}

.stChatInputContainer input:focus,
.stChatInputContainer textarea:focus {
    background: rgba(255, 255, 255, 0.3) !important;
    border-color: rgba(255, 255, 255, 0.6) !important;
    outline: none !important;
}

.stChatInputContainer input::placeholder,
.stChatInputContainer textarea::placeholder {
    color: rgba(255, 255, 255, 0.7) !important;
}

/* Chat input send button */
.stChatInputContainer button {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.9) 0%, 
        rgba(118, 75, 162, 0.9) 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 50% !important;
    color: white !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
}

.stChatInputContainer button:hover {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 1) 0%, 
        rgba(118, 75, 162, 1) 100%) !important;
    transform: translateY(-2px) scale(1.05) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
}

/* Sidebar header */
.sidebar-header {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.4) 0%, 
        rgba(118, 75, 162, 0.4) 50%,
        rgba(240, 147, 251, 0.4) 100%);
    backdrop-filter: blur(25px) saturate(180%);
    color: white;
    padding: 2rem 1.5rem;
    border-radius: 24px;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: bold;
    box-shadow: 
        0 12px 40px rgba(102, 126, 234, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
    border: 2px solid rgba(255, 255, 255, 0.4);
}

/* Sidebar styling for dark text */
.css-1d391kg .stMarkdown, 
.css-1d391kg .stText,
.css-1d391kg label,
section[data-testid="stSidebar"] .stMarkdown, 
section[data-testid="stSidebar"] .stText,
section[data-testid="stSidebar"] label {
    color: #262626 !important;
    font-weight: 600;
}

/* Sidebar inputs */
.css-1d391kg .stTextInput > div > div > input,
.css-1d391kg .stTextArea > div > div > textarea {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.4) 0%, 
        rgba(255, 255, 255, 0.3) 100%) !important;
    backdrop-filter: blur(15px) saturate(150%) !important;
    border: 2px solid rgba(255, 255, 255, 0.5) !important;
    border-radius: 16px !important;
    color: #1a1a1a !important;
    font-weight: 600 !important;
    padding: 12px 16px !important;
}

/* Sidebar buttons */
.css-1d391kg .stButton > button {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.35) 0%, 
        rgba(255, 255, 255, 0.25) 50%,
        rgba(255, 255, 255, 0.35) 100%);
    backdrop-filter: blur(15px) saturate(150%);
    border: 2px solid rgba(255, 255, 255, 0.6);
    color: #1a1a1a;
    border-radius: 18px;
    font-weight: 700;
}

/* Text styling */
h1, h2, h3, h4, h5, h6 {
    color: white !important;
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

p, div, span {
    color: rgba(255, 255, 255, 0.95) !important;
}

/* Force textarea width - simplified approach */
textarea {
    width: 60% !important;
    max-width: 60% !important;
    min-width: 60% !important;
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Premium scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.3) 0%, 
        rgba(255, 255, 255, 0.1) 100%);
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.4) 0%, 
        rgba(255, 255, 255, 0.2) 100%);
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions" not in st.session_state:
    st.session_state.sessions = []
if "bots" not in st.session_state:
    st.session_state.bots = []
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False


# Helper functions
def create_session(bot_name: str, user_name: str, personality: str, custom_prompt: str = None):
    """Create a new chat session"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/create",
            json={
                "bot_name": bot_name,
                "user_name": user_name,
                "personality": personality,
                "custom_prompt": custom_prompt
            }
        )
        if response.status_code == 200:
            session = response.json()
            st.session_state.current_session_id = session["id"]
            st.session_state.messages = []
            return session
        else:
            st.error(f"Failed to create session: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error creating session: {e}")
        return None


def send_message(session_id: str, message: str):
    """Send a message to the bot"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/send",
            json={
                "session_id": session_id,
                "message": message
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to send message: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return None


def load_sessions():
    """Load all chat sessions"""
    try:
        response = requests.get(f"{API_BASE_URL}/chat/sessions")
        if response.status_code == 200:
            data = response.json()
            st.session_state.sessions = data["sessions"]
            return data["sessions"]
        return []
    except Exception as e:
        st.error(f"Error loading sessions: {e}")
        return []


def load_session_messages(session_id: str):
    """Load messages for a specific session"""
    try:
        response = requests.get(f"{API_BASE_URL}/chat/sessions/{session_id}/messages")
        if response.status_code == 200:
            data = response.json()
            return data["messages"]
        return []
    except Exception as e:
        st.error(f"Error loading messages: {e}")
        return []


# Personality descriptions for better UX
PERSONALITY_INFO = {
    "friendly": {"emoji": "😊", "desc": "Warm and outgoing person who loves conversations"},
    "professional": {"emoji": "💼", "desc": "Successful professional with strong communication skills"},
    "creative": {"emoji": "🎨", "desc": "Artistic and imaginative person who thinks differently"},
    "analytical": {"emoji": "📊", "desc": "Logical thinker who enjoys solving problems"},
    "empathetic": {"emoji": "💝", "desc": "Deeply caring person who connects emotionally"},
    "humorous": {"emoji": "😄", "desc": "Naturally funny person who loves making others laugh"},
    "adventurous": {"emoji": "🏔️", "desc": "Explorer who loves new experiences and adventures"},
    "intellectual": {"emoji": "🧠", "desc": "Well-read person who enjoys deep discussions"}
}

# Main app
def main():
    # Custom header
    st.markdown("""
    <div class="chat-header">
        <h1>💬 CHAI Social Chat</h1>
        <p>Connect with AI personalities that feel real</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        # Sidebar header
        st.markdown("""
        <div class="sidebar-header">
            <h3>🎭 Chat Control Panel</h3>
        </div>
        """, unsafe_allow_html=True)

        # New session
        with st.expander("✨ Create New Session", expanded=True):
            bot_name = st.text_input("🤖 Bot Name", value="Assistant", help="Give your AI friend a name")
            user_name = st.text_input("👤 Your Name", value="User", help="How should the bot address you?")
            
            # Enhanced personality selection with cards
            st.write("🎭 **Choose Personality:**")
            
            # Initialize personality if not set
            if "selected_personality" not in st.session_state:
                st.session_state.selected_personality = "friendly"
            
            # Create personality cards in a grid
            personality_keys = list(PERSONALITY_INFO.keys())
            rows = [personality_keys[i:i+2] for i in range(0, len(personality_keys), 2)]
            
            for row in rows:
                cols = st.columns(len(row))
                for idx, personality_key in enumerate(row):
                    with cols[idx]:
                        info = PERSONALITY_INFO[personality_key]
                        # Check if this personality is selected
                        is_selected = st.session_state.selected_personality == personality_key
                        
                        # Create a styled button that looks like a card
                        button_style = "primary" if is_selected else "secondary"
                        
                        if st.button(
                            f"{info['emoji']} **{personality_key.title()}**\n\n{info['desc'][:45]}{'...' if len(info['desc']) > 45 else ''}",
                            key=f"personality_{personality_key}",
                            type=button_style,
                            use_container_width=True,
                            help=f"Select {personality_key} personality: {info['desc']}"
                        ):
                            st.session_state.selected_personality = personality_key
                            st.rerun()
            
            # Set the selected personality for the session creation
            personality = st.session_state.selected_personality

            custom_prompt = st.text_area("💬 Custom Instructions (Optional)", 
                                       help="Add specific instructions for your AI friend")

            if st.button("🚀 Create Session", type="primary", use_container_width=True):
                session = create_session(bot_name, user_name, personality, custom_prompt)
                if session:
                    st.success(f"✅ Created session with {bot_name}")
                    st.rerun()

        # Existing sessions
        st.subheader("Your Sessions")
        sessions = load_sessions()

        if sessions:
            for session in sessions:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(
                            f"💬 {session['bot_name']}",
                            key=f"session_{session['id']}",
                            use_container_width=True
                    ):
                        st.session_state.current_session_id = session['id']
                        st.session_state.messages = load_session_messages(session['id'])
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"delete_{session['id']}"):
                        requests.delete(f"{API_BASE_URL}/chat/sessions/{session['id']}")
                        st.rerun()
        else:
            st.info("No sessions yet. Create one to start chatting!")

        # Session actions
        if st.session_state.current_session_id:
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear Chat"):
                    requests.post(
                        f"{API_BASE_URL}/chat/sessions/{st.session_state.current_session_id}/clear"
                    )
                    st.session_state.messages = []
                    st.rerun()
            with col2:
                if st.button("End Session"):
                    requests.post(
                        f"{API_BASE_URL}/chat/sessions/{st.session_state.current_session_id}/deactivate"
                    )
                    st.session_state.current_session_id = None
                    st.session_state.messages = []
                    st.rerun()

    # Main chat area
    if st.session_state.current_session_id:
        # Get current session info
        current_session = next(
            (s for s in sessions if s['id'] == st.session_state.current_session_id),
            None
        )

        if current_session:
            # Chat header with back button
            col1, col2 = st.columns([1, 5])
            if st.button("← Back", type="secondary", help="Return to home page"):
                    st.session_state.current_session_id = None
                    st.session_state.messages = []
                    st.rerun()

            with col2:
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-top: 8px;">
                    <h3 style="margin: 0; color: #667eea;">
                        💬 Chatting with {current_session['bot_name']} 
                        <span class="personality-badge">{PERSONALITY_INFO[current_session['personality']]['emoji']} {current_session['personality'].title()}</span>
                    </h3>
                </div>
                """, unsafe_allow_html=True)

            # Chat messages container
            chat_container = st.container()

            # Display messages
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(
                            "user" if message["sender"] == current_session["user_name"] else "assistant"
                    ):
                        st.write(message["content"])
                        st.caption(
                            datetime.fromisoformat(message["timestamp"]).strftime("%H:%M:%S")
                        )

            # Chat input
            if prompt := st.chat_input("Type your message..."):
                # Add user message to display
                user_message = {
                    "sender": current_session["user_name"],
                    "content": prompt,
                    "timestamp": datetime.utcnow().isoformat()
                }
                st.session_state.messages.append(user_message)

                # Display user message immediately
                with st.chat_message("user"):
                    st.write(prompt)

                # Send message and get response
                with st.spinner("Thinking..."):
                    response = send_message(st.session_state.current_session_id, prompt)

                if response:
                    # Add bot response to messages
                    bot_message = {
                        "sender": response["bot_name"],
                        "content": response["response"],
                        "timestamp": response["timestamp"]
                    }
                    st.session_state.messages.append(bot_message)

                    # Display bot response
                    with st.chat_message("assistant"):
                        st.write(response["response"])
                        st.caption(
                            datetime.fromisoformat(response["timestamp"]).strftime("%H:%M:%S")
                        )

                # Rerun to update the chat
                st.rerun()
    else:
        # Welcome screen
        st.markdown("""
        <div class="welcome-container">
            <h2>🌟 Welcome to CHAI Social Chat!</h2>
            <p>Experience conversations with AI personalities that feel human and real.</p>
            <p>👈 Create a new session or select an existing one to start chatting!</p>
        </div>
        """, unsafe_allow_html=True)

        # Feature highlights
        st.markdown("### ✨ Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🎭 8 Unique Personalities**
            - Friendly & Creative
            - Professional & Analytical  
            - Empathetic & Humorous
            - Adventurous & Intellectual
            """)
        
        with col2:
            st.markdown("""
            **💬 Natural Conversations**
            - Human-like responses
            - Contextual memory
            - Personal storytelling
            - Emotional connections
            """)
        
        with col3:
            st.markdown("""
            **🚀 Easy to Use**
            - Quick session creation
            - Multiple chat sessions
            - Custom personalities
            - Real-time responses
            """)

        # Quick start with personality showcase
        st.markdown("### 🚀 Quick Start - Try These Personalities!")
        
        # Create personality cards in a grid
        personalities_grid = [
            ["creative", "analytical", "friendly"],
            ["empathetic", "humorous", "adventurous"],
            ["professional", "intellectual"]
        ]
        
        for row in personalities_grid:
            cols = st.columns(len(row))
            for idx, personality in enumerate(row):
                with cols[idx]:
                    info = PERSONALITY_INFO[personality]
                    if st.button(
                        f"{info['emoji']} {personality.title()}\n{info['desc'][:50]}...",
                        key=f"quick_{personality}",
                        use_container_width=True
                    ):
                        session = create_session(
                            f"{personality.title()} Friend", 
                            "User", 
                            personality
                        )
                        if session:
                            st.rerun()

        # Tips section
        st.markdown("### 💡 Tips for Better Conversations")
        st.markdown("""
        - **Be specific**: The more details you provide, the better the response
        - **Try different personalities**: Each one offers a unique conversation style
        - **Use custom instructions**: Add specific traits or backgrounds for your AI friend
        - **Have fun**: These AI personalities love to chat about anything!
        """)


if __name__ == "__main__":
    main()