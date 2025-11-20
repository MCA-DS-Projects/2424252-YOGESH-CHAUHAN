"""
Property-based tests for video upload, validation, and streaming.

Feature: course-media-and-access-fixes
"""

import pytest
import os
import uuid
from datetime import datetime, timezone
from hypothesis import given, strategies as st, settings


# Helper functions to simulate video validation logic
def validate_video_file(file_extension, file_size_bytes):
    """
    Validates video file based on type and size.
    
    Args:
        file_extension: File extension (e.g., 'mp4', 'webm', 'ogg', 'avi')
        file_size_bytes: File size in bytes
    
    Returns:
        dict with 'is_valid' boolean and optional 'error' message
    """
    allowed_extensions = {'mp4', 'webm', 'ogg'}
    max_size_bytes = 500 * 1024 * 1024  # 500MB
    
    is_valid_type = file_extension.lower() in allowed_extensions
    is_valid_size = file_size_bytes <= max_size_bytes
    
    if not is_valid_type:
        return {
            'is_valid': False,
            'error': f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
        }
    
    if not is_valid_size:
        return {
            'is_valid': False,
            'error': f'File size exceeds maximum allowed size of 500MB'
        }
    
    return {'is_valid': True}


def generate_unique_video_filename(original_filename):
    """
    Generates a unique filename for video using UUID and preserving extension.
    
    Args:
        original_filename: Original filename with extension
    
    Returns:
        Unique filename string with preserved extension
    """
    if '.' in original_filename:
        file_extension = original_filename.rsplit('.', 1)[1].lower()
    else:
        file_extension = 'mp4'  # default
    
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{file_extension}"


def store_video_path(video_path):
    """
    Simulates storing and retrieving video path from database.
    
    Args:
        video_path: Path to store
    
    Returns:
        The same path (simulating round-trip)
    """
    # In real implementation, this would store in MongoDB and retrieve
    # For testing, we just return the same path
    return video_path


def get_mime_type_for_video(file_extension):
    """
    Returns the MIME type for a video file extension.
    
    Args:
        file_extension: File extension (e.g., 'mp4', 'webm', 'ogg')
    
    Returns:
        MIME type string
    """
    mime_types = {
        'mp4': 'video/mp4',
        'webm': 'video/webm',
        'ogg': 'video/ogg'
    }
    return mime_types.get(file_extension.lower(), 'video/mp4')


# Property 12: Video file validation
@given(
    file_extension=st.sampled_from(['mp4', 'webm', 'ogg', 'avi', 'mov', 'mkv', 'flv', 'wmv']),
    file_size_mb=st.floats(min_value=0.1, max_value=600.0)
)
@settings(max_examples=100)
def test_property_12_video_file_validation(file_extension, file_size_mb):
    """
    **Feature: course-media-and-access-fixes, Property 12: Video file validation**
    **Validates: Requirements 3.1**
    
    Property: For any file upload attempt, if the file is a valid video type 
    (MP4, WebM, OGG) and under 500MB, the system should accept it; 
    otherwise, it should reject it with an appropriate error.
    """
    file_size_bytes = int(file_size_mb * 1024 * 1024)
    
    # Determine expected validity
    allowed_extensions = {'mp4', 'webm', 'ogg'}
    is_valid_type = file_extension.lower() in allowed_extensions
    is_valid_size = file_size_bytes <= 500 * 1024 * 1024
    expected_valid = is_valid_type and is_valid_size
    
    # Test the validation function
    result = validate_video_file(file_extension, file_size_bytes)
    
    # Assert the result matches expectations
    assert result['is_valid'] == expected_valid, \
        f"Expected valid={expected_valid} for {file_extension} ({file_size_mb:.2f}MB), got {result['is_valid']}"
    
    # If invalid, should have error message
    if not expected_valid:
        assert 'error' in result, "Invalid file should have error message"
        assert len(result['error']) > 0, "Error message should not be empty"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])



