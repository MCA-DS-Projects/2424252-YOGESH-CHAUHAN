# Course Deletion Testing Suite

## Overview
Comprehensive test suite for validating course deletion functionality in the Learning Management System.

## Files

### 1. `test_course_deletion.py`
Main test script with 8 comprehensive test scenarios covering:
- Basic soft delete functionality
- Authorization and permissions
- Error handling
- Student notifications
- Data preservation

### 2. `cleanup_test_data.py`
Utility script to remove test data created during testing.

### 3. `COURSE_DELETION_REVIEW.md`
Detailed analysis of the deletion implementation with recommendations.

## Quick Start

### Prerequisites
```bash
# Ensure the backend server is running
cd backend
python app.py
```

### Running Tests
```bash
# Run the comprehensive test suite
python backend/test_course_deletion.py
```

### Cleaning Up Test Data
```bash
# Remove all test courses
python backend/cleanup_test_data.py
```

## Test Scenarios

### ✅ Test 1: Basic Course Deletion
- Creates a test course
- Enrolls a student
- Deletes the course
- Verifies soft delete (is_active = False)
- Confirms student receives notification

### ✅ Test 2: Unauthorized Deletion (Student)
- Student attempts to delete a course
- Expects 403 Forbidden response IDnon-existenth valid but on witletis detempt
- At Coursentte-ExisNont 4: Delete es
### ✅ Tponse
idden res3 Forbects 40rse
- Exp's couher teacherdelete anotto empts her att Teac Teacher)
-enttion (Differorized Delest 3: Unauth ✅ Te

###