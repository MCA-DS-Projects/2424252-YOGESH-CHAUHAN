"""
Integration tests for student course enrollment and access control.

Tests the actual API endpoints with database operations.
Feature: course-media-and-access-fixes
"""

import pytest
from bson import ObjectId
from datetime import datetime


def test_enrollment_record_creation_integration(client, db, student_user, student_token, teacher_user):
    """
    Integration test for Property 26: Enrollment record creation
    
    Verifies that when a student enrolls in a course, an enrollment record
    is created in the database with all required fields.
    """
    # Create a test course
    course_data = {
        '_id': ObjectId(),
        'title': 'Test Course for Enrollment',
        'description': 'Test course description',
        'teacher_id': str(teacher_user['_id']),
        'category': 'Technology',
        'difficulty': 'Beginner',
        'is_active': True,
        'is_public': True,
        'created_at': datetime.utcnow()
    }
    db.courses.insert_one(course_data)
    course_id = str(course_data['_id'])
    
    # Enroll student in course
    response = client.post(
        f'/api/courses/{course_id}/enroll',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    assert response.status_code == 200, f"Enrollment should succeed, got {response.status_code}"
    
    # Verify enrollment record exists in database
    enrollment = db.enrollments.find_one({
        'course_id': course_id,
        'student_id': str(student_user['_id'])
    })
    
    assert enrollment is not None, "Enrollment record should exist in database"
    
    # Verify enrollment has required fields
    assert 'student_id' in enrollment, "Enrollment should have student_id"
    assert 'course_id' in enrollment, "Enrollment should have course_id"
    assert 'enrolled_at' in enrollment, "Enrollment should have enrolled_at"
    assert 'progress' in enrollment, "Enrollment should have progress"
    assert 'completed_materials' in enrollment, "Enrollment should have completed_materials"
    assert 'is_active' in enrollment, "Enrollment should have is_active"
    
    # Verify enrollment links correct student and course
    assert enrollment['student_id'] == str(student_user['_id'])
    assert enrollment['course_id'] == course_id
    
    # Verify initial state
    assert enrollment['progress'] == 0
    assert enrollment['completed_materials'] == []
    assert enrollment['is_active'] == True
    
    # Cleanup
    db.courses.delete_one({'_id': course_data['_id']})
    db.enrollments.delete_one({'_id': enrollment['_id']})


def test_unauthorized_access_rejection_integration(client, db, student_user, student_token, teacher_user):
    """
    Integration test for Property 32: Unauthorized course access rejection
    
    Verifies that unenrolled students receive 403 Forbidden when attempting
    to access course materials.
    """
    # Create a test course
    course_data = {
        '_id': ObjectId(),
        'title': 'Test Course for Access Control',
        'description': 'Test course description',
        'teacher_id': str(teacher_user['_id']),
        'category': 'Technology',
        'difficulty': 'Beginner',
        'is_active': True,
        'is_public': True,
        'created_at': datetime.utcnow()
    }
    db.courses.insert_one(course_data)
    course_id = str(course_data['_id'])
    
    # Create a test video
    video_data = {
        '_id': ObjectId(),
        'filename': 'test_video.mp4',
        'original_filename': 'test_video.mp4',
        'file_path': '/backend/uploads/videos/test_video.mp4',
        'file_size': 1024,
        'mime_type': 'video/mp4',
        'uploaded_by': str(teacher_user['_id']),
        'created_at': datetime.utcnow()
    }
    db.videos.insert_one(video_data)
    video_id = str(video_data['_id'])
    
    # Create a material linking the video to the course
    material_data = {
        '_id': ObjectId(),
        'course_id': course_id,
        'title': 'Test Video Material',
        'type': 'video',
        'content': video_id,
        'order': 1,
        'created_at': datetime.utcnow()
    }
    db.materials.insert_one(material_data)
    
    # Attempt to access video without enrollment
    response = client.get(
        f'/api/videos/{video_id}/stream',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    assert response.status_code == 403
    
    # Cleanup
    db.courses.delete_one({'_id': course_data['_id']})
    db.videos.delete_one({'_id': video_data['_id']})
    db.materials.delete_one({'_id': material_data['_id']})


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
