# EV Platform: Ride-Hailing, P2P Rentals & Parcel Delivery

A comprehensive electric vehicle platform with ride-hailing, peer-to-peer rentals, parcel delivery, and compliance management.

## 🚗 Platform Overview

### Core Services
- **Book Ride**: Ride-hailing service for passengers
- **List My EV**: Vehicle owners can list their EVs for rental
- **Rent EV**: Users can rent EVs from other users
- **Parcel Delivery**: Send packages with ride-sharing
- **Rewards System**: Points-based loyalty program
- **Compliance Hub**: KYC, license tracking, and regulatory compliance

### Architecture
- **Mobile App**: React Native (Android/iOS)
- **Backend**: FastAPI + PostgreSQL
- **Payments**: Hyperswitch integration
- **Automation**: Rube + n8n workflows
- **AI Layer**: vLLM/Ollama for document processing
- **MCP-Zero**: Dynamic tool discovery for automations

## 🏗️ Project Structure

```
ev-platform/
├── backend/                 # FastAPI services
├── mobile/                  # React Native app
├── automations/             # Rube + n8n workflows
├── ai-layer/               # vLLM/Ollama services
├── docs/                   # API docs & schemas
├── scripts/                # Test suites & utilities
└── docker/                 # Containerization
```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Mobile App
```bash
cd mobile
npm install
npx expo start
```

### Automations
```bash
cd automations
# Start Rube workspace
# Configure n8n workflows
```

## 📋 MVP Task Board

### Week 1
- [ ] Backend APIs (Users, Rides, Vehicles, Payments)
- [ ] Mobile app navigation & ride booking
- [ ] Hyperswitch payment integration
- [ ] Basic automation workflows

### Week 2
- [ ] P2P rental marketplace
- [ ] Rewards system
- [ ] Compliance workflows
- [ ] QA testing & launch prep

## 🔧 Key Integrations

- **Hyperswitch**: Payment processing
- **Slack**: Notifications & approvals
- **Twilio**: SMS communications
- **Notion**: Task tracking & documentation
- **MCP-Zero**: Dynamic automation tooling

## 📱 Mobile App Features

- Bottom tab navigation
- Ride booking with real-time tracking
- EV rental marketplace
- Wallet & rewards management
- Compliance hub for KYC/licensing

## 🔒 Compliance & Security

- KYC verification workflows
- License expiry tracking
- Audit logging for all transactions
- Police verification callbacks
- Fraud detection systems

## 📊 Monitoring & Analytics

- Real-time ride monitoring
- Listing approval workflows
- Booking analytics
- Performance dashboards
- Error tracking & alerting

---

*Built with FastAPI, React Native, and MCP-Zero automation*
