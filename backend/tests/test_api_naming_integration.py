"""
Integration test to verify API endpoints return camelCase responses
**Feature: course-media-and-access-fixes, Property 40: API field naming convention**
**Validates: Requirements 7.6**
"""
import pytest
from utils.api_response import prepare_api_response, error_response, success_response
from utils.case_converter import convert_dict_keys_to_camel


def test_prepare_api_response_converts_to_camel_case(app):
    """Test that prepare_api_response converts snake_case to camelCase"""
    with app.app_context():
        # Database record with snake_case
        db_data = {
            'course_id': 'c123',
            'student_id': 's456',
            'created_at': '2024-01-01',
            'last_accessed': '2024-01-02'
        }
        
        response, status_code = prepare_api_response(db_data, status_code=200)
        response_data = response.get_json()
    
        # Verify camelCase keys
        assert 'courseId' in response_data
        assert 'studentId' in response_data
        assert 'createdAt' in response_data
        assert 'lastAccessed' in response_data
        
        # Verify no snake_case keys
        assert 'course_id' not in response_data
        assert 'student_id' not in response_data
        assert 'created_at' not in response_data
        assert 'last_accessed' not in response_data
        
        assert status_code == 200


def test_error_response_converts_kwargs_to_camel_case(app):
    """Test that error_response converts kwargs to camelCase"""
    with app.app_context():
        response, status_code = error_response(
            'Not found',
            404,
            course_id='c123',
            student_id='s456'
        )
        response_data = response.get_json()
        
        assert 'error' in response_data
        assert response_data['error'] == 'Not found'
        assert 'courseId' in response_data
        assert 'studentId' in response_data
        assert 'course_id' not in response_data
        assert 'student_id' not in response_data
        assert status_code == 404


def test_success_response_converts_data_to_camel_case(app):
    """Test that success_response converts data to camelCase"""
    with app.app_context():
        data = {
            'video_id': 'v123',
            'file_size': 1024,
            'mime_type': 'video/mp4'
        }
        
        response, status_code = success_response('Success', data, 201)
        response_data = response.get_json()
        
        assert 'message' in response_data
        assert response_data['message'] == 'Success'
        assert 'videoId' in response_data
        assert 'fileSize' in response_data
        assert 'mimeType' in response_data
        assert 'video_id' not in response_data
        assert 'file_size' not in response_data
        assert 'mime_type' not in response_data
        assert status_code == 201


def test_nested_dict_conversion(app):
    """Test that nested dictionaries are converted to camelCase"""
    with app.app_context():
        data = {
            'course_id': 'c123',
            'student_info': {
                'student_id': 's456',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            'progress_data': [
                {'material_id': 'm1', 'completed_at': '2024-01-01'},
                {'material_id': 'm2', 'completed_at': '2024-01-02'}
            ]
        }
        
        response, status_code = prepare_api_response(data, status_code=200)
        response_data = response.get_json()
        
        # Check top-level conversion
        assert 'courseId' in response_data
        assert 'studentInfo' in response_data
        assert 'progressData' in response_data
        
        # Check nested object conversion
        assert 'studentId' in response_data['studentInfo']
        assert 'firstName' in response_data['studentInfo']
        assert 'lastName' in response_data['studentInfo']
        
        # Check nested array conversion
        assert 'materialId' in response_data['progressData'][0]
        assert 'completedAt' in response_data['progressData'][0]
        assert 'materialId' in response_data['progressData'][1]
        assert 'completedAt' in response_data['progressData'][1]


def test_mongodb_id_field_conversion(app):
    """Test that MongoDB _id field is converted to id"""
    with app.app_context():
        data = {
            '_id': '507f1f77bcf86cd799439011',
            'course_id': 'c123',
            'title': 'Test Course'
        }
        
        response, status_code = prepare_api_response(data, status_code=200)
        response_data = response.get_json()
        
        # _id should become id
        assert 'id' in response_data
        assert response_data['id'] == '507f1f77bcf86cd799439011'
        assert '_id' not in response_data
        
        # Other fields should be camelCase
        assert 'courseId' in response_data
        assert 'title' in response_data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
