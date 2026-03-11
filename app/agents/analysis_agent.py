from crewai import Agent
from app.agents.config import get_llm


def create_analysis_agent():
    llm = get_llm()

    return Agent(
        role="Job Match Analyst",
        goal="Analyse job descriptions and determine the perfect fit with user skills and strategy.",
        backstory="""You are a senior technical recruiter who has reviewed thousands of resumes. 
        You have a keen eye for detail and can spot hidden requirements in job descriptions. 
        You are fair but rigorous in assessing match quality to ensure the user only applies to jobs 
        where they have a high chance of success.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
