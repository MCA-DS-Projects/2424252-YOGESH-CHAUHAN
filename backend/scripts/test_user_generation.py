#!/usr/bin/env python3
"""
Quick Test Script for User Generation System
Verifies that the test user generation system is working correctly.

Usage:
    python backend/scripts/test_user_generation.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_header(title):
    """Print formatted header"""
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


def main():
    """Main test function"""
    print_header("Test User Generation System - Quick Test")
    
    # Connect to MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/edunexa_lms')
    
    try:
        client = MongoClient(MONGO_URI)
        db = client.edunexa_lms
        client.admin.command('ping')
        print_success(f"Connected to MongoDB")
    except Exception as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    # Test 1: Check if test users exist
    print_header("Test 1: Check Test Users Exist")
    
    test_students = db.users.count_documents({
        "role": "student",
        "email": {"$regex": "@student\\.edu$"}
    })
    
    test_teachers = db.users.count_documents({
        "role": "teacher",
        "email": {"$regex": "@faculty\\.edu$"}
    })
    
    print_info(f"Test Students: {test_students}")
    print_info(f"Test Teachers: {test_teachers}")
    
    if test_students >= 100:
        print_success("✓ At least 100 test students found")
    else:
        print_error(f"✗ Only {test_students} test students found (expected 100)")
    
    if test_teachers >= 10:
        print_success("✓ At least 10 test teachers found")
    else:
        print_error(f"✗ Only {test_teachers} test teachers found (expected 10)")
    
    # Test 2: Check for unique emails
    print_header("Test 2: Check Email Uniqueness")
    
    duplicate_emails = list(db.users.aggregate([
        {"$match": {"email": {"$regex": "@(student|faculty)\\.edu$"}}},
        {"$group": {"_id": "$email", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]))
    
    if len(duplicate_emails) == 0:
        print_success("✓ All emails are unique")
    else:
        print_error(f"✗ Found {len(duplicate_emails)} duplicate emails")
        for dup in duplicate_emails[:5]:
            print_info(f"   Duplicate: {dup['_id']} (count: {dup['count']})")
    
    # Test 3: Check for unique roll numbers
    print_header("Test 3: Check Roll Number Uniqueness")
    
    duplicate_rolls = list(db.users.aggregate([
        {"$match": {"role": "student", "roll_number": {"$exists": True}}},
        {"$group": {"_id": "$roll_number", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]))
    
    if len(duplicate_rolls) == 0:
        print_success("✓ All roll numbers are unique")
    else:
        print_error(f"✗ Found {len(duplicate_rolls)} duplicate roll numbers")
    
    # Test 4: Check for unique employee IDs
    print_header("Test 4: Check Employee ID Uniqueness")
    
    duplicate_emp_ids = list(db.users.aggregate([
        {"$match": {"role": "teacher", "employee_id": {"$exists": True}}},
        {"$group": {"_id": "$employee_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]))
    
    if len(duplicate_emp_ids) == 0:
        print_success("✓ All employee IDs are unique")
    else:
        print_error(f"✗ Found {len(duplicate_emp_ids)} duplicate employee IDs")
    
    # Test 5: Check data structure
    print_header("Test 5: Check Data Structure")
    
    sample_student = db.users.find_one({
        "role": "student",
        "email": {"$regex": "@student\\.edu$"}
    })
    
    if sample_student:
        required_fields = ['name', 'email', 'roll_number', 'department', 'year', 
                          'phone', 'date_of_birth', 'profile_pic']
        missing_fields = [f for f in required_fields if f not in sample_student]
        
        if len(missing_fields) == 0:
            print_success("✓ Student records have all required fields")
        else:
            print_error(f"✗ Missing fields in student records: {', '.join(missing_fields)}")
    
    sample_teacher = db.users.find_one({
        "role": "teacher",
        "email": {"$regex": "@faculty\\.edu$"}
    })
    
    if sample_teacher:
        required_fields = ['name', 'email', 'employee_id', 'department', 'designation',
                          'phone', 'date_of_birth', 'profile_pic', 'specializations']
        missing_fields = [f for f in required_fields if f not in sample_teacher]
        
        if len(missing_fields) == 0:
            print_success("✓ Teacher records have all required fields")
        else:
            print_error(f"✗ Missing fields in teacher records: {', '.join(missing_fields)}")
    
    # Test 6: Sample data display
    print_header("Test 6: Sample Data")
    
    if sample_student:
        print("\n📚 Sample Student:")
        print(f"   Name: {sample_student.get('name')}")
        print(f"   Email: {sample_student.get('email')}")
        print(f"   Roll Number: {sample_student.get('roll_number')}")
        print(f"   Department: {sample_student.get('department')}")
        print(f"   Year: {sample_student.get('year')}")
    
    if sample_teacher:
        print("\n👨‍🏫 Sample Teacher:")
        print(f"   Name: {sample_teacher.get('name')}")
        print(f"   Email: {sample_teacher.get('email')}")
        print(f"   Employee ID: {sample_teacher.get('employee_id')}")
        print(f"   Department: {sample_teacher.get('department')}")
        print(f"   Designation: {sample_teacher.get('designation')}")
    
    # Summary
    print_header("Test Summary")
    
    all_tests_passed = (
        test_students >= 100 and
        test_teachers >= 10 and
        len(duplicate_emails) == 0 and
        len(duplicate_rolls) == 0 and
        len(duplicate_emp_ids) == 0
    )
    
    if all_tests_passed:
        print_success("\n🎉 All tests passed!")
        print_info("\nSystem is ready for demonstration:")
        print_info("  1. View users: python backend/scripts/view_test_users.py")
        print_info("  2. Start backend: cd backend && python run.py")
        print_info("  3. Test API: curl http://localhost:5000/api/test-users/stats")
    else:
        print_error("\n⚠️  Some tests failed. Please review the output above.")
        print_info("\nTo regenerate test users:")
        print_info("  python backend/scripts/generate_test_users.py")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
