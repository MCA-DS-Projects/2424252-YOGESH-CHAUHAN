# Design Document

## Overview

This design enhances the existing EduNexa LMS backend by:
1. **Leveraging the existing Gmail notification service** (`backend/services/notification_service.py`) which already provides comprehensive email functionality
2. **Fixing teacher assignment deletion permissions** in the assignments controller to properly authorize teachers to delete their own assignments
3. **Removing automatic mock data loading** from `db_init.py` and moving test data scripts to a dedicated seeders directory

The system already has a robust notification service with Gmail SMTP integration. Our focus is on integrating it into more workflows, fixing the permission bug, and ensuring MongoDB is the sole runtime data source.

## Architecture

### Current State Analysis

**Existing Components:**
- `backend/services/notification_service.py` - Fully functional Gmail SMTP service with:
  - `send_email()` - Individual email sending
  - `notify_users_by_role()` - Role-based bulk notifications
  - `notify_user_by_id()` - Single user notifications
  - `notify_course_participants()` - Course-wide notifications
  - Proper error handling and logging
  - Email validation
  - Environment variable configuration

- `backend/routes/assignments.py` - Assignment CRUD with:
  - Partial notification integration (create, submit)
  - **BUG**: Delete endpoint has correct permission logic but needs verification
  - Uses threading for async notifications

- `backend/utils/db_init.py` - Database initialization that:
  - **ISSUE**: Automatically creates sample data on startup if DB is empty
  - Creates indexes (good, keep this)
  - Should only run indexes, not seed data

### Modified Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Flask Application                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐         ┌──────────────────┐       │
│  │  Assignment    │────────▶│   Notification   │       │
│  │  Controller    │         │     Service      │       │
│  │                │         │                  │       │
│  │ - Create ✓     │         │ - send_email()   │       │
│  │ - Update       │────────▶│ - notify_role()  │       │
│  │ - Delete (FIX) │         │ - notify_course()│       │
│  │ - Submit ✓     │         └──────────────────┘       │
│  └────────────────┘                  │                  │
│         │                            │                  │
│         │                            ▼                  │
│         │                   ┌─────────────────┐        │
│         └──────────────────▶│    MongoDB      │        │
│                             │                 │        │
│                             │ - users         │        │
│                             │ - courses       │        │
│                             │ - assignments   │        │
│                             │ - submissions   │        │
│                             └─────────────────┘        │
│                                                         │
└─────────────────────────────────────────────────────────┘

External:
┌──────────────────┐
│  Gmail SMTP      │◀─── Environment Variables
│  smtp.gmail.com  │     (EMAIL_ADDRESS, EMAIL_PASSWORD)
└──────────────────┘

Seeders (Manual Only):
┌────────────────────────────────────┐
│  backend/scripts/seeders/          │
│  - seed_sample_data.py             │
│  - create_test_teacher.py          │
│  - create_test_student_data.py     │
└────────────────────────────────────┘
```

## Components and Interfaces

### 1. Notification Service (Existing - No Changes Needed)

**Location:** `backend/services/notification_service.py`

**Status:** ✅ Already implemented correctly

**Key Functions:**
```python
def send_email(to_address: str, subject: str, body: str, html: Optional[str] = None) -> bool
def notify_users_by_role(db, roles: List[str], subject: str, body: str, html: Optional[str] = None, extra_filter: Optional[Dict] = None) -> Dict[str, int]
def notify_user_by_id(db, user_id: str, subject: str, body: str, html: Optional[str] = None) -> bool
def notify_course_participants(db, course_id: str, subject: str, body: str, html: Optional[str] = None, include_teacher: bool = True) -> Dict[str, int]
```

**Configuration (Environment Variables):**
- `EMAIL_SMTP_HOST` (default: smtp.gmail.com)
- `EMAIL_SMTP_PORT` (default: 587)
- `EMAIL_ADDRESS` (required)
- `EMAIL_PASSWORD` (required - use Gmail App Password)
- `EMAIL_USE_TLS` (default: true)

### 2. Assignment Controller Modifications

**Location:** `backend/routes/assignments.py`

**Current Delete Implementation Analysis:**
```python
@assignments_bp.route('/<assignment_id>', methods=['DELETE'])
@jwt_required()
def delete_assignment(assignment_id):
    # Current logic:
    is_admin = user['role'] in ['admin', 'super_admin']
    is_teacher = user['role'] == 'teacher'
    is_owner = is_teacher and course and course['teacher_id'] == user_id
    
    if not (is_admin or is_owner):
        return 403
