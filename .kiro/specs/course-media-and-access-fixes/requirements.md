# Requirements Document

## Introduction

This specification addresses critical bugs in the EduNexa Learning Management System related to course media handling, student course access, and the complete teacher-to-student workflow. The system currently fails to display course thumbnails, prevents students from accessing courses, and blocks video playback within course modules. These issues break the core learning experience and must be resolved to restore full platform functionality.

## Glossary

- **System**: The EduNexa Learning Management System (Flask backend + React frontend)
- **Teacher**: A user with the 'teacher' role who creates and manages courses
- **Student**: A user with the 'student' role who enrolls in and accesses courses
- **Course**: A learning unit containing modules, materials, videos, documents, and assignments
- **Module**: A section within a course that organizes related learning materials
- **Thumbnail**: A preview image representing a course, uploaded during course creation
- **Video**: A learning material file (MP4 format) uploaded to course modules
- **Document**: A learning material file (PDF, DOCX, etc.) uploaded to course modules
- **Course_Card**: A UI component displaying course information on dashboards
- **Start_Button**: A button on a Course_Card for first-time course access
- **Continue_Button**: A button on a Course_Card for returning to an in-progress course
- **Video_Player**: The frontend component that renders and plays video files
- **Upload_Directory**: The backend file storage location for course media (thumbnails, videos, documents)
- **API_Endpoint**: A backend route that handles HTTP requests for course operations
- **Progress_State**: A database record tracking whether a student has started a course

## Requirements

### Requirement 1: Course Thumbnail Upload and Display

**User Story:** As a teacher, I want to upload a course thumbnail during course creation so that my courses are visually identifiable on student and teacher dashboards.

#### Acceptance Criteria

1. WHEN a teacher creates a course with a thumbnail file, THE System SHALL accept image files (JPEG, PNG, GIF, WebP) up to 5MB in size
2. WHEN a thumbnail is uploaded, THE System SHALL store the file in the Upload_Directory at `backend/uploads/thumbnails/`
3. WHEN a thumbnail is uploaded, THE System SHALL generate a unique filename using UUID to prevent collisions
4. WHEN a thumbnail is uploaded, THE System SHALL save the file path or URL in the course database record
5. WHEN a Course_Card is rendered on any dashboard, THE System SHALL fetch and display the course thumbnail image
6. IF a course has no thumbnail, THE System SHALL display a default placeholder image
7. THE System SHALL serve thumbnail files via a dedicated API_Endpoint at `/api/courses/thumbnail/<filename>`

### Requirement 2: Student Course Access and Routing

**User Story:** As a student, I want to click on a course card and access the course content so that I can begin or continue my learning.

#### Acceptance Criteria

1. WHEN a student views their dashboard, THE System SHALL display enrolled courses as clickable Course_Cards
2. WHEN a student has never accessed a course, THE Course_Card SHALL display a Start_Button
3. WHEN a student has previously accessed a course, THE Course_Card SHALL display a Continue_Button
4. WHEN a student clicks the Start_Button or Continue_Button, THE System SHALL navigate to the course detail page at `/courses/<course_id>`
5. THE System SHALL determine button state by checking the Progress_State database for the student and course combination
6. WHEN a student first clicks Start_Button, THE System SHALL create a Progress_State record in the database
7. THE System SHALL update the Progress_State record with the last accessed timestamp on each course visit

### Requirement 3: Video Upload, Storage, and Playback

**User Story:** As a student, I want to watch videos within course modules so that I can learn from the video content provided by my teacher.

#### Acceptance Criteria

1. WHEN a teacher uploads a video to a module, THE System SHALL accept video files (MP4, WebM, OGG) up to 500MB in size
2. WHEN a video is uploaded, THE System SHALL store the file in the Upload_Directory at `backend/uploads/videos/`
3. WHEN a video is uploaded, THE System SHALL generate a unique filename using UUID and preserve the file extension
4. WHEN a video is uploaded, THE System SHALL save the file path in the module's materials array in the database
5. WHEN a student opens a module, THE System SHALL display all video materials with play buttons
6. WHEN a student clicks a video, THE Video_Player SHALL fetch the video file via API_Endpoint at `/api/videos/<video_id>`
7. THE System SHALL serve video files with proper MIME type headers (video/mp4, video/webm, video/ogg)
8. THE System SHALL support HTTP range requests for video streaming and seeking
9. WHEN a video fails to load, THE System SHALL display a clear error message to the student

