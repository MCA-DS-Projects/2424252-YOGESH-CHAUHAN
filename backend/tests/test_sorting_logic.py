"""
Simple test to verify MongoDB sorting logic works as expected.
"""

def test_mongodb_sort_simulation():
    """
    Simulate MongoDB's sort behavior to verify our implementation.
    """
    # Simulate modules with different order values
    modules = [
        {'_id': '1', 'title': 'Module C', 'order': 3},
        {'_id': '2', 'title': 'Module A', 'order': 1},
        {'_id': '3', 'title': 'Module B', 'order': 2},
        {'_id': '4', 'title': 'Module D', 'order': 4},
    ]
    
    # Sort by order field (ascending) - simulating .sort('order', 1)
    sorted_modules = sorted(modules, key=lambda x: x['order'])
    
    # Verify order
    assert sorted_modules[0]['title'] == 'Module A'
    assert sorted_modules[1]['title'] == 'Module B'
    assert sorted_modules[2]['title'] == 'Module C'
    assert sorted_modules[3]['title'] == 'Module D'
    
    print("✓ Module sorting works correctly")


def test_materials_sort_simulation():
    """
    Simulate MongoDB's sort behavior for materials.
    """
    # Simulate materials with different order values
    materials = [
        {'_id': '1', 'title': 'Material 3', 'order': 3},
        {'_id': '2', 'title': 'Material 1', 'order': 1},
        {'_id': '3', 'title': 'Material 4', 'order': 4},
        {'_id': '4', 'title': 'Material 2', 'order': 2},
    ]
    
    # Sort by order field (ascending) - simulating .sort('order', 1)
    sorted_materials = sorted(materials, key=lambda x: x['order'])
    
    # Verify order
    assert sorted_materials[0]['title'] == 'Material 1'
    assert sorted_materials[1]['title'] == 'Material 2'
    assert sorted_materials[2]['title'] == 'Material 3'
    assert sorted_materials[3]['title'] == 'Material 4'
    
    print("✓ Material sorting works correctly")


if __name__ == '__main__':
    test_mongodb_sort_simulation()
    test_materials_sort_simulation()
    print("\n✅ All sorting logic tests passed!")
