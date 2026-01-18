# Architecture Overview

System architecture, design patterns, and component interaction for Fluxora.

---

## 📑 Table of Contents

- [High-Level Architecture](#high-level-architecture)
- [System Components](#system-components)
- [Data Flow](#data-flow)
- [Module Structure](#module-structure)
- [Design Patterns](#design-patterns)
- [Technology Stack](#technology-stack)
- [Security Architecture](#security-architecture)
- [Scalability & Performance](#scalability--performance)

---

## High-Level Architecture

Fluxora follows a layered architecture with clear separation of concerns.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Web Frontend │  │ Mobile App   │  │  API Clients │          │
│  │  (React)     │  │ (React Native)│  │  (3rd Party) │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Load Balancer │
                    │   (Nginx/K8s)   │
                    └────────┬────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                    Application Layer                              │
│                    ┌────────▼────────┐                           │
│                    │   FastAPI App   │                           │
│                    │  (Main Entry)   │                           │
│                    └────────┬────────┘                           │
│                             │                                     │
│    ┌────────────────────────┼────────────────────────┐          │
│    │           │             │             │          │          │
│ ┌──▼──┐   ┌───▼───┐   ┌────▼────┐   ┌───▼───┐  ┌──▼──┐       │
│ │Auth │   │ Data  │   │Predict  │   │Analytics│ │Health│       │
│ │ API │   │  API  │   │   API   │   │   API   │ │Check │       │
│ └──┬──┘   └───┬───┘   └────┬────┘   └───┬────┘ └──┬───┘       │
└────┼──────────┼────────────┼─────────────┼─────────┼───────────┘
     │          │            │             │         │
┌────┼──────────┼────────────┼─────────────┼─────────┼───────────┐
│    │     Business Logic / Domain Layer  │         │            │
│ ┌──▼──────┐  ┌───────────┐  ┌──────────▼────┐    │            │
│ │Security │  │   CRUD    │  │  ML Models    │    │            │
│ │         │  │Operations │  │ (Train/Predict)│    │            │
│ └─────────┘  └─────┬─────┘  └───────┬───────┘    │            │
│                    │                 │            │            │
│              ┌─────▼──────┐   ┌──────▼──────┐     │            │
│              │  Feature   │   │Model Manager│     │            │
│              │Engineering │   │  & Registry │     │            │
│              └─────┬──────┘   └──────┬──────┘     │            │
└────────────────────┼─────────────────┼────────────┼───────────┘
                     │                 │            │
┌────────────────────┼─────────────────┼────────────┼───────────┐
│               Infrastructure Layer   │            │            │
│    ┌─────────────┐    ┌──────────────▼──┐   ┌────▼──────┐    │
│    │ PostgreSQL  │    │  Feature Store  │   │   Redis   │    │
│    │  Database   │    │   (Feast-like)  │   │   Cache   │    │
│    └─────────────┘    └─────────────────┘   └───────────┘    │
│                                                                │
│    ┌─────────────┐    ┌─────────────────┐   ┌───────────┐    │
│    │   MLflow    │    │    Prometheus   │   │   Loki    │    │
│    │  Tracking   │    │    Metrics      │   │   Logs    │    │
│    └─────────────┘    └─────────────────┘   └───────────┘    │
└────────────────────────────────────────────────────────────────┘
```

---

## System Components

### Frontend Components

| Component         | Technology         | Port | Purpose                                   |
| ----------------- | ------------------ | ---- | ----------------------------------------- |
| **Web Dashboard** | React, Node.js     | 3000 | Interactive web UI for data visualization |
| **Mobile App**    | React Native, Expo | N/A  | iOS/Android mobile access                 |
| **Admin Panel**   | React              | 3000 | System administration interface           |

### Backend Components

| Component             | Technology               | Port | Purpose                               |
| --------------------- | ------------------------ | ---- | ------------------------------------- |
| **API Server**        | FastAPI, Python          | 8000 | REST API for all operations           |
| **Auth Service**      | JWT, OAuth2              | 8000 | User authentication and authorization |
| **Prediction Engine** | scikit-learn, TensorFlow | 8000 | ML model serving                      |
| **Analytics Engine**  | Pandas, NumPy            | 8000 | Data aggregation and analysis         |

### Data Components

| Component            | Technology          | Port | Purpose                       |
| -------------------- | ------------------- | ---- | ----------------------------- |
| **Primary Database** | PostgreSQL          | 5432 | Persistent data storage       |
| **Cache Layer**      | Redis               | 6379 | Session and query caching     |
| **Feature Store**    | Custom (Feast-like) | N/A  | ML feature management         |
| **Time-series DB**   | Planned (InfluxDB)  | N/A  | Future: Optimized time-series |

### ML Components

| Component                 | Technology               | Port | Purpose                       |
| ------------------------- | ------------------------ | ---- | ----------------------------- |
| **Training Pipeline**     | scikit-learn, TensorFlow | N/A  | Model training                |
| **Model Registry**        | MLflow                   | 5000 | Model versioning and tracking |
| **Feature Engineering**   | Pandas, NumPy            | N/A  | Feature extraction            |
| **Hyperparameter Tuning** | Optuna                   | N/A  | Automated optimization        |

### Infrastructure Components

| Component             | Technology          | Port       | Purpose                      |
| --------------------- | ------------------- | ---------- | ---------------------------- |
| **Container Runtime** | Docker              | N/A        | Application containerization |
| **Orchestration**     | Kubernetes          | N/A        | Container management         |
| **IaC**               | Terraform           | N/A        | Infrastructure provisioning  |
| **CI/CD**             | GitHub Actions      | N/A        | Automated deployment         |
| **Monitoring**        | Prometheus, Grafana | 9090, 3000 | System observability         |

---

## Data Flow

### Prediction Request Flow

```
1. Client Request
   │
   ├─→ API Gateway (FastAPI)
   │
   ├─→ Authentication Middleware
   │   └─→ JWT Token Validation
   │
   ├─→ Prediction Controller (/v1/predictions/)
   │   │
   │   ├─→ Load Historical Data (Database)
   │   │
   │   ├─→ Feature Engineering
   │   │   ├─→ Extract Time Features
   │   │   ├─→ Calculate Lag Features
   │   │   └─→ Compute Rolling Statistics
   │   │
   │   ├─→ Load ML Model (JobLib/MLflow)
   │   │
   │   ├─→ Make Predictions
   │   │   └─→ Apply Model to Features
   │   │
   │   └─→ Format Response
   │       └─→ Add Confidence Intervals
   │
   └─→ Return JSON Response
```

### Data Ingestion Flow

```
1. Data Source
   │
   ├─→ API Endpoint (POST /v1/data/)
   │
   ├─→ Request Validation (Pydantic)
   │   ├─→ Schema Validation
   │   └─→ Data Quality Checks
   │
   ├─→ Business Logic
   │   ├─→ User Authorization Check
   │   └─→ Data Transformation
   │
   ├─→ Database Layer
   │   ├─→ ORM (SQLAlchemy)
   │   └─→ Write to PostgreSQL
   │
   ├─→ Cache Update (Redis)
   │   └─→ Invalidate Related Queries
   │
   └─→ Success Response
```

### Model Training Flow

```
1. Trigger Training (CLI/Scheduled)
   │
   ├─→ Data Extraction
   │   └─→ Query Database for Training Data
   │
   ├─→ Data Preprocessing
   │   ├─→ Handle Missing Values
   │   ├─→ Remove Outliers
   │   └─→ Feature Engineering
   │
   ├─→ Train/Test Split
   │
   ├─→ Model Training
   │   ├─→ Fit Model (RF/XGBoost/LSTM)
   │   └─→ Hyperparameter Optimization (Optuna)
   │
   ├─→ Model Evaluation
   │   ├─→ Calculate Metrics (MSE, R2)
   │   └─→ Validate Performance
   │
   ├─→ Model Persistence
   │   ├─→ Save Model File (.joblib)
   │   └─→ Register in MLflow
   │
   └─→ Deploy Model
       └─→ Update Production Model
```

---

## Module Structure

### Directory Organization

```
Fluxora/
├── code/                      # Main application code
│   ├── api/                   # API routes and endpoints
│   │   └── v1/               # API version 1
│   │       ├── auth.py       # Authentication endpoints
│   │       ├── data.py       # Data management endpoints
│   │       ├── predictions.py # Prediction endpoints
│   │       └── analytics.py  # Analytics endpoints
│   ├── backend/              # Backend services
│   │   ├── app.py           # FastAPI application
│   │   ├── database.py      # Database connection
│   │   ├── security.py      # Auth & security
│   │   └── middleware.py    # Custom middleware
│   ├── core/                # Cross-cutting concerns
│   │   ├── circuit_breaker.py # Fault tolerance
│   │   ├── retry.py         # Retry logic
│   │   ├── logging_framework.py # Logging
│   │   ├── metrics.py       # Prometheus metrics
│   │   └── health_check.py  # Health checks
│   ├── models/              # ML models
│   │   ├── train.py         # Training pipeline
│   │   ├── predict.py       # Prediction service
│   │   └── model_versioning.py # Version management
│   ├── features/            # Feature engineering
│   │   └── feature_store.py # Feature management
│   ├── data/                # Data processing
│   │   └── features/        # Feature extraction
│   │       └── feature_engineering.py
│   ├── crud/                # Database operations
│   │   └── data.py          # Data CRUD
│   ├── schemas/             # Pydantic models
│   │   └── user.py          # User schema
│   └── visualization/       # Data visualization
│       └── plot_utils.py    # Plotting utilities
├── config/                  # Configuration files
│   ├── config.yaml         # Main config
│   └── preprocessing.yaml  # Preprocessing config
├── infrastructure/         # Infrastructure as Code
│   ├── terraform/          # Cloud provisioning
│   ├── kubernetes/         # K8s manifests
│   ├── ansible/            # Configuration management
│   └── monitoring/         # Monitoring configs
├── tests/                  # Test suites
│   ├── test_api.py        # API tests
│   ├── test_models.py     # Model tests
│   └── conftest.py        # Test fixtures
├── web-frontend/          # React web app
├── mobile-frontend/       # React Native app
├── scripts/               # Utility scripts
├── notebooks/             # Jupyter notebooks
└── docs/                  # Documentation
```

### Module Dependencies

```python
# High-level dependency graph
main.py
├── api.v1
│   ├── auth (→ backend.security)
│   ├── data (→ crud.data, backend.database)
│   ├── predictions (→ models.predict, features)
│   └── analytics (→ crud.data, pandas)
├── backend
│   ├── database (→ sqlalchemy)
│   ├── security (→ jwt, passlib)
│   └── middleware (→ core.logging)
├── core
│   ├── circuit_breaker
│   ├── retry
│   ├── metrics (→ prometheus_client)
│   └── logging_framework
├── models
│   ├── train (→ features, sklearn)
│   ├── predict (→ joblib, features)
│   └── model_versioning (→ mlflow)
└── features
    └── feature_store
```

---

## Design Patterns

### 1. Layered Architecture

**Purpose:** Separation of concerns and maintainability

**Layers:**

- **Presentation:** API endpoints, request/response handling
- **Application:** Business logic, orchestration
- **Domain:** Core entities, ML models, feature engineering
- **Infrastructure:** Database, cache, external services

### 2. Repository Pattern

**Location:** `code/crud/`

**Purpose:** Abstract data access logic

```python
# Example: Data repository
class DataRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int):
        return self.db.query(EnergyData).filter_by(id=id).first()

    def get_by_time_range(self, start, end):
        return self.db.query(EnergyData).filter(
            EnergyData.timestamp.between(start, end)
        ).all()
```

### 3. Circuit Breaker Pattern

**Location:** `code/core/circuit_breaker.py`

**Purpose:** Prevent cascading failures

```python
@CircuitBreaker(failure_threshold=5, recovery_timeout=30)
def external_api_call():
    # Protected function
    pass
```

### 4. Dependency Injection

**Location:** `code/backend/dependencies.py`

**Purpose:** Loose coupling and testability

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoint
@app.get("/data")
def get_data(db: Session = Depends(get_db)):
    return db.query(EnergyData).all()
```

### 5. Strategy Pattern

**Location:** `code/models/model_selector.py`

**Purpose:** Interchangeable ML models

```python
class ModelStrategy:
    def train(self, data): pass
    def predict(self, data): pass

class XGBoostStrategy(ModelStrategy):
    def train(self, data): ...
    def predict(self, data): ...

class LSTMStrategy(ModelStrategy):
    def train(self, data): ...
    def predict(self, data): ...
```

### 6. SAGA Pattern

**Location:** `code/core/saga_orchestrator.py`

**Purpose:** Distributed transaction management

```python
class SagaOrchestrator:
    def execute(self, steps):
        for step in steps:
            try:
                step.execute()
            except Exception:
                step.compensate()  # Rollback
                raise
```

---

## Technology Stack

### Backend Stack

```yaml
Runtime:
  - Python: 3.9+
  - FastAPI: 0.95.2
  - Uvicorn: 0.22.0

Data Processing:
  - Pandas: 1.4.4
  - NumPy: (implicit)
  - SQLAlchemy: (via FastAPI)

Machine Learning:
  - TensorFlow: 2.12.0
  - XGBoost: 1.7.5
  - scikit-learn: 1.2.2
  - Prophet: 1.1.3

MLOps:
  - MLflow: 2.4.0
  - Optuna: 3.2.0
  - DVC: 3.29.0
  - Prefect: 2.10.5
  - Feast: 0.31.0

Database & Cache:
  - PostgreSQL: 13+
  - Redis: 6+
  - SQLAlchemy: ORM

Monitoring:
  - Prometheus: prometheus-client 0.17.0
  - Evidently: 0.3.0
```

### Frontend Stack

```yaml
Web Frontend:
  - Node.js: 16+
  - React: Latest
  - Package Manager: npm

Mobile Frontend:
  - React Native
  - Expo: Latest
  - Package Manager: npm
```

### Infrastructure Stack

```yaml
Containerization:
  - Docker: 20.10+
  - Docker Compose: 1.29+

Orchestration:
  - Kubernetes: 1.20+
  - Helm: (optional)

Infrastructure as Code:
  - Terraform: 1.0+
  - Ansible: 2.10+

CI/CD:
  - GitHub Actions
  - Pre-commit hooks

Monitoring:
  - Prometheus
  - Grafana
  - Loki
  - Alertmanager
```

---

## Security Architecture

### Authentication Flow

```
1. User Login Request
   ├─→ POST /v1/auth/login (username, password)
   │
2. Password Verification
   ├─→ Hash password with bcrypt
   ├─→ Compare with stored hash
   │
3. Token Generation
   ├─→ Create JWT payload (user_id, email, exp)
   ├─→ Sign with SECRET_KEY (HS256)
   │
4. Return Token
   └─→ {"access_token": "eyJ...", "token_type": "bearer"}

5. Subsequent Requests
   ├─→ Header: Authorization: Bearer eyJ...
   ├─→ Verify signature
   ├─→ Check expiration
   └─→ Extract user_id → Authorize request
```

### Security Layers

| Layer                | Mechanism             | Implementation       |
| -------------------- | --------------------- | -------------------- |
| **Transport**        | HTTPS/TLS             | Nginx/Load Balancer  |
| **Authentication**   | JWT tokens            | FastAPI Security     |
| **Authorization**    | Role-based            | Dependency injection |
| **Input Validation** | Pydantic models       | FastAPI validation   |
| **SQL Injection**    | ORM parameterization  | SQLAlchemy           |
| **CORS**             | Origin whitelist      | FastAPI middleware   |
| **Rate Limiting**    | Request throttling    | Custom middleware    |
| **Secrets**          | Environment variables | .env files, Vault    |

---

## Scalability & Performance

### Horizontal Scaling

```yaml
API Layer:
  - Stateless design
  - Load balancer distribution
  - Kubernetes HPA (CPU/Memory based)
  - Target: Handle 1000+ req/s

Database Layer:
  - Read replicas for queries
  - Write to primary
  - Connection pooling
  - Query optimization

Cache Layer:
  - Redis cluster
  - Cache-aside pattern
  - TTL-based invalidation
```

### Performance Optimizations

| Technique              | Implementation                | Benefit                        |
| ---------------------- | ----------------------------- | ------------------------------ |
| **Database Indexing**  | Indexes on timestamp, user_id | 10x query speedup              |
| **Connection Pooling** | SQLAlchemy pool_size=20       | Reduced connection overhead    |
| **Caching**            | Redis for frequent queries    | 100x response time improvement |
| **Async I/O**          | FastAPI async endpoints       | Handle concurrent requests     |
| **Model Caching**      | In-memory model loading       | Avoid disk I/O per request     |
| **Batch Prediction**   | Process multiple inputs       | Efficient GPU/CPU utilization  |
| **Query Optimization** | Eager loading, pagination     | Reduced data transfer          |

### Monitoring & Observability

```
Metrics Collection:
  - Prometheus scrapes /metrics endpoint
  - Custom metrics: request_duration, prediction_latency
  - System metrics: CPU, memory, disk

Logging:
  - Structured JSON logs
  - Loki aggregation
  - Log levels: DEBUG, INFO, WARNING, ERROR

Tracing:
  - Request ID propagation
  - Distributed tracing (planned: Jaeger)
  - Correlate logs across services

Alerting:
  - Prometheus alert rules
  - Alertmanager routing
  - Channels: Email, Slack, PagerDuty
```

---

## Next Steps

- **[Feature Matrix](FEATURE_MATRIX.md)** - All features and capabilities
- **[API Reference](API.md)** - API endpoint details
- **[Configuration](CONFIGURATION.md)** - System configuration
- **[Examples](examples/)** - Working code examples

---

**Need Help?** Check [Troubleshooting](TROUBLESHOOTING.md) or open an issue on [GitHub](https://github.com/quantsingularity/Fluxora/issues).
