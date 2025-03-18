import streamlit as st
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import os
import streamlit.components.v1 as components
from datetime import datetime
import json
from exam_module import exam_interface

# Load environment 
load_dotenv()

def initialize_groq():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(client, prompt, system_message="You are a helpful AI assistant. Provide clear and accurate responses to questions."):
    try:
        # Check if the prompt is likely about mathematical content
        math_keywords = ["math", "equation", "formula", "symbol", "pi", "π", "sigma", "integral", 
                         "derivative", "calculus", "algebra", "theta", "alpha", "beta", "gamma"]
        
        is_math_related = any(keyword in prompt.lower() for keyword in math_keywords)
        
        if is_math_related:
            # Add special instruction for mathematical content display
            system_message += " If the user asks about mathematical concepts, display equations and symbols using LaTeX for proper formatting."
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
        )
        
        response = chat_completion.choices[0].message.content
        
        # Enable LaTeX rendering for math-related responses
        if is_math_related:
            # Process response to enable LaTeX rendering using streamlit's markdown
            # This works because streamlit supports LaTeX with dollar signs
            common_symbols = {
                "pi": "$\\pi$",
                "π": "$\\pi$",
                "theta": "$\\theta$",
                "θ": "$\\theta$",
                "sigma": "$\\sigma$",
                "Σ": "$\\Sigma$",
                "delta": "$\\delta$",
                "Δ": "$\\Delta$",
                "alpha": "$\\alpha$",
                "β": "$\\beta$",
                "gamma": "$\\gamma$",
                "lambda": "$\\lambda$",
                "μ": "$\\mu$",
                "square root": "$\\sqrt{x}$",
                "infinity": "$\\infty$"
            }
            
            # Replace common symbols with LaTeX versions
            for symbol, latex in common_symbols.items():
                # Use word boundaries to avoid replacing parts of words
                response = response.replace(f" {symbol} ", f" {latex} ")
                response = response.replace(f" {symbol},", f" {latex},")
                response = response.replace(f" {symbol}.", f" {latex}.")
                
            # Add instructions for properly displaying the response
            response = "This response contains mathematical notation. Viewing it with LaTeX rendering enabled:\n\n" + response
            
        return response
    except Exception as e:
        return f"Error getting AI response: {str(e)}"

def analyze_notes(client, notes):
    system_message = """You are an educational analyst. Analyze the following notes and provide:
    1. Main concepts covered
    2. Knowledge gaps or areas needing clarification
    3. Suggestions for better organization
    4. Key points to review
    Be specific and constructive in your feedback."""
    
    return get_ai_response(client, notes, system_message)

def generate_summary(client, notes, topic=None):
    if topic:
        system_message = f"""You are a study assistant. Generate a focused summary of the notes specifically about '{topic}'.
        Include:
        1. Key points about the topic
        2. Related concepts
        3. Important definitions or formulas
        If the topic isn't found in the notes, kindly indicate that."""
    else:
        system_message = """You are a study assistant. Generate a comprehensive summary of these notes.
        Include:
        1. Main topics covered
        2. Key points for each topic
        3. Important concepts and their relationships"""
    
    return get_ai_response(client, notes, system_message)

def format_last_edited(timestamp):
    """Format the last edited timestamp in a Google Docs style"""
    dt = datetime.fromtimestamp(timestamp)
    return f"Last edited {dt.strftime('%I:%M %p')}"

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

