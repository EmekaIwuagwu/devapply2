# DevApply: Autonomous AI Job Application Agent
## Complete Specification & Development Prompt for IDX (Project Antigravity)

---

## 📋 Executive Summary

**Project Name:** DevApply  
**Purpose:** An intelligent, autonomous AI agent solution that automates job applications across multiple platforms (LinkedIn, Indeed, Google Jobs) based on user-defined strategies, skills, and preferences.  
**Architecture:** Full-stack Python application (Pure Python - No JavaScript/React)  
**Frontend:** Streamlit (Python-based UI framework)  
**Backend:** FastAPI (Python)  
**AI Models:** Free & Self-Hosted (Ollama, Hugging Face, LLaMA 2, Mistral)  
**Scope:** Web application with browser automation, computer vision, LLM reasoning, and human behavior simulation  
**Target Users:** Job seekers who want to automate their application process while maintaining control over strategy and preferences  

---

## 🎯 Project Objectives

1. **Automate Job Application Process** - Submit applications at scale across job platforms without manual intervention
2. **Intelligent Job Matching** - Use LLM to analyze job descriptions and match against user skills/preferences
3. **Evade Bot Detection** - Simulate human behavior to bypass CAPTCHA and bot-detection systems
4. **Resume Customization** - Dynamically tailor resumes based on job requirements
5. **User Control & Transparency** - Dashboard showing application history, success rates, and strategy effectiveness
6. **Secure Authentication** - User registration, login, and profile management with encryption
7. **Data Persistence** - Track applications, responses, resumes, and strategy performance

---

## 🏗️ System Architecture

### High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│             Frontend Layer (Streamlit + Python)               │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐ │
│  │    Login     │   Dashboard  │   Strategy   │   Profile  │ │
│  │ & Register   │   & Analytics│   Config     │  Management│ │
│  └──────────────┴──────────────┴──────────────┴────────────┘ │
│       Pure Python Streamlit App (Single Executable)          │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    Backend API Layer (FastAPI)                │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐ │
│  │  Auth Svc    │   User Mgmt  │  Strategy    │  Analytics │ │
│  │ JWT Tokens   │  CRUD Ops    │   Scheduler  │  Service   │ │
│  └──────────────┴──────────────┴──────────────┴────────────┘ │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                   AI Agent Orchestration Layer                │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐ │
│  │   CrewAI     │  LangChain   │  Job Search  │ Application│ │
│  │  Agents      │  Chains      │  Analysis    │  Agent     │ │
│  └──────────────┴──────────────┴──────────────┴────────────┘ │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│              Browser Automation & Vision Layer                │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐ │
│  │  Playwright  │   OpenCV     │   Tesseract  │   DOM      │ │
│  │  Bot Control │   Vision     │   OCR        │  Parsing   │ │
│  │              │              │              │ Beautiful  │ │
│  │              │              │              │   Soup     │ │
│  └──────────────┴──────────────┴──────────────┴────────────┘ │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                         │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐ │
│  │  PostgreSQL  │  Redis Cache │  File Storage│  Resume    │ │
│  │  (Primary DB)│  (Sessions)  │  (Resumes)   │  Versioning│ │
│  └──────────────┴──────────────┴──────────────┴────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 👥 Feature Specifications

### A. FRONTEND - User-Facing Interface (Streamlit + Python)

**Frontend Architecture Overview:**
- Pure Python application using Streamlit
- Rendered as interactive web application
- Direct communication with FastAPI backend
- Session management with JWT tokens
- File uploads handled via Streamlit widgets
- Real-time updates with st.experimental_fragment and callbacks

#### 1. **Authentication & User Management**

**Login Page (auth.py)**
```python
# Streamlit page with:
- Email/password input fields
- "Remember me" session persistence
- Password reset link (redirects to reset form)
- Social login integration (optional)
- Error message display
- Login success redirect to dashboard
```

**Registration Page**
```python
# Streamlit form with:
- Email input (validated)
- Password strength requirements
- Password confirmation
- Terms of service checkbox
- Email verification flow
- Auto-redirect to login on success
```

**Profile Management Page**
```python
# User settings dashboard with:
- Personal information editor (name, email, phone)
- Password change form with current password verification
- Account deletion with confirmation dialog
- API key generation for integrations
- Profile photo upload
```

#### 2. **Dashboard**

**Overview Section (dashboard.py)**
```python
# Main dashboard with Streamlit columns/metrics:
- st.metric() for:
  * Total applications sent (counter)
  * Success rate percentage
  * Applications sent this week
  * Average response time
- st.selectbox() for date range filters
- st.columns() for responsive layout
```

**Recent Applications Table**
```python
# Interactive data table with:
- st.dataframe() for application list (sortable, filterable)
- Columns: Job title, Company, Platform, Date Applied, Status
- st.button() for each row to view details in modal
- Status badges with color coding
- Sort by date, company, status
```

**Analytics Dashboard (matplotlib/plotly)**
```python
# Charts using plotly in Streamlit:
- Line chart: Applications over time (st.plotly_chart)
- Pie chart: Success rate by job category
- Bar chart: Most successful strategies
- Heatmap: Best application times
- Refresh button to reload metrics
```

#### 3. **Strategy & Skill Configuration**

**Skill Management (skills_config.py)**
```python
# Streamlit multiselect and sliders for:
- st.multiselect() for adding skills
- st.columns() with st.select_slider() for proficiency levels
- st.button() to add/remove skills
- Display skills as pills with st.metric() style
- Skill suggestions based on job titles
```

**Strategy Configuration**
```python
# Form with:
- st.text_input() for strategy name
- st.multiselect() for target job titles (searchable)
- st.slider() for salary range (min/max)
- st.checkbox() for job types (Full-time, Contract, etc)
- st.radio() for location preferences
- st.selectbox() for company size preferences
- st.multiselect() for industries
- st.button() to save/update strategy
```

**Bio & Summary**
```python
# Text editor section with:
- st.text_area() for professional bio (with char counter)
- st.text_input() for LinkedIn URL
- st.text_input() for GitHub URL
- st.text_input() for portfolio URL
- AI-powered suggestions (from LLM) for improvements
- st.button() to apply LLM suggestions
```

**Resume Management**
```python
# Resume upload & management with:
- st.file_uploader() for PDF/DOCX files
- Drag-and-drop support
- File size validation
- Resume preview (PDF display)
- st.button() to set as primary resume
- Version history (st.expander() for older versions)
- Auto-extract skills from resume
```

#### 4. **Job Application Monitor**

**Active Applications List (applications.py)**
```python
# Interactive table with:
- st.dataframe() with filterable columns
- Filter by status, platform, date range
- st.text_input() for search by company/job title
- Bulk actions via st.multiselect()
- Export to CSV button (st.download_button)
- Sorting capabilities
```

**Application Details Modal**
```python
# Modal-style expander with:
- st.expander() for full job description
- Application timestamp, current status
- Customizations applied
- AI analysis summary from agent
- Manual status update buttons
```

#### 5. **Agent Control & Monitoring (automation.py)**

**Agent Dashboard**
```python
# Real-time agent monitoring with:
- st.button() to start/stop automation
- st.selectbox() to choose strategy to run
- Live log display (st.write() streaming)
- Progress bar (st.progress())
- Status indicators (green/red dots)
- Execution history table
- Manual run button (run once)
```

