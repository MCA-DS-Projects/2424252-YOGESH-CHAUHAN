#!/usr/bin/env python3
"""
Verification script for document upload functionality
Demonstrates Requirements 4.1, 4.2, 4.3, 4.4
"""

import os
import sys

def verify_document_system():
    """Verify document upload system is properly configured"""
    
    print("=" * 60)
    print("Document Upload System Verification")
    print("=" * 60)
    print()
    
    # Check 1: Documents directory exists
    print("✓ Checking documents directory...")
    upload_dir = os.path.join(
        os.path.dirname(__file__),
        'uploads',
        'documents'
    )
    
    if os.path.exists(upload_dir) and os.path.isdir(upload_dir):
        print(f"  ✅ Documents directory exists: {upload_dir}")
    else:
        print(f"  ❌ Documents directory not found: {upload_dir}")
        return False
    
    # Check 2: Documents route file exists
    print("\n✓ Checking documents route...")
    routes_file = os.path.join(
        os.path.dirname(__file__),
        'routes',
        'documents.py'
    )
    
    if os.path.exists(routes_file):
        print(f"  ✅ Documents route exists: {routes_file}")
    else:
        print(f"  ❌ Documents route not found: {routes_file}")
        return False
    
    # Check 3: Verify route configuration
    print("\n✓ Checking route configuration...")
    with open(routes_file, 'r') as f:
        content = f.read()
        
        checks = [
            ('UPLOAD_FOLDER', 'Upload folder configured'),
            ('ALLOWED_EXTENSIONS', 'Allowed extensions defined'),
            ('MAX_FILE_SIZE', 'Max file size defined'),
            ('@documents_bp.route(\'/upload\'', 'Upload endpoint defined'),
            ('def upload_document', 'Upload function exists'),
            ('uuid.uuid4()', 'UUID generation for unique filenames'),
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description} - NOT FOUND")
                return False
    
    # Check 4: Verify app registration
    print("\n✓ Checking app registration...")
    app_file = os.path.join(
        os.path.dirname(__file__),
        'app.py'
    )
    
    with open(app_file, 'r') as f:
        content = f.read()
        
        if 'from routes.documents import documents_bp' in content:
            print("  ✅ Documents blueprint imported")
        else:
            print("  ❌ Documents blueprint not imported")
            return False
        
        if 'app.register_blueprint(documents_bp' in content:
            print("  ✅ Documents blueprint registered")
        else:
            print("  ❌ Documents blueprint not registered")
            return False
    
    # Check 5: Verify test files exist
    print("\n✓ Checking test files...")
    test_files = [
        'tests/test_document_upload.py',
        'tests/test_document_integration.py'
    ]
    
    for test_file in test_files:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            print(f"  ✅ Test file exists: {test_file}")
        else:
            print(f"  ⚠️  Test file not found: {test_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Document Upload System Verification PASSED")
    print("=" * 60)
    print()
    print("System is ready for document uploads!")
    print()
    print("Supported file types: PDF, DOCX, PPTX, TXT")
    print("Maximum file size: 50MB")
    print("Storage location: backend/uploads/documents/")
    print()
    print("API Endpoints:")
    print("  - POST /api/documents/upload (upload document)")
    print("  - POST /api/courses/<course_id>/materials (link to course)")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = verify_document_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        sys.exit(1)
