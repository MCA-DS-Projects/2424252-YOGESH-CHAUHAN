# Notification System - API Examples

## Authentication

All endpoints require JWT authentication. First, login to get a token:

```bash
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "student@test.com",
  "password": "YourPassword123!"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { ... }
}
```

Use the `access_token` in subsequent requests:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## User Endpoints

### 1. Get Notification Settings

**Request:**
```bash
GET http://localhost:5000/api/notification-settings
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "settings": {
    "email_enabled": true,
    "in_app_enabled": true
  },
  "message": "Notification settings retrieved successfully"
}
```

**cURL:**
```bash
curl -X GET http://localhost:5000/api/notification-settings \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. Update Notification Settings

**Request:**
```bash
PUT http://localhost:5000/api/notification-settings
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "email_enabled": false,
  "in_app_enabled": true
}
```

**Response:**
```json
{
  "message": "Notification settings updated successfully",
  "settings": {
    "email_enabled": false,
    "in_app_enabled": true
  }
}
```

**cURL:**
```bash
curl -X PUT http://localhost:5000/api/notification-settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_enabled":false,"in_app_enabled":true}'
```

---

### 3. Send Test Email

**Request:**
```bash
POST http://localhost:5000/api/notification-settings/test-email
Authorization: Bearer YOUR_TOKEN
```

**Success Response:**
```json
{
  "message": "Test email sent successfully to student@test.com",
  "email": "student@test.com"
}
```

**Error Response (Email Disabled):**
```json
{
  "error": "Email notifications are disabled in your settings",
  "message": "Please enable email notifications first"
}
```

**cURL:**
```bash
curl -X POST http://localhost:5000/api/notification-settings/test-email \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Send Test In-App Notification

**Request:**
```bash
POST http://localhost:5000/api/notification-settings/test-notification
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "message": "Test notification created successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

**cURL:**
```bash
curl -X POST http://localhost:5000/api/notification-settings/test-notification \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 5. Get Notification History

**Request:**
```bash
GET http://localhost:5000/api/notification-history?limit=10&channel=email&status=sent
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters:**
- `limit` (optional): Number of records (default: 50)
- `channel` (optional): Filter by channel (email, in_app)
- `status` (optional): Filter by status (sent, failed, skipped)

**Response:**
```json
{
  "history": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "user_id": "507f1f77bcf86cd799439012",
      "notification_type": "assignment_created",
      "channel": "email",
      "status": "sent",
      "details": {
        "subject": "New Assignment: Python Programming"
      },
      "timestamp": "2024-11-17T10:30:00Z"
    },
    {
      "_id": "507f1f77bcf86cd799439013",
      "user_id": "507f1f77bcf86cd799439012",
      "notification_type": "test_email",
      "channel": "email",
      "status": "sent",
      "details": {
        "subject": "Test Email from EduNexa LMS"
      },
      "timestamp": "2024-11-17T10:25:00Z"
    }
  ],
  "total": 2,
  "statistics": {
    "total_sent": 45,
    "total_failed": 2
  }
}
```

**cURL:**
```bash
curl -X GET "http://localhost:5000/api/notification-history?limit=10&channel=email" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Admin Endpoints

### 6. Send Custom Notification (Admin Only)

**Send to Specific Roles:**
```bash
POST http://localhost:5000/api/admin/send-notification
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json

{
  "notification_type": "assignment_created",
  "context": {
    "title": "Final Exam",
    "course_title": "Data Structures",
    "due_date": "2024-12-31",
    "points": "100",
    "message": "Final exam has been posted"
  },
  "roles": ["student"]
}
```

**Send to Specific Users:**
```bash
POST http://localhost:5000/api/admin/send-notification
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json

{
  "notification_type": "assignment_graded",
  "context": {
    "title": "Midterm Exam",
    "score": "85",
    "max_points": "100",
    "feedback": "Good work! Review chapter 5."
  },
  "user_ids": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
}
```

**Response:**
```json
{
  "message": "Notifications sent successfully",
  "results": {
    "email_sent": 25,
    "email_failed": 0,
    "in_app_sent": 25,
    "in_app_failed": 0
  }
}
```

