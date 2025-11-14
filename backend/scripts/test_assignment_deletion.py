"""
Test script for assignment deletion permissions.

This script tests the following scenarios:
1. Teacher deletes own assignment (should succeed)
2. Teacher deletes another teacher's assignment (should fail with 403)
3. Admin deletes any assignment (should succeed)

Requirements tested: 2.1, 2.2, 2.3
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import requests
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/edunexa_lms')

# Test data
TEST_PREFIX = "test_deletion_"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")

def setup_test_data(db):
    """Create test users, courses, and assignments"""
    print_header("Setting up test data")
    
    # Create test users
    teacher1_data = {
        '_id': ObjectId(),
        'name': f'{TEST_PREFIX}teacher1',
        'email': f'{TEST_PREFIX}teacher1@test.com',
        'password': generate_password_hash('password123'),
        'role': 'teacher',
        'created_at': datetime.utcnow()
    }
    
    teacher2_data = {
        '_id': ObjectId(),
        'name': f'{TEST_PREFIX}teacher2',
        'email': f'{TEST_PREFIX}teacher2@test.com',
        'password': generate_password_hash('password123'),
        'role': 'teacher',
        'created_at': datetime.utcnow()
    }
    
    admin_data = {
        '_id': ObjectId(),
        'name': f'{TEST_PREFIX}admin',
        'email': f'{TEST_PREFIX}admin@test.com',
        'password': generate_password_hash('password123'),
        'role': 'admin',
        'created_at': datetime.utcnow()
    }
    
    # Insert users
    db.users.insert_one(teacher1_data)
    db.users.insert_one(teacher2_data)
    db.users.insert_one(admin_data)
    
    print_success(f"Created teacher1: {teacher1_data['email']}")
    print_success(f"Created teacher2: {teacher2_data['email']}")
    print_success(f"Created admin: {admin_data['email']}")
    
    # Create courses for each teacher
    course1_data = {
        '_id': ObjectId(),
        'title': f'{TEST_PREFIX}course1',
        'description': 'Test course 1',
        'teacher_id': str(teacher1_data['_id']),
        'created_at': datetime.utcnow()
    }
    
    course2_data = {
        '_id': ObjectId(),
        'title': f'{TEST_PREFIX}course2',
        'description': 'Test course 2',
        'teacher_id': str(teacher2_data['_id']),
        'created_at': datetime.utcnow()
    }
    
    db.courses.insert_one(course1_data)
    db.courses.insert_one(course2_data)
    
    print_success(f"Created course1 for teacher1")
    print_success(f"Created course2 for teacher2")
    
    # Create assignments for each course
    assignment1_data = {
        '_id': ObjectId(),
        'title': f'{TEST_PREFIX}assignment1',
        'description': 'Test assignment 1',
        'course_id': str(course1_data['_id']),
        'due_date': datetime.utcnow() + timedelta(days=7),
        'max_points': 100,
        'created_by': str(teacher1_data['_id']),
        'created_at': datetime.utcnow()
    }
    
    assignment2_data = {
        '_id': ObjectId(),
        'title': f'{TEST_PREFIX}assignment2',
        'description': 'Test assignment 2',
        'course_id': str(course2_data['_id']),
        'due_date': datetime.utcnow() + timedelta(days=7),
        'max_points': 100,
        'created_by': str(teacher2_data['_id']),
        'created_at': datetime.utcnow()
    }
    
    db.assignments.insert_one(assignment1_data)
    db.assignments.insert_one(assignment2_data)
    
    print_success(f"Created assignment1 for course1")
    print_success(f"Created assignment2 for course2")
    
    return {
        'teacher1': teacher1_data,
        'teacher2': teacher2_data,
        'admin': admin_data,
        'course1': course1_data,
        'course2': course2_data,
        'assignment1': assignment1_data,
        'assignment2': assignment2_data
    }

def cleanup_test_data(db):
    """Remove all test data"""
    print_header("Cleaning up test data")
    
    # Delete test users
    result = db.users.delete_many({'email': {'$regex': f'^{TEST_PREFIX}'}})
    print_info(f"Deleted {result.deleted_count} test users")
    
    # Delete test courses
    result = db.courses.delete_many({'title': {'$regex': f'^{TEST_PREFIX}'}})
    print_info(f"Deleted {result.deleted_count} test courses")
    
    # Delete test assignments
    result = db.assignments.delete_many({'title': {'$regex': f'^{TEST_PREFIX}'}})
    print_info(f"Deleted {result.deleted_count} test assignments")
    
    # Delete test submissions (if any)
    result = db.submissions.delete_many({'assignment_id': {'$regex': f'^{TEST_PREFIX}'}})
    print_info(f"Deleted {result.deleted_count} test submissions")

def login(email, password):
    """Login and get JWT token"""
    response = requests.post(
        f'{API_BASE_URL}/auth/login',
        json={'email': email, 'password': password}
    )
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print_error(f"Login failed for {email}: {response.text}")
        return None

def delete_assignment(assignment_id, token):
    """Delete an assignment using the API"""
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(
        f'{API_BASE_URL}/assignments/{assignment_id}',
        headers=headers
    )
    return response

def test_teacher_deletes_own_assignment(test_data):
    """Test: Teacher deletes own assignment (should succeed)"""
    print_header("Test 1: Teacher deletes own assignment")
    
    # Login as teacher1
    token = login(test_data['teacher1']['email'], 'password123')
    if not token:
        print_error("Failed to login as teacher1")
        return False
    
    print_info(f"Logged in as teacher1")
    
    # Try to delete own assignment
    assignment_id = str(test_data['assignment1']['_id'])
    response = delete_assignment(assignment_id, token)
    
    if response.status_code == 200:
        print_success(f"Teacher1 successfully deleted own assignment (Status: {response.status_code})")
        print_info(f"Response: {response.json()}")
        return True
    else:
        print_error(f"Teacher1 failed to delete own assignment (Status: {response.status_code})")
        print_error(f"Response: {response.text}")
        return False

def test_teacher_deletes_other_assignment(test_data):
    """Test: Teacher deletes another teacher's assignment (should fail with 403)"""
    print_header("Test 2: Teacher deletes another teacher's assignment")
    
    # Login as teacher1
    token = login(test_data['teacher1']['email'], 'password123')
    if not token:
        print_error("Failed to login as teacher1")
        return False
    
    print_info(f"Logged in as teacher1")
    
    # Try to delete teacher2's assignment
    assignment_id = str(test_data['assignment2']['_id'])
    response = delete_assignment(assignment_id, token)
    
    if response.status_code == 403:
        print_success(f"Teacher1 correctly denied from deleting teacher2's assignment (Status: {response.status_code})")
        print_info(f"Response: {response.json()}")
        return True
    else:
        print_error(f"Teacher1 was able to delete teacher2's assignment! (Status: {response.status_code})")
        print_error(f"Response: {response.text}")
        return False

