"""
Script to create missing database indexes.

This script creates the indexes that were added to db_init.py but haven't been
applied to the existing database yet.

Usage:
    python backend/scripts/create_missing_indexes.py
"""

import sys
import os
from pymongo import MongoClient

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


def create_indexes():
    """Create all database indexes"""
    
    print("🔧 Creating database indexes...")
    
    # Modules collection indexes (Requirement 7.2)
    print("  Creating modules indexes...")
    db.modules.create_index("course_id")
    db.modules.create_index([("course_id", 1), ("order", 1)])
    
    # Materials collection indexes (Requirement 7.3)
    print("  Creating materials indexes...")
    db.materials.create_index("course_id")
    db.materials.create_index("module_id")
    db.materials.create_index([("module_id", 1), ("order", 1)])
    db.materials.create_index("type")
    
    print("✅ Database indexes created successfully!")


def main():
    """Main function"""
    print("=" * 60)
    print("🔍 Creating Missing Database Indexes")
    print("=" * 60)
    
    try:
        create_indexes()
        print("\n✅ All indexes created successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Error creating indexes: {e}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
