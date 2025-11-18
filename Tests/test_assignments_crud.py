"""
Unit tests for Assignment CRUD operations
Tests delete, update, and permission checks
"""

import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from bson import ObjectId
from datetime import datetime, timedelta


class TestAssignmentDelete:
    """Test assignment deletion functionality"""
    
    def test_teacher_can_delete_own_assignment(self, client, db, teacher_user, teacher_token):
        """Teacher can delete their own assignment"""
        # Create a course owned by teacher
        course = {
            '_id': ObjectId(),
            'title': 'Test Course',
            'teacher_id': str(teacher_user['_id']),
            'is_active': True
        }
        db.courses.insert_one(course)
        
        # Create assignment
        assignment = {
            '_id': ObjectId(),
            'title': 'Test Assignment',
            'description': 'Test Description',
            'course_id': str(course['_id']),
            'due_date': (datetime.utcnow() + timedelta(days=7)).isoformat(),
            'max_points': 100,
            'created_by': str(teacher_user['_id']),
            'is_active': True
        }
        db.assignments.insert_one(assignment)
        
        # Delete assignment
        response = client.delete(
            f'/api/assignments/{assignment["_id"]}',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.json['message'].lower()
        
        # Verify assignment deleted from database
        deleted = db.assignments.find_one({'_id': assignment['_id']})
        assert deleted is None
    
    def test_teacher_cannot_delete_other_teacher_assignment(self, client, db, teacher_user, teacher_token):
        """Teacher cannot delete another teacher's assignment"""
        # Create another teacher
        other_teacher = {
            '_id': ObjectId(),
            'name': 'Other Teacher',
            'email': 'other@teacher.com',
            'role': 'teacher'
        }
        db.users.insert_one(other_teacher)
        
        # Create course owned by other teacher
        course = {
            '_id': ObjectId(),
            'title': 'Other Course',
            'teacher_id': str(other_teacher['_id']),
            'is_active': True
        }
        db.courses.insert_one(course)
        
        # Create assignment
        assignment = {
            '_id': ObjectId(),
            'title': 'Other Assignment',
            'course_id': str(course['_id']),
            'created_by': str(other_teacher['_id'])
        }
        db.assignments.insert_one(assignment)
        
        # Try to delete
        response = client.delete(
            f'/api/assignments/{assignment["_id"]}',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert response.status_code == 403
        assert 'access denied' in response.json['error'].lower()
        
        # Verify assignment still exists
        exists = db.assignments.find_one({'_id': assignment['_id']})
        assert exists is not None
    
    def test_student_cannot_delete_assignment(self, client, db, student_user, student_token):
        """Student cannot delete any assignment"""
        # Create assignment
        assignment = {
            '_id': ObjectId(),
            'title': 'Test Assignment',
            'course_id': str(ObjectId())
        }
        db.assignments.insert_one(assignment)
        
        # Try to delete
        response = client.delete(
            f'/api/assignments/{assignment["_id"]}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        assert response.status_code == 403
        
        # Verify assignment still exists
        exists = db.assignments.find_one({'_id': assignment['_id']})
        assert exists is not None
    
    def test_admin_can_delete_any_assignment(self, client, db, admin_user, admin_token):
        """Admin can delete any assignment"""
        # Create assignment
        assignment = {
            '_id': ObjectId(),
            'title': 'Test Assignment',
            'course_id': str(ObjectId()),
            'created_by': str(ObjectId())  # Different user
        }
        db.assignments.insert_one(assignment)
        
        # Delete as admin
        response = client.delete(
            f'/api/assignments/{assignment["_id"]}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        
        # Verify deleted
        deleted = db.assignments.find_one({'_id': assignment['_id']})
        assert deleted is None
    
    def test_delete_removes_related_submissions(self, client, db, teacher_user, teacher_token):
        """Deleting assignment removes related submissions"""
        # Create course and assignment
        course = {
            '_id': ObjectId(),
            'title': 'Test Course',
            'teacher_id': str(teacher_user['_id'])
        }
        db.courses.insert_one(course)
        
        assignment = {
            '_id': ObjectId(),
            'title': 'Test Assignment',
            'course_id': str(course['_id']),
            'created_by': str(teacher_user['_id'])
        }
        db.assignments.insert_one(assignment)
        
        # Create submissions
        submission1 = {
            '_id': ObjectId(),
            'assignment_id': str(assignment['_id']),
            'student_id': str(ObjectId()),
            'text_content': 'Test submission 1'
        }
        submission2 = {
            '_id': ObjectId(),
            'assignment_id': str(assignment['_id']),
            'student_id': str(ObjectId()),
            'text_content': 'Test submission 2'
        }
        db.submissions.insert_many([submission1, submission2])
        
        # Verify submissions exist
        count_before = db.submissions.count_documents({'assignment_id': str(assignment['_id'])})
        assert count_before == 2
        
        # Delete assignment
        response = client.delete(
            f'/api/assignments/{assignment["_id"]}',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert response.status_code == 200
        
        # Verify submissions deleted
        count_after = db.submissions.count_documents({'assignment_id': str(assignment['_id'])})
        assert count_after == 0
    
    def test_delete_nonexistent_assignment_returns_404(self, client, teacher_token):
        """Deleting non-existent assignment returns 404"""
        fake_id = str(ObjectId())
        
        response = client.delete(
            f'/api/assignments/{fake_id}',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert response.status_code == 404
        assert 'not found' in response.json['error'].lower()


class TestAssignmentUpdate:
    """Test assignment update functionality"""
    
    def test_teacher_can_update_own_assignment(self, client, db, teacher_user, teacher_token):
        """Teacher can update their own assignment"""
        # Create course and assignment
        course = {
            '_id': ObjectId(),
            'title': 'Test Course',
            'teacher_id': str(teacher_user['_id'])
        }
        db.courses.insert_one(course)
        
        assignment = {
            '_id': ObjectId(),
            'title': 'Original Title',
            'description': 'Original Description',
            'course_id': str(course['_id']),
            'max_points': 100,
            'created_by': str(teacher_user['_id'])
        }
        db.assignments.insert_one(assignment)
        
        # Update assignment
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'max_points': 150
        }
        
        response = client.put(
            f'/api/assignments/{assignment["_id"]}',
            json=update_data,
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert response.status_code == 200
        assert response.json['assignment']['title'] == 'Updated Title'
        assert response.json['assignment']['description'] == 'Updated Description'
        assert response.json['assignment']['max_points'] == 150
        
        # Verify in database
        updated = db.assignments.find_one({'_id': assignment['_id']})
        assert updated['title'] == 'Updated Title'
        assert updated['max_points'] == 150
    
    def test_teacher_cannot_update_other_teacher_assignment(self, client, db, teacher_user, teacher_token):
        """Teacher cannot update another teacher's assignment"""
        # Create other teacher and their assignment
        other_teacher = {
            '_id': ObjectId(),
            'name': 'Other Teacher',
            'role': 'teacher'
        }
        db.users.insert_one(other_teacher)
        
        course = {
            '_id': ObjectId(),
            'teacher_id': str(other_teacher['_id'])
        }
        db.courses.insert_one(course)
        
        assignment = {
            '_id': ObjectId(),
            'title': 'Original',
            'course_id': str(course['_id']),
            'created_by': str(other_teacher['_id'])
        }
        db.assignments.insert_one(assignment)
        
        # Try to update
        response = client.put(
            f'/api/assignments/{assignment["_id"]}',
            json={'title': 'Hacked'},
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert response.status_code == 403
        
        # Verify not updated
        unchanged = db.assignments.find_one({'_id': assignment['_id']})
        assert unchanged['title'] == 'Original'
    
    def test_update_validates_max_points(self, client, db, teacher_user, teacher_token):
        """Update validates max_points is positive"""
        # Create assignment
        course = {
            '_id': ObjectId(),
            'teacher_id': str(teacher_user['_id'])
        }
        db.courses.insert_one(course)
        
        assignment = {
            '_id': ObjectId(),
            'title': 'Test',
            'course_id': str(course['_id']),
            'max_points': 100,
            'created_by': str(teacher_user['_id'])
        }
        db.assignments.insert_one(assignment)
        
        # Try invalid update
        response = client.put(
            f'/api/assignments/{assignment["_id"]}',
            json={'max_points': -10},
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert response.status_code == 400
        
        # Verify not updated
        unchanged = db.assignments.find_one({'_id': assignment['_id']})
        assert unchanged['max_points'] == 100
    
    def test_update_validates_due_date_format(self, client, db, teacher_user, teacher_token):
        """Update validates due_date is valid ISO format"""
        # Create assignment
        course = {
            '_id': ObjectId(),
            'teacher_id': str(teacher_user['_id'])
        }
        db.courses.insert_one(course)
        
        assignment = {
            '_id': ObjectId(),
            'title': 'Test',
            'course_id': str(course['_id']),
            'due_date': datetime.utcnow().isoformat(),
            'created_by': str(teacher_user['_id'])
        }
        db.assignments.insert_one(assignment)
        
        # Try invalid date
        response = client.put(
            f'/api/assignments/{assignment["_id"]}',
            json={'due_date': 'invalid-date'},
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert response.status_code == 400


class TestAssignmentPermissions:
    """Test permission checks for assignment operations"""
    
    def test_unauthenticated_cannot_access(self, client, db):
        """Unauthenticated users cannot access assignment endpoints"""
        assignment_id = str(ObjectId())
        
        # Try without token
        response = client.delete(f'/api/assignments/{assignment_id}')
        assert response.status_code == 401
        
        response = client.put(f'/api/assignments/{assignment_id}', json={})
        assert response.status_code == 401
    
    def test_student_cannot_create_assignment(self, client, student_token):
        """Students cannot create assignments"""
        response = client.post(
            '/api/assignments/',
            json={
                'title': 'Test',
                'description': 'Test',
                'course_id': str(ObjectId()),
                'due_date': datetime.utcnow().isoformat()
            },
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        assert response.status_code == 403
    
    def test_student_cannot_update_assignment(self, client, db, student_token):
        """Students cannot update assignments"""
        assignment = {
            '_id': ObjectId(),
            'title': 'Test'
        }
        db.assignments.insert_one(assignment)
        
        response = client.put(
            f'/api/assignments/{assignment["_id"]}',
            json={'title': 'Hacked'},
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        assert response.status_code == 403


# Pytest fixtures
@pytest.fixture
def teacher_user(db):
    """Create a teacher user"""
    user = {
        '_id': ObjectId(),
        'name': 'Test Teacher',
        'email': 'teacher@test.com',
        'role': 'teacher'
    }
    db.users.insert_one(user)
    return user


@pytest.fixture
def teacher_token(teacher_user):
    """Create JWT token for teacher"""
    return create_access_token(identity=str(teacher_user['_id']))


@pytest.fixture
def student_user(db):
    """Create a student user"""
    user = {
        '_id': ObjectId(),
        'name': 'Test Student',
        'email': 'student@test.com',
        'role': 'student'
    }
    db.users.insert_one(user)
    return user


@pytest.fixture
def student_token(student_user):
    """Create JWT token for student"""
    return create_access_token(identity=str(student_user['_id']))


@pytest.fixture
def admin_user(db):
    """Create an admin user"""
    user = {
        '_id': ObjectId(),
        'name': 'Test Admin',
        'email': 'admin@test.com',
        'role': 'admin'
    }
    db.users.insert_one(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    """Create JWT token for admin"""
    return create_access_token(identity=str(admin_user['_id']))
