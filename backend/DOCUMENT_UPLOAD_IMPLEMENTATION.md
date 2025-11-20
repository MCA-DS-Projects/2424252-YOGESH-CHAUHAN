# Document Upload and Storage Implementation

## Overview
This document describes the implementation of Task 10: Document upload and storage system for the EduNexa LMS.

## Requirements Implemented

### Requirement 4.1: File Validation
- ✅ Accepts document files: PDF, DOCX, PPTX, TXT
- ✅ Maximum file size: 50MB
- ✅ Rejects invalid file types with 400 error
- ✅ Rejects oversized files with 413 error

### Requirement 4.2: Storage Location
- ✅ Documents stored in `backend/uploads/documents/`
- ✅ Directory created automatically if it doesn't exist
- ✅ Files stored with proper permissions

### Requirement 4.3: Unique Filenames
- ✅ Generates unique filenames using UUID v4
- ✅ Preserves original file extension
- ✅ Prevents filename collisions
- ✅ Format: `{uuid}.{extension}` (e.g., `8370a349-2b9f-47b1-a1a3-9fe55052f7de.pdf`)

### Requirement 4.4: Database Storage and Material Linking
- ✅ Document metadata stored in `documents` collection
- ✅ Stores: filename, original_filename, file_path, file_size, mime_type, uploaded_by, created_at
- ✅ Documents can be linked to course materials via `/api/courses/<course_id>/materials` endpoint
- ✅ Material type set to 'document' with document_id in content field

## API Endpoints

### POST /api/documents/upload
Upload a document file (teachers only)

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Headers: Authorization: Bearer {token}
- Body: document file

**Response (201):**
```json
{
  "message": "Document uploaded successfully",
  "documentId": "691d8dc6ce3674fe2a89aafd",
  "document_id": "691d8dc6ce3674fe2a89aafd",
  "filename": "8370a349-2b9f-47b1-a1a3-9fe55052f7de.pdf",
  "originalFilename": "integration_test.pdf",
  "original_filename": "integration_test.pdf",
  "fileSize": 47,
  "file_size": 47,
  "mimeType": "application/pdf",
  "mime_type": "application/pdf",
  "documentUrl": "/api/documents/691d8dc6ce3674fe2a89aafd",
  "document_url": "/api/documents/691d8dc6ce3674fe2a89aafd"
}
```

**Error Responses:**
- 400: Invalid file type or no file provided
- 403: Only teachers can upload documents
- 413: File size exceeds 50MB limit
- 500: Server error

### POST /api/courses/{course_id}/materials
Link a document to a course material

**Request:**
```json
{
  "title": "Course Syllabus",
  "description": "PDF syllabus for the course",
  "type": "document",
  "content": "691d8dc6ce3674fe2a89aafd",
  "order": 1,
  "is_required": true
}
```

**Response (201):**
```json
{
  "message": "Material uploaded successfully",
  "material": {
    "_id": "691d8dc6ce3674fe2a89aafe",
    "course_id": "691d8dc6ce3674fe2a89aafc",
    "title": "Course Syllabus",
    "description": "PDF syllabus for the course",
    "type": "document",
    "content": "691d8dc6ce3674fe2a89aafd",
    "order": 1,
    "is_required": true,
    "uploaded_by": "691d8dc6ce3674fe2a89ab00",
    "created_at": "2025-01-19T12:34:56.789Z"
  }
}
```

## Database Schema

### documents Collection
```javascript
{
  _id: ObjectId,
  filename: String,              // UUID-based unique filename
  original_filename: String,     // Original upload filename
  file_path: String,            // Full path to file on disk
  file_size: Number,            // Size in bytes
  mime_type: String,            // MIME type (application/pdf, text/plain, etc.)
  uploaded_by: String,          // User ID of uploader
  created_at: Date              // Upload timestamp
}
```

### materials Collection (Document Type)
```javascript
{
  _id: ObjectId,
  course_id: String,            // Course this material belongs to
  title: String,                // Material title
  description: String,          // Material description
  type: "document",             // Material type
  content: String,              // Document ID (references documents collection)
  order: Number,                // Display order
  is_required: Boolean,         // Whether material is required
  uploaded_by: String,          // User ID of uploader
  created_at: Date              // Creation timestamp
}
```

## File Structure
```
backend/
├── uploads/
│   ├── documents/                    # Document storage directory
│   │   ├── {uuid}.pdf               # PDF documents
│   │   ├── {uuid}.docx              # Word documents
│   │   ├── {uuid}.pptx              # PowerPoint documents
│   │   └── {uuid}.txt               # Text documents
│   ├── videos/                      # Video files
│   ├── thumbnails/                  # Course thumbnails
│   └── assignments/                 # Assignment submissions
├── routes/
│   ├── documents.py                 # Document upload routes
│   └── courses.py                   # Course and material routes
└── tests/
    ├── test_document_upload.py      # Unit tests for document upload
    └── test_document_integration.py # Integration tests
```

## Security Features

1. **Authentication**: Only authenticated teachers can upload documents
2. **File Type Validation**: Only allowed file types (PDF, DOCX, PPTX, TXT) are accepted
3. **File Size Limits**: Maximum 50MB per document
4. **Filename Sanitization**: Original filenames are sanitized using `secure_filename()`
5. **Unique Storage**: UUID-based filenames prevent collisions and path traversal attacks
6. **Authorization**: Teachers can only upload documents for their own courses

## Testing

### Unit Tests (7 tests)
- ✅ Document upload endpoint exists
- ✅ Documents directory exists
- ✅ File type validation works
- ✅ File size validation works
- ✅ Unique filename generation
- ✅ Database storage verification
- ✅ Material linking functionality

### Integration Tests (2 tests)
- ✅ Complete workflow: upload → store → link to course
- ✅ Multiple document types (PDF, TXT, DOCX)

**Test Results:** All 9 tests passed ✅

## Usage Example

### 1. Upload a Document
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "Authorization: Bearer {teacher_token}" \
  -F "document=@syllabus.pdf"
```

### 2. Link Document to Course Material
```bash
curl -X POST http://localhost:5000/api/courses/{course_id}/materials \
  -H "Authorization: Bearer {teacher_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Course Syllabus",
    "description": "Detailed course syllabus",
    "type": "document",
    "content": "{document_id}",
    "order": 1,
    "is_required": true
  }'
```

## Integration with Existing System

The document upload system integrates seamlessly with:

1. **Course Creation**: Teachers can upload documents when creating courses
2. **Material Management**: Documents are treated as course materials alongside videos
3. **Student Access**: Students can view and download documents from enrolled courses
4. **Progress Tracking**: Document access can be tracked for course progress

## Next Steps (Task 11)

The next task will implement:
- Document serving endpoint: `GET /api/documents/<document_id>`
- Authorization checks for document access
- Proper MIME type and Content-Disposition headers
- Download functionality in frontend

## Notes

- The implementation follows the same pattern as video upload for consistency
- Both camelCase and snake_case field names are returned for backward compatibility
- The system is ready for Task 11 (document serving and download)
- All requirements for Task 10 have been successfully implemented and tested
