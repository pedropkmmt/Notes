import os
import streamlit as st
from groq_client import get_ai_response

def generate_flashcards(client, notes, topic=None):
    """Generate flashcards from notes using the Groq API"""
    if topic:
        system_message = f"""You are a study assistant. Create 5-10 flashcards from the notes specifically about '{topic}'.
        Format each flashcard as:
        Q: [Question]
        A: [Answer]
        
        Make sure the flashcards cover key concepts, definitions, and important details about {topic}.
        If the topic isn't covered in the notes, generate a few general flashcards from the available content."""
    else:
        system_message = """You are a study assistant. Create 5-10 flashcards from the notes provided.
        Format each flashcard as:
        Q: [Question]
        A: [Answer]
        
        Cover key concepts, definitions, and important relationships between ideas.
        Include a mix of factual recall and conceptual understanding questions."""
    
    return get_ai_response(client, notes, system_message)

def generate_study_guide(client, notes, topic=None):
    """Generate a study guide from notes using the Groq API"""
    if topic:
        system_message = f"""You are a study assistant. Create a focused study guide about '{topic}' based on the provided notes.
        Include:
        1. Key definitions and concepts related to {topic}
        2. Important relationships and processes
        3. Notable examples or applications
        4. Common misconceptions to avoid
        5. Tips for better understanding
        
        Format the guide with clear headings and bullet points for easy review.
        If the topic isn't covered in the notes, create a study guide for the most relevant related content."""
    else:
        system_message = """You are a study assistant. Create a comprehensive study guide based on the provided notes.
        Include:
        1. Overview of main topics
        2. Key definitions and concepts for each topic
        3. Relationships between different concepts
        4. Common misconceptions to avoid
        5. Practice questions or examples
        
        Format the guide with clear headings and bullet points for easy review."""
    
    return get_ai_response(client, notes, system_message)

def generate_mind_map(client, notes, topic=None):
    """Generate a mind map description from notes using the Groq API"""
    if topic:
        system_message = f"""You are a study assistant. Create a text-based mind map about '{topic}' based on the provided notes.
        Format the mind map as:
        
        # {topic}
        - Main Concept 1
          - Subconcept 1.1
            - Detail 1.1.1
            - Detail 1.1.2
          - Subconcept 1.2
        - Main Concept 2
          - Subconcept 2.1
          - Subconcept 2.2
        
        Focus on showing hierarchical relationships and connections between concepts related to {topic}.
        If the topic isn't covered in the notes, create a mind map for the most relevant related content."""
    else:
        system_message = """You are a study assistant. Create a text-based mind map from the provided notes.
        Format the mind map as:
        
        # Main Topic
        - Main Concept 1
          - Subconcept 1.1
            - Detail 1.1.1
            - Detail 1.1.2
          - Subconcept 1.2
        - Main Concept 2
          - Subconcept 2.1
          - Subconcept 2.2
        
        Focus on showing hierarchical relationships and connections between concepts.
        Include all major topics from the notes with their related subtopics and details."""
    
    return get_ai_response(client, notes, system_message)

def generate_diagram(client, notes, topic=None):
    """Generate a diagram description or code from notes using the Groq API"""
    if topic:
        system_message = f"""You are a study assistant. Create a Mermaid diagram about '{topic}' based on the provided notes.
        Focus on visualizing:
        1. Process flows
        2. Hierarchical relationships
        3. Concept connections
        4. Sequential steps
        
        Choose the appropriate diagram type (flowchart, sequence, class, etc.) based on the content about {topic}.
        Provide the diagram in Mermaid syntax, surrounded by triple backticks with mermaid language specification.
        
        If the topic isn't covered in the notes, create a diagram for the most relevant related content."""
    else:
        system_message = """You are a study assistant. Create a Mermaid diagram based on the provided notes.
        Focus on visualizing:
        1. Process flows
        2. Hierarchical relationships
        3. Concept connections
        4. Sequential steps
        
        Choose the appropriate diagram type (flowchart, sequence, class, etc.) based on the content.
        Provide the diagram in Mermaid syntax, surrounded by triple backticks with mermaid language specification."""
    
    response = get_ai_response(client, notes, system_message)
    
    # To properly render Mermaid diagrams in Streamlit, we need some additional processing
    # We'll wrap the response to ensure proper rendering
    if "```mermaid" in response:
        # Extract just the mermaid code
        mermaid_start = response.find("```mermaid")
        mermaid_end = response.find("```", mermaid_start + 10)
        
        if mermaid_end > mermaid_start:
            mermaid_code = response[mermaid_start + 10:mermaid_end].strip()
            
            # Create a wrapper with explanation and the mermaid code for rendering
            processed_response = response[:mermaid_start].strip() + "\n\n"
            processed_response += "Here's a diagram based on your notes:\n\n"
            processed_response += f"```mermaid\n{mermaid_code}\n```\n\n"
            processed_response += response[mermaid_end + 3:].strip()
            
            return processed_response
    
    return response