def display_notes_sidebar():
    """Display the notes sidebar"""
    st.sidebar.subheader("My Documents")
    
    # New document button with better styling
    if st.sidebar.button("➕ New Document", type="primary", use_container_width=True):
        new_note = {
            "title": "Untitled Document",
            "content": "",
            "created": datetime.now().timestamp(),
            "last_edited": datetime.now().timestamp(),
            "id": len(st.session_state.notes)
        }
        st.session_state.notes.append(new_note)
        st.session_state.current_note = new_note["id"]
    
    # List of existing documents
    if st.session_state.notes:
        st.sidebar.divider()
        for note in st.session_state.notes:
            note_selected = st.sidebar.button(
                f"📄 {note['title']}",
                key=f"doc_{note['id']}",
                use_container_width=True
            )
            if note_selected:
                st.session_state.current_note = note["id"]
            # Display last edited time in smaller text
            st.sidebar.caption(f"{format_last_edited(note['last_edited'])}")
    else:
        st.sidebar.info("No documents yet. Click '➕ New Document' to get started!")
            
    # Search and Analysis Tools
    st.sidebar.divider()
    st.sidebar.subheader("Tools")
    
    # Search through notes
    search_query = st.sidebar.text_input("🔍 Search in notes...")
    if search_query:
        st.sidebar.markdown("### Search Results")
        found_notes = False
        for note in st.session_state.notes:
            if search_query.lower() in note['content'].lower() or search_query.lower() in note['title'].lower():
                if st.sidebar.button(f"🔍 {note['title']}", key=f"search_{note['id']}", use_container_width=True):
                    st.session_state.current_note = note["id"]
                found_notes = True
        
        if not found_notes:
            st.sidebar.info("No matching notes found.")

def display_whiteboard():
    """Display the whiteboard tab"""
    st.header("Interactive Whiteboard")
    
    # Add controls for the whiteboard
    col1, col2, col3 = st.columns(3)
    with col1:
        stroke_width = st.slider("Stroke width", 1, 10, 2)
    with col2:
        stroke_color = st.color_picker("Stroke color", "#000000")
    with col3:
        background_color = st.color_picker("Background color", "#ffffff")
    
    # Canvas with improved parameters
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=background_color,
        height=500,
        drawing_mode=st.selectbox("Drawing mode", ["freedraw", "line", "rect", "circle", "transform"]),
        key="canvas",
    )
    
    # Add buttons for clear and save
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Canvas", use_container_width=True):
            # This will trigger a rerun with a new canvas
            st.rerun()
    with col2:
        analyze_button = st.button("Analyze Whiteboard", type="primary", use_container_width=True)
    
    if canvas_result.image_data is not None and analyze_button:
        with st.spinner("Analyzing..."):
            st.info("Whiteboard analysis feature will be integrated with OCR + Groq AI in the next update.")
            # Add a placeholder for future functionality
            st.success("Analysis complete! (This is a placeholder)")

