#!/bin/bash

# docker_manager.sh
# Simplifies Docker operations for Fluxora
#
# This script provides easy commands for managing Docker containers:
# - build: Build all Docker images
# - start: Start all containers
# - stop: Stop all containers
# - status: Check status of all containers
# - logs: View logs from containers
# - clean: Remove all containers and images

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

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please run setup_environment.sh first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please run setup_environment.sh first."
        exit 1
    fi
}

# Function to check if docker-compose.yml exists
check_compose_file() {
    if [ ! -f "${PROJECT_DIR}/docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in ${PROJECT_DIR}"
        print_warning "Please run this script from the Fluxora project root directory"
        print_warning "or specify the project directory with -d option"
        exit 1
    fi
}

# Function to build Docker images
build_images() {
    print_section "Building Docker Images"

    check_compose_file

    print_warning "Building all Docker images. This may take a while..."
    docker-compose -f "${PROJECT_DIR}/docker-compose.yml" build

    print_success "All Docker images built successfully"
}

# Function to start Docker containers
start_containers() {
    print_section "Starting Docker Containers"

    check_compose_file

    print_warning "Starting all containers in detached mode..."
    docker-compose -f "${PROJECT_DIR}/docker-compose.yml" up -d

    print_success "All containers started successfully"
    print_warning "Use 'docker_manager.sh status' to check container status"
    print_warning "Use 'docker_manager.sh logs' to view container logs"
}

# Function to stop Docker containers
stop_containers() {
    print_section "Stopping Docker Containers"

    check_compose_file

    print_warning "Stopping all containers..."
    docker-compose -f "${PROJECT_DIR}/docker-compose.yml" down

    print_success "All containers stopped successfully"
}

# Function to check status of Docker containers
check_status() {
    print_section "Docker Container Status"

    check_compose_file

    echo "Current running containers:"
    docker-compose -f "${PROJECT_DIR}/docker-compose.yml" ps
}

# Function to view Docker container logs
view_logs() {
    print_section "Docker Container Logs"

    check_compose_file

    if [ -z "$1" ]; then
        print_warning "Showing logs for all containers. Press Ctrl+C to exit."
        docker-compose -f "${PROJECT_DIR}/docker-compose.yml" logs -f
    else
        print_warning "Showing logs for $1. Press Ctrl+C to exit."
        docker-compose -f "${PROJECT_DIR}/docker-compose.yml" logs -f "$1"
    fi
}

# Function to clean Docker containers and images
clean_docker() {
    print_section "Cleaning Docker Resources"

    check_compose_file

    print_warning "Stopping all containers..."
    docker-compose -f "${PROJECT_DIR}/docker-compose.yml" down

    print_warning "Removing all project containers..."
    docker-compose -f "${PROJECT_DIR}/docker-compose.yml" rm -f

    print_warning "Removing all project images..."
    docker-compose -f "${PROJECT_DIR}/docker-compose.yml" down --rmi all

    print_warning "Removing all dangling images..."
    docker image prune -f

    print_warning "Removing all dangling volumes..."
    docker volume prune -f

    print_success "Docker cleanup completed successfully"
}

# Function to display help message
show_help() {
    echo "Docker Manager for Fluxora"
    echo ""
    echo "Usage: $0 [options] command [service_name]"
    echo ""
    echo "Commands:"
    echo "  build              Build all Docker images"
    echo "  start              Start all containers"
    echo "  stop               Stop all containers"
    echo "  status             Check status of all containers"
    echo "  logs [service]     View logs from all or specific container"
    echo "  clean              Remove all containers and images"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -d, --directory    Specify Fluxora project directory (default: current directory)"
    echo ""
    echo "Examples:"
    echo "  $0 build                   # Build all Docker images"
    echo "  $0 start                   # Start all containers"
    echo "  $0 logs api                # View logs from the API service"
    echo "  $0 -d /path/to/fluxora start  # Start containers in specific directory"
}

# Parse command line arguments
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
        build|start|stop|status|clean)
            COMMAND="$1"
            shift
            ;;
        logs)
            COMMAND="$1"
            SERVICE="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option or command: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if Docker is installed
check_docker

# Execute the specified command
case $COMMAND in
    build)
        build_images
        ;;
    start)
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs "$SERVICE"
        ;;
    clean)
        clean_docker
        ;;
    *)
        show_help
        ;;
esac

exit 0
