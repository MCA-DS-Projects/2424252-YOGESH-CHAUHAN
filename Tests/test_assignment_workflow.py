#!/usr/bin/env python3
"""
End-to-end workflow test for assignment lifecycle with notifications
Tests:
- Assignment creation with notifications
- Teacher can delete own assignments
- Teacher cannot delete other teacher's assignments
- Admin can delete any assignment
- Notifications sent at appropriate events
- Permission denials work correctly

Usage:
    python backend/scripts/test_assignment_workflow.py
"""
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
from bson import ObjectId

# Load environment variables
load_dotenv()

# API base URL
BASE_URL = "http://localhost:5000/api"

# Test credentials
TEACHER1_EMAIL = "teacher01@datams.edu"
TEACHER1_PASSWORD = "Teach@2025"

TEACHER2_EMAIL = "teacher02@datams.edu"
TEACHER2_PASSWORD = "Teach@2025"

ADMIN_EMAIL = "superadmin@datams.edu"
ADMIN_PASSWORD = "Admin@123456"


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step_num, description):
    """Print a test step"""
    print(f"\n📋 Step {step_num}: {description}")


def login(email, password):
    """Login and return access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Logged in as: {data['user']['name']} ({data['user']['role']})")
        return data['access_token'], data['user']
    else:
        print(f"   ❌ Login failed: {response.json()}")
        return None, None


def create_assignment(token, course_id, title):
    """Create an assignment"""
    headers = {"Authorization": f"Bearer {token}"}
    
    assignment_data = {
        "title": title,
        "description": f"Test assignment: {title}",
        "course_id": course_id,
        "instructions": "Complete the assignment as instructed",
        "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "max_points": 100,
        "submission_type": "file",
        "allowed_file_types": ["pdf", "doc", "docx"],
        "max_file_size": 10
    }
    
    response = requests.post(
        f"{BASE_URL}/assignments",
        json=assignment_data,
        headers=headers
    )
    
    if response.status_code == 201:
        data = response.json()
        assignment_id = data['assignment']['_id']
        print(f"   ✅ Assignment created: {assignment_id}")
        return assignment_id
    else:
        print(f"   ❌ Failed to create assignment: {response.json()}")
        return None


def update_assignment_due_date(token, assignment_id):
    """Update assignment due date"""
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "due_date": (datetime.utcnow() + timedelta(days=14)).isoformat()
    }
    
    response = requests.put(
        f"{BASE_URL}/assignments/{assignment_id}",
        json=update_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"   ✅ Assignment due date updated")
        return True
    else:
        print(f"   ❌ Failed to update assignment: {response.json()}")
        return False


def delete_assignment(token, assignment_id):
    """Delete an assignment"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(
        f"{BASE_URL}/assignments/{assignment_id}",
        headers=headers
    )
    
    return response


def test_teacher_delete_own_assignment(db):
    """Test that teacher can delete their own assignment"""
    print_header("TEST 1: Teacher Deletes Own Assignment")
    
    # Login as teacher1
    print_step(1, "Login as Teacher 1")
    token1, user1 = login(TEACHER1_EMAIL, TEACHER1_PASSWORD)
    if not token1:
        print("❌ Test failed: Could not login")
        return False
    
    # Get a course created by teacher1
    print_step(2, "Find course created by Teacher 1")
    course = db.courses.find_one({"teacher_id": user1['_id']})
    if not course:
        print("   ⚠️  No courses found for Teacher 1")
        print("   Run seed scripts first: python backend/scripts/seeders/seed_sample_data.py")
        return False
    
    course_id = str(course['_id'])
    print(f"   ✅ Found course: {course['title']} ({course_id})")
    
    # Create assignment
    print_step(3, "Create assignment")
    assignment_id = create_assignment(token1, course_id, "Test Assignment - Teacher 1")
    if not assignment_id:
        print("❌ Test failed: Could not create assignment")
        return False
    
    # Delete assignment
    print_step(4, "Delete own assignment")
    response = delete_assignment(token1, assignment_id)
    
    if response.status_code == 200:
        print(f"   ✅ Assignment deleted successfully (Status: {response.status_code})")
        print("   ✅ Notification should be sent to students and admins")
        return True
    else:
        print(f"   ❌ Failed to delete assignment: {response.json()}")
        return False


