import streamlit as st
from dotenv import load_dotenv
import os
from groq_client import initialize_groq
from ui_components import (
    set_page_config,
    display_header,
    display_navigation_sidebar
)
from whiteboard_module import display_whiteboard
from ai_chat_module import display_ai_chat
from notes_module import display_notes_main, display_notes_sidebar
from exam_module import exam_interface
from datetime import datetime
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize all session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'notes' not in st.session_state:
        st.session_state.notes = []
    if 'current_note' not in st.session_state:
        st.session_state.current_note = None
    if 'show_analysis' not in st.session_state:
        st.session_state.show_analysis = False
    if 'exams' not in st.session_state:
        st.session_state.exams = []
    if 'exam_results' not in st.session_state:
        st.session_state.exam_results = []
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Whiteboard"
    if 'prompt_suggestion' not in st.session_state:
        st.session_state.prompt_suggestion = None

def main():
    def setup_mermaid_support():
        """Add support for Mermaid diagrams in Streamlit"""
        components.html(
            """
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>
                mermaid.initialize({startOnLoad: true});
                document.addEventListener('DOMContentLoaded', function() {
                    mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                });
            </script>
            """,
            height=0,
        )
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY not found in environment variables. Please check your .env file.")
        return

    # Set up the page with a consistent theme
    set_page_config()
    
    # Initialize Groq client
    client = initialize_groq()
    
    # Initialize session state
    initialize_session_state()

    # App header with logo and title
    display_header()

    # Navigation sidebar
    with st.sidebar:
        display_navigation_sidebar()
        
        # Only show notes sidebar if on Notes tab
        if st.session_state.current_tab == "Notes":
            display_notes_sidebar()

    # Main content area - show content based on selected tab
    if st.session_state.current_tab == "Whiteboard":
        display_whiteboard()
    elif st.session_state.current_tab == "AI Chat":
        display_ai_chat(client)
    elif st.session_state.current_tab == "Notes":
        display_notes_main(client)
    elif st.session_state.current_tab == "Exams":
        exam_interface()
    
    # Add footer
    st.divider()
    st.caption("© 2025 YourNote - Your AI Study Partner")
    setup_mermaid_support()
if __name__ == "__main__":
    main()