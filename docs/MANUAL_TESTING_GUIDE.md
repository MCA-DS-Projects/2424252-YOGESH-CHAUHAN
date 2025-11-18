# Manual Testing Guide

## Prerequisites
- Backend server running on `http://localhost:5000`
- Frontend running on `http://localhost:3000`
- Test accounts created:
  - Teacher A: `teacherA@example.com` / `password123`
  - Teacher B: `teacherB@example.com` / `password123`
  - Student: `student@example.com` / `password123`

---

## Test Suite 1: Mock Data Removal ✅

### Test 1.1: Student Dashboard - No Mock Data
**Steps:**
1. Login as student
2. Navigate to dashboard (`/dashboard`)
3. Open browser DevTools → Network tab
4. Refresh page

**Expected Results:**
- ✅ All course data comes from API calls
- ✅ Progress bars show real data (not random)
- ✅ Stats cards show calculated values
- ✅ No hardcoded "7 days streak" or "Daily goal: 2 hours"
- ✅ Achievements section shows real unlocked achievements or empty state

**Verify:**
- Check Network tab for API calls:
  - `GET /api/courses`
  - `GET /api/assignments`
  - `GET /api/achievements`
  - `GET /api/ai/recommendations`

### Test 1.2: Analytics Page - No Mock Data
**Steps:**
1. Navigate to analytics page (`/analytics`)
2. Check all stats and charts

**Expected Results:**
- ✅ Stats show real data or "N/A"
- ✅ Charts show data from API or empty state
- ✅ No hardcoded "124.5h" or "87%" values
- ✅ If API fails, shows error message with fallback

### Test 1.3: Achievements Page - Database Driven
**Steps:**
1. Navigate to achievements page (`/achievements`)
2. Check achievements display

**Expected Results:**
- ✅ Shows achievements from database
- ✅ Unlocked achievements show unlock date
- ✅ Locked achievements show progress bar
- ✅ No hardcoded rank number

---

## Test Suite 2: Teacher Dashboard & Permissions

### Test 2.1: Teacher Can Only See Own Courses
**Steps:**
1. Login as Teacher A
2. Navigate to dashboard
3. Note the courses displayed
4. Logout and login as Teacher B
5. Navigate to dashboard

**Expected Results:**
- ✅ Teacher A sees only courses they created
- ✅ Teacher B sees only courses they created
- ✅ No overlap in course lists

**Verify in DevTools:**
```
GET /api/teacher/courses
Response should filter by teacher_id
```

### Test 2.2: Teacher Can Edit Own Course
**Steps:**
1. Login as Teacher A
2. Navigate to "My Courses"
3. Click on one of your courses
4. Click "Edit Course"
5. Change title to "Updated Course Title"
6. Click "Save"

**Expected Results:**
- ✅ Course updates successfully
- ✅ Success message appears
- ✅ New title displays immediately

**Verify in DevTools:**
```
PUT /api/courses/{course_id}
Status: 200 OK
Response: { "title": "Updated Course Title", ... }
```

### Test 2.3: Teacher Cannot Edit Other Teacher's Course
**Steps:**
1. Login as Teacher A
2. Get course ID from Teacher B (from database or API)
3. Try to access edit page: `/courses/{teacher_b_course_id}/edit`
4. Or use DevTools Console:
```javascript
fetch('http://localhost:5000/api/courses/teacher_b_course_id', {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ title: 'Hacked' })
})
```

**Expected Results:**
- ✅ Returns 403 Forbidden
- ✅ Error message: "Unauthorized: You are not the instructor of this course"
- ✅ Course is NOT updated

---

## Test Suite 3: Assignment Delete & Edit

### Test 3.1: Teacher Can Delete Own Assignment
**Steps:**
1. Login as Teacher A
2. Navigate to course with assignments
3. Click on an assignment
4. Click "Delete Assignment"
5. Confirm deletion

**Expected Results:**
- ✅ Confirmation dialog appears
- ✅ After confirmation, assignment is deleted
- ✅ Success message: "Assignment deleted successfully"
- ✅ Assignment removed from list immediately (optimistic UI)
- ✅ Students enrolled in course receive notification

**Verify in DevTools:**
```
DELETE /api/assignments/{assignment_id}
Status: 200 OK
Response: { "message": "Assignment deleted successfully", "archived_submissions": 5 }
```

**Verify in Database:**
- Assignment marked as `is_deleted: true`
- Submissions marked as `is_archived: true`
- Notifications created for students

### Test 3.2: Teacher Can Edit Own Assignment
**Steps:**
1. Login as Teacher A
2. Navigate to assignment
3. Click "Edit Assignment"
4. Change:
   - Title: "Updated Assignment"
   - Due date: +7 days
   - Max points: 150
5. Click "Save"

**Expected Results:**
- ✅ Assignment updates successfully
- ✅ Changes reflect immediately
- ✅ If due date changed, students receive notification

