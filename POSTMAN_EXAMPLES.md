# API Testing Examples - Postman/cURL

## Authentication

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "password": "password123"
  }'

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "user_123",
    "email": "teacher@example.com",
    "role": "teacher"
  }
}
```

---

## Courses API

### Get All Courses (Student)
```bash
curl -X GET http://localhost:5000/api/courses \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "courses": [
    {
      "id": "course_123",
      "title": "Introduction to Python",
      "description": "Learn Python basics",
      "instructor": "John Doe",
      "progress": 45,
      "totalLessons": 20,
      "completedLessons": 9
    }
  ]
}
```

### Get Teacher Courses
```bash
curl -X GET http://localhost:5000/api/teacher/courses \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN"

# Response:
{
  "courses": [
    {
      "_id": "course_123",
      "title": "Introduction to Python",
      "enrolled_students": 25,
      "total_assignments": 5,
      "is_active": true
    }
  ]
}
```

### Create Course (Teacher Only)
```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced JavaScript",
    "description": "Deep dive into JS",
    "category": "Programming",
    "difficulty": "Advanced",
    "max_students": 30,
    "modules": [
      {
        "title": "Module 1",
        "lessons": [
          {
            "title": "Lesson 1",
            "type": "video",
            "content": "video_url",
            "duration": "15 min"
          }
        ]
      }
    ]
  }'

# Response:
{
  "id": "course_456",
  "title": "Advanced JavaScript",
  "teacher_id": "user_123",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Update Course (Teacher Only - Own Courses)
```bash
curl -X PUT http://localhost:5000/api/courses/course_123 \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Course Title",
    "description": "Updated description"
  }'

# Success Response (200):
{
  "id": "course_123",
  "title": "Updated Course Title",
  "updated_at": "2024-01-15T11:00:00Z"
}

# Error Response (403) - Not your course:
{
  "error": "Unauthorized: You are not the instructor of this course"
}
```

### Delete Course (Teacher Only - Own Courses)
```bash
curl -X DELETE http://localhost:5000/api/courses/course_123 \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN"

# Success Response (200):
{
  "message": "Course deleted successfully"
}

# Error Response (403):
{
  "error": "Unauthorized: You are not the instructor of this course"
}
```

---

## Assignments API

### Get All Assignments
```bash
curl -X GET http://localhost:5000/api/assignments \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "assignments": [
    {
      "id": "assignment_123",
      "title": "Python Basics Quiz",
      "course_id": "course_123",
      "course_title": "Introduction to Python",
      "due_date": "2024-01-20T23:59:59Z",
      "max_points": 100,
      "status": "pending"
    }
  ]
}
```

### Create Assignment (Teacher Only)
```bash
curl -X POST http://localhost:5000/api/assignments \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "course_123",
    "title": "Week 1 Assignment",
    "description": "Complete the exercises",
    "due_date": "2024-01-25T23:59:59Z",
    "max_points": 100,
    "instructions": "Submit your code"
  }'

# Response:
{
  "id": "assignment_456",
  "title": "Week 1 Assignment",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Update Assignment (Teacher Only - Own Course)
```bash
curl -X PUT http://localhost:5000/api/assignments/assignment_123 \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Assignment Title",
    "due_date": "2024-01-30T23:59:59Z",
    "max_points": 150
  }'

# Success Response (200):
{
  "id": "assignment_123",
  "title": "Updated Assignment Title",
  "due_date": "2024-01-30T23:59:59Z",
  "updated_at": "2024-01-15T11:30:00Z"
}

# Error Response (403):
{
  "error": "Unauthorized: You are not the instructor of this course"
}
```

### Delete Assignment (Teacher Only - Own Course)
```bash
curl -X DELETE http://localhost:5000/api/assignments/assignment_123 \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN"

# Success Response (200):
{
  "message": "Assignment deleted successfully",
  "archived_submissions": 15
}

# Error Response (403):
{
  "error": "Unauthorized: You are not the instructor of this course"
}
```

### Submit Assignment (Student)
```bash
curl -X POST http://localhost:5000/api/assignments/assignment_123/submit \
  -H "Authorization: Bearer YOUR_STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "submission_text": "My solution...",
    "file_url": "https://storage.example.com/file.pdf"
  }'

# Response:
{
  "submission_id": "sub_789",
  "status": "submitted",
  "submitted_at": "2024-01-15T12:00:00Z"
}
```

---

## Notifications API

### Get Unread Count (Optimized)
```bash
curl -X GET http://localhost:5000/api/notifications/unread-count \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response (Fast - from cache):
{
  "count": 5
}

# Response Time: < 100ms
# Cache TTL: 10 seconds
```

### Get All Notifications
```bash
curl -X GET "http://localhost:5000/api/notifications?unread_only=false&limit=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "notifications": [
    {
      "id": "notif_123",
      "type": "assignment_graded",
      "message": "Your assignment has been graded",
      "read": false,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 20,
  "unread_count": 5
}
```

### Mark as Read
```bash
curl -X POST http://localhost:5000/api/notifications/notif_123/read \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "message": "Notification marked as read"
}
```

### Mark All as Read
```bash
curl -X POST http://localhost:5000/api/notifications/read-all \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "message": "All notifications marked as read",
  "count": 5
}
```

---

## Analytics API

### Get Student Analytics
```bash
curl -X GET http://localhost:5000/api/analytics/student/user_123 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "total_study_time": 124.5,
  "completion_rate": 87,
  "average_grade": "A-",
  "learning_streak": 15,
  "weekly_progress": [
    {"day": "Mon", "hours": 2.5, "completed": 3},
    {"day": "Tue", "hours": 3.2, "completed": 4}
  ],
  "subject_performance": [
    {"subject": "Python", "progress": 85, "grade": "A-"}
  ]
}
```

### Get Teacher Dashboard Stats
```bash
curl -X GET http://localhost:5000/api/teacher/dashboard \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN"

