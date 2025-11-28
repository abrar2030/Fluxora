#!/bin/bash

# install_dependencies.sh
# Automates the installation of all dependencies for Fluxora components
#
# This script installs dependencies for:
# - Backend (Python)
# - Web Frontend (Node.js)
# - Mobile Frontend (React Native)
# - Monitoring tools

set -euo pipefail

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

# Function to install backend dependencies
install_backend_deps() {
    print_section "Installing Backend Dependencies"

    if ! check_directory "${PROJECT_DIR}/src"; then
        print_warning "Backend source directory not found, skipping..."
        return
    fi

    cd "${PROJECT_DIR}/src"

    # Check if virtualenv exists, create if not
    if [ ! -d "venv" ]; then
        print_warning "Creating Python virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    print_warning "Activating virtual environment..."
    source venv/bin/activate

    # Upgrade pip
    print_warning "Upgrading pip..."
    pip install --upgrade pip

    # Install requirements
    if [ -f "requirements.txt" ]; then
        print_warning "Installing Python dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        print_error "requirements.txt not found in ${PROJECT_DIR}/src"
    fi

    # Install development requirements if available
    if [ -f "requirements-dev.txt" ]; then
        print_warning "Installing development dependencies..."
        pip install -r requirements-dev.txt
    fi

    # Deactivate virtual environment
    deactivate

    print_success "Backend dependencies installed successfully"
}

# Function to install web frontend dependencies
install_web_frontend_deps() {
    print_section "Installing Web Frontend Dependencies"

    if ! check_directory "${PROJECT_DIR}/web-frontend"; then
        print_warning "Web frontend directory not found, skipping..."
        return
    fi

    cd "${PROJECT_DIR}/web-frontend"

    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please run setup_environment.sh first."
        return
    fi

    # Install dependencies
    if [ -f "package.json" ]; then
        print_warning "Installing Node.js dependencies..."
        npm install
    else
        print_error "package.json not found in ${PROJECT_DIR}/web-frontend"
    fi

    print_success "Web frontend dependencies installed successfully"
}

# Function to install mobile frontend dependencies
install_mobile_frontend_deps() {
    print_section "Installing Mobile Frontend Dependencies"

    if ! check_directory "${PROJECT_DIR}/mobile-frontend"; then
        print_warning "Mobile frontend directory not found, skipping..."
        return
    fi

    cd "${PROJECT_DIR}/mobile-frontend"

    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please run setup_environment.sh first."
        return
    fi

    # Install dependencies
    if [ -f "package.json" ]; then
        print_warning "Installing Node.js dependencies..."
        npm install
    else
        print_error "package.json not found in ${PROJECT_DIR}/mobile-frontend"
    fi

    # Check if React Native CLI is installed
    if ! command -v npx react-native &> /dev/null; then
        print_warning "Installing React Native CLI..."
        npm install -g react-native-cli
    fi

    print_success "Mobile frontend dependencies installed successfully"
}

# Function to install monitoring dependencies
install_monitoring_deps() {
    print_section "Installing Monitoring Dependencies"

    if ! check_directory "${PROJECT_DIR}/monitoring"; then
        print_warning "Monitoring directory not found, skipping..."
        return
    fi

    cd "${PROJECT_DIR}/monitoring"

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please run setup_environment.sh first."
        return
    fi

    print_warning "Monitoring dependencies will be handled by Docker"
    print_warning "Use docker_manager.sh to build and start monitoring services"

    print_success "Monitoring setup completed"
}

# Function to install all dependencies
install_all_deps() {
    print_section "Installing All Dependencies"

    install_backend_deps
    install_web_frontend_deps
    install_mobile_frontend_deps
    install_monitoring_deps

    print_section "Dependency Installation Complete"
    print_success "All dependencies have been installed successfully"

    echo -e "\nNext steps:"
    echo "1. Run the start_services.sh script to start all required services"
    echo "2. Access the application at http://localhost:8000"
}

# Function to display help message
show_help() {
    echo "Dependency Installer for Fluxora"
    echo ""
    echo "Usage: $0 [options] [component]"
    echo ""
    echo "Components:"
    echo "  backend            Install backend dependencies"
    echo "  web                Install web frontend dependencies"
    echo "  mobile             Install mobile frontend dependencies"
    echo "  monitoring         Install monitoring dependencies"
    echo "  all                Install all dependencies (default)"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -d, --directory    Specify Fluxora project directory (default: current directory)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Install all dependencies"
    echo "  $0 backend                   # Install only backend dependencies"
    echo "  $0 -d /path/to/fluxora web   # Install web frontend dependencies in specific directory"
}

# Parse command line arguments
COMPONENT="all"

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
        backend|web|mobile|monitoring|all)
            COMPONENT="$1"
            shift
            ;;
        *)
            print_error "Unknown option or component: $1"
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

# Execute based on component
case $COMPONENT in
    backend)
        install_backend_deps
        ;;
    web)
        install_web_frontend_deps
        ;;
    mobile)
        install_mobile_frontend_deps
        ;;
    monitoring)
        install_monitoring_deps
        ;;
    all)
        install_all_deps
        ;;
esac

exit 0
