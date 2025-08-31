#!/bin/bash

# EV Platform API Test Suite
# Comprehensive cURL tests for all endpoints

set -e

# Configuration
BASE_URL="http://localhost:8000/api/v1"
TEST_EMAIL="test@example.com"
TEST_PHONE="+919876543210"
TEST_NAME="Test User"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper functions
log_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED_TESTS=$((PASSED_TESTS + 1))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAILED_TESTS=$((FAILED_TESTS + 1))
}

# Test API endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=$4
    local auth_token=$5
    
    local headers=""
    if [ ! -z "$auth_token" ]; then
        headers="-H \"Authorization: Bearer $auth_token\""
    fi
    
    local curl_cmd="curl -s -w \"%{http_code}\" -X $method"
    if [ ! -z "$data" ]; then
        curl_cmd="$curl_cmd -H \"Content-Type: application/json\" -d '$data'"
    fi
    if [ ! -z "$headers" ]; then
        curl_cmd="$curl_cmd $headers"
    fi
    curl_cmd="$curl_cmd \"$BASE_URL$endpoint\""
    
    local response=$(eval $curl_cmd)
    local status_code="${response: -3}"
    local body="${response%???}"
    
    if [ "$status_code" = "$expected_status" ]; then
        log_pass "$method $endpoint -> $status_code"
        echo "$body"
    else
        log_fail "$method $endpoint -> Expected $expected_status, got $status_code"
        echo "Response: $body"
    fi
}

echo "🚀 Starting EV Platform API Tests"
echo "=================================="

# Test 1: Health Check
log_test "Health check"
test_endpoint "GET" "/health" "" "200"

# Test 2: User Registration
log_test "User registration"
REGISTER_DATA="{\"email\":\"$TEST_EMAIL\",\"phone\":\"$TEST_PHONE\",\"full_name\":\"$TEST_NAME\",\"role\":\"passenger\"}"
REGISTER_RESPONSE=$(test_endpoint "POST" "/users/register" "$REGISTER_DATA" "201")

# Test 3: User Login
log_test "User login"
LOGIN_DATA="{\"email\":\"$TEST_EMAIL\"}"
LOGIN_RESPONSE=$(test_endpoint "POST" "/users/login" "$LOGIN_DATA" "200")
AUTH_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$AUTH_TOKEN" ]; then
    log_pass "Authentication token obtained"
else
    log_fail "Failed to get authentication token"
    exit 1
fi

# Test 4: Get User Profile
log_test "Get user profile"
test_endpoint "GET" "/users/me" "" "200" "$AUTH_TOKEN"

