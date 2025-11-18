# Implementation Plan - Data & Operations Fix

## ✅ Phase 1: Mock Data Removal (COMPLETED)

### Completed Tasks:
1. **Student Dashboard**
   - ✅ Removed random progress generation
   - ✅ Removed hardcoded stats (study streak, daily goals)
   - ✅ Integrated with AchievementAPI for recent achievements
   - ✅ All data now from database or calculated from real data

2. **Analytics Page**
   - ✅ Removed all hardcoded learning data
   - ✅ Integrated with analyticsAPI
   - ✅ Added fallback calculations from course data
   - ✅ Proper error handling and loading states

3. **Achievements Page**
   - ✅ Already working with backend
   - ✅ Changed hardcoded rank to dynamic total count
   - ✅ Proper filtering and search

4. **Teacher Dashboard**
   - ✅ Already clean - no mock data
   - ✅ Uses TeacherAPI for all data

5. **Settings Page**
   - ✅ Removed Appearance section
   - ✅ Removed Language & Region section
   - ✅ Profile and password change working with backend

---

## 🔄 Phase 2: Teacher Dashboard & Permissions (IN PROGRESS)

### Current Status:
- Teacher dashboard exists and fetches data from backend
- Backend endpoint: `GET /api/teacher/courses`
- Returns only courses where user is instructor

### Required Checks:
1. ✅ Verify backend filters courses by teacher_id
2. ⚠️ Add permission checks for course edit/delete
3. ⚠️ Add permission checks for assignment operations

### Implementation Steps:

#### 2.1 Backend Permission Middleware
```python
# backend/middleware/permissions.py
def require_course_teacher(course_id):
    """Ensure logged-in user is teacher of the course"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            course = Course.query.get(course_id)
            if not course or course.teacher_id != user.id:
                return jsonify({'error': 'Unauthorized'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

#### 2.2 Apply to Routes
- `DELETE /api/courses/:id` - Add teacher check
- `PUT /api/courses/:id` - Add teacher check
- `DELETE /api/assignments/:id` - Add teacher check
- `PUT /api/assignments/:id` - Add teacher check

---

## 🔄 Phase 3: Assignment Delete & Edit (NEXT)

### 3.1 Backend Implementation

#### Delete Assignment Endpoint
```python
@assignments_bp.route('/<assignment_id>', methods=['DELETE'])
@jwt_required()
@require_course_teacher  # Check if user is teacher of course
def delete_assignment(assignment_id):
    """
    Delete assignment and related data
    - Mark assignment as deleted (soft delete)
    - Archive submissions
    - Send notifications to enrolled students
    """
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Soft delete
    assignment.is_deleted = True
    assignment.deleted_at = datetime.utcnow()
    
    # Archive submissions
    Submission.query.filter_by(assignment_id=assignment_id).update({
        'is_archived': True
    })
    
    # Create notification for students
    students = get_course_students(assignment.course_id)
    for student in students:
        create_notification(
            user_id=student.id,
            type='assignment_deleted',
            message=f'Assignment "{assignment.title}" has been removed'
        )
    
    db.session.commit()
    return jsonify({'message': 'Assignment deleted successfully'}), 200
```

#### Edit Assignment Endpoint
```python
@assignments_bp.route('/<assignment_id>', methods=['PUT', 'PATCH'])
@jwt_required()
@require_course_teacher
def update_assignment(assignment_id):
    """
    Update assignment fields
    - Validate permissions
    - Update allowed fields
    - Notify students of changes
    """
    assignment = Assignment.query.get_or_404(assignment_id)
    data = request.get_json()
    
    # Allowed fields
    allowed_fields = ['title', 'description', 'due_date', 'max_points', 'instructions']
    
    for field in allowed_fields:
        if field in data:
            setattr(assignment, field, data[field])
    
    assignment.updated_at = datetime.utcnow()
    
    # Notify students if due date changed
    if 'due_date' in data:
        notify_students_due_date_change(assignment)
    
    db.session.commit()
    return jsonify(assignment.to_dict()), 200
