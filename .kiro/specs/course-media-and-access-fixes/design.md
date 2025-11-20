# Design Document

## Overview

This design addresses critical bugs in the EduNexa LMS that prevent the core learning workflow from functioning. The system currently has three major failure points:

1. **Thumbnail Upload/Display**: Course thumbnails are uploaded but not stored or displayed correctly
2. **Course Access**: Students cannot click course cards to access course content
3. **Video Playback**: Videos uploaded to modules fail to play due to incorrect file paths and API routing

The design focuses on fixing these issues while maintaining the existing architecture and ensuring data consistency across the MongoDB database, Flask backend, and React frontend.

## Architecture

### Current System Architecture
```
┌─────────────────┐
│  React Frontend │
│  (Port 5173)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Flask Backend  │
│  (Port 5000)    │
└────────┬────────┘
         │ MongoDB Driver
         ▼
┌─────────────────┐
│    MongoDB      │
│  (Port 27017)   │
└─────────────────┘
```

### File Storage Structure
```
backend/
├── uploads/
│   ├── thumbnails/     # Course thumbnail images
│   ├── videos/         # Course video files
│   ├── documents/      # Course document files
│   └── assignments/    # Assignment submission files
```

## Components and Interfaces

### 1. Thumbnail Management System

#### Backend Components

**File Upload Handler** (`backend/routes/courses.py`)
- Endpoint: `POST /api/courses/upload-thumbnail`
- Accepts: multipart/form-data with image file
- Validates: file type (jpg, jpeg, png, gif, webp), size (max 5MB)
- Generates: unique filename using UUID + timestamp
- Stores: file in `backend/uploads/thumbnails/`
- Returns: thumbnail URL path

**File Serving Handler** (`backend/routes/courses.py`)
- Endpoint: `GET /api/courses/thumbnails/<filename>`
- Validates: filename exists and is safe (no directory traversal)
- Serves: static file with appropriate MIME type
- No authentication required (public access for thumbnails)

**Course Creation Handler** (`backend/routes/courses.py`)
- Modified: `POST /api/courses/`
- Accepts: thumbnail URL from upload endpoint
- Stores: thumbnail path in course document
- Fallback: default placeholder if no thumbnail provided

#### Frontend Components

**Thumbnail Upload Component** (`src/components/courses/CreateCoursePage.tsx`)
- Provides: file input for thumbnail selection
- Previews: selected image before upload
- Uploads: thumbnail to backend before course creation
- Stores: returned thumbnail URL for course creation payload

**Course Card Component** (`src/components/dashboard/CourseCard.tsx`)
- Displays: thumbnail image from course.thumbnail field
- Handles: missing thumbnails with placeholder
- Optimizes: image loading with lazy loading

#### Database Schema

**courses collection**
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  thumbnail: String,  // FIXED: Store full path "/api/courses/thumbnails/filename.jpg"
  teacher_id: String,
  category: String,
  difficulty: String,
  created_at: Date,
  updated_at: Date
}
```

### 2. Course Access and Routing System

#### Backend Components

**Progress State Manager** (`backend/routes/progress.py`)
- Endpoint: `GET /api/progress/course/<course_id>`
- Returns: student's progress state for a course
- Creates: initial progress record if none exists
- Tracks: started status, last_accessed timestamp

**Progress Initialization** (`backend/routes/progress.py`)
- Endpoint: `POST /api/progress/course/<course_id>/start`
- Creates: progress record when student first accesses course
- Sets: started=true, last_accessed=current timestamp
- Returns: confirmation of progress initialization

#### Frontend Components

**Course Card Button Logic** (`src/components/dashboard/CourseCard.tsx`)
```typescript
interface CourseCardProps {
  course: Course;
  onClick: () => void;
  hasStarted: boolean;  // NEW: Determines button text
}

