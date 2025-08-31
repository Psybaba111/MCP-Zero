# 🚀 EV Platform Deployment on Rube.app

## Complete Integration Guide

This guide provides step-by-step instructions to deploy the entire EV Platform on Rube.app with all necessary integrations for a production-ready automation system.

## 🎯 What You'll Deploy

### Core Platform
- **Backend API** (FastAPI + PostgreSQL) - All 8 services
- **Mobile App** (React Native) - Complete ride/rental/parcel flows  
- **Ops Dashboard** (React) - Real-time monitoring and approvals
- **Automation Layer** (Rube + MCP-Zero) - Intelligent workflows

### Automation Workflows
1. **KYC Approval Flow** - AI-powered document processing
2. **License Expiry Monitor** - Daily compliance tracking
3. **Deposit Release** - Automated refund processing
4. **Ride Assignment** - Driver matching and notifications

### Integrations (500+ via Rube)
- **Slack** - Operations communication
- **Gmail** - Compliance notifications
- **Google Calendar** - Scheduling and reminders
- **Notion** - Documentation and run logs
- **Twilio** - SMS alerts
- **Hyperswitch** - Payment processing
- **PagerDuty** - Incident management
- **Linear** - Issue tracking

---

## 🚀 Quick Deployment (5 Minutes)

### Prerequisites
```bash
# Install Composio CLI
npm install -g @composio/cli

# Login to Composio/Rube
composio login
```

### One-Command Deploy
```bash
# Clone and deploy
git clone <your-repo>
cd ev-platform
./rube-deployment/deploy-to-rube.sh
```

### Configure Environment
```bash
# Update with your API keys
nano rube-deployment/.env

# Required keys:
# - HYPERSWITCH_API_KEY (payment processing)
# - SLACK_WEBHOOK_URL (notifications)
# - OPENAI_API_KEY (AI document processing)
# - TWILIO credentials (SMS alerts)
# - NOTION_API_KEY (documentation)
```

---

## 📋 Detailed Setup Instructions

### Step 1: Service Authentication

Authenticate each service in Rube:

```bash
# Core communication services
composio add slack
composio add gmail  
composio add googlecalendar

# Documentation and tracking
composio add notion
composio add linear

# Alerts and incidents
composio add twilio
composio add pagerduty

# Custom APIs
composio add custom_api --name hyperswitch
composio add custom_api --name backend_api
```

### Step 2: Deploy Automation Workflows

```bash
# Deploy all 4 core workflows
composio deploy workflow workflows/kyc_approval_flow.py --name kyc-approval
composio deploy workflow workflows/license_expiry_monitor.py --name license-monitor --cron "0 0 * * *"
composio deploy workflow workflows/deposit_release_automation.py --name deposit-release
composio deploy workflow workflows/ride_assignment_flow.py --name ride-assignment
```

### Step 3: Configure Webhook Integration

Add this to your backend (`main.py`):

```python
# Add Rube webhook router
from rube_deployment.webhook_integration import router as rube_router
app.include_router(rube_router, prefix="/api/v1/webhooks", tags=["rube-integration"])
```

### Step 4: Set Environment Variables

```bash
# In Rube dashboard, configure these variables:
BACKEND_API_URL=https://your-backend.com/api/v1
BACKEND_API_TOKEN=your-jwt-token
HYPERSWITCH_API_KEY=your-hyperswitch-key
SLACK_WEBHOOK_URL=your-slack-webhook
TWILIO_ACCOUNT_SID=your-twilio-sid
NOTION_API_KEY=your-notion-key
OPENAI_API_KEY=your-openai-key
```

---

## 🔄 Workflow Triggers

### Automatic Triggers

| Workflow | Trigger | Event Source | Frequency |
|----------|---------|--------------|-----------|
| KYC Approval | Webhook | Document upload | Real-time |
| License Monitor | Cron | System scheduler | Daily 00:00 IST |
| Deposit Release | Webhook | Vehicle return | Real-time |
| Ride Assignment | Webhook | Payment success | Real-time |

### Manual Triggers

You can also trigger workflows manually in Rube:

```bash
# Test KYC workflow
composio trigger kyc-approval --data '{"user_id": "test-user", "document_type": "license"}'

# Test deposit release
composio trigger deposit-release --data '{"rental_id": "test-rental"}'

# Test ride assignment  
composio trigger ride-assignment --data '{"entity_id": "test-ride", "entity_type": "ride"}'
```

---

## 📊 Monitoring & Analytics

### Rube Dashboard
- **Workflow Execution Logs** - Real-time status and results
- **Integration Health** - Service connectivity status
- **Performance Metrics** - Execution times and success rates
- **Error Tracking** - Failed workflows and debugging info

### Slack Notifications
All workflows send status updates to configured Slack channels:
- `#ev-platform-ops` - General operations
- `#ev-platform-alerts` - Critical alerts
- `#kyc-review` - Manual review requests
- `#finance-ops` - Payment and deposit updates

### Success Metrics
- **Automation Success Rate**: ≥98%
- **Response Time**: <5 seconds per workflow
- **Error Rate**: <2% across all workflows
- **Notification Delivery**: <30 seconds

---

## 🔧 Integration Configurations

