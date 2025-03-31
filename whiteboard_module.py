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
    """Display the whiteboard tab with enhanced analysis functionality"""
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
        
        # Add field for subject area to provide better context
        subject_area = st.selectbox(
            "Subject Area (for better analysis)",
            ["General", "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", 
             "Economics", "History", "Literature", "Engineering", "Other"]
        )
        
        if subject_area == "Other":
            custom_subject = st.text_input("Specify subject:")
            if custom_subject:
                subject_area = custom_subject
    
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
                    
                    # Enhanced analysis with Groq
                    with st.spinner("Performing comprehensive analysis..."):
                        system_message = f"""You are an educational assistant specializing in {subject_area}. 
                        Analyze the following content extracted from a whiteboard:
                        
                        1. Tell the user exactly what concepts, topics, or ideas are present on their whiteboard
                        2. Explain the significance and applications of these concepts in {subject_area}
                        3. Identify key relationships between concepts
                        4. Suggest real-world contexts where these concepts are applied
                        5. Recommend related topics the user might want to explore next
                        6. If there appear to be errors or misconceptions, tactfully correct them
                        7. Organize the information in a more structured way if needed
                        
                        Please compensate for any OCR errors by inferring the most likely intended meaning."""
                        
                        ai_analysis = get_ai_response(st.session_state.groq_client, extracted_text, system_message)
                        st.subheader("Comprehensive Analysis")
                        st.markdown(ai_analysis)
                        
                        # Add additional insights section
                        st.subheader("Practical Applications")
                        practical_prompt = f"Based on these concepts from {subject_area}: {extracted_text}\n\nProvide 3-5 specific real-world applications or scenarios where these concepts are used in practice. Be specific and concrete."
                        practical_insights = get_ai_response(st.session_state.groq_client, practical_prompt, "You are a practical application specialist.")
                        st.markdown(practical_insights)
            
            elif analysis_type == "Mathematical Content":
                # For math, get both the text and the image
                extracted_text = extract_text_from_image(image_array)
                encoded_img = extract_math_from_image(image_array)
                
                st.subheader("Detected Content")
                st.image(f"data:image/png;base64,{encoded_img}", caption="Processed Image", width=400)
                
                if extracted_text and "No content detected" not in extracted_text:
                    st.text_area("OCR Result (May have limitations with math symbols)", extracted_text, height=100)
                
                # Enhanced math analysis with Groq
                with st.spinner("Interpreting mathematical content..."):
                    system_message = f"""You are a mathematics tutor specializing in {subject_area}. 
                    Analyze the following content extracted from a whiteboard:
                    
                    1. Clearly identify all mathematical concepts, equations, or formulas present
                    2. Explain what these mathematical expressions represent in plain language
                    3. Correct any errors in the mathematical notation
                    4. Provide the proper LaTeX representation if applicable
                    5. Explain where and how these mathematical concepts are applied in {subject_area} and related fields
                    6. Provide step-by-step explanations for any procedures or proofs
                    7. Connect these concepts to prerequisites and more advanced topics
                    
                    Note that OCR often struggles with mathematical symbols, so please use context to infer the most likely intended mathematics."""
                    
                    prompt = f"This is content from a mathematical whiteboard related to {subject_area}. The OCR extracted the following text (which may have errors with math symbols): {extracted_text}\n\nPlease interpret the mathematical content, identify all concepts present, correct any notation errors, and explain both the mathematical meaning and practical applications."
                    
                    ai_analysis = get_ai_response(st.session_state.groq_client, prompt, system_message)
                    st.subheader("Mathematical Interpretation")
                    st.markdown(ai_analysis)
                    
                    # Add examples section
                    st.subheader("Example Problems")
                    examples_prompt = f"Based on the mathematical concepts identified ({extracted_text}), provide 2-3 example problems with solutions that would help reinforce understanding of these concepts."
                    examples = get_ai_response(st.session_state.groq_client, examples_prompt, "You are a mathematics educator.")
                    st.markdown(examples)
            
            else:  # Diagram/Drawing
                encoded_img = extract_math_from_image(image_array)
                
                st.subheader("Detected Diagram")
                st.image(f"data:image/png;base64,{encoded_img}", caption="Processed Diagram", width=400)
                
                # Provide options for diagram type to improve analysis
                diagram_type = st.selectbox(
                    "What type of diagram have you drawn?",
                    ["Concept Map", "Flow Chart", "Process Diagram", "System Architecture", 
                     "Molecular Structure", "Circuit Diagram", "Free-form Sketch", "Other"]
                )
                
                # Enhanced diagram analysis
                with st.spinner("Analyzing diagram..."):
                    system_message = f"""You are a visual content analyst specializing in {subject_area} diagrams.
                    For the user's {diagram_type}, please provide:
                
                    1. An explanation of what this type of diagram typically represents in {subject_area}
                    2. The key components that should be present in this type of diagram
                    3. How to effectively use this type of visualization for learning or communication
                    4. Common applications of this diagram type in academic and professional contexts
                    5. How this type of diagram connects to other forms of representation in {subject_area}
                    6. Advanced techniques for enhancing this type of diagram"""
                    
                    prompt = f"I've drawn a {diagram_type} related to {subject_area} on my study app whiteboard. Please help me understand how to make this visualization more effective and how it's used in real-world contexts."
                    
                    ai_analysis = get_ai_response(st.session_state.groq_client, prompt, system_message)
                    st.subheader("Diagram Analysis")
                    st.markdown(ai_analysis)
                    
                    st.info("For more accurate diagram analysis, describe your diagram below.")
                    user_description = st.text_area("Describe your diagram to get better AI feedback:", height=100)
                    
                    if user_description and st.button("Get Custom Feedback", use_container_width=True):
                        with st.spinner("Generating custom feedback..."):
                            custom_prompt = f"I've drawn this {diagram_type} related to {subject_area} on my whiteboard: {user_description}. Please analyze this diagram, explain what concepts it represents, where these concepts are used in real-world applications, and suggest improvements or extensions."
                            
                            custom_system = f"""You are an expert in {subject_area} visualization. Provide a detailed analysis that includes:
                            1. A complete explanation of what's on the user's whiteboard based on their description
                            2. How each element relates to key concepts in {subject_area}
                            3. Specific real-world applications where this diagram or these concepts are used
                            4. How professionals and researchers use similar diagrams
                            5. Suggested improvements for clarity and completeness
                            6. Related concepts that could be incorporated
                            """
                            
                            custom_feedback = get_ai_response(st.session_state.groq_client, custom_prompt, custom_system)
                            st.subheader("Custom Diagram Analysis")
                            st.markdown(custom_feedback)
                            
                # Add a section for related resources
                st.subheader("Learning Resources")
                resources_prompt = f"Based on this {diagram_type} related to {subject_area}, suggest learning resources (categories of books, online courses, or tools - not specific titles) that would help the user deepen their understanding of these concepts."
                resources = get_ai_response(st.session_state.groq_client, resources_prompt, "You are an educational resource specialist.")
                st.markdown(resources)
