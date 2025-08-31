# Mobile E2E Test Cases
EV Platform Mobile App - End-to-End Testing Scenarios

## Golden Path Test Cases

### 1. Book Ride Flow
**Objective**: Test complete ride booking from search to payment confirmation

**Steps**:
1. Open app and login with test credentials
2. Tap "Book Ride" on home screen
3. Set pickup location (use current location)
4. Set drop location by tapping on map
5. Tap "Next" to proceed to vehicle selection
6. Select "E-Scooter" vehicle type
7. Verify fare estimate is displayed
8. Tap "Proceed to Pay"
9. Verify payment sheet shows correct amount
10. Tap "Pay" button
11. Wait for payment processing (2-3 seconds)
12. Verify booking confirmation screen appears
13. Check that ride status shows "PAID" or "ASSIGNED"
14. Verify driver card appears if assigned

**Expected Results**:
- ✅ All screens load without crashes
- ✅ Payment completes successfully
- ✅ Booking confirmation shows correct details
- ✅ Audit logs show ride creation and payment events
- ✅ Slack notification sent to #ride-ops channel

### 2. Send Parcel Flow
**Objective**: Test parcel delivery booking end-to-end

**Steps**:
1. From home screen, tap "Send Parcel"
2. Fill in pickup address
3. Fill in drop address
4. Enter recipient name and phone
5. Enter parcel weight (2.5 kg)
6. Tap "Proceed to Pay"
7. Complete payment
8. Verify parcel tracking screen

**Expected Results**:
- ✅ Parcel created with correct details
- ✅ Payment processed successfully
- ✅ Tracking information displayed
- ✅ Audit trail recorded

### 3. Rent EV Flow
**Objective**: Test vehicle rental booking and return

**Steps**:
1. Navigate to "Rent EV" tab
2. Select "Cars" category
3. Browse available vehicles
4. Tap on a vehicle card
5. View vehicle details
6. Select rental time slot (start: +1 hour, end: +5 hours)
7. Review price summary
8. Tap "Pay & Book"
9. Complete payment for rental + deposit
10. Verify rental confirmation
11. Navigate to rental in profile
12. Tap "Return Now" (when end time reached)
13. Upload return photos
14. Submit return
15. Verify deposit release notification

**Expected Results**:
- ✅ Vehicle booking completes successfully
- ✅ Both rental and deposit payments process
- ✅ Return flow works correctly
- ✅ Deposit release automation triggers
- ✅ Owner receives booking notification

### 4. KYC Upload Flow
**Objective**: Test document upload and KYC processing

**Steps**:
1. Navigate to Profile tab
2. Tap "View Compliance Hub"
3. Tap "Upload/Update" for driving license
4. Select photo from gallery or take new photo
5. Fill in document details
6. Submit document
7. Verify upload confirmation
8. Check KYC status updates

**Expected Results**:
- ✅ Document uploads successfully
- ✅ KYC status changes to "in_progress"
- ✅ Automation workflow triggers
- ✅ Document processing completes
- ✅ Status updates to "approved" or "manual review"

### 5. Rewards and Wallet Flow
**Objective**: Test points earning and redemption

**Steps**:
1. Complete a ride (from Test Case 1)
2. Navigate to Wallet tab
3. Verify points balance increased
4. Check rewards history
5. Tap "Redeem Points"
6. Select redemption option
7. Confirm redemption
8. Verify balance updated

**Expected Results**:
- ✅ Points credited after ride completion
- ✅ Rewards history shows correct events
- ✅ Redemption processes successfully
- ✅ Balance updates immediately

### 6. Vehicle Listing Flow (Owner)
**Objective**: Test vehicle listing submission

**Steps**:
1. Register as owner role
2. Navigate to Profile → My Vehicles
3. Tap "Add Vehicle"
4. Fill vehicle details (make, model, year)
5. Upload vehicle photos
6. Set pricing (hourly/daily rates, deposit)
7. Submit for approval
8. Verify pending approval status

**Expected Results**:
- ✅ Vehicle listing created successfully
- ✅ Status shows "pending approval"
- ✅ Ops dashboard shows listing for approval
- ✅ Owner receives confirmation

## Performance Benchmarks

### App Performance Targets
- ✅ App launch time: < 3 seconds
- ✅ Screen transitions: < 500ms
- ✅ API response time: < 2 seconds
- ✅ Map loading: < 5 seconds
- ✅ Image upload: < 10 seconds
- ✅ Crash rate: < 1% in staging

### Backend Performance Targets
- ✅ API response p95: < 2 seconds
- ✅ Database query time: < 500ms
- ✅ Webhook processing: < 2 seconds
- ✅ Error rate: < 1%
- ✅ Uptime: > 99.5%

## Automation Testing

### MCP-Zero Validation
- ✅ Tool discovery returns relevant tools
- ✅ Static fallback works when MCP-Zero disabled
- ✅ Tool-token reduction ≥ 80%
- ✅ Processing time < 30 seconds per workflow

### Workflow Success Rates
- ✅ KYC processing: ≥ 98%
- ✅ License reminders: ≥ 98%
- ✅ Deposit release: ≥ 98%
- ✅ Ride notifications: ≥ 98%
- ✅ Rental notifications: ≥ 98%

## Test Data Setup

### Test Users
```json
{
  "passenger": {
    "email": "passenger@test.com",
    "phone": "+919876543210",
    "full_name": "Test Passenger"
  },
  "driver": {
    "email": "driver@test.com",
    "phone": "+919876543211",
    "full_name": "Test Driver"
  },
  "owner": {
    "email": "owner@test.com",
    "phone": "+919876543212",
    "full_name": "Test Owner"
  }
}
```

### Test Vehicles
```json
{
  "car": {
    "make": "Tata",
    "model": "Nexon EV",
    "year": 2023,
    "registration": "KA01AB1234",
    "hourly_rate": 150,
    "daily_rate": 2500,
    "deposit": 5000
  },
  "scooter": {
    "make": "Ather",
    "model": "450X",
    "year": 2023,
    "registration": "KA02CD5678",
    "hourly_rate": 50,
    "daily_rate": 800,
    "deposit": 2000
  }
}
```

## Test Execution Instructions

### Prerequisites
1. Backend services running on localhost:8000
2. Database seeded with test data
3. Mobile app built and installed on test device
4. Test user accounts created

### Execution
1. Run automated API tests: `./testing/api-tests.sh`
2. Execute mobile E2E tests manually or with automation tool
3. Verify automation workflows in Rube dashboard
4. Check ops dashboard functionality
5. Validate all golden paths complete successfully

### Success Criteria
- ✅ API tests: ≥ 95% pass rate
- ✅ Mobile E2E: All 6 golden paths complete
- ✅ Automation: ≥ 98% workflow success rate
- ✅ Performance: All targets met
- ✅ No critical bugs or crashes