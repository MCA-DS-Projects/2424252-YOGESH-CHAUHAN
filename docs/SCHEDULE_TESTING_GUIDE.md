# Schedule Page - Testing Guide

## ✅ Implementation Complete

Schedule page ab fully functional hai with assignment integration aur status tracking.

## Testing Steps

### 1. Student Login Test

**Test Case 1: View Assignments in Schedule**
```
1. Login as a student
2. Navigate to Schedule page
3. Verify:
   ✓ Teacher ke diye gaye assignments calendar mein dikhte hain
   ✓ Assignment colors correct hain:
     - Red (📝) = Pending
     - Yellow (⏳) = Submitted
     - Green (✅) = Graded
   ✓ Legend top par visible hai
```

**Test Case 2: Add Personal Event**
```
1. Click "Add Event" button
2. Fill event details:
   - Title: "Study Session"
   - Type: Class/Meeting/etc.
   - Date: Select future date
   - Start Time: 10:00
   - End Time: 12:00
   - Course: (Optional)
   - Location: "Library"
3. Click "Add Event"
4. Verify:
   ✓ Event calendar mein dikhta hai
   ✓ Success toast message aata hai
   ✓ Event details correct hain
```

**Test Case 3: View Assignment Details**
```
1. Click on any assignment (red/yellow/green event)
2. Verify modal shows:
   ✓ Assignment title
   ✓ "Assignment Deadline" label
   ✓ Status badge (Pending/Submitted/Graded)
   ✓ Course name
   ✓ Due date with "(Due Date)" label
   ✓ Description with status information
   ✓ Grade (if graded)
```

### 2. Teacher Login Test

**Test Case 1: View Own Schedule**
```
1. Login as teacher
2. Navigate to Schedule page
3. Verify:
   ✓ Personal events dikhte hain
   ✓ Created assignments bhi dikhte hain
   ✓ Legend visible hai
```

**Test Case 2: Create Assignment and Check Schedule**
```
1. Go to Courses page
2. Select a course
3. Create new assignment with due date
4. Navigate back to Schedule page
5. Verify:
   ✓ New assignment calendar mein dikhai deta hai
   ✓ Due date correct hai
   ✓ Color red hai (pending status)
```

### 3. Edge Cases Testing

**Test Case 1: Multiple Events on Same Day**
```
1. Add multiple events on same date
2. Add assignment with same due date
3. Verify:
   ✓ All events visible hain
   ✓ Scrollable if needed
   ✓ Click karke details dekh sakte hain
```

**Test Case 2: Past Due Assignments**
```
1. Check assignments with past due dates
2. Verify:
   ✓ Still visible in calendar
   ✓ Color based on status (not date)
   ✓ Details accessible
```

**Test Case 3: No Assignments**
```
1. Login as student with no assignments
2. Navigate to Schedule
3. Verify:
   ✓ Only personal events dikhte hain
   ✓ No errors
   ✓ Can add new events
```

**Test Case 4: Long Titles/Descriptions**
```
1. Create event with very long title
2. Create assignment with long description
3. Verify:
   ✓ Text truncates properly in calendar
   ✓ Full text visible in modal
   ✓ No layout breaking
```

### 4. Navigation Testing

**Test Case 1: Week Navigation**
```
1. Click "Next" arrow
2. Verify: Next week shows with correct events
3. Click "Previous" arrow
4. Verify: Previous week shows
5. Click "Today" button
6. Verify: Current week shows
```

**Test Case 2: Month Changes**
```
1. Navigate to different months
2. Verify:
   ✓ Events load correctly
   ✓ Assignments show on correct dates
   ✓ No duplicate events
```

### 5. Status Change Testing

**Test Case 1: Submit Assignment**
```
1. Find pending assignment (red 📝)
2. Go to Assignments page
3. Submit the assignment
4. Return to Schedule page
5. Verify:
   ✓ Assignment color changed to yellow (⏳)
   ✓ Status shows "Submitted"
   ✓ Modal shows updated status
```

**Test Case 2: Assignment Graded**
```
1. After teacher grades assignment
2. Refresh Schedule page
3. Verify:
   ✓ Assignment color changed to green (✅)
   ✓ Status shows "Graded"
   ✓ Grade visible in details
```

## Expected Behavior

### Visual Indicators
- **📝 Red**: Assignment not submitted yet
- **⏳ Yellow**: Assignment submitted, waiting for grade
- **✅ Green**: Assignment graded
- **🕐 Time**: Regular events show time

### Event Types
- **Class**: Blue color
- **Meeting**: Purple color
- **Deadline**: Red/Yellow/Green (based on status)
- **Exam**: Orange color
- **Office Hours**: Green color

### Auto-refresh
- Schedule automatically updates when:
  - New assignment created
  - Assignment status changes
  - New event added
  - Courses updated

## Common Issues & Solutions

### Issue 1: Assignments not showing
**Solution**: 
- Check if student is enrolled in course
- Verify assignment has valid due date
- Check LMSContext is loading assignments

### Issue 2: Wrong colors
**Solution**:
- Verify assignment status in database
- Check status mapping logic
- Refresh page to reload data

### Issue 3: Events not saving
**Solution**:
- Check all required fields filled
- Verify backend schedule API is running
- Check browser console for errors

## API Endpoints Used

```
GET  /schedule/events          - Fetch user events
POST /schedule/events          - Create new event
DELETE /schedule/events/:id    - Delete event

GET  /assignments              - Fetch assignments (from LMSContext)
GET  /courses                  - Fetch courses (from LMSContext)
```

## Success Criteria

✅ Students can see their personal events
✅ Students can see teacher's assignments with due dates
✅ Assignment status clearly visible (color + icon)
✅ Can add new personal events
✅ Event details modal shows complete information
✅ Legend helps users understand status indicators
✅ Auto-refresh works when data changes
✅ No errors in console
✅ Responsive design works on mobile

## Performance Notes

- Events load on component mount
- Auto-refresh when assignments/courses change
- Efficient data merging (user events + assignments)
- No unnecessary re-renders

---

**Implementation Status**: ✅ COMPLETE
**Last Updated**: November 17, 2025
**Files Modified**: `src/components/schedule/SchedulePage.tsx`
