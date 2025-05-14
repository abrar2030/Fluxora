# Development Setup Guide

This guide will help you set up your development environment for the Fluxora project.

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn
- Docker and Docker Compose
- Git

## Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/fluxora.git
   cd fluxora
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_dev.txt
   ```

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd apps/backend
   ```

2. Set up environment variables:
   ```bash
   cp config/dev/.env.example config/dev/.env
   # Edit .env with your configuration
   ```

3. Initialize the database:
   ```bash
   python manage.py migrate
   ```

4. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Web Frontend Setup

1. Navigate to the web directory:
   ```bash
   cd apps/web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

## Mobile Frontend Setup

1. Navigate to the mobile directory:
   ```bash
   cd apps/mobile
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the development server:
   ```bash
   npm start
   ```

## Shared Packages Setup

1. Install shared package dependencies:
   ```bash
   cd packages/shared
   pip install -e .
   ```

2. Install UI package dependencies:
   ```bash
   cd packages/ui
   npm install
   ```

3. Install utility package dependencies:
   ```bash
   cd packages/utils
   pip install -e .
   ```

## Development Tools Setup

1. Set up development scripts:
   ```bash
   cd tools/scripts
   chmod +x *.sh  # On Unix-like systems
   ```

2. Configure monitoring tools:
   ```bash
   cd tools/monitoring
   cp config.example.yaml config.yaml
   # Edit config.yaml with your configuration
   ```

## Running Tests

1. Backend tests:
   ```bash
   cd apps/backend
   pytest
   ```

2. Web frontend tests:
   ```bash
   cd apps/web
   npm test
   ```

3. Mobile frontend tests:
   ```bash
   cd apps/mobile
   npm test
   ```

## Development Workflow

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

3. Push your changes:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request on GitHub

## Common Issues and Solutions

### Backend Issues

1. Database connection errors:
   - Check database credentials in `.env`
   - Ensure database server is running
   - Verify network connectivity

2. Migration errors:
   - Delete migration files and database
   - Run `python manage.py makemigrations`
   - Run `python manage.py migrate`

### Frontend Issues

1. Build errors:
   - Clear node_modules and reinstall
   - Check for version conflicts
   - Verify environment variables

2. Runtime errors:
   - Check browser console for errors
   - Verify API endpoints
   - Check network connectivity

### Shared Package Issues

1. Import errors:
   - Verify package installation
   - Check package paths
   - Update package versions

## Additional Resources

- [API Documentation](../api/README.md)
- [Architecture Overview](../architecture/README.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Code Style Guide](../STYLE_GUIDE.md)

## Getting Help

- Create an issue on GitHub
- Join our Slack channel
- Contact the development team 