# Test 5: Create Ride
log_test "Create ride booking"
RIDE_DATA="{\"pickup_lat\":12.9716,\"pickup_lng\":77.5946,\"pickup_address\":\"Bangalore Central\",\"drop_lat\":12.9352,\"drop_lng\":77.6245,\"drop_address\":\"Whitefield\",\"vehicle_type\":\"scooter\"}"
RIDE_RESPONSE=$(test_endpoint "POST" "/rides" "$RIDE_DATA" "201" "$AUTH_TOKEN")
RIDE_ID=$(echo "$RIDE_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

# Test 6: Create Parcel
log_test "Create parcel delivery"
PARCEL_DATA="{\"pickup_lat\":12.9716,\"pickup_lng\":77.5946,\"pickup_address\":\"Bangalore Central\",\"drop_lat\":12.9352,\"drop_lng\":77.6245,\"drop_address\":\"Whitefield\",\"recipient_name\":\"John Doe\",\"recipient_phone\":\"+919876543211\",\"weight_kg\":2.5}"
PARCEL_RESPONSE=$(test_endpoint "POST" "/parcels" "$PARCEL_DATA" "201" "$AUTH_TOKEN")
PARCEL_ID=$(echo "$PARCEL_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

# Test 7: Create Vehicle Listing
log_test "Create vehicle listing"
VEHICLE_DATA="{\"vehicle_type\":\"car\",\"make\":\"Tata\",\"model\":\"Nexon EV\",\"year\":2023,\"registration_number\":\"KA01AB1234\",\"battery_capacity\":30.2,\"range_km\":312,\"hourly_rate\":150,\"daily_rate\":2500,\"deposit_amount\":5000,\"location_lat\":12.9716,\"location_lng\":77.5946,\"photos\":[\"https://example.com/photo1.jpg\"],\"features\":[\"AC\",\"GPS\",\"Fast Charging\"]}"
VEHICLE_RESPONSE=$(test_endpoint "POST" "/vehicles" "$VEHICLE_DATA" "201" "$AUTH_TOKEN")
VEHICLE_ID=$(echo "$VEHICLE_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

# Test 8: Search Vehicles
log_test "Search vehicles"
test_endpoint "GET" "/vehicles?vehicle_type=car&available_only=true" "" "200" "$AUTH_TOKEN"

# Test 9: Create Payment Intent
if [ ! -z "$RIDE_ID" ]; then
    log_test "Create payment intent for ride"
    PAYMENT_DATA="{\"entity_type\":\"ride\",\"entity_id\":\"$RIDE_ID\",\"amount\":150}"
    PAYMENT_RESPONSE=$(test_endpoint "POST" "/payments/intents" "$PAYMENT_DATA" "201" "$AUTH_TOKEN")
    PAYMENT_INTENT_ID=$(echo "$PAYMENT_RESPONSE" | grep -o '"payment_intent_id":"[^"]*"' | cut -d'"' -f4)
fi

# Test 10: Simulate Payment Webhook
if [ ! -z "$PAYMENT_INTENT_ID" ]; then
    log_test "Simulate payment webhook"
    WEBHOOK_DATA="{\"event_type\":\"payment_intent.succeeded\",\"payment_intent_id\":\"$PAYMENT_INTENT_ID\",\"status\":\"succeeded\",\"amount\":15000,\"currency\":\"INR\"}"
    test_endpoint "POST" "/payments/webhooks" "$WEBHOOK_DATA" "200"
fi

# Test 11: Create Reward Event
log_test "Create reward event"
REWARD_DATA="{\"event_type\":\"ride_completed\",\"entity_type\":\"ride\",\"entity_id\":\"$RIDE_ID\",\"metadata\":{\"fare\":150,\"vehicle_type\":\"scooter\"}}"
test_endpoint "POST" "/rewards/events" "$REWARD_DATA" "201" "$AUTH_TOKEN"

# Test 12: Get Reward Balance
log_test "Get reward balance"
test_endpoint "GET" "/rewards/balance" "" "200" "$AUTH_TOKEN"

# Test 13: Upload KYC Document
log_test "Upload KYC document"
KYC_DATA="{\"document_type\":\"license\",\"document_url\":\"https://example.com/license.jpg\",\"extracted_data\":{\"license_number\":\"DL1234567890\",\"expiry_date\":\"2025-12-31\"}}"
test_endpoint "POST" "/users/kyc/documents" "$KYC_DATA" "201" "$AUTH_TOKEN"

# Test 14: Audit Logs
log_test "Get audit logs"
test_endpoint "GET" "/audit/my?limit=10" "" "200" "$AUTH_TOKEN"

# Test 15: KYC Event
log_test "KYC requested event"
test_endpoint "POST" "/users/events/kyc.requested" "" "200" "$AUTH_TOKEN"

# Test 16: Create Rental (if vehicle exists)
if [ ! -z "$VEHICLE_ID" ]; then
    log_test "Create vehicle rental"
    START_TIME=$(date -d "+1 hour" --iso-8601=seconds)
    END_TIME=$(date -d "+5 hours" --iso-8601=seconds)
    RENTAL_DATA="{\"vehicle_id\":\"$VEHICLE_ID\",\"start_time\":\"$START_TIME\",\"end_time\":\"$END_TIME\"}"
    RENTAL_RESPONSE=$(test_endpoint "POST" "/rentals" "$RENTAL_DATA" "201" "$AUTH_TOKEN")
    RENTAL_ID=$(echo "$RENTAL_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
fi

# Test 17: List User's Rides
log_test "List user rides"
test_endpoint "GET" "/rides" "" "200" "$AUTH_TOKEN"

# Test 18: List User's Vehicles
log_test "List user vehicles"
test_endpoint "GET" "/vehicles/my/listings" "" "200" "$AUTH_TOKEN"

# Test 19: Metrics Endpoint
log_test "Get system metrics"
test_endpoint "GET" "/metrics" "" "200"

# Test 20: Invalid Endpoint (should return 404)
log_test "Invalid endpoint (should fail)"
test_endpoint "GET" "/invalid/endpoint" "" "404"

# Summary
echo ""
echo "=================================="
echo "🏁 Test Summary"
echo "=================================="
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo "Pass Rate: $PASS_RATE%"

if [ $PASS_RATE -ge 95 ]; then
    echo -e "${GREEN}✅ Test suite PASSED (≥95% success rate)${NC}"
    exit 0
else
    echo -e "${RED}❌ Test suite FAILED (<95% success rate)${NC}"
    echo ""
    echo "💡 Actionable hints for failures:"
    echo "1. Ensure backend is running on port 8000"
    echo "2. Check database connection"
    echo "3. Verify environment variables are set"
    echo "4. Check logs for specific error details"
    exit 1
fi