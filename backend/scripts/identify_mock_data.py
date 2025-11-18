#!/usr/bin/env python3
"""
Identify Mock/Seed Data in Database

This script identifies all mock/seed data in the database and provides
a detailed report of what needs to be cleaned up.

Usage:
    python backend/scripts/identify_mock_data.py
"""

import sys
import os
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def identify_seed_data(db):
    """Identify all seed/mock data in database"""
    
    print_header("Identifying Mock/Seed Data")
    
    # Known seed email patterns
    seed_email_patterns = [
        '@datams.edu',
        '@test.com',
        'teacher@',
        'student@',
        'admin@test'
    ]
    
    # Known seed course titles
    seed_course_titles = [
        'Introduction to Machine Learning',
        'Advanced Python Programming',
        'Data Science Fundamentals',
        'Web Development with React',
        'TEST_',
        'Mock',
        'Sample'
    ]
    
    # Find seed users
    print_header("1. Seed Users")
    seed_users = []
    
    for pattern in seed_email_patterns:
        users = list(db.users.find({'email': {'$regex': pattern, '$options': 'i'}}))
        seed_users.extend(users)
    
    # Remove duplicates
    seed_users = list({u['_id']: u for u in seed_users}.values())
    
    if seed_users:
        print_warning(f"Found {len(seed_users)} potential seed users:")
        for user in seed_users:
            print(f"\n  📧 {user['email']}")
            print(f"     Name: {user['name']}")
            print(f"     Role: {user['role']}")
            print(f"     Created: {user.get('created_at', 'N/A')}")
            
            # Check if user has created courses
            if user['role'] == 'teacher':
                courses_created = user.get('courses_created', [])
                if courses_created:
                    print(f"     Courses Created: {len(courses_created)}")
    else:
        print_success("No seed users found")
    
    # Find seed courses
    print_header("2. Seed Courses")
    
    # Get teacher IDs from seed users
    teacher_ids = [str(u['_id']) for u in seed_users if u['role'] == 'teacher']
    
    # Find courses by title or teacher
    seed_courses = []
    
    # By title
    for title_pattern in seed_course_titles:
        courses = list(db.courses.find({'title': {'$regex': title_pattern, '$options': 'i'}}))
        seed_courses.extend(courses)
    
    # By teacher ID
    if teacher_ids:
        courses = list(db.courses.find({'teacher_id': {'$in': teacher_ids}}))
        seed_courses.extend(courses)
    
    # Remove duplicates
    seed_courses = list({c['_id']: c for c in seed_courses}.values())
    
    if seed_courses:
        print_warning(f"Found {len(seed_courses)} potential seed courses:")
        for course in seed_courses:
            print(f"\n  📚 {course['title']}")
            print(f"     Category: {course.get('category', 'N/A')}")
            print(f"     Teacher ID: {course.get('teacher_id', 'N/A')}")
            print(f"     Created: {course.get('created_at', 'N/A')}")
            print(f"     Active: {course.get('is_active', True)}")
            
            # Get teacher info
            teacher = db.users.find_one({'_id': ObjectId(course['teacher_id'])})
            if teacher:
                print(f"     Teacher: {teacher['name']} ({teacher['email']})")
            
            # Count enrollments
            enrollment_count = db.enrollments.count_documents({'course_id': str(course['_id'])})
            print(f"     Enrollments: {enrollment_count}")
            
            # Count assignments
            assignment_count = db.assignments.count_documents({'course_id': str(course['_id'])})
            print(f"     Assignments: {assignment_count}")
    else:
        print_success("No seed courses found")
    
    # Find related data
    print_header("3. Related Data")
    
    course_ids = [str(c['_id']) for c in seed_courses]
    
    # Enrollments
    enrollments = list(db.enrollments.find({'course_id': {'$in': course_ids}}))
    if enrollments:
        print_warning(f"Found {len(enrollments)} enrollments in seed courses")
    else:
        print_success("No enrollments in seed courses")
    
    # Assignments
    assignments = list(db.assignments.find({'course_id': {'$in': course_ids}}))
    if assignments:
        print_warning(f"Found {len(assignments)} assignments in seed courses")
        assignment_ids = [str(a['_id']) for a in assignments]
        
        # Submissions
        submissions = list(db.submissions.find({'assignment_id': {'$in': assignment_ids}}))
        if submissions:
            print_warning(f"Found {len(submissions)} submissions for seed assignments")
        else:
            print_success("No submissions for seed assignments")
    else:
        print_success("No assignments in seed courses")
    
    # Materials
    materials = list(db.materials.find({'course_id': {'$in': course_ids}}))
    if materials:
        print_warning(f"Found {len(materials)} materials in seed courses")
    else:
        print_success("No materials in seed courses")
    
    # Summary
    print_header("Summary Report")
    
    total_seed_items = len(seed_users) + len(seed_courses) + len(enrollments) + len(assignments) + len(materials)
    
    if total_seed_items > 0:
        print_warning(f"⚠️  Found {total_seed_items} seed/mock data items in database:")
        print(f"\n   📊 Breakdown:")
        print(f"      Users: {len(seed_users)}")
        print(f"      Courses: {len(seed_courses)}")
        print(f"      Enrollments: {len(enrollments)}")
        print(f"      Assignments: {len(assignments)}")
        print(f"      Submissions: {len(submissions) if assignments else 0}")
        print(f"      Materials: {len(materials)}")
        
        print(f"\n   🧹 To clean up this data, run:")
        print(f"      python backend/scripts/cleanup_seed_data.py --confirm")
        
        # List specific courses to remove
        if seed_courses:
            print(f"\n   📚 Courses that will be removed:")
            for course in seed_courses:
                teacher = db.users.find_one({'_id': ObjectId(course['teacher_id'])})
                teacher_email = teacher['email'] if teacher else 'Unknown'
                print(f"      - {course['title']} (by {teacher_email})")
    else:
        print_success("✅ No seed/mock data found in database!")
        print_info("Database is clean and ready for production use.")
    
    return seed_users, seed_courses

