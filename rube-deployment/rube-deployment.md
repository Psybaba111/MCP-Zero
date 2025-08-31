# EV Platform Deployment on Rube.app

This guide walks you through deploying the EV Platform automation workflows on Rube.app with all necessary integrations.

## 🚀 Quick Deploy to Rube.app

### Step 1: Install Rube in Your AI Client

```bash
# Install Rube MCP server in Cursor/Claude/VS Code
npm install -g @composio/rube

# Or follow Rube.app installation guide for your specific AI client
```

### Step 2: Authenticate Required Services

Run these commands in your AI client to authenticate each service:

```
Authenticate with Slack for EV Platform operations
Authenticate with Gmail for compliance notifications  
Authenticate with Google Calendar for rental scheduling
Authenticate with Notion for run logs and tracking
Authenticate with Twilio for SMS alerts
Authenticate with Linear for issue tracking
Authenticate with PagerDuty for incident management
```

### Step 3: Configure Environment Variables

Set up these environment variables in Rube:

```bash
# Backend API
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
```

### Step 4: Deploy Workflows

Upload and configure these automation workflows:

#### 1. KYC Approval Flow
```
Upload workflow: kyc_approval_flow.py
Trigger: Webhook - /kyc/document-uploaded
Description: Automated KYC document processing with AI extraction
```

#### 2. License Expiry Monitor
```
Upload workflow: license_expiry_monitor.py  
Trigger: Cron - 0 0 * * * (Daily at midnight IST)
Description: Daily license expiry monitoring and notifications
```

#### 3. Deposit Release Automation
```
Upload workflow: deposit_release_automation.py
Trigger: Webhook - /rental/returned
Description: Automated deposit processing after vehicle return
```

#### 4. Ride Assignment Flow
```
Upload workflow: ride_assignment_flow.py
Trigger: Webhook - /ride/payment-completed
Description: Driver assignment after ride payment
```

### Step 5: Configure Webhook Endpoints

Set up these webhook URLs in your backend to trigger Rube workflows:

```python
# Add to your backend webhook handler
RUBE_WEBHOOKS = {
    "kyc_document_uploaded": "https://rube.app/webhook/kyc-approval",
    "rental_returned": "https://rube.app/webhook/deposit-release", 
    "ride_payment_completed": "https://rube.app/webhook/ride-assignment",
    "license_expiry_check": "https://rube.app/webhook/license-monitor"
}
```

### Step 6: Test Integration

Run these test commands in your AI client:

```
Test KYC workflow with sample document upload
Test license reminder system with mock expiry data
Test deposit release with sample rental return
Test ride assignment with mock payment completion
Verify all Slack channels receive notifications
Check Notion databases are updated correctly
```

## 🔧 Integration Details

### Slack Integration
**Channels Required:**
- `#ev-platform-ops` - General operations
- `#ev-platform-alerts` - Critical alerts
- `#kyc-review` - Manual KYC reviews
- `#ride-ops` - Ride operations
- `#rental-ops` - Rental operations  
- `#finance-ops` - Financial operations
- `#license-tracking` - License compliance

**Permissions:**
- Send messages to channels
- Upload files and images
- Read channel history
- Mention users and groups

### Gmail Integration
**Use Cases:**
- Daily license expiry reports to legal team
- KYC status updates
- Compliance notifications
- Incident reports

**Templates:**
- License reminder emails
- KYC approval/rejection notices
- Deposit processing confirmations

### Google Calendar Integration
**Calendars:**
- `legal@evplatform.com` - Legal team calendar
- `ops@evplatform.com` - Operations calendar
- `rentals@evplatform.com` - Rental schedules

**Event Types:**
- License expiry follow-ups
- Rental start/end reminders
- Compliance deadlines
- Team meetings

### Notion Integration
**Databases:**
- **Run Logs**: Track all automation executions
- **Compliance Tracker**: Monitor KYC and license status
- **Vehicle Approvals**: Track listing approval workflow
- **Incident Reports**: Document system issues

### Twilio Integration
**SMS Use Cases:**
- Urgent license expiry alerts (≤7 days)
- Driver assignment notifications
- Critical system alerts
- OTP for sensitive operations

### Hyperswitch Integration
**Payment Operations:**
- Process refunds for deposits
- Handle payment failures
- Webhook verification
- Transaction reconciliation

### PagerDuty Integration
**Incident Types:**
- Critical automation failures
- Payment processing errors
- High error rates
- System downtime

### Linear Integration
**Issue Types:**
- Automation bugs
- Feature requests
- Driver shortage alerts
- System improvements

## 📊 Monitoring & Analytics

### Workflow Success Metrics
- **KYC Processing**: ≥98% auto-approval rate
- **License Monitoring**: 100% coverage of expiring licenses
- **Deposit Release**: ≤2 hour processing time
- **Ride Assignment**: ≥80% automatic assignment rate

### Performance Targets
- **Webhook Response**: <5 seconds
- **Notification Delivery**: <30 seconds
- **Error Rate**: <2% across all workflows
- **Uptime**: ≥99.5% availability

### Alerting Rules
- **Critical**: Workflow failure rate >5%
- **Warning**: Response time >10 seconds
- **Info**: Successful workflow completion

## 🔒 Security Configuration

### API Security
- Use environment variables for all secrets
- Rotate API keys monthly
- Enable webhook signature verification
- Implement rate limiting

### Access Control
- Restrict Rube access to authorized team members
- Use least-privilege principle for integrations
- Monitor and audit all automation actions
- Regular security reviews

## 🚀 Go-Live Checklist

### Pre-deployment
- [ ] All environment variables configured
- [ ] Webhook endpoints tested
- [ ] Integration authentication completed
- [ ] Test workflows executed successfully
- [ ] Monitoring dashboards configured

### Deployment
- [ ] Upload all workflow files to Rube
- [ ] Configure cron schedules
- [ ] Set up webhook triggers
- [ ] Test end-to-end flows
- [ ] Verify all notifications work

### Post-deployment
- [ ] Monitor workflow execution logs
- [ ] Validate integration health
- [ ] Check notification delivery
- [ ] Review performance metrics
- [ ] Document any issues

## 🆘 Troubleshooting

### Common Issues

**Webhook Not Triggering**
- Verify webhook URL is correct
- Check authentication tokens
- Validate payload format
- Review Rube logs

**Integration Authentication Failed**
- Re-authenticate service in Rube
- Check API key validity
- Verify required permissions
- Update environment variables

**Workflow Execution Errors**
- Check service availability
- Validate input data format
- Review error logs in Rube dashboard
- Test individual integration steps

**Notification Delivery Issues**
- Verify channel/email addresses
- Check service rate limits
- Validate message formatting
- Test with simple messages first

### Support Resources
- **Rube Documentation**: https://docs.rube.app
- **Composio GitHub**: https://github.com/ComposioHQ/composio
- **EV Platform Support**: Check internal documentation
- **Integration Guides**: Service-specific setup guides

---

**Status**: Ready for Rube.app deployment ✅

This configuration provides a complete automation setup for the EV Platform with intelligent workflows, comprehensive monitoring, and robust error handling.