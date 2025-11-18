# Enhanced Notification System - Implementation Guide

## Overview

The Enhanced Notification System provides comprehensive email and in-app notification functionality for all user roles (Student, Teacher, Admin) in the EduNexa LMS. The system supports user preferences, role-specific templates, notification history, and delivery validation.

## Features

✅ **Role-Specific Notifications**
- Student: Assignment created, graded, course enrollment
- Teacher: Assignment submissions, new enrollments
- Admin: Course creation, user registration

✅ **Dual Delivery Channels**
- Email notifications via SMTP
- In-app notifications stored in database

✅ **User Preferences**
- Toggle email notifications on/off
- Toggle in-app notifications on/off
- Settings persist per user

✅ **Feature Toggles**
- Global enable/disable for email notifications
- Global enable/disable for in-app notifications
- Configured via .env file

✅ **Notification History**
- All notifications logged to database
- Track delivery status (sent, failed, skipped)
- View history per user or system-wide

✅ **Template System**
- Role-specific email templates
- HTML and plain text versions
- Context-based variable substitution

## Configuration

### 1. Environment Variables (.env)

Add the following to your `backend/.env` file:

```bash
# Email/Notification Configuration
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
EMAIL_USE_TLS=true

# Notification Feature Toggles
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_IN_APP_NOTIFICATIONS=true
NOTIFICATION_FROM_NAME=EduNexa LMS
```

### 2. Gmail App Password Setup

To use Gmail for sending notifications:

1. Go to https://myaccount.google.com/
2. Navigate to **Security** > **2-Step Verification** (enable if not already)
3. Go to **Security** > **App passwords**
4. Select **Mail** and **Other (Custom name)**
5. Generate the 16-character app password
6. Copy the password (remove spaces) and paste in `EMAIL_PASSWORD`

### 3. Database Collections

The system uses the following MongoDB collections:

- `notifications` - In-app notifications
- `notification_history` - Delivery logs
- `users.notification_settings` - User preferences (embedded in users collection)

## API Endpoints

### User Endpoints

#### Get Notification Settings
```http
GET /api/notification-settings
Authorization: Bearer <token>
```

Response:
```json
{
  "settings": {
    "email_enabled": true,
    "in_app_enabled": true
  },
  "message": "Notification settings retrieved successfully"
}
```

#### Update Notification Settings
```http
PUT /api/notification-settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "email_enabled": false,
  "in_app_enabled": true
}
```

Response:
```json
{
  "message": "Notification settings updated successfully",
  "settings": {
    "email_enabled": false,
    "in_app_enabled": true
  }
}
```

#### Send Test Email
```http
POST /api/notification-settings/test-email
Authorization: Bearer <token>
```

Response:
```json
{
  "message": "Test email sent successfully to user@example.com",
  "email": "user@example.com"
}
```

#### Send Test In-App Notification
```http
POST /api/notification-settings/test-notification
Authorization: Bearer <token>
```

Response:
```json
{
  "message": "Test notification created successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

#### Get Notification History
```http
GET /api/notification-history?limit=50&channel=email&status=sent
Authorization: Bearer <token>
```

Query Parameters:
- `limit` (optional): Number of records to return (default: 50)
- `channel` (optional): Filter by channel (email, in_app)
- `status` (optional): Filter by status (sent, failed, skipped)

Response:
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
    }
  ],
  "total": 1,
  "statistics": {
    "total_sent": 45,
    "total_failed": 2
  }
}
```

### Admin Endpoints

#### Send Custom Notification (Admin Only)
```http
POST /api/admin/send-notification
Authorization: Bearer <token>
Content-Type: application/json

{
  "notification_type": "assignment_created",
  "context": {
    "title": "Final Exam",
    "course_title": "Data Structures",
    "due_date": "2024-12-31",
    "points": "100"
  },
  "roles": ["student"]
}
```

Or send to specific users:
```json
{
  "notification_type": "assignment_created",
  "context": { ... },
  "user_ids": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
}
```

Response:
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

#### Get System Notification Statistics (Admin Only)
```http
GET /api/admin/notification-stats
Authorization: Bearer <token>
```

Response:
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

## Programmatic Usage

### Send Notification to Single User

```python
from services.enhanced_notification_service import send_notification

# Send notification
result = send_notification(
    db=db,
    user_id="507f1f77bcf86cd799439011",
    notification_type="assignment_created",
    context={
        "title": "Python Assignment",
        "course_title": "Intro to Python",
        "due_date": "2024-12-31",
        "points": "100"
    },
    in_app_title="New Assignment Posted",
    in_app_link="/assignments"
)

print(result)
# {
#   "email": {"sent": True, "message": "Email sent successfully"},
#   "in_app": {"sent": True, "message": "In-app notification created"}
# }
```

