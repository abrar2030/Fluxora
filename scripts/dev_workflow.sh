#!/bin/bash

# dev_workflow.sh
# Automates common development tasks for Fluxora
#
# This script provides shortcuts for:
# - Code formatting and linting
# - Git operations
# - Database migrations
# - Local development tasks

set -e

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Default project directory
PROJECT_DIR="$(pwd)"

# Function to print section headers
print_section() {
    echo -e "\n${BOLD}${BLUE}==== $1 ====${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to check if directory exists
check_directory() {
    if [ ! -d "$1" ]; then
        print_error "Directory $1 not found"
        return 1
    fi
    return 0
}

# Function to format Python code
format_python() {
    print_section "Formatting Python Code"

    if ! check_directory "${PROJECT_DIR}/src"; then
        print_warning "Backend source directory not found, skipping..."
        return 1
    fi

    cd "${PROJECT_DIR}"

    # Check if virtualenv exists
    if [ ! -d "src/venv" ]; then
        print_error "Python virtual environment not found"
        print_warning "Please run install_dependencies.sh first"
        return 1
    fi

    # Activate virtual environment
    print_warning "Activating virtual environment..."
    source src/venv/bin/activate

    # Check if black is installed
    if ! pip list | grep -q black; then
        print_warning "Installing black formatter..."
        pip install black
    fi

    # Format Python code with black
    print_warning "Formatting Python code with black..."
    python -m black src/ backend/

    # Check if isort is installed
    if ! pip list | grep -q isort; then
        print_warning "Installing isort..."
        pip install isort
    fi

    # Sort imports with isort
    print_warning "Sorting imports with isort..."
    python -m isort src/ backend/

    # Deactivate virtual environment
    deactivate

    print_success "Python code formatting completed"
}

# Function to lint Python code
lint_python() {
    print_section "Linting Python Code"

    if ! check_directory "${PROJECT_DIR}/src"; then
        print_warning "Backend source directory not found, skipping..."
        return 1
    fi

    cd "${PROJECT_DIR}"

    # Check if virtualenv exists
    if [ ! -d "src/venv" ]; then
        print_error "Python virtual environment not found"
        print_warning "Please run install_dependencies.sh first"
        return 1
    fi

    # Activate virtual environment
    print_warning "Activating virtual environment..."
    source src/venv/bin/activate

    # Check if flake8 is installed
    if ! pip list | grep -q flake8; then
        print_warning "Installing flake8..."
        pip install flake8
    fi

    # Lint Python code with flake8
    print_warning "Linting Python code with flake8..."
    python -m flake8 src/ backend/

    # Check if pylint is installed
    if ! pip list | grep -q pylint; then
        print_warning "Installing pylint..."
        pip install pylint
    fi

    # Lint Python code with pylint
    print_warning "Linting Python code with pylint..."
    python -m pylint src/ backend/ --errors-only

    # Deactivate virtual environment
    deactivate

    print_success "Python code linting completed"
}

# Function to format JavaScript/TypeScript code
format_js() {
    print_section "Formatting JavaScript/TypeScript Code"

    # Check for web frontend
    if check_directory "${PROJECT_DIR}/web-frontend"; then
        cd "${PROJECT_DIR}/web-frontend"

        # Check if Node.js is installed
        if ! command -v node &> /dev/null; then
            print_error "Node.js is not installed"
            print_warning "Please run setup_environment.sh first"
            return 1
        fi

        # Check if dependencies are installed
        if [ ! -d "node_modules" ]; then
            print_error "Node.js dependencies not installed"
            print_warning "Please run install_dependencies.sh first"
            return 1
        fi

        # Format code with Prettier
        print_warning "Formatting web frontend code with Prettier..."
        npx prettier --write "src/**/*.{js,jsx,ts,tsx,json,css,scss,md}"

        print_success "Web frontend code formatting completed"
    else
        print_warning "Web frontend directory not found, skipping..."
    fi

    # Check for mobile frontend
    if check_directory "${PROJECT_DIR}/mobile-frontend"; then
        cd "${PROJECT_DIR}/mobile-frontend"

        # Check if Node.js is installed
        if ! command -v node &> /dev/null; then
            print_error "Node.js is not installed"
            print_warning "Please run setup_environment.sh first"
            return 1
        fi

        # Check if dependencies are installed
        if [ ! -d "node_modules" ]; then
            print_error "Node.js dependencies not installed"
            print_warning "Please run install_dependencies.sh first"
            return 1
        fi

        # Format code with Prettier
        print_warning "Formatting mobile frontend code with Prettier..."
        npx prettier --write "src/**/*.{js,jsx,ts,tsx,json,css,scss,md}"

        print_success "Mobile frontend code formatting completed"
    else
        print_warning "Mobile frontend directory not found, skipping..."
    fi
}

# Function to lint JavaScript/TypeScript code
lint_js() {
    print_section "Linting JavaScript/TypeScript Code"

    # Check for web frontend
    if check_directory "${PROJECT_DIR}/web-frontend"; then
        cd "${PROJECT_DIR}/web-frontend"

        # Check if Node.js is installed
        if ! command -v node &> /dev/null; then
            print_error "Node.js is not installed"
            print_warning "Please run setup_environment.sh first"
            return 1
        fi

        # Check if dependencies are installed
        if [ ! -d "node_modules" ]; then
            print_error "Node.js dependencies not installed"
            print_warning "Please run install_dependencies.sh first"
            return 1
        fi

        # Lint code with ESLint
        print_warning "Linting web frontend code with ESLint..."
        npx eslint "src/**/*.{js,jsx,ts,tsx}"

        print_success "Web frontend code linting completed"
    else
        print_warning "Web frontend directory not found, skipping..."
    fi

    # Check for mobile frontend
    if check_directory "${PROJECT_DIR}/mobile-frontend"; then
        cd "${PROJECT_DIR}/mobile-frontend"

        # Check if Node.js is installed
        if ! command -v node &> /dev/null; then
            print_error "Node.js is not installed"
            print_warning "Please run setup_environment.sh first"
            return 1
        fi

        # Check if dependencies are installed
        if [ ! -d "node_modules" ]; then
            print_error "Node.js dependencies not installed"
            print_warning "Please run install_dependencies.sh first"
            return 1
        fi

        # Lint code with ESLint
        print_warning "Linting mobile frontend code with ESLint..."
        npx eslint "src/**/*.{js,jsx,ts,tsx}"

        print_success "Mobile frontend code linting completed"
    else
        print_warning "Mobile frontend directory not found, skipping..."
    fi
}

# Function to run database migrations
run_migrations() {
    print_section "Running Database Migrations"

    if ! check_directory "${PROJECT_DIR}/src"; then
        print_warning "Backend source directory not found, skipping..."
        return 1
    fi

    cd "${PROJECT_DIR}/src"

    # Check if virtualenv exists
    if [ ! -d "venv" ]; then
        print_error "Python virtual environment not found"
        print_warning "Please run install_dependencies.sh first"
        return 1
    fi

    # Activate virtual environment
    print_warning "Activating virtual environment..."
    source venv/bin/activate

    # Run migrations
    print_warning "Running database migrations..."
    python manage.py migrate

    # Deactivate virtual environment
    deactivate

    print_success "Database migrations completed"
}

# Function to create a new migration
create_migration() {
    print_section "Creating New Database Migration"

    if ! check_directory "${PROJECT_DIR}/src"; then
        print_warning "Backend source directory not found, skipping..."
        return 1
    fi

    cd "${PROJECT_DIR}/src"

    # Check if virtualenv exists
    if [ ! -d "venv" ]; then
        print_error "Python virtual environment not found"
        print_warning "Please run install_dependencies.sh first"
        return 1
    fi

    # Activate virtual environment
    print_warning "Activating virtual environment..."
    source venv/bin/activate

    # Get app name
    read -p "Enter app name: " APP_NAME

    # Get migration name
    read -p "Enter migration name: " MIGRATION_NAME

    # Create migration
    print_warning "Creating migration for ${APP_NAME}..."
    python manage.py makemigrations $APP_NAME --name $MIGRATION_NAME

    # Deactivate virtual environment
    deactivate

    print_success "Migration created successfully"
}

# Function to create a git commit
git_commit() {
    print_section "Creating Git Commit"

    cd "${PROJECT_DIR}"

    # Check if git is initialized
    if [ ! -d ".git" ]; then
        print_error "Git repository not initialized"
        print_warning "Please run 'git init' first"
        return 1
    fi

    # Check for changes
    if git diff --quiet && git diff --staged --quiet; then
        print_warning "No changes to commit"
        return 1
    fi

    # Add all changes
    print_warning "Adding all changes..."
    git add .

    # Get commit message
    read -p "Enter commit message: " COMMIT_MESSAGE

    # Create commit
    print_warning "Creating commit..."
    git commit -m "$COMMIT_MESSAGE"

    print_success "Commit created successfully"
}

# Function to create a git branch
git_branch() {
    print_section "Creating Git Branch"

    cd "${PROJECT_DIR}"

    # Check if git is initialized
    if [ ! -d ".git" ]; then
        print_error "Git repository not initialized"
        print_warning "Please run 'git init' first"
        return 1
    fi

    # Get branch name
    read -p "Enter branch name: " BRANCH_NAME

    # Create branch
    print_warning "Creating branch ${BRANCH_NAME}..."
    git checkout -b $BRANCH_NAME

    print_success "Branch created successfully"
}

# Function to format all code
format_all() {
    print_section "Formatting All Code"

    format_python
    format_js

    print_success "All code formatting completed"
}

# Function to lint all code
lint_all() {
    print_section "Linting All Code"

    lint_python
    lint_js

    print_success "All code linting completed"
}

# Function to display help message
show_help() {
    echo "Development Workflow Helper for Fluxora"
    echo ""
    echo "Usage: $0 [options] command"
    echo ""
    echo "Commands:"
    echo "  format-py          Format Python code"
    echo "  lint-py            Lint Python code"
    echo "  format-js          Format JavaScript/TypeScript code"
    echo "  lint-js            Lint JavaScript/TypeScript code"
    echo "  format-all         Format all code"
    echo "  lint-all           Lint all code"
    echo "  migrate            Run database migrations"
    echo "  make-migration     Create a new database migration"
    echo "  commit             Create a git commit"
    echo "  branch             Create a git branch"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -d, --directory    Specify Fluxora project directory (default: current directory)"
    echo ""
    echo "Examples:"
    echo "  $0 format-all                  # Format all code"
    echo "  $0 -d /path/to/fluxora lint-py # Lint Python code in specific directory"
}

# Parse command line arguments
COMMAND=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--directory)
            PROJECT_DIR="$2"
            shift 2
            ;;
        format-py|lint-py|format-js|lint-js|format-all|lint-all|migrate|make-migration|commit|branch)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option or command: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory $PROJECT_DIR does not exist"
    exit 1
fi

# Check if command is provided
if [ -z "$COMMAND" ]; then
    print_error "No command specified"
    show_help
    exit 1
fi

# Execute based on command
case $COMMAND in
    format-py)
        format_python
        ;;
    lint-py)
        lint_python
        ;;
    format-js)
        format_js
        ;;
    lint-js)
        lint_js
        ;;
    format-all)
        format_all
        ;;
    lint-all)
        lint_all
        ;;
    migrate)
        run_migrations
        ;;
    make-migration)
        create_migration
        ;;
    commit)
        git_commit
        ;;
    branch)
        git_branch
        ;;
esac

exit 0
