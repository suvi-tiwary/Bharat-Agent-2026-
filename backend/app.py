import streamlit as st
from PyPDF2 import PdfReader
import io
from main import run_crew

st.set_page_config(page_title="JobMatch AI", page_icon="🚀", layout="wide")

st.title("🚀 JobMatch AI: Your Personal Career Agent")
st.markdown("Upload your resume. Our AI agents will find the best jobs, analyze your resume gaps, and write personalized outreach emails to HR.")

# File Upload
uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    # Extract text from PDF
    pdf_reader = PdfReader(uploaded_file)
    resume_text = ""
    for page in pdf_reader.pages:
        resume_text += page.extract_text() + "\n"
    
    st.success("Resume parsed successfully!")
    
    if st.button("Find My Dream Jobs & Generate Outreach", type="primary"):
        with st.spinner("🤖 AI Agents are analyzing your resume, searching jobs, and finding HR contacts... (This takes ~1-2 mins)"):
            try:
                # Run the Crew
                final_report = run_crew(resume_text)
                
                # Display Results
                st.markdown("---")
                st.header("🎯 Your Matched Opportunities")
                st.markdown(final_report)
                
                st.balloons()
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.info("Check your API keys in the .env file.")
else:
    st.info("Please upload your resume to get started.")