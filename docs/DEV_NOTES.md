# EduNexa LMS - Developer Notes

This document provides essential setup instructions, configuration details, and troubleshooting guidance for developers working on the EduNexa Learning Management System.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Email Configuration (Gmail SMTP)](#email-configuration-gmail-smtp)
- [Database Seeding](#database-seeding)
- [Testing Procedures](#testing-procedures)
- [Troubleshooting](#troubleshooting)

---

## Environment Setup

### Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Node.js 16+ (for frontend)
- Git

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd edunexa-lms
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   npm install
   ```

4. **Environment Variables**
   
   Copy the example environment file and configure it:
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` with your configuration (see sections below for details).

5. **Start MongoDB**
   
   Ensure MongoDB is running on your system:
   
   **Windows:**
   ```bash
   net start MongoDB
   ```
   
   **Linux/Mac:**
   ```bash
   sudo systemctl start mongod
   ```

6. **Initialize Database**
   
   Start the backend application to create database indexes:
   ```bash
   python backend/app.py
   ```
   
   The application will automatically create necessary indexes but **will not** load any sample data.

7. **Seed Sample Data (Optional)**
   
   See [Database Seeding](#database-seeding) section below.

---

## Email Configuration (Gmail SMTP)

The EduNexa LMS uses Gmail SMTP to send email notifications for various system events (assignment creation, grading, due date changes, etc.).

### Why Gmail App Passwords?

Gmail requires App Passwords when using SMTP with accounts that have 2-Step Verification enabled. This is more secure than using your actual Gmail password.

### Step-by-Step Gmail Setup

#### 1. Enable 2-Step Verification

1. Go to your [Google Account](https://myaccount.google.com/)
2. Navigate to **Security** in the left sidebar
3. Under "Signing in to Google", click **2-Step Verification**
4. Follow the prompts to enable 2-Step Verification
5. You may need to verify your identity via phone

#### 2. Generate an App Password

1. After enabling 2-Step Verification, return to **Security** settings
2. Under "Signing in to Google", click **App passwords**
   - If you don't see this option, ensure 2-Step Verification is fully enabled
3. At the bottom, click **Select app** and choose **Mail**
4. Click **Select device** and choose **Other (Custom name)**
5. Enter a name like "EduNexa LMS" or "Development Server"
6. Click **Generate**
7. Google will display a 16-character password (e.g., `abcd efgh ijkl mnop`)
8. **Copy this password immediately** - you won't be able to see it again

#### 3. Configure Environment Variables

Edit your `backend/.env` file and add the email configuration:

```bash
# Email Configuration (Gmail SMTP)
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop  # Your 16-character App Password (no spaces)
EMAIL_USE_TLS=true
```

**Important Notes:**
- Remove all spaces from the App Password when pasting it
- Use your full Gmail address (e.g., `yourname@gmail.com`)
- Never commit your `.env` file to version control
- The `.env.example` file should only contain placeholder values

#### 4. Verify Email Configuration

Test your email configuration using the test script:

```bash
python backend/scripts/test_email_notification.py
```

This will attempt to send a test email and report any errors.

### Alternative Email Providers

While Gmail is recommended for development, you can use other SMTP providers:

**SendGrid:**
```bash
EMAIL_SMTP_HOST=smtp.sendgrid.net
EMAIL_SMTP_PORT=587
EMAIL_ADDRESS=apikey
EMAIL_PASSWORD=your-sendgrid-api-key
```

**Mailgun:**
```bash
EMAIL_SMTP_HOST=smtp.mailgun.org
EMAIL_SMTP_PORT=587
EMAIL_ADDRESS=postmaster@your-domain.mailgun.org
EMAIL_PASSWORD=your-mailgun-password
```

**AWS SES:**
```bash
EMAIL_SMTP_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_SMTP_PORT=587
EMAIL_ADDRESS=your-ses-smtp-username
EMAIL_PASSWORD=your-ses-smtp-password
```

---

## Database Seeding

The EduNexa LMS uses MongoDB as its single source of truth. The application **does not** automatically load any mock or sample data on startup. All data must be seeded manually using the scripts in `backend/scripts/seeders/`.

### Why Manual Seeding?

- **Production Safety**: Prevents accidental data pollution in production environments
- **Clean Testing**: Allows developers to start with a clean database for testing
- **Flexibility**: Developers can choose which data to seed based on their needs
- **Consistency**: Ensures all environments behave the same way

### Available Seed Scripts

#### 1. Seed Sample Data

Creates a complete development environment with users, courses, enrollments, and assignments.

**Usage:**
```bash
python backend/scripts/seeders/seed_sample_data.py
```

**What it creates:**
- 3 sample students (student01@datams.edu, student02@datams.edu, student03@datams.edu)
- 2 sample teachers (teacher01@datams.edu, teacher02@datams.edu)
- 1 super admin (superadmin@datams.edu)
- 4 sample courses (ML, Python, Data Science, React)
- Student enrollments (each student enrolled in 2-3 courses)
- 2 assignments per course

**Default Password:** 
- Students: `Stud@2025`
- Teachers: `Teach@2025`
- Super Admin: `Admin@123456`

#### 2. Create Test Teacher

Creates a single test teacher account for integration testing.

**Usage:**
```bash
python backend/scripts/seeders/create_test_teacher.py
```

**Credentials:**
- Email: `teacher@test.com`
- Password: `test123`

#### 3. Create Test Student Data

Creates a complete test scenario for testing grading workflows.

**Prerequisites:** Must run `create_test_teacher.py` first.

**Usage:**
```bash
# First, create the test teacher
python backend/scripts/seeders/create_test_teacher.py

# Then, create the test student data
python backend/scripts/seeders/create_test_student_data.py
```

**What it creates:**
- 1 test student (student@test.com)
- 1 test course (owned by test teacher)
- Student enrollment
- 1 test assignment
- 1 test submission (ready for grading)

**Credentials:**
- Email: `student@test.com`
- Password: `test123`

### Common Seeding Workflows

#### Fresh Development Environment

```bash
# 1. Start MongoDB
net start MongoDB  # Windows
# or
sudo systemctl start mongod  # Linux/Mac

# 2. Start the application (creates indexes)
python backend/app.py

# 3. In a new terminal, seed sample data
python backend/scripts/seeders/seed_sample_data.py
```

#### Integration Testing Setup

```bash
# 1. Create test teacher
python backend/scripts/seeders/create_test_teacher.py

# 2. Create test student and related data
python backend/scripts/seeders/create_test_student_data.py

# 3. Run your tests
python backend/test_teacher_endpoints.py
```

#### Resetting the Database

```bash
# Option 1: Using MongoDB shell
mongo
use edunexa_lms
db.dropDatabase()
exit

# Option 2: Using MongoDB Compass
# Connect to localhost:27017
# Right-click on "edunexa_lms" database
# Select "Drop Database"

# After dropping, restart the application to recreate indexes
python backend/app.py

# Re-seed data as needed
python backend/scripts/seeders/seed_sample_data.py
```

### Seed Script Details

For more detailed information about each seed script, including troubleshooting and best practices, see:
- `backend/scripts/seeders/README.md`

---

## Testing Procedures

### Testing Email Notifications Locally

#### 1. Configure Email Settings

Ensure your `backend/.env` file has valid Gmail SMTP credentials (see [Email Configuration](#email-configuration-gmail-smtp)).

#### 2. Test Email Service Directly

```bash
python backend/scripts/test_email_notification.py
```

This script tests:
- Basic email sending functionality
- Role-based notifications
- Course participant notifications
- Error handling

**Expected Output:**
```
Testing Email Notification Service
===================================
✅ Email service configured
✅ Test email sent successfully
✅ Role-based notification sent to 2 admins
✅ Course notification sent to 5 participants
```

#### 3. Test Assignment Workflow Notifications

Create a test scenario to verify notifications are sent during assignment operations:

```bash
# 1. Seed test data
python backend/scripts/seeders/create_test_teacher.py
python backend/scripts/seeders/create_test_student_data.py

# 2. Start the backend
python backend/app.py

# 3. In another terminal, test assignment operations
python backend/scripts/test_assignment_deletion.py
```

**What to verify:**
- Assignment creation sends email to enrolled students
- Assignment deletion sends email to course participants and admins
- Assignment due date update sends email to enrolled students
- Assignment grading sends email to the student

#### 4. Manual API Testing

Use tools like Postman, curl, or Thunder Client to test API endpoints:

**Create Assignment (should send notification):**
```bash
curl -X POST http://localhost:5000/api/assignments \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Assignment",
    "description": "Testing notifications",
    "course_id": "COURSE_ID",
    "due_date": "2024-12-31T23:59:59Z",
    "max_points": 100
  }'
```

**Update Assignment Due Date (should send notification):**
```bash
curl -X PUT http://localhost:5000/api/assignments/ASSIGNMENT_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "due_date": "2025-01-15T23:59:59Z"
  }'
```

**Delete Assignment (should send notification):**
```bash
curl -X DELETE http://localhost:5000/api/assignments/ASSIGNMENT_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Testing Assignment Deletion Permissions

#### Manual Test Scenarios

**Scenario 1: Teacher deletes own assignment (should succeed)**

1. Login as teacher (teacher@test.com / test123)
2. Create an assignment in your course
3. Attempt to delete the assignment
4. **Expected:** 200/204 response, assignment deleted, notifications sent

**Scenario 2: Teacher deletes another teacher's assignment (should fail)**

1. Login as teacher01@datams.edu
2. Find an assignment created by teacher02@datams.edu
3. Attempt to delete the assignment
4. **Expected:** 403 Forbidden response with error message

**Scenario 3: Admin deletes any assignment (should succeed)**

1. Login as superadmin@datams.edu
2. Find any assignment
3. Attempt to delete the assignment
4. **Expected:** 200/204 response, assignment deleted, notifications sent

#### Automated Test Script

```bash
python backend/scripts/test_assignment_deletion.py
```

This script automatically tests all three scenarios and reports results.

### Testing MongoDB-Only Data Flow

Verify that the application does not automatically load any mock data:

```bash
# 1. Drop the database
mongo
use edunexa_lms
db.dropDatabase()
exit

# 2. Start the application
python backend/app.py

# 3. Verify no data was created automatically
mongo
use edunexa_lms
db.users.count()  # Should return 0
db.courses.count()  # Should return 0
db.assignments.count()  # Should return 0
exit

# 4. Verify indexes were created
mongo
use edunexa_lms
db.users.getIndexes()  # Should show indexes
exit
```

**Expected Behavior:**
- Application starts successfully
- Database indexes are created
- No users, courses, or assignments exist
- Application is ready for manual data seeding

---

## Troubleshooting

### Email Issues

#### "Authentication failed" or "Username and password not accepted"

**Cause:** Invalid Gmail credentials or App Password not configured.

**Solution:**
1. Verify 2-Step Verification is enabled on your Google Account
2. Generate a new App Password (see [Email Configuration](#email-configuration-gmail-smtp))
3. Ensure you're using the App Password, not your Gmail password
4. Remove all spaces from the App Password in your `.env` file
5. Verify `EMAIL_ADDRESS` is your full Gmail address

#### "SMTPServerDisconnected: Connection unexpectedly closed"

**Cause:** Gmail may be blocking the connection or TLS settings are incorrect.

**Solution:**
1. Verify `EMAIL_USE_TLS=true` in your `.env` file
2. Check that `EMAIL_SMTP_PORT=587` (not 465 or 25)
3. Ensure your firewall isn't blocking outbound SMTP connections
4. Try accessing Gmail from the same network to ensure it's not blocked

#### Emails not being received

**Cause:** Emails may be going to spam or Gmail sending limits reached.

**Solution:**
1. Check the spam/junk folder of recipient email
2. Verify the recipient email address is correct
3. Check Gmail sending limits (500/day for free accounts)
4. Review application logs for email sending errors
5. Test with the test script: `python backend/scripts/test_email_notification.py`

#### "No module named 'services.notification_service'"

**Cause:** Python path not configured correctly in scripts.

**Solution:**
1. Ensure you're running scripts from the project root directory
2. Verify the script includes proper path configuration:
   ```python
   import sys
   import os
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
   ```

### Database Issues

#### "Failed to connect to MongoDB"

**Cause:** MongoDB is not running or connection string is incorrect.

**Solution:**

**Windows:**
```bash
# Check if MongoDB is running
net start MongoDB

# If not running, start it
net start MongoDB
```

**Linux/Mac:**
```bash
# Check status
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod

# Enable MongoDB to start on boot
sudo systemctl enable mongod
```

**Verify Connection String:**
- Check `MONGO_URI` in `backend/.env`
- Default: `mongodb://localhost:27017/edunexa_lms`
- Ensure the database name is correct

#### "Database already contains X users" when seeding

**Cause:** Seed script detects existing data.

**Solution:**
- Choose 'y' to add more data alongside existing data
- Choose 'n' to cancel
- Or reset the database (see [Resetting the Database](#resetting-the-database))

#### "Test teacher not found" when running create_test_student_data.py

**Cause:** Test teacher must be created before test student data.

**Solution:**
```bash
# Run in this order:
python backend/scripts/seeders/create_test_teacher.py
python backend/scripts/seeders/create_test_student_data.py
```

### Permission Issues

#### Teacher cannot delete own assignment

**Cause:** Possible bug in permission logic or incorrect user/assignment data.

**Solution:**
1. Verify the teacher is logged in (check JWT token)
2. Verify the assignment's `created_by` field matches the teacher's user ID
3. Check application logs for detailed error messages
4. Run the test script: `python backend/scripts/test_assignment_deletion.py`

#### Admin cannot delete any assignment

**Cause:** Role not properly set or JWT token issue.

**Solution:**
1. Verify the user's role is 'admin' or 'super_admin' in the database:
   ```javascript
   db.users.findOne({email: "superadmin@datams.edu"})
   ```
2. Verify the JWT token includes the correct role
3. Check that the JWT secret key matches between token generation and validation

### Import Errors

#### "ModuleNotFoundError: No module named 'X'"

**Cause:** Missing Python dependencies.

**Solution:**
```bash
# Reinstall dependencies
pip install -r backend/requirements.txt

# If using virtual environment, ensure it's activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Application Startup Issues

#### "Port 5000 already in use"

**Cause:** Another process is using port 5000.

**Solution:**

**Windows:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

**Or change the port in `backend/.env`:**
```bash
PORT=5001
```

#### Application crashes on startup

**Cause:** Various possible issues.

**Solution:**
1. Check the error message in the console
2. Verify all environment variables are set correctly
3. Ensure MongoDB is running
4. Check Python version (requires 3.8+)
5. Review application logs for detailed error information

### Testing Issues

#### Test scripts fail with authentication errors

**Cause:** Invalid or expired JWT tokens.

**Solution:**
1. Ensure test users exist (run seed scripts)
2. Generate fresh JWT tokens by logging in
3. Update test scripts with new tokens
4. Verify JWT_SECRET_KEY is consistent

#### Notifications not sent during tests

**Cause:** Email configuration not set or notifications running in background threads.

**Solution:**
1. Verify email configuration (see [Email Configuration](#email-configuration-gmail-smtp))
2. Check application logs for notification errors
3. Notifications run asynchronously - check logs after a few seconds
4. Test email service directly: `python backend/scripts/test_email_notification.py`

---

## Additional Resources

- **Backend README**: `backend/README.md` - Main backend documentation
- **Seeders README**: `backend/scripts/seeders/README.md` - Detailed seeder documentation
- **API Documentation**: `docs/PROJECT_DOCUMENTATION.md` - Complete API reference
- **Deployment Guide**: `docs/DEPLOYMENT_GUIDE.md` - Production deployment instructions

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the application logs for detailed error messages
2. Review the relevant documentation files listed above
3. Search existing issues in the project repository
4. Create a new issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - Error messages and logs
   - Your environment details (OS, Python version, MongoDB version)

---

**Last Updated:** 2024  
**Maintained By:** EduNexa Development Team
