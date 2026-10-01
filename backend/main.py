from crewai import Crew, Process
from agents import resume_agent, job_hunter_agent, contact_agent, strategist_agent
from tasks import analyze_resume_task, find_jobs_task, find_contacts_task, strategy_task

def run_crew(resume_text):
    crew = Crew(
        agents=[resume_agent, job_hunter_agent, contact_agent, strategist_agent],
        tasks=[analyze_resume_task, find_jobs_task, find_contacts_task, strategy_task],
        process=Process.sequential,
        verbose=True
    )
    
    inputs = {"resume_text": resume_text}
    result = crew.kickoff(inputs=inputs)
    return result.raw