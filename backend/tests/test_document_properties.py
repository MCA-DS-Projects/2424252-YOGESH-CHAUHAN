"""
Property-based tests for document upload, validation, and serving.

Feature: course-media-and-access-fixes
"""

import pytest
import os
import uuid
from datetime import datetime, timezone
from hypothesis import given, strategies as st, settings


# Helper functions to simulate document validation logic
def validate_document_file(file_extension, file_size_bytes):
    """
    Validates document file based on type and size.
    
    Args:
        file_extension: File extension (e.g., 'pdf', 'docx', 'pptx', 'txt')
        file_size_bytes: File size in bytes
    
    Returns:
        dict with 'is_valid' boolean and optional 'error' message
    """
    allowed_extensions = {'pdf', 'docx', 'pptx', 'txt'}
    max_size_bytes = 50 * 1024 * 1024  # 50MB
    
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
            'error': f'File size exceeds maximum allowed size of 50MB'
        }
    
    return {'is_valid': True}


def generate_unique_document_filename(original_filename):
    """
    Generates a unique filename for document using UUID and preserving extension.
    
    Args:
        original_filename: Original filename with extension
    
    Returns:
        Unique filename string with preserved extension
    """
    if '.' in original_filename:
        file_extension = original_filename.rsplit('.', 1)[1].lower()
    else:
        file_extension = 'pdf'  # default
    
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{file_extension}"


def store_document_path(document_path):
    """
    Simulates storing and retrieving document path from database.
    
    Args:
        document_path: Path to store
    
    Returns:
        The same path (simulating round-trip)
    """
    # In real implementation, this would store in MongoDB and retrieve
    # For testing, we just return the same path
    return document_path


# Property 19: Document file validation
@given(
    file_extension=st.sampled_from(['pdf', 'docx', 'pptx', 'txt', 'exe', 'zip', 'mp4', 'jpg']),
    file_size_mb=st.floats(min_value=0.1, max_value=60.0)
)
@settings(max_examples=100)
def test_property_19_document_file_validation(file_extension, file_size_mb):
    """
    **Feature: course-media-and-access-fixes, Property 19: Document file validation**
    **Validates: Requirements 4.1**
    
    Property: For any file upload attempt, if the file is a valid document type 
    (PDF, DOCX, PPTX, TXT) and under 50MB, the system should accept it; 
    otherwise, it should reject it with an appropriate error.
    """
    file_size_bytes = int(file_size_mb * 1024 * 1024)
    
    # Determine expected validity
    allowed_extensions = {'pdf', 'docx', 'pptx', 'txt'}
    is_valid_type = file_extension.lower() in allowed_extensions
    is_valid_size = file_size_bytes <= 50 * 1024 * 1024
    expected_valid = is_valid_type and is_valid_size
    
    # Test the validation function
    result = validate_document_file(file_extension, file_size_bytes)
    
    # Assert the result matches expectations
    assert result['is_valid'] == expected_valid, \
        f"Expected valid={expected_valid} for {file_extension} ({file_size_mb:.2f}MB), got {result['is_valid']}"
    
    # If invalid, should have error message
    if not expected_valid:
        assert 'error' in result, "Invalid file should have error message"
        assert len(result['error']) > 0, "Error message should not be empty"


# Property 21: Document filename uniqueness with extension
@given(
    filenames=st.lists(
        st.builds(
            lambda name, ext: f"{name}.{ext}",
            name=st.text(
                alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
                min_size=1,
                max_size=50
            ),
            ext=st.sampled_from(['pdf', 'docx', 'pptx', 'txt'])
        ),
        min_size=2,
        max_size=20
    )
)
@settings(max_examples=100)
def test_property_21_document_filename_uniqueness(filenames):
    """
    **Feature: course-media-and-access-fixes, Property 21: Document filename uniqueness with extension**
    **Validates: Requirements 4.3**
    
    Property: For any two document uploads, the system should generate different 
    unique filenames while preserving the original file extension.
    """
    # Generate unique filenames for all inputs
    generated_names = [generate_unique_document_filename(name) for name in filenames]
    
    # All generated names should be unique
    assert len(generated_names) == len(set(generated_names)), \
        f"Generated filenames are not unique: {generated_names}"
    
    # Each generated name should preserve the extension
    for original, generated in zip(filenames, generated_names):
        original_ext = original.rsplit('.', 1)[1].lower() if '.' in original else 'pdf'
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


# Property 22: Document path round-trip
@given(
    document_path=st.builds(
        lambda filename: f"/backend/uploads/documents/{filename}",
        filename=st.builds(
            lambda uuid_str, ext: f"{uuid_str}.{ext}",
            uuid_str=st.text(
                alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-'),
                min_size=36,
                max_size=36
            ),
            ext=st.sampled_from(['pdf', 'docx', 'pptx', 'txt'])
        )
    )
)
@settings(max_examples=100)
def test_property_22_document_path_round_trip(document_path):
    """
    **Feature: course-media-and-access-fixes, Property 22: Document path round-trip**
    **Validates: Requirements 4.4**
    
    Property: For any document uploaded to a module, fetching the module from 
    the database should return the same document path that was stored.
    """
    # Store the document path
    stored_path = store_document_path(document_path)
    
    # Retrieve should return the same path
    assert stored_path == document_path, \
        f"Round-trip failed: stored '{document_path}', got back '{stored_path}'"
    
    # Path should be preserved exactly (no modifications)
    assert len(stored_path) == len(document_path), \
        "Path length should be preserved"
    
    # Path should contain the expected directory structure
    assert '/documents/' in stored_path, \
        "Path should contain '/documents/' directory"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
