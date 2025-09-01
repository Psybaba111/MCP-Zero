#!/bin/bash

# EV Platform Setup Script
# Automates the initial project setup and configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log_info "Checking system dependencies..."
    
    local missing_deps=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        missing_deps+=("docker-compose")
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("pip3")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install the missing dependencies and run the setup again."
        log_info "Installation commands:"
        log_info "  Docker: https://docs.docker.com/get-docker/"
        log_info "  Node.js: https://nodejs.org/en/download/"
        log_info "  Python: https://www.python.org/downloads/"
        exit 1
    fi
    
    log_success "All dependencies are available"
}

# Create environment files
create_env_files() {
    log_info "Creating environment configuration files..."
    
    # Backend .env
    if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
        cat > "$PROJECT_ROOT/backend/.env" << EOF
# Database Configuration
DATABASE_URL=postgresql://ev_user:ev_password@localhost:5432/ev_platform
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Hyperswitch Payment Gateway
HYPERSWITCH_PUBLIC_KEY=your_public_key_here
HYPERSWITCH_SECRET_KEY=your_secret_key_here
HYPERSWITCH_WEBHOOK_SECRET=your_webhook_secret_here

# External Services
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_SIGNING_SECRET=your_slack_signing_secret_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
NOTION_API_KEY=your_notion_api_key_here
PAGERDUTY_API_KEY=your_pagerduty_api_key_here

# MCP-Zero Configuration
MCP_ZERO_ENDPOINT=http://localhost:8001
MCP_ZERO_ENABLED=true

# App Settings
APP_NAME=EV Platform
DEBUG=true
CORS_ORIGINS=["*"]
EOF
        log_success "Created backend/.env"
    else
        log_warning "backend/.env already exists, skipping..."
    fi
    
    # Mobile app .env
    if [ ! -f "$PROJECT_ROOT/mobile-app/.env" ]; then
        cat > "$PROJECT_ROOT/mobile-app/.env" << EOF
# API Configuration
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_HYPERSWITCH_PUBLIC_KEY=your_public_key_here

# Feature Flags
EV_OPPORTUNITY_ENABLED=false
EOF
        log_success "Created mobile-app/.env"
    else
        log_warning "mobile-app/.env already exists, skipping..."
    fi
    
    # Automation .env
    if [ ! -f "$PROJECT_ROOT/automation/.env" ]; then
        cat > "$PROJECT_ROOT/automation/.env" << EOF
# Backend API
BACKEND_API_URL=http://localhost:8000
BACKEND_API_KEY=your_api_key_here

# External Services
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_SIGNING_SECRET=your_slack_signing_secret_here
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here
PAGERDUTY_API_KEY=your_pagerduty_api_key_here
PAGERDUTY_SERVICE_ID=your_pagerduty_service_id_here

# MCP-Zero
MCP_ZERO_ENDPOINT=http://localhost:8001
MCP_ZERO_ENABLED=true
EOF
        log_success "Created automation/.env"
    else
        log_warning "automation/.env already exists, skipping..."
    fi
}

# Setup backend
setup_backend() {
    log_info "Setting up backend services..."
    
    cd "$PROJECT_ROOT/backend"
    
    # Create logs directory
    mkdir -p logs
    
    # Start services
    log_info "Starting backend services with Docker Compose..."
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "Backend services are running"
    else
        log_warning "Backend services might still be starting up..."
    fi
    
    cd "$PROJECT_ROOT"
}

# Setup mobile app
setup_mobile_app() {
    log_info "Setting up mobile app..."
    
    cd "$PROJECT_ROOT/mobile-app"
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        log_info "Installing mobile app dependencies..."
        npm install
        log_success "Mobile app dependencies installed"
    else
        log_warning "Mobile app dependencies already installed, skipping..."
    fi
    
    cd "$PROJECT_ROOT"
}

# Setup ops dashboard
setup_ops_dashboard() {
    log_info "Setting up ops dashboard..."
    
    cd "$PROJECT_ROOT/ops-dashboard"
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        log_info "Installing ops dashboard dependencies..."
        npm install
        log_success "Ops dashboard dependencies installed"
    else
        log_warning "Ops dashboard dependencies already installed, skipping..."
    fi
    
    cd "$PROJECT_ROOT"
}

