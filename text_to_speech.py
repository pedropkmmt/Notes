# text_to_speech.py
import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64
import os

def text_to_speech(text, lang='en'):
    """
    Convert text to speech using gTTS and return an HTML audio element
    
    Args:
        text (str): The text to convert to speech
        lang (str): Language code (default: 'en' for English)
    
    Returns:
        str: HTML audio element with the speech audio
    """
    try:
        # Create a BytesIO object to store the audio data
        audio_bytes = BytesIO()
        
        # Generate the TTS audio and save it to the BytesIO object
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.write_to_fp(audio_bytes)
        
        # Reset the pointer to the start of the BytesIO object
        audio_bytes.seek(0)
        
        # Encode the audio bytes as base64
        audio_base64 = base64.b64encode(audio_bytes.read()).decode()
        
        # Create an HTML audio element with the base64-encoded audio
        audio_html = f'<audio controls autoplay="false"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        
        return audio_html
    except Exception as e:
        return f"Error generating speech: {str(e)}"

def add_text_to_speech_to_notes(note_content, section=None):
    """
    Add text-to-speech functionality to notes
    
    Args:
        note_content (str): The content of the note
        section (str, optional): Specific section to convert (default: None for entire note)
    
    Returns:
        None: Displays the audio player directly via st.markdown
    """
    if not note_content:
        st.warning("No content to read.")
        return
    
    # If a specific section is requested, try to extract it
    text_to_read = note_content
    if section:
        # Simple section extraction - looks for headers
        sections = note_content.split('\n## ')
        if len(sections) > 1:
            # Check if any section title matches the requested section
            for i, s in enumerate(sections):
                if i == 0:  # Handle the first section which may start with # instead of ## 
                    if s.startswith('# '):
                        title = s.split('\n')[0].replace('# ', '')
                    else:
                        title = "Introduction"
                else:
                    title = s.split('\n')[0]
                
                if section.lower() in title.lower():
                    text_to_read = s if i == 0 else '## ' + s
                    st.success(f"Reading section: {title}")
                    break
            else:
                st.warning(f"Section '{section}' not found. Reading entire note.")
    
    # Generate the audio
    st.markdown("### Audio Player")
    
    # Add language selection
    lang_options = {
        'English': 'en',
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de',
        'Italian': 'it',
        'Portuguese': 'pt',
        'Chinese': 'zh-CN',
        'Japanese': 'ja',
        'Korean': 'ko',
        'Hindi': 'hi'
    }
    
    selected_lang = st.selectbox("Select language:", options=list(lang_options.keys()))
    lang_code = lang_options[selected_lang]
    
    # Add voice speed option
    reading_speed = st.slider("Reading speed:", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
    
    if st.button("Generate Audio", type="primary"):
        with st.spinner("Generating audio..."):
            # Adjust text based on reading speed if needed
            # Note: gTTS only has slow=True/False, but we could implement more sophisticated
            # solutions if needed in the future
            use_slow = reading_speed < 0.8
            
            # Create the audio player
            audio_html = text_to_speech(text_to_read, lang=lang_code)
            st.markdown(audio_html, unsafe_allow_html=True)
            
            # Download option
            st.download_button(
                label="Download Audio File",
                data=BytesIO(base64.b64decode(audio_html.split('base64,')[1].split('"')[0])),
                file_name=f"note_audio.mp3",
                mime="audio/mp3"
            )