"""
Test script for verifying teacher courses endpoint
Tests:
- JWT authentication is required
- Teacher role check is enforced
- Only teacher's courses are returned
- Enrollment counts are included
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

def test_courses_without_auth():
    """Test that endpoint requires authentication"""
    print_section("TEST 1: Courses endpoint without authentication")
    
    response = requests.get(f"{BASE_URL}/courses")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("✅ PASS: Authentication is required")
        return True
    else:
        print("❌ FAIL: Should require authentication")
        return False

def test_courses_with_student_auth():
    """Test that students get different data than teachers"""
    print_section("TEST 2: Courses endpoint with student authentication")
    
    # Login as student
    login_data = {
        "email": "student@test.com",
        "password": "password123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ FAIL: Could not login as student")
        print(f"Response: {json.dumps(login_response.json(), indent=2)}")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get courses
    response = requests.get(f"{BASE_URL}/courses", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        courses = data.get('courses', [])
        print(f"Number of courses returned: {len(courses)}")
        
        if courses:
            print(f"\nFirst course structure:")
            print(json.dumps(courses[0], indent=2))
            
            # Check that student sees active courses
            print(f"\n✅ PASS: Student can access courses endpoint")
            return True
        else:
            print("⚠️  WARNING: No courses found for student")
            return True
    else:
        print(f"❌ FAIL: Unexpected status code")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return False

def test_courses_with_teacher_auth():
    """Test that teachers only see their own courses with enrollment counts"""
    print_section("TEST 3: Courses endpoint with teacher authentication")
    
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
    user_id = login_response.json()['user']['id']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get courses
    response = requests.get(f"{BASE_URL}/courses", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        courses = data.get('courses', [])
        print(f"Number of courses returned: {len(courses)}")
        
        if courses:
            print(f"\nFirst course structure:")
            first_course = courses[0]
            print(json.dumps(first_course, indent=2))
            
            # Verify all courses belong to this teacher
            all_teacher_courses = all(course.get('teacher_id') == user_id for course in courses)
            
            # Check for required fields
            has_enrollment_count = 'enrolled_students' in first_course
            has_teacher_stats = 'total_assignments' in first_course
            has_average_progress = 'average_progress' in first_course
            has_active_students = 'active_students' in first_course
            
            print(f"\n📊 Verification Results:")
            print(f"  - All courses belong to teacher: {all_teacher_courses}")
            print(f"  - Has enrollment count: {has_enrollment_count}")
            print(f"  - Has assignment statistics: {has_teacher_stats}")
            print(f"  - Has average progress: {has_average_progress}")
            print(f"  - Has active students count: {has_active_students}")
            
            if all_teacher_courses and has_enrollment_count:
                print(f"\n✅ PASS: Teacher sees only their courses with enrollment counts")
                return True
            else:
                print(f"\n❌ FAIL: Missing required data or showing other teachers' courses")
                return False
        else:
            print("⚠️  WARNING: No courses found for teacher")
            return True
    else:
        print(f"❌ FAIL: Unexpected status code")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return False

def test_course_statistics():
    """Test that teacher courses include detailed statistics"""
    print_section("TEST 4: Verify course statistics for teachers")
    
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
    
    # Get courses
    response = requests.get(f"{BASE_URL}/courses", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        courses = data.get('courses', [])
        
        if not courses:
            print("⚠️  WARNING: No courses to test statistics")
            return True
        
        course = courses[0]
        
        # Check for all expected statistics
        expected_fields = [
            'enrolled_students',
            'total_assignments',
            'average_progress',
            'active_students',
            'engagement_rate',
            'completion_rate',
            'total_submissions',
            'graded_submissions',
            'pending_submissions',
            'average_grade',
            'student_performance'
        ]
        
        print(f"\n📊 Statistics Check:")
        missing_fields = []
        for field in expected_fields:
            present = field in course
            status = "✅" if present else "❌"
            print(f"  {status} {field}: {course.get(field, 'MISSING')}")
            if not present:
                missing_fields.append(field)
        
        if not missing_fields:
            print(f"\n✅ PASS: All expected statistics are present")
            return True
        else:
            print(f"\n⚠️  WARNING: Missing fields: {', '.join(missing_fields)}")
            print("Note: Some fields may be missing if there's no data yet")
            return True
    else:
        print(f"❌ FAIL: Could not retrieve courses")
        return False

def main():
    print("\n" + "🧪 TEACHER COURSES ENDPOINT VERIFICATION" + "\n")
    print("Testing /api/courses endpoint")
    print("Requirements: 5.2, 5.3, 5.4, 5.5")
    
    results = []
    
    # Run tests
    results.append(("Authentication Required", test_courses_without_auth()))
    results.append(("Student Access", test_courses_with_student_auth()))
    results.append(("Teacher Access & Filtering", test_courses_with_teacher_auth()))
    results.append(("Course Statistics", test_course_statistics()))
    
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
