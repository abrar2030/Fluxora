# Setup and Installation Guide

## Prerequisites
- Python 3.8+ (as per common modern standards, specific version might be in `requirements.txt`)
- Git
- Pip (Python package installer)
- Virtualenv (recommended for Python environment isolation)
- (Optional) DVC (Data Version Control) - if used for managing large data files not in Git.
- (Optional) Node.js and npm/yarn - if planning to develop/run the placeholder `web-frontend`.

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fluxora
```

### 2. Set Up Python Environment
It is highly recommended to use a virtual environment.
```bash
# Create a virtual environment (e.g., named .venv)
python -m venv .venv

# Activate the virtual environment
# On Windows:
# .venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate

# Install core Python dependencies
# Ensure requirements.txt is up-to-date and reflects the project needs.
# It should include libraries like pandas, scikit-learn, evidently, prometheus-client, etc.
pip install -r requirements.txt

# Install development dependencies (if requirements_dev.txt exists and is used)
# pip install -r requirements_dev.txt
```

### 3. (Optional) Initialize DVC
If the project uses DVC for managing large data files:
```bash
# dvc init # Only if DVC is being used for data versioning
# dvc pull # To get DVC-tracked data if a remote is configured
```

### 4. (Optional) Set Up Web Frontend (Placeholder)
The `web-frontend` directory contains a placeholder structure for a React application. If you intend to develop this:
```bash
cd web-frontend
# Install frontend dependencies (e.g., using npm or yarn)
# npm install
# or
# yarn install
cd ..
```
Note: The `mobile-frontend` directory is also a placeholder and does not contain a functional application.

### 5. Configure Environment Variables (If Applicable)
If the application requires specific configurations (e.g., API keys, database URLs for a full application), these would typically be managed via environment variables or a configuration file (like `.env` or within `packages/shared/utils/config.py`).

The current `packages/shared/utils/config.py` provides example structures. For a real application, you might create a `.env` file in the root directory and load it using a library like `python-dotenv`.
Example `.env` content:
```env
# Example: For a database connection (if used by a backend service)
# DATABASE_URL="postgresql://user:password@host:port/database"

# Example: For an external API key
# EXTERNAL_API_KEY="your_api_key_here"

# Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL="INFO"
```
Ensure `packages/shared/utils/logger.py` or other relevant modules are adapted to read these environment variables if needed.

### 6. Running Components
This project is primarily a collection of utilities and scripts rather than a single runnable application server.
- **Scripts**: Individual Python scripts (e.g., in `tools/monitoring/`, `packages/shared/data/`) can be run directly.
  ```bash
  python packages/shared/data/make_dataset.py # Example
  python tools/monitoring/drift_detection.py # Example
  ```
- **Monitoring**: The `tools/monitoring/performance.py` script can expose Prometheus metrics if `start_http_server` is uncommented and run.
- **Web Frontend**: If developed, the frontend would be started typically with:
  ```bash
  # cd web-frontend
  # npm start
  # or
  # yarn start
  ```

## Development Tools
- **Linters/Formatters**: Consider using tools like Black, Flake8, or Pylint for Python code quality (usually configured in `pyproject.toml` or `setup.cfg`).
- **Testing**: Implement and run tests (e.g., using `pytest` or `unittest`). Test files would typically reside in a `tests/` directory.
- **Makefile**: The `Makefile` (if present and updated) can provide shortcuts for common tasks like testing, linting, and cleaning.

## Key Project Structure Overview
- `packages/shared/`: Contains core Python modules for data processing, feature engineering, models (placeholders), utilities (logging, config, alerts, monitoring), and visualization.
- `tools/monitoring/`: Contains scripts for data drift detection and performance metric collection.
- `notebooks/`: For experimental work and data exploration.
- `docs/`: Project documentation.
- `web-frontend/`: Placeholder for a React-based web application.
- `mobile-frontend/`: Placeholder for a mobile application.

## Troubleshooting
- **Dependency Issues**: Ensure your Python virtual environment is active and all packages in `requirements.txt` are installed correctly. Resolve any version conflicts.
- **Import Errors**: Verify that your `PYTHONPATH` is set up correctly if running scripts from different locations, or run scripts as modules if structured as a package (e.g., `python -m packages.shared.data.make_dataset`). Ensure the project root is recognized by your IDE or terminal session.
- **Configuration**: If using `packages/shared/utils/config.py`, ensure the default values are appropriate or are correctly overridden by environment variables or other mechanisms.

## Additional Resources
- [Project Overview](PROJECT_OVERVIEW.md)
- [API Documentation](API_DOCS.md) (Review for relevance to current structure)
- [Development Guidelines](DEVELOPMENT_GUIDELINES.md)
- [System Architecture](ARCHITECTURE.md) (Reflects the new structure)
