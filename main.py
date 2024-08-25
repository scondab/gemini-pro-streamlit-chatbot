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

cv = st.file_uploader("Upload your CV", type=["pdf"])
job_description = st.text_area("Paste the Job Description here")
company_details_url = st.text_input("Enter Company Details URL")

if st.button("Submit Details"):
    if not cv or not job_description or not company_details_url:
        st.error("Please provide all required information!")
    else:
        st.success("Details received! Let's move on to the interview preparation.")

# Step 2: Summarize Learnings
def summarize_learnings(job_description, company_details_url):
    prompt = (
        f"Act like a professional job interview coach.\n\n"
        f"### Job Description ###\n{job_description}\n### Job Description ###\n\n"
        f"### Company's Website ###\nBrowse the internet to get information from this website: {company_details_url}\n### Company's Website ###\n\n"
        "Step 2: Write a quick summary of your learnings, and who you have to become in order to be my job interviewer."
    )
    response = model.send_message(prompt)
    return response.text

summary = ""
if job_description and company_details_url:
    summary = summarize_learnings(job_description, company_details_url)
    st.subheader("Learnings Summary")
    st.write(summary)

# Step 3: Read CV and Tailor Answers
def tailor_answers(cv):
    prompt = (
        f"Step 3: Read my resume / CV (uploaded as a PDF) to tailor your perfect answers later on.\n\n"
        f"CV Content:\n{cv}\n"
    )
    response = model.send_message(prompt)
    return response.text

if cv and summary:
    tailored_summary = tailor_answers(cv.read().decode("utf-8"))
    st.subheader("Tailored Interview Preparation")
    st.write(tailored_summary)

# Step 4: Start the Job Interview
def start_interview(job_description):
    prompt = (
        f"Step 4: Start the job interview, one question at a time, like a real simulation.\n\n"
        f"### Job Description ###\n{job_description}\n### Job Description ###"
    )
    response = model.send_message(prompt)
    return response.text

questions = []
if job_description:
    questions = start_interview(job_description).split('\n')

responses = []
if questions:
    st.subheader("Job Interview Simulation")
    for idx, question in enumerate(questions):
        st.markdown(f"**Question {idx + 1}:** {question}")
        response = st.text_area(f"Your response to Question {idx + 1}", key=f"response_{idx}")
        if response:
            responses.append(response)

# Step 5: Provide Detailed Feedback Using the CARL Method
def provide_feedback(response, question):
    prompt = (
        f"Step 5: Once I answered, I want you to provide 5 paragraphs, divided by line breaks.\n\n"
        f"Paragraph 1 = What was good in my answer?\n"
        f"Paragraph 2 = What was bad in my answer?\n"
        f"Paragraph 3 = What could be added to my answer?\n"
        f"Paragraph 4 = Pretend you are me & write a detailed perfect answer using the CARL method.\n"
        f"Paragraph 5 = Ask me if we can move on to the next interview question.\n\n"
        f"My Answer: {response}\n\n"
        f"Question: {question}"
    )
    feedback_response = model.send_message(prompt)
    return feedback_response.text

feedback = []
if responses:
    st.subheader("Detailed Feedback on Your Responses")
    for idx, response in enumerate(responses):
        if response:
            feedback_text = provide_feedback(response, questions[idx])
            feedback.append(feedback_text)
            st.markdown(f"**Feedback for Question {idx + 1}:**")
            st.write(feedback_text)

# Ask if ready to move on to the next question
if feedback:
    if st.button("Move on to the next interview question?"):
        st.write("Great! Let's continue...")
