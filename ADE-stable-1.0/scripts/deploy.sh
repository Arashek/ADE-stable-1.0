#!/bin/bash

# Deployment script for ADE Platform on cloudev.ai

# Exit on error
set -e

echo "Deploying ADE Platform to cloudev.ai..."

# Check for required environment variables
if [ -z "$CLOUDEV_API_KEY" ]; then
    echo "Error: CLOUDEV_API_KEY environment variable is not set"
    exit 1
fi

if [ -z "$CLOUDEV_PROJECT_ID" ]; then
    echo "Error: CLOUDEV_PROJECT_ID environment variable is not set"
    exit 1
fi

# Build production version
echo "Building production version..."
./scripts/build_prod.sh

# Push Docker image to registry
echo "Pushing Docker image to registry..."
docker tag ade-platform:latest cloudev.ai/$CLOUDEV_PROJECT_ID/ade-platform:latest
docker push cloudev.ai/$CLOUDEV_PROJECT_ID/ade-platform:latest

# Deploy to cloudev.ai
echo "Deploying to cloudev.ai..."
curl -X POST \
    -H "Authorization: Bearer $CLOUDEV_API_KEY" \
    -H "Content-Type: application/json" \
    -d @deploy-config.json \
    https://api.cloudev.ai/v1/projects/$CLOUDEV_PROJECT_ID/deployments

echo "Deployment completed successfully!" 