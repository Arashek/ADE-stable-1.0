#!/bin/bash

# Function to check if Ollama is ready
check_ollama_ready() {
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:11434/api/health > /dev/null; then
            return 0
        fi
        echo "Waiting for Ollama to be ready (attempt $attempt/$max_attempts)..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    return 1
}

# Function to download a model if it doesn't exist
download_model() {
    local model=$1
    local max_attempts=3
    local attempt=1
    
    echo "Checking if model $model exists..."
    
    # Check if model exists
    if ollama list | grep -q "^$model"; then
        echo "Model $model already exists"
        return 0
    fi
    
    while [ $attempt -le $max_attempts ]; do
        echo "Downloading model $model (attempt $attempt/$max_attempts)..."
        if ollama pull $model; then
            echo "Successfully downloaded $model"
            return 0
        else
            echo "Failed to download $model on attempt $attempt"
            if [ $attempt -lt $max_attempts ]; then
                echo "Retrying in 5 seconds..."
                sleep 5
            fi
        fi
        attempt=$((attempt + 1))
    done
    
    echo "Failed to download $model after $max_attempts attempts"
    return 1
}

# Wait for Ollama to be ready
if ! check_ollama_ready; then
    echo "Error: Ollama failed to start within the expected time"
    exit 1
fi

# Download our preferred models
MODELS=(
    "mistral:7b-instruct"
    "codellama:7b-instruct"
    "neural-chat:7b-v3-1"
)

# Track failed downloads
failed_models=()

for model in "${MODELS[@]}"; do
    if ! download_model $model; then
        failed_models+=("$model")
    fi
done

# Report any failures
if [ ${#failed_models[@]} -ne 0 ]; then
    echo "Warning: Failed to download the following models:"
    printf '%s\n' "${failed_models[@]}"
    echo "The container will continue running with available models"
fi

# Keep the container running
exec tail -f /dev/null 