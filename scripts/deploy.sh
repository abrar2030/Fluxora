#!/bin/bash

# deploy.sh
# Streamlines the deployment process for Fluxora
#
# This script:
# - Prepares the application for deployment
# - Handles different deployment environments (dev, staging, prod)
# - Manages infrastructure provisioning
# - Deploys application components

set -e

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Default settings
PROJECT_DIR="$(pwd)"
ENVIRONMENT="dev"
SKIP_TESTS=false
SKIP_BUILD=false

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

# Function to check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        print_warning "Please run setup_environment.sh first"
        return 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        print_warning "Please run setup_environment.sh first"
        return 1
    fi
    
    # Check if Terraform is installed (for infrastructure)
    if ! command -v terraform &> /dev/null; then
        print_warning "Terraform is not installed"
        print_warning "Infrastructure provisioning will be skipped"
    fi
    
    # Check if kubectl is installed (for Kubernetes)
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl is not installed"
        print_warning "Kubernetes deployment will be skipped"
    fi
    
    print_success "Prerequisites check completed"
    return 0
}

# Function to run tests before deployment
run_tests() {
    print_section "Running Tests"
    
    if [ "$SKIP_TESTS" = true ]; then
        print_warning "Tests skipped as requested"
        return 0
    fi
    
    # Check if run_tests.sh exists
    if [ -f "${PROJECT_DIR}/run_tests.sh" ]; then
        print_warning "Running tests using run_tests.sh..."
        bash "${PROJECT_DIR}/run_tests.sh"
    else
        # Run tests manually
        cd "${PROJECT_DIR}"
        
        # Backend tests
        if check_directory "${PROJECT_DIR}/src"; then
            print_warning "Running backend tests..."
            cd "${PROJECT_DIR}/src"
            source venv/bin/activate
            python -m pytest ../backend/tests/
            deactivate
        fi
        
        # Frontend tests
        if check_directory "${PROJECT_DIR}/web-frontend"; then
            print_warning "Running frontend tests..."
            cd "${PROJECT_DIR}/web-frontend"
            npm test
        fi
    fi
    
    print_success "Tests completed successfully"
    return 0
}

# Function to build application
build_application() {
    print_section "Building Application"
    
    if [ "$SKIP_BUILD" = true ]; then
        print_warning "Build skipped as requested"
        return 0
    fi
    
    # Build backend
    if check_directory "${PROJECT_DIR}/src"; then
        print_warning "Building backend..."
        cd "${PROJECT_DIR}/src"
        source venv/bin/activate
        
        # Collect static files if Django
        if [ -f "manage.py" ]; then
            python manage.py collectstatic --noinput
        fi
        
        deactivate
    fi
    
    # Build web frontend
    if check_directory "${PROJECT_DIR}/web-frontend"; then
        print_warning "Building web frontend..."
        cd "${PROJECT_DIR}/web-frontend"
        npm run build
    fi
    
    # Build mobile frontend
    if check_directory "${PROJECT_DIR}/mobile-frontend"; then
        print_warning "Building mobile frontend..."
        cd "${PROJECT_DIR}/mobile-frontend"
        npm run build
    fi
    
    # Build Docker images
    print_warning "Building Docker images..."
    cd "${PROJECT_DIR}"
    docker-compose -f docker-compose.${ENVIRONMENT}.yml build
    
    print_success "Application built successfully"
    return 0
}

# Function to provision infrastructure
provision_infrastructure() {
    print_section "Provisioning Infrastructure"
    
    if ! check_directory "${PROJECT_DIR}/infrastructure"; then
        print_warning "Infrastructure directory not found, skipping..."
        return 1
    fi
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed"
        print_warning "Please install Terraform to provision infrastructure"
        return 1
    fi
    
    cd "${PROJECT_DIR}/infrastructure/${ENVIRONMENT}"
    
    # Initialize Terraform
    print_warning "Initializing Terraform..."
    terraform init
    
    # Plan infrastructure changes
    print_warning "Planning infrastructure changes..."
    terraform plan -out=tfplan
    
    # Ask for confirmation
    read -p "Do you want to apply these infrastructure changes? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Infrastructure provisioning cancelled"
        return 1
    fi
    
    # Apply infrastructure changes
    print_warning "Applying infrastructure changes..."
    terraform apply tfplan
    
    print_success "Infrastructure provisioned successfully"
    return 0
}

# Function to deploy to Kubernetes
deploy_kubernetes() {
    print_section "Deploying to Kubernetes"
    
    if ! check_directory "${PROJECT_DIR}/deployments/kubernetes"; then
        print_warning "Kubernetes deployment directory not found, skipping..."
        return 1
    fi
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        print_warning "Please install kubectl to deploy to Kubernetes"
        return 1
    fi
    
    cd "${PROJECT_DIR}/deployments/kubernetes/${ENVIRONMENT}"
    
    # Apply Kubernetes manifests
    print_warning "Applying Kubernetes manifests..."
    kubectl apply -f .
    
    # Wait for deployments to be ready
    print_warning "Waiting for deployments to be ready..."
    kubectl rollout status deployment/fluxora-api
    kubectl rollout status deployment/fluxora-web
    
    print_success "Kubernetes deployment completed successfully"
    return 0
}