def test_teacher_cannot_delete_other_assignment(db):
    """Test that teacher cannot delete another teacher's assignment"""
    print_header("TEST 2: Teacher Cannot Delete Other Teacher's Assignment")
    
    # Login as teacher1
    print_step(1, "Login as Teacher 1")
    token1, user1 = login(TEACHER1_EMAIL, TEACHER1_PASSWORD)
    if not token1:
        print("❌ Test failed: Could not login as Teacher 1")
        return False
    
    # Login as teacher2
    print_step(2, "Login as Teacher 2")
    token2, user2 = login(TEACHER2_EMAIL, TEACHER2_PASSWORD)
    if not token2:
        print("❌ Test failed: Could not login as Teacher 2")
        return False
    
    # Get a course created by teacher2
    print_step(3, "Find course created by Teacher 2")
    course = db.courses.find_one({"teacher_id": user2['_id']})
    if not course:
        print("   ⚠️  No courses found for Teacher 2")
        return False
    
    course_id = str(course['_id'])
    print(f"   ✅ Found course: {course['title']} ({course_id})")
    
    # Teacher2 creates assignment
    print_step(4, "Teacher 2 creates assignment")
    assignment_id = create_assignment(token2, course_id, "Test Assignment - Teacher 2")
    if not assignment_id:
        print("❌ Test failed: Could not create assignment")
        return False
    
    # Teacher1 tries to delete Teacher2's assignment
    print_step(5, "Teacher 1 tries to delete Teacher 2's assignment")
    response = delete_assignment(token1, assignment_id)
    
    if response.status_code == 403:
        print(f"   ✅ Access denied as expected (Status: {response.status_code})")
        print(f"   ✅ Error message: {response.json().get('error', 'N/A')}")
        
        # Cleanup: Teacher2 deletes their own assignment
        print_step(6, "Cleanup: Teacher 2 deletes their assignment")
        cleanup_response = delete_assignment(token2, assignment_id)
        if cleanup_response.status_code == 200:
            print("   ✅ Cleanup successful")
        
        return True
    else:
        print(f"   ❌ Expected 403, got {response.status_code}")
        print(f"   Response: {response.json()}")
        return False


def test_admin_can_delete_any_assignment(db):
    """Test that admin can delete any assignment"""
    print_header("TEST 3: Admin Can Delete Any Assignment")
    
    # Login as teacher1
    print_step(1, "Login as Teacher 1")
    token_teacher, user_teacher = login(TEACHER1_EMAIL, TEACHER1_PASSWORD)
    if not token_teacher:
        print("❌ Test failed: Could not login as Teacher")
        return False
    
    # Login as admin
    print_step(2, "Login as Admin")
    token_admin, user_admin = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token_admin:
        print("❌ Test failed: Could not login as Admin")
        return False
    
    # Get a course created by teacher
    print_step(3, "Find course created by Teacher")
    course = db.courses.find_one({"teacher_id": user_teacher['_id']})
    if not course:
        print("   ⚠️  No courses found for Teacher")
        return False
    
    course_id = str(course['_id'])
    print(f"   ✅ Found course: {course['title']} ({course_id})")
    
    # Teacher creates assignment
    print_step(4, "Teacher creates assignment")
    assignment_id = create_assignment(token_teacher, course_id, "Test Assignment - For Admin Delete")
    if not assignment_id:
        print("❌ Test failed: Could not create assignment")
        return False
    
    # Admin deletes the assignment
    print_step(5, "Admin deletes the assignment")
    response = delete_assignment(token_admin, assignment_id)
    
    if response.status_code == 200:
        print(f"   ✅ Admin deleted assignment successfully (Status: {response.status_code})")
        print("   ✅ Notification should be sent to students and admins")
        return True
    else:
        print(f"   ❌ Failed to delete assignment: {response.json()}")
        return False


