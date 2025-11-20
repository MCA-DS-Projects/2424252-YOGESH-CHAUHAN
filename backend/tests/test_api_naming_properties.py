"""
Property-based tests for API field naming conventions
**Feature: course-media-and-access-fixes, Property 40: API field naming convention**
**Validates: Requirements 7.6**

Tests that API responses use camelCase while database uses snake_case
"""
import pytest
from hypothesis import given, strategies as st, assume
from utils.case_converter import (
    snake_to_camel,
    camel_to_snake,
    convert_dict_keys_to_camel,
    convert_dict_keys_to_snake,
    is_camel_case,
    is_snake_case
)


# Strategy for generating valid snake_case identifiers
@st.composite
def snake_case_identifier(draw):
    """Generate valid snake_case identifiers"""
    # Start with a lowercase letter
    first_char = draw(st.sampled_from('abcdefghijklmnopqrstuvwxyz'))
    
    # Generate 0-3 additional segments
    num_segments = draw(st.integers(min_value=0, max_value=3))
    
    segments = [first_char]
    for _ in range(num_segments):
        # Add underscore and another word
        word_length = draw(st.integers(min_value=1, max_value=8))
        word = ''.join(draw(st.sampled_from('abcdefghijklmnopqrstuvwxyz')) 
                      for _ in range(word_length))
        segments.append('_')
        segments.append(word)
    
    return ''.join(segments)


