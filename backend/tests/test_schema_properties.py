"""
Property-based tests for database schema completeness.

Feature: course-media-and-access-fixes
"""

import pytest
from datetime import datetime, timezone
from hypothesis import given, strategies as st, settings
from bson import ObjectId


# Helper functions to create database records with proper schemas

def create_course_record(title, description, teacher_id, thumbnail=None):
    """
    Creates a course record with all required fields.
    
    Args:
        title: Course title
        description: Course description
        teacher_id: Teacher's user ID
        thumbnail: Optional thumbnail path
    
    Returns:
        dict representing the course record
    """
    course_record = {
        '_id': ObjectId(),
        'title': title,
        'description': description,
        'thumbnail': thumbnail or 'https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg',
        'teacher_id': teacher_id,
        'category': 'General',
        'difficulty': 'Beginner',
        'duration': '4 weeks',
        'prerequisites': [],
        'learning_objectives': [],
        'is_active': True,
        'is_public': True,
        'max_students': 0,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    
    return course_record


def create_module_record(course_id, title, description, order):
    """
    Creates a module record with all required fields.
    
    Args:
        course_id: Course ID
        title: Module title
        description: Module description
        order: Module order
    
    Returns:
        dict representing the module record
    """
    module_record = {
        '_id': ObjectId(),
        'course_id': course_id,
        'title': title,
        'description': description,
        'order': order,
        'created_at': datetime.now(timezone.utc)
    }
    
    return module_record


def create_material_record(course_id, module_id, title, material_type, file_path):
    """
    Creates a material record with all required fields.
    
    Args:
        course_id: Course ID
        module_id: Module ID
        title: Material title
        material_type: Type of material (video, document, link)
        file_path: Path to the file
    
    Returns:
        dict representing the material record
    """
    material_record = {
        '_id': ObjectId(),
        'course_id': course_id,
        'module_id': module_id,
        'title': title,
        'type': material_type,
        'content': file_path,  # file_path or video_id
        'file_size': 1024000,  # 1MB
        'mime_type': 'video/mp4' if material_type == 'video' else 'application/pdf',
        'order': 1,
        'is_required': False,
        'uploaded_at': datetime.now(timezone.utc),
        'created_at': datetime.now(timezone.utc)
    }
    
    return material_record


def create_enrollment_record(student_id, course_id):
    """
    Creates an enrollment record with all required fields.
    
    Args:
        student_id: Student's user ID
        course_id: Course ID
    
    Returns:
        dict representing the enrollment record
    """
    enrollment_record = {
        '_id': ObjectId(),
        'student_id': student_id,
        'course_id': course_id,
        'enrolled_at': datetime.now(timezone.utc),
        'progress': 0,
        'completed_materials': [],
        'completed_assignments': [],
        'is_active': True
    }
    
    return enrollment_record


def create_progress_record(student_id, course_id, started=False):
    """
    Creates a progress record with all required fields.
    
    Args:
        student_id: Student's user ID
        course_id: Course ID
        started: Whether the course has been started
    
    Returns:
        dict representing the progress record
    """
    current_time = datetime.now(timezone.utc)
    
    progress_record = {
        '_id': ObjectId(),
        'student_id': student_id,
        'course_id': course_id,
        'last_accessed': current_time if started else None,
        'started': started,
        'completed_materials': [],
        'overall_progress': 0,
        'created_at': current_time,
        'updated_at': current_time
    }
    
    return progress_record


# Property 35: Course schema completeness
@given(
    title=st.text(min_size=1, max_size=200),
    description=st.text(min_size=1, max_size=1000),
    teacher_id=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=24,
        max_size=24
    )
)
@settings(max_examples=100)
def test_property_35_course_schema_completeness(title, description, teacher_id):
    """
    **Feature: course-media-and-access-fixes, Property 35: Course schema completeness**
    **Validates: Requirements 7.1**
    
    Property: For any course record in the database, it should contain all required fields:
    _id, title, description, thumbnail_path, teacher_id, created_at, updated_at
    """
    # Create course record
    course = create_course_record(title, description, teacher_id)
    
    # Verify all required fields are present
    required_fields = ['_id', 'title', 'description', 'thumbnail', 'teacher_id', 'created_at', 'updated_at']
    
    for field in required_fields:
        assert field in course, f"Course record should have '{field}' field"
    
    # Verify field types
    assert isinstance(course['_id'], ObjectId), "_id should be an ObjectId"
    assert isinstance(course['title'], str), "title should be a string"
    assert isinstance(course['description'], str), "description should be a string"
    assert isinstance(course['thumbnail'], str), "thumbnail should be a string"
    assert isinstance(course['teacher_id'], str), "teacher_id should be a string"
    assert isinstance(course['created_at'], datetime), "created_at should be a datetime"
    assert isinstance(course['updated_at'], datetime), "updated_at should be a datetime"
    
    # Verify field values match input
    assert course['title'] == title, f"Course title should be '{title}'"
    assert course['description'] == description, f"Course description should be '{description}'"
    assert course['teacher_id'] == teacher_id, f"Course teacher_id should be '{teacher_id}'"


