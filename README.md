# Your Note 🚀
![Screenshot_19-3-2025_192055_localhost](https://github.com/user-attachments/assets/629e7eeb-1f54-4ffb-80d7-1279aa7f13d4)
##AUTHORS
https://www.linkedin.com/in/pedro-muttenda-944834225

##Article and Landing Page
https://docs.google.com/document/d/15O34EfPjfC2h1lFSssFb1iwewh5W_vSeCqrYc3Y2NTc/edit?usp=sharing

https://polite-cajeta-1eb67d.netlify.app

## Overview

Your Note is an AI-powered platform designed to help students understand their studies better by providing personalized learning support through advanced AI technologies.

##Installation

To install all the required dependencies for your project, you can use the following command:  

```bash
pip install streamlit streamlit-drawable-canvas pillow pandas groq gtts opencv-python pytesseract numpy
```

### **Additional Installation Notes:**
1. **Tesseract OCR (for PyTesseract)**  
   If you're using **PyTesseract** for text recognition, you also need to install **Tesseract-OCR** separately:  
   - **Windows**: Download and install it from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki). Then, add the path to your environment variables.
   - **Linux (Debian/Ubuntu)**:  
     ```bash
     sudo apt install tesseract-ocr
     ```
   - **Mac (Homebrew)**:  
     ```bash
     brew install tesseract
     ```

2. **Verifying Installation**  
   After installing, you can check if everything is installed correctly by running:
   ```bash
   python -c "import streamlit, pillow, pandas, groq, gtts, cv2, pytesseract, numpy; print('All dependencies installed successfully!')"
   ```
  Here’s a structured **README** section covering **Usage, Contributing, Related Projects, and Licensing** for your project:  

---

## **Usage**  
This AI-powered study assistant helps students learn more effectively by leveraging AI for note analysis, test generation, and text-to-audio conversion.  

### **Features:**  
- **AI-Powered Study Assistant:** Upload or write study notes, and the AI will summarize key concepts, highlight knowledge gaps, and suggest improvements.  
- **Test Generation:** Automatically create multiple-choice and short-answer questions from notes for self-assessment.  
- **Text-to-Audio Conversion:** Convert study materials into speech using Google Text-to-Speech (gTTS) for auditory learners.  
- **Handwritten Note Recognition:** Upload handwritten notes, and the system will extract and analyze the text.  
- **Writable/Drawable Canvas:** A digital whiteboard where students can write or draw, with AI-powered feedback.  

### **Running the Project**  
1. Install dependencies:  
   ```bash
   pip install streamlit streamlit-drawable-canvas pillow pandas groq gtts opencv-python pytesseract numpy
   ```
2. Run the application:  
   ```bash
   streamlit run main.py
   ```
   Replace `main.py` with the actual entry-point script of your project.  

---

## **Contributing**  
We welcome contributions! Here's how you can get involved:  

1. **Fork the Repository**  
2. **Clone Your Fork**  
   ```bash
   git clone https://github.com/your-username/project-name.git
   cd project-name
   ```
3. **Create a New Branch**  
   ```bash
   git checkout -b feature-name
   ```
4. **Make Changes & Commit**  
   ```bash
   git add .
   git commit -m "Added a new feature"
   ```
5. **Push Your Changes**  
   ```bash
   git push origin feature-name
   ```
6. **Create a Pull Request (PR)** on GitHub and wait for review.  

Contributions can include bug fixes, new features, improved documentation, or optimizations.  

---

## **Related Projects**  
If you find this project useful, you might also like:  
- **[Streamlit](https://streamlit.io/)** – A Python framework for building interactive web apps.  
- **[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)** – Optical Character Recognition (OCR) engine used for extracting text from images.  
- **[Google Text-to-Speech (gTTS)](https://github.com/pndurette/gTTS)** – A Python library for converting text to speech.  
- **[Llama AI by Groq](https://groq.com/)** – AI model powering text-based AI interactions in this project.  

---

## **License**  
This project is licensed under the **MIT License**.  

```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---




