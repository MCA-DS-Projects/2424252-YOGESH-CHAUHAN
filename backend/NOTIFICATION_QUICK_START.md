# Notification System - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Configure Email Credentials

Edit `backend/.env`:

```bash
# Add these lines
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_IN_APP_NOTIFICATIONS=true
```

**Get Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to App passwords
4. Generate password for "Mail" → "Other"
5. Copy the 16-character password (no spaces)

### Step 2: Start Backend

```bash
cd backend
python run.py
```

### Step 3: Run Tests

```bash
python backend/scripts/test_notification_system.py
```

## 📧 Quick Test Commands

### Test as Student

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@test.com","password":"password"}'

# Get token from response, then:

# Check settings
curl -X GET http://localhost:5000/api/notification-settings \
  -H "Authorization: Bearer YOUR_TOKEN"

# Send test email
curl -X POST http://localhost:5000/api/notification-settings/test-email \
  -H "Authorization: Bearer YOUR_TOKEN"

# Send test in-app notification
curl -X POST http://localhost:5000/api/notification-settings/test-notification \
  -H "Authorization: Bearer YOUR_TOKEN"

# View history
curl -X GET http://localhost:5000/api/notification-history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Toggle Email Off/On

```bash
# Disable email
curl -X PUT http://localhost:5000/api/notification-settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_enabled":false}'

# Enable email
curl -X PUT http://localhost:5000/api/notification-settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_enabled":true}'
```

## ✅ Manual Testing Checklist

### Basic Tests (5 min)
- [ ] Configure .env with email credentials
- [ ] Start backend server
- [ ] Run test script: `python backend/scripts/test_notification_system.py`
- [ ] Check email inbox for test messages
- [ ] Verify all tests pass

### Student Tests (5 min)
- [ ] Login as student
- [ ] GET `/api/notification-settings` - view current settings
- [ ] POST `/api/notification-settings/test-email` - receive test email
- [ ] Check email inbox
- [ ] POST `/api/notification-settings/test-notification` - create in-app notification
- [ ] GET `/api/notifications` - view in-app notifications
- [ ] GET `/api/notification-history` - view delivery history

### Toggle Tests (3 min)
- [ ] PUT `/api/notification-settings` with `{"email_enabled": false}`
- [ ] POST `/api/notification-settings/test-email` - should fail with disabled message
- [ ] PUT `/api/notification-settings` with `{"email_enabled": true}`
- [ ] POST `/api/notification-settings/test-email` - should succeed
- [ ] GET `/api/notification-history` - verify skipped entry logged

### Teacher Tests (3 min)
- [ ] Login as teacher
- [ ] POST `/api/notification-settings/test-email`
- [ ] Check email - verify teacher-specific template
- [ ] GET `/api/notification-history`

### Admin Tests (4 min)
- [ ] Login as admin
- [ ] POST `/api/notification-settings/test-email`
- [ ] Check email - verify admin-specific template
- [ ] GET `/api/admin/notification-stats` - view system statistics
- [ ] POST `/api/admin/send-notification` - send bulk notification

### Database Verification (2 min)
- [ ] Open MongoDB Compass or mongo shell
- [ ] Check `notifications` collection - verify in-app notifications
- [ ] Check `notification_history` collection - verify delivery logs
- [ ] Check `users` collection - verify notification_settings field

**Total Time: ~22 minutes**

## 🎯 Viva Demo Script (10 minutes)

### 1. Show Configuration (1 min)
```bash
# Show .env file
cat backend/.env | grep -A 5 "EMAIL"
```

### 2. Run Automated Tests (2 min)
```bash
python backend/scripts/test_notification_system.py
```
- Show all tests passing
- Explain what each test does

### 3. Test Student Flow (2 min)
- Login as student in browser/Postman
- Send test email
- Show received email in inbox
- Show role-specific template

### 4. Test Preferences (2 min)
- Disable email notifications
- Try sending email (show error)
- Re-enable email
- Show notification history

### 5. Show Database (2 min)
- Open MongoDB Compass
- Show `notifications` collection
- Show `notification_history` collection
- Explain logging and tracking

### 6. Admin Features (1 min)
- Show admin statistics endpoint
- Explain bulk notification capability

## 🔧 Troubleshooting

### Email Not Sending?

```bash
# Check configuration
cat backend/.env | grep EMAIL

# Test SMTP connection
python backend/scripts/test_notification_system.py

# Check logs
tail -f backend/logs/app.log
```

**Common Issues:**
- ❌ Wrong App Password → Generate new one
- ❌ 2-Step Verification not enabled → Enable it
- ❌ Spaces in password → Remove them
- ❌ Using regular password → Use App Password

### In-App Notifications Not Showing?

```bash
# Check global toggle
cat backend/.env | grep ENABLE_IN_APP

# Check user settings
curl -X GET http://localhost:5000/api/notification-settings \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check database
mongo edunexa_lms --eval "db.notifications.find().limit(5)"
```

### Tests Failing?

```bash
# Ensure MongoDB is running
mongo --eval "db.adminCommand('ping')"

# Ensure backend is running
curl http://localhost:5000/api/health

# Check for test users
mongo edunexa_lms --eval "db.users.count()"
```

## 📚 Key Files

- `backend/.env` - Configuration
- `backend/services/enhanced_notification_service.py` - Core service
- `backend/routes/notification_settings.py` - API endpoints
- `backend/scripts/test_notification_system.py` - Test script
- `backend/NOTIFICATION_SYSTEM_README.md` - Full documentation

## 🎓 For Viva

**Be Ready to Explain:**
1. How email notifications work (SMTP, Gmail App Password)
2. How user preferences are stored (MongoDB, embedded in users)
3. How role-specific templates work (template dictionary, context substitution)
4. How notification history is logged (separate collection, all deliveries tracked)
5. How feature toggles work (.env variables, global enable/disable)

**Be Ready to Demonstrate:**
1. Sending test email to each role
2. Toggling email notifications off/on
3. Viewing notification history
4. Showing database entries
5. Admin bulk notification

**Key Points:**
- ✅ All three roles supported (student, teacher, admin)
- ✅ Email and in-app notifications
- ✅ User preferences respected
- ✅ Feature toggles in .env
- ✅ Complete delivery logging
- ✅ Role-specific templates
- ✅ Validation and error handling

## 📞 Quick Reference

### API Endpoints
- `GET /api/notification-settings` - Get user settings
- `PUT /api/notification-settings` - Update settings
- `POST /api/notification-settings/test-email` - Send test email
- `POST /api/notification-settings/test-notification` - Send test in-app
- `GET /api/notification-history` - View history
- `GET /api/admin/notification-stats` - Admin statistics
- `POST /api/admin/send-notification` - Admin bulk send

### Environment Variables
- `EMAIL_ADDRESS` - Gmail address
- `EMAIL_PASSWORD` - Gmail App Password
- `ENABLE_EMAIL_NOTIFICATIONS` - Global email toggle
- `ENABLE_IN_APP_NOTIFICATIONS` - Global in-app toggle

### Database Collections
- `notifications` - In-app notifications
- `notification_history` - Delivery logs
- `users.notification_settings` - User preferences

Good luck with your viva! 🎉
