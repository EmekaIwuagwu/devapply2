import subprocess
import time
import sys
import os

def start_services():
    print("🚀 Starting DevApply Full Stack...")
    
    # Set PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    # 1. Start FastAPI Backend
    print("Starting Backend...")
    # Run uvicorn as a module: python -m uvicorn
    backend_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"], env=env)
    
    # Get the directory of the current python executable (venv/Scripts)
    scripts_dir = os.path.dirname(sys.executable)
    celery_exe = os.path.join(scripts_dir, "celery.exe")
    streamlit_exe = os.path.join(scripts_dir, "streamlit.exe")

    # 2. Start Celery Worker (Requires Redis)
    print("Starting Celery Worker...")
    # Note: On Windows, use 'solo' pool
    celery_proc = subprocess.Popen([celery_exe, "-A", "app.tasks.celery_tasks", "worker", "--loglevel=info", "-P", "solo"], env=env)
    
    # 3. Start Streamlit Frontend
    print("Starting Streamlit...")
    frontend_proc = subprocess.Popen([streamlit_exe, "run", "app/frontend/main.py"], env=env)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        backend_proc.terminate()
        celery_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    start_services()
