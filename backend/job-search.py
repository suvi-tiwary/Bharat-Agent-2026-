import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def search_jobs(profile):

    roles = ", ".join(profile["job_roles"])
    skills = ", ".join(profile["skills"])
    locations = ", ".join(profile["locations"])

    query = f"""
    Find current job openings for {roles}
    requiring skills like {skills}
    in {locations}.

    Prefer official company career pages
    and official job application pages.
    """

    response = tavily.search(
        query=query,
        search_depth="basic",
        max_results=5
    )

    jobs = []

    for result in response["results"]:

        job = {
            "title": result["title"],
            "url": result["url"],
            "description": result["content"]
        }

        jobs.append(job)

    return jobs