### Slack Setup
```yaml
Channels Required:
- #ev-platform-ops (general operations)
- #ev-platform-alerts (critical alerts)  
- #kyc-review (document reviews)
- #ride-ops (ride operations)
- #rental-ops (rental operations)
- #finance-ops (financial operations)
- #license-tracking (compliance)

Permissions:
- Send messages to channels
- Upload files and attachments
- Read channel history
- Mention users and groups
```

### Gmail Templates
```html
<!-- License Reminder Template -->
<html>
<body>
  <h2>🚨 License Renewal Required</h2>
  <p>Your driving license expires in {{days_remaining}} days.</p>
  <div style="background: #f5f5f5; padding: 15px;">
    <strong>License:</strong> {{license_number}}<br>
    <strong>Expiry:</strong> {{expiry_date}}
  </div>
  <p>Please renew to continue using EV Platform.</p>
</body>
</html>
```

### Notion Database Schema
```json
{
  "run_logs": {
    "Title": "text",
    "Type": "select", 
    "Status": "select",
    "Execution Time": "date",
    "Details": "rich_text"
  },
  "compliance_tracker": {
    "User": "text",
    "Document Type": "select",
    "Status": "select", 
    "Expiry Date": "date",
    "Days Remaining": "number"
  }
}
```

---

## 🧪 Testing Your Deployment

### 1. Test Individual Workflows

```bash
# Test KYC workflow
curl -X POST http://localhost:8000/api/v1/webhooks/rube/kyc-uploaded \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "document_id": "test-doc", "document_url": "https://example.com/license.jpg", "document_type": "license"}'

# Test deposit release
curl -X POST http://localhost:8000/api/v1/webhooks/rube/rental-returned \
  -H "Content-Type: application/json" \
  -d '{"rental_id": "test-rental", "user_id": "test-user"}'
```

### 2. End-to-End Testing

```bash
# Run complete API test suite
./testing/api-tests.sh

# Expected: ≥95% pass rate
```

### 3. Mobile App Testing

Follow the mobile E2E test cases in `/testing/mobile-e2e-tests.md`:
- Book ride flow
- Rent vehicle flow  
- Send parcel flow
- KYC upload flow
- Wallet and rewards flow

---

## 🔒 Security & Compliance

### API Security
- JWT authentication for all endpoints
- Rate limiting on sensitive endpoints
- Webhook signature verification
- CORS configuration for production

### Data Protection
- Encrypted storage of sensitive data
- Audit logging for all operations
- GDPR-compliant data handling
- Secure API key management

### Monitoring
- Real-time error tracking
- Performance monitoring
- Security event logging
- Automated incident response

---

## 📈 Scaling Considerations

### Performance Optimization
- Database connection pooling
- Redis caching layer
- CDN for mobile assets
- Load balancing for API

### Automation Scaling
- Parallel workflow execution
- Queue-based processing
- Circuit breaker patterns
- Graceful degradation

### Monitoring & Alerting
- Comprehensive metrics collection
- Proactive alerting rules
- Incident response playbooks
- Performance benchmarking

---

## 🆘 Support & Troubleshooting

### Common Issues

**Workflow Not Triggering**
```bash
# Check webhook configuration
composio list-webhooks

# Verify environment variables
composio env list

# Test webhook manually
curl -X POST <webhook-url> -d '{"test": "data"}'
```

**Integration Authentication Errors**
```bash
# Re-authenticate service
composio auth <service-name>

# Check integration status
composio integrations status

# Refresh tokens
composio refresh-tokens
```

**Performance Issues**
```bash
# Check workflow execution times
composio logs <workflow-name> --metrics

# Monitor resource usage
composio stats

# Scale workflow instances
composio scale <workflow-name> --instances 3
```

### Getting Help

1. **Rube Documentation**: https://docs.rube.app
2. **Composio GitHub**: https://github.com/ComposioHQ/composio
3. **Community Discord**: https://discord.gg/composio
4. **Support Email**: support@composio.dev

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] All API keys and tokens configured
- [ ] Slack channels created and configured
- [ ] Notion databases set up
- [ ] Twilio account verified
- [ ] Backend services running and healthy

### Deployment
- [ ] Rube project initialized
- [ ] All integrations authenticated
- [ ] Workflows deployed successfully
- [ ] Webhook URLs configured in backend
- [ ] Environment variables set

### Post-Deployment
- [ ] Test all workflows manually
- [ ] Verify notifications in Slack
- [ ] Check Notion logs are updating
- [ ] Monitor workflow execution metrics
- [ ] Validate end-to-end flows

### Production Readiness
- [ ] Error handling tested
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Documentation updated
- [ ] Team training completed

---

## 🎉 Success! Your EV Platform is Live on Rube.app

Once deployed, your platform will have:

✅ **Intelligent Automation** - MCP-Zero powered workflows
✅ **500+ Integrations** - Via Rube/Composio ecosystem  
✅ **Real-time Monitoring** - Comprehensive observability
✅ **Scalable Architecture** - Production-ready infrastructure
✅ **Complete MVP** - All features from specification implemented

**Platform Status**: 🟢 **PRODUCTION READY**

Your EV Platform is now live with intelligent automation, comprehensive integrations, and production-grade monitoring. The system is ready to handle real users and scale as your business grows.

**Next Steps**: 
1. Configure your API keys
2. Test all workflows
3. Launch pilot program
4. Monitor and optimize

Happy automating! 🤖⚡🚗