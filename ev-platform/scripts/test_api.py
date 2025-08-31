#!/usr/bin/env python3
"""
EV Platform API Test Script
Tests all major API endpoints to ensure they're working correctly
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_users_api():
    """Test users API endpoints"""
    print("\n👥 Testing Users API...")
    
    # Test user creation
    user_data = {
        "email": f"test_{int(time.time())}@example.com",
        "phone": f"98765{int(time.time()) % 100000:05d}",
        "full_name": "Test User",
        "password": "testpassword123",
        "address": "123 Test Street, Test City",
        "emergency_contact": "9876543210"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=HEADERS)
        if response.status_code == 201:
            user = response.json()
            user_id = user["id"]
            print(f"✅ User created successfully: {user_id}")
            
            # Test user retrieval
            response = requests.get(f"{BASE_URL}/users/{user_id}")
            if response.status_code == 200:
                print("✅ User retrieval successful")
            else:
                print(f"❌ User retrieval failed: {response.status_code}")
            
            # Test KYC request
            kyc_data = {
                "license_number": f"DL{int(time.time()) % 100000:05d}",
                "license_expiry": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                "address": "123 Test Street, Test City",
                "emergency_contact": "9876543210"
            }
            
            response = requests.post(f"{BASE_URL}/users/{user_id}/kyc", json=kyc_data, headers=HEADERS)
            if response.status_code == 200:
                print("✅ KYC request successful")
            else:
                print(f"❌ KYC request failed: {response.status_code}")
            
            return user_id
        else:
            print(f"❌ User creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Users API error: {e}")
        return None

def test_rides_api():
    """Test rides API endpoints"""
    print("\n🚗 Testing Rides API...")
    
    # Test ride estimate
    estimate_data = {
        "pickup_location": "123 Main Street, City Center",
        "drop_location": "456 Business District, Downtown",
        "ride_type": "ride",
        "vehicle_type_preference": "car"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/rides/estimate", json=estimate_data, headers=HEADERS)
        if response.status_code == 200:
            estimate = response.json()
            print(f"✅ Ride estimate successful: ₹{estimate['total_fare']}")
            
            # Test ride creation
            ride_data = {
                "ride_type": "ride",
                "passenger_id": 1,  # Assuming user ID 1 exists
                "pickup_location": "123 Main Street, City Center",
                "drop_location": "456 Business District, Downtown",
                "vehicle_type_preference": "car",
                "estimated_distance": 5.2,
                "estimated_duration": 15,
                "base_fare": 50.0,
                "distance_fare": 52.0,
                "time_fare": 30.0,
                "total_fare": 132.0
            }
            
            response = requests.post(f"{BASE_URL}/rides/", json=ride_data, headers=HEADERS)
            if response.status_code == 201:
                ride = response.json()
                ride_id = ride["id"]
                print(f"✅ Ride created successfully: {ride_id}")
                return ride_id
            else:
                print(f"❌ Ride creation failed: {response.status_code}")
                return None
        else:
            print(f"❌ Ride estimate failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Rides API error: {e}")
        return None

def test_vehicles_api():
    """Test vehicles API endpoints"""
    print("\n🚙 Testing Vehicles API...")
    
    # Test vehicle creation
    vehicle_data = {
        "vehicle_type": "car",
        "brand": "Tesla",
        "model": "Model 3",
        "year": 2023,
        "color": "White",
        "battery_capacity": 75.0,
        "range_km": 350.0,
        "max_speed": 162.0,
        "seating_capacity": 5,
        "hourly_rate": 200.0,
        "daily_rate": 1500.0,
        "deposit_amount": 5000.0,
        "pickup_location": "789 EV Street, Green City",
        "registration_number": f"KA{int(time.time()) % 100000:05d}",
        "photos": ["photo1.jpg", "photo2.jpg"],
        "documents": ["insurance.pdf", "fitness.pdf"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/vehicles/?owner_id=1", json=vehicle_data, headers=HEADERS)
        if response.status_code == 201:
            vehicle = response.json()
            vehicle_id = vehicle["id"]
            print(f"✅ Vehicle created successfully: {vehicle_id}")
            
            # Test vehicle retrieval
            response = requests.get(f"{BASE_URL}/vehicles/{vehicle_id}")
            if response.status_code == 200:
                print("✅ Vehicle retrieval successful")
            else:
                print(f"❌ Vehicle retrieval failed: {response.status_code}")
            
            return vehicle_id
        else:
            print(f"❌ Vehicle creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Vehicles API error: {e}")
        return None

def test_rentals_api():
    """Test rentals API endpoints"""
    print("\n🔑 Testing Rentals API...")
    
    # Test rental creation
    rental_data = {
        "vehicle_id": 1,  # Assuming vehicle ID 1 exists
        "renter_id": 1,   # Assuming user ID 1 exists
        "start_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=3)).isoformat(),
        "hourly_rate": 200.0,
        "total_hours": 2.0,
        "total_amount": 400.0,
        "deposit_amount": 5000.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/rentals/", json=rental_data, headers=HEADERS)
        if response.status_code == 201:
            rental = response.json()
            rental_id = rental["id"]
            print(f"✅ Rental created successfully: {rental_id}")
            
            # Test rental retrieval
            response = requests.get(f"{BASE_URL}/rentals/{rental_id}")
            if response.status_code == 200:
                print("✅ Rental retrieval successful")
            else:
                print(f"❌ Rental retrieval failed: {response.status_code}")
            
            return rental_id
        else:
            print(f"❌ Rental creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Rentals API error: {e}")
        return None

def test_payments_api():
    """Test payments API endpoints"""
    print("\n💳 Testing Payments API...")
    
    # Test payment intent creation
    payment_data = {
        "amount": 13200,  # ₹132.00 in paise
        "currency": "inr",
        "payment_type": "ride",
        "ride_id": 1,     # Assuming ride ID 1 exists
        "description": "Test ride payment"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/payments/intents", json=payment_data, headers=HEADERS)
        if response.status_code == 200:
            payment = response.json()
            print(f"✅ Payment intent created successfully: {payment['payment_intent_id']}")
            
            # Test payment methods
            response = requests.get(f"{BASE_URL}/payments/methods")
            if response.status_code == 200:
                methods = response.json()
                print(f"✅ Payment methods retrieved: {len(methods)} methods")
            else:
                print(f"❌ Payment methods retrieval failed: {response.status_code}")
            
            return payment["payment_intent_id"]
        else:
            print(f"❌ Payment intent creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Payments API error: {e}")
        return None

def test_rewards_api():
    """Test rewards API endpoints"""
    print("\n🎁 Testing Rewards API...")
    
    # Test reward event creation
    reward_data = {
        "event_type": "ride_completed",
        "event_id": "ride_123",
        "user_id": 1,  # Assuming user ID 1 exists
        "points_earned": 100
    }
    
    try:
        response = requests.post(f"{BASE_URL}/rewards/events", json=reward_data, headers=HEADERS)
        if response.status_code == 200:
            reward = response.json()
            reward_id = reward["id"]
            print(f"✅ Reward event created successfully: {reward_id}")
            
            # Test reward balance
            response = requests.get(f"{BASE_URL}/rewards/user/1/balance")
            if response.status_code == 200:
                balance = response.json()
                print(f"✅ Reward balance retrieved: {balance['available_points']} points")
            else:
                print(f"❌ Reward balance retrieval failed: {response.status_code}")
            
            return reward_id
        else:
            print(f"❌ Reward event creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Rewards API error: {e}")
        return None

def test_audit_api():
    """Test audit API endpoints"""
    print("\n📊 Testing Audit API...")
    
    try:
        # Test audit log creation
        audit_data = {
            "event_type": "user_created",
            "user_id": 1,
            "event_data": {"action": "test_audit_log"},
            "source": "test_script",
            "tags": ["test", "api"]
        }
        
        response = requests.post(f"{BASE_URL}/audit/logs", json=audit_data, headers=HEADERS)
        if response.status_code == 201:
            audit_log = response.json()
            print(f"✅ Audit log created successfully: {audit_log['id']}")
            
            # Test compliance digest
            response = requests.get(f"{BASE_URL}/audit/compliance/digest")
            if response.status_code == 200:
                digest = response.json()
                print(f"✅ Compliance digest retrieved: {digest['total_users']} users")
            else:
                print(f"❌ Compliance digest retrieval failed: {response.status_code}")
            
            return audit_log["id"]
        else:
            print(f"❌ Audit log creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Audit API error: {e}")
        return None

def main():
    """Run all API tests"""
    print("🚀 Starting EV Platform API Tests...")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("❌ Health check failed. Please ensure the backend is running.")
        return
    
    # Test all API endpoints
    test_results = {
        "users": test_users_api(),
        "rides": test_rides_api(),
        "vehicles": test_vehicles_api(),
        "rentals": test_rentals_api(),
        "payments": test_payments_api(),
        "rewards": test_rewards_api(),
        "audit": test_audit_api()
    }
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for api_name, result in test_results.items():
        if result is not None:
            print(f"✅ {api_name.capitalize()} API: PASSED")
            passed += 1
        else:
            print(f"❌ {api_name.capitalize()} API: FAILED")
    
    print(f"\n🎯 Overall Result: {passed}/{total} APIs passed")
    
    if passed == total:
        print("🎉 All API tests passed successfully!")
    else:
        print("⚠️  Some API tests failed. Please check the logs above.")

if __name__ == "__main__":
    main()