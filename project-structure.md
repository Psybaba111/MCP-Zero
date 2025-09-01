# EV Platform MVP - Project Structure

## Overview
Comprehensive EV ride-hailing, parcel delivery, and P2P rental platform with MCP-Zero automation integration.

## Directory Structure

```
ev-platform/
├── backend/                    # FastAPI + PostgreSQL
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── users.py
│   │   │   │   ├── vehicles.py
│   │   │   │   ├── rides.py
│   │   │   │   ├── parcels.py
│   │   │   │   ├── rentals.py
│   │   │   │   ├── payments.py
│   │   │   │   ├── rewards.py
│   │   │   │   ├── compliance.py
│   │   │   │   └── audit.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── vehicle.py
│   │   │   ├── ride.py
│   │   │   ├── parcel.py
│   │   │   ├── rental.py
│   │   │   ├── payment.py
│   │   │   ├── reward.py
│   │   │   └── audit.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── vehicle.py
│   │   │   ├── ride.py
│   │   │   ├── parcel.py
│   │   │   ├── rental.py
│   │   │   ├── payment.py
│   │   │   └── reward.py
│   │   ├── services/
│   │   │   ├── user_service.py
│   │   │   ├── vehicle_service.py
│   │   │   ├── ride_service.py
│   │   │   ├── parcel_service.py
│   │   │   ├── rental_service.py
│   │   │   ├── payment_service.py
│   │   │   └── reward_service.py
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── docker-compose.yml
├── mobile-app/                 # React Native
│   ├── src/
│   │   ├── screens/
│   │   │   ├── Home/
│   │   │   ├── RideBooking/
│   │   │   ├── ParcelDelivery/
│   │   │   ├── RentEV/
│   │   │   ├── Profile/
│   │   │   ├── Wallet/
│   │   │   ├── Compliance/
│   │   │   └── EVOpportunities/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── ride/
│   │   │   ├── rental/
│   │   │   └── payment/
│   │   ├── navigation/
│   │   ├── services/
│   │   ├── store/
│   │   └── utils/
│   ├── App.js
│   ├── package.json
│   └── metro.config.js
├── ops-dashboard/              # React Dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── RideMonitoring/
│   │   │   ├── ListingApprovals/
│   │   │   └── BookingMonitor/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.js
├── automation/                  # Rube + n8n + MCP-Zero
│   ├── rube/
│   │   ├── playbooks/
│   │   │   ├── kyc_loop.yaml
│   │   │   ├── license_reminder.yaml
│   │   │   ├── surge_rollback.yaml
│   │   │   └── rental_return.yaml
│   │   ├── mcp-zero/
│   │   │   ├── discovery.py
│   │   │   └── fallback.py
│   │   └── config.yaml
│   ├── n8n/
│   │   ├── workflows/
│   │   │   └── daily_license_digest.json
│   │   └── docker-compose.yml
│   └── llm-helpers/
│       ├── vllm/
│       └── ollama/
├── integrations/                # External service integrations
│   ├── hyperswitch/
│   ├── slack/
│   ├── twilio/
│   ├── notion/
│   └── pagerduty/
├── docs/                        # Documentation
│   ├── api/
│   ├── mobile/
│   ├── automation/
│   └── deployment/
├── scripts/                     # Automation scripts
│   ├── setup.sh
│   ├── test-suite.sh
│   └── deployment/
├── docker/                      # Docker configurations
│   ├── backend/
│   ├── mobile/
│   └── ops-dashboard/
└── README.md
```

## Key Components by Task

### Backend (Week 1)
- **BE-01**: Users/KYC/Compliance API (`backend/app/api/v1/users.py`, `backend/app/api/v1/compliance.py`)
- **BE-02**: Rides + Parcels (`backend/app/api/v1/rides.py`, `backend/app/api/v1/parcels.py`)
- **BE-03**: P2P Vehicles + Rentals (`backend/app/api/v1/vehicles.py`, `backend/app/api/v1/rentals.py`)
- **BE-04**: Payments (Hyperswitch) (`backend/app/api/v1/payments.py`)

### Mobile App (Week 1-2)
- **APP-01**: Navigation + Tabs (`mobile-app/src/navigation/`)
- **APP-02**: Ride booking + Parcel flow (`mobile-app/src/screens/RideBooking/`, `mobile-app/src/screens/ParcelDelivery/`)
- **APP-03**: Rent EV marketplace (`mobile-app/src/screens/RentEV/`)
- **APP-04**: Profile → Compliance Hub (`mobile-app/src/screens/Profile/`, `mobile-app/src/screens/Compliance/`)
- **APP-05**: Wallet + Rewards (`mobile-app/src/screens/Wallet/`)

### Automation (Week 1-2)
- **AUTO-01**: Rube workspace import (`automation/rube/`)
- **AUTO-02**: n8n cron (`automation/n8n/`)
- **AUTO-03**: LLM helpers (`automation/llm-helpers/`)

### Payments (Week 1-2)
- **PAY-01**: Hyperswitch sandbox (`integrations/hyperswitch/`)
- **PAY-02**: Deposits and refunds (`backend/app/services/payment_service.py`)

### Compliance & Ops (Week 2)
- **OPS-01**: Slack approvals (`automation/rube/playbooks/`)
- **OPS-02**: Ops Desk Card (`ops-dashboard/src/components/`)

### QA & Launch (Week 2)
- **QA-01**: cURL test suite (`scripts/test-suite.sh`)
- **QA-02**: Mobile E2E (`scripts/mobile-e2e.sh`)

## Environment Variables

### Backend
```
DATABASE_URL=postgresql://user:pass@localhost:5432/ev_platform
HYPERSWITCH_PUBLIC_KEY=your_public_key
HYPERSWITCH_SECRET_KEY=your_secret_key
WEBHOOK_SECRET=your_webhook_secret
JWT_SECRET=your_jwt_secret
```

### Mobile
```
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_HYPERSWITCH_PUBLIC_KEY=your_public_key
EV_OPPORTUNITY_ENABLED=false
```

### Automation
```
BACKEND_API_URL=http://localhost:8000
SLACK_BOT_TOKEN=your_slack_token
NOTION_API_KEY=your_notion_key
MCP_ZERO_ENDPOINT=http://localhost:8001
```

## Quick Start Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Mobile App
cd mobile-app
npm install
npx expo start

# Ops Dashboard
cd ops-dashboard
npm install
npm run dev

# Automation
cd automation/rube
rube run playbooks/kyc_loop.yaml

# Test Suite
./scripts/test-suite.sh
```