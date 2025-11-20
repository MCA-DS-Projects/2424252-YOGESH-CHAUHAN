"""
Integration tests for document upload and serving functionality.
"""

import pytest
import os
import tempfile
from io import BytesIO
from bson import ObjectId
from datetime import datetime


def test_document_upload_and_serve(client, teacher_token, student_token, db):
    """Test complete document upload and serving workflow"""
    
    # 1. Teacher uploads a document
    data = {
        'document': (BytesIO(b'Test document content'), 'test.pdf')
    }
    
    response = client.post(
        '/api/documents/upload',
        data=data,
        headers={'Authorization': f'Bearer {teacher_token}'},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    result = response.get_json()
    assert 'documentId' in result
    document_id = result['documentId']
    
    # 2. Create a test course
    course_data = {
        'title': 'Test Course',
        'description': 'Test Description',
        'category': 'Technology'
    }
    
    course_response = client.post(
        '/api/courses/',
        json=course_data,
        headers={'Authorization': f'Bearer {teacher_token}'}
    )
    
    assert course_response.status_code == 201
    course_id = course_response.get_json()['course']['_id']
    
    # 3. Link document to course material
    material_data = {
        'course_id': course_id,
        'type': 'document',
        'content': document_id,
        'title': 'Test Document',
        'description': 'Test document material'
    }
    
    db.materials.insert_one(material_data)
    
    # 4. Student enrolls in course
    enroll_response = client.post(
        f'/api/courses/{course_id}/enroll',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    assert enroll_response.status_code == 200
    
    # 5. Student downloads document
    download_response = client.get(
        f'/api/documents/{document_id}',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    assert download_response.status_code == 200
    assert download_response.data == b'Test document content'
    assert 'Content-Type' in download_response.headers
    assert 'Content-Disposition' in download_response.headers


def test_document_access_without_enrollment(client, teacher_token, student_token, db):
    """Test that students cannot access documents without enrollment"""
    
    # 1. Teacher uploads a document
    data = {
        'document': (BytesIO(b'Test document content'), 'test.pdf')
    }
    
    response = client.post(
        '/api/documents/upload',
        data=data,
        headers={'Authorization': f'Bearer {teacher_token}'},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    document_id = response.get_json()['documentId']
    
    # 2. Create a test course
    course_data = {
        'title': 'Test Course',
        'description': 'Test Description',
        'category': 'Technology'
    }
    
    course_response = client.post(
        '/api/courses/',
        json=course_data,
        headers={'Authorization': f'Bearer {teacher_token}'}
    )
    
    course_id = course_response.get_json()['course']['_id']
    
    # 3. Link document to course material
    material_data = {
        'course_id': course_id,
        'type': 'document',
        'content': document_id,
        'title': 'Test Document'
    }
    
    db.materials.insert_one(material_data)
    
    # 4. Student tries to download without enrollment
    download_response = client.get(
        f'/api/documents/{document_id}',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    # Should be denied
    assert download_response.status_code == 403


def test_document_not_found(client, student_token):
    """Test accessing non-existent document"""
    
    fake_id = str(ObjectId())
    
    response = client.get(
        f'/api/documents/{fake_id}',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    assert response.status_code == 404


def test_document_invalid_id(client, student_token):
    """Test accessing document with invalid ID"""
    
    response = client.get(
        '/api/documents/invalid-id',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
