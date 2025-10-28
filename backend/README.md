# Fluxora Backend

## Energy Forecasting Platform - Backend Components and Testing

The `backend` directory is a crucial part of the Fluxora project's testing and deployment infrastructure, primarily housing the comprehensive test suite for the core services. The actual backend application logic, which handles the energy forecasting API, data processing, and machine learning models, is located in the parent directory's `src/` and `packages/` folders.

This document provides an overview of the backend's architecture, technology stack, and how the tests in this directory validate the system.

---

## Table of Contents

- [Overview](#overview)
- [Architecture & Technology Stack](#architecture--technology-stack)
  - [Core Technologies](#core-technologies)
  - [MLOps Components](#mlops-components)
- [Backend Structure](#backend-structure)
- [Test Suite Detail](#test-suite-detail)
  - [Test File Breakdown](#test-file-breakdown)
- [Getting Started](#getting-started)

---

## Overview

The Fluxora backend is built around a **Python-based data science and machine learning pipeline**, exposed via a high-performance **FastAPI** web framework. Its primary function is to ingest energy data, run advanced forecasting models, and serve predictions through a robust API.

## Architecture & Technology Stack

The backend employs a modern, Python-centric stack, heavily leveraging libraries for data manipulation, machine learning, and MLOps.

### Core Technologies

| Category | Technology | Purpose | Key Dependencies |
| :--- | :--- | :--- | :--- |
| **API Framework** | **FastAPI** | High-performance, asynchronous API for serving predictions and managing data. | `fastapi`, `uvicorn` |
| **Data Processing** | **Python** | Core language for all backend logic, data transformation, and model execution. | `numpy`, `pandas` |
| **Machine Learning** | **Scikit-learn, XGBoost, Prophet, TensorFlow** | Implementation of various forecasting models and general-purpose machine learning. | `scikit-learn`, `xgboost`, `prophet`, `tensorflow` |
| **Configuration** | **Hydra** | Manages complex configuration for experiments, models, and deployment environments. | `hydra-core` |

### MLOps Components

The system incorporates several specialized tools to manage the end-to-end Machine Learning Operations (MLOps) lifecycle.

| Component | Tool/Library | Function |
| :--- | :--- | :--- |
| **Workflow Orchestration** | **Prefect** | Defines, schedules, and monitors the data processing and model training pipelines. |
| **Experiment Tracking** | **MLflow** | Logs model parameters, metrics, and artifacts for experiment reproducibility and management. |
| **Data Versioning** | **DVC (Data Version Control)** | Manages versions of datasets and models, ensuring reproducibility across the project. |
| **Feature Store** | **Feast** | Serves features consistently for both training (offline) and inference (online) environments. |
| **Model Monitoring** | **Evidently** | Tracks model drift, data quality, and performance in production. |
| **Metrics** | **Prometheus Client** | Exposes application and model performance metrics for external monitoring systems. |

## Backend Structure

While this directory (`Fluxora/backend`) is primarily for testing, the core logic is distributed across the following directories in the project root:

| Directory | Content | Description |
| :--- | :--- | :--- |
| `src/api/` | `app.py`, `schemas.py`, `middleware.py` | Contains the core **FastAPI application**, Pydantic schemas, and API-level middleware. |
| `src/features/` | `build_features.py`, `feature_store.py` | Logic for **feature engineering**, including temporal and domain-specific features, and interaction with the Feature Store. |
| `src/models/` | `train.py`, `predict.py`, `model_selector.py` | Contains the **model training, prediction, and selection logic** for the energy forecasting tasks. |
| `packages/shared/` | `utils/`, `logger.py`, `config.py` | **Shared utilities** and common code used across the entire backend application, including logging and configuration handling. |
| `backend/` | `tests/` | **Comprehensive test suite** for the API, database, and core utilities. |

## Test Suite Detail

The `backend/tests` directory contains a comprehensive suite of unit and integration tests written using **Pytest**. These tests ensure the reliability and correctness of the backend services.

### Test File Breakdown

| Test File | Component Tested | Primary Focus |
| :--- | :--- | :--- |
| `test_api.py` | API Endpoints | Validates RESTful API behavior, request/response schemas, and error handling. |
| `test_auth.py` | Authentication | Ensures secure user authentication, token validation, and authorization mechanisms. |
| `test_config.py` | Configuration | Verifies correct loading, parsing, and application of configuration settings (e.g., from Hydra). |
| `test_database.py` | Data Access | Tests database connections, ORM queries, and data integrity checks. |
| `test_middleware.py` | Middleware | Validates the functionality of request/response processing middleware (e.g., logging, security, rate-limiting). |
| `test_models.py` | Data Models | Ensures Pydantic and ORM data models are correctly defined and validated. |
| `test_services.py` | Business Logic | Validates the core business logic and service layers (e.g., forecasting service). |
| `test_utils.py` | Utility Functions | Tests helper functions, logging, and custom exception handling. |

## Getting Started

To run the backend application and its tests, you should refer to the main project's `README.md` and the `requirements.txt` file for environment setup.

### Running Tests

Tests are executed using `pytest`.

```bash
# From the project root directory (/home/ubuntu/Fluxora)
pytest backend/tests/

# To run a specific test file
pytest backend/tests/test_api.py
```

---