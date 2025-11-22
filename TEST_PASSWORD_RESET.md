# Test Password Reset Email - Complete Guide

## ✅ What Was Fixed:

### Problem:
ForgotPasswordForm was using **fake/simulated API call** instead of calling the actual backend!

```typescript
// OLD CODE (WRONG):
await new Promise(resolve => setTimeout(resolve, 2000)); // Fake delay
setIsSuccess(true); // Always success, no real API call
```

### Solution:
Now using **real backend API call**:

```typescript
// NEW CODE (CORRECT):
await authAPI.forgotPassword(email); // Real API call to backend
setIsSuccess(true); // Success only if API succeeds
```

---

## 🧪 Testing Steps:

### Step 1: Verify Backend is Running

```bash
cd backend
python run.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 2: Verify Email Configuration

Check `backend/.env`:
```env
EMAIL_ADDRESS=yogesh.chauhan.ai@gmail.com  # ← Should NOT have "your-" prefix
EMAIL_PASSWORD=wehs zbpq otgy hfbq         # ← 16-character App Password
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USE_TLS=true
```

### Step 3: Test Email Configuration

```bash
cd backend
python test_email.py
```

**Expected output:**
```
✅ SMTP connection successful!
✅ Authentication successful!
✅ EMAIL CONFIGURATION IS WORKING!
```

### Step 4: Check Database for Test User

Make sure you have a user in the database to test with:

```bash
cd backend
python -c "from pymongo import MongoClient; db = MongoClient('mongodb://localhost:27017/edunexa_lms').edunexa_lms; users = list(db.users.find({}, {'email': 1, 'name': 1})); print('Users:', [(u['email'], u['name']) for u in users[:5]])"
```

### Step 5: Test Frontend

1. **Open browser:** http://localhost:3000
2. **Click:** "Forgot Password" link
3. **Enter email:** Use an email from your database (e.g., `student01@datams.edu`)
4. **Click:** "Send Reset Link"
5. **Wait:** 2-5 seconds for API call
6. **Check:** Success message should appear

### Step 6: Check Backend Logs

In the backend terminal, you should see:

```
Password reset email sent to student01@datams.edu
```

OR if there's an error:

```
Failed to send password reset email to student01@datams.edu
Error: [error details]
```

### Step 7: Check Email Inbox

1. **Check inbox** of the email you entered
2. **Check spam/junk folder** if not in inbox
3. **Wait 1-2 minutes** for email to arrive

**Expected email:**
- Subject: "Password Reset Request - EduNexa LMS"
- From: yogesh.chauhan.ai@gmail.com
- Contains: "Reset Your Password" button
- Contains: Reset link with token

---

## 🔍 Troubleshooting:

### Issue 1: "Failed to send reset email"

**Check:**
1. Backend is running
2. MongoDB is running
3. Email exists in database
4. Backend logs for specific error

**Solution:**
```bash
# Check if user exists
cd backend
python -c "from pymongo import MongoClient; db = MongoClient('mongodb://localhost:27017/edunexa_lms').edunexa_lms; user = db.users.find_one({'email': 'student01@datams.edu'}); print('User found:', user is not None)"
```

### Issue 2: "SMTP Authentication Error"

**Check:**
1. Gmail App Password is correct
2. 2-Step Verification is enabled
3. No spaces in password (or spaces are correct)

**Solution:**
1. Go to: https://myaccount.google.com/apppasswords
2. Delete old "EduNexa LMS" app password
3. Create new app password
4. Copy exactly as shown (with or without spaces)
5. Update `EMAIL_PASSWORD` in `.env`
6. Restart backend

### Issue 3: Email Not Received

**Check:**
1. Spam/Junk folder
2. Email address is correct
3. Gmail account not locked
4. Backend logs show "Email sent successfully"

**Test manually:**
```bash
# Send test email using Python
cd backend
python -c "
from services.notification_service import send_email
result = send_email(
    'your-test-email@gmail.com',
    'Test Email',
    'This is a test email from EduNexa LMS',
    '<h1>Test Email</h1><p>This is a test email from EduNexa LMS</p>'
)
print('Email sent:', result)
"
```

### Issue 4: "Network Error" or "Failed to fetch"

**Check:**
1. Backend is running on port 5000
2. Frontend can reach backend
3. No CORS errors in browser console

**Test API directly:**
```bash
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "student01@datams.edu"}'
```

**Expected response:**
```json
{
  "message": "If an account with that email exists, a password reset link has been sent"
}
```

---

## 📧 Email Template Preview:

The email will look like this:

```
┌─────────────────────────────────────────┐
│  🎓 EduNexa                             │
│  SMART LEARNING MANAGEMENT SYSTEM       │
│  (Purple-Blue Gradient Background)      │
├─────────────────────────────────────────┤
│                                         │
│  Hello John Doe,                        │
│                                         │
│  You have requested to reset your       │
│  password for your EduNexa LMS account. │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   [Reset Your Password Button]    │ │
│  │   (Blue Gradient, Clickable)      │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ⏰ Important: This link will expire    │
│  in 1 hour for security reasons.       │
│                                         │
│  Or copy this link:                     │
│  http://localhost:3000/reset-password   │
│  ?token=abc123...                       │
│                                         │
│  🔒 Security Tips:                      │
│  • Use a strong, unique password        │
│  • Don't share your password            │
│  • Enable two-factor authentication     │
│                                         │
│  If you didn't request this, ignore it. │
│                                         │
├─────────────────────────────────────────┤
│  Best regards,                          │
│  EduNexa LMS Team                       │
│                                         │
│  © 2024 EduNexa LMS                     │
└─────────────────────────────────────────┘
```

---

## ✅ Success Checklist:

- [ ] Backend running on port 5000
- [ ] MongoDB running and accessible
- [ ] Email configuration correct in .env
- [ ] Gmail App Password valid
- [ ] Test email script passes
- [ ] User exists in database
- [ ] Frontend forgot password form works
- [ ] Backend logs show "Email sent successfully"
- [ ] Email received in inbox (or spam)
- [ ] Reset link works when clicked

---

## 🎯 Expected Flow:

1. **User clicks** "Forgot Password"
2. **User enters** email address
3. **Frontend sends** POST to `/api/auth/forgot-password`
4. **Backend checks** if user exists
5. **Backend generates** reset token (valid 1 hour)
6. **Backend saves** token to `password_resets` collection
7. **Backend sends** email with reset link
8. **Backend logs** "Password reset email sent to {email}"
9. **Backend returns** success message
10. **Frontend shows** "Check Your Email" message
11. **User receives** email within 1-2 minutes
12. **User clicks** reset link in email
13. **User enters** new password
14. **Password updated** successfully

---

## 🚀 Quick Test Command:

```bash
# All-in-one test
cd backend && \
python tse
 databaists inexent if user il only sual ema)
- Actmerationl enurevent emaicurity: p(se message s success returnend alwaysck
- Ba **once** usedn only betoken ca- Each  hour**
ires in **1xp eReset tokenst
- older** firam f*spheck * Always ctes
-nue 1-2 mi** - may takynchronous **asing isendEmail s

-  📝 Notes:##

---

"
```il inbox!heck emacall OK - CI n✅ AP"\o ' && \
ech.edu"}datams"student01@mail":  '{"e \
  -don"ation/jsType: applicontent-
  -H "Cassword \h/forgot-pautapi/t:5000/alhosttp://loc-X POST h&& \
curl onfig OK" Email c
echo "✅ \ail.py && est_em