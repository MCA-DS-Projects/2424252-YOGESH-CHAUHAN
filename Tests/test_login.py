#!/usr/bin/env python3
"""
Script to test the login functionality
"""

import requests
import json

def test_login():
    """Test the login endpoint"""
    
    # API endpoint
    login_url = "http://localhost:5000/api/auth/login"
    
    # Login credentials
    credentials = {
        "email": "superadmin@datams.edu",
        "password": "Admin@123456"
    }
    
    try:
        print("🔄 Testing login...")
        print(f"📧 Email: {credentials['email']}")
        print(f"🔑 Password: {credentials['password']}")
        print(f"🌐 URL: {login_url}")
        
        # Make the request
        response = requests.post(login_url, json=credentials)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"👤 User: {data.get('user', {}).get('name', 'Unknown')}")
            print(f"🎭 Role: {data.get('user', {}).get('role', 'Unknown')}")
            print(f"🎫 Token: {data.get('access_token', 'No token')[:50]}...")
        else:
            print("❌ Login failed!")
            try:
                error_data = response.json()
                print(f"🚨 Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"🚨 Error: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the backend server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    test_login()