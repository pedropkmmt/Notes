import streamlit as st
from datetime import datetime

def set_page_config():
    """Set the Streamlit page configuration"""
    st.set_page_config(
        layout="wide", 
        page_title="UniStudent | Interactive Learning Platform",
        page_icon="🎓",
        initial_sidebar_state="expanded"
    )
    
    # Enable LaTeX rendering throughout the app
    st.markdown("""
    <script type="text/javascript" async
      src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
    .katex { font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    """Display the app header with logo and title"""
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("# 🎓")
    with col2:
        st.title("YourNote")
        st.caption("Your AI-powered study companion")

def display_navigation_sidebar():
    """Display the navigation sidebar with tab selection"""
    st.header("Navigation")
    
    # Create a more visual tab selector
    tab_icons = {
        "Whiteboard": "✏️",
        "AI Chat": "💬",
        "Notes": "📝",
        "Exams": "📚"
    }
    
    # Display tabs with icons
    selected_tab = st.radio(
        "Select a section:",
        list(tab_icons.keys()),
        format_func=lambda x: f"{tab_icons[x]} {x}",
        key="sidebar_tabs"
    )
    st.session_state.current_tab = selected_tab
    
    st.divider()

    # Add a help section at the bottom
    with st.expander("❓ Help & Tips"):
        st.markdown("""
        - **Whiteboard**: Draw and sketch ideas freely
        - **AI Chat**: Get answers to your study questions
        - **Notes**: Take and organize your study notes
        - **Exams**: Practice with AI-generated quizzes
        """)

def create_doc_toolbar():
    """Create a Google Docs-style toolbar"""
    cols = st.columns(8)
    
    with cols[0]:
        st.button("📝", help="Edit", use_container_width=True)
    with cols[1]:
        st.button("🔍", help="Search", use_container_width=True)
    with cols[2]:
        st.button("💾", help="Save", use_container_width=True)
    with cols[3]:
        st.button("📤", help="Share", use_container_width=True)
    with cols[4]:
        st.button("⚙️", help="Settings", use_container_width=True)

def format_last_edited(timestamp):
    """Format the last edited timestamp in a Google Docs style"""
    dt = datetime.fromtimestamp(timestamp)
    return f"Last edited {dt.strftime('%I:%M %p')}"
