import json
import os

import requests
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

TAVILY_URL = "https://api.tavily.com/search"


def _search_web(query: str, max_results: int) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("Add TAVILY_API_KEY to backend/.env to enable web search.")

    response = requests.post(
        TAVILY_URL,
        json={
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("results", [])


@tool("Search Jobs")
def search_jobs(query: str) -> str:
    """Search public web results for relevant job listings and application pages."""
    try:
        results = _search_web(f"{query} job opening careers apply", 8)
        jobs = [
            {
                "title": item.get("title", "Untitled role"),
                "company": "",
                "location": "",
                "link": item.get("url", ""),
                "description": item.get("content", "")[:500],
            }
            for item in results
        ]
        return json.dumps({"jobs": jobs})
    except Exception as error:
        return json.dumps({"error": str(error), "jobs": []})


@tool("Search Recruiter Contacts")
def search_hr_contact(company_name: str) -> str:
    """Search public web results for a company's recruiter or hiring team."""
    try:
        results = _search_web(
            f"{company_name} recruiter hiring team careers LinkedIn",
            5,
        )
        contacts = [
            {
                "name_or_page": item.get("title", ""),
                "url": item.get("url", ""),
                "source_summary": item.get("content", "")[:400],
            }
            for item in results
        ]
        return json.dumps({"company": company_name, "results": contacts})
    except Exception as error:
        return json.dumps({"company": company_name, "error": str(error), "results": []})


@tool("Search Learning Resources")
def search_learning_resources(skill: str) -> str:
    """Find free, credible courses and practice resources for a specific career skill."""
    try:
        results = _search_web(
            f"free course learn {skill} official documentation India students",
            5,
        )
        resources = [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "summary": item.get("content", "")[:400],
            }
            for item in results
        ]
        return json.dumps({"skill": skill, "resources": resources})
    except Exception as error:
        return json.dumps({"skill": skill, "error": str(error), "resources": []})