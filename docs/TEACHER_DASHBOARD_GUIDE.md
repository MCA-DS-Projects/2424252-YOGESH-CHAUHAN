# Teacher Dashboard User Guide

## Overview

The Teacher Dashboard is a comprehensive interface designed specifically for teachers to manage their courses, track student progress, grade assignments, and access analytics—all powered by real-time data from the MongoDB database.

## Key Features

### 1. Dashboard Statistics

**Real-time metrics displayed:**
- **Active Courses:** Number of courses you're currently teaching
- **Total Students:** Total number of students enrolled across all your courses
- **Pending Grades:** Number of assignments waiting to be graded
- **Course Rating:** Average rating across all your courses
- **Monthly Growth:** Track changes in courses, students, and ratings

**Data Source:** `/api/analytics/teacher/dashboard`

### 2. My Courses Section

**Displays:**
- Course title and description
- Number of enrolled students
- Number of assignments
- Course status (Active/Inactive)
- Quick access to course management

**Features:**
- View up to 3 recent courses on dashboard
- "View All" link to see complete course list
- "New Course" button to create courses
- Direct links to manage each course

**Data Source:** `/api/courses` (filtered by teacher_id)

**Course Analytics Included:**
- Enrolled student count
- Average student progress
- Active students (last 7 days)
- Engagement rate
- Completion rate
- Assignment statistics
- Average grades
- Student performance breakdown

### 3. Pending Grades Section

**Shows:**
- Assignments with ungraded submissions
- Course name for each assignment
- Number of pending submissions
- Quick link to grade assignments

**Features:**
- View up to 5 pending assignments
- Direct link to grading interface
- Real-time submission counts

**Data Source:** `/api/assignments` (filtered by teacher's courses)

### 4. Quick Actions

**One-click access to:**
- Create Course
- New Assignment
- Grade Assignments
- View Analytics

### 5. Learner Insights Widget

**AI-powered insights:**
- Student performance trends
- Engagement patterns
- Recommendations for improvement

### 6. Schedule & Announcements

**Stay organized with:**
- Today's schedule
- Recent announcements
- Important notifications

### 7. AI Teaching Assistant

**Get help with:**
- Student performance analysis
- Content suggestions
- Teaching strategy recommendations

## Data Flow

```
Teacher Dashboard
    ↓
Teacher API Service
    ↓
Backend API Routes
    ↓
MongoDB Database
```

### Authentication & Authorization

1. **JWT Token:** All requests require valid JWT authentication
2. **Role Check:** Backend verifies user role is 'teacher'
3. **Data Filtering:** Courses automatically filtered by teacher_id
4. **Permission Checks:** Edit/delete operations verify ownership

## Refresh Mechanisms

### Manual Refresh
- Click the refresh button (🔄) in the welcome section
- Debounced to prevent multiple simultaneous requests
- Invalidates cache and fetches fresh data
- Shows toast notification on success/failure

### Auto-Refresh
- Automatic refresh every 5 minutes (via LMS Context)
- Refreshes when tab becomes visible (if >1 min since last refresh)
- Can be disabled in settings

### Cache Strategy
- Dashboard stats cached for 5 minutes
- Courses cached for 5 minutes
- Assignments cached for 5 minutes
- Manual refresh clears all caches

## Error Handling

### Partial Success
If some API calls fail, the dashboard will:
- Display available data
- Show warning banner for failed sections
- Allow retry without losing loaded data

### Complete Failure
If all API calls fail:
- Show error message
- Display "Try Again" button
- Preserve user session

### Network Issues
- Detects offline status
- Shows user-friendly error messages
- Suggests checking network connection

## Permission Checks

### View Courses
✅ Only courses where you are the teacher

### Edit Course
✅ Only if you created the course OR you're an admin

### Delete Course
✅ Only if you created the course OR you're an admin
- Soft delete (sets is_active: False)
- Notifies enrolled students

### View Students
✅ Only students enrolled in your courses

### Grade Assignments
✅ Only assignments from your courses

### View Analytics
✅ Only analytics for your courses and students

## Comparison: Teacher vs Student Dashboard

| Feature | Teacher Dashboard | Student Dashboard |
|---------|------------------|-------------------|
| **View** | All courses they teach | Courses they're enrolled in |
| **Analytics** | Class-wide statistics | Personal progress |
| **Assignments** | Grade submissions | Submit assignments |
| **Students** | View all enrolled students | View classmates (if enabled) |
| **Course Management** | Create, edit, delete | Enroll, unenroll |
| **Grading** | Grade all submissions | View own grades |
| **AI Assistant** | Teaching strategies | Study recommendations |

## Best Practices

### 1. Regular Monitoring
- Check pending grades daily
- Review student engagement weekly
- Monitor course completion rates

### 2. Timely Grading
- Grade assignments within 48 hours
- Provide constructive feedback
- Use rubrics for consistency

### 3. Student Engagement
- Track active vs inactive students
- Reach out to struggling students
- Celebrate high performers

### 4. Course Optimization
- Review analytics monthly
- Update content based on feedback
- Adjust difficulty based on performance

### 5. Communication
- Post regular announcements
- Respond to student questions
- Use notifications effectively

## Troubleshooting

### Dashboard Not Loading
1. Check if backend server is running
2. Verify MongoDB connection
3. Check browser console for errors
4. Try manual refresh

### No Courses Showing
1. Verify you're logged in as a teacher
2. Check if you've created any courses
3. Verify courses are active (not deleted)
4. Check backend logs for errors

### Stats Not Updating
1. Wait for auto-refresh (5 minutes)
2. Try manual refresh
3. Clear browser cache
4. Check if data changed in database

### Permission Denied
1. Verify you're logged in as teacher
2. Check JWT token hasn't expired
3. Verify you own the course
4. Contact admin if issue persists

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/analytics/teacher/dashboard` | GET | Dashboard statistics |
| `/api/courses` | GET | Teacher's courses |
| `/api/assignments` | GET | Teacher's assignments |
| `/api/courses/:id/students` | GET | Course students |
| `/api/analytics/course/:id` | GET | Course analytics |
| `/api/grading/submissions` | GET | Pending submissions |

## Security Features

1. **JWT Authentication:** All requests require valid token
2. **Role Verification:** Backend checks user role
3. **Data Isolation:** Teachers only see their data
4. **Permission Checks:** Edit/delete verified
5. **Soft Delete:** Data preserved for audit
6. **Token Expiration:** 2-hour session timeout
7. **Token Blacklist:** Revoked tokens blocked

## Performance Optimization

1. **Caching:** Reduces redundant API calls
2. **Parallel Fetching:** Multiple APIs called simultaneously
3. **Lazy Loading:** Data loaded as needed
4. **Debouncing:** Prevents rapid refresh clicks
5. **Skeleton Loaders:** Better perceived performance

## Future Enhancements

### Planned Features
- WebSocket for real-time updates
- Bulk grading interface
- Advanced analytics dashboard
- Export reports (PDF/Excel)
- Course templates
- Automated grading for MCQs
- Video conferencing integration
- Assignment plagiarism detection

### Requested Features
- Mobile app
- Offline mode
- Custom rubrics
- Peer review system
- Gamification elements
- Integration with external LMS

## Support

### Getting Help
1. Check this guide first
2. Review audit report for technical details
3. Check backend logs for errors
4. Contact system administrator
5. Submit bug report with details

### Reporting Issues
Include:
- User role (teacher)
- Browser and version
- Steps to reproduce
- Error messages
- Screenshots if applicable

---

**Last Updated:** November 17, 2025  
**Version:** 1.0  
**Status:** Production Ready
