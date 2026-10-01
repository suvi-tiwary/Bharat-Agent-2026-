from crewai import Task


def create_tasks(agents, preferred_location: str, response_language: str = "English"):
    resume_agent, job_hunter_agent, contact_agent, learning_agent, strategist_agent = agents

    analyze_resume = Task(
        description=(
            "Analyze this resume. Extract up to 8 explicit skills, experience level, "
            "and up to 5 realistic target job titles. Identify evidence from projects, "
            "education, volunteering, and informal experience too. Do not infer unsupported facts. "
            "Return only JSON with keys: top_skills (array), experience_level (string), "
            "target_roles (array). Resume: {resume_text}"
        ),
        expected_output="Valid JSON containing top_skills, experience_level, and target_roles.",
        agent=resume_agent,
    )

    find_jobs = Task(
        description=(
            "Use the resume analysis and Search Jobs tool to find up to 6 suitable open "
            "roles in India. Preferred location or role: {preferred_location}. Search with the "
            "candidate's target titles and this preference. Return only JSON with a "
            "jobs array; each item must contain title, company, location, link, and "
            "description. Keep source links from search results and never invent listings."
        ),
        expected_output="Valid JSON with a jobs array of sourced job listings.",
        agent=job_hunter_agent,
        context=[analyze_resume],
    )

    find_contacts = Task(
        description=(
            "For the employers in the job results, use Search Recruiter Contacts to find "
            "public recruiter or hiring-team pages. Return only JSON with a contacts "
            "array; each item must contain company, name_or_page, url, and source_summary. "
            "Never present a search result as a verified individual email address."
        ),
        expected_output="Valid JSON with a contacts array and public source links.",
        agent=contact_agent,
        context=[find_jobs],
    )

    find_learning = Task(
        description=(
            "Compare the resume analysis with the job listings. Identify up to 3 high-value "
            "skills the candidate can build next. Use Search Learning Resources to find "
            "free or low-cost resources from credible providers. Return only JSON with a "
            "learning_plan array; each item must contain skill, why_it_matters, "
            "resource_title, resource_url, and a practical first_step. Never invent a URL."
        ),
        expected_output="Valid JSON with up to 3 skill-building steps and source URLs.",
        agent=learning_agent,
        context=[analyze_resume, find_jobs],
    )

    create_strategy = Task(
        description=(
            "Create the final Bharat-focused career launch plan from the resume analysis, "
            "sourced jobs, contact research, and learning research. Write user-facing text "
            "in {response_language}, but keep JSON keys, URLs, and proper nouns unchanged. "
            "Return only valid JSON with keys candidate_summary (experience_level, "
            "top_skills, target_roles) and opportunities (array), plus learning_plan "
            "(array) and impact (object with ready_to_apply_count and verified_source_count). "
            "Each opportunity must contain title, company, location, application_url, "
            "description, matched_skills (array), missing_skills (array), contact "
            "(name_or_page, url), and outreach (subject, email, linkedin_message). "
            "Each learning step must contain skill, why_it_matters, resource_title, "
            "resource_url, and first_step. Count only roles with a real source link as "
            "ready_to_apply_count; count only distinct URLs in supplied search results "
            "as verified_source_count. Use only supplied evidence; unknowns must be "
            "empty strings or arrays. Tailor concise outreach to matching skills."
        ),
        expected_output=(
            "Valid JSON with candidate summary, sourced opportunities, learning plan, "
            "and source-count impact measures."
        ),
        agent=strategist_agent,
        context=[analyze_resume, find_jobs, find_contacts, find_learning],
    )

    return [analyze_resume, find_jobs, find_contacts, find_learning, create_strategy]