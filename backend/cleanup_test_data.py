"""
Cleanup script for test data created during course deletion tests
"""
import requests
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_PREFIX = "TEST_DELETE_"

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_info(text):
    print(f"ℹ️  {text}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def login_as_admin():
    """Login as admin or teacher to clean up test data"""
    print_header("Logging in for Cleanup")
    
    # Try teacher account first
    login_data = {
        "email": f"{TEST_PREFIX}teacher@test.com",
        "password": "TestPass123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Logged in as: {data.get('user', {}).get('name', 'User')}")
            return data.get('access_token')
        else:
            print_error(f"Login failed: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None

def get_test_courses(token):
    """Get all test courses"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/courses", headers=headers)
        if response.status_code == 200:
            courses = response.json().get('courses', [])
            # Filter test courses
            test_courses = [c for c in courses if c['title'].startswith(TEST_PREFIX)]
            return test_courses
        else:
            print_error(f"Failed to get courses: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error getting courses: {str(e)}")
        return []

def delete_course(token, course_id):
    """Delete a course"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/courses/{course_id}", headers=headers)
        return response.status_code == 200
    except Exception as e:
        print_error(f"Error deleting course: {str(e)}")
        return False

def main():
    print_header("Test Data Cleanup")
    print_info("This script removes all test courses created during testing")
    
    # Login
    token = login_as_admin()
    if not token:
        print_error("Cannot proceed without authentication")
        return
    
    # Get test courses
    print_header("Finding Test Courses")
    test_courses = get_test_courses(token)
    
    if not test_courses:
        print_success("No test courses found. Database is clean!")
        return
    
    print_info(f"Found {len(test_courses)} test courses")
    
    # Confirm deletion
    print("\nTest courses to be deleted:")
    for course in test_courses:
        print(f"  - {course['title']} (ID: {course['_id']})")
    
    confirm = input("\nProceed with deletion? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print_info("Cleanup cancelled")
        return
    
    # Delete courses
    print_header("Deleting Test Courses")
    deleted_count = 0
    failed_count = 0
    
    for course in test_courses:
        if delete_course(token, course['_id']):
            print_success(f"Deleted: {course['title']}")
            deleted_count += 1
        else:
            print_error(f"Failed to delete: {course['title']}")
            failed_count += 1
    
    # Summary
    print_header("Cleanup Summary")
    print(f"✅ Deleted: {deleted_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Total: {len(test_courses)}")
    
    if failed_count == 0:
        print_success("\n🎉 All test courses cleaned up successfully!")
    else:
        print_error(f"\n⚠️  {failed_count} courses could not be deleted")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
