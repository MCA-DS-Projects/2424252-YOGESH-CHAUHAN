# Implementation Plan

## Overview
This implementation plan breaks down the course media and access fixes into discrete, manageable tasks. Each task builds incrementally on previous work to restore full functionality to the course creation, access, and media playback workflows.

## Tasks

- [x] 1. Fix thumbnail upload and storage system










  - Create thumbnails directory in backend/uploads/
  - Implement thumbnail upload endpoint with file validation (type, size)
  - Generate unique filenames using UUID + timestamp
  - Return thumbnail URL path to frontend
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Fix thumbnail serving and display








  - Implement thumbnail serving endpoint at `/api/courses/thumbnails/<filename>`
  - Update course creation to store thumbnail path in database
  - Update CourseCard component to display thumbnail from course.thumbnail field
  - Add placeholder image fallback for courses without thumbnails
  - _Requirements: 1.4, 1.5, 1.6, 1.7_

- [x] 2.1 Write property test for thumbnail validation


  - **Property 1: Thumbnail file validation**
  - **Validates: Requirements 1.1**

- [x] 2.2 Write property test for thumbnail uniqueness


  - **Property 3: Thumbnail filename uniqueness**
  - **Validates: Requirements 1.3**

- [x] 2.3 Write property test for thumbnail round-trip


  - **Property 4: Thumbnail path round-trip**
  - **Validates: Requirements 1.4**

- [x] 3. Implement progress state tracking system









  - Create progress collection schema in MongoDB
  - Implement GET `/api/progress/course/<course_id>` endpoint to fetch progress
  - Implement POST `/api/progress/course/<course_id>/start` endpoint to initialize progress
  - Add started field and last_accessed timestamp to progress records
  - _Requirements: 2.5, 2.6, 2.7_

- [x] 4. Fix course access and Start/Continue button logic





  - Update StudentDashboard to fetch progress state for each enrolled course
  - Update CourseCard component to accept hasStarted prop
  - Implement button text logic: "Start" if not started, "Continue" if started
  - Implement onClick handler to navigate to course detail page
  - Update course detail page to initialize progress on first visit
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 4.1 Write property test for Start button display



  - **Property 6: Start button for new courses**
  - **Validates: Requirements 2.2**

- [x] 4.2 Write property test for Continue button display


  - **Property 7: Continue button for accessed courses**
  - **Validates: Requirements 2.3**

- [x] 4.3 Write property test for progress state button logic


  - **Property 9: Progress state determines button**
  - **Validates: Requirements 2.5**

- [x] 4.4 Write property test for progress record creation


  - **Property 10: Progress record creation on first access**
  - **Validates: Requirements 2.6**

- [x] 5. Create video collection and upload system





  - Create videos collection schema in MongoDB
  - Implement POST `/api/videos/upload` endpoint with file validation
  - Generate unique video filenames using UUID
  - Store video files in backend/uploads/videos/
  - Return video ID and metadata to frontend
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 6. Fix video storage and material linking









  - Update material creation to store video_id in content field
  - Update course creation flow to link uploaded videos to materials
  - Ensure material.type is set to 'video' for video materials
  - _Requirements: 3.4_

- [x] 7. Implement video streaming endpoint





  - Create GET `/api/videos/<video_id>/stream` endpoint
  - Implement user authorization check (enrollment verification)
  - Support HTTP range requests for video seeking
  - Serve video with proper MIME type headers
  - Track view count on video access
  - _Requirements: 3.6, 3.7, 3.8_

- [x] 7.1 Write property test for video file validation


  - **Property 12: Video file validation**
  - **Validates: Requirements 3.1**


- [x] 7.2 Write property test for video filename uniqueness

  - **Property 14: Video filename uniqueness with extension**
  - **Validates: Requirements 3.3**


- [x] 7.3 Write property test for video path round-trip

  - **Property 15: Video path round-trip**
  - **Validates: Requirements 3.4**


- [x] 7.4 Write property test for video MIME type headers

  - **Property 17: Video MIME type headers**
  - **Validates: Requirements 3.7**

- [x] 8. Fix video player and playback









  - Update VideoPlayer component to fetch video from `/api/videos/<video_id>/stream`
  - Implement video controls (play, pause, seek, volume)
  - Add loading state and error handling
  - Display clear error messages when video fails to load
  - _Requirements: 3.5, 3.9_

- [x] 9. Implement video progress tracking





  - Create video_progress collection schema in MongoDB
  - Track watch time as student watches video
  - Update progress on video pause, seek, or completion
  - Mark video as completed when watched >80%
  - Update overall course progress based on video completion
  - _Requirements: 5.7_

- [x] 10. Implement document upload and storage

















  - Create documents directory in backend/uploads/
  - Implement POST `/api/documents/upload` endpoint with file validation
  - Generate unique document filenames using UUID
  - Store document files in backend/uploads/documents/
  - Link documents to course materials
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 11. Implement document serving and download





  - Create GET `/api/documents/<document_id>` endpoint
  - Implement user authorization check (enrollment verification)
  - Serve document with proper MIME type and Content-Disposition headers
  - Update CourseDetailPage to display documents with download buttons
  - _Requirements: 4.5, 4.6, 4.7_

- [x] 11.1 Write property test for document file validation


  - **Property 19: Document file validation**
  - **Validates: Requirements 4.1**



