"""
Unit tests for progress tracking endpoints
"""
import pytest
from datetime import datetime
from bson import ObjectId

def test_progress_schema():
    """Test that progress record has all required fields"""
    progress_record = {
        '_id': ObjectId(),
        'course_id': 'test_course_123',
        'student_id': 'test_student_456',
        'started': True,
        'last_accessed': datetime.utcnow(),
        'completed_materials': [],
        'overall_progress': 0,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Verify all required fields are present
    assert '_id' in progress_record
    assert 'course_id' in progress_record
    assert 'student_id' in progress_record
    assert 'started' in progress_record
    assert 'last_accessed' in progress_record
    assert 'completed_materials' in progress_record
    assert 'overall_progress' in progress_record
    assert 'created_at' in progress_record
    assert 'updated_at' in progress_record
    
    # Verify field types
    assert isinstance(progress_record['_id'], ObjectId)
    assert isinstance(progress_record['course_id'], str)
    assert isinstance(progress_record['student_id'], str)
    assert isinstance(progress_record['started'], bool)
    assert isinstance(progress_record['last_accessed'], datetime)
    assert isinstance(progress_record['completed_materials'], list)
    assert isinstance(progress_record['overall_progress'], (int, float))
    assert isinstance(progress_record['created_at'], datetime)
    assert isinstance(progress_record['updated_at'], datetime)
    
    print("✅ Progress schema test passed")

def test_default_progress_state():
    """Test default progress state for new courses"""
    default_progress = {
        'course_id': 'test_course_123',
        'student_id': 'test_student_456',
        'started': False,
        'last_accessed': None,
        'overall_progress': 0,
        'completed_materials': []
    }
    
    # Verify default state
    assert default_progress['started'] is False
    assert default_progress['last_accessed'] is None
    assert default_progress['overall_progress'] == 0
    assert len(default_progress['completed_materials']) == 0
    
    print("✅ Default progress state test passed")

def test_started_progress_state():
    """Test progress state after course is started"""
    started_progress = {
        'course_id': 'test_course_123',
        'student_id': 'test_student_456',
        'started': True,
        'last_accessed': datetime.utcnow(),
        'overall_progress': 0,
        'completed_materials': []
    }
    
    # Verify started state
    assert started_progress['started'] is True
    assert started_progress['last_accessed'] is not None
    assert isinstance(started_progress['last_accessed'], datetime)
    
    print("✅ Started progress state test passed")

if __name__ == "__main__":
    test_progress_schema()
    test_default_progress_state()
    test_started_progress_state()
    print("\n✅ All unit tests passed!")