**Verify in DevTools:**
```
PUT /api/assignments/{assignment_id}
Status: 200 OK
Response: { "title": "Updated Assignment", "max_points": 150, ... }
```

### Test 3.3: Optimistic UI with Rollback
**Steps:**
1. Login as Teacher A
2. Open DevTools → Network tab
3. Set network to "Offline"
4. Try to delete an assignment
5. Set network back to "Online"

**Expected Results:**
- ✅ Assignment disappears immediately (optimistic)
- ✅ After network error, assignment reappears (rollback)
- ✅ Error message: "Failed to delete assignment"
- ✅ No data corruption

### Test 3.4: Student Cannot Delete Assignment
**Steps:**
1. Login as Student
2. Try to access assignment delete via DevTools:
```javascript
fetch('http://localhost:5000/api/assignments/assignment_id', {
  method: 'DELETE',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
  }
})
```

**Expected Results:**
- ✅ Returns 403 Forbidden
- ✅ Error: "Unauthorized: Only teachers can delete assignments"

---

## Test Suite 4: Notifications Optimization

### Test 4.1: Polling Frequency
**Steps:**
1. Login as any user
2. Open DevTools → Network tab
3. Filter by "unread-count"
4. Watch for requests
5. Note timestamps

**Expected Results:**
- ✅ Requests occur every 30 seconds (not 5-10 seconds)
- ✅ Response time < 100ms
- ✅ Response body is minimal: `{ "count": 5 }`

**Verify:**
```
GET /api/notifications/unread-count
Response Time: < 100ms
Response Size: < 50 bytes
```

### Test 4.2: Exponential Backoff When Idle
**Steps:**
1. Login and stay on dashboard
2. Open DevTools → Network tab
3. Switch to another browser tab
4. Wait 1 minute
5. Check network requests

**Expected Results:**
- ✅ When tab is active: polling every 30s
- ✅ When tab is hidden: polling slows to 60s
- ✅ When tab becomes active again: returns to 30s

### Test 4.3: Cache Performance
**Steps:**
1. Login as user
2. Open DevTools → Network tab
3. Make multiple rapid requests to unread count:
```javascript
for(let i=0; i<10; i++) {
  fetch('http://localhost:5000/api/notifications/unread-count', {
    headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
  }).then(r => r.json()).then(console.log);
}
```

**Expected Results:**
- ✅ All 10 requests return same count
- ✅ All responses < 100ms
- ✅ Backend uses cache (check logs for "Cache hit")

### Test 4.4: Database Index Performance
**Steps:**
1. Check database query performance:
```sql
EXPLAIN ANALYZE 
SELECT COUNT(*) FROM notifications 
WHERE user_id = 'user_123' AND read = false;
```

**Expected Results:**
- ✅ Query uses index: `idx_notifications_user_read`
- ✅ Execution time < 10ms
- ✅ No full table scan

---

## Test Suite 5: Gemini AI Resilience

### Test 5.1: Retry on Transient Errors
**Steps:**
1. Login as student
2. Navigate to dashboard
3. Click "Generate Learning Path"
4. Simulate network issue (disconnect briefly)
5. Reconnect

**Expected Results:**
- ✅ Shows loading state
- ✅ Automatically retries (check DevTools for multiple requests)
- ✅ Eventually succeeds or shows error after 3 retries
- ✅ No UI crash

### Test 5.2: Circuit Breaker Pattern
**Steps:**
1. Simulate Gemini API failure (backend returns 500)
2. Make 5 consecutive AI requests
3. Make 6th request

**Expected Results:**
- ✅ First 5 requests: Try and fail
- ✅ 6th request: Immediately returns fallback (circuit open)
- ✅ Fallback message: "AI service temporarily unavailable"
- ✅ After 60 seconds: Circuit tries again (half-open)

### Test 5.3: Background Job Processing (Optional)
**Steps:**
1. Request learning path generation
2. Check response

**Expected Results:**
- ✅ Returns 202 Accepted immediately
- ✅ Response includes: `{ "job_id": "job_123", "status": "processing" }`
- ✅ Frontend polls for result
- ✅ When ready, displays learning path
- ✅ UI remains responsive during processing

### Test 5.4: Graceful Degradation
**Steps:**
1. Disconnect from internet
2. Try to use AI features
3. Reconnect

**Expected Results:**
- ✅ Shows cached recommendations if available
- ✅ Shows friendly error message
- ✅ Suggests alternative actions
- ✅ No blank screens or crashes

---

## Test Suite 6: End-to-End Workflows

### Workflow 1: Teacher Creates and Manages Course
**Steps:**
1. Login as Teacher A
2. Click "Create Course"
3. Fill in course details:
   - Title: "Test Course"
   - Description: "Test Description"
   - Add 2 modules with 2 lessons each