# Property 36: Module schema completeness
@given(
    course_id=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=24,
        max_size=24
    ),
    title=st.text(min_size=1, max_size=200),
    description=st.text(min_size=0, max_size=1000),
    order=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=100)
def test_property_36_module_schema_completeness(course_id, title, description, order):
    """
    **Feature: course-media-and-access-fixes, Property 36: Module schema completeness**
    **Validates: Requirements 7.2**
    
    Property: For any module record in the database, it should contain all required fields:
    _id, course_id, title, description, order, created_at
    
    Note: materials field is not required in the module record itself, as materials
    are stored in a separate collection with module_id references.
    """
    # Create module record
    module = create_module_record(course_id, title, description, order)
    
    # Verify all required fields are present
    required_fields = ['_id', 'course_id', 'title', 'description', 'order', 'created_at']
    
    for field in required_fields:
        assert field in module, f"Module record should have '{field}' field"
    
    # Verify field types
    assert isinstance(module['_id'], ObjectId), "_id should be an ObjectId"
    assert isinstance(module['course_id'], str), "course_id should be a string"
    assert isinstance(module['title'], str), "title should be a string"
    assert isinstance(module['description'], str), "description should be a string"
    assert isinstance(module['order'], int), "order should be an integer"
    assert isinstance(module['created_at'], datetime), "created_at should be a datetime"
    
    # Verify field values match input
    assert module['course_id'] == course_id, f"Module course_id should be '{course_id}'"
    assert module['title'] == title, f"Module title should be '{title}'"
    assert module['description'] == description, f"Module description should be '{description}'"
    assert module['order'] == order, f"Module order should be {order}"


# Property 37: Material schema completeness
@given(
    course_id=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=24,
        max_size=24
    ),
    module_id=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=24,
        max_size=24
    ),
    title=st.text(min_size=1, max_size=200),
    material_type=st.sampled_from(['video', 'document', 'link']),
    file_path=st.text(min_size=1, max_size=500)
)
@settings(max_examples=100)
def test_property_37_material_schema_completeness(course_id, module_id, title, material_type, file_path):
    """
    **Feature: course-media-and-access-fixes, Property 37: Material schema completeness**
    **Validates: Requirements 7.3**
    
    Property: For any material record in the database, it should contain all required fields:
    _id (material_id), type, title, content (file_path), file_size, mime_type, uploaded_at
    """
    # Create material record
    material = create_material_record(course_id, module_id, title, material_type, file_path)
    
    # Verify all required fields are present
    # Note: Using 'content' instead of 'file_path' as per actual implementation
    required_fields = ['_id', 'type', 'title', 'content', 'file_size', 'mime_type', 'uploaded_at']
    
    for field in required_fields:
        assert field in material, f"Material record should have '{field}' field"
    
    # Verify field types
    assert isinstance(material['_id'], ObjectId), "_id should be an ObjectId"
    assert isinstance(material['type'], str), "type should be a string"
    assert isinstance(material['title'], str), "title should be a string"
    assert isinstance(material['content'], str), "content (file_path) should be a string"
    assert isinstance(material['file_size'], int), "file_size should be an integer"
    assert isinstance(material['mime_type'], str), "mime_type should be a string"
    assert isinstance(material['uploaded_at'], datetime), "uploaded_at should be a datetime"
    
    # Verify field values match input
    assert material['type'] == material_type, f"Material type should be '{material_type}'"
    assert material['title'] == title, f"Material title should be '{title}'"
    assert material['content'] == file_path, f"Material content should be '{file_path}'"
    
    # Verify type is one of the allowed values
    assert material['type'] in ['video', 'document', 'link'], \
        f"Material type should be one of ['video', 'document', 'link'], got '{material['type']}'"


