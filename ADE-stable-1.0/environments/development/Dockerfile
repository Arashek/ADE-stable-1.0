FROM python:3.9-slim as builder

# Install development tools and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY requirements.txt .
COPY pyproject.toml .
COPY setup.py .

# Install dependencies with development extras
RUN pip install -r requirements.txt[dev]

# Development-specific setup
RUN npm install -g nodemon

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=development
ENV DEBUG=1

# Expose ports
EXPOSE 8000
EXPOSE 3000

# Use nodemon for hot reload
CMD ["nodemon", "--watch", "src", "--ext", "py", "--exec", "python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 