### Send Notification to Multiple Users by Role

```python
from services.enhanced_notification_service import notify_by_role

# Notify all students
results = notify_by_role(
    db=db,
    roles=["student"],
    notification_type="assignment_created",
    context={
        "title": "Final Exam",
        "course_title": "Data Structures",
        "due_date": "2024-12-31",
        "points": "100"
    }
)

print(results)
# {
#   "email_sent": 25,
#   "email_failed": 0,
#   "in_app_sent": 25,
#   "in_app_failed": 0
# }
```

### Update User Notification Settings

```python
from services.enhanced_notification_service import update_user_notification_settings

# Disable email notifications for a user
success = update_user_notification_settings(
    db=db,
    user_id="507f1f77bcf86cd799439011",
    email_enabled=False,
    in_app_enabled=True
)
```

## Notification Types and Templates

### Student Notifications

1. **assignment_created**
   - Context: `title`, `course_title`, `due_date`, `points`
   - Triggered: When teacher creates new assignment

2. **assignment_graded**
   - Context: `title`, `score`, `max_points`, `feedback`
   - Triggered: When teacher grades submission

3. **course_enrolled**
   - Context: `course_title`
   - Triggered: When student enrolls in course

### Teacher Notifications

1. **assignment_submitted**
   - Context: `title`, `course_title`, `student_name`, `submitted_at`
   - Triggered: When student submits assignment

2. **course_enrollment**
   - Context: `course_title`, `student_name`, `enrolled_at`
   - Triggered: When student enrolls in teacher's course

### Admin Notifications

1. **course_created**
   - Context: `course_title`, `teacher_name`, `created_at`
   - Triggered: When teacher creates new course

2. **user_registered**
   - Context: `user_name`, `user_email`, `user_role`, `registered_at`
   - Triggered: When new user registers

## Testing

### Run Automated Tests

```bash
# Run comprehensive test suite
python backend/scripts/test_notification_system.py
```

The test script will:
1. Verify environment configuration
2. Test user notification settings (enable/disable)
3. Send test notifications to each role
4. Test email disabled behavior
5. Test bulk notifications
6. Verify notification history logging

### Manual Testing Checklist

#### For Students:
- [ ] Register/login as student
- [ ] Check notification settings: `GET /api/notification-settings`
- [ ] Send test email: `POST /api/notification-settings/test-email`
- [ ] Check email inbox for test message
- [ ] Send test in-app notification: `POST /api/notification-settings/test-notification`
- [ ] View in-app notifications: `GET /api/notifications`
- [ ] Disable email notifications: `PUT /api/notification-settings` with `{"email_enabled": false}`
- [ ] Send test email again (should fail with message about disabled setting)
- [ ] Re-enable email: `PUT /api/notification-settings` with `{"email_enabled": true}`
- [ ] View notification history: `GET /api/notification-history`

#### For Teachers:
- [ ] Register/login as teacher
- [ ] Repeat all student tests above
- [ ] Verify teacher-specific templates work

#### For Admins:
- [ ] Login as admin
- [ ] Repeat all student tests above
- [ ] Send custom notification: `POST /api/admin/send-notification`
- [ ] View system statistics: `GET /api/admin/notification-stats`
- [ ] Verify admin-specific templates work

### Database Verification

Check MongoDB collections:

```javascript
// View in-app notifications
db.notifications.find().sort({created_at: -1}).limit(10)

// View notification history
db.notification_history.find().sort({timestamp: -1}).limit(10)

// View users with disabled email
db.users.find({"notification_settings.email_enabled": false})

// Count notifications by status
db.notification_history.aggregate([
  {$group: {_id: "$status", count: {$sum: 1}}}
])
```

## Troubleshooting

### Email Not Sending

1. **Check credentials**
   ```bash
   # Verify .env file
   cat backend/.env | grep EMAIL
   ```

2. **Test SMTP connection**
   ```python
   python backend/scripts/test_notification_system.py
   ```

3. **Check Gmail App Password**
   - Ensure 2-Step Verification is enabled
   - Generate new App Password if needed
   - Remove spaces from password

4. **Check logs**
   ```bash
   # Backend logs will show SMTP errors
   tail -f backend/logs/app.log
   ```

### In-App Notifications Not Appearing

1. **Check global toggle**
   ```bash
   # Verify in .env
   ENABLE_IN_APP_NOTIFICATIONS=true
   ```

