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

# Load environment 
load_dotenv()

def initialize_groq():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(client, prompt, system_message="You are a helpful AI assistant. Provide clear and accurate responses to questions."):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error getting AI response: {str(e)}"

def generate_exam_from_notes(client, notes_content, num_questions=5, exam_type="multiple_choice"):
    """Generate exam questions based on the notes content"""
    system_message = f"""You are an education expert. Generate {num_questions} {exam_type} questions based on the following notes.
    For each question:
    1. Create a clear, concise question
    2. Provide answer options if multiple choice
    3. Include the correct answer
    4. Explain why the answer is correct
    
    Format the response as a JSON array with objects containing:
    - question: The question text
    - options: Array of options (for multiple choice)
    - answer: The correct answer
    - explanation: Brief explanation of the correct answer
    """
    
    prompt = f"Generate an exam based on these notes:\n\n{notes_content}"
    response = get_ai_response(client, prompt, system_message)
    
    # Try to parse the response as JSON
    try:
        # Sometimes the AI wraps the JSON in markdown code blocks or adds text
        # Let's try to extract just the JSON part
        if "```json" in response:
            json_text = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_text = response.split("```")[1].strip()
        else:
            json_text = response
            
        questions = json.loads(json_text)
        return questions
    except json.JSONDecodeError:
        # If parsing fails, return the raw response
        return [{"error": "Failed to parse AI response as JSON", "raw_response": response}]

