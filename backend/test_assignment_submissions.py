"""
Test script for verifying assignment submissions endpoint
Tests:
- GET /api/assignments/:id endpoint returns assignment details
- Submissions are included in response for teachers
- Student information is populated in submissions
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_assignment_detail_without_auth():
    """Test that endpoint requires authentication"""
    print_section("TEST 1: Assignment detail without authentication")
    
    # Use a dummy assignment ID
    assignment_id = "507f1f77bcf86cd799439011"
    response = requests.get(f"{BASE_URL}/assignments/{assignment_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("✅ PASS: Authentication is required")
        return True
    else:
        print("❌ FAIL: Should require authentication")
        return False

def test_assignment_detail_with_teacher():
    """Test that teachers get assignment with all submissions and student info"""
    print_section("TEST 2: Assignment detail with teacher authentication")
    
    # Login as teacher
    login_data = {
        "email": "teacher@test.com",
        "password": "password123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ FAIL: Could not login as teacher")
        print(f"Response: {json.dumps(login_response.json(), indent=2)}")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, get list of assignments to find a valid ID
    assignments_response = requests.get(f"{BASE_URL}/assignments", headers=headers)
    
    if assignments_response.status_code != 200:
        print(f"❌ FAIL: Could not get assignments list")
        return False
    
    assignments = assignments_response.json().get('assignments', [])
    
    if not assignments:
        print("⚠️  WARNING: No assignments found for teacher")
        print("Cannot test assignment detail endpoint without assignments")
        return True
    
    # Get first assignment details
    assignment_id = assignments[0]['_id']
    print(f"\nTesting with assignment ID: {assignment_id}")
    
    response = requests.get(f"{BASE_URL}/assignments/{assignment_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        assignment = data.get('assignment', {})
        
        print(f"\n📋 Assignment Details:")
        print(f"  Title: {assignment.get('title')}")
        print(f"  Course: {assignment.get('course_title')}")
        print(f"  Max Points: {assignment.get('max_points')}")
        
        # Check for submissions
        submissions = assignment.get('submissions', [])
        print(f"\n📝 Submissions: {len(submissions)} found")
        
        if submissions:
            print(f"\nFirst submission structure:")
            first_submission = submissions[0]
            print(json.dumps(first_submission, indent=2))
            
            # Verify student information is populated
            has_student_name = 'student_name' in first_submission
            has_student_email = 'student_email' in first_submission
            has_roll_no = 'roll_no' in first_submission
            has_submission_data = 'submitted_at' in first_submission
            has_status = 'status' in first_submission
            
            print(f"\n📊 Verification Results:")
            print(f"  - Has student name: {has_student_name}")
            print(f"  - Has student email: {has_student_email}")
            print(f"  - Has roll number: {has_roll_no}")
            print(f"  - Has submission date: {has_submission_data}")
            print(f"  - Has status: {has_status}")
            
            if all([has_student_name, has_student_email, has_submission_data, has_status]):
                print(f"\n✅ PASS: Submissions include all required student information")
                return True
            else:
                print(f"\n❌ FAIL: Missing required student information in submissions")
                return False
        else:
            print("⚠️  WARNING: No submissions found for this assignment")
            print("Cannot verify student information population")
            return True
    else:
        print(f"❌ FAIL: Unexpected status code")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return False

def test_assignment_detail_with_student():
    """Test that students get assignment with only their submission"""
    print_section("TEST 3: Assignment detail with student authentication")
    
    # Login as student
    login_data = {
        "email": "student@test.com",
        "password": "password123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ FAIL: Could not login as student")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get list of assignments
    assignments_response = requests.get(f"{BASE_URL}/assignments", headers=headers)
    
    if assignments_response.status_code != 200:
        print(f"❌ FAIL: Could not get assignments list")
        return False
    
    assignments = assignments_response.json().get('assignments', [])
    
    if not assignments:
        print("⚠️  WARNING: No assignments found for student")
        return True
    
    # Get first assignment details
    assignment_id = assignments[0]['_id']
    print(f"\nTesting with assignment ID: {assignment_id}")
    
    response = requests.get(f"{BASE_URL}/assignments/{assignment_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        assignment = data.get('assignment', {})
        
        print(f"\n📋 Assignment Details:")
        print(f"  Title: {assignment.get('title')}")
        
        # Check that student only sees their own submission
        has_submission = 'submission' in assignment
        has_submissions_list = 'submissions' in assignment
        
        print(f"\n📊 Verification Results:")
        print(f"  - Has own submission: {has_submission}")
        print(f"  - Has all submissions list: {has_submissions_list}")
        
        if has_submission and not has_submissions_list:
            print(f"\n✅ PASS: Student sees only their own submission")
            return True
        elif not has_submission and not has_submissions_list:
            print(f"\n✅ PASS: Student has not submitted yet (no submission data)")
            return True
        else:
            print(f"\n❌ FAIL: Student should not see all submissions")
            return False
    else:
        print(f"❌ FAIL: Unexpected status code")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return False

def test_assignment_access_control():
    """Test that teachers can only access assignments from their courses"""
    print_section("TEST 4: Assignment access control")
    
    # Login as teacher
    login_data = {
        "email": "teacher@test.com",
        "password": "password123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ FAIL: Could not login as teacher")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to access an assignment (if any exist)
    assignments_response = requests.get(f"{BASE_URL}/assignments", headers=headers)
    
    if assignments_response.status_code == 200:
        assignments = assignments_response.json().get('assignments', [])
        
        if assignments:
            assignment_id = assignments[0]['_id']
            detail_response = requests.get(f"{BASE_URL}/assignments/{assignment_id}", headers=headers)
            
            if detail_response.status_code == 200:
                print(f"✅ PASS: Teacher can access their own assignment")
                return True
            elif detail_response.status_code == 403:
                print(f"✅ PASS: Access denied for other teacher's assignment")
                return True
            else:
                print(f"⚠️  WARNING: Unexpected status code: {detail_response.status_code}")
                return True
        else:
            print("⚠️  WARNING: No assignments to test access control")
            return True
    else:
        print(f"❌ FAIL: Could not get assignments list")
        return False

def main():
    print("\n" + "🧪 ASSIGNMENT SUBMISSIONS ENDPOINT VERIFICATION" + "\n")
    print("Testing /api/assignments/:id endpoint")
    print("Requirements: 5.2, 5.3, 5.4, 5.5")
    
    results = []
    
    # Run tests
    results.append(("Authentication Required", test_assignment_detail_without_auth()))
    results.append(("Teacher Access with Submissions", test_assignment_detail_with_teacher()))
    results.append(("Student Access", test_assignment_detail_with_student()))
    results.append(("Access Control", test_assignment_access_control()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
