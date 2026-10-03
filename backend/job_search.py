import os
import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def search_jobs(profile):

    roles = profile.get("job_roles", [])
    skills = profile.get("skills", [])
    locations = profile.get("locations", [])

    roles_text = ", ".join(roles)
    skills_text = ", ".join(skills)
    locations_text = ", ".join(locations)

    query = f"""
Find individual CURRENT job openings matching this candidate.

Roles:
{roles_text}

Skills:
{skills_text}

Locations:
{locations_text}

IMPORTANT:
Return individual job postings, NOT:
- search result pages
- category pages
- job listing aggregators
- "page 2/page 3" pages
- general career pages

Prefer:
- official company job pages
- Greenhouse job pages
- Lever job pages
- Workday job pages
- individual company career postings

Find at least 10 relevant individual job postings if available.
"""

    response = requests.post(
        "https://api.tavily.com/search",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "max_results": 10,
            "include_answer": False
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    jobs = []

    for result in data.get("results", []):

        title = result.get("title", "")
        url = result.get("url", "")
        description = result.get("content", "")

        if not url:
            continue

        # Remove obvious search/category pages
        bad_words = [
            "page 2",
            "page 3",
            "page 4",
            "page 5",
            "search",
            "search-results",
            "job-search",
            "jobs-in-",
            "jobs?keyword="
        ]

        url_lower = url.lower()
        title_lower = title.lower()

        if any(word in url_lower for word in bad_words):
            continue

        if "page 3" in title_lower or "page 2" in title_lower:
            continue

        jobs.append({
            "title": title,
            "url": url,
            "description": description
        })

    return jobs[:10]