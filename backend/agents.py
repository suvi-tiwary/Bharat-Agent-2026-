# tasks.py
from crewai import Task
from agents import resume_agent, job_hunter_agent, contact_agent, strategist_agent

analyze_resume_task = Task(
    description="Analyze the following resume text and extract: 1. Top 5 hard skills. 2. Experience level (Intern, Junior, Mid). 3. Target job titles. Resume: {resume_text}",
    expected_output="A structured summary of skills, experience level, and target roles.",
    agent=resume_agent
)

find_jobs_task = Task(
    description="Based on the resume analysis, use the Search Jobs API to find the top 5 to 11 matching jobs or internships. Ensure you get official application links.",
    expected_output="A list of 5 to 11 jobs with Title, Company, Location, Official Link, and a brief description.",
    agent=job_hunter_agent,
    context=[analyze_resume_task]
)

find_contacts_task = Task(
    description="For each company in the job list, use the Search HR Contact Info tool to find a specific HR person, recruiter, or hiring manager. Get their LinkedIn URL or email if possible.",
    expected_output="A list of HR/Recruiter contacts mapped to their respective companies.",
    agent=contact_agent,
    context=[find_jobs_task]
)

strategy_task = Task(
    description="""
    Compile the final report. For each of the 5-11 jobs:
    1. Provide the Job Details and Official Link.
    2. Provide the HR Contact/LinkedIn found.
    3. RESUME GAP ANALYSIS: Tell the user what skills they have that match, and what 1-2 skills they are missing for THIS specific job.
    4. OUTREACH TEMPLATE: Write a short, personalized cold-email or LinkedIn connection request to the HR contact found, mentioning the specific job and the candidate's matching skills.
    """,
    expected_output="A beautifully formatted markdown report containing the jobs, links, HR contacts, gap analysis, and outreach templates.",
    agent=strategist_agent,
    context=[find_jobs_task, find_contacts_task]
)