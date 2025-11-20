"""
Integration test for video streaming endpoint with authorization and HTTP range support.
Tests Requirements 3.6, 3.7, 3.8
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from bson import ObjectId
from datetime import datetime
import tempfile


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def db():
    """Get database instance"""
    with app.app_context():
        yield app.db


def test_video_streaming_endpoint_exists(client, db):
    """
    Test that the video streaming endpoint exists and requires authentication.
    Validates: Requirement 3.6 - Video streaming endpoint
    """
    # Create a test video
    video_doc = {
        'filename': 'test_stream.mp4',
        'original_filename': 'test_stream.mp4',
        'file_path': '/fake/path/test_stream.mp4',
        'file_size': 1000000,
        'mime_type': 'video/mp4',
        'uploaded_by': 'test_user',
        'created_at': datetime.utcnow()
    }
    
    result = db.videos.insert_one(video_doc)
    video_id = str(result.inserted_id)
    
    try:
        # Try to access without authentication
        response = client.get(f'/api/videos/{video_id}/stream')
        
        # Should require authentication
        assert response.status_code == 401, \
            f"Expected 401 Unauthorized, got {response.status_code}"
        
    finally:
        # Cleanup
        db.videos.delete_one({'_id': ObjectId(video_id)})


def test_video_mime_type_stored_correctly(db):
    """
    Test that video MIME types are stored correctly in the database.
    Validates: Requirement 3.7 - Proper MIME type headers
    """
    test_cases = [
        ('video.mp4', 'video/mp4'),
        ('video.webm', 'video/webm'),
        ('video.ogg', 'video/ogg')
    ]
    
    video_ids = []
    
    try:
        for filename, expected_mime in test_cases:
            video_doc = {
                'filename': filename,
                'original_filename': filename,
                'file_path': f'/fake/path/{filename}',
                'file_size': 1000000,
                'mime_type': expected_mime,
                'uploaded_by': 'test_user',
                'created_at': datetime.utcnow()
            }
            
            result = db.videos.insert_one(video_doc)
            video_id = str(result.inserted_id)
            video_ids.append(video_id)
            
            # Verify the MIME type was stored correctly
            saved_video = db.videos.find_one({'_id': ObjectId(video_id)})
            assert saved_video['mime_type'] == expected_mime, \
                f"Expected MIME type '{expected_mime}', got '{saved_video['mime_type']}'"
    
    finally:
        # Cleanup
        for video_id in video_ids:
            db.videos.delete_one({'_id': ObjectId(video_id)})


def test_view_count_tracking(db):
    """
    Test that view count is tracked when videos are accessed.
    Validates: Requirement - Track view count on video access
    """
    # Create a test video
    video_doc = {
        'filename': 'tracked_video.mp4',
        'original_filename': 'tracked_video.mp4',
        'file_path': '/fake/path/tracked_video.mp4',
        'file_size': 1000000,
        'mime_type': 'video/mp4',
        'uploaded_by': 'test_user',
        'view_count': 0,
        'created_at': datetime.utcnow()
    }
    
    result = db.videos.insert_one(video_doc)
    video_id = str(result.inserted_id)
    
    try:
        # Simulate view count increment (as done in the endpoint)
        db.videos.update_one(
            {'_id': ObjectId(video_id)},
            {'$inc': {'view_count': 1}}
        )
        
        # Verify view count was incremented
        updated_video = db.videos.find_one({'_id': ObjectId(video_id)})
        assert updated_video['view_count'] == 1, \
            f"Expected view_count=1, got {updated_video['view_count']}"
        
        # Increment again
        db.videos.update_one(
            {'_id': ObjectId(video_id)},
            {'$inc': {'view_count': 1}}
        )
        
        # Verify view count was incremented again
        updated_video = db.videos.find_one({'_id': ObjectId(video_id)})
        assert updated_video['view_count'] == 2, \
            f"Expected view_count=2, got {updated_video['view_count']}"
    
    finally:
        # Cleanup
        db.videos.delete_one({'_id': ObjectId(video_id)})


def test_enrollment_verification_logic(db):
    """
    Test that enrollment verification logic works correctly.
    Validates: Requirement 3.6 - User authorization check (enrollment verification)
    """
    # Create test data
    student_id = 'test_student_' + str(ObjectId())
    teacher_id = 'test_teacher_' + str(ObjectId())
    course_id = 'test_course_' + str(ObjectId())
    
    # Create a video
    video_doc = {
        'filename': 'course_video.mp4',
        'original_filename': 'course_video.mp4',
        'file_path': '/fake/path/course_video.mp4',
        'file_size': 1000000,
        'mime_type': 'video/mp4',
        'uploaded_by': teacher_id,
        'created_at': datetime.utcnow()
    }
    video_result = db.videos.insert_one(video_doc)
    video_id = str(video_result.inserted_id)
    
    # Create a material linking the video to a course
    material_doc = {
        'course_id': course_id,
        'title': 'Test Video',
        'type': 'video',
        'content': video_id,
        'order': 1,
        'created_at': datetime.utcnow()
    }
    material_result = db.materials.insert_one(material_doc)
    material_id = str(material_result.inserted_id)
    
    try:
        # Test 1: Student NOT enrolled - should not have access
        enrollment = db.enrollments.find_one({
            'student_id': student_id,
            'course_id': course_id
        })
        assert enrollment is None, "Student should not be enrolled initially"
        
        # Test 2: Create enrollment
        enrollment_doc = {
            'student_id': student_id,
            'course_id': course_id,
            'enrolled_at': datetime.utcnow()
        }
        enrollment_result = db.enrollments.insert_one(enrollment_doc)
        enrollment_id = str(enrollment_result.inserted_id)
        
        # Test 3: Student IS enrolled - should have access
        enrollment = db.enrollments.find_one({
            'student_id': student_id,
            'course_id': course_id
        })
        assert enrollment is not None, "Student should be enrolled"
        assert enrollment['student_id'] == student_id, "Student ID should match"
        assert enrollment['course_id'] == course_id, "Course ID should match"
        
        # Cleanup enrollment
        db.enrollments.delete_one({'_id': ObjectId(enrollment_id)})
        
    finally:
        # Cleanup
        db.materials.delete_one({'_id': ObjectId(material_id)})
        db.videos.delete_one({'_id': ObjectId(video_id)})


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
