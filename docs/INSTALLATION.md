# Installation Guide

This guide covers all installation methods for Fluxora, from development environments to production deployments.

---

## 📑 Table of Contents

- [System Prerequisites](#system-prerequisites)
- [Installation Methods](#installation-methods)
  - [Method 1: Local Python Installation](#method-1-local-python-installation)
  - [Method 2: Docker Installation](#method-2-docker-installation)
  - [Method 3: Kubernetes Deployment](#method-3-kubernetes-deployment)
- [Web Frontend Setup](#web-frontend-setup)
- [Mobile Frontend Setup](#mobile-frontend-setup)
- [Verification](#verification)
- [Deployment Options](#deployment-options)

---

## System Prerequisites

### Required Software

| Software           | Minimum Version | Purpose                       | Installation Guide                                          |
| ------------------ | --------------- | ----------------------------- | ----------------------------------------------------------- |
| **Python**         | 3.9+            | Backend and ML components     | [python.org](https://www.python.org/downloads/)             |
| **Node.js**        | 16.0+           | Web and mobile frontends      | [nodejs.org](https://nodejs.org/)                           |
| **Docker**         | 20.10+          | Container runtime             | [docker.com](https://docs.docker.com/get-docker/)           |
| **Docker Compose** | 1.29+           | Multi-container orchestration | [docs.docker.com](https://docs.docker.com/compose/install/) |
| **PostgreSQL**     | 13+             | Relational database           | [postgresql.org](https://www.postgresql.org/download/)      |
| **Redis**          | 6.0+            | Caching and sessions          | [redis.io](https://redis.io/download)                       |
| **Git**            | 2.30+           | Version control               | [git-scm.com](https://git-scm.com/downloads)                |

### Optional Software

| Software       | Version | Purpose                  |
| -------------- | ------- | ------------------------ |
| **Kubernetes** | 1.20+   | Production orchestration |
| **Terraform**  | 1.0+    | Infrastructure as Code   |
| **Ansible**    | 2.10+   | Configuration management |
| **Kubectl**    | 1.20+   | Kubernetes CLI           |

### Hardware Requirements

| Deployment Type | CPU      | RAM    | Storage | Notes               |
| --------------- | -------- | ------ | ------- | ------------------- |
| **Development** | 2 cores  | 4 GB   | 10 GB   | Local testing       |
| **Staging**     | 4 cores  | 8 GB   | 50 GB   | Integration testing |
| **Production**  | 8+ cores | 16+ GB | 100+ GB | Scalable with load  |

---

## Installation Methods

### Method 1: Local Python Installation

Best for development and testing on a single machine.

#### Step 1: Clone Repository

```bash
git clone https://github.com/abrar2030/Fluxora.git
cd Fluxora
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

#### Step 3: Install Python Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "fastapi|tensorflow|xgboost|mlflow"
```

#### Step 4: Set Up Environment Variables

```bash
# Copy example environment file
cp code/.env.example code/.env

# Edit with your settings
nano code/.env
```

Required environment variables:

```bash
DATABASE_URL=sqlite:///./fluxora.db
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
LOG_LEVEL=INFO
```

#### Step 5: Initialize Database

```bash
cd code
python -c "from backend.database import init_db; init_db()"
```

#### Step 6: Start API Server

```bash
# From code directory
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Access API at: `http://localhost:8000/docs`

---

### Method 2: Docker Installation

Recommended for consistent environments and easy deployment.

#### Step 1: Clone Repository

```bash
git clone https://github.com/abrar2030/Fluxora.git
cd Fluxora
```

#### Step 2: Configure Environment

```bash
# Copy and edit environment file
cp code/.env.example code/.env
nano code/.env
```

#### Step 3: Build and Start Containers

```bash
# Build all services
docker-compose build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Step 4: Verify Services

```bash
# Check running containers
docker-compose ps

# Expected output:
# NAME                STATUS              PORTS
# fluxora-api        Up 30 seconds       0.0.0.0:8000->8000/tcp
# fluxora-db         Up 30 seconds       5432/tcp
# fluxora-redis      Up 30 seconds       6379/tcp
# fluxora-frontend   Up 30 seconds       0.0.0.0:3000->3000/tcp
```

#### Step 5: Access Services

| Service           | URL                            | Description          |
| ----------------- | ------------------------------ | -------------------- |
| API Documentation | `http://localhost:8000/docs`   | Interactive API docs |
| Web Dashboard     | `http://localhost:3000`        | User interface       |
| Health Check      | `http://localhost:8000/health` | System status        |

---

### Method 3: Kubernetes Deployment

For production environments requiring high availability and scalability.

#### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify kubectl
kubectl version --client
```

#### Step 1: Configure Kubernetes Cluster

```bash
# Set your cluster context
kubectl config use-context <your-cluster-name>

# Verify cluster access
kubectl cluster-info
```

#### Step 2: Create Namespace

```bash
kubectl create namespace fluxora

# Set as default namespace
kubectl config set-context --current --namespace=fluxora
```

#### Step 3: Deploy Application

```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/kubernetes/

# Check deployment status
kubectl get pods -n fluxora
kubectl get services -n fluxora
```

#### Step 4: Expose Service (Optional)

```bash
# Using LoadBalancer
kubectl expose deployment fluxora-api --type=LoadBalancer --port=8000

# Get external IP
kubectl get services fluxora-api
```

#### Step 5: Verify Deployment

```bash
# Check pod logs
kubectl logs -f deployment/fluxora-api

# Describe deployment
kubectl describe deployment fluxora-api

# Check resource usage
kubectl top pods
```

---

## Web Frontend Setup

The web frontend is a Node.js application built with modern frameworks.

### Installation Steps

```bash
# Navigate to web frontend directory
cd web-frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
nano .env
```

### Environment Configuration

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

### Start Development Server

```bash
# Start with hot reload
npm start

# Access at http://localhost:3000
```

### Build for Production

```bash
# Create optimized production build
npm run build

# Serve production build
npm install -g serve
serve -s build -l 3000
```

---

## Mobile Frontend Setup

Mobile app built with React Native and Expo.

### Installation Steps

```bash
# Navigate to mobile frontend directory
cd mobile-frontend

# Install dependencies
npm install

# Install Expo CLI globally
npm install -g expo-cli
```

### Configure Environment

```bash
# Edit app.json for configuration
nano app.json
```

### Start Development Server

```bash
# Start Expo development server
npx expo start

# Or use specific platform
npx expo start --ios
npx expo start --android
```

### Device Testing

```bash
# Install Expo Go app on your mobile device
# Scan QR code from terminal to launch app
```

---

## Verification

After installation, verify all components are working correctly.

### Backend Verification

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"ok"}

# Test API documentation
curl http://localhost:8000/docs
```

### Database Verification

```bash
# For SQLite (default)
sqlite3 code/fluxora.db ".tables"

# For PostgreSQL
psql -U postgres -d fluxora -c "\dt"
```

### Model Verification

```bash
# Check if model file exists
ls -lh code/fluxora_model.joblib

# Train initial model if missing
cd code
python models/train.py
```

### Frontend Verification

```bash
# Test web frontend
curl http://localhost:3000

# Check for 200 OK response
```

---

## Deployment Options

### Platform-Specific Installation

| OS / Platform     | Installation Command                                                              | Notes                       |
| ----------------- | --------------------------------------------------------------------------------- | --------------------------- |
| **Ubuntu/Debian** | `sudo apt-get install python3.9 python3-pip && pip install -r requirements.txt`   | Use system package manager  |
| **CentOS/RHEL**   | `sudo yum install python39 python39-pip && pip install -r requirements.txt`       | May require EPEL repository |
| **macOS**         | `brew install python@3.9 && pip install -r requirements.txt`                      | Requires Homebrew           |
| **Windows**       | Download Python installer from python.org, then `pip install -r requirements.txt` | Use PowerShell or CMD       |
| **Docker**        | `docker-compose up -d`                                                            | Cross-platform, recommended |
| **Kubernetes**    | `kubectl apply -f infrastructure/kubernetes/`                                     | Production environments     |

### Cloud Deployment

#### AWS Deployment

```bash
cd infrastructure/terraform/aws
terraform init
terraform plan
terraform apply
```

#### Google Cloud Platform

```bash
cd infrastructure/terraform/gcp
terraform init
terraform plan
terraform apply
```

#### Azure Deployment

```bash
cd infrastructure/terraform/azure
terraform init
terraform plan
terraform apply
```

---

## Troubleshooting Installation

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`

```bash
# Solution: Ensure virtual environment is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt
```

**Issue**: `Port 8000 already in use`

```bash
# Solution: Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

**Issue**: `Database connection failed`

```bash
# Solution: Check database is running and credentials are correct
# For PostgreSQL:
sudo systemctl status postgresql
# Check DATABASE_URL in .env file
```

For more issues, see [Troubleshooting Guide](TROUBLESHOOTING.md).

---

## Next Steps

After successful installation:

1. **[Configure Your System](CONFIGURATION.md)** - Set up environment variables and config files
2. **[Follow Usage Guide](USAGE.md)** - Learn common workflows and operations
3. **[Explore API Reference](API.md)** - Start making API calls
4. **[Review Examples](examples/)** - See working code samples

---

**Need Help?** Open an issue on [GitHub](https://github.com/abrar2030/Fluxora/issues) or check the [Troubleshooting Guide](TROUBLESHOOTING.md).
