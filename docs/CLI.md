# CLI Reference

Command-line interface reference for Fluxora, including Make commands, Python scripts, and utility tools.

---

## 📑 Table of Contents

- [Make Commands](#make-commands)
- [Python Scripts](#python-scripts)
- [Infrastructure Commands](#infrastructure-commands)
- [Development Commands](#development-commands)
- [Utility Scripts](#utility-scripts)

---

## Make Commands

Fluxora provides convenient Make targets for common operations. All commands should be run from the repository root.

### Installation & Setup Commands

| Command        | Arguments | Description                                           | Example        |
| -------------- | --------- | ----------------------------------------------------- | -------------- |
| `make install` | None      | Install all Python dependencies and configure Prefect | `make install` |

**Details:**

```bash
make install
```

Performs:

- Installs all packages from `requirements.txt`
- Configures Prefect API URL for workflow orchestration
- Verifies installation success

---

### Data Pipeline Commands

| Command     | Arguments | Description                               | Example     |
| ----------- | --------- | ----------------------------------------- | ----------- |
| `make data` | None      | Run ETL pipeline to prepare training data | `make data` |

**Details:**

```bash
make data
```

Performs:

- Loads raw data from configured source
- Applies data validation and cleaning
- Performs feature engineering
- Saves processed data to destination folder

**Configuration:** Edit `config/config.yaml` to customize data sources

---

### Model Training Commands

| Command      | Arguments | Description                       | Example      |
| ------------ | --------- | --------------------------------- | ------------ |
| `make train` | None      | Train machine learning models     | `make train` |
| `make tune`  | None      | Hyperparameter tuning with Optuna | `make tune`  |

**Train Command:**

```bash
make train
```

Performs:

- Loads processed training data
- Trains RandomForest model
- Evaluates model performance
- Saves model to `code/fluxora_model.joblib`

**Output:**

```
[INFO] Starting training pipeline...
[INFO] Model Training Complete. MSE: 12.3456, R2: 0.8901
[INFO] Model saved to fluxora_model.joblib
```

**Tune Command:**

```bash
make tune
```

Performs:

- Runs hyperparameter optimization with Optuna
- Tests multiple parameter combinations
- Stores results in MLflow
- Saves best model configuration

---

### Deployment Commands

| Command       | Arguments | Description                          | Example       |
| ------------- | --------- | ------------------------------------ | ------------- |
| `make deploy` | None      | Build and deploy with Docker Compose | `make deploy` |

**Details:**

```bash
make deploy
```

Performs:

- Builds Docker images from scratch (no cache)
- Starts all services in detached mode
- Includes: API, database, Redis, frontends

**Services Started:**

- `fluxora-api` - Backend API server (port 8000)
- `fluxora-db` - PostgreSQL database
- `fluxora-redis` - Redis cache
- `fluxora-frontend` - Web dashboard (port 3000)

---

### Monitoring Commands

| Command        | Arguments | Description                                  | Example        |
| -------------- | --------- | -------------------------------------------- | -------------- |
| `make monitor` | None      | Start monitoring stack (Prometheus, Prefect) | `make monitor` |

**Details:**

```bash
make monitor
```

Starts:

- Prefect Orion server (workflow orchestration)
- Prometheus (metrics collection)

**Access:**

- Prefect UI: `http://localhost:4200`
- Prometheus: `http://localhost:9090`

---

### Testing Commands

| Command     | Arguments | Description                           | Example     |
| ----------- | --------- | ------------------------------------- | ----------- |
| `make test` | None      | Run complete test suite with coverage | `make test` |

**Details:**

```bash
make test
```

Performs:

- Runs all pytest tests in `tests/` directory
- Generates coverage report for `src/` code
- Creates HTML coverage report in `htmlcov/`

**View Coverage:**

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

### Cleanup Commands

| Command      | Arguments | Description                            | Example      |
| ------------ | --------- | -------------------------------------- | ------------ |
| `make clean` | None      | Remove build artifacts and cache files | `make clean` |

**Details:**

```bash
make clean
```

Removes:

- `*.pyc` compiled Python files
- `__pycache__` directories
- `.pytest_cache` test artifacts
- `.mlruns` MLflow experiments
- `htmlcov/` coverage reports

---

## Python Scripts

### Model Training Script

**Location:** `code/models/train.py`

**Purpose:** Train machine learning models on energy data

**Usage:**

```bash
cd code
python models/train.py
```

**Options:**

```bash
# With experiment name (for MLflow tracking)
python models/train.py --experiment-name=prod_v1
```

**Output Files:**

- `fluxora_model.joblib` - Trained model file
- MLflow logs in `.mlruns/` directory

**Example Output:**

```
[INFO] Starting training pipeline...
[INFO] Loading data from database...
[INFO] Model Training Complete. MSE: 12.3456, R2: 0.8901
[INFO] Model saved to fluxora_model.joblib

Final Metrics:
{
  'mean_squared_error': 12.3456,
  'r2_score': 0.8901,
  'feature_count': 15,
  'training_samples': 576,
  'test_samples': 144
}
```

---

### Hyperparameter Tuning Script

**Location:** `code/models/tune_hyperparams.py`

**Purpose:** Optimize model hyperparameters using Optuna

**Usage:**

```bash
cd code
python models/tune_hyperparams.py --storage=mlruns
```

**Options:**

| Option       | Type    | Default  | Description                   |
| ------------ | ------- | -------- | ----------------------------- |
| `--storage`  | string  | `mlruns` | MLflow storage path           |
| `--n-trials` | integer | `50`     | Number of optimization trials |
| `--timeout`  | integer | `3600`   | Timeout in seconds            |

**Example:**

```bash
python models/tune_hyperparams.py --storage=mlruns --n-trials=100
```

---

### Data Fetching Script

**Location:** `scripts/fetch_realtime_data.py`

**Purpose:** Fetch real-time energy data from external sources

**Usage:**

```bash
cd scripts
python fetch_realtime_data.py
```

**Requirements:**

- WebSocket connection to data provider
- Valid API credentials in environment variables

**Environment Variables:**

```bash
ENERGY_API_URL=wss://realtime-energy.com/ws
ENERGY_API_KEY=your-api-key-here
```

---

### API Server

**Location:** `code/main.py`

**Purpose:** Start FastAPI web server

**Usage:**

```bash
cd code

# Development mode with auto-reload
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Options:**

| Option        | Description                 | Example            |
| ------------- | --------------------------- | ------------------ |
| `--reload`    | Auto-reload on code changes | `--reload`         |
| `--host`      | Bind to host address        | `--host 0.0.0.0`   |
| `--port`      | Listen on port              | `--port 8000`      |
| `--workers`   | Number of worker processes  | `--workers 4`      |
| `--log-level` | Logging level               | `--log-level info` |

**Example Production Start:**

```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level warning \
  --access-log
```

---

## Infrastructure Commands

### Docker Commands

#### Build Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build api

# Build without cache
docker-compose build --no-cache
```

#### Start/Stop Services

```bash
# Start all services in foreground
docker-compose up

# Start in background (detached)
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

#### View Logs

```bash
# Follow all service logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f api

# View last 100 lines
docker-compose logs --tail=100
```

#### Service Management

```bash
# List running services
docker-compose ps

# Restart service
docker-compose restart api

# Execute command in container
docker-compose exec api bash

# View service resource usage
docker stats
```

---

### Kubernetes Commands

#### Deployment

```bash
# Apply all manifests
kubectl apply -f infrastructure/kubernetes/

# Apply specific manifest
kubectl apply -f infrastructure/kubernetes/deployment.yaml

# Delete resources
kubectl delete -f infrastructure/kubernetes/
```

#### Pod Management

```bash
# List pods
kubectl get pods -n fluxora

# Describe pod
kubectl describe pod <pod-name> -n fluxora

# View pod logs
kubectl logs -f <pod-name> -n fluxora

# Execute command in pod
kubectl exec -it <pod-name> -n fluxora -- bash
```

#### Service Management

```bash
# List services
kubectl get services -n fluxora

# Expose service
kubectl expose deployment fluxora-api --type=LoadBalancer --port=8000

# Port forward to local
kubectl port-forward svc/fluxora-api 8000:8000 -n fluxora
```

#### Scaling

```bash
# Scale deployment
kubectl scale deployment fluxora-api --replicas=3 -n fluxora

# Autoscale
kubectl autoscale deployment fluxora-api --min=2 --max=10 --cpu-percent=80
```

#### Status Checks

```bash
# Check deployment status
kubectl rollout status deployment/fluxora-api -n fluxora

# View resource usage
kubectl top pods -n fluxora
kubectl top nodes

# Check events
kubectl get events -n fluxora --sort-by='.lastTimestamp'
```

---

### Terraform Commands

#### AWS Deployment

```bash
cd infrastructure/terraform/aws

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply changes
terraform apply

# Destroy infrastructure
terraform destroy

# Show current state
terraform show

# List resources
terraform state list
```

#### GCP Deployment

```bash
cd infrastructure/terraform/gcp

# Initialize
terraform init

# Apply with variables file
terraform apply -var-file="production.tfvars"
```

#### Azure Deployment

```bash
cd infrastructure/terraform/azure

# Initialize
terraform init

# Plan with target
terraform plan -target=azurerm_resource_group.fluxora

# Apply
terraform apply
```

---

## Development Commands

### Linting & Formatting

```bash
# Run pre-commit hooks
pre-commit run --all-files

# Python linting
pylint code/

# Python formatting
black code/
isort code/

# JavaScript linting
cd web-frontend && npm run lint

# Fix linting issues
cd web-frontend && npm run lint:fix
```

### Database Commands

```bash
# Create database (PostgreSQL)
createdb fluxora

# Run migrations
cd code
alembic upgrade head

# Create new migration
alembic revision -m "Add new table"

# Rollback migration
alembic downgrade -1

# SQLite operations
sqlite3 code/fluxora.db ".schema"
sqlite3 code/fluxora.db "SELECT * FROM users;"
```

### Testing Commands

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest tests/ --cov=code --cov-report=html

# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test_api.py::test_health_check

# Run tests by marker
pytest tests/ -m integration
```

---

## Utility Scripts

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate
deactivate

# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip install --upgrade -r requirements.txt

# Generate requirements
pip freeze > requirements.txt
```

### Data Management

```bash
# Export data to CSV
cd code
python -c "
import pandas as pd
from backend.database import engine
df = pd.read_sql('SELECT * FROM energy_data', engine)
df.to_csv('energy_data.csv', index=False)
"

# Import data from CSV
python -c "
import pandas as pd
from backend.database import engine
df = pd.read_csv('energy_data.csv')
df.to_sql('energy_data', engine, if_exists='append', index=False)
"
```

### Log Management

```bash
# View API logs
tail -f logs/fluxora.log

# Search logs for errors
grep ERROR logs/fluxora.log

# Monitor logs in real-time with filtering
tail -f logs/fluxora.log | grep -E 'ERROR|WARNING'

# Rotate logs
logrotate -f /etc/logrotate.d/fluxora
```

---

## Next Steps

- **[Configuration Guide](CONFIGURATION.md)** - Configure environment variables and settings
- **[API Reference](API.md)** - API endpoint documentation
- **[Examples](examples/)** - Working code examples
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common CLI issues and solutions

---

**Need Help?** Check [Troubleshooting](TROUBLESHOOTING.md) or open an issue on [GitHub](https://github.com/quantsingularity/Fluxora/issues).
