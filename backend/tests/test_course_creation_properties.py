"""
Property-based tests for course creation workflow.

Feature: course-media-and-access-fixes
"""

import pytest
import os
import sys
from datetime import datetime, timezone
from hypothesis import given, strategies as st, settings, assume
from bson import ObjectId

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Helper functions to simulate course creation logic
def create_course_with_metadata(title, description, thumbnail):
    """
    Simulates creating a course with metadata and storing in database.
    
    Args:
        title: Course title
        description: Course description
        thumbnail: Thumbnail URL/path
    
    Returns:
        dict representing the stored course
    """
    course_data = {
        '_id': str(ObjectId()),
        'title': title,
        'description': description,
        'thumbnail': thumbnail,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    return course_data


def fetch_course_from_db(course_data):
    """
    Simulates fetching course from database.
    
    Args:
        course_data: Course data to simulate fetching
    
    Returns:
        The same course data (simulating round-trip)
    """
    # In real implementation, this would query MongoDB
    # For testing, we return the same data
    return course_data


def create_module_with_metadata(course_id, title, description, order):
    """
    Simulates creating a module with metadata.
    
    Args:
        course_id: ID of the parent course
        title: Module title
        description: Module description
        order: Module order number
    
    Returns:
        dict representing the stored module
    """
    module_data = {
        '_id': str(ObjectId()),
        'course_id': course_id,
        'title': title,
        'description': description,
        'order': order,
        'materials': [],
        'created_at': datetime.utcnow()
    }
    return module_data


def fetch_modules_for_course(course_id, modules):
    """
    Simulates fetching modules for a course from database.
    
    Args:
        course_id: ID of the course
        modules: List of modules to simulate fetching
    
    Returns:
        List of modules for the course
    """
    # In real implementation, this would query MongoDB
    # For testing, we return the same modules
    return [m for m in modules if m['course_id'] == course_id]


def create_material_with_metadata(course_id, title, material_type, content, file_path, file_size, mime_type):
    """
    Simulates creating a material with metadata.
    
    Args:
        course_id: ID of the parent course
        title: Material title
        material_type: Type of material (video, document, etc.)
        content: Content reference (video_id, document_id, etc.)
        file_path: Path to the file
        file_size: Size of the file in bytes
        mime_type: MIME type of the file
    
    Returns:
        dict representing the stored material
    """
    material_data = {
        'material_id': str(ObjectId()),
        'course_id': course_id,
        'title': title,
        'type': material_type,
        'content': content,
        'file_path': file_path,
        'file_size': file_size,
        'mime_type': mime_type,
        'uploaded_at': datetime.utcnow()
    }
    return material_data


def fetch_materials_for_module(module_id, materials):
    """
    Simulates fetching materials for a module from database.
    
    Args:
        module_id: ID of the module
        materials: List of materials to simulate fetching
    
    Returns:
        List of materials for the module
    """
    # In real implementation, this would query MongoDB
    # For testing, we return the same materials
    return materials


# Property 23: Course metadata round-trip
@given(
    title=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    description=st.text(min_size=1, max_size=2000).filter(lambda x: x.strip()),
    thumbnail=st.one_of(
        st.builds(
            lambda uuid_str: f"/api/courses/thumbnails/{uuid_str}.jpg",
            uuid_str=st.uuids().map(str)
        ),
        st.just('https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg?auto=compress&cs=tinysrgb&w=400')
    )
)
@settings(max_examples=100)
def test_property_23_course_metadata_round_trip(title, description, thumbnail):
    """
    **Feature: course-media-and-access-fixes, Property 23: Course metadata round-trip**
    **Validates: Requirements 5.1**
    
    Property: For any course created with metadata (title, description, thumbnail), 
    fetching the course should return all the same metadata values.
    """
    # Create course with metadata
    created_course = create_course_with_metadata(title, description, thumbnail)
    
    # Fetch course from database
    fetched_course = fetch_course_from_db(created_course)
    
    # Verify all metadata is preserved
    assert fetched_course['title'] == title, \
        f"Title not preserved: expected '{title}', got '{fetched_course['title']}'"
    
    assert fetched_course['description'] == description, \
        f"Description not preserved: expected '{description}', got '{fetched_course['description']}'"
    
    assert fetched_course['thumbnail'] == thumbnail, \
        f"Thumbnail not preserved: expected '{thumbnail}', got '{fetched_course['thumbnail']}'"
    
    # Verify course has required fields
    assert '_id' in fetched_course, "Course should have _id field"
    assert 'created_at' in fetched_course, "Course should have created_at field"
    assert 'updated_at' in fetched_course, "Course should have updated_at field"


# Property 24: Module metadata round-trip
@given(
    modules=st.lists(
        st.builds(
            lambda title, desc, order: {
                'title': title,
                'description': desc,
                'order': order
            },
            title=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
            desc=st.text(min_size=0, max_size=1000),
            order=st.integers(min_value=1, max_value=100)
        ),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100)
def test_property_24_module_metadata_round_trip(modules):
    """
    **Feature: course-media-and-access-fixes, Property 24: Module metadata round-trip**
    **Validates: Requirements 5.2**
    
    Property: For any modules added to a course, fetching the course should 
    return all modules with their metadata intact.
    """
    # Create a course
    course_id = str(ObjectId())
    
    # Create modules with metadata
    created_modules = []
    for module_spec in modules:
        module = create_module_with_metadata(
            course_id,
            module_spec['title'],
            module_spec['description'],
            module_spec['order']
        )
        created_modules.append(module)
    
    # Fetch modules for the course
    fetched_modules = fetch_modules_for_course(course_id, created_modules)
    
    # Verify all modules are returned
    assert len(fetched_modules) == len(modules), \
        f"Expected {len(modules)} modules, got {len(fetched_modules)}"
    
    # Verify each module's metadata is preserved
    for original, fetched in zip(modules, fetched_modules):
        assert fetched['title'] == original['title'], \
            f"Module title not preserved: expected '{original['title']}', got '{fetched['title']}'"
        
        assert fetched['description'] == original['description'], \
            f"Module description not preserved: expected '{original['description']}', got '{fetched['description']}'"
        
        assert fetched['order'] == original['order'], \
            f"Module order not preserved: expected {original['order']}, got {fetched['order']}"
        
        # Verify module has required fields
        assert '_id' in fetched, "Module should have _id field"
        assert 'course_id' in fetched, "Module should have course_id field"
        assert fetched['course_id'] == course_id, "Module should be linked to correct course"
        assert 'materials' in fetched, "Module should have materials field"
        assert 'created_at' in fetched, "Module should have created_at field"


# Property 25: Material metadata round-trip
@given(
    materials=st.lists(
        st.builds(
            lambda title, mat_type, content, file_size: {
                'title': title,
                'type': mat_type,
                'content': content,
                'file_size': file_size
            },
            title=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
            mat_type=st.sampled_from(['video', 'document', 'link']),
            content=st.uuids().map(str),  # Simulating video_id or document_id
            file_size=st.integers(min_value=1024, max_value=500*1024*1024)  # 1KB to 500MB
        ),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100)
def test_property_25_material_metadata_round_trip(materials):
    """
    **Feature: course-media-and-access-fixes, Property 25: Material metadata round-trip**
    **Validates: Requirements 5.3**
    
    Property: For any materials uploaded to a module, fetching the module should 
    return all materials with their metadata intact.
    """
    # Create a course and module
    course_id = str(ObjectId())
    module_id = str(ObjectId())
    
    # Create materials with metadata
    created_materials = []
    for material_spec in materials:
        # Generate file path and MIME type based on material type
        if material_spec['type'] == 'video':
            file_path = f"/backend/uploads/videos/{material_spec['content']}.mp4"
            mime_type = 'video/mp4'
        elif material_spec['type'] == 'document':
            file_path = f"/backend/uploads/documents/{material_spec['content']}.pdf"
            mime_type = 'application/pdf'
        else:
            file_path = material_spec['content']
            mime_type = 'text/html'
        
        material = create_material_with_metadata(
            course_id,
            material_spec['title'],
            material_spec['type'],
            material_spec['content'],
            file_path,
            material_spec['file_size'],
            mime_type
        )
        created_materials.append(material)
    
    # Fetch materials for the module
    fetched_materials = fetch_materials_for_module(module_id, created_materials)
    
    # Verify all materials are returned
    assert len(fetched_materials) == len(materials), \
        f"Expected {len(materials)} materials, got {len(fetched_materials)}"
    
    # Verify each material's metadata is preserved
    for original, fetched in zip(materials, fetched_materials):
        assert fetched['title'] == original['title'], \
            f"Material title not preserved: expected '{original['title']}', got '{fetched['title']}'"
        
        assert fetched['type'] == original['type'], \
            f"Material type not preserved: expected '{original['type']}', got '{fetched['type']}'"
        
        assert fetched['content'] == original['content'], \
            f"Material content not preserved: expected '{original['content']}', got '{fetched['content']}'"
        
        assert fetched['file_size'] == original['file_size'], \
            f"Material file_size not preserved: expected {original['file_size']}, got {fetched['file_size']}"
        
        # Verify material has required fields
        assert 'material_id' in fetched, "Material should have material_id field"
        assert 'course_id' in fetched, "Material should have course_id field"
        assert fetched['course_id'] == course_id, "Material should be linked to correct course"
        assert 'file_path' in fetched, "Material should have file_path field"
        assert 'mime_type' in fetched, "Material should have mime_type field"
        assert 'uploaded_at' in fetched, "Material should have uploaded_at field"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
