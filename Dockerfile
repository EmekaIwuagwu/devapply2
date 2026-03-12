# ─────────────────────────────────────────────────────────────────────────────
# DevApply — Production Dockerfile (Render-ready)
#
# Runs both services in one container:
#   • FastAPI backend  → internal port 8000
#   • Streamlit UI     → $PORT (Render sets this; default 8501)
#
# Build:  docker build -t devapply .
# Run:    docker run -p 8501:8501 --env-file .env devapply
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Prevents Python from writing .pyc files and buffers stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Store Playwright browsers inside the image (not in $HOME/.cache)
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# ── System dependencies ────────────────────────────────────────────────────
# Chromium headless needs a specific set of shared libs.
# tesseract-ocr is required by pytesseract (OCR fallback in ApplicationAgent).
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OCR
    tesseract-ocr \
    # OpenCV headless
    libgl1 \
    libglib2.0-0 \
    # Chromium runtime deps (equivalent to playwright install-deps chromium)
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ────────────────────────────────────────────────────
# Use requirements-render.txt (stripped of unused heavy ML packages)
COPY requirements-render.txt .
RUN pip install --no-cache-dir -r requirements-render.txt

# ── Playwright Chromium ────────────────────────────────────────────────────
# Must use `python -m playwright` (not the Node.js `playwright` CLI)
RUN python -m playwright install chromium

# ── Application code ───────────────────────────────────────────────────────
COPY . .

# Create runtime directories (Render has ephemeral storage on free plan)
RUN mkdir -p storage/resumes logs screenshots

# ── Startup script ─────────────────────────────────────────────────────────
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose both ports for local docker-compose use.
# On Render only $PORT is routed publicly (Streamlit UI).
EXPOSE 8000 8501

CMD ["/start.sh"]