```

### 3.2 Frontend Implementation

#### Assignment Delete
```typescript
// src/services/assignmentAPI.ts
export const AssignmentAPI = {
  delete: async (assignmentId: string) => {
    return apiClient.delete(`/api/assignments/${assignmentId}`);
  },
  
  update: async (assignmentId: string, data: Partial<Assignment>) => {
    return apiClient.put(`/api/assignments/${assignmentId}`, data);
  }
};
```

#### Optimistic UI Update
```typescript
// In component
const handleDelete = async (assignmentId: string) => {
  // Optimistic update
  setAssignments(prev => prev.filter(a => a.id !== assignmentId));
  
  try {
    await AssignmentAPI.delete(assignmentId);
    showToast('Assignment deleted successfully', 'success');
  } catch (error) {
    // Rollback on error
    setAssignments(originalAssignments);
    showToast('Failed to delete assignment', 'error');
  }
};
```

### 3.3 Tests Required
```python
# backend/tests/test_assignments.py
def test_delete_assignment_as_teacher():
    """Teacher can delete their own assignment"""
    
def test_delete_assignment_as_other_teacher():
    """Other teacher cannot delete assignment"""
    
def test_delete_assignment_cascades():
    """Deleting assignment archives submissions"""
    
def test_update_assignment_permissions():
    """Only course teacher can update assignment"""
```

---

## 🔄 Phase 4: Notifications Optimization (NEXT)

### Current Issues:
- Aggressive polling (every 5-10 seconds)
- No caching
- Full notification objects returned for count

### 4.1 Backend Optimization

#### Add Redis Cache
```python
# backend/utils/cache.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_unread_count(ttl=10):
    """Cache unread count for 10 seconds"""
    def decorator(f):
        @wraps(f)
        def decorated_function(user_id, *args, **kwargs):
            cache_key = f'unread_count:{user_id}'
            cached = redis_client.get(cache_key)
            
            if cached:
                return int(cached)
            
            result = f(user_id, *args, **kwargs)
            redis_client.setex(cache_key, ttl, result)
            return result
        return decorated_function
    return decorator
```

#### Optimize Endpoint
```python
@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
@cache_unread_count(ttl=10)
def get_unread_count():
    """Return only count, not full objects"""
    user_id = get_jwt_identity()
    
    # Use COUNT query instead of fetching all
    count = Notification.query.filter_by(
        user_id=user_id,
        read=False
    ).count()
    
    return jsonify({'count': count}), 200
```

#### Add Database Index
```python
# backend/migrations/add_notification_indexes.py
def upgrade():
    op.create_index(
        'idx_notifications_user_read',
        'notifications',
        ['user_id', 'read']
    )
```

### 4.2 Frontend Optimization

#### Reduce Polling Frequency
```typescript
// src/hooks/useNotifications.ts
export const useNotifications = () => {
  const [pollingInterval, setPollingInterval] = useState(30000); // 30s default
  
  useEffect(() => {
    // Exponential backoff when idle
    const handleVisibilityChange = () => {
      if (document.hidden) {
        setPollingInterval(60000); // 1 minute when hidden
      } else {
        setPollingInterval(30000); // 30s when visible
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);
  
  // Poll with current interval
  useInterval(() => {
    fetchUnreadCount();
  }, pollingInterval);
};
```

#### WebSocket Alternative (Optional)
```typescript
// src/services/websocket.ts
export class NotificationWebSocket {
  private ws: WebSocket;
  
  connect(userId: string) {
    this.ws = new WebSocket(`ws://localhost:5000/ws/notifications/${userId}`);
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'unread_count') {
        updateUnreadCount(data.count);
      }
    };
  }
}
```

---

## 🔄 Phase 5: Gemini AI Timeout Handling (NEXT)

### Current Issues:
- No retry logic
- Timeouts block UI
- No fallback for failures

### 5.1 Retry with Exponential Backoff

```typescript
// src/utils/retry.ts
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error: any) {
      lastError = error;
      
      // Don't retry on 4xx errors
      if (error.response?.status >= 400 && error.response?.status < 500) {
        throw error;
      }
      
      // Exponential backoff
      const delay = baseDelay * Math.pow(2, i);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError!;
}
```

### 5.2 Background Job Processing

```python
# backend/tasks/ai_tasks.py
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def generate_learning_path(user_id, goal, timeframe):
    """Process AI request in background"""
    try:
        result = gemini_api.generate_learning_path(goal, timeframe)
        
        # Store result
        cache_result(f'learning_path:{user_id}', result, ttl=3600)
        
        # Notify user via WebSocket
        notify_user(user_id, 'learning_path_ready', result)
        
        return result
    except Exception as e:
        log_error(f'Gemini API failed: {e}')
        return None
```

### 5.3 Circuit Breaker Pattern

```typescript
// src/utils/circuitBreaker.ts
class CircuitBreaker {
  private failures = 0;
  private lastFailTime = 0;
  private state: 'closed' | 'open' | 'half-open' = 'closed';
  