- [x] 11.2 Write property test for document filename uniqueness





  - **Property 21: Document filename uniqueness with extension**


  - **Validates: Requirements 4.3**

- [x] 11.3 Write property test for document path round-trip





  - **Property 22: Document path round-trip**
  - **Validates: Requirements 4.4**

- [x] 12. Fix course creation workflow







  - Update CreateCoursePage to upload thumbnail before creating course
  - Update course creation API to accept and store thumbnail path
  - Ensure all course metadata is saved correctly (title, description, thumbnail)
  - Verify modules and materials are linked correctly to course
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 12.1 Write property test for course metadata round-trip


  - **Property 23: Course metadata round-trip**
  - **Validates: Requirements 5.1**

- [x] 12.2 Write property test for module metadata round-trip


  - **Property 24: Module metadata round-trip**
  - **Validates: Requirements 5.2**



- [x] 12.3 Write property test for material metadata round-trip



  - **Property 25: Material metadata round-trip**
  - **Validates: Requirements 5.3**

- [x] 13. Fix student course enrollment and access





  - Verify enrollment record creation on course enrollment
  - Implement enrollment check before serving course materials
  - Return 403 Forbidden for unenrolled students attempting access
  - Display enrolled courses on student dashboard
  - _Requirements: 5.4, 6.3_

- [x] 13.1 Write property test for enrollment record creation


  - **Property 26: Enrollment record creation**
  - **Validates: Requirements 5.4**


- [x] 13.2 Write property test for unauthorized access rejection

  - **Property 32: Unauthorized course access rejection**
  - **Validates: Requirements 6.3**

- [x] 14. Fix module and material ordering





  - Ensure modules are fetched and displayed in order by order field
  - Ensure materials within modules are displayed in order by order field
  - Update CourseDetailPage to sort modules and materials correctly
  - _Requirements: 5.5, 5.6_

- [x] 14.1 Write property test for module ordering


  - **Property 27: Module ordering consistency**
  - **Validates: Requirements 5.5**

- [x] 14.2 Write property test for material ordering


  - **Property 28: Material ordering consistency**
  - **Validates: Requirements 5.6**

- [x] 15. Implement comprehensive error handling














  - Add file size validation with 413 error for oversized files
  - Add file type validation with 400 error for invalid types
  - Add 404 error handling for non-existent files
  - Add directory traversal prevention in file path validation
  - Add user-friendly error messages in frontend
  - _Requirements: 6.1, 6.2, 6.4, 6.7_

- [x] 15.1 Write property test for directory traversal prevention


  - **Property 33: Directory traversal prevention**
  - **Validates: Requirements 6.7**

- [x] 16. Implement file operation logging



  - Add logging for all file uploads (thumbnail, video, document)
  - Add logging for all file access operations
  - Include user ID, file path, and timestamp in logs
  - Log errors with full stack traces for debugging
  - _Requirements: 6.8_

- [x] 16.1 Write property test for file operation logging


  - **Property 34: File operation logging**
  - **Validates: Requirements 6.8**

- [x] 17. Verify database schema consistency




  


  - Verify all course records have required fields
  - Verify all module records have required fields
  - Verify all material records have required fields
  - Verify all enrollment records have required fields
  - Verify all progress records have required fields
  - Create database indexes on frequently queried fields
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_


- [x] 17.1 Write property tests for schema completeness




  - **Property 35: Course schema completeness**
  - **Property 36: Module schema completeness**
  - **Property 37: Material schema completeness**
  - **Property 38: Enrollment schema completeness**
  - **Property 39: Progress schema completeness**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
- [x] 18. Fix API field naming conventions










  
- [ ] 18. Fix API field naming conventions

  - Ensure database uses snake_case (course_id, student_id, created_at)
  - Ensure API responses use camelCase (courseId, studentId, createdAt)
  - Add transformation layer in API endpoints
  - Update frontend to use camelCase field names
  - _Requirements: 7.6_


- [x] 18.1 Write property test for API naming convention



  - **Property 40: API field naming convention**
  - **Validates: Requirements 7.6**

- [x] 19. Test complete teacher-to-student workflow






  - Teacher creates course with thumbnail
  - Teacher uploads videos to modules
  - Teacher uploads documents to modules
  - Teacher creates assignments for course
  - Student enrolls in course
  - Student clicks "Start" to access course
  - Student watches videos and downloads documents
  - Student submits assignment
  - Verify all data is stored correctly in database
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9_

- [ ] 20. Checkpoint - Ensure all tests pass, ask the user if questions arise

## Testing Notes

- All property-based tests are now required for comprehensive validation
- Each property test should run a minimum of 100 iterations
- Use Hypothesis (Python) for backend property tests
- Use fast-check (TypeScript) for frontend property tests
- All property tests must include a comment with the format: `**Feature: course-media-and-access-fixes, Property X: [property name]**`
- Integration tests should verify the complete workflow from teacher course creation to student course consumption

## Implementation Order

The tasks are ordered to:
1. Fix thumbnail system first (most visible issue)
2. Fix course access and navigation (blocking student access)
3. Fix video upload and playback (core learning functionality)
4. Add document support (supplementary materials)
5. Verify complete workflow (end-to-end validation)
6. Add comprehensive error handling and logging (robustness)
7. Verify database schema and API conventions (data consistency)

Each task should be completed and tested before moving to the next task.
