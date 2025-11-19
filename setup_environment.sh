#!/bin/bash

# setup_environment.sh
# Automates the setup of development environment for Fluxora
#
# This script checks and installs all prerequisites required for Fluxora:
# - Python 3.9+
# - Node.js 16+
# - Docker and Docker Compose
# - PostgreSQL 13+
# - Redis
# - Other development tools

set -e

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check version meets minimum requirement
version_gte() {
    # $1 = version to check, $2 = minimum version
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
    return $?
}

# Check if script is run with sudo
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        print_warning "This script may need sudo privileges to install system packages."
        print_warning "You might be prompted for your password during execution."
    fi
}

# Check and install Python
setup_python() {
    print_section "Setting up Python"

    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
        echo "Python version: $PYTHON_VERSION"

        if version_gte "$PYTHON_VERSION" "3.9"; then
            print_success "Python $PYTHON_VERSION is installed and meets requirements"
        else
            print_warning "Python $PYTHON_VERSION is installed but Fluxora requires 3.9+"
            install_python
        fi
    else
        print_warning "Python not found"
        install_python
    fi

    # Check pip
    if ! command_exists pip3; then
        print_warning "pip not found, installing..."
        sudo apt-get update
        sudo apt-get install -y python3-pip
    fi

    # Install virtualenv
    if ! command_exists virtualenv; then
        print_warning "virtualenv not found, installing..."
        pip3 install virtualenv
    fi

    print_success "Python environment is ready"
}

# Install Python if needed
install_python() {
    print_warning "Installing Python 3.9+..."
    sudo apt-get update
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.9 python3.9-dev python3.9-venv python3-pip
    print_success "Python 3.9 installed"
}

# Check and install Node.js
setup_nodejs() {
    print_section "Setting up Node.js"

    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d "v" -f 2)
        echo "Node.js version: $NODE_VERSION"

        if version_gte "$NODE_VERSION" "16.0.0"; then
            print_success "Node.js $NODE_VERSION is installed and meets requirements"
        else
            print_warning "Node.js $NODE_VERSION is installed but Fluxora requires 16+"
            install_nodejs
        fi
    else
        print_warning "Node.js not found"
        install_nodejs
    fi

    # Check npm
    if ! command_exists npm; then
        print_warning "npm not found, it should be installed with Node.js"
        install_nodejs
    fi

    print_success "Node.js environment is ready"
}

# Install Node.js if needed
install_nodejs() {
    print_warning "Installing Node.js 16+..."
    curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
    sudo apt-get install -y nodejs
    print_success "Node.js installed"
}

# Check and install Docker
setup_docker() {
    print_section "Setting up Docker"

    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | cut -d " " -f 3 | cut -d "," -f 1)
        echo "Docker version: $DOCKER_VERSION"
        print_success "Docker is installed"
    else
        print_warning "Docker not found"
        install_docker
    fi

    # Check Docker Compose
    if command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d " " -f 3 | cut -d "," -f 1)
        echo "Docker Compose version: $COMPOSE_VERSION"
        print_success "Docker Compose is installed"
    else
        print_warning "Docker Compose not found, installing..."
        sudo apt-get update
        sudo apt-get install -y docker-compose
    fi

    # Ensure user is in docker group
    if ! groups | grep -q docker; then
        print_warning "Adding user to docker group..."
        sudo usermod -aG docker $USER
        print_warning "You may need to log out and back in for group changes to take effect"
    fi

    print_success "Docker environment is ready"
}

# Install Docker if needed
install_docker() {
    print_warning "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    print_success "Docker installed"
}

# Check and install PostgreSQL
setup_postgres() {
    print_section "Setting up PostgreSQL"

    if command_exists psql; then
        PG_VERSION=$(psql --version | cut -d " " -f 3)
        echo "PostgreSQL version: $PG_VERSION"

        if version_gte "$PG_VERSION" "13.0"; then
            print_success "PostgreSQL $PG_VERSION is installed and meets requirements"
        else
            print_warning "PostgreSQL $PG_VERSION is installed but Fluxora requires 13+"
            install_postgres
        fi
    else
        print_warning "PostgreSQL not found"
        install_postgres
    fi

    print_success "PostgreSQL environment is ready"
}

# Install PostgreSQL if needed
install_postgres() {
    print_warning "Installing PostgreSQL 13+..."
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install -y postgresql-13
    print_success "PostgreSQL 13 installed"
}

# Check and install Redis
setup_redis() {
    print_section "Setting up Redis"

    if command_exists redis-server; then
        REDIS_VERSION=$(redis-server --version | cut -d " " -f 3 | cut -d "=" -f 2)
        echo "Redis version: $REDIS_VERSION"
        print_success "Redis is installed"
    else
        print_warning "Redis not found"
        install_redis
    fi

    print_success "Redis environment is ready"
}

# Install Redis if needed
install_redis() {
    print_warning "Installing Redis..."
    sudo apt-get update
    sudo apt-get install -y redis-server
    sudo systemctl enable redis-server
    print_success "Redis installed"
}

# Main function
main() {
    print_section "Fluxora Environment Setup"
    echo "This script will check and install all prerequisites for Fluxora."

    check_sudo

    # Update package lists
    print_warning "Updating package lists..."
    sudo apt-get update

    # Install basic tools
    print_warning "Installing basic development tools..."
    sudo apt-get install -y build-essential curl wget git

    # Setup components
    setup_python
    setup_nodejs
    setup_docker
    setup_postgres
    setup_redis

    print_section "Environment Setup Complete"
    print_success "All prerequisites for Fluxora have been installed and configured."
    print_warning "Note: You may need to log out and back in for some changes to take effect."

    echo -e "\nNext steps:"
    echo "1. Clone the Fluxora repository: git clone https://github.com/abrar2030/fluxora.git"
    echo "2. Run the install_dependencies.sh script to install project dependencies"
    echo "3. Run the start_services.sh script to start all required services"
}

# Run main function
main
