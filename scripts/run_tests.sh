#!/bin/bash

# run_tests.sh
# Executes tests for different Fluxora components with reporting
#
# This script:
# - Runs backend tests (Python/pytest)
# - Runs frontend tests (JavaScript/Jest)
# - Runs integration tests
# - Generates test reports

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
REPORTS_DIR="${PROJECT_DIR}/test_reports"

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

# Function to ensure reports directory exists
ensure_reports_dir() {
    if [ ! -d "$REPORTS_DIR" ]; then
        print_warning "Creating reports directory: ${REPORTS_DIR}"
        mkdir -p "$REPORTS_DIR"
    fi
}

# Function to run backend tests
run_backend_tests() {
    print_section "Running Backend Tests"
    
    if ! check_directory "${PROJECT_DIR}/src"; then
        print_warning "Backend source directory not found, skipping..."
        return 1
    fi
    
    if ! check_directory "${PROJECT_DIR}/backend/tests"; then
        print_warning "Backend tests directory not found, skipping..."
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
    
    # Run pytest with coverage
    print_warning "Running backend tests with pytest..."
    
    # Create test command with appropriate options
    TEST_CMD="python -m pytest ../backend/tests/ --verbose"
    
    # Add coverage if pytest-cov is installed
    if pip list | grep -q pytest-cov; then
        TEST_CMD="${TEST_CMD} --cov=. --cov-report=term --cov-report=html:${REPORTS_DIR}/backend_coverage"
    fi
    
    # Add JUnit XML report
    TEST_CMD="${TEST_CMD} --junitxml=${REPORTS_DIR}/backend_tests.xml"
    
    # Run the tests
    eval $TEST_CMD
    
    BACKEND_EXIT_CODE=$?
    
    # Deactivate virtual environment
    deactivate
    
    if [ $BACKEND_EXIT_CODE -eq 0 ]; then
        print_success "Backend tests completed successfully"
    else
        print_error "Backend tests failed with exit code $BACKEND_EXIT_CODE"
    fi
    
    return $BACKEND_EXIT_CODE
}

