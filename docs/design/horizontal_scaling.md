# Horizontal Scaling and Load Balancing Design

## Overview

This document outlines the design for implementing horizontal scaling capabilities and load balancing for the Fluxora energy forecasting platform. The design aims to enhance the platform's ability to handle increased load by distributing requests across multiple service instances while maintaining high availability and performance.

## Design Goals

1. Enable seamless horizontal scaling of Fluxora services
2. Implement efficient load balancing across service instances
3. Provide service discovery mechanisms for dynamic scaling
4. Ensure compatibility with existing Kubernetes infrastructure
5. Minimize changes to application code
6. Support both manual and automatic scaling based on metrics

## Architecture Components

### 1. Service Registry

A central service registry will be implemented to maintain an up-to-date catalog of available service instances. This registry will:

- Track service health and availability
- Support dynamic registration and deregistration
- Provide service metadata for intelligent routing
- Integrate with Kubernetes service discovery

**Implementation**: We will use Kubernetes Service and Endpoints resources as the foundation, enhanced with a custom service registry controller for additional metadata and health tracking.

### 2. Load Balancer

A load balancer will distribute incoming requests across available service instances based on configurable strategies. The load balancer will:

- Support multiple balancing algorithms (round-robin, least connections, weighted)
- Consider instance health and performance metrics
- Handle failover scenarios
- Provide sticky sessions when needed
- Offer circuit breaking capabilities

**Implementation**: We will implement an API Gateway pattern using Envoy proxy with custom configuration for advanced load balancing features.

### 3. Scaling Controller

A scaling controller will manage the dynamic scaling of services based on defined metrics and policies. The controller will:

- Monitor service performance metrics
- Scale services based on CPU, memory, and custom metrics
- Support scheduled scaling for predictable load patterns
- Implement scaling policies with cooldown periods
- Provide manual scaling capabilities

**Implementation**: We will leverage Kubernetes Horizontal Pod Autoscaler (HPA) extended with custom metrics from Prometheus.

### 4. Service Mesh

A service mesh will provide advanced networking capabilities for service-to-service communication. The mesh will:

- Enable secure communication between services
- Provide traffic management capabilities
- Support canary deployments and A/B testing
- Offer detailed telemetry for service interactions
- Implement retry and timeout policies

**Implementation**: We will integrate Istio service mesh for comprehensive service networking capabilities.

## Implementation Details

### Service Registry Implementation

```yaml
# service-registry.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fluxora-service-registry
  namespace: fluxora
spec:
  replicas: 3
  selector:
    matchLabels:
      app: service-registry
  template:
    metadata:
      labels:
        app: service-registry
    spec:
      containers:
        - name: service-registry
          image: fluxora/service-registry:latest
          ports:
            - containerPort: 8500
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
            requests:
              cpu: "200m"
              memory: "256Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 8500
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8500
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: service-registry
  namespace: fluxora
spec:
  selector:
    app: service-registry
  ports:
    - port: 8500
      targetPort: 8500
  type: ClusterIP
```

### Load Balancer Implementation

```yaml
# api-gateway.yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: fluxora-gateway
  namespace: fluxora
spec:
  selector:
    istio: ingressgateway
  servers:
    - port:
        number: 80
        name: http
        protocol: HTTP
      hosts:
        - "*"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: fluxora-api
  namespace: fluxora
spec:
  hosts:
    - "*"
  gateways:
    - fluxora-gateway
  http:
    - match:
        - uri:
            prefix: /api
      route:
        - destination:
            host: fluxora-api
            port:
              number: 8000
          weight: 100
      retries:
        attempts: 3
        perTryTimeout: 2s
      timeout: 5s
```

### Scaling Configuration

```yaml
# horizontal-pod-autoscaler.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fluxora-api-hpa
  namespace: fluxora
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fluxora-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: requests_per_second
        target:
          type: AverageValue
          averageValue: 1000
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
    scaleUp:
      stabilizationWindowSeconds: 60
```

### Service Mesh Configuration

