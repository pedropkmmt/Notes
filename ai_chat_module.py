import streamlit as st
from groq_client import get_ai_response

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