```

**Status:** ✅ Logic appears correct - needs testing to verify

**Changes Needed:**
1. **Verify permission logic works correctly** (may already be working)
2. **Enhance notification on delete** - currently sends to course participants, should also notify admins
3. **Add assignment deadline update notifications** (new requirement)

**New/Enhanced Endpoints:**

```python
# EXISTING - Verify and potentially enhance
DELETE /api/assignments/<assignment_id>
- Authorization: Teacher (owner) OR Admin
- Deletes assignment and related submissions
- Sends notifications to course participants
- NEW: Also notify admins of deletion

# EXISTING - Add notification
PUT /api/assignments/<assignment_id>
- Authorization: Teacher (owner) OR Admin
- Updates assignment details
- NEW: If due_date changes, notify enrolled students
```

### 3. Database Initialization Refactor

**Location:** `backend/utils/db_init.py`

**Current Behavior:**
- Checks if `db.users.count_documents({}) > 0`
- If empty, automatically creates sample users, courses, enrollments, assignments
- This is problematic for production and clean test environments

**New Behavior:**
```python
def initialize_database(db):
    """Initialize database with indexes only"""
    print("🔧 Initializing database...")
    
    # Create indexes for better performance (KEEP THIS)
    create_indexes(db)
    
    # REMOVE automatic data seeding
    # Users must manually run seed scripts if needed
    
    print("✅ Database initialized with indexes")
```

**Rationale:**
- Indexes are infrastructure, not data - safe to create automatically
- Sample data should be opt-in via manual scripts
- Prevents accidental data pollution in production
- Allows clean test environments

### 4. Seed Scripts Organization

**New Structure:**
```
backend/
├── scripts/
│   └── seeders/
│       ├── README.md                    # Documentation
│       ├── seed_sample_data.py          # Moved from db_init.py
│       ├── create_test_teacher.py       # Moved from root
│       └── create_test_student_data.py  # Moved from root
```

**Seed Scripts:**
1. `seed_sample_data.py` - Creates sample users, courses, enrollments (extracted from db_init.py)
2. `create_test_teacher.py` - Creates test teacher account (moved from backend root)
3. `create_test_student_data.py` - Creates test student, course, assignment, submission (moved from backend root)

## Data Models

### No Changes to Existing Models

All MongoDB collections remain unchanged:
- `users` - User accounts with roles
- `courses` - Course information
- `assignments` - Assignment details
- `submissions` - Student submissions
- `enrollments` - Student-course relationships
- `notifications` - In-app notifications (separate from email)

### Email Notification Events

| Event | Trigger | Recipients | Implementation Status |
|-------|---------|-----------|----------------------|
| Assignment Created | POST /assignments | Enrolled students | ✅ Implemented |
| Assignment Deleted | DELETE /assignments/:id | Course participants + Admins | ⚠️ Partial (add admins) |
| Assignment Updated | PUT /assignments/:id | Enrolled students (if due_date changed) | ❌ Not implemented |
| Assignment Submitted | POST /assignments/:id/submit | Course teacher | ✅ Implemented |
| Assignment Graded | POST /submissions/:id/grade | Student | ✅ Implemented |

## Error Handling

### Notification Failures

**Current Strategy (Keep):**
- Notifications run in background threads (daemon threads)
- Failures are logged but don't block primary operations
- Returns success/failure counts for monitoring

**Example Pattern:**
```python
try:
    from services.notification_service import notify_course_participants
    import threading
    
    thread = threading.Thread(
        target=notify_course_participants,
        args=(db, course_id, subject, body)
    )
    thread.daemon = True
    thread.start()
except Exception as e:
    # Log but don't fail the operation
    logger.error(f"Notification failed: {e}")
```

### Permission Errors

**Assignment Deletion:**
```python
# Clear error messages for different scenarios
if not assignment:
    return 404, "Assignment not found"

if not (is_admin or is_owner):
    return 403, "Access denied. You can only delete your own assignments."
