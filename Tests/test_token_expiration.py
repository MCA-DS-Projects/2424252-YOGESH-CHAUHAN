#!/usr/bin/env python3
"""
Test script for token expiration functionality
Run this script to test the token expiration features
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER = {
    "email": "test@example.com",
    "password": "TestPassword123!",
    "name": "Test User",
    "role": "student",
    "rollNumber": "TEST001",
    "department": "Computer Science",
    "year": "2024"
}

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def print_response(response, title="Response"):
    print(f"\n{title}:")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Data: {json.dumps(data, indent=2)}")
    except:
        print(f"Text: {response.text}")

def test_token_expiration():
    print_section("Token Expiration Test")
    
    # Test 1: Register or Login
    print("\n1. Testing user registration/login...")
    
    # Try to register (might fail if user exists)
    register_response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    
    if register_response.status_code == 409:  # User already exists
        print("User already exists, trying login...")
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        print_response(login_response, "Login Response")
        
        if login_response.status_code != 200:
            print("❌ Login failed!")
            return
        
        tokens = login_response.json()
    else:
        print_response(register_response, "Register Response")
        
        if register_response.status_code != 201:
            print("❌ Registration failed!")
            return
        
        tokens = register_response.json()
    
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    
    if not access_token or not refresh_token:
        print("❌ No tokens received!")
        return
    
    print(f"✅ Got tokens!")
    print(f"Access token (first 20 chars): {access_token[:20]}...")
    print(f"Refresh token (first 20 chars): {refresh_token[:20]}...")
    
    # Test 2: Validate token
    print("\n2. Testing token validation...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    validate_response = requests.get(f"{BASE_URL}/auth/validate-token", headers=headers)
    print_response(validate_response, "Token Validation")
    
    if validate_response.status_code == 200:
        print("✅ Token is valid!")
        token_info = validate_response.json()
        expires_at = token_info.get('expires_at')
        if expires_at:
            print(f"Token expires at: {expires_at}")
    else:
        print("❌ Token validation failed!")
        return
    
    # Test 3: Make authenticated request
    print("\n3. Testing authenticated request...")
    profile_response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    print_response(profile_response, "Profile Request")
    
    if profile_response.status_code == 200:
        print("✅ Authenticated request successful!")
    else:
        print("❌ Authenticated request failed!")
    
    # Test 4: Test refresh token
    print("\n4. Testing token refresh...")
    refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
    refresh_data = {"refresh_token": refresh_token}
    
    refresh_response = requests.post(f"{BASE_URL}/auth/refresh", 
                                   headers=refresh_headers, 
                                   json=refresh_data)
    print_response(refresh_response, "Token Refresh")
    
    if refresh_response.status_code == 200:
        print("✅ Token refresh successful!")
        new_tokens = refresh_response.json()
        new_access_token = new_tokens.get('access_token')
        new_refresh_token = new_tokens.get('refresh_token')
        
        if new_access_token:
            print(f"New access token (first 20 chars): {new_access_token[:20]}...")
            access_token = new_access_token  # Update for further tests
        if new_refresh_token:
            print(f"New refresh token (first 20 chars): {new_refresh_token[:20]}...")
            refresh_token = new_refresh_token
    else:
        print("❌ Token refresh failed!")
    
    # Test 5: Test logout
    print("\n5. Testing logout...")
    headers = {"Authorization": f"Bearer {access_token}"}
    logout_response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print_response(logout_response, "Logout")
    
    if logout_response.status_code == 200:
        print("✅ Logout successful!")
        
        # Test if token is now invalid
        print("\n6. Testing token after logout...")
        profile_response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
        print_response(profile_response, "Profile Request After Logout")
        
        if profile_response.status_code == 401:
            print("✅ Token correctly invalidated after logout!")
        else:
            print("❌ Token should be invalid after logout!")
    else:
        print("❌ Logout failed!")

def test_admin_endpoints():
    print_section("Admin Endpoints Test")
    
    # First, login as admin (you'll need to create an admin user)
    admin_user = {
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "name": "Admin User",
        "role": "super_admin",
        "department": "Administration",
        "designation": "System Administrator"
    }
    
    print("\n1. Testing admin login...")
    
    # Try to register admin (might fail if user exists)
    register_response = requests.post(f"{BASE_URL}/auth/register", json=admin_user)
    
    if register_response.status_code == 409:  # User already exists
        print("Admin user already exists, trying login...")
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": admin_user["email"],
            "password": admin_user["password"]
        })
    else:
        login_response = register_response
    
    print_response(login_response, "Admin Login")
    
    if login_response.status_code not in [200, 201]:
        print("❌ Admin login failed!")
        return
    
    admin_token = login_response.json().get('access_token')
    if not admin_token:
        print("❌ No admin token received!")
        return
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test token stats
    print("\n2. Testing token statistics...")
    stats_response = requests.get(f"{BASE_URL}/auth/token-stats", headers=admin_headers)
    print_response(stats_response, "Token Statistics")
    
    if stats_response.status_code == 200:
        print("✅ Token statistics retrieved!")
    else:
        print("❌ Failed to get token statistics!")
    
    # Test token cleanup
    print("\n3. Testing token cleanup...")
    cleanup_response = requests.post(f"{BASE_URL}/auth/cleanup-tokens", headers=admin_headers)
    print_response(cleanup_response, "Token Cleanup")
    
    if cleanup_response.status_code == 200:
        print("✅ Token cleanup successful!")
    else:
        print("❌ Token cleanup failed!")

def main():
    print("🚀 Starting Token Expiration Tests")
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    
    try:
        # Test basic token functionality
        test_token_expiration()
        
        # Test admin endpoints
        test_admin_endpoints()
        
        print_section("Test Summary")
        print("✅ All tests completed!")
        print("\nNote: Some tests may fail if:")
        print("- Server is not running")
        print("- Database is not accessible")
        print("- Test users already exist with different passwords")
        print("- Network connectivity issues")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()