def exam_interface():
    """Display the exam interface"""
    st.header("Exams")
    
    # Initialize client
    client = initialize_groq()
    
    # Initialize session state for exams
    if 'exams' not in st.session_state:
        st.session_state.exams = []
    if 'current_exam' not in st.session_state:
        st.session_state.current_exam = None
    if 'exam_results' not in st.session_state:
        st.session_state.exam_results = []
    
    # Create simple exam interface
    st.subheader("Create or Take Exams")

    exam_options = ["Create New Exam", "Take Practice Exam", "Review Previous Exams"]
    selected_option = st.selectbox("Select an option:", exam_options)
    
    if selected_option == "Create New Exam":
        st.write("### Create New Exam")
        exam_title = st.text_input("Exam Title:")
        
        # Source notes selection
        if 'notes' in st.session_state and st.session_state.notes:
            note_titles = [note["title"] for note in st.session_state.notes]
            selected_note = st.selectbox("Select notes to base exam on:", note_titles)
            
            # Find the selected note
            selected_note_content = next(
                (note["content"] for note in st.session_state.notes 
                 if note["title"] == selected_note), 
                ""
            )
            
            # Exam generation options
            question_type = st.selectbox("Question Type:", ["Multiple Choice", "True/False", "Short Answer"])
            num_questions = st.slider("Number of Questions:", 3, 20, 5)
            
            if st.button("Generate Exam"):
                if selected_note_content:
                    with st.spinner("Generating exam from notes..."):
                        exam_type = question_type.lower().replace(" ", "_")
                        questions = generate_exam_from_notes(client, selected_note_content, num_questions, exam_type)
                        
                        # Create new exam
                        new_exam = {
                            "title": exam_title if exam_title else f"Exam on {selected_note}",
                            "source_note": selected_note,
                            "date_created": datetime.now().timestamp(),
                            "questions": questions,
                            "id": len(st.session_state.exams)
                        }
                        
                        st.session_state.exams.append(new_exam)
                        st.success(f"Exam '{new_exam['title']}' created successfully!")
                        st.session_state.current_exam = new_exam["id"]
                else:
                    st.error("Selected note has no content. Please add content to your notes first.")
        else:
            st.warning("No notes available. Please create notes first before generating an exam.")
            
    elif selected_option == "Take Practice Exam":
        st.write("### Available Exams")
        
        if st.session_state.exams:
            exam_titles = [exam["title"] for exam in st.session_state.exams]
            selected_exam_title = st.selectbox("Select an exam to take:", exam_titles)
            
            # Find the selected exam
            selected_exam = next(
                (exam for exam in st.session_state.exams 
                 if exam["title"] == selected_exam_title), 
                None
            )
            
            if selected_exam:
                st.write(f"### {selected_exam['title']}")
                st.write(f"Based on: {selected_exam['source_note']}")
                
                # Show exam
                user_answers = []
                for i, q in enumerate(selected_exam["questions"]):
                    st.write(f"**Question {i+1}:** {q.get('question', '')}")
                    
                    # Handle different question types
                    if "options" in q and isinstance(q["options"], list):
                        # Multiple choice
                        options = q["options"]
                        answer = st.radio(
                            f"Select your answer for question {i+1}:",
                            options,
                            key=f"q_{i}"
                        )
                        user_answers.append(answer)
                    elif q.get("question", "").strip().endswith("?"):
                        # True/False
                        answer = st.radio(
                            f"Select your answer for question {i+1}:",
                            ["True", "False"],
                            key=f"q_{i}"
                        )
                        user_answers.append(answer)
                    else:
                        # Short answer
                        answer = st.text_area(
                            f"Your answer for question {i+1}:",
                            key=f"q_{i}"
                        )
                        user_answers.append(answer)
                
                if st.button("Submit Exam"):
                    score = 0
                    results = []
                    
                    for i, (q, user_answer) in enumerate(zip(selected_exam["questions"], user_answers)):
                        correct_answer = q.get("answer", "")
                        is_correct = (user_answer.lower() == correct_answer.lower())
                        
                        if is_correct:
                            score += 1
                            
                        results.append({
                            "question": q.get("question", ""),
                            "user_answer": user_answer,
                            "correct_answer": correct_answer,
                            "is_correct": is_correct,
                            "explanation": q.get("explanation", "")
                        })
                    
                    # Save results
                    exam_result = {
                        "exam_id": selected_exam["id"],
                        "exam_title": selected_exam["title"],
                        "date_taken": datetime.now().timestamp(),
                        "score": score,
                        "total_questions": len(selected_exam["questions"]),
                        "percentage": (score / len(selected_exam["questions"])) * 100 if selected_exam["questions"] else 0,
                        "results": results
                    }
                    
                    st.session_state.exam_results.append(exam_result)
                    st.success(f"Exam submitted! Your score: {score}/{len(selected_exam['questions'])} ({exam_result['percentage']:.1f}%)")
                    
                    # Show results
                    st.write("### Results")
                    for i, result in enumerate(results):
                        st.write(f"**Question {i+1}:** {result['question']}")
                        st.write(f"Your answer: {result['user_answer']}")
                        st.write(f"Correct answer: {result['correct_answer']}")
                        
                        if result['is_correct']:
                            st.success("Correct!")
                        else:
                            st.error("Incorrect")
                            
                        st.write(f"Explanation: {result['explanation']}")
                        st.divider()
        else:
            st.info("No exams available yet. Create one first!")
        
    else:  # Review Previous Exams
        st.write("### Exam History")
        
        if st.session_state.exam_results:
            for result in st.session_state.exam_results:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{result['exam_title']}**")
                with col2:
                    st.write(f"Score: {result['score']}/{result['total_questions']}")
                with col3:
                    st.write(f"{result['percentage']:.1f}%")
                
                if st.button(f"View Results", key=f"view_{result['exam_title']}_{result['date_taken']}"):
                    st.write("### Detailed Results")
                    for i, question_result in enumerate(result['results']):
                        st.write(f"**Question {i+1}:** {question_result['question']}")
                        st.write(f"Your answer: {question_result['user_answer']}")
                        st.write(f"Correct answer: {question_result['correct_answer']}")
                        
                        if question_result['is_correct']:
                            st.success("Correct!")
                        else:
                            st.error("Incorrect")
                            
                        st.write(f"Explanation: {question_result['explanation']}")
                        st.divider()
        else:
            st.info("No exam history available.")

def display_exams():
    """Function to display exams tab"""
    exam_interface()

def main():
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY not found in environment variables. Please check your .env file.")
        return

    st.set_page_config(layout="wide", page_title="Interactive Learning Platform")
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
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Whiteboard"

    st.title("Interactive Learning Platform")

    # Move tabs to sidebar
    with st.sidebar:
        st.header("Navigation")
        selected_tab = st.radio(
            "Select a section:",
            ["Whiteboard", "AI Chat", "Notes", "Exams"],
            key="sidebar_tabs"
        )
        st.session_state.current_tab = selected_tab
        
        st.divider()
        
        # Only show notes sidebar if on Notes tab
        if selected_tab == "Notes":
            display_notes_sidebar()

    # Main content area - show content based on selected tab
    if st.session_state.current_tab == "Whiteboard":
        display_whiteboard()
    elif st.session_state.current_tab == "AI Chat":
        display_ai_chat(client)
    elif st.session_state.current_tab == "Notes":
        display_notes_main(client)
    elif st.session_state.current_tab == "Exams":
        display_exams()

if __name__ == "__main__":
    main()
