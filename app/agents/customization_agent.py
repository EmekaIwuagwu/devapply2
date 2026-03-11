from crewai import Agent
from app.agents.config import get_llm


def create_customization_agent():
    llm = get_llm()

    return Agent(
        role="Resume Optimization Specialist",
        goal="Tailor the user's resume for specific job applications to maximize ATS compatibility and human appeal.",
        backstory="""You are a professional resume writer and ATS (Applicant Tracking System) expert. 
        You know exactly how to rephrase experience and highlight skills to pass automated filters 
        while still reading naturally and impressively to human recruiters.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
