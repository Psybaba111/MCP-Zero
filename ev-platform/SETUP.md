# EV Platform Setup Guide

This guide will help you set up the complete EV Platform development environment.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ (for mobile app)
- Git

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ev-platform

# Copy environment file
cp backend/.env.example backend/.env

# Edit environment variables
nano backend/.env
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Verify Setup

```bash
# Test API endpoints
python scripts/test_api.py

# Check health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/users/
```

## 🏗️ Architecture Overview

### Backend Services

- **FastAPI**: Main API server with automatic OpenAPI documentation
- **PostgreSQL**: Primary database for all business data
- **Redis**: Caching and session management
- **Alembic**: Database migrations

### External Integrations

- **Hyperswitch**: Payment processing gateway
- **Slack**: Notifications and approvals
- **Twilio**: SMS communications
- **Notion**: Task tracking and documentation
- **MCP-Zero**: Dynamic automation tooling

### AI Services

- **vLLM**: High-performance LLM inference
- **Ollama**: Local LLM deployment

### Automation

- **n8n**: Workflow automation platform
- **Rube**: MCP-Zero enabled automation workspace

## 📁 Project Structure

```
ev-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routers
│   │   ├── core/           # Configuration
│   │   ├── db/             # Database models
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # Test suite
│   ├── main.py             # FastAPI app
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Container definition
├── mobile/                  # React Native app
├── automations/             # Rube + n8n workflows
├── ai-layer/               # vLLM/Ollama services
├── docs/                   # API documentation
├── scripts/                # Test and utility scripts
├── docker-compose.yml      # Service orchestration
└── README.md               # Project overview
```

## 🔧 Configuration

### Environment Variables

Key configuration variables in `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://ev_user:ev_password@localhost:5432/ev_platform
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256

# Hyperswitch
HYPERSWITCH_PUBLISHABLE_KEY=pk_test_...
HYPERSWITCH_SECRET_KEY=sk_test_...
HYPERSWITCH_WEBHOOK_SECRET=whsec_...

# External Services
SLACK_BOT_TOKEN=xoxb-...
TWILIO_ACCOUNT_SID=...
NOTION_TOKEN=...

# MCP-Zero
MCP_ZERO_ENDPOINT=http://localhost:8001
MCP_ZERO_ENABLED=true
```

### Database Setup

```bash
# Connect to PostgreSQL
docker exec -it ev_platform_db psql -U ev_user -d ev_platform

# Create initial tables
python -c "from app.db.database import create_tables; create_tables()"

# Run migrations (when available)
alembic upgrade head
```

## 🧪 Testing

### API Testing

```bash
# Run comprehensive API tests
python scripts/test_api.py

# Test specific endpoints
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","phone":"9876543210","full_name":"Test User","password":"test123"}'
```

### Database Testing

```bash
# Test database connection
docker exec -it ev_platform_backend python -c "
from app.db.database import get_db
db = next(get_db())
print('Database connection successful')
"
```

## 📱 Mobile App Setup

### React Native Development

```bash
cd mobile

# Install dependencies
npm install

# Start development server
npx expo start

# Run on Android
npx expo run:android

# Run on iOS
npx expo run:ios
```

### Environment Configuration

```bash
# Create mobile environment file
cp .env.example .env

# Configure API endpoints
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
EXPO_PUBLIC_HYPERSWITCH_KEY=pk_test_...
```

## 🔄 Automation Setup

### n8n Workflows

1. Access n8n at `http://localhost:5678`
2. Login with `admin` / `ev_platform_2024`
3. Import workflow templates from `automations/n8n/`

### Rube Workspace

1. Access Rube at `http://localhost:8003`
2. Configure MCP-Zero endpoint
3. Import automation playbooks

### MCP-Zero Integration

```bash
# Test MCP-Zero connection
curl http://localhost:8001/health

# Verify tool discovery
curl http://localhost:8001/discover
```

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Verify database connection
docker exec -it ev_platform_db pg_isready -U ev_user

# Restart services
docker-compose restart backend postgres
```

#### Database Connection Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
# Wait for postgres to be ready
docker-compose up -d backend
```

#### Port Conflicts

```bash
# Check port usage
netstat -tulpn | grep :8000

# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Performance Issues

```bash
# Monitor resource usage
docker stats

# Scale services
docker-compose up -d --scale backend=2

# Check logs for errors
docker-compose logs -f --tail=100
```

## 📊 Monitoring

### Health Checks

- **Backend**: `http://localhost:8000/health`
- **Database**: `http://localhost:8000/api/v1/audit/health`
- **MCP-Zero**: `http://localhost:8001/health`

### Metrics

- **Audit Metrics**: `http://localhost:8000/api/v1/audit/metrics`
- **Compliance Digest**: `http://localhost:8000/api/v1/audit/compliance/digest`

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f postgres
```

## 🔒 Security

### Development Security

- Use strong passwords in `.env`
- Don't commit `.env` files
- Use HTTPS in production
- Implement proper authentication

### Production Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Implement backup strategy
- [ ] Configure rate limiting

## 📚 API Documentation

### Interactive Docs

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints

#### Core Services

- **Users**: `/api/v1/users/`
- **Rides**: `/api/v1/rides/`
- **Vehicles**: `/api/v1/vehicles/`
- **Rentals**: `/api/v1/rentals/`
- **Payments**: `/api/v1/payments/`
- **Rewards**: `/api/v1/rewards/`
- **Audit**: `/api/v1/audit/`

#### Key Features

- **KYC Management**: User verification workflows
- **Payment Processing**: Hyperswitch integration
- **Rewards System**: Points-based loyalty
- **Compliance Tracking**: Audit and monitoring
- **Automation**: MCP-Zero enabled workflows

## 🚀 Deployment

### Production Setup

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production config
docker-compose -f docker-compose.prod.yml up -d

# Set production environment
export NODE_ENV=production
export DEBUG=false
```

### Scaling

```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Add load balancer
docker-compose up -d nginx
```

## 📞 Support

### Getting Help

1. Check the troubleshooting section above
2. Review logs for error messages
3. Check API documentation
4. Review test scripts for examples

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Happy coding! 🚗⚡**