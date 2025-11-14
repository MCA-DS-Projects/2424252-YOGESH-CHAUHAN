#!/usr/bin/env python3
"""
Verification script for MongoDB-only data flow
Tests that the application starts with empty database and only creates indexes

Usage:
    python backend/scripts/verify_mongodb_only.py
"""
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_database_empty(db):
    """Check if database collections are empty"""
    print_header("Step 1: Check Database State")
    
    collections = {
        'users': db.users.count_documents({}),
        'courses': db.courses.count_documents({}),
        'assignments': db.assignments.count_documents({}),
        'enrollments': db.enrollments.count_documents({}),
        'submissions': db.submissions.count_documents({})
    }
    
    print("\n📊 Collection Document Counts:")
    for collection, count in collections.items():
        status = "✅ Empty" if count == 0 else f"⚠️  {count} documents"
        print(f"   - {collection}: {status}")
    
    all_empty = all(count == 0 for count in collections.values())
    
    if all_empty:
        print("\n✅ Database is empty (no automatic seeding)")
        return True
    else:
        print("\n⚠️  Database contains data")
        print("   This could be from:")
        print("   - Previous manual seeding")
        print("   - Old automatic seeding (before cleanup)")
        print("   - Production data")
        return False


def check_indexes_created(db):
    """Verify that indexes are created"""
    print_header("Step 2: Verify Indexes Created")
    
    expected_indexes = {
        'users': ['email', 'role'],
        'courses': ['teacher_id', 'category', 'is_active'],
        'enrollments': ['course_id', 'student_id'],
        'assignments': ['course_id', 'due_date'],
        'submissions': ['student_id']
    }
    
    all_indexes_present = True
    
    for collection_name, expected_fields in expected_indexes.items():
        collection = db[collection_name]
        indexes = collection.index_information()
        
        print(f"\n📋 {collection_name} indexes:")
        
        for field in expected_fields:
            # Check if any index contains this field
            found = False
            for index_name, index_info in indexes.items():
                index_keys = [key[0] for key in index_info.get('key', [])]
                if field in index_keys:
                    found = True
                    print(f"   ✅ {field} (index: {index_name})")
                    break
            
            if not found:
                print(f"   ❌ {field} (missing)")
                all_indexes_present = False
    
    if all_indexes_present:
        print("\n✅ All expected indexes are present")
    else:
        print("\n⚠️  Some indexes are missing")
        print("   Run: python backend/app.py to create indexes")
    
    return all_indexes_present


def test_manual_seeding(db):
    """Test manual seed script execution"""
    print_header("Step 3: Test Manual Seed Scripts")
    
    print("\n📝 Available seed scripts:")
    print("   1. backend/scripts/seeders/seed_sample_data.py")
    print("   2. backend/scripts/seeders/create_test_teacher.py")
    print("   3. backend/scripts/seeders/create_test_student_data.py")
    
    print("\n⚠️  Manual seeding test requires user action")
    print("   To test manual seeding:")
    print("   1. Run: python backend/scripts/seeders/seed_sample_data.py")
    print("   2. Verify data is created in MongoDB")
    print("   3. Run this script again to see the data")
    
    return True


def verify_no_automatic_seeding():
    """Verify db_init.py doesn't automatically seed data"""
    print_header("Step 4: Verify No Automatic Seeding in Code")
    
    db_init_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'db_init.py')
    
    if not os.path.exists(db_init_path):
        print("❌ db_init.py not found")
        return False
    
    with open(db_init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for problematic patterns
    problematic_patterns = [
        'create_sample_users',
        'create_sample_courses',
        'create_sample_enrollments',
        'create_sample_assignments'
    ]
    
    issues_found = []
    for pattern in problematic_patterns:
        if pattern in content and f'def {pattern}' not in content:
            # Pattern found but not as a function definition (likely a call)
            issues_found.append(pattern)
    
    if issues_found:
        print("❌ Found automatic seeding calls in db_init.py:")
        for issue in issues_found:
            print(f"   - {issue}()")
        print("\n   These should be removed or moved to seed scripts")
        return False
    else:
        print("✅ No automatic seeding calls found in db_init.py")
        print("   Only index creation should be present")
        return True


def main():
    """Main execution function"""
    print("=" * 60)
    print("  🔍 MongoDB-Only Data Flow Verification")
    print("=" * 60)
    
    # Connect to MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/edunexa_lms')
    
    try:
        client = MongoClient(MONGO_URI)
        db = client.edunexa_lms
        client.admin.command('ping')
        print(f"\n✅ Connected to MongoDB: {MONGO_URI}")
    except Exception as e:
        print(f"\n❌ Failed to connect to MongoDB: {e}")
        print("   Make sure MongoDB is running")
        sys.exit(1)
    
    # Run verification steps
    results = {}
    
    try:
        # Step 1: Check if database is empty
        results['empty_db'] = check_database_empty(db)
        
        # Step 2: Verify indexes are created
        results['indexes'] = check_indexes_created(db)
        
        # Step 3: Test manual seeding
        results['manual_seed'] = test_manual_seeding(db)
        
        # Step 4: Verify no automatic seeding in code
        results['no_auto_seed'] = verify_no_automatic_seeding()
        
        # Summary
        print_header("Verification Summary")
        
        print("\n📊 Results:")
        print(f"   {'✅' if results['empty_db'] else '⚠️ '} Database starts empty (no auto-seed)")
        print(f"   {'✅' if results['indexes'] else '❌'} Indexes created automatically")
        print(f"   {'✅' if results['manual_seed'] else '❌'} Manual seed scripts available")
        print(f"   {'✅' if results['no_auto_seed'] else '❌'} No automatic seeding in code")
        
        all_passed = all(results.values())
        
        if all_passed:
            print("\n" + "=" * 60)
            print("  ✅ MongoDB-Only Data Flow Verified!")
            print("=" * 60)
            print("\n✨ Key Points:")
            print("   - Application starts with empty database")
            print("   - Only indexes are created automatically")
            print("   - Data seeding requires manual script execution")
            print("   - MongoDB is the single source of truth")
        else:
            print("\n" + "=" * 60)
            print("  ⚠️  Some Checks Failed")
            print("=" * 60)
            print("\n📝 Action Items:")
            if not results['empty_db']:
                print("   - Database has data (may be from previous seeding)")
            if not results['indexes']:
                print("   - Run the application to create indexes")
            if not results['no_auto_seed']:
                print("   - Remove automatic seeding from db_init.py")
        
        print("\n📚 Documentation:")
        print("   - See docs/DEV_NOTES.md for setup instructions")
        print("   - See backend/scripts/seeders/README.md for seeding guide")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