def test_admin_deletes_any_assignment(test_data):
    """Test: Admin deletes any assignment (should succeed)"""
    print_header("Test 3: Admin deletes any assignment")
    
    # Login as admin
    token = login(test_data['admin']['email'], 'password123')
    if not token:
        print_error("Failed to login as admin")
        return False
    
    print_info(f"Logged in as admin")
    
    # Try to delete teacher2's assignment
    assignment_id = str(test_data['assignment2']['_id'])
    response = delete_assignment(assignment_id, token)
    
    if response.status_code == 200:
        print_success(f"Admin successfully deleted any assignment (Status: {response.status_code})")
        print_info(f"Response: {response.json()}")
        return True
    else:
        print_error(f"Admin failed to delete assignment (Status: {response.status_code})")
        print_error(f"Response: {response.text}")
        return False

def test_cascade_deletion(db, test_data):
    """Test: Verify that related submissions are deleted when assignment is deleted"""
    print_header("Test 4: Verify cascade deletion of submissions")
    
    # Create a student
    student_data = {
        '_id': ObjectId(),
        'name': f'{TEST_PREFIX}student',
        'email': f'{TEST_PREFIX}student@test.com',
        'password': generate_password_hash('password123'),
        'role': 'student',
        'created_at': datetime.utcnow()
    }
    db.users.insert_one(student_data)
    print_info(f"Created test student: {student_data['email']}")
    
    # Create a course for teacher1
    course_data = {
        '_id': ObjectId(),
        'title': f'{TEST_PREFIX}cascade_course',
        'description': 'Test course for cascade deletion',
        'teacher_id': str(test_data['teacher1']['_id']),
        'created_at': datetime.utcnow()
    }
    db.courses.insert_one(course_data)
    print_info(f"Created test course")
    
    # Create an assignment
    assignment_data = {
        '_id': ObjectId(),
        'title': f'{TEST_PREFIX}cascade_assignment',
        'description': 'Test assignment for cascade deletion',
        'course_id': str(course_data['_id']),
        'due_date': datetime.utcnow() + timedelta(days=7),
        'max_points': 100,
        'created_by': str(test_data['teacher1']['_id']),
        'created_at': datetime.utcnow()
    }
    db.assignments.insert_one(assignment_data)
    assignment_id = str(assignment_data['_id'])
    print_info(f"Created test assignment")
    
    # Create multiple submissions for this assignment
    submission1_data = {
        '_id': ObjectId(),
        'assignment_id': assignment_id,
        'student_id': str(student_data['_id']),
        'course_id': str(course_data['_id']),
        'text_content': 'Test submission 1',
        'submitted_at': datetime.utcnow(),
        'status': 'submitted'
    }
    
    submission2_data = {
        '_id': ObjectId(),
        'assignment_id': assignment_id,
        'student_id': str(test_data['teacher1']['_id']),  # Another submission
        'course_id': str(course_data['_id']),
        'text_content': 'Test submission 2',
        'submitted_at': datetime.utcnow(),
        'status': 'submitted'
    }
    
    db.submissions.insert_one(submission1_data)
    db.submissions.insert_one(submission2_data)
    print_info(f"Created 2 test submissions")
    
    # Verify submissions exist
    submission_count_before = db.submissions.count_documents({'assignment_id': assignment_id})
    print_info(f"Submissions before deletion: {submission_count_before}")
    
    if submission_count_before != 2:
        print_error(f"Expected 2 submissions, found {submission_count_before}")
        return False
    
    # Login as teacher1 and delete the assignment
    token = login(test_data['teacher1']['email'], 'password123')
    if not token:
        print_error("Failed to login as teacher1")
        return False
    
    response = delete_assignment(assignment_id, token)
    
    if response.status_code != 200:
        print_error(f"Failed to delete assignment (Status: {response.status_code})")
        return False
    
    print_success(f"Assignment deleted successfully")
    
    # Verify submissions are also deleted (cascade)
    submission_count_after = db.submissions.count_documents({'assignment_id': assignment_id})
    print_info(f"Submissions after deletion: {submission_count_after}")
    
    if submission_count_after == 0:
        print_success(f"All related submissions were deleted (cascade deletion works)")
        return True
    else:
        print_error(f"Cascade deletion failed! {submission_count_after} submissions still exist")
        return False

