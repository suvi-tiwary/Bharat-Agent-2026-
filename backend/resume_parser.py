import os
import json

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model=os.getenv("GROQ_MODEL"),
    temperature=0
)

def parse_resume(resume_text):

    prompt = f"""
Read this resume and extract the candidate information.

Return ONLY JSON.

Format:

{{
    "name": "",
    "skills": [],
    "education": [],
    "projects": [],
    "experience": [],
    "job_roles": [],
    "locations": []
}}

Do not invent information.

Resume:

{resume_text}
"""

    response = llm.invoke(prompt)

    return json.loads(response.content)