// Button rendering logic
{hasStarted ? (
  <button>Continue</button>
) : (
  <button>Start</button>
)}
```

**Student Dashboard** (`src/components/dashboard/StudentDashboard.tsx`)
- Fetches: progress state for each enrolled course
- Determines: Start vs Continue button state
- Handles: click event to navigate to course detail page
- Route: `/courses/<course_id>` or `/course-detail?id=<course_id>`

**Course Detail Page** (`src/components/courses/CourseDetailPage.tsx`)
- Initializes: progress tracking on first visit
- Updates: last_accessed timestamp on each visit
- Displays: course modules and materials

#### Database Schema

**progress collection** (NEW or MODIFIED)
```javascript
{
  _id: ObjectId,
  student_id: String,
  course_id: String,
  started: Boolean,  // FIXED: Track if course has been started
  last_accessed: Date,
  completed_materials: [String],  // Array of material IDs
  overall_progress: Number,  // Percentage 0-100
  created_at: Date,
  updated_at: Date
}
```

### 3. Video Upload, Storage, and Playback System

#### Backend Components

**Video Upload Handler** (`backend/routes/videos.py`)
- Endpoint: `POST /api/videos/upload`
- Accepts: multipart/form-data with video file
- Validates: file type (mp4, webm, ogg), size (max 500MB)
- Generates: unique filename using UUID
- Stores: file in `backend/uploads/videos/`
- Creates: video record in videos collection
- Returns: video ID and metadata

**Video Serving Handler** (`backend/routes/videos.py`)
- Endpoint: `GET /api/videos/<video_id>/stream`
- Validates: user has access to video's course
- Supports: HTTP range requests for streaming
- Serves: video file with proper MIME type
- Tracks: view count and watch progress

**Material Creation Handler** (`backend/routes/courses.py`)
- Modified: `POST /api/courses/<course_id>/materials`
- Links: video ID to course material
- Stores: video_id in material.content field
- Type: material.type = 'video'

#### Frontend Components

**Video Upload Component** (`src/components/courses/VideoUpload.tsx`)
- Provides: file input for video selection
- Shows: upload progress bar
- Validates: file size and type before upload
- Returns: video ID for material creation

**Video Player Component** (`src/components/courses/VideoPlayer.tsx`)
- Fetches: video stream from `/api/videos/<video_id>/stream`
- Supports: play, pause, seek, volume controls
- Tracks: watch time and progress
- Reports: progress to backend for tracking

**Course Detail Page - Video Section** (`src/components/courses/CourseDetailPage.tsx`)
- Lists: all video materials in modules
- Renders: VideoPlayer component when video is selected
- Updates: completion status when video is watched
- Displays: watch progress indicator

#### Database Schema

**videos collection** (NEW)
```javascript
{
  _id: ObjectId,
  filename: String,  // Unique filename on disk
  original_filename: String,  // Original upload filename
  file_path: String,  // Full path: /backend/uploads/videos/filename.mp4
  file_size: Number,  // Size in bytes
  mime_type: String,  // video/mp4, video/webm, etc.
  duration: Number,  // Duration in seconds (optional)
  uploaded_by: String,  // User ID of uploader
  created_at: Date
}
```

**materials collection** (MODIFIED)
```javascript
{
  _id: ObjectId,
  course_id: String,
  title: String,
  description: String,
  type: String,  // 'video', 'document', 'link'
  content: String,  // FIXED: Store video_id (references videos collection)
  order: Number,
  is_required: Boolean,
  created_at: Date
}
```

**video_progress collection** (NEW)
```javascript
{
  _id: ObjectId,
  student_id: String,
  video_id: String,
  course_id: String,
  watch_time: Number,  // Seconds watched
  last_watched: Date,
  completed: Boolean,  // Watched >80% of video
  created_at: Date,
  updated_at: Date
}
```

## Data Models

### Course Model
```python
class Course:
    _id: ObjectId
    title: str
    description: str
    thumbnail: str  # Path to thumbnail file
    teacher_id: str
    category: str
    difficulty: str
    duration: str
    prerequisites: List[str]
    learning_objectives: List[str]
    is_active: bool
    is_public: bool
    max_students: int
    created_at: datetime
    updated_at: datetime