# Response:
{
  "active_courses": 5,
  "total_students": 125,
  "pending_grades": 23,
  "course_rating": 4.5,
  "monthly_growth": {
    "courses": 2,
    "students": 15,
    "rating_change": 0.3
  }
}
```

---

## Achievements API

### Get User Achievements
```bash
curl -X GET http://localhost:5000/api/achievements \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "achievements": [
    {
      "id": "ach_123",
      "title": "First Steps",
      "description": "Complete your first lesson",
      "category": "learning",
      "rarity": "common",
      "points": 10,
      "icon": "🎯",
      "unlocked_at": "2024-01-10T15:30:00Z",
      "progress": {
        "current": 1,
        "total": 1
      }
    },
    {
      "id": "ach_456",
      "title": "Assignment Master",
      "description": "Complete 10 assignments",
      "category": "performance",
      "rarity": "rare",
      "points": 50,
      "icon": "🏆",
      "unlocked_at": null,
      "progress": {
        "current": 7,
        "total": 10
      }
    }
  ]
}
```

---

## AI Features API

### Get Recommendations
```bash
curl -X GET http://localhost:5000/api/ai/recommendations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "course_recommendations": [
    {
      "title": "Advanced Python",
      "description": "Take your Python skills to the next level",
      "reason": "Based on your progress in Python Basics"
    }
  ],
  "study_tips": [
    "Create a consistent daily study schedule",
    "Use active recall techniques"
  ],
  "performance_summary": {
    "strong_areas": ["Python", "Data Structures"],
    "weak_areas": ["Algorithms"],
    "total_points": 450
  }
}
```

### Generate Learning Path
```bash
curl -X POST http://localhost:5000/api/ai/learning-path \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Become a full-stack developer",
    "timeframe": "6 months"
  }'

# Response:
{
  "learning_path": {
    "goal": "Become a full-stack developer",
    "timeframe": "6 months",
    "learning_path": "### Month 1-2: Frontend Basics\n- HTML/CSS\n- JavaScript\n\n### Month 3-4: Backend\n- Node.js\n- Databases"
  }
}
```

### Chat with AI
```bash
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How can I improve my Python skills?"
  }'

# Response:
{
  "response": "Here are some ways to improve your Python skills:\n1. Practice coding daily\n2. Work on real projects\n3. Read Python documentation"
}
```

---

## Testing Permission Scenarios

### Scenario 1: Teacher tries to edit another teacher's course
```bash
# Login as Teacher A
TOKEN_A=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "teacherA@example.com", "password": "pass123"}' \
  | jq -r '.access_token')

# Try to edit Teacher B's course
curl -X PUT http://localhost:5000/api/courses/teacher_b_course_id \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"title": "Hacked Title"}'

# Expected: 403 Forbidden
{
  "error": "Unauthorized: You are not the instructor of this course"
}
```

### Scenario 2: Student tries to delete assignment
```bash
# Login as Student
TOKEN_STUDENT=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "student@example.com", "password": "pass123"}' \
  | jq -r '.access_token')

# Try to delete assignment
curl -X DELETE http://localhost:5000/api/assignments/assignment_123 \
  -H "Authorization: Bearer $TOKEN_STUDENT"

# Expected: 403 Forbidden
{
  "error": "Unauthorized: Only teachers can delete assignments"
}
```

---

## Performance Testing

### Test Notification Polling
```bash
# Run 100 requests and measure response time
for i in {1..100}; do
  curl -w "@curl-format.txt" -o /dev/null -s \
    -X GET http://localhost:5000/api/notifications/unread-count \
    -H "Authorization: Bearer YOUR_TOKEN"
done

# curl-format.txt:
time_total: %{time_total}s\n

# Expected: All requests < 100ms
```

### Test Concurrent Requests
```bash
# Use Apache Bench
ab -n 1000 -c 10 -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/notifications/unread-count

# Expected Results:
# - Requests per second: > 100
# - Mean response time: < 100ms
# - No failed requests
```

---

## Monitoring Endpoints

### Health Check
```bash
curl -X GET http://localhost:5000/api/health

# Response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

### Metrics (Prometheus)
```bash
curl -X GET http://localhost:5000/metrics

# Response (Prometheus format):
# HELP notification_polls_total Total notification polls
# TYPE notification_polls_total counter
notification_polls_total{user_id="user_123"} 150

# HELP gemini_request_duration_seconds Gemini API request duration
# TYPE gemini_request_duration_seconds histogram
gemini_request_duration_seconds_bucket{le="1.0"} 45
gemini_request_duration_seconds_bucket{le="5.0"} 98
```

---

## Error Scenarios

### 401 Unauthorized
```bash
curl -X GET http://localhost:5000/api/courses

# Response:
{
  "error": "Missing Authorization Header"
}
```

### 403 Forbidden
```bash
curl -X DELETE http://localhost:5000/api/courses/other_teacher_course \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response:
{
  "error": "Unauthorized: You are not the instructor of this course"
}
```

### 404 Not Found
```bash
curl -X GET http://localhost:5000/api/courses/nonexistent_id \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response:
{
  "error": "Course not found"
}
```

### 429 Rate Limit
```bash
# After too many requests
curl -X GET http://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response:
{
  "error": "Rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

### 500 Server Error
```bash
# When Gemini API fails
curl -X POST http://localhost:5000/api/ai/learning-path \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Learn AI", "timeframe": "month"}'

# Response (with circuit breaker):
{
  "error": "AI service temporarily unavailable",
  "fallback": "Please try again later or check your learning dashboard for recommendations"
}
```