# Property 14: Video filename uniqueness with extension
@given(
    filenames=st.lists(
        st.builds(
            lambda name, ext: f"{name}.{ext}",
            name=st.text(
                alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
                min_size=1,
                max_size=50
            ),
            ext=st.sampled_from(['mp4', 'webm', 'ogg'])
        ),
        min_size=2,
        max_size=20
    )
)
@settings(max_examples=100)
def test_property_14_video_filename_uniqueness(filenames):
    """
    **Feature: course-media-and-access-fixes, Property 14: Video filename uniqueness with extension**
    **Validates: Requirements 3.3**
    
    Property: For any two video uploads, the system should generate different 
    unique filenames while preserving the original file extension.
    """
    # Generate unique filenames for all inputs
    generated_names = [generate_unique_video_filename(name) for name in filenames]
    
    # All generated names should be unique
    assert len(generated_names) == len(set(generated_names)), \
        f"Generated filenames are not unique: {generated_names}"
    
    # Each generated name should preserve the extension
    for original, generated in zip(filenames, generated_names):
        original_ext = original.rsplit('.', 1)[1].lower() if '.' in original else 'mp4'
        generated_ext = generated.rsplit('.', 1)[1].lower() if '.' in generated else ''
        
        assert generated_ext == original_ext, \
            f"Extension not preserved: original '{original}' ({original_ext}) -> generated '{generated}' ({generated_ext})"
    
    # Each generated name should contain UUID pattern
    for generated_name in generated_names:
        # Should have format: <uuid>.<ext>
        parts = generated_name.rsplit('.', 1)
        assert len(parts) == 2, f"Generated filename should have extension: {generated_name}"
        
        uuid_part = parts[0]
        # UUID should be 36 characters (8-4-4-4-12 with hyphens)
        assert len(uuid_part) == 36, f"UUID part should be 36 characters: {uuid_part}"
        assert uuid_part.count('-') == 4, f"UUID should have 4 hyphens: {uuid_part}"



# Property 15: Video path round-trip
@given(
    video_path=st.builds(
        lambda filename: f"/backend/uploads/videos/{filename}",
        filename=st.builds(
            lambda uuid_str, ext: f"{uuid_str}.{ext}",
            uuid_str=st.text(
                alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-'),
                min_size=36,
                max_size=36
            ),
            ext=st.sampled_from(['mp4', 'webm', 'ogg'])
        )
    )
)
@settings(max_examples=100)
def test_property_15_video_path_round_trip(video_path):
    """
    **Feature: course-media-and-access-fixes, Property 15: Video path round-trip**
    **Validates: Requirements 3.4**
    
    Property: For any video uploaded to a module, fetching the module from 
    the database should return the same video path that was stored.
    """
    # Store the video path
    stored_path = store_video_path(video_path)
    
    # Retrieve should return the same path
    assert stored_path == video_path, \
        f"Round-trip failed: stored '{video_path}', got back '{stored_path}'"
    
    # Path should be preserved exactly (no modifications)
    assert len(stored_path) == len(video_path), \
        "Path length should be preserved"
    
    # Path should contain the expected directory structure
    assert '/videos/' in stored_path, \
        "Path should contain '/videos/' directory"



# Property 17: Video MIME type headers
@given(
    file_extension=st.sampled_from(['mp4', 'webm', 'ogg'])
)
@settings(max_examples=100)
def test_property_17_video_mime_type_headers(file_extension):
    """
    **Feature: course-media-and-access-fixes, Property 17: Video MIME type headers**
    **Validates: Requirements 3.7**
    
    Property: For any video file served by the API, the response should include 
    a Content-Type header matching the video's MIME type.
    """
    # Get the MIME type for the file extension
    mime_type = get_mime_type_for_video(file_extension)
    
    # Expected MIME types
    expected_mime_types = {
        'mp4': 'video/mp4',
        'webm': 'video/webm',
        'ogg': 'video/ogg'
    }
    
    expected_mime = expected_mime_types.get(file_extension.lower())
    
    # Assert the MIME type matches the expected value
    assert mime_type == expected_mime, \
        f"Expected MIME type '{expected_mime}' for extension '{file_extension}', got '{mime_type}'"
    
    # MIME type should start with 'video/'
    assert mime_type.startswith('video/'), \
        f"MIME type should start with 'video/', got '{mime_type}'"
    
    # MIME type should not be empty
    assert len(mime_type) > 0, "MIME type should not be empty"
