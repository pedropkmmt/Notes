import os
from groq import Groq

def initialize_groq():
    """Initialize and return a Groq client"""
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(client, prompt, system_message="You are a helpful AI assistant. Provide clear and accurate responses to questions."):
    """Get a synchronous response from the Groq API"""
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
            model=os.getenv("GROQ_MODEL", "llama3-70b-8192"),  # Updated default model
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
            max_tokens=1024
        )
        
        response = chat_completion.choices[0].message.content
        
        # Enable LaTeX rendering for math-related responses
        if is_math_related:
            # Process response to enable LaTeX rendering using streamlit's markdown
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

def get_ai_response_streaming(client, prompt, system_message="You are a helpful AI assistant. Provide clear and accurate responses to questions."):
    """Get a streaming response from the Groq API"""
    try:
        # Check if the prompt is likely about mathematical content
        math_keywords = ["math", "equation", "formula", "symbol", "pi", "π", "sigma", "integral", 
                         "derivative", "calculus", "algebra", "theta", "alpha", "beta", "gamma"]
        
        is_math_related = any(keyword in prompt.lower() for keyword in math_keywords)
        
        if is_math_related:
            # Add special instruction for mathematical content display
            system_message += " If the user asks about mathematical concepts, display equations and symbols using LaTeX for proper formatting."
        
        # Create the streaming chat completion
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            model=os.getenv("GROQ_MODEL", "llama3-70b-8192"),  
            temperature=float(os.getenv("AI_TEMPERATURE", "1")),
            stream=True,
           max_completion_tokens=1024
        )
        
        # Collect response for potential math symbol processing
        full_response = ""
        
        # Stream the response
        for chunk in completion:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
        
        # If math-related, do post-processing for LaTeX symbols
        if is_math_related:
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
                full_response = full_response.replace(f" {symbol} ", f" {latex} ")
                full_response = full_response.replace(f" {symbol},", f" {latex},")
                full_response = full_response.replace(f" {symbol}.", f" {latex}.")
            
            # Yield a final LaTeX instruction
            yield "\n\n*Note: This response contains mathematical notation. Best viewed with LaTeX rendering enabled.*"
    
    except Exception as e:
        yield f"Error getting AI response: {str(e)}"


def analyze_notes(client, notes):
    """Analyze notes using the Groq API"""
    system_message = """You are an educational analyst. Analyze the following notes and provide:
    1. Main concepts covered
    2. Knowledge gaps or areas needing clarification
    3. Suggestions for better organization
    4. Key points to review
    Be specific and constructive in your feedback."""
    
    return get_ai_response(client, notes, system_message)

def analyze_notes_streaming(client, notes):
    """Analyze notes using streaming Groq API"""
    system_message = """You are an educational analyst. Analyze the following notes and provide:
    1. Main concepts covered
    2. Knowledge gaps or areas needing clarification
    3. Suggestions for better organization
    4. Key points to review
    Be specific and constructive in your feedback."""
    
    return get_ai_response_streaming(client, notes, system_message)

def generate_summary(client, notes, topic=None):
    """Generate a summary of notes using the Groq API"""
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

def generate_summary_streaming(client, notes, topic=None):
    """Generate a streaming summary of notes using the Groq API"""
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
    
    return get_ai_response_streaming(client, notes, system_message)
