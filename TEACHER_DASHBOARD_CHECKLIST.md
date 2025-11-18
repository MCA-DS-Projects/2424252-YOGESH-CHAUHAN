# Teacher Dashboard - Quick Verification Checklist

Use this checklist to quickly verify the teacher dashboard is working correctly.

## Pre-Flight Checks

### Backend Server
- [ ] MongoDB is running
- [ ] Backend server is running (`python backend/app.py`)
- [ ] Backend accessible at `http://localhost:5000`
- [ ] Health check passes: `http://localhost:5000/api/health`

### Frontend Server
- [ ] Frontend is running (`npm run dev`)
- [ ] Frontend accessible at `http://localhost:5173`
- [ ] No console errors on page load

## Teacher Account Setup

- [ ] Have a teacher account created
- [ ] Can login successfully
- [ ] JWT token is generated
- [ ] User role is 'teacher'

## Dashboard Verification

### 1. Dashboard Loads
- [ ] Dashboard page loads without errors
- [ ] Welcome section displays teacher name
- [ ] Stats cards show numbers (not loading forever)
- [ ] No "mock" or "test" data visible

### 2. Statistics Display
- [ ] Active Courses count is correct
- [ ] Total Students count is correct
- [ ] Pending Grades count is correct
- [ ] Course Rating displays
- [ ] Monthly growth stats show

### 3. Courses Section
- [ ] "My Courses" section displays
- [ ] Shows only courses created by this teacher
- [ ] Each course shows:
  - [ ] Course title and description
  - [ ] Enrolled students count
  - [ ] Total assignments count
  - [ ] Active/Inactive status
  - [ ] "Manage" link works
- [ ] "New Course" button is visible
- [ ] "View All" link works (if >3 courses)

### 4. Pending Grades Section
- [ ] "Pending Grades" section displays
- [ ] Shows assignments with submissions
- [ ] Each assignment shows:
  - [ ] Assignment title
  - [ ] Course name
  - [ ] Submission count
  - [ ] "Grade" link
- [ ] "View All" link works (if >5 assignments)

### 5. Quick Actions
- [ ] All 4 quick action buttons visible:
  - [ ] Create Course
  - [ ] New Assignment
  - [ ] Grade Assignments
  - [ ] View Analytics
- [ ] Each button links to correct page

### 6. Sidebar Widgets
- [ ] Learner Insights widget displays
- [ ] Today's Schedule section shows
- [ ] Recent Announcements section shows
- [ ] AI Teaching Assistant section shows

### 7. Refresh Functionality
- [ ] Manual refresh button (🔄) is visible
- [ ] Clicking refresh updates data
- [ ] Toast notification shows on refresh
- [ ] No duplicate refresh requests

## Permission Checks

### View Permissions
- [ ] Can see only own courses
- [ ] Cannot see other teachers' courses
- [ ] Can see students in own courses
- [ ] Can see assignments for own courses

### Edit Permissions
- [ ] Can edit own courses
- [ ] Cannot edit other teachers' courses
- [ ] Can create new courses
- [ ] Can create assignments for own courses

### Delete Permissions
- [ ] Can delete own courses
- [ ] Cannot delete other teachers' courses
- [ ] Deleted courses are soft-deleted (is_active: false)
- [ ] Students are notified of course deletion

## Data Verification

### No Mock Data
- [ ] No courses with "Test" or "Mock" in title
- [ ] No hardcoded student counts
- [ ] No placeholder data
- [ ] All data matches database

### Real-Time Sync
- [ ] Creating a course shows immediately (after refresh)
- [ ] Deleting a course removes it (after refresh)
- [ ] New enrollments update student count
- [ ] New submissions update pending count

### Database Consistency
- [ ] Course count matches MongoDB
- [ ] Student count matches enrollments
- [ ] Assignment count matches database
- [ ] All IDs are valid ObjectIds

## Error Handling

### Network Errors
- [ ] Shows error message if backend is down
- [ ] "Try Again" button appears
- [ ] Doesn't crash the app
- [ ] Preserves user session

### Partial Failures
- [ ] Shows available data if some APIs fail
- [ ] Warning banner for failed sections
- [ ] Can retry without losing data
- [ ] Error messages are user-friendly

### Authentication Errors
- [ ] Redirects to login if token expired
- [ ] Shows "session expired" message
- [ ] Doesn't expose sensitive errors
- [ ] Preserves intended destination

## Performance Checks

### Loading Speed
- [ ] Dashboard loads in <3 seconds
- [ ] Skeleton loaders show while loading
- [ ] No long white screens
- [ ] Smooth transitions

### Caching
- [ ] Second load is faster (cached)
- [ ] Manual refresh clears cache
- [ ] Cache expires after 5 minutes
- [ ] No stale data issues

### Responsiveness
- [ ] Works on desktop (1920x1080)
- [ ] Works on laptop (1366x768)
- [ ] Works on tablet (768x1024)
- [ ] Works on mobile (375x667)

## Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

## Security Checks

### Authentication
- [ ] JWT token required for all requests
- [ ] Token in Authorization header
- [ ] Token expires after 2 hours
- [ ] Refresh token works

### Authorization
- [ ] Role checked on backend
- [ ] Teacher can't access admin routes
- [ ] Teacher can't access other teachers' data
- [ ] Student can't access teacher dashboard

### Data Protection
- [ ] No sensitive data in URLs
- [ ] No passwords in logs
- [ ] No tokens in console
- [ ] HTTPS in production

## Automated Verification

Run the verification script:
```bash
python verify_teacher_dashboard.py
```

Expected output:
```
✅ Teacher Login: PASSED
✅ Dashboard Stats: PASSED
✅ Teacher Courses: PASSED
✅ Teacher Assignments: PASSED
✅ No Mock Data: PASSED

🎉 All verifications PASSED!
```

## Common Issues & Solutions

### Issue: Dashboard shows no courses
**Solution:**
1. Verify you're logged in as teacher
2. Check if you've created any courses
3. Run: `db.courses.find({teacher_id: "<your_user_id>"})`
4. Create a test course to verify

### Issue: Stats show 0 for everything
**Solution:**
1. Check backend logs for errors
2. Verify MongoDB connection
3. Check if analytics endpoint is working
4. Create test data if database is empty

### Issue: Refresh button doesn't work
**Solution:**
1. Check browser console for errors
2. Verify backend is running
3. Check network tab for failed requests
4. Clear browser cache and try again

### Issue: Permission denied errors
**Solution:**
1. Verify JWT token is valid
2. Check user role is 'teacher'
3. Verify course ownership
4. Check backend logs for details

## Sign-Off

### Tested By
- Name: _______________
- Date: _______________
- Role: _______________

### Results
- [ ] All checks passed
- [ ] Some issues found (documented below)
- [ ] Major issues found (requires fix)

### Issues Found
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Notes
_____________________________________________________
_____________________________________________________
_____________________________________________________

---

**Checklist Version:** 1.0  
**Last Updated:** November 17, 2025  
**Next Review:** After major updates
