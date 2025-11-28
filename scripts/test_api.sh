#!/bin/bash

# api_tester.sh
# Tests API endpoints and generates example requests for Fluxora
#
# This script:
# - Tests API connectivity
# - Generates example API requests for common operations
# - Validates API responses
# - Creates a collection of example requests

set -euo pipefail

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Default settings
API_HOST="localhost"
API_PORT="8000"
API_BASE_URL="http://${API_HOST}:${API_PORT}"
OUTPUT_DIR="$(pwd)/api_examples"
VERBOSE=false

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

# Function to print verbose messages
print_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "$1"
    fi
}

# Function to check if curl is installed
check_curl() {
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed"
        print_warning "Please install curl to use this script"
        exit 1
    fi
}

# Function to check if API is running
check_api() {
    print_section "Checking API Availability"

    print_warning "Testing connection to API at ${API_BASE_URL}..."

    if curl -s -o /dev/null -w "%{http_code}" "${API_BASE_URL}/health" | grep -q "200"; then
        print_success "API is running and healthy"
        return 0
    else
        print_error "API is not available at ${API_BASE_URL}"
        print_warning "Make sure the API server is running (use start_services.sh)"
        return 1
    fi
}

# Function to ensure output directory exists
ensure_output_dir() {
    if [ ! -d "$OUTPUT_DIR" ]; then
        print_warning "Creating output directory: ${OUTPUT_DIR}"
        mkdir -p "$OUTPUT_DIR"
    fi
}

# Function to generate authentication token
get_auth_token() {
    print_section "Generating Authentication Token"

    local username="user@example.com"
    local password="secure_password"

    print_warning "Requesting authentication token for ${username}..."

    local response=$(curl -s -X POST "${API_BASE_URL}/api/auth/token" \
        -H "Content-Type: application/json" \
        -d "{
            \"username\": \"${username}\",
            \"password\": \"${password}\"
        }")

    print_verbose "Response: $response"

    # Extract token from response
    local token=$(echo "$response" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

    if [ -n "$token" ]; then
        print_success "Authentication token obtained"
        echo "$token"

        # Save example request to file
        cat > "${OUTPUT_DIR}/auth_example.sh" << EOF
#!/bin/bash
# Example: Authenticate and get token

curl -X POST "${API_BASE_URL}/api/auth/token" \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "user@example.com",
    "password": "secure_password"
  }'
EOF
        chmod +x "${OUTPUT_DIR}/auth_example.sh"

        return 0
    else
        print_error "Failed to obtain authentication token"
        return 1
    fi
}

# Function to test prediction endpoint
test_prediction() {
    print_section "Testing Prediction Endpoint"

    local token=$1

    print_warning "Sending prediction request..."

    local response=$(curl -s -X POST "${API_BASE_URL}/api/predict" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: ${token}" \
        -d '{
            "timestamp": "2023-08-15T14:00:00",
            "meter_id": "MT_001",
            "historical_load": [0.45, 0.48, 0.52]
        }')

    print_verbose "Response: $response"

    # Check if response contains prediction
    if echo "$response" | grep -q '"prediction"'; then
        print_success "Prediction request successful"

        # Save example request to file
        cat > "${OUTPUT_DIR}/prediction_example.sh" << EOF
#!/bin/bash
# Example: Make a prediction

curl -X POST "${API_BASE_URL}/api/predict" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: \$API_TOKEN" \\
  -d '{
    "timestamp": "2023-08-15T14:00:00",
    "meter_id": "MT_001",
    "historical_load": [0.45, 0.48, 0.52]
  }'
EOF
        chmod +x "${OUTPUT_DIR}/prediction_example.sh"

        return 0
    else
        print_error "Prediction request failed"
        return 1
    fi
}

