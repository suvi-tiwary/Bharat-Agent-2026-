import os
import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def search_jobs(profile):

    roles = ", ".join(profile.get("job_roles", []))
    skills = ", ".join(profile.get("skills", []))
    locations = ", ".join(profile.get("locations", []))

    query = f"""
    Find current job openings for {roles}
    requiring skills like {skills}
    in {locations}.

    Prefer official company career pages
    and official job application pages.
    Only return currently relevant job openings.
    """

    response = requests.post(
        "https://api.tavily.com/search",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": 5
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    jobs = []

    for result in data.get("results", []):

        job = {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "description": result.get("content", "")
        }

        jobs.append(job)

    return jobs