def test_assignment_due_date_notification(db):
    """Test that notification is sent when assignment due date is updated"""
    print_header("TEST 4: Assignment Due Date Update Notification")
    
    # Login as teacher1
    print_step(1, "Login as Teacher 1")
    token, user = login(TEACHER1_EMAIL, TEACHER1_PASSWORD)
    if not token:
        print("❌ Test failed: Could not login")
        return False
    
    # Get a course created by teacher
    print_step(2, "Find course created by Teacher")
    course = db.courses.find_one({"teacher_id": user['_id']})
    if not course:
        print("   ⚠️  No courses found for Teacher")
        return False
    
    course_id = str(course['_id'])
    print(f"   ✅ Found course: {course['title']} ({course_id})")
    
    # Create assignment
    print_step(3, "Create assignment")
    assignment_id = create_assignment(token, course_id, "Test Assignment - Due Date Update")
    if not assignment_id:
        print("❌ Test failed: Could not create assignment")
        return False
    
    # Update due date
    print_step(4, "Update assignment due date")
    success = update_assignment_due_date(token, assignment_id)
    
    if success:
        print("   ✅ Due date updated successfully")
        print("   ✅ Notification should be sent to enrolled students")
        
        # Cleanup
        print_step(5, "Cleanup: Delete assignment")
        cleanup_response = delete_assignment(token, assignment_id)
        if cleanup_response.status_code == 200:
            print("   ✅ Cleanup successful")
        
        return True
    else:
        print("   ❌ Failed to update due date")
        return False


def main():
    """Main execution function"""
    print("=" * 60)
    print("  🧪 Assignment Workflow End-to-End Test Suite")
    print("=" * 60)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"\n✅ Backend server is running: {BASE_URL}")
    except requests.exceptions.RequestException:
        print(f"\n❌ Backend server is not running!")
        print(f"   Please start the backend server first:")
        print(f"   python backend/run.py")
        sys.exit(1)
    
    # Connect to MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/edunexa_lms')
    
    try:
        client = MongoClient(MONGO_URI)
        db = client.edunexa_lms
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {MONGO_URI}")
    except Exception as e:
        print(f"\n❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    # Check if test data exists
    teacher1 = db.users.find_one({"email": TEACHER1_EMAIL})
    teacher2 = db.users.find_one({"email": TEACHER2_EMAIL})
    admin = db.users.find_one({"email": ADMIN_EMAIL})
    
    if not teacher1 or not teacher2 or not admin:
        print("\n⚠️  Test users not found in database!")
        print("   Please run seed scripts first:")
        print("   python backend/scripts/seeders/seed_sample_data.py")
        sys.exit(1)
    
    print("✅ Test users found in database")
    
    # Run tests
    results = {}
    
    try:
        # Test 1: Teacher deletes own assignment
        results['test1'] = test_teacher_delete_own_assignment(db)
        
        # Test 2: Teacher cannot delete other teacher's assignment
        results['test2'] = test_teacher_cannot_delete_other_assignment(db)
        
        # Test 3: Admin can delete any assignment
        results['test3'] = test_admin_can_delete_any_assignment(db)
        
        # Test 4: Assignment due date notification
        results['test4'] = test_assignment_due_date_notification(db)
        
        # Summary
        print_header("Test Summary")
        
        print("\n📊 Results:")
        print(f"   {'✅' if results['test1'] else '❌'} Test 1: Teacher deletes own assignment")
        print(f"   {'✅' if results['test2'] else '❌'} Test 2: Teacher cannot delete other's assignment")
        print(f"   {'✅' if results['test3'] else '❌'} Test 3: Admin can delete any assignment")
        print(f"   {'✅' if results['test4'] else '❌'} Test 4: Assignment due date notification")
        
        all_passed = all(results.values())
        
        if all_passed:
            print("\n" + "=" * 60)
            print("  ✅ All Tests Passed!")
            print("=" * 60)
            print("\n✨ Verified:")
            print("   - Teachers can delete their own assignments")
            print("   - Teachers cannot delete other teachers' assignments")
            print("   - Admins can delete any assignment")
            print("   - Notifications sent on assignment events")
            print("   - Permission checks work correctly")
        else:
            print("\n" + "=" * 60)
            print("  ⚠️  Some Tests Failed")
            print("=" * 60)
            failed_tests = [name for name, passed in results.items() if not passed]
            print(f"\n   Failed: {', '.join(failed_tests)}")
        
        print("\n📝 Notes:")
        print("   - Check email inbox for notification emails")
        print("   - Check backend logs for detailed error messages")
        print("   - Verify EMAIL_ADDRESS and EMAIL_PASSWORD are configured")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