```yaml
# service-mesh.yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  namespace: istio-system
  name: fluxora-istio-config
spec:
  profile: default
  components:
    egressGateways:
      - name: istio-egressgateway
        enabled: true
    ingressGateways:
      - name: istio-ingressgateway
        enabled: true
    pilot:
      enabled: true
  values:
    global:
      proxy:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

## Application Changes

### Service Registration

Each service will need to be updated to register with the service registry on startup and deregister on shutdown. This will be implemented through a common library that can be imported by all services.

```python
# service_registry.py
import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def register_service(app: FastAPI, service_name: str, service_version: str):
    """
    Register service with the service registry
    """
    registry_url = os.getenv("SERVICE_REGISTRY_URL", "http://service-registry:8500")
    service_id = f"{service_name}-{os.getenv('HOSTNAME', 'unknown')}"
    service_port = int(os.getenv("SERVICE_PORT", "8000"))

    # Register service on startup
    @app.on_event("startup")
    async def startup_event():
        try:
            response = requests.put(
                f"{registry_url}/v1/agent/service/register",
                json={
                    "ID": service_id,
                    "Name": service_name,
                    "Port": service_port,
                    "Check": {
                        "HTTP": f"http://{os.getenv('HOSTNAME')}:{service_port}/health",
                        "Interval": "10s",
                        "Timeout": "1s"
                    },
                    "Meta": {
                        "version": service_version
                    }
                }
            )
            if response.status_code == 200:
                print(f"Successfully registered service {service_id}")
            else:
                print(f"Failed to register service: {response.text}")
        except Exception as e:
            print(f"Error registering service: {str(e)}")

    # Deregister service on shutdown
    @app.on_event("shutdown")
    async def shutdown_event():
        try:
            response = requests.put(
                f"{registry_url}/v1/agent/service/deregister/{service_id}"
            )
            if response.status_code == 200:
                print(f"Successfully deregistered service {service_id}")
            else:
                print(f"Failed to deregister service: {response.text}")
        except Exception as e:
            print(f"Error deregistering service: {str(e)}")
```

### Health Check Endpoint

Each service will need a health check endpoint that can be used by the service registry and load balancer to determine service health.

```python
# health_check.py
from fastapi import FastAPI, Response, status
import psutil
import os

def add_health_check(app: FastAPI):
    """
    Add health check endpoints to the FastAPI application
    """
    @app.get("/health")
    async def health_check():
        """
        Basic health check endpoint
        """
        return {"status": "healthy"}

    @app.get("/health/detailed")
    async def detailed_health_check(response: Response):
        """
        Detailed health check with system metrics
        """
        # Check CPU and memory usage
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent

        # Check disk usage
        disk_usage = psutil.disk_usage('/').percent

        # Define thresholds
        cpu_threshold = 90
        memory_threshold = 90
        disk_threshold = 90

        # Determine health status
        is_healthy = (
            cpu_percent < cpu_threshold and
            memory_percent < memory_threshold and
            disk_usage < disk_threshold
        )

        # Set response status
        if not is_healthy:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_usage
            },
            "thresholds": {
                "cpu_percent": cpu_threshold,
                "memory_percent": memory_threshold,
                "disk_percent": disk_threshold
            }
        }
```

## Integration with Existing Infrastructure

The horizontal scaling and load balancing components will integrate with the existing Fluxora infrastructure as follows:

1. **Kubernetes Integration**: The service registry, load balancer, and scaling controller will be deployed as Kubernetes resources in the existing cluster.

2. **Monitoring Integration**: The scaling controller will use metrics from the existing Prometheus monitoring stack to make scaling decisions.

3. **Deployment Integration**: The existing CI/CD pipeline will be updated to include the new components and configurations.

4. **Configuration Integration**: The existing configuration management system will be extended to include configuration for the new components.

## Deployment Strategy

The horizontal scaling and load balancing components will be deployed in phases:

1. **Phase 1**: Deploy the service registry and update services to register with it.
2. **Phase 2**: Deploy the load balancer and configure it to use the service registry.
3. **Phase 3**: Deploy the scaling controller and configure it to scale services based on metrics.
4. **Phase 4**: Deploy the service mesh and configure it for advanced networking capabilities.

## Testing Strategy

The horizontal scaling and load balancing components will be tested as follows:

1. **Unit Testing**: Each component will have comprehensive unit tests to verify its functionality.
2. **Integration Testing**: The components will be tested together to ensure they work as expected.
3. **Load Testing**: The system will be subjected to load tests to verify its ability to scale and balance load.
4. **Failure Testing**: The system will be tested under failure conditions to verify its resilience.

## Conclusion

This design provides a comprehensive approach to implementing horizontal scaling and load balancing for the Fluxora platform. By leveraging Kubernetes, service mesh, and custom components, the design enables seamless scaling while maintaining high availability and performance.