# Strategy for generating valid camelCase identifiers
@st.composite
def camel_case_identifier(draw):
    """Generate valid camelCase identifiers"""
    # Start with a lowercase letter
    first_char = draw(st.sampled_from('abcdefghijklmnopqrstuvwxyz'))
    
    # Generate 0-3 additional segments (capitalized)
    num_segments = draw(st.integers(min_value=0, max_value=3))
    
    segments = [first_char]
    for _ in range(num_segments):
        # Add a capitalized word
        word_length = draw(st.integers(min_value=1, max_value=8))
        word = draw(st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        word += ''.join(draw(st.sampled_from('abcdefghijklmnopqrstuvwxyz')) 
                       for _ in range(word_length - 1))
        segments.append(word)
    
    return ''.join(segments)


class TestSnakeToCamelConversion:
    """Test snake_case to camelCase conversion"""
    
    @given(snake_case_identifier())
    def test_snake_to_camel_produces_camel_case(self, snake_str):
        """
        Property: For any snake_case string, converting to camelCase 
        should produce a valid camelCase string
        """
        camel_str = snake_to_camel(snake_str)
        assert is_camel_case(camel_str), f"Expected camelCase but got: {camel_str}"
    
    @given(snake_case_identifier())
    def test_snake_to_camel_no_underscores(self, snake_str):
        """
        Property: For any snake_case string, the camelCase version 
        should not contain underscores (except for _id special case)
        """
        camel_str = snake_to_camel(snake_str)
        if snake_str != '_id':
            assert '_' not in camel_str, f"camelCase should not have underscores: {camel_str}"
    
    def test_snake_to_camel_special_cases(self):
        """Test known special cases"""
        assert snake_to_camel('_id') == 'id'
        assert snake_to_camel('user_id') == 'userId'
        assert snake_to_camel('created_at') == 'createdAt'
        assert snake_to_camel('student_id') == 'studentId'
        assert snake_to_camel('course_id') == 'courseId'


class TestCamelToSnakeConversion:
    """Test camelCase to snake_case conversion"""
    
    @given(camel_case_identifier())
    def test_camel_to_snake_produces_snake_case(self, camel_str):
        """
        Property: For any camelCase string, converting to snake_case 
        should produce a valid snake_case string
        """
        snake_str = camel_to_snake(camel_str)
        assert is_snake_case(snake_str), f"Expected snake_case but got: {snake_str}"
    
    @given(camel_case_identifier())
    def test_camel_to_snake_lowercase(self, camel_str):
        """
        Property: For any camelCase string, the snake_case version 
        should be all lowercase
        """
        snake_str = camel_to_snake(camel_str)
        assert snake_str == snake_str.lower(), f"snake_case should be lowercase: {snake_str}"
    
    def test_camel_to_snake_special_cases(self):
        """Test known special cases"""
        assert camel_to_snake('id') == '_id'
        assert camel_to_snake('userId') == 'user_id'
        assert camel_to_snake('createdAt') == 'created_at'
        assert camel_to_snake('studentId') == 'student_id'
        assert camel_to_snake('courseId') == 'course_id'


class TestRoundTripConversion:
    """Test round-trip conversion properties"""
    
    @given(snake_case_identifier())
    def test_snake_to_camel_to_snake_round_trip(self, original_snake):
        """
        Property: For any snake_case string (except _id), converting to 
        camelCase and back should return the original string
        """
        # Skip _id as it's a special case
        assume(original_snake != '_id')
        
        camel_str = snake_to_camel(original_snake)
        back_to_snake = camel_to_snake(camel_str)
        
        assert back_to_snake == original_snake, \
            f"Round trip failed: {original_snake} -> {camel_str} -> {back_to_snake}"
    
    @given(camel_case_identifier())
    def test_camel_to_snake_to_camel_round_trip(self, original_camel):
        """
        Property: For any camelCase string (except 'id'), converting to 
        snake_case and back should return the original string
        """
        # Skip 'id' as it's a special case
        assume(original_camel != 'id')
        
        snake_str = camel_to_snake(original_camel)
        back_to_camel = snake_to_camel(snake_str)
        
        assert back_to_camel == original_camel, \
            f"Round trip failed: {original_camel} -> {snake_str} -> {back_to_camel}"


class TestDictConversion:
    """Test dictionary key conversion"""
    
    @given(st.dictionaries(
        keys=snake_case_identifier(),
        values=st.one_of(st.text(), st.integers(), st.booleans(), st.none())
    ))
    def test_dict_snake_to_camel_all_keys_camel(self, snake_dict):
        """
        Property: For any dictionary with snake_case keys, converting to 
        camelCase should result in all keys being camelCase
        """
        camel_dict = convert_dict_keys_to_camel(snake_dict)
        
        for key in camel_dict.keys():
            assert is_camel_case(key), f"Key should be camelCase: {key}"
    
    @given(st.dictionaries(
        keys=camel_case_identifier(),
        values=st.one_of(st.text(), st.integers(), st.booleans(), st.none())
    ))
    def test_dict_camel_to_snake_all_keys_snake(self, camel_dict):
        """
        Property: For any dictionary with camelCase keys, converting to 
        snake_case should result in all keys being snake_case
        """
        snake_dict = convert_dict_keys_to_snake(camel_dict)
        
        for key in snake_dict.keys():
            assert is_snake_case(key), f"Key should be snake_case: {key}"
    
    @given(st.dictionaries(
        keys=snake_case_identifier(),
        values=st.one_of(st.text(), st.integers(), st.booleans())
    ))
    def test_dict_conversion_preserves_values(self, snake_dict):
        """
        Property: For any dictionary, converting keys should not change values
        """
        camel_dict = convert_dict_keys_to_camel(snake_dict)
        
        # Check that all values are preserved (though keys are different)
        snake_values = set(str(v) for v in snake_dict.values())
        camel_values = set(str(v) for v in camel_dict.values())
        
        assert snake_values == camel_values, "Values should be preserved during conversion"
    
    def test_nested_dict_conversion(self):
        """Test nested dictionary conversion"""
        snake_dict = {
            'user_id': '123',
            'created_at': '2024-01-01',
            'profile': {
                'first_name': 'John',
                'last_name': 'Doe',
                'email_address': 'john@example.com'
            },
            'enrolled_courses': [
                {'course_id': 'c1', 'progress_percent': 50},
                {'course_id': 'c2', 'progress_percent': 75}
            ]
        }
        
        camel_dict = convert_dict_keys_to_camel(snake_dict)
        
        # Check top-level keys
        assert 'userId' in camel_dict
        assert 'createdAt' in camel_dict
        assert 'profile' in camel_dict
        assert 'enrolledCourses' in camel_dict
        
        # Check nested object keys
        assert 'firstName' in camel_dict['profile']
        assert 'lastName' in camel_dict['profile']
        assert 'emailAddress' in camel_dict['profile']
        
        # Check nested array object keys
        assert 'courseId' in camel_dict['enrolledCourses'][0]
        assert 'progressPercent' in camel_dict['enrolledCourses'][0]


class TestAPIResponseConvention:
    """
    Test that API responses follow camelCase convention
    **Property 40: API field naming convention**
    **Validates: Requirements 7.6**
    """
    
    @given(st.dictionaries(
        keys=snake_case_identifier(),
        values=st.one_of(
            st.text(),
            st.integers(),
            st.booleans(),
            st.none(),
            st.lists(st.text())
        ),
        min_size=1,
        max_size=10
    ))
    def test_api_response_uses_camel_case(self, db_record):
        """
        Property: For any database record with snake_case fields, 
        the API response should use camelCase fields
        
        This is the core property for Requirement 7.6:
        - Database uses snake_case (course_id, student_id, created_at)
        - API responses use camelCase (courseId, studentId, createdAt)
        """
        # Simulate database record (snake_case)
        # Simulate API transformation
        api_response = convert_dict_keys_to_camel(db_record)
        
        # Verify all keys in API response are camelCase
        for key in api_response.keys():
            assert is_camel_case(key), \
                f"API response key '{key}' should be camelCase (from db key in snake_case)"
        
        # Verify no snake_case keys remain
        for key in api_response.keys():
            assert '_' not in key or key == 'id', \
                f"API response should not contain underscores: {key}"
    
    def test_common_api_fields_are_camel_case(self):
        """
        Test that common API fields follow camelCase convention
        """
        # Simulate a typical database record
        db_course = {
            '_id': '507f1f77bcf86cd799439011',
            'course_id': 'c123',
            'title': 'Python Programming',
            'teacher_id': 't456',
            'student_id': 's789',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z',
            'enrolled_at': '2024-01-03T00:00:00Z',
            'last_accessed': '2024-01-04T00:00:00Z'
        }
        
        # Convert to API response format
        api_response = convert_dict_keys_to_camel(db_course)
        
        # Verify expected camelCase fields
        assert 'id' in api_response  # _id -> id
        assert 'courseId' in api_response
        assert 'title' in api_response  # No change for single word
        assert 'teacherId' in api_response
        assert 'studentId' in api_response
        assert 'createdAt' in api_response
        assert 'updatedAt' in api_response
        assert 'enrolledAt' in api_response
        assert 'lastAccessed' in api_response
        
        # Verify no snake_case fields remain
        assert 'course_id' not in api_response
        assert 'teacher_id' not in api_response
        assert 'student_id' not in api_response
        assert 'created_at' not in api_response
        assert 'updated_at' not in api_response
        assert 'enrolled_at' not in api_response
        assert 'last_accessed' not in api_response
        assert '_id' not in api_response


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
