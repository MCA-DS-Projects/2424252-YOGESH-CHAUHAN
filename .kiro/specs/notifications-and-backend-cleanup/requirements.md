# Requirements Document

## Introduction

This feature enhances the learning management system by adding a shared email notification service accessible to all user roles (User, Admin, Teacher), fixing teacher assignment deletion permissions, and removing all mock/static data to ensure MongoDB is the single source of truth for runtime data. The system uses Gmail SMTP for email delivery and implements proper role-based access control for assignment management.

## Glossary

- **LMS**: Learning Management System - the Flask-based application managing courses, assignments, and users
- **Notification Service**: A shared Python module that sends emails via Gmail SMTP to users based on system events
- **Assignment Controller**: The Flask route/blueprint handling CRUD operations for assignments
- **MongoDB**: The NoSQL database serving as the single source of truth for all runtime data
- **Mock Data**: Hard-coded JSON arrays, fixtures, or seed data that runs automatically at application startup
- **Role**: User classification (User/Student, Teacher, Admin) determining access permissions
- **SMTP**: Simple Mail Transfer Protocol used for sending emails via Gmail
- **Environment Variables**: Configuration values stored outside code (EMAIL_ADDRESS, EMAIL_PASSWORD, MONGO_URI, etc.)

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want a shared email notification service that works for all user roles, so that the system can notify users about important events without duplicating email logic across different modules.

#### Acceptance Criteria

1. THE LMS SHALL provide a notification service module at `backend/services/notification_service.py`
2. WHEN the notification service sends an email, THE LMS SHALL use Gmail SMTP with credentials from environment variables (EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_SMTP_HOST, EMAIL_SMTP_PORT)
3. THE LMS SHALL provide a function `send_email(to, subject, body, html=None)` that sends individual emails via SMTP
4. THE LMS SHALL provide a function `notify_role(role, subject, body, extra=None)` that fetches user emails from MongoDB by role and sends notifications
5. WHEN an email send operation fails, THE LMS SHALL log the error and continue processing without crashing the application flow
6. THE LMS SHALL validate recipient email addresses before attempting to send emails
7. THE LMS SHALL NOT store email credentials in source code or commit them to version control

### Requirement 2

**User Story:** As a teacher, I want to delete assignments that I created, so that I can remove outdated or incorrect assignments from my courses.

#### Acceptance Criteria

1. WHEN a teacher requests to delete an assignment they own, THE Assignment Controller SHALL authorize the deletion and return success (200 or 204)
2. WHEN a teacher requests to delete an assignment they do not own, THE Assignment Controller SHALL deny the request and return 403 Forbidden
3. WHEN an admin requests to delete any assignment, THE Assignment Controller SHALL authorize the deletion regardless of ownership
4. THE Assignment Controller SHALL verify assignment ownership by comparing the assignment's creator ID with the authenticated user's ID
5. THE LMS SHALL remove the assignment record from MongoDB upon successful deletion authorization

### Requirement 3

**User Story:** As a developer, I want all runtime data to come from MongoDB with no mock or static data loaded automatically, so that the system behaves consistently across environments and data is managed through proper database operations.

#### Acceptance Criteria

1. THE LMS SHALL NOT load mock data, fixtures, or hard-coded JSON arrays automatically during application startup
2. WHEN the application starts, THE LMS SHALL connect to MongoDB using the MONGO_URI environment variable as the sole data source
3. THE LMS SHALL replace all in-code data arrays (e.g., `ASSIGNMENTS = [...]`) with MongoDB queries (e.g., `db.assignments.find()`)
4. IF seed data or test data scripts exist, THE LMS SHALL move them to a `backend/scripts/seeders/` directory and require manual execution
5. THE LMS SHALL document the manual seeding process in `docs/DEV_NOTES.md` for development environment setup

### Requirement 4

**User Story:** As a system operator, I want the notification service to integrate with key system events, so that users receive timely updates about assignments and course activities.

#### Acceptance Criteria

1. WHEN a new assignment is created, THE LMS SHALL send email notifications to enrolled students and the course teacher
2. WHEN an assignment is deleted, THE LMS SHALL send email notifications to the teacher and admin users
3. WHEN an assignment deadline is updated, THE LMS SHALL send email notifications to enrolled students
4. THE LMS SHALL handle notification failures gracefully without blocking the primary operation (create, delete, update)
5. WHERE possible, THE LMS SHALL send notifications asynchronously using background threads or job queues

### Requirement 5

**User Story:** As a developer, I want clear documentation and a clean Git history for these changes, so that the team can understand, review, and deploy the updates confidently.

#### Acceptance Criteria

1. THE LMS SHALL implement all changes in a feature branch named `feat/notifications-fix-cleanup`
2. THE LMS SHALL include commit messages following conventional commit format (feat:, fix:, chore:)
3. THE LMS SHALL provide a `docs/DEV_NOTES.md` file documenting environment variable setup and manual seed script usage
4. THE LMS SHALL include test cases or test scripts verifying teacher assignment deletion and notification email sending
5. THE LMS SHALL create a pull request with a description summarizing changes and local testing steps
