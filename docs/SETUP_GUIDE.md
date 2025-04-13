# Setup and Installation Guide

## Prerequisites
- Python 3.x
- Git
- DVC (Data Version Control)
- Make
- A Unix-like shell (for running shell scripts)

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fluxora
```

### 2. Set Up Python Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

### 3. Initialize DVC
```bash
dvc init
```

### 4. Set Up Frontend
```bash
cd frontend
# Install frontend dependencies
npm install
```

### 5. Configure Environment Variables
Create a `.env` file in the root directory with necessary environment variables:
```
# Example environment variables
DATABASE_URL=your_database_url
API_KEY=your_api_key
```

### 6. Run the Application
```bash
# Start the backend server
python src/main.py

# In a separate terminal, start the frontend
cd frontend
npm start
```

## Development Tools
- Use `make` commands for common tasks (check Makefile)
- Use `git-auto-commit.sh` for automated git commits
- Use DVC for data versioning

## Troubleshooting
- If you encounter permission issues with shell scripts, run:
  ```bash
  chmod +x *.sh
  ```
- For database connection issues, verify your `.env` configuration
- For frontend issues, ensure all npm packages are installed correctly

## Additional Resources
- [Project Overview](PROJECT_OVERVIEW.md)
- [API Documentation](API_DOCS.md)
- [Development Guidelines](DEVELOPMENT_GUIDELINES.md) 