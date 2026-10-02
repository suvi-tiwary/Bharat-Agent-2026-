from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import tempfile
import os

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