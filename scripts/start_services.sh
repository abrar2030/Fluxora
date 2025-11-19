#!/bin/bash

# start_services.sh
# Automates the startup of all Fluxora services in the correct order
#
# This script handles:
# - Starting backend services
# - Starting frontend applications
# - Starting monitoring stack
# - Checking service health

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

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to wait for a service to be available
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=$3
    local attempt=1

    print_warning "Waiting for $service_name to be available on port $port..."

    while [ $attempt -le $max_attempts ]; do
        if check_port $port; then
            print_success "$service_name is available on port $port"
            return 0
        fi

        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "$service_name did not become available on port $port after $max_attempts attempts"
    return 1
}

# Function to start backend services
start_backend() {
    print_section "Starting Backend Services"

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

    # Start API server in background
    print_warning "Starting API server..."
    if [ -f "api/main.py" ]; then
        python api/main.py > ../logs/api.log 2>&1 &
        API_PID=$!
        echo $API_PID > ../logs/api.pid
        print_success "API server started with PID $API_PID"

        # Wait for API to be available
        wait_for_service "API server" 8000 15
    else
        print_error "API main.py not found in ${PROJECT_DIR}/src/api"
        return 1
    fi

    # Deactivate virtual environment
    deactivate

    print_success "Backend services started successfully"
    return 0
}

# Function to start web frontend
start_web_frontend() {
    print_section "Starting Web Frontend"

    if ! check_directory "${PROJECT_DIR}/web-frontend"; then
        print_warning "Web frontend directory not found, skipping..."
        return 1
    fi

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

    # Start web frontend in development mode
    print_warning "Starting web frontend in development mode..."
    npm start > ../logs/web-frontend.log 2>&1 &
    WEB_PID=$!
    echo $WEB_PID > ../logs/web-frontend.pid
    print_success "Web frontend started with PID $WEB_PID"

    # Wait for web frontend to be available
    wait_for_service "Web frontend" 3000 20

    print_success "Web frontend started successfully"
    return 0
}

# Function to start mobile frontend
start_mobile_frontend() {
    print_section "Starting Mobile Frontend"

    if ! check_directory "${PROJECT_DIR}/mobile-frontend"; then
        print_warning "Mobile frontend directory not found, skipping..."
        return 1
    fi

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

    # Start Metro bundler for React Native
    print_warning "Starting Metro bundler for React Native..."
    npx react-native start > ../logs/mobile-frontend.log 2>&1 &
    MOBILE_PID=$!
    echo $MOBILE_PID > ../logs/mobile-frontend.pid
    print_success "Mobile frontend bundler started with PID $MOBILE_PID"

    print_warning "To run on a device or emulator, use a separate terminal and run:"
    print_warning "cd ${PROJECT_DIR}/mobile-frontend && npx react-native run-android"
    print_warning "or"
    print_warning "cd ${PROJECT_DIR}/mobile-frontend && npx react-native run-ios"

    print_success "Mobile frontend started successfully"
    return 0
}

# Function to start monitoring stack
start_monitoring() {
    print_section "Starting Monitoring Stack"

    if ! check_directory "${PROJECT_DIR}/monitoring"; then
        print_warning "Monitoring directory not found, skipping..."
        return 1
    fi

    # Check if Docker is installed
    if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
        print_error "Docker or Docker Compose is not installed"
        print_warning "Please run setup_environment.sh first"
        return 1
    fi

    cd "${PROJECT_DIR}/monitoring"

    # Start monitoring stack with Docker Compose
    print_warning "Starting monitoring stack with Docker Compose..."
    docker-compose up -d

    # Wait for Grafana to be available
    wait_for_service "Grafana" 3000 30

    print_success "Monitoring stack started successfully"
    print_warning "Access Grafana dashboard at http://localhost:3000"
    print_warning "Default credentials: admin/admin"

    return 0
}