def check_real_data(db):
    """Check for real (non-seed) data in database"""
    print_header("Real Data Check")
    
    # Count all users
    total_users = db.users.count_documents({})
    
    # Count non-seed users (not @datams.edu or @test.com)
    real_users = db.users.count_documents({
        'email': {
            '$not': {'$regex': '@datams.edu|@test.com', '$options': 'i'}
        }
    })
    
    print_info(f"Total users: {total_users}")
    print_info(f"Real users: {real_users}")
    print_info(f"Seed users: {total_users - real_users}")
    
    # Count all courses
    total_courses = db.courses.count_documents({})
    
    # Get seed teacher IDs
    seed_teachers = list(db.users.find({
        'role': 'teacher',
        'email': {'$regex': '@datams.edu|@test.com', '$options': 'i'}
    }))
    seed_teacher_ids = [str(t['_id']) for t in seed_teachers]
    
    # Count real courses (not by seed teachers)
    real_courses = db.courses.count_documents({
        'teacher_id': {'$nin': seed_teacher_ids}
    })
    
    print_info(f"Total courses: {total_courses}")
    print_info(f"Real courses: {real_courses}")
    print_info(f"Seed courses: {total_courses - real_courses}")
    
    if real_users > 0 or real_courses > 0:
        print_success(f"\n✅ Database contains real data:")
        print(f"   - {real_users} real users")
        print(f"   - {real_courses} real courses")
        print_warning("   ⚠️  Be careful when cleaning up - don't delete real data!")
    else:
        print_info("\nℹ️  Database contains only seed data")
        print_info("   Safe to clean up everything")

def main():
    print_header("Mock/Seed Data Identification Tool")
    
    # Connect to MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/edunexa_lms')
    
    try:
        client = MongoClient(MONGO_URI)
        db = client.edunexa_lms
        
        # Test connection
        client.admin.command('ping')
        print_success("Connected to MongoDB successfully!")
        
    except Exception as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    # Identify seed data
    seed_users, seed_courses = identify_seed_data(db)
    
    # Check for real data
    check_real_data(db)
    
    print("\n" + "="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Identification interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
