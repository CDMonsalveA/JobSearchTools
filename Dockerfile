# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for PostgreSQL and Playwright
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy only dependency files first for better caching
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create virtual environment and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Install system dependencies for Playwright browsers
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers (for dynamic spiders)
RUN playwright install chromium firefox

# Copy the application code
COPY src/ ./src/
COPY README.md ./

# Install the project itself
RUN poetry install --no-interaction --no-ansi --only-root

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data /app/cache

# Set the Python path
ENV PYTHONPATH=/app/src

# Expose any ports if needed (optional, for future web interface)
# EXPOSE 8000

# Health check
HEALTHCHECK --interval=30m --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import psycopg2; conn = psycopg2.connect(host='${DB_HOST}', database='${DB_NAME}', user='${DB_USER}', password='${DB_PASSWORD}'); conn.close()" || exit 1

# Run the scheduler by default
CMD ["python", "-m", "jobsearchtools.scheduler"]