```

### Video Model
```python
class Video:
    _id: ObjectId
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    duration: int
    uploaded_by: str
    created_at: datetime
```

### Material Model
```python
class Material:
    _id: ObjectId
    course_id: str
    title: str
    description: str
    type: str  # 'video', 'document', 'link'
    content: str  # video_id or document_id or URL
    order: int
    is_required: bool
    created_at: datetime
```

### Progress Model
```python
class Progress:
    _id: ObjectId
    student_id: str
    course_id: str
    started: bool
    last_accessed: datetime
    completed_materials: List[str]
    overall_progress: float
    created_at: datetime
    updated_at: datetime
```

### VideoProgress Model
```python
class VideoProgress:
    _id: ObjectId
    student_id: str
    video_id: str
    course_id: str
    watch_time: int
    last_watched: datetime
    completed: bool
    created_at: datetime
    updated_at: datetime
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Thumbnail file validation
*For any* file upload attempt, if the file is a valid image type (JPEG, PNG, GIF, WebP) and under 5MB, the system should accept it; otherwise, it should reject it with an appropriate error
**Validates: Requirements 1.1**

### Property 2: Thumbnail storage location consistency
*For any* uploaded thumbnail, the file should exist at the path `backend/uploads/thumbnails/<filename>` after upload completes
**Validates: Requirements 1.2**

### Property 3: Thumbnail filename uniqueness
*For any* two thumbnail uploads, even with the same original filename, the system should generate different unique filenames
**Validates: Requirements 1.3**

### Property 4: Thumbnail path round-trip
*For any* course created with a thumbnail, fetching the course from the database should return the same thumbnail path that was stored
**Validates: Requirements 1.4**

### Property 5: Course card thumbnail display
*For any* course with a thumbnail path, the rendered course card should include an image element with that thumbnail URL
**Validates: Requirements 1.5**

### Property 6: Start button for new courses
*For any* student who has never accessed a course, the course card should display a "Start" button
**Validates: Requirements 2.2**

### Property 7: Continue button for accessed courses
*For any* student who has previously accessed a course, the course card should display a "Continue" button
**Validates: Requirements 2.3**

### Property 8: Course navigation on button click
*For any* course card button click, the system should navigate to the course detail page with the correct course ID in the URL
**Validates: Requirements 2.4**

### Property 9: Progress state determines button
*For any* student-course combination, the button state (Start/Continue) should match the presence of a progress record in the database
**Validates: Requirements 2.5**

### Property 10: Progress record creation on first access
*For any* student clicking "Start" on a course for the first time, a progress record should be created in the database
**Validates: Requirements 2.6**

### Property 11: Last accessed timestamp updates
*For any* course visit by a student, the progress record's last_accessed timestamp should be updated to the current time
**Validates: Requirements 2.7**

### Property 12: Video file validation
*For any* file upload attempt, if the file is a valid video type (MP4, WebM, OGG) and under 500MB, the system should accept it; otherwise, it should reject it with an appropriate error
**Validates: Requirements 3.1**

### Property 13: Video storage location consistency
*For any* uploaded video, the file should exist at the path `backend/uploads/videos/<filename>` after upload completes
**Validates: Requirements 3.2**

### Property 14: Video filename uniqueness with extension
*For any* two video uploads, the system should generate different unique filenames while preserving the original file extension
**Validates: Requirements 3.3**

### Property 15: Video path round-trip
*For any* video uploaded to a module, fetching the module from the database should return the same video path that was stored
**Validates: Requirements 3.4**

### Property 16: Video player API fetch
*For any* video click in a module, the video player should make an API request to `/api/videos/<video_id>` with the correct video ID
**Validates: Requirements 3.6**

### Property 17: Video MIME type headers
*For any* video file served by the API, the response should include a Content-Type header matching the video's MIME type
**Validates: Requirements 3.7**

