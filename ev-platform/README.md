# EV Platform MVP 🚗⚡

A comprehensive EV ride-hailing, parcel delivery, and P2P rental platform with MCP-Zero automation integration.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │  Ops Dashboard  │    │   Backend API   │
│  (React Native) │    │    (React)      │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Automation    │
                    │ (Rube + MCP-0)  │
                    └─────────────────┘
```

## ✨ Features

### 🚗 Ride-Hailing & Parcel Delivery
- **Smart Booking**: Pickup/drop location with real-time fare estimation
- **Parcel Service**: Weight-based pricing with tracking
- **Driver Assignment**: Automated driver matching and status tracking
- **Payment Integration**: Hyperswitch payment gateway with webhook handling

### ⚡ P2P EV Rentals
- **Vehicle Marketplace**: Cars, bikes, scooters, and cycles
- **Owner Portal**: Vehicle listing with approval workflow
- **Renter Experience**: Slot booking with deposit management
- **Return Process**: Automated return checklist and deposit release

### 🔐 Compliance & KYC
- **User Verification**: Multi-document KYC with police verification
- **License Tracking**: Automated expiry reminders and notifications
- **Audit Trail**: Comprehensive logging for regulatory compliance
- **Approval Workflows**: Slack-based approval gates for high-value operations

### 🎁 Rewards System
- **Points Accrual**: Ride completion, KYC approval, on-time returns
- **Tier System**: Bronze to Platinum with increasing benefits
- **Redemption**: Catalog-based point redemption
- **Fraud Prevention**: Device fingerprinting and anomaly detection

### 🤖 Automation Layer
- **MCP-Zero Integration**: Dynamic tool discovery for intelligent automation
- **Rube Playbooks**: KYC processing, license reminders, surge rollback
- **n8n Workflows**: Daily digest emails and calendar integration
- **LLM Helpers**: vLLM/Ollama integration for incident summaries

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for mobile app and dashboard)
- Python 3.11+ (for backend development)
- PostgreSQL 15+
- Redis 7+

### 1. Clone and Setup
```bash
git clone <repository-url>
cd ev-platform

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

### 2. Backend Setup
```bash
cd backend

# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

### 3. Mobile App Setup
```bash
cd mobile-app

# Install dependencies
npm install

# Start development server
npx expo start
```

### 4. Ops Dashboard Setup
```bash
cd ops-dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Automation Setup
```bash
cd automation/rube

# Install Rube
pip install rube

# Run KYC playbook
rube run playbooks/kyc_loop.yaml
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://ev_user:ev_password@localhost:5432/ev_platform

# Security
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Hyperswitch
HYPERSWITCH_PUBLIC_KEY=your_public_key
HYPERSWITCH_SECRET_KEY=your_secret_key
HYPERSWITCH_WEBHOOK_SECRET=your_webhook_secret

# External Services
SLACK_BOT_TOKEN=your_slack_token
TWILIO_ACCOUNT_SID=your_twilio_sid
NOTION_API_KEY=your_notion_key
PAGERDUTY_API_KEY=your_pagerduty_key

# MCP-Zero
MCP_ZERO_ENDPOINT=http://localhost:8001
MCP_ZERO_ENABLED=true
```

#### Mobile App (.env)
```bash
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_HYPERSWITCH_PUBLIC_KEY=your_public_key
EV_OPPORTUNITY_ENABLED=false
```

#### Automation (.env)
```bash
BACKEND_API_URL=http://localhost:8000
SLACK_BOT_TOKEN=your_slack_token
NOTION_DATABASE_ID=your_notion_db_id
MCP_ZERO_ENDPOINT=http://localhost:8001
```

## 📱 API Endpoints

### Core Services
- **Users**: `/api/v1/users` - Registration, login, profile management
- **Rides**: `/api/v1/rides` - Ride booking and management
- **Parcels**: `/api/v1/parcels` - Parcel delivery service
- **Vehicles**: `/api/v1/vehicles` - P2P vehicle listings
- **Rentals**: `/api/v1/rentals` - EV rental bookings
- **Payments**: `/api/v1/payments` - Hyperswitch integration
- **Rewards**: `/api/v1/rewards` - Points system
- **Compliance**: `/api/v1/compliance` - KYC and regulatory
- **Audit**: `/api/v1/audit` - Comprehensive logging

