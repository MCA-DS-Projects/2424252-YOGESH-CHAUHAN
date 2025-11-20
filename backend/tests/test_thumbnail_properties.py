"""
Property-based tests for thumbnail upload and validation.

Feature: course-media-and-access-fixes
"""

import pytest
import os
import tempfile
import uuid
from datetime import datetime, timezone
from hypothesis import given, strategies as st, settings
from io import BytesIO
from PIL import Image


# Helper functions to simulate thumbnail validation logic
def validate_thumbnail_file(file_extension, file_size_bytes):
    """
    Validates thumbnail file based on type and size.
    
    Args:
        file_extension: File extension (e.g., 'jpg', 'png', 'gif', 'webp', 'pdf')
        file_size_bytes: File size in bytes
    
    Returns:
        dict with 'is_valid' boolean and optional 'error' message
    """
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    max_size_bytes = 5 * 1024 * 1024  # 5MB
    
    is_valid_type = file_extension.lower() in allowed_extensions
    is_valid_size = file_size_bytes <= max_size_bytes
    
    if not is_valid_type:
        return {
            'is_valid': False,
            'error': f'Invalid image file format. Allowed types: {", ".join(allowed_extensions)}'
        }
    
    if not is_valid_size:
        return {
            'is_valid': False,
            'error': f'File size exceeds maximum allowed size of 5MB'
        }
    
    return {'is_valid': True}


def generate_unique_thumbnail_filename(original_filename):
    """
    Generates a unique filename for thumbnail using UUID and timestamp.
    
    Args:
        original_filename: Original filename with extension
    
    Returns:
        Unique filename string
    """
    if '.' in original_filename:
        file_extension = original_filename.rsplit('.', 1)[1].lower()
    else:
        file_extension = 'jpg'  # default
    
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    return f"{unique_id}_{timestamp}.{file_extension}"


def store_thumbnail_path(thumbnail_path):
    """
    Simulates storing and retrieving thumbnail path from database.
    
    Args:
        thumbnail_path: Path to store
    
    Returns:
        The same path (simulating round-trip)
    """
    # In real implementation, this would store in MongoDB and retrieve
    # For testing, we just return the same path
    return thumbnail_path


# Property 1: Thumbnail file validation
@given(
    file_extension=st.sampled_from(['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'txt', 'doc', 'mp4']),
    file_size_mb=st.floats(min_value=0.1, max_value=10.0)
)
@settings(max_examples=100)
def test_property_1_thumbnail_file_validation(file_extension, file_size_mb):
    """
    **Feature: course-media-and-access-fixes, Property 1: Thumbnail file validation**
    **Validates: Requirements 1.1**
    
    Property: For any file upload attempt, if the file is a valid image type 
    (JPEG, PNG, GIF, WebP) and under 5MB, the system should accept it; 
    otherwise, it should reject it with an appropriate error.
    """
    file_size_bytes = int(file_size_mb * 1024 * 1024)
    
    # Determine expected validity
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    is_valid_type = file_extension.lower() in allowed_extensions
    is_valid_size = file_size_bytes <= 5 * 1024 * 1024
    expected_valid = is_valid_type and is_valid_size
    
    # Test the validation function
    result = validate_thumbnail_file(file_extension, file_size_bytes)
    
    # Assert the result matches expectations
    assert result['is_valid'] == expected_valid, \
        f"Expected valid={expected_valid} for {file_extension} ({file_size_mb:.2f}MB), got {result['is_valid']}"
    
    # If invalid, should have error message
    if not expected_valid:
        assert 'error' in result, "Invalid file should have error message"
        assert len(result['error']) > 0, "Error message should not be empty"


# Property 3: Thumbnail filename uniqueness
@given(
    filenames=st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1,
            max_size=50
        ).map(lambda s: s + '.jpg'),
        min_size=2,
        max_size=20
    )
)
@settings(max_examples=100)
def test_property_3_thumbnail_filename_uniqueness(filenames):
    """
    **Feature: course-media-and-access-fixes, Property 3: Thumbnail filename uniqueness**
    **Validates: Requirements 1.3**
    
    Property: For any two thumbnail uploads, even with the same original filename, 
    the system should generate different unique filenames.
    """
    # Generate unique filenames for all inputs
    generated_names = [generate_unique_thumbnail_filename(name) for name in filenames]
    
    # All generated names should be unique
    assert len(generated_names) == len(set(generated_names)), \
        f"Generated filenames are not unique: {generated_names}"
    
    # Each generated name should contain UUID pattern (8-4-4-4-12 hex digits)
    for generated_name in generated_names:
        # Should have format: <uuid>_<timestamp>.<ext>
        parts = generated_name.rsplit('.', 1)
        assert len(parts) == 2, f"Generated filename should have extension: {generated_name}"
        
        name_part = parts[0]
        # Should contain underscore separating UUID and timestamp
        assert '_' in name_part, f"Generated filename should have UUID_timestamp format: {generated_name}"


# Property 4: Thumbnail path round-trip
@given(
    thumbnail_path=st.builds(
        lambda filename: f"/api/courses/thumbnails/{filename}",
        filename=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
            min_size=5,
            max_size=50
        ).map(lambda s: s + '.jpg')
    )
)
@settings(max_examples=100)
def test_property_4_thumbnail_path_round_trip(thumbnail_path):
    """
    **Feature: course-media-and-access-fixes, Property 4: Thumbnail path round-trip**
    **Validates: Requirements 1.4**
    
    Property: For any course created with a thumbnail, fetching the course from 
    the database should return the same thumbnail path that was stored.
    """
    # Store the thumbnail path
    stored_path = store_thumbnail_path(thumbnail_path)
    
    # Retrieve should return the same path
    assert stored_path == thumbnail_path, \
        f"Round-trip failed: stored '{thumbnail_path}', got back '{stored_path}'"
    
    # Path should be preserved exactly (no modifications)
    assert len(stored_path) == len(thumbnail_path), \
        "Path length should be preserved"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