### Requirement 4: Document Upload and Access

**User Story:** As a student, I want to download and view documents within course modules so that I can access supplementary learning materials.

#### Acceptance Criteria

1. WHEN a teacher uploads a document to a module, THE System SHALL accept document files (PDF, DOCX, PPTX, TXT) up to 50MB in size
2. WHEN a document is uploaded, THE System SHALL store the file in the Upload_Directory at `backend/uploads/documents/`
3. WHEN a document is uploaded, THE System SHALL generate a unique filename using UUID and preserve the file extension
4. WHEN a document is uploaded, THE System SHALL save the file path in the module's materials array in the database
5. WHEN a student opens a module, THE System SHALL display all document materials with download buttons
6. WHEN a student clicks a document, THE System SHALL serve the file via API_Endpoint at `/api/documents/<document_id>`
7. THE System SHALL serve document files with proper MIME type headers and Content-Disposition for download

### Requirement 5: Complete Teacher-to-Student Workflow

**User Story:** As a system operator, I want the complete course creation and consumption workflow to function correctly so that teachers can deliver content and students can learn effectively.

#### Acceptance Criteria

1. WHEN a teacher creates a course, THE System SHALL save all course metadata (title, description, thumbnail) to the database
2. WHEN a teacher adds modules to a course, THE System SHALL save module metadata (title, order, description) to the database
3. WHEN a teacher uploads materials to modules, THE System SHALL save material metadata (type, filename, file_path, title) to the database
4. WHEN a student enrolls in a course, THE System SHALL create an enrollment record linking the student to the course
5. WHEN a student accesses a course, THE System SHALL display all modules in the correct order
6. WHEN a student opens a module, THE System SHALL display all materials (videos, documents) in the correct order
7. WHEN a student interacts with materials, THE System SHALL track progress and update the Progress_State record
8. WHEN a teacher creates an assignment for a course, THE System SHALL link the assignment to the course and notify enrolled students
9. WHEN a student submits an assignment, THE System SHALL save the submission and notify the teacher
10. THE System SHALL maintain referential integrity between courses, modules, materials, enrollments, and assignments

### Requirement 6: Error Handling and Validation

**User Story:** As a developer, I want comprehensive error handling and validation so that the system provides clear feedback when operations fail.

#### Acceptance Criteria

1. WHEN a file upload exceeds size limits, THE System SHALL reject the upload and return a 413 Payload Too Large error with a descriptive message
2. WHEN a file upload has an invalid file type, THE System SHALL reject the upload and return a 400 Bad Request error with allowed types
3. WHEN a student attempts to access a course they are not enrolled in, THE System SHALL return a 403 Forbidden error
4. WHEN an API_Endpoint receives a request for a non-existent file, THE System SHALL return a 404 Not Found error
5. WHEN a file path in the database points to a missing file, THE System SHALL log the error and display a user-friendly message
6. WHEN a video fails to stream, THE System SHALL provide retry functionality and fallback error messaging
7. THE System SHALL validate all file paths to prevent directory traversal attacks
8. THE System SHALL log all file upload and access operations for debugging and auditing

### Requirement 7: Database Schema Consistency

**User Story:** As a developer, I want consistent database schemas for courses, modules, and materials so that the system can reliably store and retrieve course content.

#### Acceptance Criteria

1. THE System SHALL store course records with fields: _id, title, description, thumbnail_path, teacher_id, created_at, updated_at
2. THE System SHALL store module records with fields: _id, course_id, title, description, order, materials, created_at
3. THE System SHALL store material records within modules with fields: material_id, type, title, file_path, file_size, mime_type, uploaded_at
4. THE System SHALL store enrollment records with fields: _id, student_id, course_id, enrolled_at, progress_state
5. THE System SHALL store progress records with fields: _id, student_id, course_id, last_accessed, started, completed_materials
6. THE System SHALL use consistent field naming conventions (snake_case for database, camelCase for API responses)
7. THE System SHALL create database indexes on frequently queried fields (course_id, student_id, teacher_id)