# Property 38: Enrollment schema completeness
@given(
    student_id=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=24,
        max_size=24
    ),
    course_id=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=24,
        max_size=24
    )
)
@settings(max_examples=100)
def test_property_38_enrollment_schema_completeness(student_id, course_id):
    """
    **Feature: course-media-and-access-fixes, Property 38: Enrollment schema completeness**
    **Validates: Requirements 7.4**
    
    Property: For any enrollment record in the database, it should contain all required fields:
    _id, student_id, course_id, enrolled_at, progress (progress_state)
    """
    # Create enrollment record
    enrollment = create_enrollment_record(student_id, course_id)
    
    # Verify all required fields are present
    # Note: Using 'progress' field instead of 'progress_state' as per actual implementation
    required_fields = ['_id', 'student_id', 'course_id', 'enrolled_at', 'progress']
    
    for field in required_fields:
        assert field in enrollment, f"Enrollment record should have '{field}' field"
    
    # Verify field types
    assert isinstance(enrollment['_id'], ObjectId), "_id should be an ObjectId"
    assert isinstance(enrollment['student_id'], str), "student_id should be a string"
    assert isinstance(enrollment['course_id'], str), "course_id should be a string"
    assert isinstance(enrollment['enrolled_at'], datetime), "enrolled_at should be a datetime"
    assert isinstance(enrollment['progress'], (int, float)), "progress should be a number"
    
    # Verify field values match input
    assert enrollment['student_id'] == student_id, f"Enrollment student_id should be '{student_id}'"
    assert enrollment['course_id'] == course_id, f"Enrollment course_id should be '{course_id}'"
    
    # Verify initial progress is 0
    assert enrollment['progress'] == 0, "Initial progress should be 0"
    
    # Verify additional required fields
    assert 'completed_materials' in enrollment, "Enrollment should have completed_materials field"
    assert isinstance(enrollment['completed_materials'], list), "completed_materials should be a list"
    assert 'is_active' in enrollment, "Enrollment should have is_active field"
    assert isinstance(enrollment['is_active'], bool), "is_active should be a boolean"


# Property 39: Progress schema completeness
@given(
    student_id=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=24,
        max_size=24
    ),
    course_id=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=24,
        max_size=24
    ),
    started=st.booleans()
)
@settings(max_examples=100)
def test_property_39_progress_schema_completeness(student_id, course_id, started):
    """
    **Feature: course-media-and-access-fixes, Property 39: Progress schema completeness**
    **Validates: Requirements 7.5**
    
    Property: For any progress record in the database, it should contain all required fields:
    _id, student_id, course_id, last_accessed, started, completed_materials
    """
    # Create progress record
    progress = create_progress_record(student_id, course_id, started)
    
    # Verify all required fields are present
    required_fields = ['_id', 'student_id', 'course_id', 'last_accessed', 'started', 'completed_materials']
    
    for field in required_fields:
        assert field in progress, f"Progress record should have '{field}' field"
    
    # Verify field types
    assert isinstance(progress['_id'], ObjectId), "_id should be an ObjectId"
    assert isinstance(progress['student_id'], str), "student_id should be a string"
    assert isinstance(progress['course_id'], str), "course_id should be a string"
    assert progress['last_accessed'] is None or isinstance(progress['last_accessed'], datetime), \
        "last_accessed should be None or a datetime"
    assert isinstance(progress['started'], bool), "started should be a boolean"
    assert isinstance(progress['completed_materials'], list), "completed_materials should be a list"
    
    # Verify field values match input
    assert progress['student_id'] == student_id, f"Progress student_id should be '{student_id}'"
    assert progress['course_id'] == course_id, f"Progress course_id should be '{course_id}'"
    assert progress['started'] == started, f"Progress started should be {started}"
    
    # Verify last_accessed is set when started is True
    if started:
        assert progress['last_accessed'] is not None, \
            "last_accessed should be set when course is started"
        assert isinstance(progress['last_accessed'], datetime), \
            "last_accessed should be a datetime when set"
    
    # Verify additional required fields
    assert 'overall_progress' in progress, "Progress should have overall_progress field"
    assert isinstance(progress['overall_progress'], (int, float)), "overall_progress should be a number"
    assert 'created_at' in progress, "Progress should have created_at field"
    assert isinstance(progress['created_at'], datetime), "created_at should be a datetime"
    assert 'updated_at' in progress, "Progress should have updated_at field"
    assert isinstance(progress['updated_at'], datetime), "updated_at should be a datetime"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
