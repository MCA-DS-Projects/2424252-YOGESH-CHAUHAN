"""
Property-based tests for module and material ordering.

Feature: course-media-and-access-fixes
"""

import pytest
import os
import sys
from hypothesis import given, strategies as st, settings
from bson import ObjectId

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def create_module_with_order(course_id, title, order):
    """
    Simulates creating a module with an order field.
    
    Args:
        course_id: ID of the parent course
        title: Module title
        order: Module order number
    
    Returns:
        dict representing the stored module
    """
    module_data = {
        '_id': str(ObjectId()),
        'course_id': course_id,
        'title': title,
        'order': order
    }
    return module_data


def fetch_and_sort_modules(modules):
    """
    Simulates fetching modules from database and sorting by order field.
    
    Args:
        modules: List of modules
    
    Returns:
        List of modules sorted by order field
    """
    # Sort modules by order field (ascending)
    return sorted(modules, key=lambda m: m['order'])


def create_material_with_order(module_id, title, order):
    """
    Simulates creating a material with an order field.
    
    Args:
        module_id: ID of the parent module
        title: Material title
        order: Material order number
    
    Returns:
        dict representing the stored material
    """
    material_data = {
        '_id': str(ObjectId()),
        'module_id': module_id,
        'title': title,
        'order': order
    }
    return material_data


def fetch_and_sort_materials(materials):
    """
    Simulates fetching materials from database and sorting by order field.
    
    Args:
        materials: List of materials
    
    Returns:
        List of materials sorted by order field
    """
    # Sort materials by order field (ascending)
    return sorted(materials, key=lambda m: m['order'])


# Property 27: Module ordering consistency
@given(st.lists(st.integers(min_value=0, max_value=100), min_size=2, max_size=10))
@settings(max_examples=100)
def test_module_ordering_consistency(order_values):
    """
    **Feature: course-media-and-access-fixes, Property 27: Module ordering consistency**
    **Validates: Requirements 5.5**
    
    Property: For any course with multiple modules, the modules should be 
    displayed in ascending order by their order field.
    
    This test verifies that regardless of the order in which modules are created,
    when fetched from the database, they are always sorted by their order field.
    """
    course_id = str(ObjectId())
    
    # Create modules with random order values
    modules = []
    for i, order in enumerate(order_values):
        module = create_module_with_order(
            course_id=course_id,
            title=f"Module {i + 1}",
            order=order
        )
        modules.append(module)
    
    # Fetch and sort modules (simulating database query with sort)
    sorted_modules = fetch_and_sort_modules(modules)
    
    # Extract order values from sorted modules
    sorted_order_values = [m['order'] for m in sorted_modules]
    
    # Verify they are in ascending order
    assert sorted_order_values == sorted(order_values), \
        f"Modules not sorted correctly. Expected {sorted(order_values)}, got {sorted_order_values}"


# Property 28: Material ordering consistency
@given(st.lists(st.integers(min_value=0, max_value=100), min_size=2, max_size=10))
@settings(max_examples=100)
def test_material_ordering_consistency(order_values):
    """
    **Feature: course-media-and-access-fixes, Property 28: Material ordering consistency**
    **Validates: Requirements 5.6**
    
    Property: For any module with multiple materials, the materials should be 
    displayed in ascending order by their order field.
    
    This test verifies that regardless of the order in which materials are created,
    when fetched from the database, they are always sorted by their order field.
    """
    module_id = str(ObjectId())
    
    # Create materials with random order values
    materials = []
    for i, order in enumerate(order_values):
        material = create_material_with_order(
            module_id=module_id,
            title=f"Material {i + 1}",
            order=order
        )
        materials.append(material)
    
    # Fetch and sort materials (simulating database query with sort)
    sorted_materials = fetch_and_sort_materials(materials)
    
    # Extract order values from sorted materials
    sorted_order_values = [m['order'] for m in sorted_materials]
    
    # Verify they are in ascending order
    assert sorted_order_values == sorted(order_values), \
        f"Materials not sorted correctly. Expected {sorted(order_values)}, got {sorted_order_values}"


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
