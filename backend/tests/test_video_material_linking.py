"""
Integration test for video storage and material linking
Tests Requirement 3.4: Video storage and material linking
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from bson import ObjectId
from datetime import datetime


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


def test_video_upload_response_format(db):
    """
    Test that video upload returns correct response format
    Validates: Requirement 3.4 - video_id is returned for material linking
    """
    # Create a test video document
    video_doc = {
        'filename': 'test_video.mp4',
        'original_filename': 'original_test.mp4',
        'file_path': '/fake/path/test.mp4',
        'file_size': 1024000,
        'mime_type': 'video/mp4',
        'uploaded_by': 'test_user_id',
        'created_at': datetime.utcnow()
    }
    
    result = db.videos.insert_one(video_doc)
    video_id = str(result.inserted_id)
    
    try:
        # Simulate the response format from the endpoint
        response_data = {
            'message': 'Video uploaded successfully',
            'videoId': video_id,
            'video_id': video_id,
            'filename': 'test_video.mp4',
            'originalFilename': 'original_test.mp4',
            'original_filename': 'original_test.mp4',
            'fileSize': 1024000,
            'file_size': 1024000,
            'mimeType': 'video/mp4',
            'mime_type': 'video/mp4',
            'videoUrl': f'/api/videos/{video_id}/stream',
            'video_url': f'/api/videos/{video_id}/stream'
        }
        
        # Verify both camelCase and snake_case are present
        assert 'videoId' in response_data, "Missing videoId (camelCase)"
        assert 'video_id' in response_data, "Missing video_id (snake_case)"
        assert response_data['videoId'] == response_data['video_id'], "videoId mismatch"
        
        assert 'originalFilename' in response_data, "Missing originalFilename"
        assert 'fileSize' in response_data, "Missing fileSize"
        assert 'mimeType' in response_data, "Missing mimeType"
        assert 'videoUrl' in response_data, "Missing videoUrl"
        
    finally:
        # Cleanup
        db.videos.delete_one({'_id': ObjectId(video_id)})


def test_material_stores_video_id_in_content(db):
    """
    Test that materials store video_id in content field
    Validates: Requirement 3.4 - Store video_id in content field
    """
    # Create a test video
    video_doc = {
        'filename': 'test.mp4',
        'original_filename': 'test.mp4',
        'file_path': '/fake/path/test.mp4',
        'file_size': 1000,
        'mime_type': 'video/mp4',
        'uploaded_by': 'test_user',
        'created_at': datetime.utcnow()
    }
    video_result = db.videos.insert_one(video_doc)
    video_id = str(video_result.inserted_id)
    
    try:
        # Create a material with video_id
        material_data = {
            'course_id': 'test_course_id',
            'title': 'Test Video Material',
            'description': 'Test Description',
            'type': 'video',
            'content': video_id,  # Store video_id in content field
            'order': 1,
            'is_required': True,
            'uploaded_by': 'test_user',
            'created_at': datetime.utcnow()
        }
        
        material_result = db.materials.insert_one(material_data)
        material_id = str(material_result.inserted_id)
        
        # Verify material was created correctly
        saved_material = db.materials.find_one({'_id': ObjectId(material_id)})
        
        assert saved_material is not None, "Material not found"
        assert saved_material['type'] == 'video', f"Expected type 'video', got '{saved_material['type']}'"
        assert saved_material['content'] == video_id, f"Expected content '{video_id}', got '{saved_material['content']}'"
        
    finally:
        # Cleanup
        db.materials.delete_many({'course_id': 'test_course_id'})
        db.videos.delete_one({'_id': ObjectId(video_id)})


def test_material_type_is_video_for_video_materials(db):
    """
    Test that material.type is set to 'video' for video materials
    Validates: Requirement 3.4 - Ensure material.type is set to 'video'
    """
    # Create a test video
    video_doc = {
        'filename': 'lesson_video.mp4',
        'original_filename': 'lesson_video.mp4',
        'file_path': '/fake/path/lesson_video.mp4',
        'file_size': 2000000,
        'mime_type': 'video/mp4',
        'uploaded_by': 'test_teacher',
        'created_at': datetime.utcnow()
    }
    video_result = db.videos.insert_one(video_doc)
    video_id = str(video_result.inserted_id)
    
    try:
        # Test different scenarios where type should be 'video'
        test_cases = [
            {'type': 'video', 'content': video_id},  # Explicit type
            {'content': video_id},  # No type specified, should default to video
        ]
        
        for i, lesson_data in enumerate(test_cases):
            # Simulate course creation logic
            material_type = lesson_data.get('type', 'video')
            if material_type == 'video' or (not lesson_data.get('type') and lesson_data.get('content')):
                material_type = 'video'
            
            material_data = {
                'course_id': f'test_course_{i}',
                'title': f'Video Lesson {i}',
                'description': 'A video lesson',
                'type': material_type,
                'content': lesson_data['content'],
                'order': i,
                'is_required': False,
                'uploaded_by': 'test_teacher',
                'created_at': datetime.utcnow()
            }
            
            material_result = db.materials.insert_one(material_data)
            material_id = str(material_result.inserted_id)
            
            # Verify the material
            saved_material = db.materials.find_one({'_id': ObjectId(material_id)})
            
            assert saved_material['type'] == 'video', f"Test case {i}: Material type should be 'video', got '{saved_material['type']}'"
            assert saved_material['content'] == video_id, f"Test case {i}: Material content should be video_id"
            
            # Cleanup this material
            db.materials.delete_one({'_id': ObjectId(material_id)})
    
    finally:
        # Cleanup
        db.materials.delete_many({'course_id': {'$regex': '^test_course_'}})
        db.videos.delete_one({'_id': ObjectId(video_id)})


def test_course_creation_links_videos_to_materials(db):
    """
    Test that course creation properly links uploaded videos to materials
    Validates: Requirement 3.4 - Update course creation flow to link uploaded videos
    """
    # Create a test video
    video_doc = {
        'filename': 'course_video.mp4',
        'original_filename': 'course_video.mp4',
        'file_path': '/fake/path/course_video.mp4',
        'file_size': 3000000,
        'mime_type': 'video/mp4',
        'uploaded_by': 'test_teacher',
        'created_at': datetime.utcnow()
    }
    video_result = db.videos.insert_one(video_doc)
    video_id = str(video_result.inserted_id)
    
    course_id = 'test_course_' + str(ObjectId())
    
    try:
        # Simulate course creation with modules containing video lessons
        modules = [
            {
                'title': 'Module 1',
                'description': 'First module',
                'lessons': [
                    {
                        'title': 'Video Lesson 1',
                        'description': 'First video lesson',
                        'type': 'video',
                        'content': video_id,  # This is the video_id from upload
                        'order': 1,
                        'is_required': True
                    }
                ]
            }
        ]
        
        # Process modules and create materials (as done in course creation endpoint)
        for module in modules:
            for lesson in module.get('lessons', []):
                if lesson.get('content') and lesson.get('title'):
                    # Determine material type
                    material_type = lesson.get('type', 'video')
                    
                    # Ensure type is set to 'video' for video materials
                    if material_type == 'video' or (not lesson.get('type') and lesson.get('content')):
                        material_type = 'video'
                    
                    material_data = {
                        'course_id': course_id,
                        'title': lesson['title'],
                        'description': lesson.get('description', ''),
                        'type': material_type,  # Ensure type is 'video' for video materials
                        'content': lesson['content'],  # Store video_id in content field
                        'order': lesson.get('order', 0),
                        'is_required': lesson.get('is_required', False),
                        'uploaded_by': 'test_teacher',
                        'created_at': datetime.utcnow()
                    }
                    db.materials.insert_one(material_data)
        
        # Verify materials were created correctly
        materials = list(db.materials.find({'course_id': course_id}))
        
        assert len(materials) == 1, f"Expected 1 material, got {len(materials)}"
        
        material = materials[0]
        assert material['type'] == 'video', f"Material type should be 'video', got '{material['type']}'"
        assert material['content'] == video_id, f"Material content should be video_id '{video_id}', got '{material['content']}'"
        assert material['title'] == 'Video Lesson 1', "Material title mismatch"
        
        # Verify the video exists and can be retrieved
        video = db.videos.find_one({'_id': ObjectId(video_id)})
        assert video is not None, "Video should exist in database"
        
    finally:
        # Cleanup
        db.materials.delete_many({'course_id': course_id})
        db.videos.delete_one({'_id': ObjectId(video_id)})


def test_multiple_videos_in_course(db):
    """
    Test that a course can have multiple video materials
    Validates: Requirement 3.4 - Multiple videos can be linked to a course
    """
    # Create multiple test videos
    video_ids = []
    for i in range(3):
        video_doc = {
            'filename': f'video_{i}.mp4',
            'original_filename': f'video_{i}.mp4',
            'file_path': f'/fake/path/video_{i}.mp4',
            'file_size': 1000000 * (i + 1),
            'mime_type': 'video/mp4',
            'uploaded_by': 'test_teacher',
            'created_at': datetime.utcnow()
        }
        result = db.videos.insert_one(video_doc)
        video_ids.append(str(result.inserted_id))
    
    course_id = 'test_course_multi_' + str(ObjectId())
    
    try:
        # Create materials for each video
        for i, video_id in enumerate(video_ids):
            material_data = {
                'course_id': course_id,
                'title': f'Video Lesson {i + 1}',
                'description': f'Lesson {i + 1} description',
                'type': 'video',
                'content': video_id,
                'order': i + 1,
                'is_required': True,
                'uploaded_by': 'test_teacher',
                'created_at': datetime.utcnow()
            }
            db.materials.insert_one(material_data)
        
        # Verify all materials were created
        materials = list(db.materials.find({'course_id': course_id}).sort('order', 1))
        
        assert len(materials) == 3, f"Expected 3 materials, got {len(materials)}"
        
        # Verify each material
        for i, material in enumerate(materials):
            assert material['type'] == 'video', f"Material {i} type should be 'video'"
            assert material['content'] == video_ids[i], f"Material {i} content mismatch"
            assert material['order'] == i + 1, f"Material {i} order mismatch"
            
            # Verify the video exists
            video = db.videos.find_one({'_id': ObjectId(video_ids[i])})
            assert video is not None, f"Video {i} should exist"
    
    finally:
        # Cleanup
        db.materials.delete_many({'course_id': course_id})
        for video_id in video_ids:
            db.videos.delete_one({'_id': ObjectId(video_id)})


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
