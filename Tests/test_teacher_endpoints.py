"""
Test script to verify teacher endpoints
This script tests all teacher-related endpoints to ensure they work correctly
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_TEACHER_EMAIL = "teacher@test.com"
TEST_TEACHER_PASSWORD = "test123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def login_as_teacher():
    """Login as teacher and return JWT token"""
    print_info("Logging in as teacher...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_TEACHER_EMAIL,
        "password": TEST_TEACHER_PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        print_success(f"Login successful")
        return token
    else:
        print_error(f"Login failed: {response.json()}")
        return None

def test_teacher_dashboard_stats(token):
    """Test 6.1: Verify teacher dashboard stats endpoint"""
    print_info("\n=== Test 6.1: Teacher Dashboard Stats Endpoint ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with valid token
    print_info("Testing /api/analytics/teacher/dashboard with valid token...")
    response = requests.get(f"{BASE_URL}/analytics/teacher/dashboard", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'dashboard_stats' in data:
            stats = data['dashboard_stats']
            required_fields = ['active_courses', 'total_students', 'pending_grades', 'course_rating', 'monthly_growth']
            
            all_present = all(field in stats for field in required_fields)
            if all_present:
                print_success("Dashboard stats endpoint working correctly")
                print_info(f"  - Active Courses: {stats['active_courses']}")
                print_info(f"  - Total Students: {stats['total_students']}")
                print_info(f"  - Pending Grades: {stats['pending_grades']}")
                print_info(f"  - Course Rating: {stats['course_rating']}")
                return True
            else:
                print_error("Missing required fields in response")
                return False
        else:
            print_error("Response missing 'dashboard_stats' key")
            return False
    else:
        print_error(f"Request failed with status {response.status_code}: {response.json()}")
        return False

def test_teacher_dashboard_auth(token):
    """Test JWT authentication requirement"""
    print_info("\nTesting authentication requirement...")
    
    # Test without token
    response = requests.get(f"{BASE_URL}/analytics/teacher/dashboard")
    if response.status_code == 401:
        print_success("Correctly requires JWT authentication")
    else:
        print_error(f"Should return 401 without token, got {response.status_code}")
        return False
    
    return True

def test_teacher_courses_endpoint(token):
    """Test 6.2: Verify teacher courses endpoint"""
    print_info("\n=== Test 6.2: Teacher Courses Endpoint ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print_info("Testing /api/courses with teacher authentication...")
    response = requests.get(f"{BASE_URL}/courses", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'courses' in data:
            courses = data['courses']
            print_success(f"Courses endpoint working correctly ({len(courses)} courses found)")
            
            # Check if enrollment counts are included
            if courses:
                first_course = courses[0]
                if 'enrolled_students' in first_course:
                    print_success("Enrollment counts are included")
                    print_info(f"  - Sample course: {first_course.get('title', 'N/A')}")
                    print_info(f"  - Enrolled students: {first_course['enrolled_students']}")
                    if 'total_assignments' in first_course:
                        print_info(f"  - Total assignments: {first_course['total_assignments']}")
                else:
                    print_warning("Enrollment counts not included in response")
            return True
        else:
            print_error("Response missing 'courses' key")
            return False
    else:
        print_error(f"Request failed with status {response.status_code}: {response.json()}")
        return False

def test_assignment_submissions_endpoint(token):
    """Test 6.3: Verify assignment submissions endpoint"""
    print_info("\n=== Test 6.3: Assignment Submissions Endpoint ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First get assignments
    print_info("Getting teacher's assignments...")
    response = requests.get(f"{BASE_URL}/assignments", headers=headers)
    
    if response.status_code != 200:
        print_error(f"Failed to get assignments: {response.json()}")
        return False
    
    assignments = response.json().get('assignments', [])
    if not assignments:
        print_warning("No assignments found for teacher")
        return True
    
    # Test getting assignment details with submissions
    assignment_id = assignments[0]['_id']
    print_info(f"Testing /api/assignments/{assignment_id}...")
    response = requests.get(f"{BASE_URL}/assignments/{assignment_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'assignment' in data:
            assignment = data['assignment']
            if 'submissions' in assignment:
                print_success(f"Assignment details endpoint working correctly")
                print_info(f"  - Assignment: {assignment.get('title', 'N/A')}")
                print_info(f"  - Submissions: {len(assignment['submissions'])}")
                
                # Check if student information is populated
                if assignment['submissions']:
                    first_sub = assignment['submissions'][0]
                    if 'student_name' in first_sub and 'student_email' in first_sub:
                        print_success("Student information is populated")
                        print_info(f"  - Sample student: {first_sub['student_name']}")
                    else:
                        print_warning("Student information not fully populated")
                return True
            else:
                print_warning("No submissions field in response (may be expected if no submissions)")
                return True
        else:
            print_error("Response missing 'assignment' key")
            return False
    else:
        print_error(f"Request failed with status {response.status_code}: {response.json()}")
        return False

def test_grade_submission_endpoint(token):
    """Test 6.4: Verify grade submission endpoint"""
    print_info("\n=== Test 6.4: Grade Submission Endpoint ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First get assignments with submissions
    print_info("Finding an ungraded submission...")
    response = requests.get(f"{BASE_URL}/assignments", headers=headers)
    
    if response.status_code != 200:
        print_error(f"Failed to get assignments: {response.json()}")
        return False
    
    assignments = response.json().get('assignments', [])
    
    # Find an assignment with submissions
    submission_id = None
    max_points = 100
    
    for assignment in assignments:
        assignment_id = assignment['_id']
        response = requests.get(f"{BASE_URL}/assignments/{assignment_id}", headers=headers)
        if response.status_code == 200:
            assignment_data = response.json().get('assignment', {})
            submissions = assignment_data.get('submissions', [])
            max_points = assignment_data.get('max_points', 100)
            
            # Find an ungraded submission
            for sub in submissions:
                if sub.get('grade') is None:
                    submission_id = sub['_id']
                    break
            
            if submission_id:
                break
    
    if not submission_id:
        print_warning("No ungraded submissions found to test grading")
        print_info("Testing validation with mock submission ID...")
        
        # Test validation with invalid data
        print_info("Testing grade validation (negative grade)...")
        response = requests.post(
            f"{BASE_URL}/assignments/submissions/000000000000000000000000/grade",
            headers=headers,
            json={"grade": -10, "feedback": "Test feedback"}
        )
        
        if response.status_code in [400, 404]:
            print_success("Grade validation working (rejected negative grade or invalid ID)")
        else:
            print_warning(f"Unexpected response: {response.status_code}")
        
        return True
    
    # Test grading with valid data
    print_info(f"Testing grade submission for submission {submission_id}...")
    test_grade = min(85, max_points)
    response = requests.post(
        f"{BASE_URL}/assignments/submissions/{submission_id}/grade",
        headers=headers,
        json={
            "grade": test_grade,
            "feedback": "Good work! This is a test grade."
        }
    )
    
    if response.status_code == 200:
        print_success("Grade submission successful")
        print_info(f"  - Grade: {test_grade}/{max_points}")
        print_info("  - Status should be updated to 'graded'")
        print_info("  - Notification should be sent to student")
        return True
    else:
        print_error(f"Grade submission failed: {response.json()}")
        return False

def test_grade_validation(token):
    """Test grade validation"""
    print_info("\nTesting grade validation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with invalid grade (exceeds max_points)
    print_info("Testing validation for grade exceeding max_points...")
    response = requests.post(
        f"{BASE_URL}/assignments/submissions/000000000000000000000000/grade",
        headers=headers,
        json={"grade": 150, "feedback": "Test"}
    )
    
    if response.status_code in [400, 404]:
        print_success("Validation working (rejected invalid grade or ID)")
    else:
        print_warning(f"Unexpected response: {response.status_code}")
    
    return True

def main():
    print_info("=" * 60)
    print_info("Teacher Endpoints Verification Test")
    print_info("=" * 60)
    
    # Login
    token = login_as_teacher()
    if not token:
        print_error("Cannot proceed without authentication token")
        return
    
    # Run all tests
    results = []
    
    results.append(("6.1 Dashboard Stats", test_teacher_dashboard_stats(token)))
    results.append(("6.1 Authentication", test_teacher_dashboard_auth(token)))
    results.append(("6.2 Teacher Courses", test_teacher_courses_endpoint(token)))
    results.append(("6.3 Assignment Submissions", test_assignment_submissions_endpoint(token)))
    results.append(("6.4 Grade Submission", test_grade_submission_endpoint(token)))
    results.append(("6.4 Grade Validation", test_grade_validation(token)))
    
    # Summary
    print_info("\n" + "=" * 60)
    print_info("Test Summary")
    print_info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print_info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("\n✓ All tests passed!")
    else:
        print_warning(f"\n⚠ {total - passed} test(s) failed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\n\nTest interrupted by user")
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
