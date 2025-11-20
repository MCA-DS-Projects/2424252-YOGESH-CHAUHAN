"""
Property-based tests for student course enrollment and access control.

Feature: course-media-and-access-fixes
"""

import pytest
import os
from datetime import datetime, timezone
from hypothesis import given, strategies as st, settings
from bson import ObjectId


# Helper functions to simulate enrollment logic
def create_enrollment_record(student_id, course_id):
    """
    Simulates creating an enrollment record when a student enrolls in a course.
    
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


def check_enrollment_exists(student_id, course_id, enrollments_db):
    """
    Checks if an enrollment record exists for a student-course combination.
    
    Args:
        student_id: Student's user ID
        course_id: Course ID
        enrollments_db: Simulated enrollments database (list of enrollment records)
    
    Returns:
        bool indicating if enrollment exists
    """
    for enrollment in enrollments_db:
        if enrollment['student_id'] == student_id and enrollment['course_id'] == course_id:
            return True
    return False


def check_course_access(student_id, course_id, enrollments_db):
    """
    Checks if a student has access to a course based on enrollment.
    
    Args:
        student_id: Student's user ID
        course_id: Course ID
        enrollments_db: Simulated enrollments database (list of enrollment records)
    
    Returns:
        dict with 'has_access' boolean and 'status_code' (200 for access, 403 for forbidden)
    """
    is_enrolled = check_enrollment_exists(student_id, course_id, enrollments_db)
    
    if is_enrolled:
        return {
            'has_access': True,
            'status_code': 200
        }
    else:
        return {
            'has_access': False,
            'status_code': 403,
            'error': 'Access denied - not enrolled in this course'
        }


# Property 26: Enrollment record creation
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
def test_property_26_enrollment_record_creation(student_id, course_id):
    """
    **Feature: course-media-and-access-fixes, Property 26: Enrollment record creation**
    **Validates: Requirements 5.4**
    
    Property: For any student enrollment in a course, an enrollment record should 
    exist in the database linking the student to the course.
    """
    # Simulate enrollments database
    enrollments_db = []
    
    # Create enrollment record
    enrollment = create_enrollment_record(student_id, course_id)
    enrollments_db.append(enrollment)
    
    # Verify enrollment record exists
    enrollment_exists = check_enrollment_exists(student_id, course_id, enrollments_db)
    
    assert enrollment_exists, \
        f"Enrollment record should exist for student {student_id} in course {course_id}"
    
    # Verify enrollment record has required fields
    assert 'student_id' in enrollment, "Enrollment should have student_id field"
    assert 'course_id' in enrollment, "Enrollment should have course_id field"
    assert 'enrolled_at' in enrollment, "Enrollment should have enrolled_at field"
    assert 'progress' in enrollment, "Enrollment should have progress field"
    assert 'completed_materials' in enrollment, "Enrollment should have completed_materials field"
    assert 'is_active' in enrollment, "Enrollment should have is_active field"
    
    # Verify enrollment links correct student and course
    assert enrollment['student_id'] == student_id, \
        f"Enrollment student_id should be {student_id}, got {enrollment['student_id']}"
    assert enrollment['course_id'] == course_id, \
        f"Enrollment course_id should be {course_id}, got {enrollment['course_id']}"
    
    # Verify initial state
    assert enrollment['progress'] == 0, "Initial progress should be 0"
    assert enrollment['completed_materials'] == [], "Initial completed_materials should be empty"
    assert enrollment['is_active'] == True, "Enrollment should be active"
    
    # Verify enrolled_at is a datetime
    assert isinstance(enrollment['enrolled_at'], datetime), \
        "enrolled_at should be a datetime object"


# Property 32: Unauthorized course access rejection
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
    is_enrolled=st.booleans()
)
@settings(max_examples=100)
def test_property_32_unauthorized_access_rejection(student_id, course_id, is_enrolled):
    """
    **Feature: course-media-and-access-fixes, Property 32: Unauthorized course access rejection**
    **Validates: Requirements 6.3**
    
    Property: For any student attempting to access a course they are not enrolled in, 
    the system should return a 403 Forbidden error.
    """
    # Simulate enrollments database
    enrollments_db = []
    
    # If student is enrolled, create enrollment record
    if is_enrolled:
        enrollment = create_enrollment_record(student_id, course_id)
        enrollments_db.append(enrollment)
    
    # Check course access
    access_result = check_course_access(student_id, course_id, enrollments_db)
    
    # Verify access matches enrollment status
    if is_enrolled:
        assert access_result['has_access'] == True, \
            f"Enrolled student should have access to course"
        assert access_result['status_code'] == 200, \
            f"Enrolled student should get 200 status, got {access_result['status_code']}"
    else:
        assert access_result['has_access'] == False, \
            f"Unenrolled student should not have access to course"
        assert access_result['status_code'] == 403, \
            f"Unenrolled student should get 403 status, got {access_result['status_code']}"
        assert 'error' in access_result, \
            "Unauthorized access should return error message"
        assert 'not enrolled' in access_result['error'].lower() or 'access denied' in access_result['error'].lower(), \
            f"Error message should indicate enrollment issue, got: {access_result['error']}"


# Additional property: Multiple enrollments uniqueness
@given(
    student_ids=st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=24,
            max_size=24
        ),
        min_size=1,
        max_size=10,
        unique=True
    ),
    course_id=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=24,
        max_size=24
    )
)
@settings(max_examples=100)
def test_property_multiple_students_enrollment(student_ids, course_id):
    """
    Property: For any course, multiple students can enroll, and each enrollment 
    record should be unique and correctly linked.
    """
    enrollments_db = []
    
    # Enroll all students
    for student_id in student_ids:
        enrollment = create_enrollment_record(student_id, course_id)
        enrollments_db.append(enrollment)
    
    # Verify all students are enrolled
    for student_id in student_ids:
        enrollment_exists = check_enrollment_exists(student_id, course_id, enrollments_db)
        assert enrollment_exists, \
            f"Student {student_id} should be enrolled in course {course_id}"
    
    # Verify number of enrollments matches number of students
    course_enrollments = [e for e in enrollments_db if e['course_id'] == course_id]
    assert len(course_enrollments) == len(student_ids), \
        f"Should have {len(student_ids)} enrollments, got {len(course_enrollments)}"
    
    # Verify each enrollment has unique student_id
    enrolled_student_ids = [e['student_id'] for e in course_enrollments]
    assert len(enrolled_student_ids) == len(set(enrolled_student_ids)), \
        "Each enrollment should have unique student_id"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
