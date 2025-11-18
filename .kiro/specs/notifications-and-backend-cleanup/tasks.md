# Implementation Plan

- [x] 1. Create feature branch and setup





  - Create Git branch `feat/notifications-fix-cleanup`
  - Verify current notification service functionality
  - _Requirements: 5.1_

- [x] 2. Reorganize seed scripts and remove automatic data loading




  - [x] 2.1 Create seeders directory structure


    - Create `backend/scripts/seeders/` directory
    - _Requirements: 3.4_

  
  - [x] 2.2 Extract and move seed data logic

    - Extract `create_sample_users()`, `create_sample_courses()`, `create_sample_enrollments()`, `create_sample_assignments()` from `backend/utils/db_init.py`
    - Create new file `backend/scripts/seeders/seed_sample_data.py` with extracted functions
    - Add main execution block to run seeding manually
    - _Requirements: 3.3, 3.4_
  


  - [x] 2.3 Move existing test data scripts

    - Move `backend/create_test_teacher.py` to `backend/scripts/seeders/create_test_teacher.py`
    - Move `backend/create_test_data.py` to `backend/scripts/seeders/create_test_student_data.py`
    - Update import paths in moved scripts if necessary


    - _Requirements: 3.4_
  
  - [x] 2.4 Update db_init.py to only create indexes

    - Remove calls to `create_sample_users()`, `create_sample_courses()`, `create_sample_enrollments()`, `create_sample_assignments()` from `initialize_database()`
    - Keep only `create_indexes()` call


    - Update print messages to reflect index-only initialization
    - Remove the data existence check (`if db.users.count_documents({}) > 0`)
    - _Requirements: 3.1, 3.2_

  
  - [x] 2.5 Update app.py startup

    - Verify `app.py` calls `initialize_database(db)` for indexes only
    - Remove any other seed-related function calls from startup
    - _Requirements: 3.1, 3.2_
  
  - [x] 2.6 Create seeders README documentation

    - Create `backend/scripts/seeders/README.md`
    - Document how to run each seed script manually
    - Include usage examples and prerequisites
    - _Requirements: 3.5, 5.3_

- [x] 3. Fix and verify teacher assignment deletion permissions






  - [x] 3.1 Review current delete endpoint implementation

    - Examine permission logic in `backend/routes/assignments.py` delete_assignment()
    - Verify role checks for admin and teacher ownership
    - Document current behavior
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  

  - [x] 3.2 Test teacher deletion scenarios

    - Create manual test script `backend/scripts/test_assignment_deletion.py`
    - Test: Teacher deletes own assignment (should succeed)
    - Test: Teacher deletes another teacher's assignment (should fail with 403)
    - Test: Admin deletes any assignment (should succeed)
    - _Requirements: 2.1, 2.2, 2.3_
  


  - [x] 3.3 Fix permission bugs if discovered

    - Apply fixes to permission logic if tests reveal issues
    - Ensure ownership check compares correct IDs
    - Improve error messages for clarity

    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 3.4 Verify deletion cascades correctly

    - Ensure related submissions are deleted
    - Verify MongoDB operations complete successfully
    - _Requirements: 2.5_

- [x] 4. Enhance notification integration for assignment workflows




  - [x] 4.1 Add admin notification on assignment deletion


    - Modify delete_assignment() in `backend/routes/assignments.py`
    - After successful deletion, call `notify_users_by_role(db, ['admin', 'super_admin'], subject, body)`
    - Use background thread to avoid blocking response
    - Handle notification failures gracefully
    - _Requirements: 1.5, 4.2_
  
  - [x] 4.2 Add student notification on assignment due date update


    - Modify update_assignment() in `backend/routes/assignments.py`
    - Check if `due_date` field changed in update
    - If changed, call `notify_course_participants()` for enrolled students
    - Use background thread for async execution
    - _Requirements: 1.5, 4.3_
  
  - [x] 4.3 Verify existing notification integrations


    - Test assignment creation notification (already implemented)
    - Test assignment submission notification (already implemented)
    - Test assignment grading notification (already implemented)
    - Ensure all use proper error handling
    - _Requirements: 1.5, 4.1, 4.4_

- [x] 5. Create comprehensive documentation




  - [x] 5.1 Create DEV_NOTES.md


    - Create `docs/DEV_NOTES.md` file
    - Document environment variable setup for Gmail SMTP
    - Include Gmail App Password creation instructions
    - Document manual seed script usage
    - Add troubleshooting section for common issues
    - _Requirements: 5.3, 5.4_
  

  - [x] 5.2 Update .env.example

    - Add email configuration variables to `backend/.env.example`
    - Include comments explaining each variable
    - Document Gmail-specific requirements
    - _Requirements: 1.2, 1.7_
  

  - [x] 5.3 Document testing procedures

    - Add testing section to DEV_NOTES.md
    - Document how to test email notifications locally
    - Include manual test scenarios for assignment deletion
    - Provide example test data setup commands
    - _Requirements: 5.4_

- [x] 6. Testing and validation





  - [x] 6.1 Create manual test script for notifications


    - Create `backend/scripts/test_email_notification.py`
    - Test sending single email via notification service
    - Test role-based notifications
    - Test course participant notifications
    - _Requirements: 1.5, 5.4_
  
  - [x] 6.2 Verify MongoDB-only data flow


    - Start application with empty database
    - Verify no automatic data seeding occurs
    - Verify indexes are created
    - Manually run seed scripts and verify data creation
    - _Requirements: 3.1, 3.2, 3.5_
  
  - [x] 6.3 End-to-end workflow testing


    - Test complete assignment lifecycle with notifications
    - Verify teacher can delete own assignments
    - Verify notifications sent at appropriate events
    - Verify permission denials work correctly
    - _Requirements: 2.1, 2.2, 2.3, 4.1, 4.2, 4.3_

- [-] 7. Finalize and create pull request




  - [x] 7.1 Review all code changes

    - Verify no credentials committed
    - Check code follows project conventions
    - Ensure all error handling is in place
    - Validate logging statements are appropriate
    - _Requirements: 1.7, 5.1_
  

  - [x] 7.2 Commit changes with conventional commit messages




    - Commit: `feat: add admin notification on assignment deletion`
    - Commit: `feat: add student notification on assignment due date update`
    - Commit: `fix: verify teacher assignment deletion permissions`
    - Commit: `chore: remove automatic mock data loading from db_init`
    - Commit: `chore: move seed scripts to scripts/seeders directory`
    - Commit: `docs: add DEV_NOTES with email setup and seed instructions`
    - _Requirements: 5.2_
  
  - [ ] 7.3 Create pull request
    - Push branch to remote repository
    - Create PR with descriptive title
    - Include summary of changes in PR description
    - List testing steps for reviewers
    - Reference requirements document
    - _Requirements: 5.5_