4. Click "Create Course"
5. Verify course appears in "My Courses"
6. Click on course
7. Click "Create Assignment"
8. Fill assignment details
9. Click "Create"
10. Edit assignment title
11. Delete assignment
12. Edit course title
13. Delete course

**Expected Results:**
- ✅ All operations succeed
- ✅ Proper permissions enforced
- ✅ UI updates immediately
- ✅ No errors in console

### Workflow 2: Student Enrolls and Completes Work
**Steps:**
1. Login as Student
2. Browse courses
3. Enroll in "Test Course"
4. View course materials
5. Complete a lesson
6. Submit assignment
7. Check notifications
8. View achievements

**Expected Results:**
- ✅ Enrollment successful
- ✅ Progress tracked correctly
- ✅ Assignment submission works
- ✅ Notifications received
- ✅ Achievements unlock when criteria met

### Workflow 3: Teacher Grades and Provides Feedback
**Steps:**
1. Login as Teacher A
2. Navigate to "Pending Grades"
3. Click on a submission
4. Enter grade and feedback
5. Click "Submit Grade"
6. Verify student receives notification

**Expected Results:**
- ✅ Grade saved successfully
- ✅ Feedback visible to student
- ✅ Student notified
- ✅ Assignment marked as graded

---

## Performance Benchmarks

### Load Testing
```bash
# Test notification endpoint
ab -n 1000 -c 10 -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/api/notifications/unread-count

# Expected:
# - Requests per second: > 100
# - Mean response time: < 100ms
# - 0% failed requests
```

### Database Query Performance
```sql
-- Should use index
EXPLAIN ANALYZE 
SELECT * FROM notifications 
WHERE user_id = 'user_123' AND read = false 
ORDER BY created_at DESC LIMIT 20;

-- Expected: < 10ms execution time
```

### API Response Times
| Endpoint | Expected Time | Max Acceptable |
|----------|--------------|----------------|
| GET /api/notifications/unread-count | < 50ms | 100ms |
| GET /api/courses | < 200ms | 500ms |
| GET /api/achievements | < 300ms | 1000ms |
| POST /api/ai/chat | < 2s | 5s |
| POST /api/ai/learning-path | < 3s | 10s |

---

## Browser Compatibility Testing

### Test on Multiple Browsers:
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)

### Test Responsive Design:
- ✅ Desktop (1920x1080)
- ✅ Tablet (768x1024)
- ✅ Mobile (375x667)

---

## Accessibility Testing

### Keyboard Navigation:
1. Use Tab key to navigate
2. Use Enter/Space to activate buttons
3. Use Escape to close modals

**Expected:**
- ✅ All interactive elements reachable
- ✅ Focus indicators visible
- ✅ Logical tab order

### Screen Reader:
1. Enable screen reader (NVDA/JAWS/VoiceOver)
2. Navigate through pages

**Expected:**
- ✅ All content announced
- ✅ Form labels present
- ✅ Error messages announced

---

## Security Testing

### Test 1: SQL Injection
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com OR 1=1--", "password": "anything"}'
```
**Expected:** ✅ Login fails, no SQL injection

### Test 2: XSS Prevention
```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "<script>alert(\"XSS\")</script>"}'
```
**Expected:** ✅ Script tags escaped, no XSS execution

### Test 3: CSRF Protection
**Expected:** ✅ All state-changing requests require valid token

---

## Monitoring & Logging

### Check Logs:
```bash
# Backend logs
tail -f backend/logs/app.log

# Look for:
# - No excessive errors
# - Reasonable response times
# - No suspicious activity
```

### Check Metrics:
```bash
# Prometheus metrics
curl http://localhost:5000/metrics

# Verify:
# - notification_polls_total increasing
# - gemini_request_duration_seconds reasonable
# - No high error rates
```

---

## Rollback Testing

### Test Rollback Procedure:
1. Deploy new version
2. Verify it works
3. Introduce breaking change
4. Rollback to previous version
5. Verify system still works

**Expected:**
- ✅ Rollback completes in < 5 minutes
- ✅ No data loss
- ✅ All features functional

---

## Sign-Off Checklist

Before marking as complete, verify:

- [ ] All mock data removed
- [ ] Teacher permissions working
- [ ] Assignment delete/edit working
- [ ] Notifications optimized (< 100ms)
- [ ] Gemini errors handled gracefully
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Security tests passed
- [ ] Documentation complete
- [ ] Monitoring configured

---

## Troubleshooting

### Issue: Notifications polling too frequently
**Solution:** Check `useNotifications` hook, verify interval is 30000ms

### Issue: Teacher can edit other teacher's course
**Solution:** Check backend permission middleware, verify teacher_id check

### Issue: Gemini timeouts crash UI
**Solution:** Verify circuit breaker is active, check retry logic

### Issue: Database queries slow
**Solution:** Check indexes exist, run EXPLAIN ANALYZE on slow queries

### Issue: Cache not working
**Solution:** Verify Redis is running, check cache TTL configuration