**cURL:**
```bash
curl -X POST http://localhost:5000/api/admin/send-notification \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "assignment_created",
    "context": {
      "title": "Final Exam",
      "course_title": "Data Structures",
      "due_date": "2024-12-31",
      "points": "100"
    },
    "roles": ["student"]
  }'
```

---

### 7. Get System Notification Statistics (Admin Only)

**Request:**
```bash
GET http://localhost:5000/api/admin/notification-stats
Authorization: Bearer ADMIN_TOKEN
```

**Response:**
```json
{
  "statistics": {
    "total_sent": 1250,
    "total_failed": 15,
    "total_skipped": 30,
    "email_sent": 600,
    "in_app_sent": 650,
    "users_email_disabled": 5,
    "users_in_app_disabled": 2
  }
}
```

**cURL:**
```bash
curl -X GET http://localhost:5000/api/admin/notification-stats \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## Complete Test Workflow

### Scenario 1: Student Tests Email Notifications

```bash
# 1. Login as student
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@test.com","password":"YourPassword123!"}'

# Save the token from response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 2. Check current settings
curl -X GET http://localhost:5000/api/notification-settings \
  -H "Authorization: Bearer $TOKEN"

# 3. Send test email
curl -X POST http://localhost:5000/api/notification-settings/test-email \
  -H "Authorization: Bearer $TOKEN"

# 4. Check email inbox (manually)

# 5. View notification history
curl -X GET http://localhost:5000/api/notification-history \
  -H "Authorization: Bearer $TOKEN"
```

---

### Scenario 2: Student Disables Email Notifications

```bash
# 1. Login
TOKEN="..." # From login

# 2. Disable email notifications
curl -X PUT http://localhost:5000/api/notification-settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_enabled":false}'

# 3. Try to send test email (should fail)
curl -X POST http://localhost:5000/api/notification-settings/test-email \
  -H "Authorization: Bearer $TOKEN"

# Expected response:
# {
#   "error": "Email notifications are disabled in your settings",
#   "message": "Please enable email notifications first"
# }

# 4. Re-enable email
curl -X PUT http://localhost:5000/api/notification-settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_enabled":true}'

# 5. Send test email again (should succeed)
curl -X POST http://localhost:5000/api/notification-settings/test-email \
  -H "Authorization: Bearer $TOKEN"
```

---

### Scenario 3: Admin Sends Bulk Notification

```bash
# 1. Login as admin
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"AdminPassword123!"}'

ADMIN_TOKEN="..." # From login

# 2. Check system statistics
curl -X GET http://localhost:5000/api/admin/notification-stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. Send notification to all students
curl -X POST http://localhost:5000/api/admin/send-notification \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "assignment_created",
    "context": {
      "title": "System Maintenance Notice",
      "course_title": "All Courses",
      "due_date": "N/A",
      "points": "N/A",
      "message": "System will be down for maintenance tonight"
    },
    "roles": ["student"]
  }'

# 4. Check statistics again
curl -X GET http://localhost:5000/api/admin/notification-stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Notification Types Reference

### Student Notification Types

#### assignment_created
```json
{
  "notification_type": "assignment_created",
  "context": {
    "title": "Assignment Title",
    "course_title": "Course Name",
    "due_date": "2024-12-31",
    "points": "100"
  }
}
```

#### assignment_graded
```json
{
  "notification_type": "assignment_graded",
  "context": {
    "title": "Assignment Title",
    "score": "85",
    "max_points": "100",
    "feedback": "Great work!"
  }
}
```

#### course_enrolled
```json
{
  "notification_type": "course_enrolled",
  "context": {
    "course_title": "Course Name"
  }
}
```

### Teacher Notification Types

#### assignment_submitted
```json
{
  "notification_type": "assignment_submitted",
  "context": {
    "title": "Assignment Title",
    "course_title": "Course Name",
    "student_name": "John Doe",
    "submitted_at": "2024-11-17 10:30:00"
  }
}
```

