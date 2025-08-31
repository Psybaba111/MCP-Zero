#!/bin/bash

# EV Platform MVP Setup Script
# Automated setup for development environment

set -e

echo "🚀 Setting up EV Platform MVP..."
echo "================================"

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js 18+ for mobile development."
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Setup environment files
setup_environment() {
    echo "🔧 Setting up environment files..."
    
    # Backend environment
    if [ ! -f backend/.env ]; then
        cp backend/.env.example backend/.env
        echo "✅ Created backend/.env from template"
        echo "⚠️  Please update backend/.env with your API keys"
    fi
    
    # Mobile environment
    if [ ! -f mobile/.env ]; then
        cat > mobile/.env << EOF
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
EV_OPPORTUNITY_ENABLED=false
EOF
        echo "✅ Created mobile/.env"
    fi
    
    # Automation environment
    if [ ! -f automation/.env ]; then
        cat > automation/.env << EOF
BACKEND_API_URL=http://localhost:8000/api/v1
OPENAI_API_KEY=your-openai-key
NOTION_API_KEY=your-notion-key
SLACK_WEBHOOK_URL=your-slack-webhook
EOF
        echo "✅ Created automation/.env"
        echo "⚠️  Please update automation/.env with your API keys"
    fi
}

# Create missing directories
setup_directories() {
    echo "📁 Creating directory structure..."
    
    mkdir -p backend/routers
    mkdir -p backend/services
    mkdir -p backend/schemas
    mkdir -p backend/middleware
    mkdir -p mobile/src/screens/auth
    mkdir -p mobile/src/screens/booking
    mkdir -p mobile/src/contexts
    mkdir -p mobile/src/navigation
    mkdir -p mobile/src/theme
    mkdir -p ops-dashboard/src/pages
    mkdir -p ops-dashboard/src/components
    mkdir -p ops-dashboard/src/contexts
    mkdir -p automation/rube/playbooks
    mkdir -p automation/n8n
    mkdir -p automation/mcp-zero-service
    mkdir -p testing
    mkdir -p nginx
    
    echo "✅ Directory structure created"
}

# Download MCP tools database
setup_mcp_tools() {
    echo "📦 Setting up MCP tools database..."
    
    if [ ! -f MCP-tools/mcp_tools_with_embedding.json ]; then
        echo "⚠️  MCP tools database not found"
        echo "   Please download from: https://drive.google.com/file/d/1RjBGU-AGdHdhUABoeYSztbfQlD0hjUBn/view"
        echo "   And place at: ./MCP-tools/mcp_tools_with_embedding.json"
    else
        echo "✅ MCP tools database found"
    fi
}

# Start services
start_services() {
    echo "🐳 Starting Docker services..."
    
    # Build and start services
    docker-compose up -d postgres redis
    
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    # Start backend
    docker-compose up -d backend
    
    echo "⏳ Waiting for backend to be ready..."
    sleep 5
    
    # Start other services
    docker-compose up -d mcp-zero ops-dashboard n8n
    
    echo "✅ All services started"
}

# Verify services
verify_services() {
    echo "🔍 Verifying services..."
    
    # Check backend health
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ Backend API is healthy"
    else
        echo "❌ Backend API is not responding"
    fi
    
    # Check ops dashboard
    if curl -f http://localhost:3000 &> /dev/null; then
        echo "✅ Ops Dashboard is running"
    else
        echo "❌ Ops Dashboard is not responding"
    fi
    
    # Check MCP-Zero service
    if curl -f http://localhost:3001/health &> /dev/null; then
        echo "✅ MCP-Zero service is healthy"
    else
        echo "❌ MCP-Zero service is not responding"
    fi
}

# Setup mobile development
setup_mobile() {
    echo "📱 Setting up mobile development..."
    
    cd mobile
    
    if [ ! -d node_modules ]; then
        echo "📦 Installing mobile dependencies..."
        npm install
    fi
    
    echo "✅ Mobile app ready for development"
    echo "   Run 'npm start' in mobile/ directory to start Expo"
    
    cd ..
}

# Run tests
run_tests() {
    echo "🧪 Running test suite..."
    
    # Make test script executable
    chmod +x testing/api-tests.sh
    
    # Wait a bit more for services to fully start
    echo "⏳ Waiting for services to stabilize..."
    sleep 10
    
    # Run API tests
    if ./testing/api-tests.sh; then
        echo "✅ API tests passed"
    else
        echo "❌ Some API tests failed - check logs for details"
    fi
}

# Main setup flow
main() {
    check_prerequisites
    setup_directories
    setup_environment
    setup_mcp_tools
    start_services
    verify_services
    setup_mobile
    run_tests
    
    echo ""
    echo "🎉 EV Platform MVP Setup Complete!"
    echo "=================================="
    echo ""
    echo "📍 Service URLs:"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Ops Dashboard: http://localhost:3000"
    echo "   n8n Automation: http://localhost:5678 (admin/admin123)"
    echo "   MCP-Zero Service: http://localhost:3001"
    echo ""
    echo "📱 Mobile Development:"
    echo "   cd mobile && npm start"
    echo ""
    echo "🔧 Next Steps:"
    echo "   1. Update API keys in backend/.env"
    echo "   2. Configure Hyperswitch sandbox credentials"
    echo "   3. Set up Slack webhook for notifications"
    echo "   4. Download MCP tools database if needed"
    echo "   5. Run mobile app: cd mobile && npm start"
    echo ""
    echo "📚 Documentation:"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - README-MVP.md for detailed documentation"
    echo "   - testing/ directory for test cases and procedures"
    echo ""
    echo "Happy coding! 🚗⚡"
}

# Run main setup
main