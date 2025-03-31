FROM python:3.9-slim as builder

# Install test dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY requirements.txt .
COPY pyproject.toml .
COPY setup.py .

# Install dependencies with test extras
RUN pip install -r requirements.txt[test]
RUN pip install pytest pytest-cov pytest-asyncio pytest-xdist

# Copy application code and tests
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=testing

# Run tests by default
CMD ["pytest", "--cov=src", "--cov-report=xml", "--cov-report=term-missing", "-v", "tests/"] 