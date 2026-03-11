import asyncio
from app.agents.executor import run_agent_workflow


async def main():
    print("🚀 Starting Agent Workflow Test...")

    test_strategy = {
        "name": "Python Developer",
        "target_job_titles": ["Python Backend Developer"],
        "min_salary": 100000,
        "max_salary": 150000,
        "job_types": ["Full-time"],
    }

    test_profile = {
        "skills": ["Python", "FastAPI", "SQLAlchemy", "Docker", "AWS"],
        "experience_years": 5,
    }

    try:
        result = await run_agent_workflow(test_strategy, test_profile)
        print(f"✅ Workflow completed with result: {result}")
    except Exception as e:
        print(f"❌ Workflow failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