def display_ai_chat(client):
    """Display the AI chat tab with enhanced math display"""
    st.header("AI Chat Assistant")
    
    # Add a helpful prompt suggestion feature
    st.caption("Need help? Try asking about:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📚 Explain a concept", use_container_width=True):
            st.session_state.prompt_suggestion = "Can you explain the concept of [topic]?"
    with col2:
        if st.button("🔍 Study tips", use_container_width=True):
            st.session_state.prompt_suggestion = "What are effective study techniques for [subject]?"
    with col3:
        if st.button("📝 Assignment help", use_container_width=True):
            st.session_state.prompt_suggestion = "How do I structure an essay about [topic]?"
    
    # Add math-specific suggestions
    math_col1, math_col2 = st.columns(2)
    with math_col1:
        if st.button("🧮 Mathematical symbols", use_container_width=True):
            st.session_state.prompt_suggestion = "Explain common mathematical symbols like pi, sigma, and theta."
    with math_col2:
        if st.button("📊 Equations", use_container_width=True):
            st.session_state.prompt_suggestion = "Show me the quadratic formula and explain how to use it."
    
    # Enable LaTeX in Streamlit for the chat
    st.markdown("""
    <style>
    .math-display .katex { font-size: 1.4em; }
    </style>
    """, unsafe_allow_html=True)
    
    # Chat history with LaTeX rendering
    st.divider()
    chat_container = st.container(height=75)
    st.markdown("""
    <style>
    .element-container:has(div[data-testid="stVerticalBlock"]:last-of-type) {
        overflow-y: auto;
        max-height: 400px;
    }
    .math-display .katex { font-size: 1.4em; }
    </style>
    """, unsafe_allow_html=True)
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 Hi there! I'm your AI study assistant. How can I help you today?")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    st.divider()
    
    # Display suggestion above chat input if exists
    if "prompt_suggestion" in st.session_state and st.session_state.prompt_suggestion:
        st.info(f"Suggested prompt: {st.session_state.prompt_suggestion}")
    
    # Chat input without value parameter
    prompt = st.chat_input("Ask about any math concept or equation...")
    
    if prompt:
        # Clear the suggestion after using it
        if "prompt_suggestion" in st.session_state:
            del st.session_state.prompt_suggestion
                
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_ai_response(client, prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

def display_notes_main(client):
    """Display the main notes area"""
    # Main document area
    col1, col2 = st.columns([3, 2])
    
    with col1:
        if st.session_state.current_note is not None:
            current_note = next(
                (note for note in st.session_state.notes 
                 if note["id"] == st.session_state.current_note), 
                None
            )
            
            if current_note:
                # Document toolbar
                create_doc_toolbar()
                
                # Title input with larger font
                new_title = st.text_input(
                    "Title",
                    value=current_note["title"],
                    key=f"title_{current_note['id']}",
                    placeholder="Enter document title..."
                )
                
                # Content area with rich text editor
                new_content = st.text_area(
                    "Content",
                    value=current_note["content"],
                    height=500,
                    key=f"content_{current_note['id']}",
                    placeholder="Start typing your notes here..."
                )
                
                # Auto-save functionality
                if new_title != current_note["title"] or new_content != current_note["content"]:
                    current_note["title"] = new_title
                    current_note["content"] = new_content
                    current_note["last_edited"] = datetime.now().timestamp()
                    st.session_state.notes = [
                        note if note["id"] != current_note["id"] else current_note 
                        for note in st.session_state.notes
                    ]
                    
                    # Show a saved indicator
                    st.caption(f"✓ Saved {datetime.now().strftime('%I:%M %p')}")
        else:
            # Welcome message when no note is selected
            st.info("👈 Select a document from the sidebar or create a new one to get started.")
            
    # Analysis panel
    with col2:
        if st.session_state.current_note is not None:
            st.markdown("### AI Study Tools")
            
            current_note = next(
                (note for note in st.session_state.notes 
                 if note["id"] == st.session_state.current_note),
                None
            )
            
            if current_note and current_note["content"]:
                # Tools in expandable sections
                with st.expander("Generate Summary", expanded=True):
                    if st.button("Create Summary", type="primary", use_container_width=True):
                        with st.spinner("Generating summary..."):
                            summary = generate_summary(client, current_note["content"])
                            st.markdown(summary)
                
                with st.expander("Topic-Specific Summary"):
                    topic = st.text_input("Enter specific topic:")
                    if topic and st.button("Generate Topic Summary", use_container_width=True):
                        with st.spinner(f"Generating summary for '{topic}'..."):
                            topic_summary = generate_summary(client, current_note["content"], topic)
                            st.markdown(topic_summary)
                
                with st.expander("Analyze Notes"):
                    if st.button("Analyze for Gaps & Improvements", use_container_width=True):
                        with st.spinner("Analyzing notes..."):
                            analysis = analyze_notes(client, current_note["content"])
                            st.markdown(analysis)
                
                with st.expander("Create Study Materials"):
                    material_type = st.selectbox(
                        "Material type:",
                        ["Flashcards", "Quiz Questions", "Mind Map", "Study Guide"]
                    )
                    if st.button("Generate Study Material", use_container_width=True):
                        with st.spinner(f"Creating {material_type}..."):
                            st.info(f"{material_type} generation will be available in the next update!")
            else:
                st.info("Add content to your note to use these tools.")

def main():
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY not found in environment variables. Please check your .env file.")
        return

    # Set up the page with a consistent theme
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
    
    client = initialize_groq()
    
    # Initialize session state
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

    # App header with logo and title
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("# 🎓")
    with col2:
        st.title("YourNote")
        st.caption("Your AI-powered study companion")

    # Move tabs to sidebar with better styling
    with st.sidebar:
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
        
        # Only show notes sidebar if on Notes tab
        if selected_tab == "Notes":
            display_notes_sidebar()
        
        # Add a help section at the bottom
        with st.sidebar.expander("❓ Help & Tips"):
            st.markdown("""
            - **Whiteboard**: Draw and sketch ideas freely
            - **AI Chat**: Get answers to your study questions
            - **Notes**: Take and organize your study notes
            - **Exams**: Practice with AI-generated quizzes
            """)

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

if __name__ == "__main__":
    main()