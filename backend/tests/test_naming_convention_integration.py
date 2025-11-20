"""
Integration tests for API naming convention
Tests that actual API endpoints return camelCase responses
"""
import pytest
from utils.case_converter import convert_dict_keys_to_camel, is_camel_case


def test_case_converter_integration():
    """Test that the case converter works with realistic data"""
    # Simulate a database record
    db_record = {
        '_id': '507f1f77bcf86cd799439011',
        'course_id': 'c123',
        'teacher_id': 't456',
        'student_id': 's789',
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-02T00:00:00Z',
        'enrolled_at': '2024-01-03T00:00:00Z',
        'last_accessed': '2024-01-04T00:00:00Z',
        'is_active': True,
        'max_students': 30,
        'enrolled_students': 15
    }
    
    # Convert to API format
    api_response = convert_dict_keys_to_camel(db_record)
    
    # Verify all keys are camelCase
    expected_keys = {
        'id', 'courseId', 'teacherId', 'studentId', 'createdAt',
        'updatedAt', 'enrolledAt', 'lastAccessed', 'isActive',
        'maxStudents', 'enrolledStudents'
    }
    
    assert set(api_response.keys()) == expected_keys
    
    # Verify values are preserved
    assert api_response['id'] == '507f1f77bcf86cd799439011'
    assert api_response['courseId'] == 'c123'
    assert api_response['teacherId'] == 't456'
    assert api_response['studentId'] == 's789'
    assert api_response['isActive'] == True
    assert api_response['maxStudents'] == 30


def test_nested_structure_conversion():
    """Test conversion of nested structures like course with modules"""
    db_course = {
        '_id': 'course123',
        'course_id': 'course123',
        'title': 'Python Programming',
        'teacher_id': 'teacher456',
        'created_at': '2024-01-01',
        'modules': [
            {
                '_id': 'module1',
                'module_id': 'module1',
                'title': 'Introduction',
                'order': 1,
                'created_at': '2024-01-01',
                'materials': [
                    {
                        '_id': 'material1',
                        'material_id': 'material1',
                        'title': 'Video 1',
                        'type': 'video',
                        'video_id': 'video123',
                        'created_at': '2024-01-01'
                    }
                ]
            }
        ]
    }
    
    # Convert to API format
    api_course = convert_dict_keys_to_camel(db_course)
    
    # Verify top-level keys
    assert 'id' in api_course
    assert 'courseId' in api_course
    assert 'teacherId' in api_course
    assert 'createdAt' in api_course
    assert 'modules' in api_course
    
    # Verify nested module keys
    module = api_course['modules'][0]
    assert 'id' in module
    assert 'moduleId' in module
    assert 'createdAt' in module
    assert 'materials' in module
    
    # Verify nested material keys
    material = module['materials'][0]
    assert 'id' in material
    assert 'materialId' in material
    assert 'videoId' in material
    assert 'createdAt' in material
    
    # Verify no snake_case keys remain
    def check_no_snake_case(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key != 'id':  # 'id' is allowed
                    assert '_' not in key, f"Found snake_case key: {key}"
                check_no_snake_case(value)
        elif isinstance(obj, list):
            for item in obj:
                check_no_snake_case(item)
    
    check_no_snake_case(api_course)


def test_array_of_objects_conversion():
    """Test conversion of arrays of objects"""
    db_enrollments = [
        {
            '_id': 'enroll1',
            'student_id': 'student1',
            'course_id': 'course1',
            'enrolled_at': '2024-01-01',
            'progress': 50
        },
        {
            '_id': 'enroll2',
            'student_id': 'student2',
            'course_id': 'course1',
            'enrolled_at': '2024-01-02',
            'progress': 75
        }
    ]
    
    # Convert to API format
    api_enrollments = convert_dict_keys_to_camel(db_enrollments)
    
    # Verify all items are converted
    assert len(api_enrollments) == 2
    
    for enrollment in api_enrollments:
        assert 'id' in enrollment
        assert 'studentId' in enrollment
        assert 'courseId' in enrollment
        assert 'enrolledAt' in enrollment
        assert 'progress' in enrollment
        
        # Verify no snake_case keys
        for key in enrollment.keys():
            if key != 'id':
                assert '_' not in key


def test_special_mongodb_id_handling():
    """Test that _id is converted to id"""
    db_doc = {'_id': '123', 'user_id': '456'}
    api_doc = convert_dict_keys_to_camel(db_doc)
    
    assert 'id' in api_doc
    assert '_id' not in api_doc
    assert api_doc['id'] == '123'
    assert api_doc['userId'] == '456'


def test_mixed_case_preservation():
    """Test that values are not modified, only keys"""
    db_doc = {
        'user_name': 'John_Doe',
        'email_address': 'john_doe@example.com',
        'description': 'This is a test_description with_underscores'
    }
    
    api_doc = convert_dict_keys_to_camel(db_doc)
    
    # Keys should be camelCase
    assert 'userName' in api_doc
    assert 'emailAddress' in api_doc
    assert 'description' in api_doc
    
    # Values should be unchanged
    assert api_doc['userName'] == 'John_Doe'
    assert api_doc['emailAddress'] == 'john_doe@example.com'
    assert api_doc['description'] == 'This is a test_description with_underscores'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
