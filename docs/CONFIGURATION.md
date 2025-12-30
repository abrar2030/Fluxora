# Configuration Guide

Complete configuration reference for Fluxora, covering environment variables, configuration files, and deployment settings.

---

## 📑 Table of Contents

- [Environment Variables](#environment-variables)
- [Configuration Files](#configuration-files)
- [Database Configuration](#database-configuration)
- [Model Configuration](#model-configuration)
- [API Configuration](#api-configuration)
- [Monitoring Configuration](#monitoring-configuration)
- [Deployment Configuration](#deployment-configuration)

---

## Environment Variables

Environment variables control runtime behavior and should be set in `.env` file or system environment.

### Core Environment Variables

| Option         | Type    | Default                  | Description                       | Where to Set    |
| -------------- | ------- | ------------------------ | --------------------------------- | --------------- |
| `DATABASE_URL` | string  | `sqlite:///./fluxora.db` | Database connection string        | `.env` file     |
| `SECRET_KEY`   | string  | _required_               | JWT signing secret (min 32 chars) | `.env` file     |
| `ENVIRONMENT`  | string  | `development`            | Deployment environment            | `.env` / System |
| `LOG_LEVEL`    | string  | `INFO`                   | Logging level                     | `.env` file     |
| `DEBUG`        | boolean | `false`                  | Enable debug mode                 | `.env` file     |
| `API_PORT`     | integer | `8000`                   | API server port                   | `.env` file     |
| `API_HOST`     | string  | `0.0.0.0`                | API server host                   | `.env` file     |

### Security Variables

| Option                     | Type    | Default                 | Description                            | Where to Set    |
| -------------------------- | ------- | ----------------------- | -------------------------------------- | --------------- |
| `SECRET_KEY`               | string  | _required_              | Secret for token signing               | `.env` (secure) |
| `ACCESS_TOKEN_EXPIRE_DAYS` | integer | `30`                    | Token expiration in days               | `.env` file     |
| `CORS_ORIGINS`             | string  | `http://localhost:3000` | Allowed CORS origins (comma-separated) | `.env` file     |
| `ALLOWED_HOSTS`            | string  | `*`                     | Allowed host headers                   | `.env` file     |

### Database Variables

| Option               | Type    | Default     | Description              | Where to Set    |
| -------------------- | ------- | ----------- | ------------------------ | --------------- |
| `POSTGRES_USER`      | string  | `postgres`  | PostgreSQL username      | `.env` / Docker |
| `POSTGRES_PASSWORD`  | string  | _required_  | PostgreSQL password      | `.env` (secure) |
| `POSTGRES_HOST`      | string  | `localhost` | PostgreSQL host          | `.env` file     |
| `POSTGRES_PORT`      | integer | `5432`      | PostgreSQL port          | `.env` file     |
| `POSTGRES_DB`        | string  | `fluxora`   | PostgreSQL database name | `.env` file     |
| `DATABASE_POOL_SIZE` | integer | `5`         | Connection pool size     | `.env` file     |

### Redis Variables

| Option           | Type    | Default     | Description               | Where to Set    |
| ---------------- | ------- | ----------- | ------------------------- | --------------- |
| `REDIS_HOST`     | string  | `localhost` | Redis server host         | `.env` file     |
| `REDIS_PORT`     | integer | `6379`      | Redis server port         | `.env` file     |
| `REDIS_PASSWORD` | string  | `null`      | Redis password (optional) | `.env` (secure) |
| `REDIS_DB`       | integer | `0`         | Redis database number     | `.env` file     |

### ML/MLOps Variables

| Option                | Type   | Default                  | Description               | Where to Set |
| --------------------- | ------ | ------------------------ | ------------------------- | ------------ |
| `MLFLOW_TRACKING_URI` | string | `http://localhost:5000`  | MLflow server URL         | `.env` file  |
| `MODEL_PATH`          | string | `./fluxora_model.joblib` | Model file path           | `.env` file  |
| `FEATURE_STORE_PATH`  | string | `./config/feature_store` | Feature store config path | `.env` file  |
| `DVC_REMOTE`          | string | `s3://bucket/path`       | DVC remote storage        | `.env` file  |

### Monitoring Variables

| Option            | Type    | Default          | Description               | Where to Set |
| ----------------- | ------- | ---------------- | ------------------------- | ------------ |
| `PROMETHEUS_PORT` | integer | `9090`           | Prometheus port           | `.env` file  |
| `GRAFANA_PORT`    | integer | `3000`           | Grafana port              | `.env` file  |
| `LOKI_HOST`       | string  | `localhost:3100` | Loki log aggregator       | `.env` file  |
| `METRICS_ENABLED` | boolean | `true`           | Enable Prometheus metrics | `.env` file  |

### Example `.env` File

```bash
# Core Settings
ENVIRONMENT=development
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
LOG_LEVEL=INFO
DEBUG=false

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Database (SQLite - Development)
DATABASE_URL=sqlite:///./fluxora.db

# Database (PostgreSQL - Production)
# DATABASE_URL=postgresql://user:password@localhost:5432/fluxora
# POSTGRES_USER=fluxora_user
# POSTGRES_PASSWORD=secure_password_here
# POSTGRES_HOST=db
# POSTGRES_PORT=5432
# POSTGRES_DB=fluxora

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MODEL_PATH=./fluxora_model.joblib

# Feature Store
FEATURE_STORE_PATH=./config/feature_store

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
METRICS_ENABLED=true
```

---

## Configuration Files

### Main Configuration File

**Location:** `config/config.yaml`

**Purpose:** Main configuration for models, data pipelines, and features

```yaml
# Default configurations
defaults:
  - preprocessing: default
  - model: xgboost

# Model configurations
model:
  xgboost:
    n_estimators: 500
    learning_rate: 0.05
    max_depth: 8
    min_child_weight: 3
    subsample: 0.8
    colsample_bytree: 0.8

  lstm:
    units: 128
    dropout: 0.2
    recurrent_dropout: 0.2
    epochs: 50
    batch_size: 32

  prophet:
    seasonality_mode: multiplicative
    changepoint_prior_scale: 0.05
    yearly_seasonality: true
    weekly_seasonality: true
    daily_seasonality: true

# Data pipeline configuration
data:
  source: s3://energy-data-bucket/raw/
  destination: ./data/processed
  validation:
    max_consumption: 1000 # kWh
    min_consumption: 0
    required_fields:
      - timestamp
      - consumption_kwh

# Feature engineering
features:
  lag_features:
    - 1h
    - 24h
    - 168h # 1 week
  rolling_features:
    windows:
      - 24 # 24 hours
      - 168 # 1 week
    statistics:
      - mean
      - std
      - min
      - max
```

### Preprocessing Configuration

**Location:** `config/preprocessing.yaml`

**Purpose:** Data preprocessing and feature engineering settings

```yaml
preprocessing:
  # Missing value handling
  missing_values:
    strategy: forward_fill # forward_fill, backward_fill, interpolate, drop
    max_missing_consecutive: 3

  # Outlier detection
  outliers:
    method: zscore # zscore, iqr, isolation_forest
    threshold: 3.0
    action: clip # clip, remove, flag

  # Scaling
  scaling:
    method: standard # standard, minmax, robust
    feature_range: [0, 1]

  # Time features
  time_features:
    extract:
      - hour
      - day_of_week
      - month
      - quarter
      - is_weekend
      - is_holiday
```

### Docker Compose Configuration

**Location:** `docker-compose.yml`

```yaml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://fluxora:password@db:5432/fluxora
      - REDIS_HOST=redis
      - ENVIRONMENT=production
    depends_on:
      - db
      - redis
    volumes:
      - ./code:/app/code
      - ./data:/app/data
      - ./config:/app/config

  db:
    image: postgres:13
    environment:
      POSTGRES_USER: fluxora
      POSTGRES_PASSWORD: password
      POSTGRES_DB: fluxora
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  frontend:
    build: ./web-frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - api

volumes:
  postgres_data:
```

---

## Database Configuration

### SQLite Configuration (Development)

```bash
# Simple file-based database
DATABASE_URL=sqlite:///./fluxora.db

# Or with absolute path
DATABASE_URL=sqlite:////home/user/fluxora/code/fluxora.db
```

**Pros:**

- Zero configuration
- Good for development and testing
- Portable single file

**Cons:**

- Not suitable for production
- Limited concurrent access
- No advanced features

### PostgreSQL Configuration (Production)

```bash
# Connection string format
DATABASE_URL=postgresql://username:password@host:port/database

# Example
DATABASE_URL=postgresql://fluxora_user:secure_pass@localhost:5432/fluxora

# With connection pool settings
DATABASE_URL=postgresql://fluxora_user:secure_pass@localhost:5432/fluxora?pool_size=20&max_overflow=10
```

**Connection Pool Settings:**

| Parameter      | Default | Description                         |
| -------------- | ------- | ----------------------------------- |
| `pool_size`    | 5       | Number of connections to maintain   |
| `max_overflow` | 10      | Max connections beyond pool_size    |
| `pool_timeout` | 30      | Seconds to wait for connection      |
| `pool_recycle` | 3600    | Seconds before recycling connection |

**Setup PostgreSQL:**

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create user and database
sudo -u postgres psql
CREATE USER fluxora_user WITH PASSWORD 'secure_password';
CREATE DATABASE fluxora OWNER fluxora_user;
GRANT ALL PRIVILEGES ON DATABASE fluxora TO fluxora_user;
\q

# Test connection
psql -U fluxora_user -d fluxora -h localhost
```

---

## Model Configuration

### Model Selection

Configure which model to use in `config/config.yaml`:

```yaml
defaults:
  - model: xgboost # xgboost, lstm, prophet, random_forest
```

### XGBoost Configuration

```yaml
model:
  xgboost:
    n_estimators: 500 # Number of trees
    learning_rate: 0.05 # Step size shrinkage
    max_depth: 8 # Maximum tree depth
    min_child_weight: 3 # Minimum leaf weight
    subsample: 0.8 # Subsample ratio
    colsample_bytree: 0.8 # Feature sampling ratio
    gamma: 0.1 # Minimum loss reduction
    reg_alpha: 0.1 # L1 regularization
    reg_lambda: 1.0 # L2 regularization
```

### LSTM Configuration

```yaml
model:
  lstm:
    units: 128 # LSTM units per layer
    dropout: 0.2 # Dropout rate
    recurrent_dropout: 0.2 # Recurrent dropout
    layers: 2 # Number of LSTM layers
    epochs: 50 # Training epochs
    batch_size: 32 # Batch size
    validation_split: 0.2 # Validation data ratio
    early_stopping:
      patience: 10
      restore_best_weights: true
```

### Prophet Configuration

```yaml
model:
  prophet:
    seasonality_mode: multiplicative # additive or multiplicative
    changepoint_prior_scale: 0.05 # Trend flexibility
    seasonality_prior_scale: 10.0 # Seasonality strength
    yearly_seasonality: true
    weekly_seasonality: true
    daily_seasonality: true
    holidays:
      country: US
      include_holidays: true
```

---

## API Configuration

### CORS Configuration

```python
# In code/main.py
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://app.fluxora.example.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting Configuration

```python
# Environment variable
RATE_LIMIT_PER_HOUR=1000

# In code (using slowapi or similar)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/v1/predictions/")
@limiter.limit("100/hour")
def get_predictions():
    pass
```

---

## Monitoring Configuration

### Prometheus Configuration

**Location:** `infrastructure/monitoring/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "fluxora-api"
    static_configs:
      - targets: ["api:8000"]
    metrics_path: "/metrics"

  - job_name: "node-exporter"
    static_configs:
      - targets: ["node-exporter:9100"]
```

### Grafana Configuration

**Location:** `infrastructure/monitoring/grafana/datasources.yml`

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
```

### Logging Configuration

```python
# In code/core/logging_framework.py
import logging
import sys

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
```

---

## Deployment Configuration

### Environment-Specific Settings

#### Development

```yaml
# config/environments/development.yaml
environment: development
debug: true
log_level: DEBUG
database_url: sqlite:///./fluxora.db
cors_origins:
  - http://localhost:3000
  - http://localhost:5173
enable_profiling: true
```

#### Staging

```yaml
# config/environments/staging.yaml
environment: staging
debug: false
log_level: INFO
database_url: postgresql://user:pass@staging-db:5432/fluxora
cors_origins:
  - https://staging.fluxora.example.com
enable_profiling: false
rate_limiting: true
```

#### Production

```yaml
# config/environments/production.yaml
environment: production
debug: false
log_level: WARNING
database_url: postgresql://user:pass@prod-db:5432/fluxora
cors_origins:
  - https://app.fluxora.example.com
enable_profiling: false
rate_limiting: true
ssl_required: true
```

### Kubernetes Configuration

**Location:** `infrastructure/kubernetes/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fluxora-api
  namespace: fluxora
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fluxora-api
  template:
    metadata:
      labels:
        app: fluxora-api
    spec:
      containers:
        - name: api
          image: fluxora/api:latest
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: fluxora-secrets
                  key: database-url
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
```

---

## Configuration Best Practices

### Security

1. **Never commit secrets to version control**

   ```bash
   # Add to .gitignore
   .env
   *.env
   secrets/
   ```

2. **Use environment variables for sensitive data**

   ```bash
   export SECRET_KEY=$(openssl rand -hex 32)
   export DATABASE_URL="postgresql://..."
   ```

3. **Rotate secrets regularly**
   - Access tokens: Every 30-90 days
   - Database passwords: Every 90 days
   - API keys: As needed

### Performance

1. **Configure connection pooling**

   ```python
   DATABASE_POOL_SIZE=20
   DATABASE_MAX_OVERFLOW=10
   ```

2. **Enable caching**

   ```python
   REDIS_ENABLED=true
   CACHE_TTL=3600
   ```

3. **Optimize model serving**
   ```python
   MODEL_CACHE_SIZE=5
   PREDICTION_BATCH_SIZE=32
   ```

### Reliability

1. **Configure health checks**

   ```yaml
   livenessProbe:
     httpGet:
       path: /health
       port: 8000
     initialDelaySeconds: 30
     periodSeconds: 10
   ```

2. **Set resource limits**

   ```yaml
   resources:
     limits:
       memory: "1Gi"
       cpu: "1000m"
   ```

3. **Enable monitoring**
   ```bash
   METRICS_ENABLED=true
   PROMETHEUS_PORT=9090
   ```

---

## Next Steps

- **[API Reference](API.md)** - API endpoint configuration
- **[CLI Reference](CLI.md)** - Command-line configuration
- **[Troubleshooting](TROUBLESHOOTING.md)** - Configuration issues
- **[Examples](examples/)** - Configuration examples

---

**Need Help?** Check [Troubleshooting](TROUBLESHOOTING.md) or open an issue on [GitHub](https://github.com/abrar2030/Fluxora/issues).
