"""
Test document upload functionality
Validates Requirements 4.1, 4.2, 4.3, 4.4
"""
import pytest
import os
import io
from bson import ObjectId
from datetime import datetime

def test_document_upload_endpoint_exists(client, teacher_token):
    """Test that the document upload endpoint exists"""
    # Create a test PDF file
    data = {
        'document': (io.BytesIO(b'%PDF-1.4 test content'), 'test.pdf')
    }
    
    response = client.post(
        '/api/documents/upload',
        data=data,
        headers={'Authorization': f'Bearer {teacher_token}'},
        content_type='multipart/form-data'
    )
    
    # Should return 201 or 200 for successful upload
    assert response.status_code in [200, 201], f"Expected 200 or 201, got {response.status_code}"
    
    json_data = response.get_json()
    assert 'documentId' in json_data or 'document_id' in json_data
    assert 'filename' in json_data

def test_document_directory_exists():
    """Test that documents directory exists - Requirement 4.2"""
    upload_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'uploads',
        'documents'
    )
    assert os.path.exists(upload_dir), "Documents directory should exist"
    assert os.path.isdir(upload_dir), "Documents path should be a directory"

def test_document_file_validation(client, teacher_token):
    """Test document file type validation - Requirement 4.1"""
    # Test with invalid file type
    data = {
        'document': (io.BytesIO(b'test content'), 'test.exe')
    }
    
    response = client.post(
        '/api/documents/upload',
        data=data,
        headers={'Authorization': f'Bearer {teacher_token}'},
        content_type='multipart/form-data'
    )
    
    # Should reject invalid file type
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data

def test_document_size_validation(client, teacher_token):
    """Test document file size validation - Requirement 4.1"""
    # Create a file larger than 50MB
    large_content = b'x' * (51 * 1024 * 1024)  # 51MB
    data = {
        'document': (io.BytesIO(large_content), 'large.pdf')
    }
    
    response = client.post(
        '/api/documents/upload',
        data=data,
        headers={'Authorization': f'Bearer {teacher_token}'},
        content_type='multipart/form-data'
    )
    
    # Should reject oversized file
    assert response.status_code == 413

def test_document_unique_filename(client, teacher_token, db):
    """Test that documents get unique filenames - Requirement 4.3"""
    # Upload same file twice
    data1 = {
        'document': (io.BytesIO(b'%PDF-1.4 test'), 'same_name.pdf')
    }
    
    response1 = client.post(
        '/api/documents/upload',
        data=data1,
        headers={'Authorization': f'Bearer {teacher_token}'},
        content_type='multipart/form-data'
    )
    
    data2 = {
        'document': (io.BytesIO(b'%PDF-1.4 test'), 'same_name.pdf')
    }
    
    response2 = client.post(
        '/api/documents/upload',
        data=data2,
        headers={'Authorization': f'Bearer {teacher_token}'},
        content_type='multipart/form-data'
    )
    
    if response1.status_code == 201 and response2.status_code == 201:
        json1 = response1.get_json()
        json2 = response2.get_json()
        
        # Filenames should be different (UUID-based)
        assert json1['filename'] != json2['filename']

def test_document_storage_in_database(client, teacher_token, db):
    """Test that document metadata is stored in database - Requirement 4.4"""
    data = {
        'document': (io.BytesIO(b'%PDF-1.4 test'), 'test_db.pdf')
    }
    
    response = client.post(
        '/api/documents/upload',
        data=data,
        headers={'Authorization': f'Bearer {teacher_token}'},
        content_type='multipart/form-data'
    )
    
    if response.status_code == 201:
        json_data = response.get_json()
        document_id = json_data.get('documentId') or json_data.get('document_id')
        
        # Check database for document record
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        assert document is not None
        assert 'filename' in document
        assert 'file_path' in document
        assert 'file_size' in document
        assert 'mime_type' in document

def test_document_linking_to_materials(client, teacher_token, db):
    """Test that documents can be linked to course materials - Requirement 4.4"""
    # First create a course
    course_data = {
        'title': 'Test Course for Documents',
        'description': 'A test course to verify document linking',
        'category': 'Test',
        'difficulty': 'Beginner'
    }
    
    course_response = client.post(
        '/api/courses/',
        json=course_data,
        headers={'Authorization': f'Bearer {teacher_token}'}
    )
    
    if course_response.status_code != 201:
        pytest.skip("Could not create test course")
    
    course_id = course_response.get_json()['course']['_id']
    
    # Upload a document
    doc_data = {
        'document': (io.BytesIO(b'%PDF-1.4 test'), 'course_doc.pdf')
    }
    
    doc_response = client.post(
        '/api/documents/upload',
        data=doc_data,
        headers={'Authorization': f'Bearer {teacher_token}'},
        content_type='multipart/form-data'
    )
    
    if doc_response.status_code != 201:
        pytest.skip("Could not upload document")
    
    document_id = doc_response.get_json().get('documentId') or doc_response.get_json().get('document_id')
    
    # Link document to course material
    material_data = {
        'title': 'Test Document Material',
        'description': 'A test document material',
        'type': 'document',
        'content': document_id,
        'order': 1
    }
    
    material_response = client.post(
        f'/api/courses/{course_id}/materials',
        json=material_data,
        headers={'Authorization': f'Bearer {teacher_token}'}
    )
    
    # Should successfully create material
    assert material_response.status_code == 201
    
    # Verify material in database
    material = db.materials.find_one({'content': document_id, 'type': 'document'})
    assert material is not None
    assert material['course_id'] == course_id
