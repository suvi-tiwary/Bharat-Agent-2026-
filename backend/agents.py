import os

from crewai import Agent, LLM

from tools import search_hr_contact, search_jobs, search_learning_resources


def create_agents():
    groq_key = os.getenv("GROQ_API_KEY")
    mistral_key = os.getenv("MISTRAL_API_KEY")

    if groq_key:
        llm = LLM(
            model=os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
            api_key=groq_key,
        )
    elif mistral_key:
        llm = LLM(
            model=os.getenv("MISTRAL_MODEL", "mistral/mistral-large-latest"),
            api_key=mistral_key,
        )
    else:
        raise RuntimeError("Add GROQ_API_KEY or MISTRAL_API_KEY to backend/.env.")

    return [
        Agent(
            role="Resume analyst",
            goal="Extract a concise, evidence-based candidate profile from the resume.",
            backstory="You are a careful career analyst who never invents experience or skills.",
            llm=llm,
            verbose=False,
        ),
        Agent(
            role="Job researcher",
            goal="Find relevant, currently listed jobs and return useful application links.",
            backstory="You search job listings and clearly distinguish sourced facts from missing data.",
            tools=[search_jobs],
            llm=llm,
            verbose=False,
        ),
        Agent(
            role="Recruiter researcher",
            goal="Find public recruiter or hiring-team contact pages for relevant employers.",
            backstory="You use public information only and never fabricate a person's contact details.",
            tools=[search_hr_contact],
            llm=llm,
            verbose=False,
        ),
        Agent(
            role="Learning pathway researcher",
            goal="Find credible, accessible learning resources for the candidate's most important skill gaps.",
            backstory="You prioritize free, reputable resources and verify every suggested URL with web search.",
            tools=[search_learning_resources],
            llm=llm,
            verbose=False,
        ),
        Agent(
            role="Career strategist",
            goal="Turn sourced job and resume data into practical, tailored application guidance.",
            backstory="You write useful, specific advice and label unknown information honestly.",
            llm=llm,
            verbose=False,
        ),
    ]