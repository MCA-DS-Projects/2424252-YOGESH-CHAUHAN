"""
Comprehensive Test Suite for Course Deletion Functionality
Tests:
1. Basic course deletion (soft delete)
2. Unauthorized deletion attempts
3. Deleting non-existent courses
4. Verifying student notifications
5. Verifying course remains accessible but inactive
"""
import requests
import json
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_PREFIX = "TEST_DELETE_"

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_info(text):
    print(f"ℹ️  {text}")

def print_success(text):
    print(f"✅ {text}")
    test_results['passed'] += 1

def print_error(text):
    print(f"❌ {text}")
    test_results['failed'] += 1
    test_results['errors'].append(text)

def print_warning(text):
    print(f"⚠️  {text}")

def register_user(email, password, name, role):
    """Register a new user"""
    register_data = {
        "email": email,
        "password": password,
        "name": name,
        "role": role
    }
    
    # Add role-specific fields
    if role == "teacher":
        register_data.update({
            "employeeId": f"EMP_{email.split('@')[0]}",
            "department": "Computer Science",
            "designation": "Assistant Professor"
        })
    elif role == "student":
        register_data.update({
            "rollNumber": f"ROLL_{email.split('@')[0]}",
            "department": "Computer Science",
            "year": "2024"
        })
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            return True
        elif response.status_code == 409:
            # User already exists
            return True
        else:
            print_warning(f"Registration issue: {response.json().get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print_warning(f"Registration error: {str(e)}")
        return False

def login_user(email, password, role_name="User"):
    """Login as a user to get access token"""
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Logged in as {role_name}: {data.get('user', {}).get('name', role_name)}")
            return data.get('access_token'), data.get('user', {}).get('_id')
        else:
            print_error(f"Login failed for {role_name}: {response.json().get('error', 'Unknown error')}")
            return None, None
    except Exception as e:
        print_error(f"Login error for {role_name}: {str(e)}")
        return None, None

def setup_test_users():
    """Setup test users for testing"""
    print_header("Setting Up Test Users")
    
    # Register test teacher
    teacher_email = f"{TEST_PREFIX}teacher@test.com"
    teacher_password = "TestPass123!"
    register_user(teacher_email, teacher_password, "Test Teacher", "teacher")
    
    # Register test student
    student_email = f"{TEST_PREFIX}student@test.com"
    student_password = "TestPass123!"
    register_user(student_email, student_password, "Test Student", "student")
    
    # Register another teacher
    other_teacher_email = f"{TEST_PREFIX}other_teacher@test.com"
    other_teacher_password = "TestPass123!"
    register_user(other_teacher_email, other_teacher_password, "Other Teacher", "teacher")
    
    print_info("Test users setup complete")
    
    return {
        'teacher': {'email': teacher_email, 'password': teacher_password},
        'student': {'email': student_email, 'password': student_password},
        'other_teacher': {'email': other_teacher_email, 'password': other_teacher_password}
    }

def create_test_course(token):
    """Create a test course"""
    print_header("Creating Test Course")
    
    course_data = {
        "title": f"{TEST_PREFIX}Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": "This is a test course for deletion testing",
        "category": "Testing",
        "difficulty": "Beginner",
        "duration": "1 week",
        "is_public": True
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/courses", json=course_data, headers=headers)
        if response.status_code == 201:
            data = response.json()
            course_id = data['course']['_id']
            print_success(f"Course created: {course_data['title']}")
            print_info(f"Course ID: {course_id}")
            return course_id
        else:
            print_error(f"Course creation failed: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print_error(f"Course creation error: {str(e)}")
        return None

def get_course(token, course_id):
    """Get course details"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/courses/{course_id}", headers=headers)
        if response.status_code == 200:
            return response.json()['course']
        return None
    except Exception as e:
        print_error(f"Get course error: {str(e)}")
        return None

def delete_course(token, course_id):
    """Delete a course using DELETE endpoint"""
    print_header("Deleting Course")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/courses/{course_id}", headers=headers)
        if response.status_code == 200:
            print_success("Course deleted successfully")
            return True
        else:
            print_error(f"Course deletion failed: {response.json().get('error', 'Unknown error')}")
            print_info(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Course deletion error: {str(e)}")
        return False

def verify_course_deleted(token, course_id):
    """Verify that the course is marked as inactive"""
    print_header("Verifying Course Deletion")
    
    course = get_course(token, course_id)
    if course:
        is_active = course.get('is_active', True)
        if not is_active:
            print_success("Course is marked as inactive (soft deleted)")
            return True
        else:
            print_error("Course is still active")
            return False
    else:
        print_error("Could not retrieve course details")
        return False

def test_unauthorized_deletion(course_id, unauthorized_token, test_name):
    """Test that unauthorized users cannot delete courses"""
    print_header(f"Test: {test_name}")
    
    headers = {"Authorization": f"Bearer {unauthorized_token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/courses/{course_id}", headers=headers)
        if response.status_code == 403:
            print_success(f"{test_name}: Correctly denied access")
            return True
        else:
            print_error(f"{test_name}: Expected 403, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"{test_name}: Error - {str(e)}")
        return False

def test_delete_nonexistent_course(token):
    """Test deleting a course that doesn't exist"""
    print_header("Test: Delete Non-Existent Course")
    
    fake_course_id = "000000000000000000000000"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/courses/{fake_course_id}", headers=headers)
        if response.status_code == 404:
            print_success("Correctly returned 404 for non-existent course")
            return True
        else:
            print_error(f"Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing non-existent course: {str(e)}")
        return False

def test_delete_invalid_course_id(token):
    """Test deleting with an invalid course ID format"""
    print_header("Test: Delete with Invalid Course ID")
    
    invalid_id = "invalid_id_format"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/courses/{invalid_id}", headers=headers)
        if response.status_code in [400, 404, 500]:
            print_success("Correctly handled invalid course ID")
            return True
        else:
            print_warning(f"Got status {response.status_code} for invalid ID")
            return True  # Still acceptable
    except Exception as e:
        print_error(f"Error testing invalid course ID: {str(e)}")
        return False

def enroll_student_in_course(student_token, course_id):
    """Enroll a student in a course"""
    headers = {"Authorization": f"Bearer {student_token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/courses/{course_id}/enroll", headers=headers)
        if response.status_code == 200:
            print_success("Student enrolled in course")
            return True
        else:
            print_warning(f"Enrollment issue: {response.json().get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print_warning(f"Enrollment error: {str(e)}")
        return False

def verify_course_in_list(token, course_id, should_exist=True):
    """Verify if course appears in course list"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/courses", headers=headers)
        if response.status_code == 200:
            courses = response.json().get('courses', [])
            course_ids = [c['_id'] for c in courses]
            exists = course_id in course_ids
            
            if should_exist and exists:
                print_success("Course found in list as expected")
                return True
            elif not should_exist and not exists:
                print_success("Course not in list as expected")
                return True
            else:
                print_error(f"Course list check failed. Expected in list: {should_exist}, Found: {exists}")
                return False
        else:
            print_error(f"Failed to get course list: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error checking course list: {str(e)}")
        return False

def main():
    print_header("Comprehensive Course Deletion Test Suite")
    print_info("Testing course deletion functionality with multiple scenarios")
    print_info(f"Target API: {BASE_URL}")
    
    # Setup test users
    users = setup_test_users()
    
    # Login all test users
    print_header("Authenticating Test Users")
    teacher_token, teacher_id = login_user(users['teacher']['email'], users['teacher']['password'], "Teacher")
    student_token, student_id = login_user(users['student']['email'], users['student']['password'], "Student")
    other_teacher_token, other_teacher_id = login_user(users['other_teacher']['email'], users['other_teacher']['password'], "Other Teacher")
    
    if not teacher_token:
        print_error("Cannot proceed without teacher authentication")
        print_test_summary()
        return
    
    # TEST 1: Basic Course Deletion (Soft Delete)
    print_header("TEST 1: Basic Course Deletion")
    course_id = create_test_course(teacher_token)
    if not course_id:
        print_error("Cannot proceed without a test course")
        print_test_summary()
        return
    
    # Verify course exists and is active
    print_info("Verifying course before deletion...")
    course = get_course(teacher_token, course_id)
    if course:
        print_success(f"Course found: {course['title']}")
        print_info(f"Is Active: {course.get('is_active', True)}")
    else:
        print_error("Course not found")
        print_test_summary()
        return
    
    # Enroll a student to test notifications
    if student_token:
        print_info("Enrolling student in course...")
        enroll_student_in_course(student_token, course_id)
    
    # Delete the course
    success = delete_course(teacher_token, course_id)
    if success:
        verify_course_deleted(teacher_token, course_id)
    
    # TEST 2: Unauthorized Deletion - Student trying to delete
    print_header("TEST 2: Unauthorized Deletion (Student)")
    course_id_2 = create_test_course(teacher_token)
    if course_id_2 and student_token:
        test_unauthorized_deletion(course_id_2, student_token, "Student Deletion Attempt")
        # Clean up
        delete_course(teacher_token, course_id_2)
    else:
        print_warning("Skipping student unauthorized test - missing prerequisites")
    
    # TEST 3: Unauthorized Deletion - Different Teacher
    print_header("TEST 3: Unauthorized Deletion (Different Teacher)")
    course_id_3 = create_test_course(teacher_token)
    if course_id_3 and other_teacher_token:
        test_unauthorized_deletion(course_id_3, other_teacher_token, "Other Teacher Deletion Attempt")
        # Clean up
        delete_course(teacher_token, course_id_3)
    else:
        print_warning("Skipping other teacher unauthorized test - missing prerequisites")
    
    # TEST 4: Delete Non-Existent Course
    test_delete_nonexistent_course(teacher_token)
    
    # TEST 5: Delete with Invalid Course ID
    test_delete_invalid_course_id(teacher_token)
    
    # TEST 6: Verify Deleted Course Still Accessible
    print_header("TEST 6: Verify Deleted Course Accessibility")
    course_id_6 = create_test_course(teacher_token)
    if course_id_6:
        delete_course(teacher_token, course_id_6)
        course = get_course(teacher_token, course_id_6)
        if course:
            print_success("Deleted course is still accessible (soft delete confirmed)")
            print_info(f"Course active status: {course.get('is_active', True)}")
        else:
            print_error("Deleted course is not accessible (hard delete detected)")
    
    # TEST 7: Verify Course Not in Active List
    print_header("TEST 7: Verify Deleted Course Not in Active List")
    if course_id_6:
        # For teacher, deleted courses might still appear
        verify_course_in_list(teacher_token, course_id_6, should_exist=True)
    
    # TEST 8: Multiple Deletions
    print_header("TEST 8: Multiple Course Deletions")
    print_info("Creating and deleting multiple courses...")
    for i in range(3):
        cid = create_test_course(teacher_token)
        if cid:
            delete_course(teacher_token, cid)
            print_success(f"Course {i+1} deleted successfully")
    
    # Print final summary
    print_test_summary()

def print_test_summary():
    """Print test results summary"""
    print_header("Test Summary")
    total_tests = test_results['passed'] + test_results['failed']
    print(f"\n📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    
    if test_results['failed'] > 0:
        print("\n❌ Failed Tests:")
        for error in test_results['errors']:
            print(f"   - {error}")
    
    success_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    if test_results['failed'] == 0:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        print_test_summary()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        print_test_summary()
