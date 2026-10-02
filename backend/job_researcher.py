import os
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def scrape_job_page(job):
    """
    Open the job page and extract job information.
    """

    url = job["url"]

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if response.status_code != 200:
            return {
                "status": "failed",
                "job_url": url,
                "error": f"HTTP {response.status_code}"
            }

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Page title
        page_title = ""

        if soup.title:
            page_title = soup.title.get_text(
                strip=True
            )

        # Extract all visible text
        page_text = soup.get_text(
            " ",
            strip=True
        )

        # --------------------------------
        # FIND APPLY LINK
        # --------------------------------

        apply_link = None

        for link in soup.find_all("a", href=True):

            text = link.get_text(
                " ",
                strip=True
            ).lower()

            href = link["href"]

            if (
                "apply" in text
                or "apply now" in text
                or "submit application" in text
            ):

                apply_link = urljoin(
                    url,
                    href
                )

                break

        return {
            "status": "success",
            "job_title": job.get("title"),
            "job_url": url,
            "page_title": page_title,
            "official_apply_link": apply_link,
            "page_content": page_text[:8000]
        }

    except Exception as e:

        return {
            "status": "failed",
            "job_url": url,
            "error": str(e)
        }


def find_company_and_hr(job_data):
    """
    Use Tavily to identify the company and
    find publicly available recruiting information.
    """

    job_url = job_data["job_url"]

    query = f"""
    Research this job posting:

    {job_url}

    Identify:

    1. Company name
    2. Job title
    3. Job location
    4. Publicly listed recruiter or talent acquisition contact
    5. Public professional recruiting email if available
    6. Public business phone number if explicitly listed
    7. Official company careers page

    Only use publicly available professional information.

    Do not guess:
    - personal phone numbers
    - personal emails
    - private contact information

    Prefer the company's official website
    and official careers pages.
    """

    try:

        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )

        sources = []

        for result in response.get(
            "results",
            []
        ):

            sources.append({
                "title": result.get("title"),
                "url": result.get("url"),
                "content": result.get("content")
            })

        return sources

    except Exception as e:

        return {
            "error": str(e)
        }


def research_job(job):
    """
    Complete research for one job.
    """

    # Step 1:
    # Scrape the actual job page

    scraped = scrape_job_page(job)

    if scraped["status"] != "success":

        return scraped

    # Step 2:
    # Research company + public HR information

    hr_information = find_company_and_hr(
        scraped
    )

    # Step 3:
    # Combine everything

    return {
        "job_title": scraped.get(
            "job_title"
        ),

        "job_url": scraped.get(
            "job_url"
        ),

        "official_apply_link": scraped.get(
            "official_apply_link"
        ),

        "page_title": scraped.get(
            "page_title"
        ),

        "job_description": scraped.get(
            "page_content"
        ),

        "company_research": hr_information
    }


def research_jobs(jobs):
    """
    Research multiple jobs.
    """

    results = []

    for job in jobs:

        result = research_job(job)

        results.append(result)

    return results