**Settings & Configuration**
```python
# Agent settings with:
- st.number_input() for max applications per run
- st.slider() for delay between submissions
- st.checkbox() for stealth mode
- st.selectbox() for browser type
- st.checkbox() to enable/disable CAPTCHA solving
- st.button() to save agent config
```

---

### B. BACKEND - API & Core Logic

#### 1. **User Service (FastAPI)**

```
POST   /api/auth/register       - User registration
POST   /api/auth/login          - User login (JWT)
POST   /api/auth/refresh        - Refresh token
POST   /api/auth/logout         - Logout
POST   /api/auth/forgot-password- Password reset
GET    /api/users/{user_id}     - Get user profile
PUT    /api/users/{user_id}     - Update user profile
DELETE /api/users/{user_id}     - Delete account
```

#### 2. **Strategy Service**

```
POST   /api/strategies          - Create new strategy
GET    /api/strategies          - List user strategies
GET    /api/strategies/{id}     - Get strategy details
PUT    /api/strategies/{id}     - Update strategy
DELETE /api/strategies/{id}     - Delete strategy
POST   /api/strategies/{id}/activate - Activate strategy
```

#### 3. **Application Service**

```
POST   /api/applications        - Log manual application
GET    /api/applications        - List user applications
GET    /api/applications/{id}   - Get application details
PUT    /api/applications/{id}   - Update application status
DELETE /api/applications/{id}   - Delete application
GET    /api/applications/stats  - Get application statistics
POST   /api/applications/export - Export applications (CSV)
```

#### 4. **Resume Service**

```
POST   /api/resumes             - Upload resume
GET    /api/resumes             - List user resumes
DELETE /api/resumes/{id}        - Delete resume
POST   /api/resumes/{id}/customize - Generate customized resume
GET    /api/resumes/{id}/versions - Get resume versions
```

#### 5. **Agent Service (Scheduler)**

```
POST   /api/agent/start         - Start automation agent
POST   /api/agent/stop          - Stop automation agent
GET    /api/agent/status        - Get agent status
POST   /api/agent/run-once      - Execute single agent run
GET    /api/agent/logs          - Fetch agent execution logs
POST   /api/agent/config        - Configure agent parameters
```

---

### C. BACKEND - AI Agent Architecture

#### **Agent 1: Job Search Agent**
**Responsibility:** Find job postings matching user criteria

- **Tools:**
  - `search_jobs(keyword, location, filters)` - Query job APIs
  - `scrape_job_listing(url)` - Extract job details
  - `validate_job_match(job, user_skills)` - Check relevance
  
- **Workflow:**
  1. Retrieve user strategy & preferences
  2. Search across platforms (LinkedIn, Indeed, Google Jobs)
  3. Filter results based on criteria
  4. Deduplicate jobs
  5. Return matching job candidates

#### **Agent 2: Job Analysis Agent**
**Responsibility:** Analyze job descriptions and user fit

- **Tools:**
  - `extract_requirements(job_description)` - Parse skills needed
  - `match_skills(required_skills, user_skills)` - Calculate fit %
  - `analyze_seniority(job_description)` - Detect level
  - `extract_salary_range(job_description)` - Parse compensation
  - `llm_decision(job_text, user_profile)` - LLM-based decision
  
- **Workflow:**
  1. Receive job from Job Search Agent
  2. Extract required skills, experience, seniority
  3. Compare against user skills & strategy
  4. Calculate match percentage
  5. Use LLM to make final recommendation
  6. Return: APPLY / SKIP with reasoning

#### **Agent 3: Resume Customization Agent**
**Responsibility:** Tailor resume for specific job

- **Tools:**
  - `load_resume(resume_id)` - Load base resume
  - `extract_keywords(job_description)` - Get ATS keywords
  - `customize_resume(resume, keywords, job_role)` - Modify resume
  - `save_version(resume, job_id)` - Store customized version
  
- **Workflow:**
  1. Receive approved job
  2. Load user's primary resume
  3. Extract key requirements from job description
  4. Reorder resume sections for ATS optimization
  5. Highlight matching skills
  6. Save customized version with version tracking

#### **Agent 4: Application Agent**
**Responsibility:** Automate form filling and submission

- **Tools:**
  - `open_job_page(url)` - Launch Playwright browser
  - `detect_captcha()` - Identify CAPTCHA presence
  - `screenshot_page()` - Visual inspection
  - `parse_html_form()` - Extract form fields
  - `fill_form(form_data)` - Populate fields
  - `handle_captcha_solving()` - CAPTCHA bypass
  - `submit_application()` - Submit form
  - `log_application(job, success_status)` - Record result
  
- **Workflow:**
  1. Receive job URL and customized resume
  2. Open browser with human behavior simulation
  3. Navigate to application page
  4. Take screenshot & analyze UI
  5. Detect form fields (OCR + DOM parsing)
  6. Fill form with user information
  7. Handle CAPTCHA if present
  8. Submit application
  9. Verify submission success
  10. Log application with metadata

---

## 🛠️ Technology Stack

### **Frontend (Pure Python)**
- **Framework:** Streamlit (Python UI framework)
- **Charting:** Plotly, Matplotlib, Altair (for interactive charts)
- **Data Display:** Pandas DataFrame integration
- **File Handling:** Streamlit built-in file uploader
- **Session Management:** Streamlit session state + JWT tokens
- **HTTP Client:** Requests library for API calls
- **Caching:** Streamlit cache decorators (@st.cache_data, @st.cache_resource)

### **Backend**
- **Framework:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL 14+ (Primary)
- **Cache:** Redis (Sessions, rate limiting, caching)
- **ORM:** SQLAlchemy 2.0+ with Alembic
- **Task Queue:** Celery + Redis (background jobs)
- **API Documentation:** FastAPI built-in Swagger
- **Authentication:** PyJWT + bcrypt
- **Validation:** Pydantic v2
- **Server:** Uvicorn (ASGI server)

### **Browser Automation & Vision**
- **Browser Control:** Playwright (Python)
- **Computer Vision:** OpenCV
- **OCR:** Tesseract + pytesseract
- **HTML Parsing:** BeautifulSoup4 + lxml
- **Image Processing:** Pillow, NumPy
- **Screenshot Processing:** Selenium-like capabilities via Playwright

### **AI & LLM (FREE & SELF-HOSTED)**

#### **Option 1: Ollama (Recommended - Fully Local & Free)**
- **Ollama Framework:** Local LLM runtime
- **Models Available:**
  - **Llama 2** (7B, 13B, 70B) - Best for general reasoning
  - **Mistral 7B** - Smaller, faster alternative
  - **Neural-chat** - Optimized for conversations
  - **Code-Llama** - Better for code analysis
- **Use Cases:**
  - Job description analysis
  - Skill matching
  - Resume customization suggestions
  - Application decision making
  
**Installation:**
```bash
# Download Ollama from ollama.ai
ollama pull llama2           # ~4GB download
ollama pull mistral          # ~5GB download
# Models run locally on CPU/GPU (no API costs)
```

#### **Option 2: Hugging Face Transformers (Free, Self-Hosted)**
- **Libraries:**
  - Transformers (for LLM inference)
  - SentenceTransformers (for embeddings)
  - FARM (for advanced NLP)
  
