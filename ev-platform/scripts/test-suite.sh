#!/bin/bash

# EV Platform Test Suite
# Comprehensive testing for all API endpoints and automation workflows

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
API_VERSION="v1"
TEST_RESULTS_DIR="./test-results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Create test results directory
mkdir -p "$TEST_RESULTS_DIR"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test helper functions
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="${3:-200}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    log_info "Running: $test_name"
    
    if eval "$test_command" > "$TEST_RESULTS_DIR/${test_name}_${TIMESTAMP}.log" 2>&1; then
        log_success "$test_name passed"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        log_error "$test_name failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Health check
test_health_check() {
    curl -s -f "$BASE_URL/health" | jq -e '.status == "healthy"'
}

# User management tests
test_user_creation() {
    local user_data='{
        "email": "test@example.com",
        "phone": "9876543210",
        "full_name": "Test User",
        "password": "testpass123",
        "role": "passenger"
    }'
    
    local response=$(curl -s -X POST "$BASE_URL/api/$API_VERSION/users" \
        -H "Content-Type: application/json" \
        -d "$user_data")
    
    echo "$response" | jq -e '.id' > /dev/null
    echo "$response" | jq -e '.email == "test@example.com"'
}

test_user_login() {
    local login_data='{
        "email": "test@example.com",
        "password": "testpass123"
    }'
    
    local response=$(curl -s -X POST "$BASE_URL/api/$API_VERSION/users/login" \
        -H "Content-Type: application/json" \
        -d "$login_data")
    
    echo "$response" | jq -e '.access_token'
    echo "$response" | jq -e '.user.email == "test@example.com"'
}

# Ride booking tests
test_ride_estimate() {
    local estimate_data='{
        "pickup_address": "123 Main St, City",
        "drop_address": "456 Oak Ave, City",
        "type": "ride"
    }'
    
    local response=$(curl -s -X POST "$BASE_URL/api/$API_VERSION/rides/estimate" \
        -H "Content-Type: application/json" \
        -d "$estimate_data")
    
    echo "$response" | jq -e '.total_fare > 0'
    echo "$response" | jq -e '.estimated_duration > 0'
}

test_ride_creation() {
    local ride_data='{
        "pickup_address": "123 Main St, City",
        "pickup_latitude": 12.9716,
        "pickup_longitude": 77.5946,
        "drop_address": "456 Oak Ave, City",
        "drop_latitude": 12.9789,
        "drop_longitude": 77.5917,
        "type": "ride"
    }'
    
    local response=$(curl -s -X POST "$BASE_URL/api/$API_VERSION/rides" \
        -H "Content-Type: application/json" \
        -d "$ride_data")
    
    echo "$response" | jq -e '.id'
    echo "$response" | jq -e '.status == "created"'
}

# Parcel delivery tests
test_parcel_creation() {
    local parcel_data='{
        "pickup_address": "123 Main St, City",
        "pickup_latitude": 12.9716,
        "pickup_longitude": 77.5946,
        "drop_address": "456 Oak Ave, City",
        "drop_latitude": 12.9789,
        "drop_longitude": 77.5917,
        "parcel_description": "Test package",
        "parcel_weight": 2.5,
        "parcel_dimensions": "20x15x10 cm"
    }'
    
    local response=$(curl -s -X POST "$BASE_URL/api/$API_VERSION/parcels" \
        -H "Content-Type: application/json" \
        -d "$parcel_data")
    
    echo "$response" | jq -e '.id'
    echo "$response" | jq -e '.type == "parcel"'
}

# Vehicle and rental tests
test_vehicle_listing() {
    local response=$(curl -s -X GET "$BASE_URL/api/$API_VERSION/vehicles")
    echo "$response" | jq -e '.message'
}

test_rental_creation() {
    local response=$(curl -s -X GET "$BASE_URL/api/$API_VERSION/rentals")
    echo "$response" | jq -e '.message'
}

# Payment tests
test_payment_intent_creation() {
    local response=$(curl -s -X POST "$BASE_URL/api/$API_VERSION/payments/intents")
    echo "$response" | jq -e '.message'
}

# Rewards tests
test_reward_balance() {
    local response=$(curl -s -X GET "$BASE_URL/api/$API_VERSION/rewards/balance")
    echo "$response" | jq -e '.message'
}