#### course_enrollment
```json
{
  "notification_type": "course_enrollment",
  "context": {
    "course_title": "Course Name",
    "student_name": "Jane Smith",
    "enrolled_at": "2024-11-17 10:30:00"
  }
}
```

### Admin Notification Types

#### course_created
```json
{
  "notification_type": "course_created",
  "context": {
    "course_title": "New Course",
    "teacher_name": "Dr. Smith",
    "created_at": "2024-11-17 10:30:00"
  }
}
```

#### user_registered
```json
{
  "notification_type": "user_registered",
  "context": {
    "user_name": "New User",
    "user_email": "newuser@example.com",
    "user_role": "student",
    "registered_at": "2024-11-17 10:30:00"
  }
}
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Authorization token is required",
  "code": "TOKEN_MISSING"
}
```

### 403 Forbidden (Admin endpoint)
```json
{
  "error": "Admin access required"
}
```

### 400 Bad Request (Email disabled)
```json
{
  "error": "Email notifications are disabled in your settings",
  "message": "Please enable email notifications first"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to send email: SMTP authentication failed"
}
```

---

## Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "EduNexa Notification System",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
              "mode": "raw",
              "raw": "{\"email\":\"student@test.com\",\"password\":\"YourPassword123!\"}"
            },
            "url": "http://localhost:5000/api/auth/login"
          }
        }
      ]
    },
    {
      "name": "Notification Settings",
      "item": [
        {
          "name": "Get Settings",
          "request": {
            "method": "GET",
            "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
            "url": "http://localhost:5000/api/notification-settings"
          }
        },
        {
          "name": "Update Settings",
          "request": {
            "method": "PUT",
            "header": [
              {"key": "Authorization", "value": "Bearer {{token}}"},
              {"key": "Content-Type", "value": "application/json"}
            ],
            "body": {
              "mode": "raw",
              "raw": "{\"email_enabled\":false,\"in_app_enabled\":true}"
            },
            "url": "http://localhost:5000/api/notification-settings"
          }
        },
        {
          "name": "Send Test Email",
          "request": {
            "method": "POST",
            "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
            "url": "http://localhost:5000/api/notification-settings/test-email"
          }
        },
        {
          "name": "Send Test Notification",
          "request": {
            "method": "POST",
            "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
            "url": "http://localhost:5000/api/notification-settings/test-notification"
          }
        },
        {
          "name": "Get History",
          "request": {
            "method": "GET",
            "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
            "url": "http://localhost:5000/api/notification-history?limit=10"
          }
        }
      ]
    },
    {
      "name": "Admin",
      "item": [
        {
          "name": "Send Notification",
          "request": {
            "method": "POST",
            "header": [
              {"key": "Authorization", "value": "Bearer {{admin_token}}"},
              {"key": "Content-Type", "value": "application/json"}
            ],
            "body": {
              "mode": "raw",
              "raw": "{\"notification_type\":\"assignment_created\",\"context\":{\"title\":\"Test\",\"course_title\":\"Test Course\",\"due_date\":\"2024-12-31\",\"points\":\"100\"},\"roles\":[\"student\"]}"
            },
            "url": "http://localhost:5000/api/admin/send-notification"
          }
        },
        {
          "name": "Get Statistics",
          "request": {
            "method": "GET",
            "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
            "url": "http://localhost:5000/api/admin/notification-stats"
          }
        }
      ]
    }
  ]
}
```

---

## Testing Tips

1. **Save tokens as variables** in Postman for easier testing
2. **Test in order**: Login → Get Settings → Test Email → View History
3. **Check email inbox** after sending test emails
4. **Use MongoDB Compass** to verify database entries
5. **Check backend logs** for detailed error messages

---

## Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/notification-settings` | GET | User | Get settings |
| `/api/notification-settings` | PUT | User | Update settings |
| `/api/notification-settings/test-email` | POST | User | Send test email |
| `/api/notification-settings/test-notification` | POST | User | Send test in-app |
| `/api/notification-history` | GET | User | View history |
| `/api/admin/send-notification` | POST | Admin | Send bulk |
| `/api/admin/notification-stats` | GET | Admin | View stats |
