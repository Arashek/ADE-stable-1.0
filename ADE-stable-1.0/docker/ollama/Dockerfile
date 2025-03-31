FROM ollama/ollama:latest

# Install additional system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create directory for model downloads
RUN mkdir -p /models

# Copy model download script
COPY scripts/download_models.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/download_models.sh

# Expose Ollama API port
EXPOSE 11434

# Health check with more lenient settings
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:11434/api/health || exit 1

# Create entrypoint script
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
/usr/local/bin/download_models.sh\n\
tail -f /dev/null' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"] 