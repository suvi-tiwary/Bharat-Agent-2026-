from crewai import Crew, Process

from agents import create_agents
from tasks import create_tasks


def run_crew(
    resume_text: str,
    preferred_location: str = "India / remote",
    response_language: str = "English",
) -> dict[str, str]:
    agents = create_agents()
    tasks = create_tasks(agents, preferred_location, response_language)
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff(
        inputs={
            "resume_text": resume_text,
            "preferred_location": preferred_location or "India / remote",
            "response_language": response_language,
        }
    )
    outputs = [str(output.raw) for output in result.tasks_output]
    outputs += [""] * (5 - len(outputs))
    return {
        "analysis": outputs[0],
        "job_search": outputs[1],
        "contacts": outputs[2],
        "learning": outputs[3],
        "report": outputs[4],
    }