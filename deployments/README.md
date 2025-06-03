# Deployments Directory

## Overview

The `deployments` directory contains configuration files and resources for deploying the Fluxora energy forecasting platform to production environments. This directory provides the necessary infrastructure as code to ensure consistent, reliable deployments across different environments.

## Structure

The directory is organized as follows:

- **Dockerfile**: Container definition for the Fluxora application
- **kubernetes/**: Kubernetes configuration files for orchestrating containers
  - **model-deployment.yaml**: Kubernetes deployment configuration for the model service

## Deployment Resources

### Dockerfile

The Dockerfile defines the container image for the Fluxora application:

- Based on Python 3.10 slim image
- Installs required dependencies
- Sets up the application environment
- Configures the entry point for the API service

Key features:
- Exposes port 8000 for the API
- Sets the Python path to include the application directory
- Uses uvicorn to serve the FastAPI application

### Kubernetes Configurations

The `kubernetes/` directory contains Kubernetes manifests for deploying Fluxora services:

#### model-deployment.yaml

Defines a Kubernetes deployment for the model service with:
- 3 replicas for high availability
- Container image configuration
- Port exposure
- Environment variable configuration via ConfigMap

## Usage

### Building the Docker Image

```bash
# From the project root
docker build -t your-registry/energy-model:latest -f deployments/Dockerfile .
```

### Pushing to Container Registry

```bash
# Login to your container registry
docker login your-registry

# Push the image
docker push your-registry/energy-model:latest
```

### Deploying to Kubernetes

```bash
# Apply the Kubernetes configuration
kubectl apply -f deployments/kubernetes/model-deployment.yaml
```

## Deployment Workflow

1. Build the Docker image using the Dockerfile
2. Push the image to your container registry
3. Update Kubernetes manifests with the correct image reference
4. Apply Kubernetes manifests to your cluster
5. Verify the deployment status

## Best Practices

- Keep sensitive information in Kubernetes Secrets, not in configuration files
- Use environment-specific configuration for different deployment environments
- Version your container images with meaningful tags
- Implement health checks and readiness probes
- Set appropriate resource limits and requests

## Integration with CI/CD

The deployment configurations can be integrated with CI/CD pipelines:

1. Automated builds triggered by code changes
2. Automated testing before deployment
3. Deployment to staging environments for validation
4. Promotion to production after approval

## Related Documentation

For more information on deployment processes, refer to:

- The `docs/ARCHITECTURE.md` file for system architecture details
- The `infrastructure/` directory for infrastructure provisioning
- The `monitoring/` directory for monitoring configurations
