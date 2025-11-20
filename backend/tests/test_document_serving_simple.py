"""
Simple integration test for document serving endpoint.
"""

import pytest
from bson import ObjectId


def test_document_not_found(client, student_token):
    """Test accessing non-existent document returns 404"""
    
    fake_id = str(ObjectId())
    
    response = client.get(
        f'/api/documents/{fake_id}',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    assert response.status_code == 404
    result = response.get_json()
    assert 'error' in result
    assert result['error'] == 'Document not found'


def test_document_invalid_id(client, student_token):
    """Test accessing document with invalid ID returns 400"""
    
    response = client.get(
        '/api/documents/invalid-id',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    assert response.status_code == 400
    result = response.get_json()
    assert 'error' in result
    assert result['error'] == 'Invalid document ID'


def test_document_requires_authentication(client):
    """Test that document endpoint requires authentication"""
    
    fake_id = str(ObjectId())
    
    response = client.get(f'/api/documents/{fake_id}')
    
    # Should return 401 Unauthorized
    assert response.status_code == 401


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
