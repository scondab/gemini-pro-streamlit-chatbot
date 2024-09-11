import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import PyPDF2

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Interview Assistant Chatbot",
    page_icon=":briefcase:",
    layout="wide",
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Function to read PDF content
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Display the app title
st.title("🤖 Interview Assistant Chatbot")

# Step 1: Collect Input
st.header("Step 1: Provide Job and Company Information")

cv = st.file_uploader("Upload your CV (PDF format)", type=["pdf"])
job_description = st.text_area("Paste the Job Description here")
company_website = st.text_area("Paste the 'About Us' section from the company's website")

# Step 2: Summarize Learnings
def summarize_learnings(job_description, company_website):
    prompt = (
        f"Act like a professional job interview coach.\n\n"
        f"### Job Description ###\n{job_description}\n### Job Description ###\n\n"
        f"### Company's Website ###\n{company_website}\n### Company's Website ###\n\n"
        "Step 2: Write a quick summary of your learnings, and who you have to become in order to be the job interviewer."
    )
    response = st.session_state.chat_session.send_message(prompt)
    return response.text

if st.button("Generate Interview Preparation Summary"):
    if not job_description or not company_website:
        st.error("Please provide both the job description and company details.")
    else:
        with st.spinner("Generating summary..."):
            summary = summarize_learnings(job_description, company_website)
            st.session_state.summary = summary
        st.success("Summary generated successfully!")

if 'summary' in st.session_state:
    st.subheader("Interview Preparation Summary")
    st.write(st.session_state.summary)

# Step 3: Read CV and Tailor Answers
def tailor_answers(cv_content):
    prompt = (
        f"Step 3: Read the following resume/CV to tailor your perfect answers later on.\n\n"
        f"CV Content:\n{cv_content}\n"
    )
    response = st.session_state.chat_session.send_message(prompt)
    return response.text

if cv and 'summary' in st.session_state:
    with st.spinner("Analyzing CV..."):
        cv_content = read_pdf(cv)
        tailored_summary = tailor_answers(cv_content)
    st.session_state.tailored_summary = tailored_summary
    st.success("CV analyzed and information tailored for the interview!")

# Step 4: Start the Job Interview
def start_interview(job_description):
    prompt = (
        f"Step 4: Start the job interview simulation. Provide one challenging and relevant interview question based on the following job description:\n\n"
        f"### Job Description ###\n{job_description}\n### Job Description ###"
    )
    response = st.session_state.chat_session.send_message(prompt)
    return response.text

if 'tailored_summary' in st.session_state:
    st.header("Step 4: Job Interview Simulation")
    if 'current_question' not in st.session_state:
        with st.spinner("Generating interview question..."):
            st.session_state.current_question = start_interview(job_description)
    
    st.subheader("Interview Question:")
    st.write(st.session_state.current_question)
    
    user_answer = st.text_area("Your Answer:", key="user_answer")

    if st.button("Submit Answer"):
        if user_answer:
            st.session_state.user_answer = user_answer
            st.success("Answer submitted. Generating feedback...")
        else:
            st.warning("Please provide an answer before submitting.")

# Step 5: Provide Detailed Feedback Using the CARL Method
def provide_feedback(response, question):
    prompt = (
        f"Step 5: Provide detailed feedback on the following answer to the interview question. "
        f"Use the CARL method and structure your response in 5 paragraphs:\n\n"
        f"Question: {question}\n"
        f"Candidate's Answer: {response}\n\n"
        f"Paragraph 1: What was good in the answer?\n"
        f"Paragraph 2: What was bad in the answer?\n"
        f"Paragraph 3: What could be added to the answer?\n"
        f"Paragraph 4: A detailed perfect answer using the CARL method.\n"
        f"Paragraph 5: Ask if we should move on to the next interview question."
    )
    feedback_response = st.session_state.chat_session.send_message(prompt)
    return feedback_response.text

if 'user_answer' in st.session_state:
    with st.spinner("Generating feedback..."):
        feedback = provide_feedback(st.session_state.user_answer, st.session_state.current_question)
    
    st.subheader("Feedback on Your Answer:")
    feedback_paragraphs = feedback.split('\n\n')
    for i, paragraph in enumerate(feedback_paragraphs, 1):
        if i == 1:
            st.markdown("### What was good in your answer?")
        elif i == 2:
            st.markdown("### What was bad in your answer?")
        elif i == 3:
            st.markdown("### What could be added to your answer?")
        elif i == 4:
            st.markdown("### Perfect answer using the CARL method")
        elif i == 5:
            st.markdown("### Next steps")
        st.write(paragraph)
    
    if st.button("Next Question"):
        del st.session_state.current_question
        del st.session_state.user_answer
        st.experimental_rerun()

# Add a sidebar with instructions
st.sidebar.title("How to Use This App")
st.sidebar.markdown("""
1. Upload your CV (PDF format)
2. Paste the job description
3. Paste the 'About Us' section from the company's website
4. Click 'Generate Interview Preparation Summary'
5. Answer the interview questions
6. Receive detailed feedback
7. Continue with more questions to improve your skills
""")
