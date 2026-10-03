import os
import tempfile

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from langchain_community.document_loaders import PyPDFLoader

from resume_parser import parse_resume
from job_search import search_jobs
from job_researcher import research_jobs


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Job Searcher API is running"
    }


@app.post("/search-jobs")
async def search_jobs_api(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):
        return {
            "error": "Please upload a PDF resume."
        }

    data = await file.read()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp:

        temp.write(data)
        temp_path = temp.name

    try:

        # Load PDF
        loader = PyPDFLoader(temp_path)

        documents = loader.load()

        # Extract resume text
        resume_text = "\n".join(
            document.page_content
            for document in documents
        )

        # Parse resume
        profile = parse_resume(
            resume_text
        )

        # Find jobs
        raw_jobs = search_jobs(
            profile
        )

        # Research jobs
        jobs = research_jobs(
            raw_jobs
        )

        return {
            "candidate_profile": profile,
            "jobs": jobs
        }

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)