# Function to test data retrieval endpoint
test_data_retrieval() {
    print_section "Testing Data Retrieval Endpoint"

    local token=$1

    print_warning "Sending data retrieval request..."

    local response=$(curl -s -X GET "${API_BASE_URL}/api/data/consumption" \
        -H "X-API-Key: ${token}" \
        -G --data-urlencode "start_date=2023-08-01" \
        --data-urlencode "end_date=2023-08-15" \
        --data-urlencode "meter_id=MT_001")

    print_verbose "Response: $response"

    # Check if response contains data
    if echo "$response" | grep -q '"data"'; then
        print_success "Data retrieval request successful"

        # Save example request to file
        cat > "${OUTPUT_DIR}/data_retrieval_example.sh" << EOF
#!/bin/bash
# Example: Retrieve consumption data

curl -X GET "${API_BASE_URL}/api/data/consumption" \\
  -H "X-API-Key: \$API_TOKEN" \\
  -G \\
  --data-urlencode "start_date=2023-08-01" \\
  --data-urlencode "end_date=2023-08-15" \\
  --data-urlencode "meter_id=MT_001"
EOF
        chmod +x "${OUTPUT_DIR}/data_retrieval_example.sh"

        return 0
    else
        print_error "Data retrieval request failed"
        return 1
    fi
}

# Function to create a README file with API documentation
create_api_readme() {
    print_section "Creating API Documentation"

    cat > "${OUTPUT_DIR}/README.md" << EOF
# Fluxora API Examples

This directory contains example scripts for interacting with the Fluxora API.

## Authentication

Before using the API, you need to obtain an authentication token:

\`\`\`bash
./auth_example.sh
\`\`\`

This will return a JSON response containing a token. Set this token as an environment variable:

\`\`\`bash
export API_TOKEN="your_token_here"
\`\`\`

## Making Predictions

To make energy consumption predictions:

\`\`\`bash
./prediction_example.sh
\`\`\`

## Retrieving Data

To retrieve historical consumption data:

\`\`\`bash
./data_retrieval_example.sh
\`\`\`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/auth/token | POST | Obtain authentication token |
| /api/predict | POST | Make energy consumption predictions |
| /api/data/consumption | GET | Retrieve historical consumption data |
| /health | GET | Check API health status |

## Request Headers

- Content-Type: application/json
- X-API-Key: Your authentication token

## Common Parameters

- timestamp: ISO format datetime (e.g., "2023-08-15T14:00:00")
- meter_id: Meter identifier (e.g., "MT_001")
- start_date: Start date for data retrieval (e.g., "2023-08-01")
- end_date: End date for data retrieval (e.g., "2023-08-15")
EOF

    print_success "API documentation created at ${OUTPUT_DIR}/README.md"
}

# Function to run all tests
run_all_tests() {
    print_section "Running All API Tests"

    # Check if API is available
    if ! check_api; then
        return 1
    fi

    # Ensure output directory exists
    ensure_output_dir

    # Get authentication token
    local token=$(get_auth_token)
    if [ -z "$token" ]; then
        return 1
    fi

    # Test prediction endpoint
    test_prediction "$token"

    # Test data retrieval endpoint
    test_data_retrieval "$token"

    # Create API documentation
    create_api_readme

    print_section "API Testing Complete"
    print_success "All API examples have been generated in ${OUTPUT_DIR}"

    echo -e "\nTo use these examples:"
    echo "1. Start the Fluxora API server (if not already running)"
    echo "2. Navigate to ${OUTPUT_DIR}"
    echo "3. Run the example scripts as described in README.md"
}

# Function to display help message
show_help() {
    echo "API Tester for Fluxora"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -H, --host         Specify API host (default: localhost)"
    echo "  -p, --port         Specify API port (default: 8000)"
    echo "  -o, --output       Specify output directory for examples (default: ./api_examples)"
    echo "  -v, --verbose      Enable verbose output"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run all tests with default settings"
    echo "  $0 -H api.example.com -p 443 # Test API at api.example.com:443"
    echo "  $0 -o ~/fluxora/api_examples # Save examples to specified directory"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -H|--host)
            API_HOST="$2"
            API_BASE_URL="http://${API_HOST}:${API_PORT}"
            shift 2
            ;;
        -p|--port)
            API_PORT="$2"
            API_BASE_URL="http://${API_HOST}:${API_PORT}"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if curl is installed
check_curl

# Run all tests
run_all_tests

exit 0
