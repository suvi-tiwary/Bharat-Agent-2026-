from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from farmerSchema import FarmerProfile
from agents import ProfileAgent


app = FastAPI(title="KisanSahayak")


# Allow your React frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create our Profile Agent
profile_agent = ProfileAgent()


# Temporary storage for farmers
profiles = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/")
def home():

    return {
        "message": "KisanSahayak API is running"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    # --------------------------------
    # 1. Get farmer's existing profile
    # --------------------------------

    if request.session_id not in profiles:

        profiles[request.session_id] = FarmerProfile()


    profile = profiles[request.session_id]


    # --------------------------------
    # 2. Give farmer's message
    #    to Profile Agent
    # --------------------------------

    result = profile_agent.process(
        request.message,
        profile
    )


    # --------------------------------
    # 3. Get updated profile
    # --------------------------------

    updated_profile = result["profile"]


    # --------------------------------
    # 4. Save it
    # --------------------------------

    profiles[request.session_id] = updated_profile


    # --------------------------------
    # 5. Send result back
    # --------------------------------

    return {

        "message": result["next_question"],

        "profile": updated_profile.model_dump(),

        "extracted": result["extracted"],

        "missing_information":
            result["missing_information"]
    }