### Property 18: HTTP range request support
*For any* video streaming request with a Range header, the system should return partial content (206 status) with the requested byte range
**Validates: Requirements 3.8**

### Property 19: Document file validation
*For any* file upload attempt, if the file is a valid document type (PDF, DOCX, PPTX, TXT) and under 50MB, the system should accept it; otherwise, it should reject it with an appropriate error
**Validates: Requirements 4.1**

### Property 20: Document storage location consistency
*For any* uploaded document, the file should exist at the path `backend/uploads/documents/<filename>` after upload completes
**Validates: Requirements 4.2**

### Property 21: Document filename uniqueness with extension
*For any* two document uploads, the system should generate different unique filenames while preserving the original file extension
**Validates: Requirements 4.3**

### Property 22: Document path round-trip
*For any* document uploaded to a module, fetching the module from the database should return the same document path that was stored
**Validates: Requirements 4.4**

### Property 23: Course metadata round-trip
*For any* course created with metadata (title, description, thumbnail), fetching the course should return all the same metadata values
**Validates: Requirements 5.1**

### Property 24: Module metadata round-trip
*For any* modules added to a course, fetching the course should return all modules with their metadata intact
**Validates: Requirements 5.2**

### Property 25: Material metadata round-trip
*For any* materials uploaded to a module, fetching the module should return all materials with their metadata intact
**Validates: Requirements 5.3**

### Property 26: Enrollment record creation
*For any* student enrollment in a course, an enrollment record should exist in the database linking the student to the course
**Validates: Requirements 5.4**

### Property 27: Module ordering consistency
*For any* course with multiple modules, the modules should be displayed in ascending order by their order field
**Validates: Requirements 5.5**

### Property 28: Material ordering consistency
*For any* module with multiple materials, the materials should be displayed in ascending order by their order field
**Validates: Requirements 5.6**

### Property 29: Progress tracking on material interaction
*For any* student interaction with a material (watching video, downloading document), the progress record should be updated to reflect the interaction
**Validates: Requirements 5.7**

### Property 30: Assignment creation and linking
*For any* assignment created by a teacher for a course, the assignment should be linked to the course in the database
**Validates: Requirements 5.8**

### Property 31: Submission saving
*For any* assignment submission by a student, the submission should be saved in the database with the correct student and assignment IDs
**Validates: Requirements 5.9**

### Property 32: Unauthorized course access rejection
*For any* student attempting to access a course they are not enrolled in, the system should return a 403 Forbidden error
**Validates: Requirements 6.3**

### Property 33: Directory traversal prevention
*For any* file path request containing directory traversal patterns (../, ..\), the system should reject the request
**Validates: Requirements 6.7**

### Property 34: File operation logging
*For any* file upload or access operation, an entry should be created in the system logs
**Validates: Requirements 6.8**

### Property 35: Course schema completeness
*For any* course record in the database, it should contain all required fields: _id, title, description, thumbnail_path, teacher_id, created_at, updated_at
**Validates: Requirements 7.1**

### Property 36: Module schema completeness
*For any* module record in the database, it should contain all required fields: _id, course_id, title, description, order, materials, created_at
**Validates: Requirements 7.2**

### Property 37: Material schema completeness
*For any* material record in the database, it should contain all required fields: material_id, type, title, file_path, file_size, mime_type, uploaded_at
**Validates: Requirements 7.3**

### Property 38: Enrollment schema completeness
*For any* enrollment record in the database, it should contain all required fields: _id, student_id, course_id, enrolled_at, progress_state
**Validates: Requirements 7.4**

### Property 39: Progress schema completeness
*For any* progress record in the database, it should contain all required fields: _id, student_id, course_id, last_accessed, started, completed_materials
**Validates: Requirements 7.5**

### Property 40: API field naming convention
*For any* API response, field names should follow camelCase convention (e.g., courseId, studentId, createdAt)
**Validates: Requirements 7.6**

## Error Handling

