#!/bin/bash

# Deploy EV Platform to Rube.app
# Automated deployment script with integration setup

set -e

echo "🚀 Deploying EV Platform to Rube.app"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RUBE_CLI="composio"  # Assuming Composio CLI is installed
PROJECT_NAME="ev-platform-automation"

# Helper functions
log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    if ! command -v composio &> /dev/null; then
        log_error "Composio CLI not found. Please install it first:"
        echo "npm install -g @composio/cli"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Initialize Rube project
init_rube_project() {
    log_step "Initializing Rube project..."
    
    # Login to Composio (if not already logged in)
    if ! composio whoami &> /dev/null; then
        echo "Please login to Composio first:"
        echo "composio login"
        exit 1
    fi
    
    # Create project
    composio create-project $PROJECT_NAME --template automation
    cd $PROJECT_NAME
    
    log_success "Rube project initialized"
}

# Setup integrations
setup_integrations() {
    log_step "Setting up integrations..."
    
    # Slack integration
    echo "Setting up Slack integration..."
    composio add slack
    
    # Gmail integration  
    echo "Setting up Gmail integration..."
    composio add gmail
    
    # Google Calendar integration
    echo "Setting up Google Calendar integration..."
    composio add googlecalendar
    
    # Notion integration
    echo "Setting up Notion integration..."
    composio add notion
    
    # Twilio integration
    echo "Setting up Twilio integration..."
    composio add twilio
    
    # Linear integration
    echo "Setting up Linear integration..."
    composio add linear
    
    # PagerDuty integration
    echo "Setting up PagerDuty integration..."
    composio add pagerduty
    
    log_success "Integrations configured"
}