### Authentication
```bash
# Login
POST /api/v1/users/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Use token in Authorization header
Authorization: Bearer <access_token>
```

## 🧪 Testing

### Run Test Suite
```bash
# Make script executable
chmod +x scripts/test-suite.sh

# Run all tests
./scripts/test-suite.sh

# Run with custom base URL
BASE_URL=http://staging.example.com ./scripts/test-suite.sh
```

### Test Coverage
- ✅ User management and authentication
- ✅ Ride booking and parcel delivery
- ✅ Vehicle listings and rentals
- ✅ Payment processing
- ✅ Rewards system
- ✅ Compliance workflows
- ✅ Automation playbooks
- ✅ MCP-Zero integration

## 🔄 Automation Workflows

### KYC Loop Playbook
- **Schedule**: Every 6 hours
- **Process**: Fetch pending KYC → MCP-Zero verification → Update status → Notify user
- **Fallback**: Static verification tools if MCP-Zero unavailable

### License Reminder
- **Schedule**: Daily at 9 AM IST
- **Process**: Query expiring licenses → Send Slack digest → Create calendar events
- **Integration**: Notion database updates

### Surge Rollback
- **Schedule**: Every 15 minutes
- **Process**: Monitor surge pricing → Trigger PagerDuty → Rollback if threshold exceeded
- **Alerts**: Slack notifications with incident tickets

### Rental Return
- **Schedule**: Every 2 hours
- **Process**: Check due returns → Send reminders → Process deposit releases
- **Audit**: Comprehensive logging for compliance

## 📊 Monitoring & Observability

### Health Checks
- **Backend**: `/health` endpoint with service status
- **Database**: Connection pool monitoring
- **Redis**: Cache availability and performance
- **Celery**: Background task queue health

### Metrics
- **API Performance**: Response times, error rates, throughput
- **Automation Success**: Playbook completion rates, MCP-Zero usage
- **Business Metrics**: Ride completion, rental success, KYC approval rates

### Logging
- **Structured Logging**: JSON format with correlation IDs
- **Audit Trail**: Complete user action logging
- **Error Tracking**: Detailed error context and stack traces

## 🚀 Deployment

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Monitoring and alerting configured
- [ ] Backup strategies implemented
- [ ] Load balancer configured
- [ ] CDN setup for static assets

### Scaling
- **Horizontal**: Multiple backend instances behind load balancer
- **Vertical**: Database connection pooling and query optimization
- **Caching**: Redis for session management and API responses
- **Background Tasks**: Celery workers for async processing

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### Code Standards
- **Python**: Black formatting, flake8 linting, type hints
- **JavaScript**: ESLint, Prettier, TypeScript
- **Testing**: Minimum 80% coverage
- **Documentation**: API docs, inline comments, README updates

## 📚 Documentation

### API Documentation
- **Interactive Docs**: Swagger UI at `/docs`
- **OpenAPI Spec**: Machine-readable API specification
- **Postman Collection**: Import-ready API testing

### Architecture Docs
- **System Design**: High-level architecture overview
- **Database Schema**: ER diagrams and table definitions
- **Integration Guides**: External service setup and configuration

### User Guides
- **Mobile App**: User onboarding and feature walkthrough
- **Owner Portal**: Vehicle listing and management
- **Ops Dashboard**: Monitoring and incident management

## 🆘 Support

### Getting Help
- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and ideas
- **Wiki**: Comprehensive documentation and troubleshooting guides

### Community
- **Slack**: Join our community channel for real-time support
- **Discord**: Developer community and collaboration
- **Meetups**: Regular community events and knowledge sharing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MCP-Zero**: Dynamic tool discovery for intelligent automation
- **FastAPI**: Modern, fast web framework for building APIs
- **React Native**: Cross-platform mobile app development
- **Hyperswitch**: Unified payment gateway integration
- **Open Source Community**: Contributors and maintainers

---

**Built with ❤️ for the EV revolution**

*Ready to transform urban mobility? Let's build the future together!*