### File Upload Errors
- **Oversized files**: Return 413 Payload Too Large with message indicating size limit
- **Invalid file types**: Return 400 Bad Request with list of allowed file types
- **Missing files**: Return 400 Bad Request with message indicating required file is missing
- **Storage failures**: Return 500 Internal Server Error with generic error message (log details server-side)

### Access Control Errors
- **Unenrolled student**: Return 403 Forbidden when student attempts to access course they're not enrolled in
- **Missing authentication**: Return 401 Unauthorized when no valid JWT token is provided
- **Expired token**: Return 401 Unauthorized with message indicating token has expired

### File Serving Errors
- **File not found**: Return 404 Not Found when requested file doesn't exist on disk
- **Missing database record**: Return 404 Not Found when video/document ID doesn't exist in database
- **Corrupted file**: Return 500 Internal Server Error and log the issue for investigation

### Progress Tracking Errors
- **Invalid course ID**: Return 404 Not Found when course doesn't exist
- **Invalid material ID**: Return 404 Not Found when material doesn't exist
- **Database connection failure**: Return 503 Service Unavailable and retry with exponential backoff

## Testing Strategy

### Unit Testing

**Backend Unit Tests** (Python with pytest)
- Test file validation functions with various file types and sizes
- Test filename generation for uniqueness
- Test database CRUD operations for all models
- Test API endpoint authorization logic
- Test error handling for edge cases

**Frontend Unit Tests** (TypeScript with Vitest)
- Test course card rendering with and without thumbnails
- Test Start/Continue button logic based on progress state
- Test video player controls and event handlers
- Test file upload component validation
- Test navigation routing logic

### Integration Testing

**End-to-End Course Creation Flow**
1. Teacher uploads thumbnail
2. Teacher creates course with thumbnail URL
3. Verify course appears on teacher dashboard with thumbnail
4. Verify course appears on student dashboard with thumbnail

**End-to-End Course Access Flow**
1. Student views dashboard with enrolled courses
2. Student clicks "Start" button on new course
3. Verify progress record is created
4. Verify navigation to course detail page
5. Student returns to dashboard
6. Verify "Continue" button is now displayed

**End-to-End Video Playback Flow**
1. Teacher uploads video to course module
2. Student accesses course and opens module
3. Student clicks video to play
4. Verify video streams correctly
5. Verify progress is tracked
6. Verify completion status updates

### Property-Based Testing

**Property Testing Framework**: Hypothesis (Python) for backend, fast-check (TypeScript) for frontend

**Test Configuration**: Each property test should run a minimum of 100 iterations

**Property Test Examples**:

```python
# Property 1: Thumbnail file validation
@given(file_type=st.sampled_from(['jpg', 'png', 'gif', 'webp', 'pdf', 'txt']),
       file_size=st.integers(min_value=0, max_value=10*1024*1024))
def test_thumbnail_validation(file_type, file_size):
    """Feature: course-media-and-access-fixes, Property 1: Thumbnail file validation"""
    is_valid_type = file_type in ['jpg', 'png', 'gif', 'webp']
    is_valid_size = file_size <= 5*1024*1024
    
    result = validate_thumbnail(file_type, file_size)
    
    assert result.is_valid == (is_valid_type and is_valid_size)
```

```python
# Property 3: Thumbnail filename uniqueness
@given(st.lists(st.text(min_size=1), min_size=2, max_size=10))
def test_thumbnail_filename_uniqueness(filenames):
    """Feature: course-media-and-access-fixes, Property 3: Thumbnail filename uniqueness"""
    generated_names = [generate_unique_filename(name) for name in filenames]
    
    # All generated names should be unique
    assert len(generated_names) == len(set(generated_names))
```

```python
# Property 4: Thumbnail path round-trip
@given(st.text(min_size=1, max_size=100))
def test_thumbnail_path_round_trip(thumbnail_path):
    """Feature: course-media-and-access-fixes, Property 4: Thumbnail path round-trip"""
    course_data = {'title': 'Test', 'thumbnail': thumbnail_path}
    course_id = create_course(course_data)
    
    fetched_course = get_course(course_id)
    
    assert fetched_course['thumbnail'] == thumbnail_path
```

