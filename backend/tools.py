import os
import requests
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool("Search Jobs API")
def search_jobs(query: str) -> str:
    """Searches for jobs using the JSearch API. Input should be a search query like 'Software Engineer Intern New York'."""
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": os.getenv("JSEARCH_API_KEY"),
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    # We ask for 11 jobs to ensure we get at least 5-10 good ones after filtering
    params = {"query": query, "page": "1", "num_pages": "1"} 
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        jobs = data.get('data', [])
        
        formatted_jobs = []
        for job in jobs[:11]:
            formatted_jobs.append({
                "title": job.get('job_title'),
                "company": job.get('employer_name'),
                "location": job.get('job_city', '') + ", " + job.get('job_state', ''),
                "link": job.get('job_google_link') or job.get('job_apply_link'),
                "description": job.get('job_description', '')[:500] # Truncate to save tokens
            })
        return str(formatted_jobs)
    except Exception as e:
        return f"Error searching jobs: {str(e)}"

@tool("Search HR Contact Info")
def search_hr_contact(company_name: str) -> str:
    """Searches the web to find the HR contact, recruiter, or hiring manager LinkedIn profile and email for a specific company."""
    url = "https://google.serper.dev/search"
    payload = {
        "q": f"{company_name} HR contact OR recruiter OR hiring manager LinkedIn email",
        "num": 5
    }
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        results = response.json().get('organic', [])
        
        contacts = []
        for res in results:
            contacts.append({
                "title": res.get('title'),
                "link": res.get('link'),
                "snippet": res.get('snippet')
            })
        return str(contacts)
    except Exception as e:
        return f"Error searching contacts: {str(e)}"