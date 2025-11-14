#!/usr/bin/env python3
"""
Manual test script for email notification service
Tests sending single emails, role-based notifications, and course participant notifications

Usage:
    python backend/scripts/test_email_notification.py
"""
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from dotenv import load_dotenv
from services.notification_service import (
    send_email,
    notify_users_by_role,
    notify_user_by_id,
    notify_course_participants
)

# Load environment variables
load_dotenv()


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_single_email(test_email):
    """Test sending a single email"""
    print_header("TEST 1: Send Single Email")
    
    subject = "EduNexa Test Email"
    body = "This is a test email from the EduNexa notification service."
    html = "<h2>EduNexa Test Email</h2><p>This is a test email from the EduNexa notification service.</p>"
    
    print(f"📧 Sending test email to: {test_email}")
    print(f"📝 Subject: {subject}")
    
    result = send_email(test_email, subject, body, html)
    
    if result:
        print("✅ Email sent successfully!")
    else:
        print("❌ Failed to send email")
        print("   Check EMAIL_ADDRESS and EMAIL_PASSWORD in .env file")
    
    return result


def test_role_based_notifications(db):
    """Test role-based notifications"""
    print_header("TEST 2: Role-Based Notifications")
    
    # Check if users exist
    admin_count = db.users.count_documents({"role": {"$in": ["admin", "super_admin"]}, "is_active": True})
    teacher_count = db.users.count_documents({"role": "teacher", "is_active": True})
    student_count = db.users.count_documents({"role": "student", "is_active": True})
    
    print(f"📊 Database Statistics:")
    print(f"   - Admins: {admin_count}")
    print(f"   - Teachers: {teacher_count}")
    print(f"   - Students: {student_count}")
    
    if admin_count == 0 and teacher_count == 0 and student_count == 0:
        print("⚠️  No users found in database. Run seed scripts first.")
        return False
    
    # Test notifying admins
    if admin_count > 0:
        print("\n📧 Sending notification to admins...")
        subject = "Test Admin Notification"
        body = "This is a test notification for administrators."
        
        result = notify_users_by_role(db, ["admin", "super_admin"], subject, body)
        print(f"   Result: {result['success']} sent, {result['failed']} failed")
    
    # Test notifying teachers
    if teacher_count > 0:
        print("\n📧 Sending notification to teachers...")
        subject = "Test Teacher Notification"
        body = "This is a test notification for teachers."
        
        result = notify_users_by_role(db, ["teacher"], subject, body)
        print(f"   Result: {result['success']} sent, {result['failed']} failed")
    
    # Test notifying students (limit to 3 for testing)
    if student_count > 0:
        print("\n📧 Sending notification to students (limited to 3)...")
        subject = "Test Student Notification"
        body = "This is a test notification for students."
        
        # Get first 3 students
        students = list(db.users.find({"role": "student", "is_active": True}).limit(3))
        student_ids = [str(s["_id"]) for s in students]
        
        result = notify_users_by_role(
            db, 
            ["student"], 
            subject, 
            body,
            extra_filter={"_id": {"$in": [s["_id"] for s in students]}}
        )
        print(f"   Result: {result['success']} sent, {result['failed']} failed")
    
    print("\n✅ Role-based notification tests completed")
    return True


def test_user_by_id_notification(db):
    """Test notifying a specific user by ID"""
    print_header("TEST 3: Notify User by ID")
    
    # Find a test user
    user = db.users.find_one({"is_active": True})
    
    if not user:
        print("⚠️  No users found in database. Run seed scripts first.")
        return False
    
    user_id = str(user["_id"])
    user_name = user.get("name", "Unknown")
    user_email = user.get("email", "No email")
    
    print(f"👤 Test User:")
    print(f"   - Name: {user_name}")
    print(f"   - Email: {user_email}")
    print(f"   - ID: {user_id}")
    
    subject = "Test Individual Notification"
    body = "This is a test notification sent to a specific user by ID."
    
    print(f"\n📧 Sending notification...")
    result = notify_user_by_id(db, user_id, subject, body)
    
    if result:
        print("✅ Notification sent successfully!")
    else:
        print("❌ Failed to send notification")
    
    return result


def test_course_participants_notification(db):
    """Test notifying course participants"""
    print_header("TEST 4: Course Participants Notification")
    
    # Find a course with enrollments
    course = db.courses.find_one({"is_active": True})
    
    if not course:
        print("⚠️  No courses found in database. Run seed scripts first.")
        return False
    
    course_id = str(course["_id"])
    course_title = course.get("title", "Unknown Course")
    
    # Count enrollments
    enrollment_count = db.enrollments.count_documents({"course_id": course_id})
    
    print(f"📚 Test Course:")
    print(f"   - Title: {course_title}")
    print(f"   - ID: {course_id}")
    print(f"   - Enrollments: {enrollment_count}")
    
    if enrollment_count == 0:
        print("⚠️  No enrollments found for this course")
        return False
    
    subject = f"Test Notification: {course_title}"
    body = f"This is a test notification for all participants of {course_title}."
    
    print(f"\n📧 Sending notification to course participants...")
    result = notify_course_participants(db, course_id, subject, body, include_teacher=True)
    
    print(f"   Result: {result['success']} sent, {result['failed']} failed")
    print("✅ Course participant notification test completed")
    
    return True


def main():
    """Main execution function"""
    print("=" * 60)
    print("  📧 Email Notification Service Test Suite")
    print("=" * 60)
    
    # Check environment variables
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("\n❌ Email credentials not configured!")
        print("   Please set EMAIL_ADDRESS and EMAIL_PASSWORD in backend/.env")
        print("\n   Example:")
        print("   EMAIL_ADDRESS=your-email@gmail.com")
        print("   EMAIL_PASSWORD=your-app-password")
        print("\n   See docs/DEV_NOTES.md for Gmail App Password setup")
        sys.exit(1)
    
    print(f"\n✅ Email configured: {EMAIL_ADDRESS}")
    
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
    
    # Ask for test email
    print("\n" + "-" * 60)
    test_email = input("Enter your email address for testing (or press Enter to skip): ").strip()
    
    # Run tests
    try:
        # Test 1: Single email (if provided)
        if test_email:
            test_single_email(test_email)
        else:
            print("\n⏭️  Skipping single email test (no email provided)")
        
        # Test 2: Role-based notifications
        test_role_based_notifications(db)
        
        # Test 3: User by ID notification
        test_user_by_id_notification(db)
        
        # Test 4: Course participants notification
        test_course_participants_notification(db)
        
        # Summary
        print("\n" + "=" * 60)
        print("  ✅ All Tests Completed!")
        print("=" * 60)
        print("\n📝 Notes:")
        print("   - Check your email inbox for test messages")
        print("   - Check spam folder if emails not received")
        print("   - Review backend logs for detailed error messages")
        print("   - Ensure Gmail App Password is correctly configured")
        
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
