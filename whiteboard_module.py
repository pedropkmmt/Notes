import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import cv2
import pytesseract
from PIL import Image
import io
import base64
import re
import sys
import os

# Import Groq functionality
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from groq_client import initialize_groq, get_ai_response

def preprocess_image(image_array):
    """Preprocess the image for better OCR results"""
    # Convert to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGBA2GRAY)
    
    # Apply threshold to get black and white image
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Dilate to connect nearby strokes
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    
    return dilated

def extract_text_from_image(image_array):
    """Extract text from image using OCR"""
    # Skip if image is empty (all white)
    if np.mean(image_array) > 250:  # Mostly white
        return "No content detected on whiteboard."
    
    # Preprocess the image
    processed_img = preprocess_image(image_array)
    
    # Convert numpy array to PIL Image
    pil_img = Image.fromarray(processed_img)
    
    try:
        # Extract text using pytesseract OCR
        text = pytesseract.image_to_string(pil_img)
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text).strip()
        
        if not text:
            return "Content detected but no text could be recognized. Try writing more clearly or drawing simpler diagrams."
        
        return text
    except Exception as e:
        return f"Error during OCR processing: {str(e)}"

def extract_math_from_image(image_array):
    """Attempt to extract mathematical notation from image"""
    # This is a simplified approach - in production you might use specialized math OCR
    processed_img = preprocess_image(image_array)
    
    # Save the processed image temporarily
    temp_img = Image.fromarray(processed_img)
    img_byte_arr = io.BytesIO()
    temp_img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Return base64 encoded image to show in the interface
    encoded = base64.b64encode(img_byte_arr).decode('utf-8')
    
    return encoded

def display_whiteboard():
    """Display the whiteboard tab with analysis functionality"""
    st.header("Interactive Whiteboard")
    
    # Initialize Groq client if not already in session state
    if 'groq_client' not in st.session_state:
        st.session_state.groq_client = initialize_groq()
    
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
    
    # Additional options for analysis
    if canvas_result.image_data is not None:
        analysis_type = st.radio(
            "Analysis Type",
            ["General Notes", "Mathematical Content", "Diagram/Drawing"],
            horizontal=True
        )
    
    # Process and analyze the whiteboard content
    if canvas_result.image_data is not None and analyze_button:
        with st.spinner("Analyzing whiteboard content..."):
            # Convert image data for processing
            image_array = np.array(canvas_result.image_data)
            
            if analysis_type == "General Notes":
                # Extract text using OCR
                extracted_text = extract_text_from_image(image_array)
                
                if "No content detected" in extracted_text or "Error" in extracted_text:
                    st.warning(extracted_text)
                else:
                    st.subheader("OCR Result")
                    st.text_area("Extracted Text", extracted_text, height=150)
                    
                    # Analyze the extracted text with Groq
                    with st.spinner("Analyzing notes with AI..."):
                        system_message = """You are an educational assistant. Analyze the following content extracted from a whiteboard:
                        1. Summarize the main points
                        2. Identify key concepts
                        3. Suggest areas for clarification if needed
                        4. Organize the information in a structured way
                        Please compensate for any OCR errors by inferring the most likely intended meaning."""
                        
                        ai_analysis = get_ai_response(st.session_state.groq_client, extracted_text, system_message)
                        st.subheader("AI Analysis")
                        st.markdown(ai_analysis)
            
            elif analysis_type == "Mathematical Content":
                # For math, get both the text and the image
                extracted_text = extract_text_from_image(image_array)
                encoded_img = extract_math_from_image(image_array)
                
                st.subheader("Detected Content")
                st.image(f"data:image/png;base64,{encoded_img}", caption="Processed Image", width=400)
                
                if extracted_text and "No content detected" not in extracted_text:
                    st.text_area("OCR Result (May have limitations with math symbols)", extracted_text, height=100)
                
                # Analyze with Groq using special math instructions
                with st.spinner("Interpreting mathematical content..."):
                    system_message = """You are a mathematics tutor. Analyze the following content extracted from a whiteboard:
                    1. Identify mathematical concepts, equations, or formulas
                    2. Explain the mathematical meaning
                    3. Correct any errors in the mathematical notation
                    4. Provide the proper LaTeX representation if applicable
                    
                    Note that OCR often struggles with mathematical symbols, so please use context to infer the most likely intended mathematics."""
                    
                    prompt = f"This is content from a mathematical whiteboard. The OCR extracted the following text (which may have errors with math symbols): {extracted_text}\n\nPlease interpret the mathematical content, correct any notation errors, and explain the concepts."
                    
                    ai_analysis = get_ai_response(st.session_state.groq_client, prompt, system_message)
                    st.subheader("AI Interpretation")
                    st.markdown(ai_analysis)
            
            else:  # Diagram/Drawing
                encoded_img = extract_math_from_image(image_array)
                
                st.subheader("Detected Diagram")
                st.image(f"data:image/png;base64,{encoded_img}", caption="Processed Diagram", width=400)
                
                # Analyze the diagram with Groq
                with st.spinner("Analyzing diagram..."):
                    system_message = """You are a visual content analyst. The user has drawn a diagram or illustration on a whiteboard.
                    Without seeing the actual image, please:
                    1. Ask them specific questions about what they've drawn to better understand it
                    2. Provide some general tips for creating effective diagrams for study purposes
                    3. Suggest how they might expand or improve their diagram"""
                    
                    prompt = "I've drawn a diagram/illustration on my study app whiteboard. Based on the type of diagrams commonly used in study notes, what questions should I ask myself to make sure this visualization is effective? What elements might I consider adding?"
                    
                    ai_analysis = get_ai_response(st.session_state.groq_client, prompt, system_message)
                    st.subheader("Diagram Analysis Guide")
                    st.markdown(ai_analysis)
                    
                    st.info("For more accurate diagram analysis, consider describing your diagram in the text area below.")
                    user_description = st.text_area("Describe your diagram to get better AI feedback:", height=100)
                    
                    if user_description and st.button("Get Custom Feedback", use_container_width=True):
                        with st.spinner("Generating custom feedback..."):
                            custom_prompt = f"I've drawn this diagram on my whiteboard: {user_description}. Can you analyze this diagram, explain what concepts it relates to, and suggest any improvements or extensions?"
                            custom_feedback = get_ai_response(st.session_state.groq_client, custom_prompt, system_message="You are a helpful educational assistant specializing in visual learning aids.")
                            st.markdown(custom_feedback)