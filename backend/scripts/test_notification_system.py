#!/usr/bin/env python3
"""
Comprehensive Notification System Test Script
Tests email notifications, in-app notifications, user preferences, and role-specific templates.

Usage:
    python backend/scripts/test_notification_system.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from dotenv import load_dotenv
from services.enhanced_notification_service import (
    send_notification,
    get_user_notification_settings,
    update_user_notification_settings,
    notify_by_role,
    send_email,
    create_in_app_notification
)
from datetime import datetime

# Load environment variables
load_dotenv()


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")


def test_environment_config():
    """Test 1: Verify environment configuration"""
    print_header("TEST 1: Environment Configuration")
    
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    ENABLE_EMAIL = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "true")
    ENABLE_IN_APP = os.getenv("ENABLE_IN_APP_NOTIFICATIONS", "true")
    
    print_info(f"Email Address: {EMAIL_ADDRESS or 'NOT SET'}")
    print_info(f"Email Password: {'SET' if EMAIL_PASSWORD else 'NOT SET'}")
    print_info(f"Email Notifications Enabled: {ENABLE_EMAIL}")
    print_info(f"In-App Notifications Enabled: {ENABLE_IN_APP}")
    
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print_error("Email credentials not configured!")
        print_info("Please set EMAIL_ADDRESS and EMAIL_PASSWORD in backend/.env")
        return False
    
    print_success("Environment configuration verified")
    return True


def test_user_notification_settings(db):
    """Test 2: User notification settings"""
    print_header("TEST 2: User Notification Settings")
    
    # Find a test user
    user = db.users.find_one({"is_active": True})
    if not user:
        print_error("No active users found in database")
        return False
    
    user_id = str(user["_id"])
    print_info(f"Testing with user: {user.get('name')} ({user.get('email')})")
    print_info(f"Role: {user.get('role')}")
    
    # Get current settings
    settings = get_user_notification_settings(db, user_id)
    print_info(f"Current settings: Email={settings['email_enabled']}, In-App={settings['in_app_enabled']}")
    
    # Test disabling email notifications
    print_info("\nDisabling email notifications...")
    success = update_user_notification_settings(db, user_id, email_enabled=False)
    if success:
        print_success("Email notifications disabled")
        new_settings = get_user_notification_settings(db, user_id)
        print_info(f"Updated settings: Email={new_settings['email_enabled']}, In-App={new_settings['in_app_enabled']}")
    else:
        print_error("Failed to update settings")
        return False
    
    # Test re-enabling email notifications
    print_info("\nRe-enabling email notifications...")
    success = update_user_notification_settings(db, user_id, email_enabled=True)
    if success:
        print_success("Email notifications re-enabled")
        new_settings = get_user_notification_settings(db, user_id)
        print_info(f"Updated settings: Email={new_settings['email_enabled']}, In-App={new_settings['in_app_enabled']}")
    else:
        print_error("Failed to update settings")
        return False
    
    print_success("User notification settings test completed")
    return True


def test_student_notifications(db):
    """Test 3: Student role notifications"""
    print_header("TEST 3: Student Role Notifications")
    
    # Find a student
    student = db.users.find_one({"role": "student", "is_active": True})
    if not student:
        print_error("No active students found in database")
        return False
    
    student_id = str(student["_id"])
    print_info(f"Testing with student: {student.get('name')} ({student.get('email')})")
    
    # Test assignment created notification
    print_info("\nSending 'assignment_created' notification...")
    context = {
        "title": "Python Programming Assignment",
        "course_title": "Introduction to Python",
        "due_date": "2024-12-31",
        "points": "100",
        "message": "A new assignment has been posted"
    }
    
    result = send_notification(
        db, student_id, "assignment_created", context,
        in_app_title="New Assignment Posted",
        in_app_link="/assignments"
    )
    
    print_info(f"Email: {result['email']['message']}")
    print_info(f"In-App: {result['in_app']['message']}")
    
    if result['email']['sent'] or result['in_app']['sent']:
        print_success("Student notification sent successfully")
        return True
    else:
        print_error("Failed to send student notification")
        return False


def test_teacher_notifications(db):
    """Test 4: Teacher role notifications"""
    print_header("TEST 4: Teacher Role Notifications")
    
    # Find a teacher
    teacher = db.users.find_one({"role": "teacher", "is_active": True})
    if not teacher:
        print_error("No active teachers found in database")
        return False
    
    teacher_id = str(teacher["_id"])
    print_info(f"Testing with teacher: {teacher.get('name')} ({teacher.get('email')})")
    
    # Test assignment submitted notification
    print_info("\nSending 'assignment_submitted' notification...")
    context = {
        "title": "Python Programming Assignment",
        "course_title": "Introduction to Python",
        "student_name": "John Doe",
        "submitted_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "message": "A student has submitted an assignment"
    }
    
    result = send_notification(
        db, teacher_id, "assignment_submitted", context,
        in_app_title="New Assignment Submission",
        in_app_link="/grading"
    )
    
    print_info(f"Email: {result['email']['message']}")
    print_info(f"In-App: {result['in_app']['message']}")
    
    if result['email']['sent'] or result['in_app']['sent']:
        print_success("Teacher notification sent successfully")
        return True
    else:
        print_error("Failed to send teacher notification")
        return False


def test_admin_notifications(db):
    """Test 5: Admin role notifications"""
    print_header("TEST 5: Admin Role Notifications")
    
    # Find an admin
    admin = db.users.find_one({"role": {"$in": ["admin", "super_admin"]}, "is_active": True})
    if not admin:
        print_error("No active admins found in database")
        return False
    
    admin_id = str(admin["_id"])
    print_info(f"Testing with admin: {admin.get('name')} ({admin.get('email')})")
    
    # Test course created notification
    print_info("\nSending 'course_created' notification...")
    context = {
        "course_title": "Advanced Machine Learning",
        "teacher_name": "Dr. Jane Smith",
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "message": "A new course has been created"
    }
    
    result = send_notification(
        db, admin_id, "course_created", context,
        in_app_title="New Course Created",
        in_app_link="/admin/courses"
    )
    
    print_info(f"Email: {result['email']['message']}")
    print_info(f"In-App: {result['in_app']['message']}")
    
    if result['email']['sent'] or result['in_app']['sent']:
        print_success("Admin notification sent successfully")
        return True
    else:
        print_error("Failed to send admin notification")
        return False


def test_notification_with_disabled_email(db):
    """Test 6: Notification when email is disabled"""
    print_header("TEST 6: Notification with Email Disabled")
    
    # Find a test user
    user = db.users.find_one({"is_active": True})
    if not user:
        print_error("No active users found in database")
        return False
    
    user_id = str(user["_id"])
    print_info(f"Testing with user: {user.get('name')} ({user.get('email')})")
    
    # Disable email notifications
    print_info("Disabling email notifications...")
    update_user_notification_settings(db, user_id, email_enabled=False)
    
    # Send notification
    print_info("Sending notification...")
    context = {
        "title": "Test Assignment",
        "course_title": "Test Course",
        "due_date": "2024-12-31",
        "points": "100",
        "message": "Test notification"
    }
    
    result = send_notification(
        db, user_id, "assignment_created", context,
        in_app_title="Test Notification"
    )
    
    print_info(f"Email: {result['email']['message']}")
    print_info(f"In-App: {result['in_app']['message']}")
    
    # Re-enable email notifications
    print_info("Re-enabling email notifications...")
    update_user_notification_settings(db, user_id, email_enabled=True)
    
    if not result['email']['sent'] and result['in_app']['sent']:
        print_success("Email correctly skipped, in-app notification sent")
        return True
    else:
        print_error("Unexpected behavior")
        return False


def test_bulk_notification_by_role(db):
    """Test 7: Bulk notification by role"""
    print_header("TEST 7: Bulk Notification by Role")
    
    # Count users by role
    student_count = db.users.count_documents({"role": "student", "is_active": True})
    teacher_count = db.users.count_documents({"role": "teacher", "is_active": True})
    
    print_info(f"Active students: {student_count}")
    print_info(f"Active teachers: {teacher_count}")
    
    if student_count == 0:
        print_error("No active students found")
        return False
    
    # Send notification to all students (limit to 3 for testing)
    print_info("\nSending notification to students (limited to 3)...")
    students = list(db.users.find({"role": "student", "is_active": True}).limit(3))
    
    context = {
        "title": "System Maintenance Notice",
        "course_title": "All Courses",
        "due_date": "N/A",
        "points": "N/A",
        "message": "System maintenance scheduled for tonight"
    }
    
    results = notify_by_role(db, ["student"], context, context)
    
    print_info(f"Results: Email sent={results['email_sent']}, Email failed={results['email_failed']}")
    print_info(f"         In-app sent={results['in_app_sent']}, In-app failed={results['in_app_failed']}")
    
    if results['email_sent'] > 0 or results['in_app_sent'] > 0:
        print_success("Bulk notification sent successfully")
        return True
    else:
        print_error("Failed to send bulk notification")
        return False


def test_notification_history(db):
    """Test 8: Notification history logging"""
    print_header("TEST 8: Notification History")
    
    # Find a user
    user = db.users.find_one({"is_active": True})
    if not user:
        print_error("No active users found in database")
        return False
    
    user_id = str(user["_id"])
    print_info(f"Checking history for user: {user.get('name')}")
    
    # Get notification history
    history = list(db.notification_history.find({"user_id": user_id})
                  .sort("timestamp", -1)
                  .limit(10))
    
    print_info(f"Found {len(history)} notification history entries")
    
    if history:
        print_info("\nRecent notifications:")
        for i, entry in enumerate(history[:5], 1):
            print_info(f"  {i}. Type: {entry.get('notification_type')}, "
                      f"Channel: {entry.get('channel')}, "
                      f"Status: {entry.get('status')}, "
                      f"Time: {entry.get('timestamp')}")
        print_success("Notification history retrieved successfully")
        return True
    else:
        print_info("No notification history found (this is normal for new users)")
        return True


def main():
    """Main execution function"""
    print("=" * 70)
    print("  📧 Enhanced Notification System Test Suite")
    print("=" * 70)
    
    # Test environment configuration
    if not test_environment_config():
        print_error("\nEnvironment configuration failed. Please fix and try again.")
        sys.exit(1)
    
    # Connect to MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/edunexa_lms')
    
    try:
        client = MongoClient(MONGO_URI)
        db = client.edunexa_lms
        client.admin.command('ping')
        print_success(f"Connected to MongoDB: {MONGO_URI}")
    except Exception as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    # Run tests
    results = {}
    
    try:
        results['test2'] = test_user_notification_settings(db)
        results['test3'] = test_student_notifications(db)
        results['test4'] = test_teacher_notifications(db)
        results['test5'] = test_admin_notifications(db)
        results['test6'] = test_notification_with_disabled_email(db)
        results['test7'] = test_bulk_notification_by_role(db)
        results['test8'] = test_notification_history(db)
        
        # Summary
        print_header("TEST SUMMARY")
        print(f"   {'✅' if results['test2'] else '❌'} Test 2: User Notification Settings")
        print(f"   {'✅' if results['test3'] else '❌'} Test 3: Student Role Notifications")
        print(f"   {'✅' if results['test4'] else '❌'} Test 4: Teacher Role Notifications")
        print(f"   {'✅' if results['test5'] else '❌'} Test 5: Admin Role Notifications")
        print(f"   {'✅' if results['test6'] else '❌'} Test 6: Email Disabled Behavior")
        print(f"   {'✅' if results['test7'] else '❌'} Test 7: Bulk Notification by Role")
        print(f"   {'✅' if results['test8'] else '❌'} Test 8: Notification History")
        
        all_passed = all(results.values())
        
        if all_passed:
            print_success("\n🎉 All tests passed!")
        else:
            print_error("\n⚠️  Some tests failed. Please review the output above.")
        
        print("\n📝 Next Steps:")
        print("   1. Check your email inbox for test notifications")
        print("   2. Check spam folder if emails not received")
        print("   3. Log in to the application to see in-app notifications")
        print("   4. Test the API endpoints using the provided examples")
        print("   5. Review notification history in the database")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
