# Video Upload System Implementation

## Overview
This document describes the implementation of the video collection and upload system for the EduNexa LMS, completing Task 5 from the course-media-and-access-fixes specification.

## Requirements Implemented
- **Requirement 3.1**: Video file validation (MP4, WebM, OGG) with 500MB size limit
- **Requirement 3.2**: Video storage in `backend/uploads/videos/` directory
- **Requirement 3.3**: Unique filename generation using UUID with extension preservation

## Implementation Details

### 1. Videos Collection Schema (MongoDB)
The videos collection stores video metadata with the following schema:

```javascript
{
  _id: ObjectId,
  filename: String,              // Unique filename on disk (UUID.extension)
  original_filename: String,     // Original upload filename
  file_path: String,             // Full path to video file
  file_size: Number,             // Size in bytes
  mime_type: String,             // video/mp4, video/webm, video/ogg
  duration: Number,              // Duration in seconds (optional)
  uploaded_by: String,           // User ID of uploader
  created_at: Date               // Upload timestamp
}
```

### 2. Video Upload Endpoint
**Endpoint**: `POST /api/videos/upload`

**Authentication**: Required (JWT token, teacher role only)

**Request**: multipart/form-data
- `video`: Video file (required)
- `title`: Video title (optional)
- `description`: Video description (optional)
- `courseId`: Associated course ID (optional)

**Validation**:
- File type: Only MP4, WebM, OGG allowed
- File size: Maximum 500MB
- Authentication: Must be logged in as teacher

**Response** (201 Created):
```json
{
  "message": "Video uploaded successfully",
  "video_id": "507f1f77bcf86cd799439011",
  "filename": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.mp4",
  "original_filename": "my_video.mp4",
  "file_size": 10485760,
  "mime_type": "video/mp4",
  "video_url": "/api/videos/507f1f77bcf86cd799439011/stream"
}
```

**Error Responses**:
- 400: Invalid file type or missing file
- 401: Not authenticated
- 403: Not a teacher
- 413: File size exceeds 500MB limit
- 500: Server error

### 3. Video Streaming Endpoint
**Endpoint**: `GET /api/videos/<video_id>/stream`

**Authentication**: Required (JWT token)

**Response**: Video file stream with appropriate MIME type headers

### 4. File Storage
- **Location**: `backend/uploads/videos/`
- **Filename Format**: `{UUID}.{extension}` (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890.mp4`)
- **Extension Preservation**: Original file extension is preserved for proper MIME type detection

### 5. Additional Endpoints

#### Get Video Details
**Endpoint**: `GET /api/videos/<video_id>`
Returns video metadata including filename, size, MIME type, uploader info, etc.

#### List Videos
**Endpoint**: `GET /api/videos/list`
Returns paginated list of videos with optional filtering

#### Update Video
**Endpoint**: `PUT /api/videos/<video_id>`
Update video metadata (duration, etc.)

#### Delete Video
**Endpoint**: `DELETE /api/videos/<video_id>`
Delete video file and database record

## File Structure
```
backend/
├── routes/
│   └── videos.py          # Video upload and management routes
├── uploads/
│   └── videos/            # Video file storage directory
└── app.py                 # Main application (videos_bp registered)
```

## Testing
A test script has been created at `Tests/test_video_upload.py` to verify:
- Valid video upload (MP4, WebM, OGG)
- File type validation
- File size validation
- Filename uniqueness
- Extension preservation
- Authentication requirements

To run tests:
```bash
python Tests/test_video_upload.py
```

## Integration with Course Materials
Videos uploaded through this system can be linked to course materials by:
1. Upload video via `/api/videos/upload`
2. Receive `video_id` in response
3. Create material record with `type: 'video'` and `content: video_id`
4. Material will reference the video in the videos collection

## Security Considerations
- Only teachers can upload videos
- File type validation prevents malicious file uploads
- File size limits prevent storage abuse
- Unique filenames prevent file collisions
- Authentication required for all video operations

## Next Steps (Future Tasks)
- Task 6: Fix video storage and material linking
- Task 7: Implement video streaming endpoint with authorization and range requests
- Task 8: Fix video player and playback in frontend
- Task 9: Implement video progress tracking

## Compliance
This implementation satisfies:
- ✅ Requirement 3.1: File validation (type and size)
- ✅ Requirement 3.2: Storage in backend/uploads/videos/
- ✅ Requirement 3.3: Unique filename generation with UUID
- ✅ Returns video ID and metadata to frontend
- ✅ Creates videos collection in MongoDB
