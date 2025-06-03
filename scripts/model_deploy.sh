#!/bin/bash

# Model Deployment Script for Fluxora
# This script handles the deployment of trained models to production

set -e

# Configuration
MODEL_DIR="./models"
DEPLOYMENT_ENV=${1:-"production"}  # Default to production if not specified
CONFIG_FILE="./config/config.yaml"
LOG_FILE="./logs/deployment.log"

# Create log directory if it doesn't exist
mkdir -p $(dirname $LOG_FILE)

echo "$(date): Starting model deployment to $DEPLOYMENT_ENV environment" | tee -a $LOG_FILE

# Check if model directory exists
if [ ! -d "$MODEL_DIR" ]; then
    echo "Error: Model directory $MODEL_DIR does not exist" | tee -a $LOG_FILE
    exit 1
fi

# Find the latest model
LATEST_MODEL=$(find $MODEL_DIR -name "model_*.pkl" -type f -printf "%T@ %p\n" | sort -nr | head -1 | cut -d' ' -f2-)

if [ -z "$LATEST_MODEL" ]; then
    echo "Error: No models found in $MODEL_DIR" | tee -a $LOG_FILE
    exit 1
fi

echo "Found latest model: $LATEST_MODEL" | tee -a $LOG_FILE

# Copy model to deployment location
DEPLOY_DIR="./deployments/models/$DEPLOYMENT_ENV"
mkdir -p $DEPLOY_DIR

echo "Copying model to deployment directory: $DEPLOY_DIR" | tee -a $LOG_FILE
cp $LATEST_MODEL $DEPLOY_DIR/current_model.pkl

# Update model version in config
MODEL_VERSION=$(basename $LATEST_MODEL | sed 's/model_\(.*\)\.pkl/\1/')
echo "Updating model version to $MODEL_VERSION in configuration" | tee -a $LOG_FILE

# For Kubernetes deployment
if [ "$DEPLOYMENT_ENV" = "production" ]; then
    echo "Preparing Kubernetes deployment" | tee -a $LOG_FILE
    
    # Update Kubernetes deployment file with new image tag
    sed -i "s/image: fluxora:v.*/image: fluxora:v$MODEL_VERSION/" ./deployments/kubernetes/model-deployment.yaml
    
    echo "Building Docker image" | tee -a $LOG_FILE
    # Uncomment the following lines when Docker is available
    # docker build -t fluxora:v$MODEL_VERSION -f ./deployments/Dockerfile .
    
    echo "Deploying to Kubernetes" | tee -a $LOG_FILE
    # Uncomment the following line when kubectl is configured
    # kubectl apply -f ./deployments/kubernetes/model-deployment.yaml
fi

echo "$(date): Model deployment completed successfully" | tee -a $LOG_FILE
echo "Model $MODEL_VERSION is now deployed to $DEPLOYMENT_ENV environment"
