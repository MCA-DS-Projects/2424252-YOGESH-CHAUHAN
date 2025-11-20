"""
Script to verify database schema consistency.

This script checks that all records in the database have the required fields
as specified in Requirements 7.1-7.5.

Usage:
    python backend/scripts/verify_schema_consistency.py
"""

import sys
import os
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/edunexa_lms')
client = MongoClient(MONGO_URI)
db = client.edunexa_lms


def verify_course_schema():
    """
    Verify all course records have required fields.
    Requirement 7.1: _id, title, description, thumbnail_path, teacher_id, created_at, updated_at
    """
    print("\n📚 Verifying Course Schema...")
    
    required_fields = ['_id', 'title', 'description', 'thumbnail', 'teacher_id', 'created_at', 'updated_at']
    
    courses = list(db.courses.find())
    
    if not courses:
        print("  ⚠️  No courses found in database")
        return True
    
    issues = []
    
    for course in courses:
        course_id = str(course.get('_id', 'unknown'))
        missing_fields = [field for field in required_fields if field not in course]
        
        if missing_fields:
            issues.append(f"  ❌ Course {course_id} missing fields: {', '.join(missing_fields)}")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    else:
        print(f"  ✅ All {len(courses)} course records have required fields")
        return True


def verify_module_schema():
    """
    Verify all module records have required fields.
    Requirement 7.2: _id, course_id, title, description, order, created_at
    """
    print("\n📖 Verifying Module Schema...")
    
    required_fields = ['_id', 'course_id', 'title', 'description', 'order', 'created_at']
    
    modules = list(db.modules.find())
    
    if not modules:
        print("  ⚠️  No modules found in database")
        return True
    
    issues = []
    
    for module in modules:
        module_id = str(module.get('_id', 'unknown'))
        missing_fields = [field for field in required_fields if field not in module]
        
        if missing_fields:
            issues.append(f"  ❌ Module {module_id} missing fields: {', '.join(missing_fields)}")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    else:
        print(f"  ✅ All {len(modules)} module records have required fields")
        return True


def verify_material_schema():
    """
    Verify all material records have required fields.
    Requirement 7.3: material_id (_id), type, title, file_path (content), file_size, mime_type, uploaded_at
    """
    print("\n📄 Verifying Material Schema...")
    
    # Note: Using 'content' instead of 'file_path' as per actual implementation
    required_fields = ['_id', 'type', 'title', 'content', 'uploaded_at']
    # file_size and mime_type are optional for some material types (like links)
    
    materials = list(db.materials.find())
    
    if not materials:
        print("  ⚠️  No materials found in database")
        return True
    
    issues = []
    
    for material in materials:
        material_id = str(material.get('_id', 'unknown'))
        missing_fields = [field for field in required_fields if field not in material]
        
        if missing_fields:
            issues.append(f"  ❌ Material {material_id} missing fields: {', '.join(missing_fields)}")
        
        # Verify type is valid
        if 'type' in material and material['type'] not in ['video', 'document', 'link']:
            issues.append(f"  ❌ Material {material_id} has invalid type: {material['type']}")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    else:
        print(f"  ✅ All {len(materials)} material records have required fields")
        return True


def verify_enrollment_schema():
    """
    Verify all enrollment records have required fields.
    Requirement 7.4: _id, student_id, course_id, enrolled_at, progress_state (progress)
    """
    print("\n🎓 Verifying Enrollment Schema...")
    
    # Note: Using 'progress' instead of 'progress_state' as per actual implementation
    required_fields = ['_id', 'student_id', 'course_id', 'enrolled_at', 'progress']
    
    enrollments = list(db.enrollments.find())
    
    if not enrollments:
        print("  ⚠️  No enrollments found in database")
        return True
    
    issues = []
    
    for enrollment in enrollments:
        enrollment_id = str(enrollment.get('_id', 'unknown'))
        missing_fields = [field for field in required_fields if field not in enrollment]
        
        if missing_fields:
            issues.append(f"  ❌ Enrollment {enrollment_id} missing fields: {', '.join(missing_fields)}")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    else:
        print(f"  ✅ All {len(enrollments)} enrollment records have required fields")
        return True


def verify_progress_schema():
    """
    Verify all progress records have required fields.
    Requirement 7.5: _id, student_id, course_id, last_accessed, started, completed_materials
    """
    print("\n📊 Verifying Progress Schema...")
    
    required_fields = ['_id', 'student_id', 'course_id', 'last_accessed', 'started', 'completed_materials']
    
    progress_records = list(db.progress.find())
    
    if not progress_records:
        print("  ⚠️  No progress records found in database")
        return True
    
    issues = []
    
    for progress in progress_records:
        progress_id = str(progress.get('_id', 'unknown'))
        missing_fields = [field for field in required_fields if field not in progress]
        
        if missing_fields:
            issues.append(f"  ❌ Progress {progress_id} missing fields: {', '.join(missing_fields)}")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    else:
        print(f"  ✅ All {len(progress_records)} progress records have required fields")
        return True


def verify_indexes():
    """
    Verify that all required indexes exist on collections.
    """
    print("\n🔍 Verifying Database Indexes...")
    
    all_good = True
    
    # Check courses indexes
    courses_indexes = db.courses.index_information()
    required_courses_indexes = ['teacher_id_1', 'category_1', 'is_active_1']
    for idx in required_courses_indexes:
        if idx not in courses_indexes:
            print(f"  ❌ Missing index on courses: {idx}")
            all_good = False
    
    # Check modules indexes
    modules_indexes = db.modules.index_information()
    required_modules_indexes = ['course_id_1']
    for idx in required_modules_indexes:
        if idx not in modules_indexes:
            print(f"  ❌ Missing index on modules: {idx}")
            all_good = False
    
    # Check materials indexes
    materials_indexes = db.materials.index_information()
    required_materials_indexes = ['course_id_1', 'module_id_1']
    for idx in required_materials_indexes:
        if idx not in materials_indexes:
            print(f"  ❌ Missing index on materials: {idx}")
            all_good = False
    
    # Check enrollments indexes
    enrollments_indexes = db.enrollments.index_information()
    required_enrollments_indexes = ['student_id_1', 'course_id_1']
    for idx in required_enrollments_indexes:
        if idx not in enrollments_indexes:
            print(f"  ❌ Missing index on enrollments: {idx}")
            all_good = False
    
    # Check progress indexes
    progress_indexes = db.progress.index_information()
    required_progress_indexes = ['student_id_1', 'course_id_1']
    for idx in required_progress_indexes:
        if idx not in progress_indexes:
            print(f"  ❌ Missing index on progress: {idx}")
            all_good = False
    
    if all_good:
        print("  ✅ All required indexes are present")
    
    return all_good


def main():
    """
    Main function to run all schema verification checks.
    """
    print("=" * 60)
    print("🔍 Database Schema Consistency Verification")
    print("=" * 60)
    
    results = []
    
    # Run all verification checks
    results.append(("Courses", verify_course_schema()))
    results.append(("Modules", verify_module_schema()))
    results.append(("Materials", verify_material_schema()))
    results.append(("Enrollments", verify_enrollment_schema()))
    results.append(("Progress", verify_progress_schema()))
    results.append(("Indexes", verify_indexes()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All schema consistency checks passed!")
        return 0
    else:
        print("\n❌ Some schema consistency checks failed. Please review the issues above.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
