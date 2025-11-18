#!/usr/bin/env python3
"""
Cleanup Script for Seed Sample Data

This script removes all sample/test data that was created by seed_sample_data.py
It identifies and removes:
- Sample users (teacher01@datams.edu, teacher02@datams.edu, student01-03@datams.edu)
- Sample courses created by these teachers
- Related enrollments, assignments, and submissions

Usage:
    python backend/scripts/cleanup_seed_data.py
"""

import sys
import os

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

def find_seed_users(db):
    """Find all users created by seed script"""
    seed_emails = [
        'student01@datams.edu',
        'student02@datams.edu',
        'student03@datams.edu',
        'teacher01@datams.edu',
        'teacher02@datams.edu',
        'superadmin@datams.edu'
    ]
    
    users = list(db.users.find({'email': {'$in': seed_emails}}))
    return users

def find_seed_courses(db, teacher_ids):
    """Find all courses created by seed teachers"""
    # Known seed course titles
    seed_course_titles = [
        'Introduction to Machine Learning',
        'Advanced Python Programming',
        'Data Science Fundamentals',
        'Web Development with React'
    ]
    
    # Find by title OR by teacher_id
    courses = list(db.courses.find({
        '$or': [
            {'title': {'$in': seed_course_titles}},
            {'teacher_id': {'$in': teacher_ids}}
        ]
    }))
    
    return courses

def cleanup_seed_data(db, dry_run=True):
    """Remove all seed data from database"""
    
    print_header("Finding Seed Data")
    
    # Find seed users
    seed_users = find_seed_users(db)
    if not seed_users:
        print_success("No seed users found in database")
        return
    
    print_info(f"Found {len(seed_users)} seed users:")
    for user in seed_users:
        print(f"  - {user['name']} ({user['email']}) - {user['role']}")
    
    # Get teacher IDs
    teacher_ids = [str(u['_id']) for u in seed_users if u['role'] == 'teacher']
    student_ids = [str(u['_id']) for u in seed_users if u['role'] == 'student']
    
    # Find seed courses
    seed_courses = find_seed_courses(db, teacher_ids)
    print_info(f"Found {len(seed_courses)} seed courses:")
    for course in seed_courses:
        print(f"  - {course['title']}")
    
    course_ids = [str(c['_id']) for c in seed_courses]
    
    # Find related data
    enrollments = list(db.enrollments.find({'course_id': {'$in': course_ids}}))
    assignments = list(db.assignments.find({'course_id': {'$in': course_ids}}))
    assignment_ids = [str(a['_id']) for a in assignments]
    submissions = list(db.submissions.find({'assignment_id': {'$in': assignment_ids}}))
    materials = list(db.materials.find({'course_id': {'$in': course_ids}}))
    
    print_info(f"Found {len(enrollments)} enrollments")
    print_info(f"Found {len(assignments)} assignments")
    print_info(f"Found {len(submissions)} submissions")
    print_info(f"Found {len(materials)} materials")
    
    # Summary
    print_header("Cleanup Summary")
    print(f"📊 Data to be removed:")
    print(f"   Users: {len(seed_users)}")
    print(f"   Courses: {len(seed_courses)}")
    print(f"   Enrollments: {len(enrollments)}")
    print(f"   Assignments: {len(assignments)}")
    print(f"   Submissions: {len(submissions)}")
    print(f"   Materials: {len(materials)}")
    
    if dry_run:
        print_warning("\n🔍 DRY RUN MODE - No data will be deleted")
        print_info("Run with --confirm flag to actually delete the data")
        return
    
    # Confirm deletion
    print_warning("\n⚠️  WARNING: This will permanently delete all seed data!")
    confirm = input("Type 'DELETE' to confirm: ").strip()
    
    if confirm != 'DELETE':
        print_info("Cleanup cancelled")
        return
    
    # Perform deletion
    print_header("Deleting Seed Data")
    
    try:
        # Delete in reverse order of dependencies
        
        # 1. Delete submissions
        if submissions:
            result = db.submissions.delete_many({'assignment_id': {'$in': assignment_ids}})
            print_success(f"Deleted {result.deleted_count} submissions")
        
        # 2. Delete assignments
        if assignments:
            result = db.assignments.delete_many({'course_id': {'$in': course_ids}})
            print_success(f"Deleted {result.deleted_count} assignments")
        
        # 3. Delete materials
        if materials:
            result = db.materials.delete_many({'course_id': {'$in': course_ids}})
            print_success(f"Deleted {result.deleted_count} materials")
        
        # 4. Delete enrollments
        if enrollments:
            result = db.enrollments.delete_many({'course_id': {'$in': course_ids}})
            print_success(f"Deleted {result.deleted_count} enrollments")
        
        # 5. Delete courses
        if seed_courses:
            result = db.courses.delete_many({'_id': {'$in': [c['_id'] for c in seed_courses]}})
            print_success(f"Deleted {result.deleted_count} courses")
        
        # 6. Delete users
        if seed_users:
            result = db.users.delete_many({'_id': {'$in': [u['_id'] for u in seed_users]}})
            print_success(f"Deleted {result.deleted_count} users")
        
        print_header("Cleanup Complete")
        print_success("🎉 All seed data has been removed successfully!")
        
    except Exception as e:
        print_error(f"Error during cleanup: {str(e)}")
        import traceback
        traceback.print_exc()

def verify_cleanup(db):
    """Verify that seed data has been removed"""
    print_header("Verification")
    
    # Check for seed users
    seed_users = find_seed_users(db)
    if seed_users:
        print_warning(f"Still found {len(seed_users)} seed users")
        return False
    else:
        print_success("No seed users found ✓")
    
    # Check for seed courses
    seed_course_titles = [
        'Introduction to Machine Learning',
        'Advanced Python Programming',
        'Data Science Fundamentals',
        'Web Development with React'
    ]
    
    seed_courses = list(db.courses.find({'title': {'$in': seed_course_titles}}))
    if seed_courses:
        print_warning(f"Still found {len(seed_courses)} seed courses")
        return False
    else:
        print_success("No seed courses found ✓")
    
    print_success("\n✅ Database is clean!")
    return True

def main():
    print_header("Seed Data Cleanup Script")
    
    # Check for --confirm flag
    dry_run = '--confirm' not in sys.argv
    
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
    
    # Run cleanup
    cleanup_seed_data(db, dry_run=dry_run)
    
    # Verify if not dry run
    if not dry_run:
        verify_cleanup(db)
    
    print("\n" + "="*70)
    if dry_run:
        print_info("To actually delete the data, run:")
        print_info("  python backend/scripts/cleanup_seed_data.py --confirm")
    print("="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