  async execute<T>(fn: () => Promise<T>, fallback: () => T): Promise<T> {
    if (this.state === 'open') {
      // Check if we should try again
      if (Date.now() - this.lastFailTime > 60000) {
        this.state = 'half-open';
      } else {
        return fallback();
      }
    }
    
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      return fallback();
    }
  }
  
  private onSuccess() {
    this.failures = 0;
    this.state = 'closed';
  }
  
  private onFailure() {
    this.failures++;
    this.lastFailTime = Date.now();
    
    if (this.failures >= 5) {
      this.state = 'open';
    }
  }
}
```

---

## 📊 Phase 6: Testing & Monitoring

### 6.1 Unit Tests

```python
# backend/tests/test_teacher_permissions.py
def test_teacher_can_edit_own_course():
    """Teacher can edit their own course"""
    
def test_teacher_cannot_edit_other_course():
    """Teacher cannot edit another teacher's course"""
    
def test_assignment_delete_cascades():
    """Deleting assignment archives submissions"""
```

### 6.2 Integration Tests

```typescript
// src/tests/integration/teacher-workflow.test.ts
describe('Teacher Workflow', () => {
  it('should create, edit, and delete assignment', async () => {
    // Create
    const assignment = await createAssignment(courseId, data);
    expect(assignment.id).toBeDefined();
    
    // Edit
    const updated = await updateAssignment(assignment.id, { title: 'New Title' });
    expect(updated.title).toBe('New Title');
    
    // Delete
    await deleteAssignment(assignment.id);
    const deleted = await getAssignment(assignment.id);
    expect(deleted).toBeNull();
  });
});
```

### 6.3 Monitoring

```python
# backend/monitoring/metrics.py
from prometheus_client import Counter, Histogram

notification_poll_counter = Counter(
    'notification_polls_total',
    'Total notification polls',
    ['user_id']
)

gemini_request_duration = Histogram(
    'gemini_request_duration_seconds',
    'Gemini API request duration'
)

@notifications_bp.route('/unread-count')
def get_unread_count():
    notification_poll_counter.labels(user_id=user_id).inc()
    # ... rest of code
```

---

## 📝 Deliverables Checklist

### Code Changes:
- [ ] Backend permission middleware
- [ ] Assignment delete/edit endpoints
- [ ] Notification optimization (cache + index)
- [ ] Gemini retry logic
- [ ] Circuit breaker implementation
- [ ] Background job setup (optional)

### Tests:
- [ ] Unit tests for permissions
- [ ] Integration tests for assignment operations
- [ ] Load tests for notifications endpoint

### Documentation:
- [ ] API documentation (Postman collection)
- [ ] Manual testing steps
- [ ] Deployment guide
- [ ] Monitoring setup guide

### Monitoring:
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Alert rules for 5xx errors
- [ ] Alert rules for high latency

---

## 🚀 Deployment Order

1. **Database Changes**
   - Add notification indexes
   - Add soft delete columns to assignments

2. **Backend Deployment**
   - Deploy permission middleware
   - Deploy optimized endpoints
   - Deploy retry logic

3. **Frontend Deployment**
   - Deploy optimized polling
   - Deploy circuit breaker
   - Deploy UI improvements

4. **Monitoring Setup**
   - Configure Prometheus
   - Set up Grafana dashboards
   - Configure alerts

---

## 📋 Manual Testing Steps

### Test Assignment Operations:
1. Login as Teacher A
2. Create assignment in Course X
3. Try to edit → Should succeed
4. Try to delete → Should succeed
5. Login as Teacher B
6. Try to edit Course X assignment → Should fail (403)
7. Try to delete Course X assignment → Should fail (403)

### Test Notifications:
1. Open browser DevTools → Network tab
2. Monitor `/api/notifications/unread-count` calls
3. Verify polling interval is 30s
4. Switch to another tab
5. Verify polling slows to 60s
6. Check response time < 100ms

### Test Gemini Resilience:
1. Simulate Gemini timeout (disconnect network)
2. Request learning path
3. Verify fallback message appears
4. Reconnect network
5. Verify circuit breaker recovers

---

## 🎯 Success Criteria

- ✅ No mock data in any component
- ✅ Teacher can only edit/delete their own courses/assignments
- ✅ Notification polling ≤ 30s with backoff
- ✅ Unread count endpoint < 100ms response time
- ✅ Gemini failures don't crash UI
- ✅ All tests passing
- ✅ Monitoring dashboards showing metrics