# Setup automation
setup_automation() {
    log_info "Setting up automation layer..."
    
    cd "$PROJECT_ROOT/automation"
    
    # Install Python dependencies
    if [ ! -f "requirements.txt" ]; then
        cat > requirements.txt << EOF
rube>=1.0.0
aiohttp>=3.8.0
slack-sdk>=3.26.0
notion-client>=2.2.0
pagerduty>=2.1.0
python-dotenv>=1.0.0
EOF
        log_success "Created automation requirements.txt"
    fi
    
    # Install dependencies
    log_info "Installing automation dependencies..."
    pip3 install -r requirements.txt
    log_success "Automation dependencies installed"
    
    cd "$PROJECT_ROOT"
}

# Create database initialization script
create_db_init() {
    log_info "Creating database initialization script..."
    
    cd "$PROJECT_ROOT/backend"
    
    if [ ! -f "init.sql" ]; then
        cat > init.sql << EOF
-- EV Platform Database Initialization
-- This script creates the initial database structure

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_rides_user_id ON rides(user_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_owner_id ON vehicles(owner_id);
CREATE INDEX IF NOT EXISTS idx_rentals_user_id ON rentals(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_entries(user_id);

-- Insert sample data (optional)
-- INSERT INTO users (email, phone, full_name, password_hash, role) VALUES 
-- ('admin@evplatform.com', '9999999999', 'Admin User', 'hashed_password', 'admin');

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ev_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ev_user;
EOF
        log_success "Created database initialization script"
    else
        log_warning "Database initialization script already exists, skipping..."
    fi
    
    cd "$PROJECT_ROOT"
}

# Run test suite
run_tests() {
    log_info "Running test suite to verify setup..."
    
    if [ -f "$PROJECT_ROOT/scripts/test-suite.sh" ]; then
        chmod +x "$PROJECT_ROOT/scripts/test-suite.sh"
        cd "$PROJECT_ROOT"
        ./scripts/test-suite.sh
    else
        log_warning "Test suite not found, skipping..."
    fi
}

# Display next steps
show_next_steps() {
    echo ""
    echo "=========================================="
    echo "🎉 EV Platform Setup Complete! 🎉"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. 🔧 Configure Environment Variables:"
    echo "   - Edit backend/.env with your API keys"
    echo "   - Edit mobile-app/.env with your configuration"
    echo "   - Edit automation/.env with your service tokens"
    echo ""
    echo "2. 🚀 Start Services:"
    echo "   cd backend && docker-compose up -d"
    echo ""
    echo "3. 📱 Start Mobile App:"
    echo "   cd mobile-app && npx expo start"
    echo ""
    echo "4. 🖥️  Start Ops Dashboard:"
    echo "   cd ops-dashboard && npm run dev"
    echo ""
    echo "5. 🤖 Test Automation:"
    echo "   cd automation/rube && rube run playbooks/kyc_loop.yaml"
    echo ""
    echo "6. 🧪 Run Tests:"
    echo "   ./scripts/test-suite.sh"
    echo ""
    echo "📚 Documentation: README.md"
    echo "🔗 API Docs: http://localhost:8000/docs"
    echo "📊 Monitoring: http://localhost:5555 (Flower)"
    echo ""
    echo "Happy coding! 🚗⚡"
}

# Main setup function
main() {
    log_info "Starting EV Platform Setup..."
    log_info "Project root: $PROJECT_ROOT"
    log_info "Timestamp: $TIMESTAMP"
    
    echo "=========================================="
    
    # Check dependencies
    check_dependencies
    
    # Create environment files
    create_env_files
    
    # Setup database initialization
    create_db_init
    
    # Setup backend
    setup_backend
    
    # Setup mobile app
    setup_mobile_app
    
    # Setup ops dashboard
    setup_ops_dashboard
    
    # Setup automation
    setup_automation
    
    echo "=========================================="
    
    # Show next steps
    show_next_steps
}

# Run setup
main