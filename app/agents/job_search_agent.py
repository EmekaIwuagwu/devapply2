from crewai import Agent
from app.agents.config import get_llm
from app.agents.tools.search_tools import search_linkedin, search_indeed


def create_job_search_agent():
    llm = get_llm(fast=True)

    return Agent(
        role="Job Search Specialist",
        goal="Find high-quality job opportunities matching user criteria across multiple platforms.",
        backstory="""You are an expert recruitment researcher. You know exactly where to look for 
        the best roles and how to filter out irrelevant or low-quality postings. 
        You specialize in tech roles but can adapt to any industry based on the user's strategy.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
