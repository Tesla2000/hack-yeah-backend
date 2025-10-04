# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Configure Poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock ./

# Install dependencies only (no dev dependencies)
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code and resources
COPY runthroughlinehackathor/ ./runthroughlinehackathor/
COPY resources/ ./resources/

# Expose port (Railway will set PORT env var)
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