# Deploy workflows
deploy_workflows() {
    log_step "Deploying automation workflows..."
    
    # Copy workflow files
    cp ../workflows/*.py ./workflows/
    
    # Deploy KYC approval workflow
    echo "Deploying KYC approval workflow..."
    composio deploy workflow \
        --file workflows/kyc_approval_flow.py \
        --trigger webhook \
        --webhook-path "/kyc/document-uploaded" \
        --name "kyc-approval-flow"
    
    # Deploy license expiry monitor
    echo "Deploying license expiry monitor..."
    composio deploy workflow \
        --file workflows/license_expiry_monitor.py \
        --trigger cron \
        --schedule "0 0 * * *" \
        --timezone "Asia/Kolkata" \
        --name "license-expiry-monitor"
    
    # Deploy deposit release automation
    echo "Deploying deposit release automation..."
    composio deploy workflow \
        --file workflows/deposit_release_automation.py \
        --trigger webhook \
        --webhook-path "/rental/returned" \
        --name "deposit-release-automation"
    
    # Deploy ride assignment flow
    echo "Deploying ride assignment flow..."
    composio deploy workflow \
        --file workflows/ride_assignment_flow.py \
        --trigger webhook \
        --webhook-path "/ride/payment-completed" \
        --name "ride-assignment-flow"
    
    log_success "Workflows deployed"
}

# Configure environment variables
setup_environment() {
    log_step "Setting up environment variables..."
    
    # Create .env file for Rube
    cat > .env << 'EOF'
# Backend API Configuration
BACKEND_API_URL=https://your-backend-url.com/api/v1
BACKEND_API_TOKEN=your-backend-jwt-token

# Payment Gateway
HYPERSWITCH_API_KEY=your-hyperswitch-sandbox-key
HYPERSWITCH_WEBHOOK_SECRET=your-webhook-secret

# Communication Services
SLACK_WEBHOOK_URL=your-slack-webhook-url
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number

# Documentation & Tracking
NOTION_API_KEY=your-notion-integration-token
NOTION_RUN_LOG_DB_ID=your-notion-database-id
NOTION_COMPLIANCE_DB_ID=your-compliance-db-id

# Incident Management
PAGERDUTY_API_KEY=your-pagerduty-api-key
PAGERDUTY_SERVICE_ID=your-service-id
LINEAR_TEAM_ID=your-linear-team-id

# AI Services (for document processing)
OPENAI_API_KEY=your-openai-api-key
DOCUMENT_AI_API_KEY=your-document-ai-key
EOF

    log_warning "Please update .env file with your actual API keys and URLs"
    log_success "Environment template created"
}

# Test integrations
test_integrations() {
    log_step "Testing integrations..."
    
    # Test Slack
    echo "Testing Slack integration..."
    composio test slack --action send_message --params '{"channel": "#test", "text": "EV Platform deployment test"}'
    
    # Test Gmail
    echo "Testing Gmail integration..."
    composio test gmail --action send_email --params '{"to": "test@example.com", "subject": "Test", "body": "Test email"}'
    
    # Test backend API
    echo "Testing backend API..."
    curl -f "${BACKEND_API_URL}/health" || log_warning "Backend API not responding"
    
    log_success "Integration tests completed"
}

# Configure webhooks in backend
configure_backend_webhooks() {
    log_step "Configuring backend webhooks..."
    
    # Get Rube webhook URLs
    KYC_WEBHOOK=$(composio get-webhook-url kyc-approval-flow)
    DEPOSIT_WEBHOOK=$(composio get-webhook-url deposit-release-automation)
    RIDE_WEBHOOK=$(composio get-webhook-url ride-assignment-flow)
    
    echo "Configure these webhook URLs in your backend:"
    echo "KYC Document Upload: $KYC_WEBHOOK"
    echo "Rental Return: $DEPOSIT_WEBHOOK"
    echo "Ride Payment: $RIDE_WEBHOOK"
    
    # Create webhook configuration file
    cat > webhook-config.json << EOF
{
  "webhooks": {
    "kyc_document_uploaded": "$KYC_WEBHOOK",
    "rental_returned": "$DEPOSIT_WEBHOOK", 
    "ride_payment_completed": "$RIDE_WEBHOOK"
  }
}
EOF
    
    log_success "Webhook configuration created"
}

# Setup monitoring
setup_monitoring() {
    log_step "Setting up monitoring..."
    
    # Create monitoring dashboard
    composio create-dashboard \
        --name "ev-platform-monitoring" \
        --workflows "kyc-approval-flow,license-expiry-monitor,deposit-release-automation,ride-assignment-flow"
    
    # Configure alerts
    composio create-alert \
        --name "workflow-failure-alert" \
        --condition "workflow.success_rate < 0.95" \
        --action "slack_notify" \
        --channel "#ev-platform-alerts"
    
    composio create-alert \
        --name "high-error-rate" \
        --condition "workflow.error_rate > 0.05" \
        --action "pagerduty_incident"
    
    log_success "Monitoring configured"
}

# Validate deployment
validate_deployment() {
    log_step "Validating deployment..."
    
    # Check workflow status
    if composio list-workflows | grep -q "ev-platform"; then
        log_success "Workflows deployed successfully"
    else
        log_error "Workflow deployment failed"
        exit 1
    fi
    
    # Check integrations
    if composio list-integrations | grep -q "slack\|gmail\|notion"; then
        log_success "Integrations configured"
    else
        log_warning "Some integrations may not be properly configured"
    fi
    
    log_success "Deployment validation completed"
}

# Main deployment flow
main() {
    echo "Starting EV Platform deployment to Rube.app..."
    
    check_prerequisites
    init_rube_project
    setup_integrations
    deploy_workflows
    setup_environment
    test_integrations
    configure_backend_webhooks
    setup_monitoring
    validate_deployment
    
    echo ""
    echo "🎉 EV Platform Successfully Deployed to Rube.app!"
    echo "=================================================="
    echo ""
    echo "📍 Next Steps:"
    echo "1. Update .env file with your actual API keys"
    echo "2. Configure webhook URLs in your backend"
    echo "3. Test workflows with real data"
    echo "4. Monitor execution in Rube dashboard"
    echo ""
    echo "📊 Monitoring:"
    echo "   Rube Dashboard: https://rube.app/dashboard/$PROJECT_NAME"
    echo "   Slack Alerts: #ev-platform-alerts"
    echo "   Notion Logs: Your configured database"
    echo ""
    echo "🔧 Management Commands:"
    echo "   List workflows: composio list-workflows"
    echo "   View logs: composio logs <workflow-name>"
    echo "   Test workflow: composio test-workflow <workflow-name>"
    echo ""
    echo "Happy automating! 🤖⚡"
}

# Run deployment
main "$@"