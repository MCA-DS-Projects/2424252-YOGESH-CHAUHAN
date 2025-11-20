# Progress Tracking System Implementation

## Overview
This document describes the implementation of the progress tracking system for the EduNexa LMS, which tracks student progress through courses.

## Database Schema

### Progress Collection
```javascript
{
  _id: ObjectId,
  course_id: String,           // Course ID
  student_id: String,          // Student user ID
  started: Boolean,            // Whether student has started the course
  last_accessed: DateTime,     // Last time student accessed the course
  completed_materials: Array,  // Array of completed material IDs
  overall_progress: Number,    // Overall progress percentage (0-100)
  created_at: DateTime,        // When progress record was created
  updated_at: DateTime         // When progress record was last updated
}
```

### Indexes
- Compound unique index on `(student_id, course_id)` - ensures one progress record per student per course
- Index on `course_id` - for querying all students' progress in a course
- Index on `student_id` - for querying all courses a student has progress in

## API Endpoints

### GET /api/progress/course/<course_id>
Retrieves the student's progress for a specific course.

**Authentication:** Required (JWT token)

**Authorization:** Student role only

**Response:**
```json
{
  "progress": {
    "course_id": "string",
    "student_id": "string",
    "started": false,
    "last_accessed": null,
    "overall_progress": 0,
    "completed_materials": []
  }
}
```

**Behavior:**
- If no progress record exists, returns default state with `started: false`
- If progress record exists, returns the actual progress data

### POST /api/progress/course/<course_id>/start
Initializes or updates progress tracking when a student first accesses a course.

**Authentication:** Required (JWT token)

**Authorization:** Student role only, must be enrolled in the course

**Response (201 Created - new record):**
```json
{
  "message": "Progress initialized",
  "progress": {
    "course_id": "string",
    "student_id": "string",
    "started": true,
    "last_accessed": "2024-01-01T00:00:00"
  }
}
```

**Response (200 OK - existing record updated):**
```json
{
  "message": "Progress updated",
  "progress": {
    "course_id": "string",
    "student_id": "string",
    "started": true,
    "last_accessed": "2024-01-01T00:00:00"
  }
}
```

**Behavior:**
- Checks if student is enrolled in the course
- Creates new progress record if none exists
- Updates `started` to `true` and `last_accessed` timestamp if record exists
- Returns appropriate status code (201 for new, 200 for update)

## Error Handling

### Common Errors

**403 Forbidden:**
- User is not a student
- Student is not enrolled in the course

**404 Not Found:**
- Course does not exist

**500 Internal Server Error:**
- Database connection issues
- Unexpected server errors

## Usage Flow

### Student Dashboard - Start/Continue Button Logic

1. **Fetch Progress State:**
   ```javascript
   GET /api/progress/course/{courseId}
   ```

2. **Determine Button Text:**
   - If `progress.started === false`: Show "Start" button
   - If `progress.started === true`: Show "Continue" button

3. **On Button Click:**
   ```javascript
   POST /api/progress/course/{courseId}/start
   ```
   Then navigate to course detail page

### Course Detail Page - Initialize Progress

When a student visits a course detail page for the first time:

```javascript
POST /api/progress/course/{courseId}/start
```

This ensures the progress record is created and `last_accessed` is updated.

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 2.5:** Progress state determines button (Start/Continue)
- **Requirement 2.6:** Progress record creation on first access
- **Requirement 2.7:** Last accessed timestamp updates

## Testing

Run the test script to verify the implementation:

```bash
python Tests/test_progress_tracking.py
```

**Prerequisites:**
- Backend server must be running
- Test student account must exist and be enrolled in at least one course

## Future Enhancements

- Track individual material completion
- Calculate overall progress percentage based on completed materials
- Add video watch time tracking
- Add assignment completion tracking
- Generate progress reports for teachers