```

### Database Errors

**Graceful Degradation:**
- If MongoDB connection fails during notification lookup, log error and skip notifications
- Primary operations (create, update, delete) should still succeed if possible
- Use try-except blocks around notification code

## Testing Strategy

### 1. Unit Tests (Optional - Mark as optional in tasks)

**Test Files:**
- `backend/test_notification_service.py` - Test email sending (requires test Gmail account)
- `backend/test_assignment_permissions.py` - Test RBAC for assignment operations

### 2. Integration Tests

**Manual Test Script:** `backend/scripts/test_assignment_workflow.py`
```python
# Test workflow:
1. Create teacher account
2. Create course
3. Create assignment (verify notification sent)
4. Teacher deletes assignment (verify permission + notification)
5. Teacher tries to delete another teacher's assignment (verify 403)
```

### 3. Environment Setup Tests

**Verify:**
- MongoDB connection without auto-seeding
- Email credentials configuration
- Manual seed scripts work correctly

### 4. Test Documentation

**Location:** `docs/DEV_NOTES.md`

**Contents:**
- Environment variable setup instructions
- Manual seed script usage
- Testing email notifications locally
- Common troubleshooting scenarios

## Implementation Phases

### Phase 1: Database Cleanup
1. Create `backend/scripts/seeders/` directory
2. Move seed logic from `db_init.py` to `seed_sample_data.py`
3. Move `create_test_teacher.py` and `create_test_data.py` to seeders
4. Update `db_init.py` to only create indexes
5. Update `app.py` to not call seed functions

### Phase 2: Assignment Permissions
1. Review and test current delete permission logic
2. Add test cases for teacher deletion scenarios
3. Fix any permission bugs discovered
4. Enhance error messages

### Phase 3: Notification Integration
1. Add admin notification on assignment deletion
2. Add student notification on assignment due date update
3. Verify all notification events work correctly
4. Test email delivery with test Gmail account

### Phase 4: Documentation
1. Create `docs/DEV_NOTES.md` with setup instructions
2. Create `backend/scripts/seeders/README.md` with usage guide
3. Update `.env.example` with email configuration
4. Document testing procedures

## Security Considerations

### Email Credentials
- ✅ Already using environment variables
- ✅ Never commit credentials to Git
- ✅ Use Gmail App Passwords (not account password)
- Document in DEV_NOTES.md

### Permission Validation
- ✅ JWT authentication on all endpoints
- ✅ Role-based access control
- ✅ Ownership verification for teacher operations
- Add comprehensive error messages

### Email Validation
- ✅ Already implemented in notification service
- Validates email format before sending
- Handles invalid emails gracefully

## Performance Considerations

### Asynchronous Notifications
- ✅ Already using daemon threads
- Notifications don't block HTTP responses
- Consider adding job queue (Celery/RQ) for production scale

### Database Queries
- ✅ Indexes already created for common queries
- Notification service fetches only necessary fields (email, name)
- Batch operations where possible

### Email Rate Limiting
- Gmail has sending limits (500/day for free accounts, 2000/day for Workspace)
- Consider implementing rate limiting for bulk notifications
- Log all email attempts for monitoring

## Deployment Considerations

### Environment Variables
Required in production:
```bash
# MongoDB
MONGO_URI=mongodb://...

# JWT
JWT_SECRET_KEY=...

# Email (Gmail)
EMAIL_ADDRESS=noreply@yourdomain.com
EMAIL_PASSWORD=your_app_password
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USE_TLS=true
```

### Database Migration
- No schema changes required
- Existing data remains unchanged
- Seed scripts are opt-in

### Monitoring
- Log all notification attempts
- Monitor email delivery success rates
- Track permission denial attempts
- Alert on repeated failures

## Open Questions & Decisions

### 1. Notification Preferences (Future Enhancement)
**Question:** Should users be able to opt-out of email notifications?

**Decision:** Not in scope for this feature. Add to backlog for future user preferences system.

### 2. Email Templates (Future Enhancement)
**Question:** Should we use HTML email templates?

**Decision:** Current plain text + optional HTML is sufficient. Can enhance later with template engine.

### 3. Notification History (Future Enhancement)
**Question:** Should we log all sent emails to database?

**Decision:** Not in scope. Current logging to console/file is sufficient for now.

### 4. Assignment Update Notifications
**Question:** Should we notify on ALL updates or only due_date changes?

**Decision:** Only notify on due_date changes to avoid notification fatigue.