```python
# Property 9: Progress state determines button
@given(has_progress=st.booleans())
def test_progress_determines_button(has_progress):
    """Feature: course-media-and-access-fixes, Property 9: Progress state determines button"""
    student_id = create_test_student()
    course_id = create_test_course()
    
    if has_progress:
        create_progress_record(student_id, course_id)
    
    button_text = get_course_button_text(student_id, course_id)
    
    expected = "Continue" if has_progress else "Start"
    assert button_text == expected
```

```python
# Property 27: Module ordering consistency
@given(st.lists(st.integers(min_value=0, max_value=100), min_size=2, max_size=10))
def test_module_ordering(order_values):
    """Feature: course-media-and-access-fixes, Property 27: Module ordering consistency"""
    course_id = create_test_course()
    
    # Create modules with random order values
    for order in order_values:
        create_module(course_id, order=order)
    
    # Fetch modules
    modules = get_course_modules(course_id)
    
    # Verify they are sorted by order
    module_orders = [m['order'] for m in modules]
    assert module_orders == sorted(module_orders)
```

### Manual Testing Checklist

**Thumbnail Upload and Display**
- [ ] Upload various image formats (JPEG, PNG, GIF, WebP)
- [ ] Verify thumbnail appears on teacher dashboard
- [ ] Verify thumbnail appears on student dashboard
- [ ] Verify placeholder appears when no thumbnail is set
- [ ] Test with images at size limit (5MB)
- [ ] Test with oversized images (should be rejected)

**Course Access and Navigation**
- [ ] Verify "Start" button appears for new courses
- [ ] Click "Start" and verify navigation to course detail page
- [ ] Return to dashboard and verify "Continue" button appears
- [ ] Click "Continue" and verify navigation to course detail page
- [ ] Verify progress timestamp updates on each visit

**Video Upload and Playback**
- [ ] Upload video to course module
- [ ] Verify video appears in module materials list
- [ ] Click video and verify it plays
- [ ] Test video seeking (skip forward/backward)
- [ ] Test video pause and resume
- [ ] Verify progress tracking updates
- [ ] Test with different video formats (MP4, WebM, OGG)

**Document Upload and Download**
- [ ] Upload document to course module
- [ ] Verify document appears in module materials list
- [ ] Click document and verify it downloads
- [ ] Test with different document formats (PDF, DOCX, PPTX, TXT)

**Error Handling**
- [ ] Test uploading oversized files
- [ ] Test uploading invalid file types
- [ ] Test accessing course without enrollment
- [ ] Test accessing non-existent video
- [ ] Test accessing non-existent document

## Implementation Notes

### File Storage Considerations
- Use UUID v4 for generating unique filenames
- Preserve original file extensions for proper MIME type detection
- Store files outside the web root for security
- Implement file cleanup for deleted courses/materials

### Database Indexing
Create indexes on frequently queried fields:
```javascript
db.courses.createIndex({ "teacher_id": 1 })
db.materials.createIndex({ "course_id": 1 })
db.progress.createIndex({ "student_id": 1, "course_id": 1 })
db.enrollments.createIndex({ "student_id": 1 })
db.enrollments.createIndex({ "course_id": 1 })
db.video_progress.createIndex({ "student_id": 1, "video_id": 1 })
```

### Security Considerations
- Validate all file uploads for type and size
- Sanitize filenames to prevent directory traversal
- Implement rate limiting on file uploads
- Require authentication for all file access
- Check enrollment status before serving course materials
- Use secure file serving (no direct path exposure)

### Performance Optimizations
- Implement lazy loading for course thumbnails
- Use HTTP range requests for video streaming
- Cache frequently accessed course data
- Implement pagination for large course lists
- Use CDN for static file serving in production

### Backward Compatibility
- Existing courses without thumbnails should use placeholder
- Existing materials should continue to work with old file paths
- Migration script needed to update old video references to new video collection
