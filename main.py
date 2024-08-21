import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with Bunmi Chatbot!",
    page_icon=":brain:",
    layout="centered",
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else user_role

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display the chatbot's title on the page
st.title("🤖 Bunmi - Interview Assistant ChatBot")

# Step 1: Collect Input
st.subheader("Upload CV, Job Description, and Company Details")

cv = st.file_uploader("Upload your CV", type=["pdf", "docx", "txt"])
job_description = st.text_area("Paste the Job Description here")
company_details = st.text_input("Enter Company Details")

if st.button("Submit Details"):
    if not cv or not job_description or not company_details:
        st.error("Please provide all required information!")
    else:
        st.success("Details received! Let's move on to the interview.")

# Step 2: Generate Interview Questions based on job description
def generate_questions(job_description, company_details):
    prompt = (
        f"Generate interview questions based on the following job description: {job_description} "
        f"and the company details: {company_details}. Focus on key skills and experiences required."
    )
    response = model.send_message(prompt)
    return response.text.split('\n')  # Assume each line is a separate question

questions = []
if job_description and company_details:
    questions = generate_questions(job_description, company_details)

# Display generated questions and receive user responses
responses = []
if questions:
    st.subheader("Interview Questions")
    for idx, question in enumerate(questions):
        st.markdown(f"**Question {idx + 1}:** {question}")
        response = st.text_area(f"Your response to Question {idx + 1}", key=f"response_{idx}")
        if response:
            responses.append(response)

# Step 3: Evaluate Responses using STAR Method
def evaluate_star(response):
    # Here we mock a STAR evaluation
    star_feedback = "Your response should include: Situation, Task, Action, Result."
    
    # We could expand this by analyzing the response text, but this is a placeholder
    if "situation" not in response.lower() or "task" not in response.lower() or \
       "action" not in response.lower() or "result" not in response.lower():
        star_feedback += " Some elements are missing."
    else:
        star_feedback += " Great job including all STAR elements!"
    
    return star_feedback

feedback = []
if responses:
    st.subheader("Feedback on Your Responses")
    for idx, response in enumerate(responses):
        feedback.append(evaluate_star(response))
        st.markdown(f"**Feedback for Question {idx + 1}:** {feedback[-1]}")

# Step 4: Provide Model Answers (Example Implementation)
def generate_model_answer(question):
    prompt = f"Provide a model answer using the STAR method for the following question: {question}"
    response = model.send_message(prompt)
    return response.text

if feedback:
    st.subheader("Model Answers")
    for idx, question in enumerate(questions):
        if st.button(f"Show Model Answer for Question {idx + 1}"):
            model_answer = generate_model_answer(question)
            st.markdown(f"**Model Answer for Question {idx + 1}:** {model_answer}")