# Function to check service health
check_health() {
    print_section "Checking Service Health"

    # Check API health
    if check_port 8000; then
        print_success "API server is running on port 8000"
    else
        print_error "API server is not running"
    fi

    # Check web frontend health
    if check_port 3000; then
        print_success "Web frontend is running on port 3000"
    else
        print_error "Web frontend is not running"
    fi

    # Check if monitoring is running (Grafana)
    if check_port 3000; then
        print_success "Monitoring (Grafana) is running on port 3000"
    else
        print_error "Monitoring (Grafana) is not running"
    fi

    # Check if Prometheus is running
    if check_port 9090; then
        print_success "Prometheus is running on port 9090"
    else
        print_error "Prometheus is not running"
    fi

    print_section "Service URLs"
    echo "API: http://localhost:8000"
    echo "Web Dashboard: http://localhost:3000"
    echo "Grafana: http://localhost:3000"
    echo "Prometheus: http://localhost:9090"
}

# Function to stop all services
stop_services() {
    print_section "Stopping All Services"

    # Stop backend
    if [ -f "${PROJECT_DIR}/logs/api.pid" ]; then
        API_PID=$(cat "${PROJECT_DIR}/logs/api.pid")
        print_warning "Stopping API server (PID: $API_PID)..."
        kill -15 $API_PID 2>/dev/null || true
        rm "${PROJECT_DIR}/logs/api.pid"
    fi

    # Stop web frontend
    if [ -f "${PROJECT_DIR}/logs/web-frontend.pid" ]; then
        WEB_PID=$(cat "${PROJECT_DIR}/logs/web-frontend.pid")
        print_warning "Stopping web frontend (PID: $WEB_PID)..."
        kill -15 $WEB_PID 2>/dev/null || true
        rm "${PROJECT_DIR}/logs/web-frontend.pid"
    fi

    # Stop mobile frontend
    if [ -f "${PROJECT_DIR}/logs/mobile-frontend.pid" ]; then
        MOBILE_PID=$(cat "${PROJECT_DIR}/logs/mobile-frontend.pid")
        print_warning "Stopping mobile frontend bundler (PID: $MOBILE_PID)..."
        kill -15 $MOBILE_PID 2>/dev/null || true
        rm "${PROJECT_DIR}/logs/mobile-frontend.pid"
    fi

    # Stop monitoring stack
    if check_directory "${PROJECT_DIR}/monitoring"; then
        cd "${PROJECT_DIR}/monitoring"
        print_warning "Stopping monitoring stack..."
        docker-compose down
    fi

    print_success "All services stopped successfully"
}

# Function to ensure logs directory exists
ensure_logs_dir() {
    if [ ! -d "${PROJECT_DIR}/logs" ]; then
        print_warning "Creating logs directory..."
        mkdir -p "${PROJECT_DIR}/logs"
    fi
}

# Function to start all services
start_all() {
    print_section "Starting All Fluxora Services"

    ensure_logs_dir

    # Start services in the correct order
    start_backend
    start_web_frontend
    start_mobile_frontend
    start_monitoring

    # Check health
    check_health

    print_section "All Services Started"
    print_success "Fluxora is now running"

    echo -e "\nUseful commands:"
    echo "- Check service health: $0 health"
    echo "- Stop all services: $0 stop"
    echo "- View logs: tail -f ${PROJECT_DIR}/logs/*.log"
}

# Function to display help message
show_help() {
    echo "Service Manager for Fluxora"
    echo ""
    echo "Usage: $0 [options] command"
    echo ""
    echo "Commands:"
    echo "  start              Start all services (default)"
    echo "  stop               Stop all services"
    echo "  restart            Restart all services"
    echo "  health             Check service health"
    echo "  backend            Start only backend services"
    echo "  web                Start only web frontend"
    echo "  mobile             Start only mobile frontend"
    echo "  monitoring         Start only monitoring stack"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -d, --directory    Specify Fluxora project directory (default: current directory)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Start all services"
    echo "  $0 stop                      # Stop all services"
    echo "  $0 -d /path/to/fluxora start # Start all services in specific directory"
}

# Parse command line arguments
COMMAND="start"

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
        start|stop|restart|health|backend|web|mobile|monitoring)
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

# Execute based on command
case $COMMAND in
    start)
        start_all
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_all
        ;;
    health)
        check_health
        ;;
    backend)
        ensure_logs_dir
        start_backend
        ;;
    web)
        ensure_logs_dir
        start_web_frontend
        ;;
    mobile)
        ensure_logs_dir
        start_mobile_frontend
        ;;
    monitoring)
        ensure_logs_dir
        start_monitoring
        ;;
esac

exit 0
