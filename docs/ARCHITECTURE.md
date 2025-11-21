# System Architecture

## Overview

Fluxora follows a modern, scalable architecture designed for maintainability and performance. The system is divided into several key components that work together to provide a robust application. The project has recently undergone restructuring to consolidate shared functionalities and improve modularity.

## System Components

### 1. Frontend Layer (Conceptual - Not Implemented in Detail)

- **Technology**: Assumed to be a React-based web application (as per `web-frontend` structure).
- **Key Features**:
  - Responsive UI components
  - State management
  - API integration
  - Client-side routing
- **Directory**: `web-frontend/` (Contains placeholders, not fully implemented)

### 2. Mobile Frontend Layer (Conceptual - Not Implemented)

- **Technology**: Assumed to be a React Native or similar mobile application.
- **Key Features**: Mobile-specific UI, native integrations.
- **Directory**: `mobile-frontend/` (Contains placeholders, not fully implemented)

### 3. Backend/Shared Logic Layer

- **Technology**: Python-based modules and utilities.
- **Key Features**:
  - Core business logic (if applicable, currently focused on utilities)
  - Data processing and manipulation utilities
  - Feature engineering and dataset preparation
  - Model interaction (training, prediction - conceptual)
  - Shared utilities for logging, monitoring, configuration, and plotting.
- **Primary Directory**: `packages/shared/` (Consolidated from the previous `src/` and other shared areas)
  - `packages/shared/data/`: Contains `make_dataset.py` for data preparation and `feature_store.py` for a conceptual feature store client.
  - `packages/shared/features/`: Contains `build_features.py` (placeholder) and `feature_engineering.py` (placeholder).
  - `packages/shared/models/`: Contains placeholders for model training (`train.py`), prediction (`predict.py`), tuning (`tune_hyperparams.py`), selection (`model_selector.py`), and versioning (`model_versioning.py`).
  - `packages/shared/utils/`: Contains core utilities like `alert_handler.py`, `config.py`, `logger.py`, and `monitoring.py` (system resource monitoring).
  - `packages/shared/visualization/`: Contains `plot_utils.py` for generating various plots.

### 4. Monitoring and Tools Layer

- **Components**:
  - Scripts for monitoring model performance and data drift.
  - Example Grafana dashboard configuration.
- **Key Features**:
  - Data drift detection using Evidently (`tools/monitoring/drift_detection.py`).
  - Performance metric collection using Prometheus client (`tools/monitoring/performance.py`).
  - Placeholder for Grafana dashboards (`tools/monitoring/grafana/dashboard.json`).
- **Directory**: `tools/monitoring/` (Consolidated from the previous `monitoring/`)

### 5. Notebooks and Experimentation

- **Components**:
  - Jupyter notebooks for data exploration, model experimentation, and visualization.
  - Utility scripts for notebook environments.
- **Key Features**:
  - Interactive data analysis.
  - Rapid prototyping of models.
  - Visualization of results.
- **Directory**: `notebooks/` (Contains example notebooks and `notebooks/utilities/plot_helpers.py` - which might be redundant with `packages/shared/visualization/plot_utils.py` and should be reviewed for consolidation).

## Data Flow (Conceptual)

### Request Flow (If a full application with API was present)

1. Client request (Web/Mobile) -> API Gateway (if used)
2. API Gateway -> Backend Services (e.g., FastAPI/Flask app using `packages/shared` logic)
3. Backend Services -> Data Layer / Feature Store
4. Response flows back through the same path.

### Data Processing Flow (ML Pipeline Focus)

1. Data ingestion (handled by `packages/shared/data/make_dataset.py` or external scripts).
2. Feature Engineering (conceptualized in `packages/shared/features/`).
3. Feature Storage/Retrieval (`packages/shared/data/feature_store.py`).
4. Model Training (`packages/shared/models/train.py`).
5. Model Prediction (`packages/shared/models/predict.py`).
6. Monitoring for Drift and Performance (`tools/monitoring/`).

## Security Architecture (Conceptual - Standard Practices)

### Authentication (If applicable)

- JWT-based authentication for APIs.
- OAuth 2.0 integration.
- Role-based access control.

### Data Security

- Encryption at rest and in transit.
- Secure key management.
- Secure handling of sensitive data in configurations and logs (leveraging the logger for appropriate levels).

## Scalability Considerations (Conceptual)

### Horizontal Scaling

- Stateless services if backend APIs are developed.
- Load balancing.

### Vertical Scaling

- Resource optimization in data processing and model serving.
- Efficient use of libraries like Pandas/Numpy.

## Monitoring and Logging (Implemented)

### System Monitoring

- **Application Metrics**: Custom metrics for model performance, API requests, and latency are exposed via Prometheus client in `tools/monitoring/performance.py`.
- **Data Drift**: Detected using `tools/monitoring/drift_detection.py` with Evidently, with alerts via `packages/shared/utils/alert_handler.py`.
- **System Resources**: Monitored by `packages/shared/utils/monitoring.py` (CPU, memory, disk).

### Logging

- **Structured Logging**: Implemented via `packages/shared/utils/logger.py`, providing configurable and consistent logging across modules.
- **Log Aggregation**: (External setup) Logs can be directed to files or stdout for collection by systems like ELK stack or Splunk.
- **Error Tracking**: Alerts for critical errors are handled by `packages/shared/utils/alert_handler.py`.

## Deployment Architecture (Conceptual)

### Environments

- Development, Staging, Production (standard practice).

### CI/CD Pipeline

- Automated testing, building, and deployment (standard practice).

## Technology Stack (Current & Assumed)

### Core & Utilities (Python)

- Pandas, NumPy for data manipulation.
- Scikit-learn for ML tasks (metrics, model splitting).
- Evidently for data drift detection.
- Prometheus Client for metrics.
- Matplotlib, Seaborn for plotting.

### Frontend (Assumed/Placeholder)

- React, Redux/Context API, CSS Modules/Styled Components, Axios.

### Backend API (Conceptual - if built)

- Python, FastAPI/Flask, SQLAlchemy, Pydantic.

### Infrastructure (Conceptual)

- Docker, Kubernetes, Terraform, Cloud Provider (AWS/GCP/Azure).

## Key Changes from Restructuring:

- The `src/` directory has been removed, and its relevant functionalities (data processing, features, models, utils) have been consolidated into `packages/shared/`.
- The `monitoring/` directory has been removed, and its contents merged into `tools/monitoring/`.
- Empty placeholder directories like `packages/ui/` and `packages/utils/` (top-level) have been removed.
- Utility scripts for logging, configuration, alert handling, system monitoring, data creation, feature storage, and plotting have been significantly enhanced or newly implemented within `packages/shared/`.
- Monitoring scripts in `tools/monitoring/` (`drift_detection.py`, `performance.py`) have been made more robust and integrated with the shared utilities.

## Additional Resources

- [Project Overview](PROJECT_OVERVIEW.md)
- [Development Guidelines](DEVELOPMENT_GUIDELINES.md)
- [API Documentation](API_DOCS.md) (Needs review for relevance to current structure)
- [Setup Guide](SETUP_GUIDE.md) (Needs review for relevance to current structure)
