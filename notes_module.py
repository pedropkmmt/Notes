import streamlit as st
from datetime import datetime
from ui_components import create_doc_toolbar, format_last_edited
from groq_client import analyze_notes, generate_summary

# Import the study material generation functions
from study_materials import (
    generate_flashcards,
    generate_study_guide,
    generate_mind_map,
    generate_diagram
)

# Import the new text-to-speech functionality
from text_to_speech import add_text_to_speech_to_notes

def display_notes_sidebar():
    """Display the notes sidebar"""
    st.subheader("My Documents")
    
    # New document button with better styling
    if st.button("➕ New Document", type="primary", use_container_width=True):
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
        st.divider()
        for note in st.session_state.notes:
            note_selected = st.button(
                f"📄 {note['title']}",
                key=f"doc_{note['id']}",
                use_container_width=True
            )
            if note_selected:
                st.session_state.current_note = note["id"]
            # Display last edited time in smaller text
            st.caption(f"{format_last_edited(note['last_edited'])}")
    else:
        st.info("No documents yet. Click '➕ New Document' to get started!")
            
    # Search and Analysis Tools
    st.divider()
    st.subheader("Tools")
    
    # Search through notes
    search_query = st.text_input("🔍 Search in notes...")
    if search_query:
        st.markdown("### Search Results")
        found_notes = False
        for note in st.session_state.notes:
            if search_query.lower() in note['content'].lower() or search_query.lower() in note['title'].lower():
                if st.button(f"🔍 {note['title']}", key=f"search_{note['id']}", use_container_width=True):
                    st.session_state.current_note = note["id"]
                found_notes = True
        
        if not found_notes:
            st.info("No matching notes found.")

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
                
                # New Text-to-Speech feature
                with st.expander("Text to Speech"):
                    st.info("Listen to your notes!")
                    section_to_read = st.text_input("Specific section to read (optional):", 
                                                  placeholder="Leave empty to read entire note")
                    add_text_to_speech_to_notes(current_note["content"], section=section_to_read)
                
                with st.expander("Create Study Materials"):
                    material_type = st.selectbox(
                        "Material type:",
                        ["Flashcards", "Quiz Questions", "Mind Map", "Study Guide", "Diagram"]
                    )
                    topic_for_material = st.text_input("Focus on specific topic (optional):", key="topic_study_material")
                    
                    if st.button("Generate Study Material", use_container_width=True):
                        with st.spinner(f"Creating {material_type}..."):
                            if material_type == "Flashcards":
                                content = generate_flashcards(client, current_note["content"], topic_for_material)
                                st.markdown(content)
                            elif material_type == "Quiz Questions":
                                # Quiz questions are essentially the same as flashcards
                                content = generate_flashcards(client, current_note["content"], topic_for_material)
                                st.markdown(content)
                            elif material_type == "Mind Map":
                                content = generate_mind_map(client, current_note["content"], topic_for_material)
                                st.markdown(content)
                            elif material_type == "Study Guide":
                                content = generate_study_guide(client, current_note["content"], topic_for_material)
                                st.markdown(content)
                            elif material_type == "Diagram":
                                content = generate_diagram(client, current_note["content"], topic_for_material)
                                st.markdown(content)
            else:
                st.info("Add content to your note to use these tools.")