def main():
    """Main test execution"""
    print_header("Assignment Deletion Permission Tests")
    print_info(f"API Base URL: {API_BASE_URL}")
    print_info(f"MongoDB URI: {MONGO_URI}")
    
    # Connect to MongoDB
    try:
        client = MongoClient(MONGO_URI)
        db = client.edunexa_lms
        client.admin.command('ping')
        print_success("Connected to MongoDB")
    except Exception as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        return
    
    # Clean up any existing test data
    cleanup_test_data(db)
    
    # Setup test data
    test_data = setup_test_data(db)
    
    # Run tests
    results = []
    
    try:
        # Test 1: Teacher deletes own assignment
        results.append(('Teacher deletes own assignment', test_teacher_deletes_own_assignment(test_data)))
        
        # Test 2: Teacher deletes another teacher's assignment
        results.append(('Teacher deletes other assignment', test_teacher_deletes_other_assignment(test_data)))
        
        # Test 3: Admin deletes any assignment
        results.append(('Admin deletes any assignment', test_admin_deletes_any_assignment(test_data)))
        
        # Test 4: Verify cascade deletion
        results.append(('Cascade deletion of submissions', test_cascade_deletion(db, test_data)))
        
    finally:
        # Cleanup
        cleanup_test_data(db)
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All tests passed!{Colors.RESET}\n")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some tests failed!{Colors.RESET}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
