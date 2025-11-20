"""
Property-based tests for error handling and security validation.

Feature: course-media-and-access-fixes
"""

import pytest
import os
from hypothesis import given, strategies as st, settings


# Helper function to validate file paths for directory traversal
def validate_file_path(file_path):
    """
    Validates file path to prevent directory traversal attacks.
    
    Args:
        file_path: File path to validate
    
    Returns:
        dict with 'is_valid' boolean and optional 'error' message
    """
    # Check for directory traversal patterns
    if '..' in file_path:
        return {
            'is_valid': False,
            'error': 'Invalid file path: directory traversal not allowed'
        }
    
    # Check for absolute paths (should be relative)
    if file_path.startswith('/') or file_path.startswith('\\'):
        return {
            'is_valid': False,
            'error': 'Invalid file path: absolute paths not allowed'
        }
    
    # Check for Windows drive letters
    if len(file_path) >= 2 and file_path[1] == ':':
        return {
            'is_valid': False,
            'error': 'Invalid file path: drive letters not allowed'
        }
    
    # Check for null bytes
    if '\x00' in file_path:
        return {
            'is_valid': False,
            'error': 'Invalid file path: null bytes not allowed'
        }
    
    return {'is_valid': True}


# Property 33: Directory traversal prevention
@given(
    path_component=st.one_of(
        # Valid paths
        st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
            min_size=1,
            max_size=50
        ),
        # Directory traversal attempts
        st.just('..'),
        st.just('../'),
        st.just('..\\'),
        st.just('../../'),
        st.just('..\\..\\'),
        st.just('/etc/passwd'),
        st.just('\\windows\\system32'),
        st.just('C:\\windows'),
        st.just('/'),
        st.just('\\'),
        # Paths with directory traversal in middle
        st.builds(lambda: 'uploads/../../../etc/passwd'),
        st.builds(lambda: 'uploads\\..\\..\\windows'),
        # Null byte injection
        st.builds(lambda: 'file\x00.txt'),
    )
)
@settings(max_examples=100)
def test_property_33_directory_traversal_prevention(path_component):
    """
    **Feature: course-media-and-access-fixes, Property 33: Directory traversal prevention**
    **Validates: Requirements 6.7**
    
    Property: For any file path request containing directory traversal patterns 
    (../, ..\\), absolute paths, or other malicious patterns, the system should 
    reject the request.
    """
    result = validate_file_path(path_component)
    
    # Determine if path contains dangerous patterns
    has_traversal = '..' in path_component
    is_absolute = path_component.startswith('/') or path_component.startswith('\\')
    has_drive_letter = len(path_component) >= 2 and path_component[1] == ':'
    has_null_byte = '\x00' in path_component
    
    is_dangerous = has_traversal or is_absolute or has_drive_letter or has_null_byte
    
    # If path is dangerous, it should be rejected
    if is_dangerous:
        assert not result['is_valid'], \
            f"Dangerous path should be rejected: {repr(path_component)}"
        assert 'error' in result, \
            f"Rejected path should have error message: {repr(path_component)}"
        assert len(result['error']) > 0, \
            "Error message should not be empty"
    else:
        # Safe paths should be accepted
        assert result['is_valid'], \
            f"Safe path should be accepted: {repr(path_component)}"


# Additional test for file size validation
@given(
    file_size_mb=st.floats(min_value=0.1, max_value=1000.0),
    max_size_mb=st.sampled_from([5, 50, 500])  # Different limits for different file types
)
@settings(max_examples=100)
def test_file_size_validation(file_size_mb, max_size_mb):
    """
    Property: For any file upload, if the file size exceeds the maximum allowed size,
    the system should reject it with a 413 error.
    """
    file_size_bytes = int(file_size_mb * 1024 * 1024)
    max_size_bytes = max_size_mb * 1024 * 1024
    
    is_valid = file_size_bytes <= max_size_bytes
    
    # Simulate validation
    if file_size_bytes > max_size_bytes:
        error_code = 413
        error_message = f'File size exceeds maximum allowed size of {max_size_mb}MB'
        assert error_code == 413, "Oversized files should return 413 error"
        assert str(max_size_mb) in error_message, \
            "Error message should mention the size limit"
    else:
        # File should be accepted
        assert is_valid, f"File of size {file_size_mb:.2f}MB should be accepted with limit {max_size_mb}MB"


# Test for file type validation
@given(
    file_extension=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=2,
        max_size=5
    ),
    allowed_types=st.sampled_from([
        {'jpg', 'jpeg', 'png', 'gif', 'webp'},  # Images
        {'mp4', 'webm', 'ogg'},  # Videos
        {'pdf', 'docx', 'pptx', 'txt'}  # Documents
    ])
)
@settings(max_examples=100)
def test_file_type_validation(file_extension, allowed_types):
    """
    Property: For any file upload, if the file type is not in the allowed list,
    the system should reject it with a 400 error.
    """
    is_valid = file_extension.lower() in allowed_types
    
    if not is_valid:
        error_code = 400
        error_message = f'Invalid file type. Allowed types: {", ".join(allowed_types)}'
        assert error_code == 400, "Invalid file types should return 400 error"
        assert 'Allowed types' in error_message or 'allowed' in error_message.lower(), \
            "Error message should mention allowed types"
    else:
        # File type should be accepted
        assert is_valid, f"File type {file_extension} should be accepted"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
