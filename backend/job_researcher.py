import os
import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# =========================================================
# SCRAPE JOB PAGE
# =========================================================

def scrape_job_page(job):

    url = job.get("url")

    if not url:
        return {
            "status": "failed",
            "error": "Job URL missing"
        }

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/154.0 Safari/537.36"
                )
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

        # -----------------------------
        # TITLE
        # -----------------------------

        page_title = ""

        if soup.title:
            page_title = soup.title.get_text(
                strip=True
            )

        job_title = job.get("title", "")

        # -----------------------------
        # PAGE TEXT
        # -----------------------------

        page_text = soup.get_text(
            " ",
            strip=True
        )

        # -----------------------------
        # FIND APPLY LINK
        # -----------------------------

        apply_link = None

        for link in soup.find_all(
            "a",
            href=True
        ):

            text = link.get_text(
                " ",
                strip=True
            ).lower()

            href = link["href"]

            if (
                "apply" in text
                or "submit application" in text
            ):

                apply_link = urljoin(
                    url,
                    href
                )

                break

        # -----------------------------
        # TRY TO FIND COMPANY
        # -----------------------------

        company = None

        meta_company = soup.find(
            "meta",
            attrs={
                "property": "og:site_name"
            }
        )

        if meta_company:
            company = meta_company.get(
                "content"
            )

        if not company:

            meta_company = soup.find(
                "meta",
                attrs={
                    "name": "author"
                }
            )

            if meta_company:
                company = meta_company.get(
                    "content"
                )

        return {
            "status": "success",
            "job_title": job_title,
            "job_url": url,
            "page_title": page_title,
            "company": company,
            "official_apply_link": apply_link,
            "job_description": page_text[:12000]
        }

    except Exception as e:

        return {
            "status": "failed",
            "job_url": url,
            "error": str(e)
        }


# =========================================================
# COMPANY + PUBLIC RECRUITER RESEARCH
# =========================================================

def research_company(job_data):

    job_url = job_data.get("job_url")
    job_title = job_data.get("job_title")
    page_text = job_data.get("job_description", "")

    query = f"""
Research this specific job posting:

Job:
{job_title}

URL:
{job_url}

Find reliable PUBLIC information about:

1. Company name
2. Company official website
3. Official careers page
4. Job location
5. Public recruiter or talent acquisition professional
6. Recruiter's professional role
7. Public professional recruiting email
8. Public business recruiting phone number

IMPORTANT:

Only use publicly available professional information.

Do NOT guess or infer:
- private phone numbers
- personal email addresses
- private contact information

Prefer:
- official company website
- official careers page
- official company contact page
- publicly listed professional recruiting information

If information cannot be verified publicly, return null.
"""

    try:

        response = requests.post(
            "https://api.tavily.com/search",
            headers={
                "Content-Type": "application/json"
            },
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "advanced",
                "max_results": 5,
                "include_answer": True
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        sources = data.get(
            "results",
            []
        )

        # Combine Tavily research text
        research_text = ""

        for result in sources:

            research_text += (
                "\n"
                + result.get("title", "")
                + "\n"
                + result.get("content", "")
                + "\n"
                + result.get("url", "")
                + "\n"
            )

        return {
            "research_text": research_text[:15000],
            "sources": [
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "content": r.get("content")
                }
                for r in sources
            ]
        }

    except Exception as e:

        return {
            "error": str(e),
            "research_text": "",
            "sources": []
        }


# =========================================================
# EXTRACT SIMPLE CONTACT INFORMATION
# =========================================================

def extract_contacts(text):

    emails = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    phones = re.findall(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text
    )

    return {
        "emails": list(dict.fromkeys(emails)),
        "phones": list(dict.fromkeys(phones))
    }


# =========================================================
# RESEARCH ONE JOB
# =========================================================

def research_job(job):

    # ---------------------------------
    # 1. Scrape actual job page
    # ---------------------------------

    scraped = scrape_job_page(job)

    if scraped.get("status") != "success":
        return scraped

    # ---------------------------------
    # 2. Public company/HR research
    # ---------------------------------

    company_research = research_company(
        scraped
    )

    research_text = company_research.get(
        "research_text",
        ""
    )

    contacts = extract_contacts(
        research_text
    )

    # ---------------------------------
    # 3. Company fallback
    # ---------------------------------

    company = scraped.get("company")

    if not company:

        # Try to get company from job title / research
        for result in company_research.get(
            "sources",
            []
        ):

            title = result.get(
                "title",
                ""
            )

            content = result.get(
                "content",
                ""
            )

            combined = (
                title + " " + content
            )

            # Basic company extraction
            match = re.search(
                r"(?:company|employer)\s*[:\-]\s*([A-Za-z0-9& .'-]{2,80})",
                combined,
                re.IGNORECASE
            )

            if match:

                company = match.group(
                    1
                ).strip()

                break

    if not company:
        company = "Company not identified"


    # ---------------------------------
    # 4. Recruiter information
    # ---------------------------------

    recruiter = {
        "name": None,
        "role": None,
        "email": (
            contacts["emails"][0]
            if contacts["emails"]
            else None
        ),
        "phone": (
            contacts["phones"][0]
            if contacts["phones"]
            else None
        )
    }


    # ---------------------------------
    # 5. FINAL RESULT
    # ---------------------------------

    return {

        "job_title": scraped.get(
            "job_title"
        ),

        "title": scraped.get(
            "job_title"
        ),

        "company": company,

        "location": job.get(
            "location",
            "Not listed"
        ),

        "job_url": scraped.get(
            "job_url"
        ),

        "official_apply_link": (
            scraped.get(
                "official_apply_link"
            )
        ),

        "description": (
            scraped.get(
                "job_description"
            )
        ),

        "job_description": (
            scraped.get(
                "job_description"
            )
        ),

        "recruiter": recruiter,

        "company_research": (
            company_research
        )
    }


# =========================================================
# RESEARCH ALL JOBS
# =========================================================

def research_jobs(jobs):

    results = []

    for job in jobs:

        result = research_job(
            job
        )

        results.append(
            result
        )

    return results