# Function to run web frontend tests
run_web_frontend_tests() {
    print_section "Running Web Frontend Tests"
    
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
    
    # Run Jest tests
    print_warning "Running web frontend tests with Jest..."
    
    # Create test command with appropriate options
    TEST_CMD="npm test -- --ci --coverage --reporters=default --reporters=jest-junit"
    
    # Set Jest JUnit output file
    export JEST_JUNIT_OUTPUT_DIR="${REPORTS_DIR}"
    export JEST_JUNIT_OUTPUT_NAME="web_frontend_tests.xml"
    
    # Run the tests
    eval $TEST_CMD
    
    WEB_EXIT_CODE=$?
    
    # Copy coverage report to reports directory
    if [ -d "coverage" ]; then
        mkdir -p "${REPORTS_DIR}/web_frontend_coverage"
        cp -r coverage/* "${REPORTS_DIR}/web_frontend_coverage/"
    fi
    
    if [ $WEB_EXIT_CODE -eq 0 ]; then
        print_success "Web frontend tests completed successfully"
    else
        print_error "Web frontend tests failed with exit code $WEB_EXIT_CODE"
    fi
    
    return $WEB_EXIT_CODE
}

# Function to run mobile frontend tests
run_mobile_frontend_tests() {
    print_section "Running Mobile Frontend Tests"
    
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
    
    # Run Jest tests
    print_warning "Running mobile frontend tests with Jest..."
    
    # Create test command with appropriate options
    TEST_CMD="npm test -- --ci --coverage --reporters=default --reporters=jest-junit"
    
    # Set Jest JUnit output file
    export JEST_JUNIT_OUTPUT_DIR="${REPORTS_DIR}"
    export JEST_JUNIT_OUTPUT_NAME="mobile_frontend_tests.xml"
    
    # Run the tests
    eval $TEST_CMD
    
    MOBILE_EXIT_CODE=$?
    
    # Copy coverage report to reports directory
    if [ -d "coverage" ]; then
        mkdir -p "${REPORTS_DIR}/mobile_frontend_coverage"
        cp -r coverage/* "${REPORTS_DIR}/mobile_frontend_coverage/"
    fi
    
    if [ $MOBILE_EXIT_CODE -eq 0 ]; then
        print_success "Mobile frontend tests completed successfully"
    else
        print_error "Mobile frontend tests failed with exit code $MOBILE_EXIT_CODE"
    fi
    
    return $MOBILE_EXIT_CODE
}

# Function to run integration tests
run_integration_tests() {
    print_section "Running Integration Tests"
    
    if ! check_directory "${PROJECT_DIR}/backend/tests/integration"; then
        print_warning "Integration tests directory not found, skipping..."
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
    
    # Run integration tests
    print_warning "Running integration tests..."
    
    # Create test command with appropriate options
    TEST_CMD="python -m pytest backend/tests/integration/ --verbose"
    
    # Add JUnit XML report
    TEST_CMD="${TEST_CMD} --junitxml=${REPORTS_DIR}/integration_tests.xml"
    
    # Run the tests
    eval $TEST_CMD
    
    INTEGRATION_EXIT_CODE=$?
    
    # Deactivate virtual environment
    deactivate
    
    if [ $INTEGRATION_EXIT_CODE -eq 0 ]; then
        print_success "Integration tests completed successfully"
    else
        print_error "Integration tests failed with exit code $INTEGRATION_EXIT_CODE"
    fi
    
    return $INTEGRATION_EXIT_CODE
}

# Function to generate test report summary
generate_test_summary() {
    print_section "Generating Test Summary"
    
    # Create summary file
    SUMMARY_FILE="${REPORTS_DIR}/test_summary.md"
    
    echo "# Fluxora Test Summary" > $SUMMARY_FILE
    echo "" >> $SUMMARY_FILE
    echo "Generated on: $(date)" >> $SUMMARY_FILE
    echo "" >> $SUMMARY_FILE
    
    # Add backend test results
    echo "## Backend Tests" >> $SUMMARY_FILE
    if [ -f "${REPORTS_DIR}/backend_tests.xml" ]; then
        # Extract test counts from XML
        BACKEND_TESTS=$(grep -o 'tests="[0-9]*"' "${REPORTS_DIR}/backend_tests.xml" | head -1 | cut -d'"' -f2)
        BACKEND_FAILURES=$(grep -o 'failures="[0-9]*"' "${REPORTS_DIR}/backend_tests.xml" | head -1 | cut -d'"' -f2)
        BACKEND_ERRORS=$(grep -o 'errors="[0-9]*"' "${REPORTS_DIR}/backend_tests.xml" | head -1 | cut -d'"' -f2)
        
        echo "- Total tests: $BACKEND_TESTS" >> $SUMMARY_FILE
        echo "- Failures: $BACKEND_FAILURES" >> $SUMMARY_FILE
        echo "- Errors: $BACKEND_ERRORS" >> $SUMMARY_FILE
        
        if [ "$BACKEND_FAILURES" -eq 0 ] && [ "$BACKEND_ERRORS" -eq 0 ]; then
            echo "- Status: ✅ PASSED" >> $SUMMARY_FILE
        else
            echo "- Status: ❌ FAILED" >> $SUMMARY_FILE
        fi
    else
        echo "- No backend test results found" >> $SUMMARY_FILE
    fi
    echo "" >> $SUMMARY_FILE
    
    # Add web frontend test results
    echo "## Web Frontend Tests" >> $SUMMARY_FILE
    if [ -f "${REPORTS_DIR}/web_frontend_tests.xml" ]; then
        # Extract test counts from XML
        WEB_TESTS=$(grep -o 'tests="[0-9]*"' "${REPORTS_DIR}/web_frontend_tests.xml" | head -1 | cut -d'"' -f2)
        WEB_FAILURES=$(grep -o 'failures="[0-9]*"' "${REPORTS_DIR}/web_frontend_tests.xml" | head -1 | cut -d'"' -f2)
        
        echo "- Total tests: $WEB_TESTS" >> $SUMMARY_FILE
        echo "- Failures: $WEB_FAILURES" >> $SUMMARY_FILE
        
        if [ "$WEB_FAILURES" -eq 0 ]; then
            echo "- Status: ✅ PASSED" >> $SUMMARY_FILE
        else
            echo "- Status: ❌ FAILED" >> $SUMMARY_FILE
        fi
    else
        echo "- No web frontend test results found" >> $SUMMARY_FILE
    fi
    echo "" >> $SUMMARY_FILE
    
    # Add mobile frontend test results
    echo "## Mobile Frontend Tests" >> $SUMMARY_FILE
    if [ -f "${REPORTS_DIR}/mobile_frontend_tests.xml" ]; then
        # Extract test counts from XML
        MOBILE_TESTS=$(grep -o 'tests="[0-9]*"' "${REPORTS_DIR}/mobile_frontend_tests.xml" | head -1 | cut -d'"' -f2)
        MOBILE_FAILURES=$(grep -o 'failures="[0-9]*"' "${REPORTS_DIR}/mobile_frontend_tests.xml" | head -1 | cut -d'"' -f2)
        
        echo "- Total tests: $MOBILE_TESTS" >> $SUMMARY_FILE
        echo "- Failures: $MOBILE_FAILURES" >> $SUMMARY_FILE
        
        if [ "$MOBILE_FAILURES" -eq 0 ]; then
            echo "- Status: ✅ PASSED" >> $SUMMARY_FILE
        else
            echo "- Status: ❌ FAILED" >> $SUMMARY_FILE
        fi
    else
        echo "- No mobile frontend test results found" >> $SUMMARY_FILE
    fi
    echo "" >> $SUMMARY_FILE
    
    # Add integration test results
    echo "## Integration Tests" >> $SUMMARY_FILE
    if [ -f "${REPORTS_DIR}/integration_tests.xml" ]; then
        # Extract test counts from XML
        INTEGRATION_TESTS=$(grep -o 'tests="[0-9]*"' "${REPORTS_DIR}/integration_tests.xml" | head -1 | cut -d'"' -f2)
        INTEGRATION_FAILURES=$(grep -o 'failures="[0-9]*"' "${REPORTS_DIR}/integration_tests.xml" | head -1 | cut -d'"' -f2)
        INTEGRATION_ERRORS=$(grep -o 'errors="[0-9]*"' "${REPORTS_DIR}/integration_tests.xml" | head -1 | cut -d'"' -f2)
        
        echo "- Total tests: $INTEGRATION_TESTS" >> $SUMMARY_FILE
        echo "- Failures: $INTEGRATION_FAILURES" >> $SUMMARY_FILE
        echo "- Errors: $INTEGRATION_ERRORS" >> $SUMMARY_FILE
        
        if [ "$INTEGRATION_FAILURES" -eq 0 ] && [ "$INTEGRATION_ERRORS" -eq 0 ]; then
            echo "- Status: ✅ PASSED" >> $SUMMARY_FILE
        else
            echo "- Status: ❌ FAILED" >> $SUMMARY_FILE
        fi
    else
        echo "- No integration test results found" >> $SUMMARY_FILE
    fi
    echo "" >> $SUMMARY_FILE
    
    # Add coverage information
    echo "## Coverage Reports" >> $SUMMARY_FILE
    echo "- Backend coverage: [HTML Report](./backend_coverage/index.html)" >> $SUMMARY_FILE
    echo "- Web frontend coverage: [HTML Report](./web_frontend_coverage/lcov-report/index.html)" >> $SUMMARY_FILE
    echo "- Mobile frontend coverage: [HTML Report](./mobile_frontend_coverage/lcov-report/index.html)" >> $SUMMARY_FILE
    
    print_success "Test summary generated at ${SUMMARY_FILE}"
}

# Function to run all tests
run_all_tests() {
    print_section "Running All Tests"
    
    # Ensure reports directory exists
    ensure_reports_dir
    
    # Run all test suites
    run_backend_tests
    BACKEND_RESULT=$?
    
    run_web_frontend_tests
    WEB_RESULT=$?
    
    run_mobile_frontend_tests
    MOBILE_RESULT=$?
    
    run_integration_tests
    INTEGRATION_RESULT=$?
    
    # Generate test summary
    generate_test_summary
    
    print_section "Test Execution Complete"
    
    # Print overall status
    if [ $BACKEND_RESULT -eq 0 ] && [ $WEB_RESULT -eq 0 ] && [ $MOBILE_RESULT -eq 0 ] && [ $INTEGRATION_RESULT -eq 0 ]; then
        print_success "All tests passed successfully"
        echo "Test reports are available in: ${REPORTS_DIR}"
        return 0
    else
        print_error "Some tests failed"
        echo "Test reports are available in: ${REPORTS_DIR}"
        return 1
    fi
}

# Function to display help message
show_help() {
    echo "Test Runner for Fluxora"
    echo ""
    echo "Usage: $0 [options] [component]"
    echo ""
    echo "Components:"
    echo "  backend            Run backend tests"
    echo "  web                Run web frontend tests"
    echo "  mobile             Run mobile frontend tests"
    echo "  integration        Run integration tests"
    echo "  all                Run all tests (default)"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -d, --directory    Specify Fluxora project directory (default: current directory)"
    echo "  -r, --reports      Specify reports output directory (default: ./test_reports)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run all tests"
    echo "  $0 backend                   # Run only backend tests"
    echo "  $0 -d /path/to/fluxora web   # Run web tests in specific directory"
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
        -r|--reports)
            REPORTS_DIR="$2"
            shift 2
            ;;
        backend|web|mobile|integration|all)
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
        ensure_reports_dir
        run_backend_tests
        ;;
    web)
        ensure_reports_dir
        run_web_frontend_tests
        ;;
    mobile)
        ensure_reports_dir
        run_mobile_frontend_tests
        ;;
    integration)
        ensure_reports_dir
        run_integration_tests
        ;;
    all)
        run_all_tests
        ;;
esac

exit 0