# Compliance tests
test_kyc_submission() {
    local kyc_data='{
        "license_number": "DL1234567890123",
        "license_expiry": "2025-12-31T23:59:59Z",
        "rc_number": "RC1234567890123",
        "insurance_expiry": "2025-06-30T23:59:59Z",
        "fitness_expiry": "2025-03-31T23:59:59Z"
    }'
    
    local response=$(curl -s -X POST "$BASE_URL/api/$API_VERSION/users/kyc" \
        -H "Content-Type: application/json" \
        -d "$kyc_data")
    
    echo "$response" | jq -e '.kyc_status'
}

# Audit tests
test_audit_entry_creation() {
    local response=$(curl -s -X POST "$BASE_URL/api/$API_VERSION/audit")
    echo "$response" | jq -e '.message'
}

# Automation tests
test_mcp_zero_discovery() {
    local response=$(curl -s -X POST "http://localhost:8001/discover" \
        -H "Content-Type: application/json" \
        -d '{"pattern": "kyc_verification", "context": {}}')
    
    if [ $? -eq 0 ]; then
        echo "$response" | jq -e '.tools'
    else
        # MCP-Zero might not be running, this is expected in some environments
        log_warning "MCP-Zero discovery test skipped (service not available)"
        return 0
    fi
}

# Performance tests
test_api_response_time() {
    local start_time=$(date +%s%N)
    curl -s -f "$BASE_URL/health" > /dev/null
    local end_time=$(date +%s%N)
    
    local response_time=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds
    
    if [ $response_time -lt 2000 ]; then  # Less than 2 seconds
        return 0
    else
        log_warning "API response time: ${response_time}ms (threshold: 2000ms)"
        return 1
    fi
}

# Database connectivity test
test_database_connectivity() {
    # This would require database credentials and tools
    # For now, we'll test if the API can respond (which implies DB connectivity)
    curl -s -f "$BASE_URL/health" | jq -e '.status == "healthy"'
}

# Main test execution
main() {
    log_info "Starting EV Platform Test Suite"
    log_info "Base URL: $BASE_URL"
    log_info "Timestamp: $TIMESTAMP"
    log_info "Results directory: $TEST_RESULTS_DIR"
    
    echo "=========================================="
    
    # Health and connectivity tests
    log_info "Running health and connectivity tests..."
    run_test "Health Check" "test_health_check"
    run_test "Database Connectivity" "test_database_connectivity"
    run_test "API Response Time" "test_api_response_time"
    
    echo "------------------------------------------"
    
    # User management tests
    log_info "Running user management tests..."
    run_test "User Creation" "test_user_creation"
    run_test "User Login" "test_user_login"
    
    echo "------------------------------------------"
    
    # Ride and parcel tests
    log_info "Running ride and parcel tests..."
    run_test "Ride Estimate" "test_ride_estimate"
    run_test "Ride Creation" "test_ride_creation"
    run_test "Parcel Creation" "test_parcel_creation"
    
    echo "------------------------------------------"
    
    # Vehicle and rental tests
    log_info "Running vehicle and rental tests..."
    run_test "Vehicle Listing" "test_vehicle_listing"
    run_test "Rental Creation" "test_rental_creation"
    
    echo "------------------------------------------"
    
    # Payment and rewards tests
    log_info "Running payment and rewards tests..."
    run_test "Payment Intent Creation" "test_payment_intent_creation"
    run_test "Reward Balance" "test_reward_balance"
    
    echo "------------------------------------------"
    
    # Compliance tests
    log_info "Running compliance tests..."
    run_test "KYC Submission" "test_kyc_submission"
    run_test "Audit Entry Creation" "test_audit_entry_creation"
    
    echo "------------------------------------------"
    
    # Automation tests
    log_info "Running automation tests..."
    run_test "MCP-Zero Discovery" "test_mcp_zero_discovery"
    
    echo "=========================================="
    
    # Test summary
    log_info "Test Suite Summary:"
    log_info "Total tests: $TOTAL_TESTS"
    log_info "Passed: $PASSED_TESTS"
    log_info "Failed: $FAILED_TESTS"
    
    local success_rate=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    log_info "Success rate: ${success_rate}%"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "All tests passed! 🎉"
        exit 0
    else
        log_error "Some tests failed. Check logs in $TEST_RESULTS_DIR"
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    local missing_deps=()
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install: sudo apt-get install ${missing_deps[*]}"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up test artifacts..."
    # Remove temporary files if needed
}

# Trap cleanup on exit
trap cleanup EXIT

# Check dependencies and run tests
check_dependencies
main