2. **Check user settings**
   ```http
   GET /api/notification-settings
   ```

3. **Check database**
   ```javascript
   db.notifications.find({user_id: "USER_ID"}).sort({created_at: -1})
   ```

### Notifications Skipped

Check notification history to see why:

```http
GET /api/notification-history?status=skipped
```

Common reasons:
- User disabled email/in-app notifications
- Global feature toggle disabled
- Invalid email address
- SMTP authentication failed

## Integration Examples

### Integrate with Assignment Creation

```python
# In routes/assignments.py
from services.enhanced_notification_service import send_notification

@assignments_bp.route('/', methods=['POST'])
@jwt_required()
def create_assignment():
    # ... create assignment logic ...
    
    # Get enrolled students
    enrollments = db.enrollments.find({"course_id": course_id})
    
    # Send notification to each student
    for enrollment in enrollments:
        send_notification(
            db=db,
            user_id=enrollment["student_id"],
            notification_type="assignment_created",
            context={
                "title": assignment["title"],
                "course_title": course["title"],
                "due_date": assignment["due_date"],
                "points": str(assignment["points"])
            },
            in_app_link=f"/assignments/{assignment_id}"
        )
    
    return jsonify({"message": "Assignment created"}), 201
```

### Integrate with Grading

```python
# In routes/grading.py
from services.enhanced_notification_service import send_notification

@grading_bp.route('/<submission_id>/grade', methods=['POST'])
@jwt_required()
def grade_submission(submission_id):
    # ... grading logic ...
    
    # Notify student
    send_notification(
        db=db,
        user_id=submission["student_id"],
        notification_type="assignment_graded",
        context={
            "title": assignment["title"],
            "score": str(grade),
            "max_points": str(assignment["points"]),
            "feedback": feedback or "No feedback provided"
        },
        in_app_link=f"/submissions/{submission_id}"
    )
    
    return jsonify({"message": "Graded successfully"}), 200
```

## Performance Considerations

1. **Bulk Notifications**: Use `notify_by_role()` or `send_bulk_notification()` for multiple users
2. **Async Processing**: Consider using Celery for large-scale notifications
3. **Rate Limiting**: Gmail has sending limits (500 emails/day for free accounts)
4. **Database Indexes**: Create indexes on frequently queried fields

```javascript
// Recommended indexes
db.notifications.createIndex({user_id: 1, created_at: -1})
db.notifications.createIndex({user_id: 1, read: 1})
db.notification_history.createIndex({user_id: 1, timestamp: -1})
db.notification_history.createIndex({status: 1})
```

## Security Considerations

1. **Email Credentials**: Never commit .env file to version control
2. **User Privacy**: Users can disable notifications at any time
3. **Admin Access**: Only admins can send custom notifications
4. **Rate Limiting**: Implement rate limiting on test endpoints
5. **Input Validation**: All context variables are sanitized

## Viva Demonstration Script

### Preparation
1. Configure .env with valid Gmail credentials
2. Run test script: `python backend/scripts/test_notification_system.py`
3. Have 3 browser tabs ready (student, teacher, admin)

### Demo Flow

**1. Show Configuration (2 min)**
- Open `.env` file
- Explain feature toggles
- Show email configuration

**2. Test Student Notifications (3 min)**
- Login as student
- Show current settings: `GET /api/notification-settings`
- Send test email: `POST /api/notification-settings/test-email`
- Check email inbox (show received email)
- Send test in-app: `POST /api/notification-settings/test-notification`
- Show in-app notification in UI

**3. Test User Preferences (2 min)**
- Disable email: `PUT /api/notification-settings` with `{"email_enabled": false}`
- Try sending test email (should show disabled message)
- Re-enable email
- Show notification history: `GET /api/notification-history`

**4. Test Role-Specific Templates (3 min)**
- Login as teacher
- Send test notification (teacher template)
- Login as admin
- Send test notification (admin template)
- Compare email templates for each role

**5. Show Database Entries (2 min)**
- Open MongoDB Compass
- Show `notifications` collection
- Show `notification_history` collection
- Show user settings in `users` collection

**6. Admin Features (2 min)**
- Login as admin
- View system stats: `GET /api/admin/notification-stats`
- Send bulk notification: `POST /api/admin/send-notification`

**Total Time: ~15 minutes**

## Support

For issues or questions:
1. Check logs in `backend/logs/`
2. Review notification history in database
3. Run test script for diagnostics
4. Check Gmail App Password configuration

## License

Part of EduNexa LMS - Educational License