# Function to deploy using Docker Compose
deploy_docker_compose() {
    print_section "Deploying with Docker Compose"
    
    cd "${PROJECT_DIR}"
    
    # Check if Docker Compose file exists
    if [ ! -f "docker-compose.${ENVIRONMENT}.yml" ]; then
        print_error "Docker Compose file for ${ENVIRONMENT} environment not found"
        return 1
    fi
    
    # Deploy with Docker Compose
    print_warning "Deploying with Docker Compose..."
    docker-compose -f docker-compose.${ENVIRONMENT}.yml up -d
    
    print_success "Docker Compose deployment completed successfully"
    return 0
}

# Function to run database migrations
run_migrations() {
    print_section "Running Database Migrations"
    
    cd "${PROJECT_DIR}"
    
    # Run migrations based on deployment method
    if [ -f "docker-compose.${ENVIRONMENT}.yml" ]; then
        print_warning "Running migrations with Docker Compose..."
        docker-compose -f docker-compose.${ENVIRONMENT}.yml exec api python manage.py migrate
    elif command -v kubectl &> /dev/null; then
        print_warning "Running migrations with Kubernetes..."
        kubectl exec -it $(kubectl get pods -l app=fluxora-api -o jsonpath="{.items[0].metadata.name}") -- python manage.py migrate
    else
        print_warning "Running migrations locally..."
        cd "${PROJECT_DIR}/src"
        source venv/bin/activate
        python manage.py migrate
        deactivate
    fi
    
    print_success "Database migrations completed successfully"
    return 0
}

# Function to verify deployment
verify_deployment() {
    print_section "Verifying Deployment"
    
    # Get deployment URL based on environment
    case $ENVIRONMENT in
        dev)
            URL="http://localhost:8000"
            ;;
        staging)
            URL="https://staging.fluxora.example.com"
            ;;
        prod)
            URL="https://fluxora.example.com"
            ;;
        *)
            URL="http://localhost:8000"
            ;;
    esac
    
    print_warning "Checking deployment at ${URL}..."
    
    # Check if curl is installed
    if command -v curl &> /dev/null; then
        if curl -s -o /dev/null -w "%{http_code}" "${URL}/health" | grep -q "200"; then
            print_success "Deployment verified successfully"
        else
            print_error "Deployment verification failed"
            print_warning "Please check logs for more information"
        fi
    else
        print_warning "curl is not installed, skipping verification"
        print_warning "Please manually verify the deployment at ${URL}"
    fi
}

# Function to deploy application
deploy_application() {
    print_section "Deploying Fluxora to ${ENVIRONMENT} Environment"
    
    # Check prerequisites
    check_prerequisites || return 1
    
    # Run tests
    run_tests || return 1
    
    # Build application
    build_application || return 1
    
    # Provision infrastructure if needed
    if [ "$ENVIRONMENT" != "dev" ]; then
        provision_infrastructure
    fi
    
    # Deploy based on environment
    if [ "$ENVIRONMENT" = "dev" ]; then
        deploy_docker_compose
    else
        deploy_kubernetes
    fi
    
    # Run database migrations
    run_migrations
    
    # Verify deployment
    verify_deployment
    
    print_section "Deployment Complete"
    print_success "Fluxora has been deployed to the ${ENVIRONMENT} environment"
    
    # Print access information
    case $ENVIRONMENT in
        dev)
            echo "Access the application at: http://localhost:8000"
            echo "Access the dashboard at: http://localhost:3000"
            ;;
        staging)
            echo "Access the application at: https://staging.fluxora.example.com"
            echo "Access the dashboard at: https://dashboard.staging.fluxora.example.com"
            ;;
        prod)
            echo "Access the application at: https://fluxora.example.com"
            echo "Access the dashboard at: https://dashboard.fluxora.example.com"
            ;;
    esac
}

# Function to display help message
show_help() {
    echo "Deployment Script for Fluxora"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -d, --directory    Specify Fluxora project directory (default: current directory)"
    echo "  -e, --environment  Specify deployment environment (dev, staging, prod) (default: dev)"
    echo "  -s, --skip-tests   Skip running tests before deployment"
    echo "  -b, --skip-build   Skip building the application"
    echo ""
    echo "Examples:"
    echo "  $0                           # Deploy to dev environment"
    echo "  $0 -e staging                # Deploy to staging environment"
    echo "  $0 -d /path/to/fluxora -e prod # Deploy to production environment"
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
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -b|--skip-build)
            SKIP_BUILD=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
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

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_warning "Valid environments are: dev, staging, prod"
    exit 1
fi

# Deploy application
deploy_application

exit 0