- **Free Models:**
  - `mistralai/Mistral-7B-Instruct-v0.1` - Lightweight reasoning
  - `meta-llama/Llama-2-7b-chat` - General purpose
  - `tiiuae/falcon-7b-instruct` - Fast inference
  - `google/flan-t5-large` - Task-specific
  
**Installation:**
```bash
pip install transformers torch
# Download models (~3-7GB each)
from transformers import AutoTokenizer, AutoModelForCausalLM
```

#### **Option 3: Hybrid Approach (Recommended)**
```python
# Use local Ollama for main reasoning tasks
# Use HuggingFace for specialized tasks (OCR, embeddings)
# Fall back to free Google Gemini API if needed (limited free tier)

# Primary LLM: Ollama Llama 2 (local, no cost)
# OCR Text Extraction: Pytesseract + Transformers
# Embeddings: Sentence-Transformers (local)
# Vision Analysis: YOLO or HuggingFace Vision models (free)
```

#### **Optional: Free Cloud LLM APIs (Limited Usage)**
- **Google Gemini API** - 60 requests/minute free tier
- **Anthropic Claude API** - Limited free credits (but model quality is excellent)
- **LLaMA 2 via Replicate** - Free tier available (limited calls)

**Recommendation for DevApply:**
```
Primary: Ollama (Llama 2 7B) - Main agent reasoning
Secondary: HuggingFace Transformers - Vision/embeddings
Backup: Google Gemini (free tier) - If local models overwhelmed
```

### **Agent Framework (FREE)**
- **Agent Framework:** CrewAI (100% open-source)
- **LLM Integration:** LangChain (free, open-source)
- **Memory Management:** Custom implementation + Redis

### **Bot Detection Evasion (FREE)**
- **User Agent Rotation:** fake-useragent
- **Mouse Behavior:** PyAutoGUI + custom delay simulation
- **Request Headers:** Custom headers library
- **Browser Stealth:** Playwright stealth plugin

### **Resume Processing**
- **DOCX Handling:** python-docx (free, open-source)
- **PDF Handling:** pdfplumber / PyPDF2 (free)
- **PDF Generation:** ReportLab / WeasyPrint (free)

### **Infrastructure & DevOps (All FREE)**
- **Containerization:** Docker + Docker Compose (free)
- **Process Manager:** Supervisor / systemd
- **Logging:** Python logging + optional ELK stack
- **Monitoring:** Prometheus + Grafana (free, open-source)
- **CI/CD:** GitHub Actions (free for public repos)
- **Hosting Options:**
  - Self-hosted (own hardware)
  - VPS (DigitalOcean, Linode - cheapest option)
  - Docker-based cloud (AWS ECS free tier)

### **Optional Machine Learning (FREE)**
- **PyTorch:** CPU-based inference
- **Transformers:** Vision models for UI detection
- **YOLO:** Object detection for buttons/elements
- **ONNX Runtime:** Optimized model inference

---

## 📊 Database Schema

### **Core Tables**

#### Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    profile_bio TEXT,
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE
);
```

#### Strategies
```sql
CREATE TABLE strategies (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    target_job_titles TEXT[], -- array of job titles
    min_salary INTEGER,
    max_salary INTEGER,
    job_types VARCHAR(50)[], -- ['Full-time', 'Contract', etc]
    location_preference VARCHAR(50)[], -- ['Remote', 'On-site', 'Hybrid']
    company_sizes VARCHAR(50)[], -- ['Startup', 'Enterprise']
    target_industries TEXT[],
    required_skills TEXT[],
    years_experience_required INTEGER,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Resumes
```sql
CREATE TABLE resumes (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(10), -- 'PDF', 'DOCX'
    detected_skills TEXT[],
    is_primary BOOLEAN DEFAULT FALSE,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version_of UUID REFERENCES resumes(id) -- for version tracking
);
```

#### Applications
```sql
CREATE TABLE applications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    strategy_id UUID NOT NULL REFERENCES strategies(id),
    job_title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    platform VARCHAR(50), -- 'LinkedIn', 'Indeed', 'Google Jobs'
    job_url VARCHAR(500) NOT NULL,
    job_description TEXT,
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customized_resume_id UUID REFERENCES resumes(id),
    status VARCHAR(50), -- 'Pending', 'Rejected', 'Interview', 'Accepted'
    match_score INTEGER, -- 0-100
    ai_recommendation TEXT,
    submission_success BOOLEAN,
    error_message TEXT,
    response_received BOOLEAN DEFAULT FALSE,
    response_date TIMESTAMP,
    user_outcome VARCHAR(50) -- manual outcome logging
);
```

#### Agent Executions (Logs)
```sql
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    strategy_id UUID REFERENCES strategies(id),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50), -- 'Running', 'Completed', 'Failed'
    jobs_found INTEGER,
    jobs_applied INTEGER,
    errors TEXT[],
    execution_logs TEXT
);
```

---

## 🤖 AI Agent Implementation Details

### **CrewAI Agent Configuration**

```python
# Agent 1: Job Search Agent
job_search_agent = Agent(
    role="Job Search Specialist",
    goal="Find job opportunities matching user criteria across multiple platforms",
    backstory="Expert in searching and filtering job listings from LinkedIn, Indeed, and Google Jobs",
    tools=[search_jobs_tool, scrape_job_tool],
    verbose=True,
    allow_delegation=False
)

# Agent 2: Job Analysis Agent
job_analysis_agent = Agent(
    role="Job Match Analyst",
    goal="Analyze job descriptions and determine fit with user skills and strategy",
    backstory="Expert recruiter who can assess skill matches and job suitability",
    tools=[extract_requirements_tool, match_skills_tool, llm_analysis_tool],
    verbose=True,
    allow_delegation=False
)

# Agent 3: Resume Customizer
resume_agent = Agent(
    role="Resume Optimization Specialist",
    goal="Customize resumes for specific job applications to maximize ATS compatibility",
    backstory="Expert in ATS optimization and tailoring resumes for specific roles",
    tools=[load_resume_tool, customize_resume_tool, save_resume_version_tool],
    verbose=True,
    allow_delegation=False
)

# Agent 4: Application Agent
application_agent = Agent(
    role="Application Automation Specialist",
    goal="Automate the job application submission process across platforms",
    backstory="Expert browser automation engineer skilled in form filling and bot detection evasion",
    tools=[playwright_tool, captcha_handler_tool, form_parser_tool, application_logger_tool],
    verbose=True,
    allow_delegation=False
)
```

### **Task Definitions**

```python
# Define tasks for agent collaboration
task_1 = Task(
    description="Search for jobs matching: {user_strategy}",
    agent=job_search_agent,
    expected_output="List of 10-20 relevant job opportunities with URLs"
)

task_2 = Task(
    description="Analyze each job and determine if user should apply based on: {user_skills}, {user_preferences}",
    agent=job_analysis_agent,
    expected_output="Filtered list of top 5-8 jobs with match scores and recommendations"
)

task_3 = Task(
    description="Customize resume for each approved job",
    agent=resume_agent,
    expected_output="Customized resume documents for each approved job"
)

task_4 = Task(
    description="Submit applications for approved jobs",
    agent=application_agent,
    expected_output="Application submission confirmations and logs"
)

# Create crew
crew = Crew(
    agents=[job_search_agent, job_analysis_agent, resume_agent, application_agent],
    tasks=[task_1, task_2, task_3, task_4],
    verbose=True,
    process=Process.sequential
)
```

---

## 🎭 Human Behavior Simulation

### **Anti-Bot Detection Techniques**

#### 1. **Mouse Movement Simulation**
```python
# Randomized mouse movement with Bezier curves
def simulate_human_mouse_movement(page, start_x, start_y, end_x, end_y):
    """Simulate natural human-like mouse movement"""
    # Use Bezier curves for smooth, non-linear paths
    # Random speed variations
    # Occasional pauses
```

#### 2. **Typing Behavior**
```python
# Type with variable speed, random mistakes, backspaces
def human_like_typing(page, text):
    """Type like a human with natural speed variations"""
    # Variable typing speed (50-150 WPM)
    # Occasional typos and corrections
    # Random pauses between words
```

#### 3. **Request Header Randomization**
```python
# Rotate user agents
# Custom headers (Referer, Accept-Language, etc.)
# Session cookies management
# Random request delays (2-8 seconds)
```

#### 4. **CAPTCHA Handling Strategy**
```python
# Google reCAPTCHA v2/v3 evasion:
#   - Use 2Captcha or similar service for fallback
#   - Simulate user interaction patterns
#   - Maintain request metadata
# Note: Never violate ToS; use where permitted
```

---

## 🔐 Security Considerations

### **Authentication & Authorization**
- JWT tokens with 1-hour expiry + refresh tokens (7 days)
- Password hashing using bcrypt (12+ rounds)
- Email verification before account activation
- Rate limiting on login attempts (5 attempts per 15 minutes)
- CORS configuration for frontend origin only

### **Data Protection**
- Encrypt sensitive data at rest (PII, resumes)
- HTTPS/TLS 1.3 for all communications
- Database backups with encryption
- Regular security audits

### **API Security**
- Request signing for critical operations
- API rate limiting per user/IP
- Input validation & sanitization (Pydantic)
- SQL injection protection (ORM)
- CSRF protection on state-changing operations

### **Browser Automation Security**
- Headless browser use with stealth mode
- IP rotation through proxy (optional)
- User agent rotation
- Respect robots.txt and ToS
- Logging all bot activities for audit

---

## 📈 Analytics & Reporting

### **Key Metrics Tracked**
- Total applications sent per user
- Success rate (responses / applications)
- Average time to response
- Most successful job titles/industries
- Strategy effectiveness metrics
- Skill match patterns
- Application volume trends

### **Dashboard Visualizations**
- Line charts: Applications over time
- Pie charts: Success by industry/platform
- Heatmaps: Best application times
- Funnel charts: Application → Interview → Offer
- Comparison charts: Strategy performance

---

## 🚀 Implementation Guidelines

### **Phase 1: Foundation (Weeks 1-2)**
- [ ] Set up project structure with FastAPI backend
- [ ] Set up Streamlit frontend structure
- [ ] Implement PostgreSQL schema with SQLAlchemy models
- [ ] Configure Redis for caching and sessions
- [ ] Implement JWT authentication in FastAPI
- [ ] Create Streamlit login/registration pages
- [ ] Set up environment variables and .env file

### **Phase 2: User Management & Dashboard (Weeks 3-4)**
- [ ] Complete CRUD operations for users
- [ ] Build dashboard with Streamlit metrics and charts
- [ ] Implement resume upload functionality (FastAPI endpoint + Streamlit widget)
- [ ] Create strategy configuration UI in Streamlit
- [ ] Implement skill management system
- [ ] Set up application tracking database
- [ ] Connect Streamlit frontend to FastAPI backend

### **Phase 3: AI Agent & LLM Integration (Weeks 5-6)**
- [ ] Set up Ollama with Llama 2 or Mistral locally
- [ ] Implement LangChain + CrewAI integration with Ollama
- [ ] Build Job Search Agent with web scraping
- [ ] Develop Job Analysis Agent using local LLM
- [ ] Create Resume Customization Agent
- [ ] Implement HuggingFace Transformers for OCR/embeddings
- [ ] Test all agents independently

### **Phase 4: Browser Automation & Application (Weeks 7-8)**
- [ ] Implement Application Agent with Playwright
- [ ] Set up human behavior simulation (mouse, typing, delays)
- [ ] Implement CAPTCHA detection (fallback handling)
- [ ] Set up job form detection and parsing (Beautiful Soup + OpenCV)
- [ ] Implement application submission logic
- [ ] Create logging and error tracking
- [ ] Build agent execution monitoring in Streamlit

### **Phase 5: Integration & Testing (Weeks 9-10)**
- [ ] Integrate all four agents into single workflow
- [ ] Set up Celery task queue for background jobs
- [ ] Implement scheduling (daily/weekly runs)
- [ ] Create analytics calculations
- [ ] Write comprehensive tests (unit, integration, E2E)
- [ ] Performance optimization
- [ ] Security audit

### **Phase 6: Deployment & Polish (Weeks 11-12)**
- [ ] Docker containerization of all services
- [ ] Docker Compose orchestration
- [ ] Set up monitoring with Prometheus/Grafana
- [ ] Logging centralization
- [ ] CI/CD pipeline with GitHub Actions
- [ ] User documentation
- [ ] Production deployment
- [ ] Load testing

---

## ⚙️ LLM Configuration for DevApply

### **Local Ollama Setup (Recommended - Zero Cost)**

```python
# config/llm_config.py
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Initialize Ollama locally (no API keys needed)
llm = Ollama(
    model="llama2",  # or "mistral" for faster inference
    base_url="http://localhost:11434",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

# Alternative: Use Mistral 7B for faster response
llm_fast = Ollama(
    model="mistral",
    base_url="http://localhost:11434"
)
```

### **Agent 1: Job Search Agent with Local LLM**

```python
# agents/job_search_agent.py
from crewai import Agent, Task, Crew, Process
from langchain.tools import tool
from langchain.llms import Ollama

# Initialize LLM
llm = Ollama(model="llama2", base_url="http://localhost:11434")

@tool
def search_jobs(keywords: str, location: str) -> str:
    """Search for jobs matching criteria"""
    # Implementation using BeautifulSoup + web scraping
    pass

@tool
def scrape_job_details(url: str) -> str:
    """Scrape detailed job information"""
    # Implementation using Playwright + Beautiful Soup
    pass

job_search_agent = Agent(
    role="Job Search Specialist",
    goal="Find job opportunities matching user criteria",
    backstory="Expert job researcher",
    tools=[search_jobs, scrape_job_details],
    llm=llm,
    verbose=True
)

job_search_task = Task(
    description="Search for Python/AI jobs in {location}",
    agent=job_search_agent,
    expected_output="List of relevant job opportunities with URLs"
)
```

### **Agent 2: Job Analysis Agent with Local LLM**

```python
# agents/job_analysis_agent.py
from crewai import Agent
from langchain.llms import Ollama

llm = Ollama(model="llama2", base_url="http://localhost:11434")

# Prompt the local Llama 2 model
analysis_prompt = """
Given the following job description and user skills, analyze if the user should apply.

Job Description:
{job_description}

User Skills:
{user_skills}

Provide:
1. Match percentage (0-100)
2. Key required skills
3. Missing skills
4. Recommendation: APPLY / SKIP
5. Brief reasoning
"""

job_analysis_agent = Agent(
    role="Job Match Analyst",
    goal="Determine if user should apply for a job",
    backstory="Expert recruiter with years of experience",
    llm=llm,
    verbose=True
)
```

### **Agent 3: Resume Customization Agent**

```python
# agents/resume_customization_agent.py
from crewai import Agent
from langchain.llms import Ollama
from transformers import AutoTokenizer, AutoModelForSequenceClassification

llm = Ollama(model="mistral", base_url="http://localhost:11434")  # Faster model

resume_customization_agent = Agent(
    role="Resume Optimization Specialist",
    goal="Customize resume for specific job applications",
    backstory="ATS optimization expert",
    llm=llm,  # Uses local Mistral for speed
    verbose=True
)

# Use HuggingFace for keyword extraction
def extract_keywords_hf(job_description):
    """Extract keywords using local HuggingFace model"""
    from transformers import pipeline
    
    # Load free extractive QA model
    qa_pipeline = pipeline("question-answering", 
                          model="deepset/roberta-base-squad2")
    
    # Extract required skills
    result = qa_pipeline(
        question="What skills are required?",
        context=job_description
    )
    return result['answer']
```

### **Cost Comparison**

```
Traditional Approach (Monthly Costs):
- OpenAI GPT-4 API: ~$300-500/month
- GPT-3.5: ~$50-100/month
- Anthropic Claude: ~$20-50/month

DevApply Approach (ZERO COST):
- Ollama (Local Llama 2): $0
- HuggingFace Transformers: $0
- Pytesseract OCR: $0
- Total: $0/month
```

---

## ⚙️ Configuration & Environment Variables

Create `.env` file in project root:

```bash
# ============================================
# DATABASE & CACHING
# ============================================
DATABASE_URL=postgresql://devapply_user:secure_password@localhost:5432/devapply
REDIS_URL=redis://localhost:6379
DATABASE_ECHO=false  # Set to true for SQL debugging

# ============================================
# JWT & SECURITY
# ============================================
JWT_SECRET_KEY=your-super-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1
REFRESH_TOKEN_EXPIRATION_DAYS=7

# ============================================
# LOCAL LLM CONFIGURATION (OLLAMA)
# ============================================
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama2          # Main model: llama2, mistral, neural-chat
OLLAMA_FAST_MODEL=mistral         # Fast model for quick tasks
OLLAMA_TEMPERATURE=0.7             # Creativity level (0-1)
OLLAMA_NUM_PREDICT=256             # Max tokens to generate

# ============================================
# HUGGING FACE MODELS (LOCAL INFERENCE)
# ============================================
HF_TRANSFORMERS_CACHE=/home/user/.cache/huggingface
HF_OCR_MODEL=distilbert-base-uncased  # For text extraction
HF_EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ============================================
# FILE STORAGE
# ============================================
STORAGE_PATH=/var/devapply/resumes
MAX_RESUME_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,docx,doc

# ============================================
# BROWSER AUTOMATION
# ============================================
PLAYWRIGHT_TIMEOUT_MS=30000
USE_HEADLESS_BROWSER=true
BROWSER_VIEWPORT_WIDTH=1920
BROWSER_VIEWPORT_HEIGHT=1080
ENABLE_STEALTH_MODE=true
BROWSER_LAUNCH_ARGS=--no-sandbox,--disable-gpu

# ============================================
# BOT DETECTION EVASION
# ============================================
MIN_DELAY_BETWEEN_ACTIONS_SEC=1
MAX_DELAY_BETWEEN_ACTIONS_SEC=5
RANDOMIZE_USER_AGENT=true
ROTATE_PROXIES=false  # Set to true if using proxy rotation
PROXY_LIST=  # Comma-separated list of proxies (optional)

# ============================================
# CAPTCHA HANDLING (Optional Fallback)
# ============================================
CAPTCHA_SOLVING_ENABLED=false
CAPTCHA_SOLVER_API_KEY=  # Leave empty if using fallback (manual review)
CAPTCHA_SOLVER_SERVICE=2captcha  # or anticaptcha, deathbycaptcha

# ============================================
# EMAIL SERVICE (Password Reset)
# ============================================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-specific-password
SMTP_TLS=true

# ============================================
# APPLICATION SETTINGS
# ============================================
APP_NAME=DevApply
APP_VERSION=1.0.0
ENVIRONMENT=development  # development, staging, production
DEBUG=true
LOG_LEVEL=INFO

# ============================================
# FRONTEND (STREAMLIT)
# ============================================
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_CLIENT_TOOLBAR_MODE=minimal
BACKEND_API_URL=http://localhost:8000

# ============================================
# AGENT CONFIGURATION
# ============================================
MAX_APPLICATIONS_PER_RUN=10
MAX_DAILY_APPLICATIONS=50
AGENT_EXECUTION_TIMEOUT_MINUTES=60
ENABLE_AGENT_LOGGING=true
AGENT_LOG_PATH=/var/log/devapply/agents.log

# ============================================
# CELERY TASK QUEUE
# ============================================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TASK_TIME_LIMIT=3600
CELERY_TASK_SOFT_TIME_LIMIT=3000

# ============================================
# MONITORING & LOGGING
# ============================================
LOG_FILE_PATH=/var/log/devapply/app.log
LOG_ROTATION_SIZE_MB=100
LOG_BACKUP_COUNT=10
SENTRY_DSN=  # Optional: for error tracking

# ============================================
# JOB PLATFORM CREDENTIALS (If Needed)
# ============================================
LINKEDIN_EMAIL=your-linkedin@email.com
LINKEDIN_PASSWORD=your-linkedin-password
# Note: Use environment variables carefully for credentials
# Preferably use OAuth2 where available
```

### **Docker Environment File (.env.docker)**
```bash
# For Docker Compose deployment
DATABASE_URL=postgresql://devapply_user:secure_password@postgres:5432/devapply
REDIS_URL=redis://redis:6379
OLLAMA_API_URL=http://ollama:11434
BACKEND_API_URL=http://fastapi:8000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### **Production Environment Variables (.env.production)**
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
JWT_EXPIRATION_HOURS=2
REFRESH_TOKEN_EXPIRATION_DAYS=30
USE_HEADLESS_BROWSER=true
ENABLE_STEALTH_MODE=true
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
```

---

---

## 📦 Installation & Setup

### **Prerequisites**
- Python 3.10+
- PostgreSQL 14+
- Redis 7+
- Ollama (for free local LLM) OR Docker (to containerize everything)
- Git

### **STEP 1: Clone Repository**
```bash
git clone https://github.com/yourusername/devapply.git
cd devapply
```

### **STEP 2: Backend Setup**
```bash
# Create Python virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Install Tesseract OCR
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

# Initialize database
python -m alembic upgrade head

# Start FastAPI backend
uvicorn app.main:app --reload --port 8000
```

### **STEP 3: Setup Free LLM (Choose One)**

#### **Option A: Ollama (Recommended)**
```bash
# Download Ollama from https://ollama.ai
# Then pull models locally (first run downloads ~4-5GB)

ollama pull llama2
# OR
ollama pull mistral

# Start Ollama service
ollama serve

# Ollama will be available at http://localhost:11434
```

#### **Option B: HuggingFace Transformers**
```bash
# Already installed via requirements.txt
# Models will auto-download on first use (3-7GB each)
# Cached in ~/.cache/huggingface/hub/

python scripts/download_models.py  # Optional: pre-download
```

#### **Option C: Docker Setup (All-in-One)**
```bash
# Use docker-compose to start everything
docker-compose up -d

# Services will start:
# - PostgreSQL (port 5432)
# - Redis (port 6379)
# - Ollama (port 11434)
# - FastAPI Backend (port 8000)
# - Streamlit Frontend (port 8501)
```

### **STEP 4: Frontend Setup (Streamlit)**
```bash
# Install Streamlit dependencies (already in requirements.txt)
pip install streamlit plotly pandas

# Create Streamlit secrets file
mkdir -p ~/.streamlit
cat > ~/.streamlit/secrets.toml << EOF
backend_url = "http://localhost:8000"
jwt_secret = "your-secret-key"
EOF

# Run Streamlit app
streamlit run app/frontend/main.py

# Access at http://localhost:8501
```

### **STEP 5: Verify Installation**

```bash
# Check all services are running
curl http://localhost:8000/docs          # FastAPI docs
curl http://localhost:11434/api/tags    # Ollama API
# Open http://localhost:8501             # Streamlit UI
```

### **Complete Docker Compose Setup (Recommended)**

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: devapply
      POSTGRES_USER: devapply_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: serve

  fastapi:
    build:
      context: .
      dockerfile: backend.Dockerfile
    environment:
      DATABASE_URL: postgresql://devapply_user:secure_password@postgres:5432/devapply
      REDIS_URL: redis://redis:6379
      OLLAMA_API_URL: http://ollama:11434
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - ollama

  streamlit:
    build:
      context: .
      dockerfile: frontend.Dockerfile
    environment:
      BACKEND_URL: http://fastapi:8000
    ports:
      - "8501:8501"
    depends_on:
      - fastapi

volumes:
  postgres_data:
  ollama_data:
```

### **STEP 6: Initialize with Demo Data**
```bash
# Create superuser
python scripts/create_admin.py

# Load sample job categories
python scripts/load_sample_data.py

# Test automation agents
python scripts/test_agents.py
```

### **Complete Requirements.txt**
```
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
streamlit==1.28.1

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1

# Task Queue
celery==5.3.4
python-celery-beat==2.5.0

# LLM & AI (Free Models)
langchain==0.0.353
crewai==0.1.0
ollama==0.1.18
transformers==4.35.2
torch==2.1.1
sentence-transformers==2.2.2

# Browser Automation
playwright==1.40.0
beautifulsoup4==4.12.2
lxml==4.9.3

# Computer Vision & OCR
opencv-python==4.8.1.78
pytesseract==0.3.10
pillow==10.1.0
numpy==1.26.2

# Utilities
requests==2.31.0
pydantic==2.5.1
pydantic-settings==2.1.0
pyjwt==2.8.1
bcrypt==4.1.1
python-dotenv==1.0.0
fake-useragent==1.4.0
pyautogui==0.9.53

# Resume Processing
python-docx==0.8.11
pdfplumber==0.10.3
pypdf==3.17.1
reportlab==4.0.7

# Data & Analytics
pandas==2.1.3
plotly==5.18.0
matplotlib==3.8.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Monitoring & Logging
python-json-logger==2.0.7

# Development
black==23.12.0
ruff==0.1.8
mypy==1.7.1
```

---

## 📚 Minimum Python Packages Required (ALL FREE & OPEN-SOURCE)

Install all packages with a single command:

```bash
pip install \
  fastapi uvicorn \
  streamlit plotly pandas \
  sqlalchemy alembic psycopg2-binary redis \
  langchain crewai ollama \
  transformers torch sentence-transformers \
  playwright beautifulsoup4 lxml \
  opencv-python pytesseract pillow numpy \
  python-docx pdfplumber \
  requests pydantic pyjwt bcrypt \
  python-dotenv fake-useragent pyautogui \
  celery python-celery-beat \
  pytest pytest-asyncio
```

### **Free & Open-Source Stack Overview**

| Component | Library | License | Cost |
|-----------|---------|---------|------|
| **Backend** | FastAPI | MIT | Free |
| **Frontend** | Streamlit | Apache 2.0 | Free |
| **Database** | PostgreSQL | PostgreSQL License | Free |
| **Cache** | Redis | BSD | Free |
| **LLM (Local)** | Ollama + Llama 2 | Open Source | Free |
| **LLM (Alt)** | Transformers | Apache 2.0 | Free |
| **Browser** | Playwright | Apache 2.0 | Free |
| **Vision** | OpenCV | Apache 2.0 | Free |
| **OCR** | Tesseract | Apache 2.0 | Free |
| **Agents** | CrewAI | MIT | Free |
| **LLM Integration** | LangChain | MIT | Free |
| **Resume Processing** | python-docx, pdfplumber | MIT, BSD | Free |
| **Task Queue** | Celery | BSD | Free |
| **Testing** | Pytest | MIT | Free |

**Total Cost:** $0 (All Open-Source & Self-Hosted)

---

## 🎯 Quick Start Guide

### **1. Clone & Setup (5 minutes)**
```bash
git clone https://github.com/yourusername/devapply.git
cd devapply
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Start Ollama (2 minutes)**
```bash
# In a new terminal
ollama pull llama2
ollama serve
# Wait for: "Listening on 127.0.0.1:11434"
```

### **3. Initialize Database (1 minute)**
```bash
python -m alembic upgrade head
python scripts/create_admin.py
```

### **4. Start Backend (1 minute)**
```bash
uvicorn app.main:app --reload --port 8000
# Visit: http://localhost:8000/docs for API docs
```

### **5. Start Frontend (1 minute)**
```bash
# In another terminal
streamlit run app/frontend/main.py
# Visit: http://localhost:8501
```

### **6. Test Agents (5 minutes)**
```bash
# In another terminal
python scripts/test_agents.py
```

**Total Setup Time: ~15 minutes (first time, includes Ollama model download)**

---

## 📋 Deliverables

### **Code**
- [ ] Fully functional FastAPI backend
- [ ] React frontend with Tailwind CSS
- [ ] CrewAI agent implementation
- [ ] Comprehensive test suite
- [ ] Docker setup

### **Documentation**
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Agent workflow documentation
- [ ] Deployment guide
- [ ] User guide & dashboard walkthrough
- [ ] Architecture documentation

### **DevOps**
- [ ] Docker Compose configuration
- [ ] GitHub Actions CI/CD pipeline
- [ ] Environment variable templates
- [ ] Database migration scripts

---

## 🎓 Success Criteria

✅ **Functional Requirements Met:**
- User authentication & profile management working
- Dashboard displaying accurate application metrics
- AI agents executing successful job searches
- Applications being submitted automatically
- Resume customization functioning properly
- CAPTCHA handling operational

✅ **Performance Targets:**
- Agent completes job search in <2 minutes
- Application submission success rate >90%
- Dashboard loads in <2 seconds
- API response times <500ms
- Support 100+ concurrent users

✅ **Security:**
- No SQL injection vulnerabilities
- JWT tokens properly secured
- Data encrypted at rest & in transit
- Rate limiting enforced
- Regular security audits passed

---

## 📞 Support & Maintenance

- Regular dependency updates
- Monthly security patches
- Agent performance optimization
- New job platform integrations
- Feature enhancements based on user feedback
- 24/7 monitoring & alerting

---

## 🧪 Testing Strategy (Pure Python with Pytest)

### **Unit Tests** - Test individual components
```bash
pytest tests/unit/test_agents.py
pytest tests/unit/test_api.py
pytest tests/unit/test_resume_customization.py
```

Example test:
```python
# tests/unit/test_agents.py
import pytest
from agents.job_search_agent import JobSearchAgent
from langchain.llms import Ollama

@pytest.fixture
def llm():
    return Ollama(model="llama2", base_url="http://localhost:11434")

def test_job_search_agent_initialization(llm):
    agent = JobSearchAgent(llm=llm)
    assert agent is not None
    assert agent.role == "Job Search Specialist"

@pytest.mark.asyncio
async def test_search_jobs_functionality(llm):
    agent = JobSearchAgent(llm=llm)
    results = await agent.search(
        keywords="Python Developer",
        location="Remote"
    )
    assert len(results) > 0
    assert "job_title" in results[0]
```

### **Integration Tests** - Test component interactions
```bash
pytest tests/integration/test_agent_workflow.py
pytest tests/integration/test_api_database.py
pytest tests/integration/test_resume_processing.py
```

Example test:
```python
# tests/integration/test_agent_workflow.py
@pytest.mark.asyncio
async def test_complete_agent_workflow():
    """Test: search → analyze → customize resume → apply"""
    user_strategy = load_test_strategy()
    
    # Run job search agent
    jobs = await job_search_agent.execute(user_strategy)
    assert len(jobs) > 0
    
    # Run analysis agent
    approved_jobs = await analysis_agent.execute(jobs, user_strategy)
    assert len(approved_jobs) <= len(jobs)
    
    # Run customization agent
    customized = await customization_agent.execute(approved_jobs[0])
    assert customized["resume"] is not None
```

### **E2E Tests** - Test complete user flows
```bash
pytest tests/e2e/test_user_registration.py
pytest tests/e2e/test_application_submission.py
```

### **Performance Tests** - Load testing
```bash
pytest tests/performance/test_load.py

# Using locust for load testing
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

### **Test Coverage**
```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# View report at: htmlcov/index.html
```

### **Continuous Testing (GitHub Actions)**
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest --cov=app
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## 🏗️ Project Structure (Pure Python)

```
devapply/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # Dependency injection
│   │
│   ├── backend/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # Login/register endpoints
│   │   │   ├── users.py          # User CRUD endpoints
│   │   │   ├── strategies.py     # Strategy management endpoints
│   │   │   ├── applications.py   # Application tracking endpoints
│   │   │   ├── resumes.py        # Resume upload endpoints
│   │   │   └── agents.py         # Agent control endpoints
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # SQLAlchemy User model
│   │   │   ├── strategy.py       # Strategy model
│   │   │   ├── application.py    # Application model
│   │   │   ├── resume.py         # Resume model
│   │   │   └── agent_execution.py # Agent logs model
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # Pydantic schemas
│   │   │   ├── strategy.py
│   │   │   ├── application.py
│   │   │   └── resume.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py   # JWT token management
│   │   │   ├── user_service.py   # User business logic
│   │   │   ├── strategy_service.py
│   │   │   ├── application_service.py
│   │   │   └── resume_service.py
│   │   │
│   │   └── database/
│   │       ├── __init__.py
│   │       ├── connection.py     # Database connection
│   │       └── session.py        # Session management
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── config.py             # LLM configuration (Ollama)
│   │   ├── job_search_agent.py   # Job search logic
│   │   ├── analysis_agent.py     # Job analysis logic
│   │   ├── customization_agent.py # Resume customization
│   │   ├── application_agent.py  # Form filling & submission
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── search_tools.py   # Job search functions
│   │   │   ├── analysis_tools.py # Skill matching, etc
│   │   │   ├── vision_tools.py   # OpenCV/OCR functions
│   │   │   └── browser_tools.py  # Playwright functions
│   │   └── executor.py           # Agent workflow orchestration
│   │
│   ├── automation/
│   │   ├── __init__.py
│   │   ├── browser.py            # Playwright wrapper
│   │   ├── vision.py             # OpenCV/Tesseract wrapper
│   │   ├── captcha_handler.py    # CAPTCHA detection
│   │   ├── form_parser.py        # HTML form parsing
│   │   └── human_simulation.py   # Mouse/typing simulation
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── celery_tasks.py       # Background job definitions
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py             # Logging configuration
│   │   ├── errors.py             # Custom exceptions
│   │   ├── validators.py         # Input validation
│   │   └── helpers.py            # Utility functions
│   │
│   └── frontend/
│       ├── main.py               # Streamlit main entry point
│       ├── config.py             # Streamlit configuration
│       ├── pages/
│       │   ├── __init__.py
│       │   ├── 01_Login.py       # Authentication page
│       │   ├── 02_Dashboard.py   # Main dashboard
│       │   ├── 03_Strategy.py    # Strategy configuration
│       │   ├── 04_Resume.py      # Resume management
│       │   ├── 05_Applications.py # Application history
│       │   ├── 06_Analytics.py   # Analytics dashboard
│       │   └── 07_Settings.py    # User settings
│       │
│       ├── components/
│       │   ├── __init__.py
│       │   ├── header.py         # Header component
│       │   ├── sidebar.py        # Navigation sidebar
│       │   ├── metrics.py        # Metric displays
│       │   ├── charts.py         # Chart components
│       │   └── tables.py         # Data table components
│       │
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── api_client.py     # HTTP client for backend
│       │   ├── auth.py           # JWT management
│       │   ├── cache.py          # Streamlit caching
│       │   └── helpers.py        # UI helpers
│       │
│       └── styles/
│           └── custom.css        # Custom Streamlit styling
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   │
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_api.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   │
│   ├── integration/
│   │   ├── test_agent_workflow.py
│   │   ├── test_api_database.py
│   │   └── test_resume_processing.py
│   │
│   └── e2e/
│       ├── test_user_flow.py
│       └── test_application_flow.py
│
├── scripts/
│   ├── __init__.py
│   ├── create_admin.py           # Create superuser
│   ├── load_sample_data.py       # Load test data
│   ├── test_agents.py            # Manual agent testing
│   ├── setup_ollama.py           # Ollama setup helper
│   └── migrations/
│       └── 001_initial_schema.sql
│
├── docker/
│   ├── Dockerfile.backend        # FastAPI Dockerfile
│   ├── Dockerfile.frontend       # Streamlit Dockerfile
│   └── Dockerfile.ollama         # Ollama Dockerfile
│
├── migrations/
│   └── versions/                 # Alembic migration files
│
├── logs/
│   └── app.log                   # Application logs
│
├── .github/
│   └── workflows/
│       ├── test.yml              # Automated testing
│       ├── lint.yml              # Code quality checks
│       └── deploy.yml            # Deployment automation
│
├── .env.example                  # Environment variables template
├── .gitignore
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Docker orchestration
├── alembic.ini                   # Database migration config
├── pytest.ini                    # Pytest configuration
├── pyproject.toml                # Project metadata
└── README.md                     # Project documentation
```

---

## 📝 Notes for IDX Development

This comprehensive specification provides a complete blueprint for building DevApply as a **production-grade, 100% Python application** with **zero external LLM costs**.

### **Key Advantages of This Approach**

✅ **Pure Python Stack**
- Single language throughout (Python for backend, frontend, agents, utilities)
- Easier to maintain and deploy
- Unified development experience
- Simpler debugging and profiling
- Reduced cognitive load for developers

✅ **Zero Licensing Costs**
- All dependencies are open-source (MIT, Apache 2.0, BSD licenses)
- No paid API keys required
- Ollama + Llama 2 fully self-hosted
- No vendor lock-in

✅ **Complete Data Privacy**
- All LLM processing happens locally
- No data sent to external APIs
- Full compliance with data protection regulations
- User resumes never leave the system

✅ **Unlimited Scalability**
- No rate limiting from external APIs
- Run as many agents as hardware allows
- Cost scales only with hardware, not API calls
- Can add more job applications without increasing costs

### **Architecture Highlights**

1. **Streamlit Frontend** - Beautiful, responsive UI built entirely in Python
   - No HTML/CSS/JavaScript required
   - Interactive widgets and real-time updates
   - Automatic responsive design
   - Easy to extend with custom components

2. **FastAPI Backend** - High-performance Python web framework
   - Async/await support for concurrent operations
   - Automatic API documentation (Swagger/OpenAPI)
   - Type hints for better code quality
   - Excellent for microservices architecture

3. **CrewAI + LangChain** - Python-native AI orchestration
   - Modular agent architecture
   - Clear separation of concerns
   - Easy to test and debug
   - Supports multiple LLM backends

4. **Ollama Local LLMs** - No subscription required
   - Llama 2: 70B (best quality), 13B (balanced), 7B (fast)
   - Mistral: 7B (faster, better at reasoning)
   - Neural-chat: Optimized for conversations
   - Can switch between models without code changes

5. **Playwright** - Modern browser automation
   - Works with Chromium, Firefox, WebKit
   - Better performance than Selenium
   - Native support for modern web features
   - Excellent for handling dynamic sites

### **Cost Breakdown (12-Month Projection)**

**Traditional Cloud Approach:**
```
OpenAI API Usage:        $5,000/month × 12  = $60,000
AWS/GCP Hosting:          $1,000/month × 12  = $12,000
Database (Managed):         $500/month × 12  = $6,000
Redis (Managed):            $300/month × 12  = $3,600
Monitoring/Logging:         $200/month × 12  = $2,400
TOTAL: $84,000/year
```

**DevApply Self-Hosted Approach:**
```
Hardware (VPS):             $30/month × 12  = $360
Domain Name:               $10/year        = $10
Miscellaneous:             $10/month × 12  = $120
TOTAL: $490/year (98% savings!)
```

### **Performance Expectations**

With recommended hardware (8GB RAM, 4 CPU cores):
- Job search: 2-5 minutes per run
- Job analysis: 30-60 seconds per job
- Resume customization: 1-3 minutes per job
- Application submission: 2-5 minutes per job
- Total workflow: 30-60 minutes for 10 applications

### **Security Best Practices Included**

1. **Authentication**
   - JWT tokens with short expiry
   - Refresh token rotation
   - Password hashing with bcrypt
   - Email verification

2. **Data Protection**
   - Environment variables for secrets
   - Encrypted database connections
   - HTTPS/TLS in production
   - Secure file storage

3. **API Security**
   - Rate limiting
   - CORS configuration
   - Input validation (Pydantic)
   - SQL injection protection (ORM)

4. **Bot Evasion**
   - Randomized delays and user agents
   - Mouse movement simulation
   - Request header customization
   - Headless browser stealth mode

### **Development Timeline**

With an experienced Python developer:
- **Weeks 1-2:** Foundation setup (API, DB, auth)
- **Weeks 3-4:** Frontend & dashboard
- **Weeks 5-6:** Agent implementation
- **Weeks 7-8:** Browser automation & integration
- **Weeks 9-10:** Testing & optimization
- **Weeks 11-12:** Deployment & documentation

**Total: 3 months to production-ready system**

### **Deployment Options**

1. **Docker Compose** (Recommended for single server)
   - All services in one stack
   - Easy to manage and update
   - Good for small to medium deployments

2. **Kubernetes** (For enterprise scale)
   - Auto-scaling capabilities
   - High availability
   - Rolling updates
   - Service mesh integration

3. **VPS Deployment** (Cost-effective)
   - DigitalOcean, Linode, Vultr
   - ~$5-30/month for adequate performance
   - Full control over environment

4. **Home Lab** (For testing)
   - Run on existing hardware
   - Perfect for development
   - Zero infrastructure costs

### **Monitoring & Maintenance**

1. **Application Monitoring**
   - Prometheus for metrics
   - Grafana for visualization
   - Custom dashboards for agent performance

2. **Log Management**
   - Centralized logging to file
   - Log rotation to prevent disk fill
   - Error tracking and alerting

3. **Health Checks**
   - Regular API health endpoints
   - Database connection monitoring
   - Ollama LLM availability checks

4. **Backup Strategy**
   - Daily database backups
   - Automated backup retention
   - Test restore procedures regularly

### **Future Enhancement Possibilities**

1. **Multi-User Support**
   - Role-based access control (RBAC)
   - Team/organization management
   - Shared strategy templates

2. **Advanced Features**
   - Interview scheduling automation
   - Offer negotiation assistant
   - Machine learning skill improvement suggestions
   - Job market analytics

3. **Platform Expansion**
   - Support for more job boards
   - Integration with HR systems
   - Mobile app (using Streamlit Mobile)
   - API for third-party integrations

4. **Monetization Options**
   - SaaS subscription model
   - Premium agent features
   - API access for developers
   - White-label solutions

### **Support Resources**

- **Streamlit Documentation:** https://docs.streamlit.io
- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **LangChain Documentation:** https://python.langchain.com
- **CrewAI Documentation:** https://github.com/joaomdmoura/crewAI
- **Ollama Documentation:** https://github.com/ollama/ollama
- **Playwright Documentation:** https://playwright.dev/python

### **Critical Success Factors**

1. **Reliable Ollama Setup** - Test locally before deployment
2. **Comprehensive Testing** - Unit, integration, and E2E tests
3. **Good Documentation** - For future maintenance
4. **Monitoring in Production** - Know when things break
5. **Regular Backups** - User data is precious
6. **Security Updates** - Keep dependencies current

---

## 🎯 Summary

DevApply represents a **modern approach to AI automation** that leverages:
- Pure Python for end-to-end development
- Free, open-source components
- Self-hosted AI models (no API costs)
- Production-ready architecture
- Enterprise-grade security

This specification is **100% implementation-ready** and provides everything needed to build a world-class job application automation platform.

**The estimated ROI for organizations using DevApply:**
- Time saved: 20-30 hours/month per job seeker
- Cost savings: $60,000+/year vs. commercial solutions
- Quality improvement: Better job matches through AI analysis
- Scalability: Zero variable costs with scale

---

**End of Specification Document**

---

**Document Version:** 1.0  
**Architecture:** Pure Python (Streamlit + FastAPI)  
**LLM Model:** Local Ollama (Llama 2 / Mistral)  
**Cost:** $0 (Open-Source)  
**Status:** Ready for Production Implementation  
**Last Updated:** 2024
